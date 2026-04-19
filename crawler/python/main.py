"""
主程序入口 - 高考数据爬虫系统
"""
import argparse
import logging
import sys
import time
from datetime import datetime
from typing import List

from .config import PROVINCES, YEARS
from .crawler import GaokaoCrawler
from .database import DatabaseManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='高考数据爬虫系统')

    parser.add_argument('school_id', type=str, help='学校ID (如: 140)')

    parser.add_argument('-y', '--years', type=int, nargs='+',
                       default=YEARS,
                       help=f'年份列表 (默认: {YEARS})')

    parser.add_argument('-p', '--provinces', type=str, nargs='+',
                       default=PROVINCES,
                       help='省份列表 (默认: 所有省份)')

    parser.add_argument('-d', '--database', type=str,
                       default=None,
                       help='数据库路径 (默认: config.py中的配置)')

    parser.add_argument('--headless', action='store_true',
                       default=True,
                       help='使用无头模式 (默认: True)')

    parser.add_argument('--no-save', action='store_true',
                       default=False,
                       help='仅爬取不保存到数据库')

    parser.add_argument('--test', action='store_true',
                       default=False,
                       help='测试模式，只爬取第一个省份的第一年数据')

    parser.add_argument('--resume', action='store_true',
                       default=False,
                       help='从上次中断处恢复')

    return parser.parse_args()

def validate_inputs(args):
    """验证输入参数"""
    # 验证年份
    current_year = datetime.now().year
    for year in args.years:
        if year < 2000 or year > current_year:
            logger.warning(f"年份 {year} 可能无效")

    # 验证省份
    invalid_provinces = []
    for province in args.provinces:
        if province not in PROVINCES:
            invalid_provinces.append(province)

    if invalid_provinces:
        logger.warning(f"以下省份不在标准列表中: {invalid_provinces}")

    # 测试模式限制
    if args.test:
        args.provinces = args.provinces[:1]
        args.years = args.years[:1]
        logger.info(f"测试模式: 只爬取 {args.provinces[0]} 省份的 {args.years[0]} 年数据")

    return args

def get_progress_file(school_id: str) -> str:
    """获取进度文件路径"""
    return f"progress_{school_id}.json"

def save_progress(school_id: str, progress: dict):
    """保存爬取进度"""
    import json
    try:
        with open(get_progress_file(school_id), 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
        logger.info(f"进度已保存: {progress}")
    except Exception as e:
        logger.error(f"保存进度失败: {e}")

def load_progress(school_id: str) -> dict:
    """加载爬取进度"""
    import json
    import os

    progress_file = get_progress_file(school_id)
    if not os.path.exists(progress_file):
        return None

    try:
        with open(progress_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载进度失败: {e}")
        return None

def main():
    """主函数"""
    args = parse_arguments()
    args = validate_inputs(args)

    logger.info("=" * 60)
    logger.info("高考数据爬虫系统启动")
    logger.info(f"学校ID: {args.school_id}")
    logger.info(f"年份: {args.years}")
    logger.info(f"省份: {args.provinces}")
    logger.info(f"数据库: {args.database or '使用默认配置'}")
    logger.info("=" * 60)

    start_time = time.time()

    # 初始化数据库
    db_manager = None
    if not args.no_save:
        try:
            db_manager = DatabaseManager(args.database)
            db_manager.connect()

            # 检查数据库状态
            stats = db_manager.get_admission_stats()
            logger.info(f"数据库当前状态: {stats}")

        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            if not args.test:
                logger.error("无法连接到数据库，程序退出")
                return 1

    # 加载进度（如果启用恢复模式）
    progress = None
    if args.resume:
        progress = load_progress(args.school_id)
        if progress:
            logger.info(f"从进度文件恢复: {progress}")
        else:
            logger.info("未找到进度文件，从头开始")

    # 初始化爬虫
    try:
        with GaokaoCrawler(headless=args.headless) as crawler:

            # 获取学校基本信息
            logger.info("获取学校基本信息...")
            school_info = crawler.extract_school_info(args.school_id)

            if school_info and 'name' in school_info:
                logger.info(f"学校名称: {school_info['name']}")

                # 保存学校信息到数据库
                if db_manager and not args.no_save:
                    try:
                        # 这里需要更多信息来保存学校，暂时只记录
                        logger.info("学校信息需要更多字段才能保存到数据库")
                    except Exception as e:
                        logger.error(f"保存学校信息失败: {e}")
            else:
                logger.warning("未能获取学校名称")

            # 准备爬取任务
            total_tasks = len(args.provinces) * len(args.years)
            completed_tasks = 0

            # 如果有进度，跳过已完成的
            if progress and 'completed' in progress:
                completed_provinces = progress['completed'].get('provinces', [])
                completed_years = progress['completed'].get('years', [])

                # 过滤掉已完成的
                provinces_to_crawl = [p for p in args.provinces if p not in completed_provinces]
                years_to_crawl = [y for y in args.years if y not in completed_years]

                if not provinces_to_crawl or not years_to_crawl:
                    logger.info("所有任务已完成")
                    return 0
            else:
                provinces_to_crawl = args.provinces
                years_to_crawl = args.years

            # 开始爬取
            all_data = []

            for province in provinces_to_crawl:
                province_data = []

                for year in years_to_crawl:
                    try:
                        logger.info(f"爬取进度: {completed_tasks+1}/{total_tasks}")
                        logger.info(f"正在爬取: {province} - {year}年")

                        # 爬取数据
                        data = crawler.extract_admission_data(
                            args.school_id, year, province
                        )

                        if data:
                            province_data.extend(data)
                            logger.info(f"提取到 {len(data)} 条数据")

                            # 保存到数据库
                            if db_manager and not args.no_save:
                                try:
                                    saved_ids = db_manager.batch_save_admission_data(data)
                                    logger.info(f"成功保存 {len(saved_ids)} 条数据到数据库")
                                except Exception as e:
                                    logger.error(f"保存数据失败: {e}")
                        else:
                            logger.warning(f"未提取到数据: {province} - {year}")

                        completed_tasks += 1

                        # 更新进度
                        if args.resume:
                            progress = {
                                'school_id': args.school_id,
                                'completed': {
                                    'provinces': provinces_to_crawl[:provinces_to_crawl.index(province) + 1],
                                    'years': years_to_crawl[:years_to_crawl.index(year) + 1]
                                },
                                'last_updated': datetime.now().isoformat()
                            }
                            save_progress(args.school_id, progress)

                        # 避免请求过快
                        time.sleep(2)

                    except Exception as e:
                        logger.error(f"爬取失败 {province} - {year}: {e}")
                        # 继续下一个任务
                        continue

                all_data.extend(province_data)

            # 汇总结果
            end_time = time.time()
            duration = end_time - start_time

            logger.info("=" * 60)
            logger.info("爬取任务完成")
            logger.info(f"总耗时: {duration:.2f} 秒")
            logger.info(f"处理任务: {completed_tasks}/{total_tasks}")
            logger.info(f"提取数据: {len(all_data)} 条")

            if db_manager and not args.no_save:
                stats = db_manager.get_admission_stats()
                logger.info(f"数据库统计: {stats}")

            # 保存数据到文件（可选）
            if all_data and args.test:
                import json
                output_file = f"data_{args.school_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=2)
                logger.info(f"数据已保存到: {output_file}")

            logger.info("=" * 60)

    except KeyboardInterrupt:
        logger.info("用户中断程序")
        return 130
    except Exception as e:
        logger.error(f"程序运行失败: {e}")
        return 1

    # 清理进度文件
    if not args.resume:
        import os
        progress_file = get_progress_file(args.school_id)
        if os.path.exists(progress_file):
            os.remove(progress_file)
            logger.info("进度文件已清理")

    return 0

if __name__ == "__main__":
    sys.exit(main())