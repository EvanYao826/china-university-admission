#!/usr/bin/env python3
"""
分析页面中的表格数据
"""
import re
import sys
import os

def analyze_page_source():
    """分析页面源码中的表格"""
    filepath = "page_sources/page_source_140_2025_北京_20260419_154513.html"

    if not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    print("分析页面源码中的表格数据...")
    print("=" * 60)

    # 查找所有表格
    table_pattern = r'<table[^>]*>(.*?)</table>'
    tables = re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)

    print(f"找到 {len(tables)} 个表格")

    for i, table_html in enumerate(tables[:3]):  # 只看前3个表格
        print(f"\n表格 {i+1}:")
        print("-" * 40)

        # 查找表格行
        row_pattern = r'<tr[^>]*>(.*?)</tr>'
        rows = re.findall(row_pattern, table_html, re.DOTALL | re.IGNORECASE)

        print(f"  行数: {len(rows)}")

        # 显示前几行内容
        for j, row_html in enumerate(rows[:5]):
            # 提取单元格内容
            cell_pattern = r'<t[dh][^>]*>(.*?)</t[dh]>'
            cells = re.findall(cell_pattern, row_html, re.DOTALL | re.IGNORECASE)

            # 清理HTML标签
            clean_cells = []
            for cell in cells:
                # 移除HTML标签
                clean = re.sub(r'<[^>]+>', '', cell)
                # 移除多余空白
                clean = re.sub(r'\s+', ' ', clean).strip()
                clean_cells.append(clean)

            if clean_cells:
                print(f"  行 {j+1}: {clean_cells}")

    # 查找包含"批次"、"科类"、"分数"等关键词的文本
    print("\n查找关键词:")
    keywords = ['批次', '科类', '最低分', '专业', '录取数', '选科要求']

    for keyword in keywords:
        pattern = rf'[^>]*{keyword}[^<]*'
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            print(f"  {keyword}: 找到 {len(matches)} 处")
            for match in matches[:3]:
                print(f"    - {match[:100]}...")

    # 查找数字模式（分数/位次）
    print("\n查找数字模式:")
    number_patterns = [
        r'(\d+)\s*/\s*(\d+)',  # 688/156 格式
        r'(\d+(?:\.\d+)?)\s*分',  # 688分 格式
        r'位次\s*(\d+)'  # 位次156 格式
    ]

    for pattern in number_patterns:
        matches = re.findall(pattern, content)
        if matches:
            print(f"  模式 '{pattern}': 找到 {len(matches)} 处")
            for match in matches[:5]:
                print(f"    - {match}")

if __name__ == "__main__":
    analyze_page_source()