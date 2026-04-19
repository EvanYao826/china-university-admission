"""
高级使用示例 - 直接使用模块API
"""
import sys
import os
import logging
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler import GaokaoCrawler
from database import DatabaseManager
from utils import generate_data_summary, save_to_json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def advanced_crawling():
    """高级爬取示例：完全控制爬取过程"""
    print("高级爬取示例")
    print("=" * 60)

    school_id = "140"
    years = [2023, 2022]
    provinces = ["北京", "上海", "广东"]

    all_data = []

    # 使用上下文管理器自动管理资源
    with GaokaoCrawler(headless=True) as crawler:
        # 1. 获取学校信息
        print("1. 获取学校基本信息...")
        school_info = crawler.extract_school_info(school_id)
        print(f"学校信息: {school_info}")

        # 2. 逐省份爬取
        for province in provinces:
            print(f"\n2. 爬取省份: {province}")

            province_data = []

            for year in years:
                print(f"   年份: {year}")

                try:
                    # 爬取数据
                    data = crawler.extract_admission_data(school_id, year, province)

                    if data:
                        print(f"   提取到 {len(data)} 条数据")
                        province_data.extend(data)

                        # 显示前几条数据
                        for i, item in enumerate(data[:2]):
                            print(f"      {i+1}. {item.get('major', '院校分数线')}: "
                                  f"最低分={item.get('min_score')}, "
                                  f"批次={item.get('batch')}")
                    else:
                        print("   未提取到数据")

                    # 请求间隔
                    time.sleep(2)

                except Exception as e:
                    print(f"   爬取失败: {e}")
                    continue

            all_data.extend(province_data)

    # 3. 数据统计
    print("\n3. 数据统计")
    print("-" * 40)

    if all_data:
        summary = generate_data_summary(all_data)

        print(f"总记录数: {summary['total_records']}")
        print(f"年份范围: {summary['years']}")
        print(f"省份数量: {len(summary['provinces'])}")
        print(f"科目类型: {summary['categories']}")
        print(f"批次类型: {summary['batches']}")

        if summary['score_stats']['count'] > 0:
            print(f"分数统计: 最低={summary['score_stats']['min']:.1f}, "
                  f"最高={summary['score_stats']['max']:.1f}, "
                  f"平均={summary['score_stats']['avg']:.1f}")
    else:
        print("未提取到任何数据")

    # 4. 保存数据
    print("\n4. 保存数据")
    print("-" * 40)

    if all_data:
        # 保存到JSON文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = f"advanced_data_{school_id}_{timestamp}.json"

        if save_to_json(all_data, json_file):
            print(f"数据已保存到: {json_file}")

        # 保存到数据库
        try:
            with DatabaseManager() as db:
                saved_ids = db.batch_save_admission_data(all_data)
                print(f"成功保存 {len(saved_ids)} 条数据到数据库")

                # 获取统计信息
                stats = db.get_admission_stats()
                print(f"数据库统计: {stats}")

        except Exception as e:
            print(f"保存到数据库失败: {e}")

    print("\n高级爬取示例完成！")
    print("=" * 60)

def incremental_crawling():
    """增量爬取示例：只爬取新数据"""
    print("\n增量爬取示例")
    print("=" * 60)

    school_id = "140"
    years = [2023]  # 只爬取最新年份
    provinces = ["北京", "上海"]

    # 连接数据库检查现有数据
    with DatabaseManager() as db:
        existing_stats = db.get_admission_stats()

        print(f"数据库现有数据:")
        print(f"  总记录数: {existing_stats['total_records']}")
        print(f"  省份数量: {existing_stats['province_count']}")
        print(f"  年份范围: {existing_stats['min_year']} - {existing_stats['max_year']}")

        new_data_count = 0

        with GaokaoCrawler(headless=True) as crawler:
            for province in provinces:
                for year in years:
                    # 检查数据是否已存在
                    # 这里简化检查，实际应该检查更具体的条件
                    print(f"\n检查: 省份={province}, 年份={year}")

                    # 假设需要爬取
                    print(f"开始爬取...")

                    try:
                        data = crawler.extract_admission_data(school_id, year, province)

                        if data:
                            # 过滤可能已存在的数据
                            filtered_data = []
                            for item in data:
                                # 简单检查：如果专业名称为空，可能是院校分数线
                                if not item.get('major'):
                                    # 检查院校分数线是否已存在
                                    exists = db.check_data_exists(
                                        school_id, year, province,
                                        item['category'], item['batch'], None
                                    )
                                    if not exists:
                                        filtered_data.append(item)
                                else:
                                    # 检查专业分数线是否已存在
                                    exists = db.check_data_exists(
                                        school_id, year, province,
                                        item['category'], item['batch'], item['major']
                                    )
                                    if not exists:
                                        filtered_data.append(item)

                            if filtered_data:
                                print(f"  发现 {len(filtered_data)} 条新数据")
                                saved_ids = db.batch_save_admission_data(filtered_data)
                                new_data_count += len(saved_ids)
                                print(f"  保存 {len(saved_ids)} 条新数据到数据库")
                            else:
                                print("  没有新数据")

                        time.sleep(2)

                    except Exception as e:
                        print(f"  爬取失败: {e}")
                        continue

        print(f"\n增量爬取完成，新增 {new_data_count} 条记录")

    print("\n增量爬取示例完成！")
    print("=" * 60)

def error_handling_example():
    """错误处理示例"""
    print("\n错误处理示例")
    print("=" * 60)

    # 测试各种错误情况
    test_cases = [
        {"school_id": "99999", "desc": "不存在的学校ID"},
        {"school_id": "140", "year": 1990, "desc": "无效年份"},
        {"school_id": "invalid", "desc": "无效学校ID格式"},
    ]

    for test_case in test_cases:
        print(f"\n测试: {test_case['desc']}")
        print("-" * 40)

        try:
            with GaokaoCrawler(headless=True) as crawler:
                # 尝试获取学校信息
                info = crawler.extract_school_info(test_case['school_id'])
                print(f"结果: {info}")

                if not info:
                    print("预期结果: 返回空字典")

        except Exception as e:
            print(f"异常: {type(e).__name__}: {e}")

        time.sleep(1)

    print("\n错误处理示例完成！")
    print("=" * 60)

def performance_test():
    """性能测试示例"""
    print("\n性能测试示例")
    print("=" * 60)

    import time

    school_id = "140"
    provinces = ["北京", "上海"]  # 测试用少量省份

    start_time = time.time()

    with GaokaoCrawler(headless=True) as crawler:
        total_data = 0

        for province in provinces:
            province_start = time.time()

            print(f"测试省份: {province}")

            # 测试不同年份
            for year in [2023, 2022]:
                year_start = time.time()

                try:
                    data = crawler.extract_admission_data(school_id, year, province)
                    elapsed = time.time() - year_start

                    if data:
                        print(f"  年份 {year}: {len(data)} 条数据, 耗时: {elapsed:.2f}秒")
                        total_data += len(data)
                    else:
                        print(f"  年份 {year}: 无数据, 耗时: {elapsed:.2f}秒")

                except Exception as e:
                    print(f"  年份 {year}: 错误 - {e}")

                time.sleep(1)

            province_elapsed = time.time() - province_start
            print(f"省份 {province} 总耗时: {province_elapsed:.2f}秒\n")

    total_elapsed = time.time() - start_time

    print(f"性能测试结果:")
    print(f"  总耗时: {total_elapsed:.2f}秒")
    print(f"  总数据: {total_data} 条")
    print(f"  平均每条数据耗时: {total_elapsed/max(total_data, 1):.2f}秒")

    print("\n性能测试完成！")
    print("=" * 60)

def main():
    """运行所有高级示例"""
    print("高考数据爬虫系统 - 高级使用示例")
    print("=" * 60)

    # 运行示例
    advanced_crawling()
    incremental_crawling()
    error_handling_example()
    performance_test()

    print("\n所有高级示例执行完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()