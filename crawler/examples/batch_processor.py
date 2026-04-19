"""
批量处理器 - 用于批量处理多个学校
"""
import sys
import os
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler import GaokaoCrawler
from database import DatabaseManager
from config import PROVINCES, YEARS

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_processor.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BatchProcessor:
    """批量处理器"""

    def __init__(self, config_file: str = None):
        """
        初始化批量处理器

        Args:
            config_file: 配置文件路径
        """
        self.config = self._load_config(config_file)
        self.results = []

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            'schools': [],  # 学校ID列表
            'years': YEARS,
            'provinces': PROVINCES,
            'batch_size': 5,  # 每批处理的学校数量
            'delay_between_schools': 10,  # 学校间延迟（秒）
            'delay_between_requests': 2,  # 请求间延迟（秒）
            'max_retries': 3,
            'save_to_database': True,
            'save_to_json': True,
            'output_dir': 'batch_output'
        }

        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
                    logger.info(f"从配置文件加载: {config_file}")
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")

        return default_config

    def load_schools_from_file(self, filepath: str):
        """从文件加载学校列表"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                schools = [line.strip() for line in f if line.strip()]
                self.config['schools'] = schools
                logger.info(f"从文件加载 {len(schools)} 个学校: {filepath}")
        except Exception as e:
            logger.error(f"加载学校文件失败: {e}")

    def process_school(self, school_id: str) -> Dict[str, Any]:
        """处理单个学校"""
        result = {
            'school_id': school_id,
            'start_time': datetime.now().isoformat(),
            'total_data': 0,
            'success': False,
            'errors': [],
            'province_results': {}
        }

        try:
            with GaokaoCrawler(headless=True) as crawler:
                # 获取学校信息
                school_info = crawler.extract_school_info(school_id)
                result['school_info'] = school_info

                school_data = []

                # 处理每个省份
                for province in self.config['provinces']:
                    province_result = {
                        'province': province,
                        'data_count': 0,
                        'errors': []
                    }

                    for year in self.config['years']:
                        try:
                            logger.info(f"处理: 学校={school_id}, 省份={province}, 年份={year}")

                            data = crawler.extract_admission_data(school_id, year, province)

                            if data:
                                school_data.extend(data)
                                province_result['data_count'] += len(data)
                                logger.info(f"提取到 {len(data)} 条数据")
                            else:
                                logger.warning("未提取到数据")

                            # 请求间隔
                            time.sleep(self.config['delay_between_requests'])

                        except Exception as e:
                            error_msg = f"年份 {year}: {e}"
                            logger.error(error_msg)
                            province_result['errors'].append(error_msg)
                            result['errors'].append(error_msg)

                    result['province_results'][province] = province_result

                result['total_data'] = len(school_data)
                result['end_time'] = datetime.now().isoformat()

                # 保存数据
                if school_data:
                    # 保存到数据库
                    if self.config['save_to_database']:
                        try:
                            with DatabaseManager() as db:
                                saved_ids = db.batch_save_admission_data(school_data)
                                result['saved_to_db'] = len(saved_ids)
                                logger.info(f"保存 {len(saved_ids)} 条数据到数据库")
                        except Exception as e:
                            logger.error(f"保存到数据库失败: {e}")
                            result['db_error'] = str(e)

                    # 保存到JSON文件
                    if self.config['save_to_json']:
                        output_dir = self.config['output_dir']
                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)

                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        json_file = os.path.join(output_dir, f"school_{school_id}_{timestamp}.json")

                        try:
                            with open(json_file, 'w', encoding='utf-8') as f:
                                json.dump({
                                    'school_id': school_id,
                                    'school_info': school_info,
                                    'data': school_data,
                                    'metadata': result
                                }, f, ensure_ascii=False, indent=2)
                            result['json_file'] = json_file
                            logger.info(f"数据保存到: {json_file}")
                        except Exception as e:
                            logger.error(f"保存JSON文件失败: {e}")

                    result['success'] = True

        except Exception as e:
            error_msg = f"处理学校 {school_id} 失败: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
            result['end_time'] = datetime.now().isoformat()

        return result

    def process_batch(self) -> List[Dict[str, Any]]:
        """处理批量任务"""
        schools = self.config['schools']
        batch_size = self.config['batch_size']

        if not schools:
            logger.warning("没有需要处理的学校")
            return []

        logger.info(f"开始批量处理 {len(schools)} 个学校，批次大小: {batch_size}")

        results = []

        # 分批处理
        for i in range(0, len(schools), batch_size):
            batch = schools[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(schools) + batch_size - 1) // batch_size

            logger.info(f"处理批次 {batch_num}/{total_batches}: {batch}")

            for school_id in batch:
                logger.info(f"处理学校: {school_id}")

                result = self.process_school(school_id)
                results.append(result)

                # 学校间延迟
                if school_id != batch[-1]:
                    delay = self.config['delay_between_schools']
                    logger.info(f"等待 {delay} 秒后处理下一个学校...")
                    time.sleep(delay)

            # 批次间额外延迟
            if i + batch_size < len(schools):
                extra_delay = self.config['delay_between_schools'] * 2
                logger.info(f"批次完成，等待 {extra_delay} 秒后继续...")
                time.sleep(extra_delay)

        self.results = results
        return results

    def generate_report(self) -> Dict[str, Any]:
        """生成处理报告"""
        if not self.results:
            return {}

        total_schools = len(self.results)
        successful = sum(1 for r in self.results if r.get('success', False))
        failed = total_schools - successful
        total_data = sum(r.get('total_data', 0) for r in self.results)

        # 错误统计
        all_errors = []
        for result in self.results:
            all_errors.extend(result.get('errors', []))

        report = {
            'timestamp': datetime.now().isoformat(),
            'total_schools': total_schools,
            'successful_schools': successful,
            'failed_schools': failed,
            'success_rate': successful / total_schools if total_schools > 0 else 0,
            'total_data_extracted': total_data,
            'error_count': len(all_errors),
            'errors': all_errors[:10],  # 只显示前10个错误
            'school_results': [
                {
                    'school_id': r['school_id'],
                    'success': r.get('success', False),
                    'data_count': r.get('total_data', 0),
                    'error_count': len(r.get('errors', []))
                }
                for r in self.results
            ]
        }

        return report

    def save_report(self, report: Dict[str, Any]):
        """保存报告到文件"""
        output_dir = self.config['output_dir']
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(output_dir, f"batch_report_{timestamp}.json")

        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"报告保存到: {report_file}")
            return report_file
        except Exception as e:
            logger.error(f"保存报告失败: {e}")
            return None

def main():
    """批量处理器主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='批量处理多个学校')
    parser.add_argument('schools_file', type=str, help='学校ID列表文件（每行一个ID）')
    parser.add_argument('-c', '--config', type=str, help='配置文件路径')
    parser.add_argument('-o', '--output', type=str, default='batch_output', help='输出目录')
    parser.add_argument('--no-db', action='store_true', help='不保存到数据库')
    parser.add_argument('--test', action='store_true', help='测试模式（只处理前2个学校）')

    args = parser.parse_args()

    # 初始化处理器
    processor = BatchProcessor(args.config)

    # 加载学校列表
    processor.load_schools_from_file(args.schools_file)

    # 更新配置
    processor.config['output_dir'] = args.output
    processor.config['save_to_database'] = not args.no_db

    if args.test:
        # 测试模式：只处理前2个学校，减少省份
        processor.config['schools'] = processor.config['schools'][:2]
        processor.config['provinces'] = processor.config['provinces'][:2]
        processor.config['years'] = processor.config['years'][:1]
        logger.info(f"测试模式：处理 {len(processor.config['schools'])} 个学校")

    # 处理批量任务
    logger.info("开始批量处理...")
    start_time = time.time()

    results = processor.process_batch()

    end_time = time.time()
    duration = end_time - start_time

    # 生成报告
    report = processor.generate_report()

    # 显示报告
    print("\n" + "=" * 60)
    print("批量处理报告")
    print("=" * 60)
    print(f"处理时间: {duration:.2f} 秒")
    print(f"处理学校: {report['total_schools']} 个")
    print(f"成功学校: {report['successful_schools']} 个")
    print(f"失败学校: {report['failed_schools']} 个")
    print(f"成功率: {report['success_rate']:.1%}")
    print(f"提取数据: {report['total_data_extracted']} 条")
    print(f"错误数量: {report['error_count']} 个")

    if report['error_count'] > 0:
        print("\n前5个错误:")
        for i, error in enumerate(report['errors'][:5], 1):
            print(f"  {i}. {error}")

    # 保存报告
    report_file = processor.save_report(report)
    if report_file:
        print(f"\n详细报告已保存: {report_file}")

    print("=" * 60)

if __name__ == "__main__":
    main()