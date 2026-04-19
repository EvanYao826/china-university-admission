#!/usr/bin/env python3
"""
调试数据解析问题
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler import GaokaoCrawler

def test_parsing():
    print("调试数据解析问题")
    print("=" * 60)

    crawler = GaokaoCrawler(headless=True)

    # 模拟从页面提取的数据（基于实际页面结构）
    print("1. 测试院校分数线解析:")

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

    # 测试_extract_numbers方法
    print("\n测试_extract_numbers方法:")
    test_texts = [
        '688/156',
        '2025',
        '本科一批',
        '普通类',
        '录取数'
    ]

    for text in test_texts:
        numbers = crawler._extract_numbers(text)
        print(f"  '{text}' -> {numbers}")

    # 测试_parse_institution_score
    print("\n测试_parse_institution_score方法:")
    result = crawler._parse_institution_score(row_data, 140, 2025, "北京")
    print(f"解析结果: {result}")

    if result:
        print(f"  min_score: {result.get('min_score')}")
        print(f"  min_rank: {result.get('min_rank')}")
        print(f"  batch: {result.get('batch')}")
        print(f"  category: {result.get('category')}")

    # 测试另一个问题：如果"最低分/最低位次"列包含年份
    print("\n2. 测试问题场景（年份在分数列）:")
    problem_row = {
        '年份': '2025',
        '录取批次': '2025',  # 批次列包含年份！
        '招生类型': '普通类',
        '最低分/最低位次': '2025/156',  # 分数列也包含年份！
        '录取数': '10'
    }

    print(f"问题数据: {problem_row}")
    result = crawler._parse_institution_score(problem_row, 140, 2025, "北京")
    print(f"解析结果: {result}")

    # 测试修复后的_extract_numbers方法
    print("\n3. 测试修复_extract_numbers方法（添加范围验证）:")

    # 当前实现
    def current_extract_numbers(text: str):
        import re
        numbers = []
        matches = re.findall(r'\d+\.?\d*', text)
        for match in matches:
            try:
                num = float(match)
                numbers.append(num)
            except:
                continue
        return numbers

    # 修复后的实现
    def fixed_extract_numbers(text: str):
        import re
        from datetime import datetime
        numbers = []
        matches = re.findall(r'\d+\.?\d*', text)
        for match in matches:
            try:
                num = float(match)

                # 过滤不合理的数字
                # 高考分数通常在200-750之间
                # 位次通常在1-1000000之间
                # 年份在2000-当前年份之间
                current_year = datetime.now().year

                # 如果是分数范围外的数字，可能是年份或其他标识
                if 200 <= num <= 750:
                    numbers.append(num)
                elif 1 <= num <= 1000000:  # 合理的位次范围
                    numbers.append(num)
                # 其他数字（如年份）不添加到分数/位次列表

            except:
                continue
        return numbers

    test_cases = [
        ('688/156', [688.0, 156.0]),
        ('2025/156', [156.0]),  # 2025被过滤掉
        ('分数: 688.5', [688.5]),
        ('位次 156', [156.0]),
        ('2025年', []),  # 年份被过滤
        ('本科一批2025年', []),  # 年份被过滤
    ]

    print("测试用例:")
    for text, expected in test_cases:
        current = current_extract_numbers(text)
        fixed = fixed_extract_numbers(text)
        print(f"  '{text}':")
        print(f"    当前: {current} (期望: {expected})")
        print(f"    修复: {fixed}")

    crawler.close_driver()

if __name__ == "__main__":
    test_parsing()