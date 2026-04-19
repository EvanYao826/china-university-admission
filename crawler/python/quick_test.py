"""
快速测试爬虫核心功能
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("快速测试爬虫改进")
print("=" * 60)

# 测试1: 导入模块
print("1. 测试模块导入...")
try:
    from crawler import GaokaoCrawler
    from database import DatabaseManager
    print("✓ 模块导入成功")
except Exception as e:
    print(f"✗ 模块导入失败: {e}")
    sys.exit(1)

# 测试2: 数据库连接
print("\n2. 测试数据库连接...")
try:
    db = DatabaseManager()
    db.connect()

    # 检查表
    cursor = db.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    required_tables = ['universities', 'undergraduate_admissions']
    missing = [t for t in required_tables if t not in tables]

    if missing:
        print(f"✗ 缺少表: {missing}")
    else:
        print(f"✓ 数据库表正常: {tables}")

    db.close()
except Exception as e:
    print(f"✗ 数据库连接失败: {e}")

# 测试3: 数据解析逻辑
print("\n3. 测试数据解析逻辑...")
try:
    crawler = GaokaoCrawler(headless=True)

    # 测试数字提取
    test_texts = [
        ("688/156", [688.0, 156.0]),
        ("分数: 688.5", [688.5]),
        ("位次 156", [156.0]),
        ("688分, 156位", [688.0, 156.0])
    ]

    all_passed = True
    for text, expected in test_texts:
        result = crawler._extract_numbers(text)
        if result == expected:
            print(f"  ✓ '{text}' -> {result}")
        else:
            print(f"  ✗ '{text}' -> {result} (期望: {expected})")
            all_passed = False

    if all_passed:
        print("✓ 数字提取测试通过")
    else:
        print("✗ 数字提取测试失败")

    crawler.close_driver()
except Exception as e:
    print(f"✗ 数据解析测试失败: {e}")

# 测试4: 模拟数据标准化
print("\n4. 测试数据标准化...")
try:
    crawler = GaokaoCrawler(headless=True)

    # 测试院校分数线解析
    institution_data = {
        '录取批次': '本科一批',
        '科类/选科': '理科',
        '最低分/最低位次': '688/156',
        '录取数': '10'
    }

    result = crawler._parse_institution_score(institution_data, 140, 2024, "北京")
    if result:
        print(f"✓ 院校分数线解析成功:")
        print(f"  批次: {result['batch']}")
        print(f"  科类: {result['category']}")
        print(f"  分数: {result['min_score']}")
        print(f"  位次: {result['min_rank']}")
    else:
        print("✗ 院校分数线解析失败")

    # 测试专业分数线解析
    major_data = {
        '专业名称': '计算机科学与技术',
        '最低分/最低位次': '694/72',
        '录取数': '5',
        '选科要求': '物理必选'
    }

    result = crawler._parse_major_score(major_data, 140, 2024, "北京")
    if result:
        print(f"\n✓ 专业分数线解析成功:")
        print(f"  专业: {result['major']}")
        print(f"  分数: {result['min_score']}")
        print(f"  位次: {result['min_rank']}")
        print(f"  选科: {result['subject_requirements']}")
    else:
        print("\n✗ 专业分数线解析失败")

    crawler.close_driver()
except Exception as e:
    print(f"✗ 数据标准化测试失败: {e}")

print("\n" + "=" * 60)
print("快速测试完成")
print("\n下一步:")
print("1. 运行测试模式: python main.py 140 --test")
print("2. 查看日志文件: crawler.log")
print("3. 如果测试失败，检查 page_sources/ 目录下的页面源码")