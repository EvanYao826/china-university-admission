#!/usr/bin/env python3
"""
集成测试修复
"""
import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from crawler import GaokaoCrawler

def test_integration():
    print("集成测试修复")
    print("=" * 60)

    crawler = GaokaoCrawler(headless=True)

    # 测试新格式数据
    print("1. 测试新格式表格数据解析:")

    # 模拟实际页面数据
    row_data_v2 = {
        '年份': '2025',
        '录取批次': '本科一批',
        '招生类型': '普通类',
        '最低分/最低位次': '688/156',
        '录取数': '录取数'
    }

    print(f"测试数据: {row_data_v2}")

    # 测试_standardize_row_data选择逻辑
    print("\n测试_standardize_row_data选择:")
    result = crawler._standardize_row_data(row_data_v2, '140', 2025, "北京")

    if result:
        print(f"解析结果:")
        print(f"  university_id: {result['university_id']} (类型: {type(result['university_id'])})")
        print(f"  min_score: {result['min_score']}")
        print(f"  min_rank: {result['min_rank']}")
        print(f"  batch: {result['batch']}")
        print(f"  category: {result['category']}")
        print(f"  enrollment_type: {result['enrollment_type']}")

        # 验证
        assert result['university_id'] == 140, f"university_id应该是140，实际是{result['university_id']}"
        assert result['min_score'] == 688.0, f"min_score应该是688.0，实际是{result['min_score']}"
        assert result['min_rank'] == 156, f"min_rank应该是156，实际是{result['min_rank']}"
        assert result['batch'] == '本科一批', f"batch应该是'本科一批'，实际是{result['batch']}"
        print("✓ 所有断言通过")
    else:
        print("✗ 解析失败")

    # 测试问题数据
    print("\n2. 测试问题数据:")
    problem_data = {
        '年份': '2025',
        '录取批次': '2025',  # 批次列包含年份
        '招生类型': '普通类',
        '最低分/最低位次': '2025/156',  # 分数列包含年份
        '录取数': '10'
    }

    print(f"问题数据: {problem_data}")
    result = crawler._standardize_row_data(problem_data, '140', 2025, "北京")

    if result:
        print(f"解析结果:")
        print(f"  min_score: {result['min_score']} (应该为None或156)")
        print(f"  min_rank: {result['min_rank']} (应该为156)")

        # 2025不应该被解析为分数
        if result['min_score'] is not None:
            assert result['min_score'] != 2025.0, "min_score不应该为2025.0"

        # 位次应该是156
        if result['min_rank'] is not None:
            assert result['min_rank'] == 156, f"min_rank应该是156，实际是{result['min_rank']}"

        print("✓ 问题数据验证通过")
    else:
        print("✗ 问题数据解析失败")

    # 测试专业表格数据
    print("\n3. 测试专业表格数据:")
    major_data = {
        '专业名称': '工科试验班（机械航空与动力类，土木水利与海洋工程，建筑类，能源与电气类，计算机类）选科要求物化选一',
        '最低分/最低位次': '694/72',
        '录取数': '录取数'
    }

    print(f"专业数据: {major_data}")
    result = crawler._standardize_row_data(major_data, '140', 2025, "北京")

    if result:
        print(f"解析结果:")
        print(f"  major: {result['major'][:50]}...")
        print(f"  min_score: {result['min_score']}")
        print(f"  min_rank: {result['min_rank']}")
        print(f"  subject_requirements: {result['subject_requirements']}")
        print("✓ 专业数据解析成功")
    else:
        print("✗ 专业数据解析失败")

    crawler.close_driver()

    print("\n" + "=" * 60)
    print("集成测试完成")

if __name__ == "__main__":
    test_integration()