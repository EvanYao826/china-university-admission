"""
测试改进后的爬虫
"""
import sys
import os
import logging

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler import GaokaoCrawler
from database import DatabaseManager

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 设置为DEBUG以查看详细日志
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_improved.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def test_school_info_extraction():
    """测试学校信息提取"""
    print("测试学校信息提取")
    print("=" * 60)

    try:
        with GaokaoCrawler(headless=True) as crawler:
            school_info = crawler.extract_school_info("140")
            print(f"学校信息: {school_info}")

            if school_info and 'name' in school_info:
                print(f"✓ 成功提取学校名称: {school_info['name']}")
                return True
            else:
                print("✗ 未能提取学校名称")
                return False

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_province_year_selection():
    """测试省份和年份选择"""
    print("\n测试省份和年份选择")
    print("=" * 60)

    try:
        with GaokaoCrawler(headless=True) as crawler:
            # 先访问页面
            url = "https://www.gaokao.cn/school/140/provinceline"
            crawler.get_page(url)

            # 测试选择北京和2024年
            success = crawler.select_province_and_year("北京", 2024)

            if success:
                print("✓ 省份和年份选择功能正常")
            else:
                print("⚠ 省份和年份选择可能失败，但继续测试")

            # 尝试提取数据
            data = crawler.extract_admission_data("140", 2024, "北京")
            print(f"提取到 {len(data)} 条数据")

            if data:
                print("✓ 成功提取数据")
                # 显示前几条数据
                for i, item in enumerate(data[:3]):
                    print(f"  数据{i+1}: {item.get('major', '院校分数线')} - "
                          f"最低分={item.get('min_score')}, 位次={item.get('min_rank')}")
                return True
            else:
                print("⚠ 未提取到数据，可能是页面结构问题")
                return False

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_parsing():
    """测试数据解析逻辑"""
    print("\n测试数据解析逻辑")
    print("=" * 60)

    try:
        from crawler import GaokaoCrawler

        # 创建爬虫实例但不启动浏览器
        crawler = GaokaoCrawler(headless=True)

        # 测试数据解析
        test_cases = [
            {
                'name': '院校分数线数据',
                'row_data': {
                    '录取批次': '本科一批',
                    '科类/选科': '理科',
                    '最低分/最低位次': '688/156',
                    '录取数': '10'
                },
                'expected': {
                    'batch': '本科一批',
                    'category': '理科',
                    'min_score': 688.0,
                    'min_rank': 156
                }
            },
            {
                'name': '专业分数线数据',
                'row_data': {
                    '专业名称': '计算机科学与技术',
                    '最低分/最低位次': '694/72',
                    '录取数': '5',
                    '选科要求': '物理必选'
                },
                'expected': {
                    'major': '计算机科学与技术',
                    'min_score': 694.0,
                    'min_rank': 72,
                    'subject_requirements': '物理必选'
                }
            }
        ]

        all_passed = True
        for test_case in test_cases:
            print(f"\n测试: {test_case['name']}")

            # 使用通用解析方法
            result = crawler._parse_general_data(
                test_case['row_data'],
                140, 2024, "北京"
            )

            if result:
                passed = True
                for key, expected_value in test_case['expected'].items():
                    actual_value = result.get(key)
                    if actual_value != expected_value:
                        print(f"  ✗ {key}: 期望 {expected_value}, 实际 {actual_value}")
                        passed = False
                    else:
                        print(f"  ✓ {key}: {actual_value}")

                if passed:
                    print("  ✓ 测试通过")
                else:
                    print("  ✗ 测试失败")
                    all_passed = False
            else:
                print("  ✗ 解析返回None")
                all_passed = False

        # 清理
        crawler.close_driver()

        return all_passed

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_integration():
    """测试数据库集成"""
    print("\n测试数据库集成")
    print("=" * 60)

    try:
        # 测试数据库连接
        with DatabaseManager() as db:
            print("✓ 数据库连接成功")

            # 测试添加学校
            print("\n测试添加学校...")
            university_id = db.add_university(
                name="测试大学2",
                province="北京",
                type="综合",
                level="985"
            )
            print(f"✓ 添加学校成功，ID: {university_id}")

            # 测试保存数据
            print("\n测试保存数据...")
            test_data = {
                'university_id': university_id,
                'province': '北京',
                'year': 2024,
                'category': '理科',
                'batch': '本科一批',
                'enrollment_type': '普通类',
                'major': '测试专业',
                'min_score': 700.0,
                'min_rank': 100,
                'source_url': 'https://www.gaokao.cn/school/140/provinceline'
            }

            data_id = db.save_undergraduate_admission_data(test_data)
            print(f"✓ 保存数据成功，ID: {data_id}")

            # 清理测试数据
            print("\n清理测试数据...")
            db.execute_query("DELETE FROM undergraduate_admissions WHERE university_id = ?", (university_id,))
            db.execute_query("DELETE FROM universities WHERE id = ?", (university_id,))
            db.commit()
            print("✓ 测试数据清理完成")

            return True

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("改进爬虫测试")
    print("=" * 60)

    tests = [
        ("学校信息提取", test_school_info_extraction),
        ("省份年份选择", test_province_year_selection),
        ("数据解析逻辑", test_data_parsing),
        ("数据库集成", test_database_integration)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"✓ {test_name} 测试通过")
            else:
                print(f"⚠ {test_name} 测试有问题")
        except Exception as e:
            print(f"✗ {test_name} 测试异常: {e}")
            results.append((test_name, False))

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print("-" * 40)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✓ 通过" if success else "⚠ 有问题"
        print(f"{test_name:20} {status}")

    print("-" * 40)
    print(f"总计: {passed}/{total} 项测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！改进的爬虫可以正常使用。")
        print("\n使用建议:")
        print("1. 运行完整爬取: python main.py 140")
        print("2. 指定年份省份: python main.py 140 -y 2024 -p 北京")
        print("3. 查看详细日志: 检查 test_improved.log 文件")
    else:
        print("\n⚠ 部分测试有问题，请检查上述信息。")
        print("建议先运行测试模式: python main.py 140 --test")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)