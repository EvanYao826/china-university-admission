#!/usr/bin/env python3
"""
测试修复后的代码
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler import GaokaoCrawler

def test_fixes():
    print("测试修复后的数据解析")
    print("=" * 60)

    crawler = GaokaoCrawler(headless=True)

    # 测试新格式表格数据
    print("1. 测试新格式院校分数线解析:")

    # 实际表格数据：['2025', '本科一批', '普通类', '688/156', '录取数']
    # 表头：['年份', '录取批次', '招生类型', '最低分/最低位次', '录取数']
    row_data = {
        '年份': '2025',
        '录取批次': '本科一批',
        '招生类型': '普通类',
        '最低分/最低位次': '688/156',
        '录取数': '录取数'
    }

    print(f"原始数据: {row_data}")

    # 测试新解析方法
    print("\n测试_parse_institution_score_v2方法:")
    result = crawler._parse_institution_score_v2(row_data, 140, 2025, "北京")
    print(f"解析结果: {result}")

    if result:
        print(f"  min_score: {result.get('min_score')} (期望: 688.0)")
        print(f"  min_rank: {result.get('min_rank')} (期望: 156)")
        print(f"  batch: {result.get('batch')} (期望: 本科一批)")
        print(f"  category: {result.get('category')}")
        print(f"  enrollment_type: {result.get('enrollment_type')} (期望: 普通类)")

    # 测试问题数据
    print("\n2. 测试问题数据（年份在分数列）:")
    problem_row = {
        '年份': '2025',
        '录取批次': '2025',  # 批次列包含年份！
        '招生类型': '普通类',
        '最低分/最低位次': '2025/156',  # 分数列也包含年份！
        '录取数': '10'
    }

    print(f"问题数据: {problem_row}")
    result = crawler._parse_institution_score_v2(problem_row, 140, 2025, "北京")
    print(f"解析结果: {result}")

    if result:
        print(f"  min_score: {result.get('min_score')} (期望: None 或 156)")
        print(f"  min_rank: {result.get('min_rank')} (期望: 156)")

    # 测试_extract_numbers_with_validation方法
    print("\n3. 测试_extract_numbers_with_validation方法:")

    test_cases = [
        ('688/156', [688.0, 156.0]),
        ('2025/156', [156.0]),  # 2025被过滤掉
        ('分数: 688.5', [688.5]),
        ('位次 156', [156.0]),
        ('2025年', []),  # 年份被过滤
        ('本科一批2025年', []),  # 年份被过滤
        ('150/2000000', [150.0]),  # 2000000超出位次范围
        ('100/50', []),  # 100低于分数范围，50低于位次范围
    ]

    print("测试用例:")
    for text, expected in test_cases:
        result = crawler._extract_numbers_with_validation(text)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{text}': {result} (期望: {expected})")

    # 测试_standardize_row_data方法的选择逻辑
    print("\n4. 测试_standardize_row_data方法选择逻辑:")

    test_cases = [
        {
            'name': '新格式（年份+批次）',
            'row_data': {'年份': '2025', '录取批次': '本科一批', '招生类型': '普通类', '最低分/最低位次': '688/156'},
            'expected_parser': 'v2'
        },
        {
            'name': '旧格式（批次+科类）',
            'row_data': {'录取批次': '本科一批', '科类/选科': '理科', '最低分/最低位次': '688/156', '录取数': '10'},
            'expected_parser': 'v1'
        },
        {
            'name': '专业格式',
            'row_data': {'专业名称': '计算机', '最低分/最低位次': '694/72', '录取数': '5', '选科要求': '物理必选'},
            'expected_parser': 'major'
        },
        {
            'name': '通用格式',
            'row_data': {'col1': '数据1', 'col2': '数据2'},
            'expected_parser': 'general'
        }
    ]

    for test in test_cases:
        headers = list(test['row_data'].keys())
        has_batch = any('批次' in h for h in headers)
        has_year = any('年份' in h for h in headers)
        has_category = any('科类' in h or '选科' in h for h in headers)
        has_major = any('专业' in h for h in headers)

        print(f"\n  {test['name']}:")
        print(f"    表头: {headers}")
        print(f"    有批次: {has_batch}, 有年份: {has_year}, 有科类: {has_category}, 有专业: {has_major}")
        print(f"    预期解析器: {test['expected_parser']}")

    crawler.close_driver()

    print("\n" + "=" * 60)
    print("测试完成")

if __name__ == "__main__":
    test_fixes()