"""
分析保存的页面源码
"""
import re

# 读取页面源码
with open('page_sources/page_source_140_2025_北京_20260419_154513.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("页面分析报告")
print("=" * 60)

# 1. 检查标题
title_match = re.search(r'<title>(.*?)</title>', content)
if title_match:
    print(f"页面标题: {title_match.group(1)}")

# 2. 查找学校名称
school_patterns = [
    r'清华大学',
    r'北京大学',
    r'中国农业大学',
    r'<h[1-6][^>]*>(.*?)</h[1-6]>',
    r'class=".*?school.*?">(.*?)<',
    r'class=".*?name.*?">(.*?)<'
]

print("\n可能的学校名称:")
for pattern in school_patterns:
    matches = re.findall(pattern, content, re.IGNORECASE)
    if matches:
        for match in matches[:3]:  # 只显示前3个
            if len(match) > 2 and len(match) < 50:
                print(f"  - {match}")

# 3. 查找表格
table_count = content.count('<table')
print(f"\n表格数量: {table_count}")

if table_count > 0:
    # 提取表格内容
    tables = re.findall(r'<table[^>]*>(.*?)</table>', content, re.DOTALL)
    print(f"找到 {len(tables)} 个完整表格")

    for i, table in enumerate(tables[:2]):  # 只分析前2个表格
        print(f"\n表格 {i+1} 预览:")
        # 清理HTML标签
        clean_text = re.sub(r'<[^>]+>', ' ', table)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        print(f"  {clean_text[:200]}...")

# 4. 查找数据相关元素
data_keywords = ['分数线', '录取', '分数', '位次', '批次', '科类', '专业']
print("\n数据相关关键词出现次数:")
for keyword in data_keywords:
    count = content.count(keyword)
    if count > 0:
        print(f"  {keyword}: {count} 次")

# 5. 查找JavaScript数据
print("\nJavaScript数据片段:")
js_patterns = [
    r'data:\s*\{[^}]*\}',
    r'props:\s*\{[^}]*\}',
    r'state:\s*\{[^}]*\}',
    r'var\s+\w+\s*=\s*\{[^}]*\}'
]

for pattern in js_patterns:
    matches = re.findall(pattern, content, re.DOTALL)
    if matches:
        for match in matches[:2]:
            print(f"  JS数据: {match[:100]}...")

# 6. 查找省份选择器
province_patterns = [
    r'北京|天津|河北|山西|内蒙古|辽宁|吉林|黑龙江|上海|江苏|浙江|安徽|福建|江西|山东|河南|湖北|湖南|广东|广西|海南|重庆|四川|贵州|云南|西藏|陕西|甘肃|青海|宁夏|新疆'
]
print("\n页面中的省份:")
all_provinces = set()
for pattern in province_patterns:
    matches = re.findall(pattern, content)
    all_provinces.update(matches)

for province in sorted(all_provinces):
    print(f"  - {province}")

# 7. 查找年份选择器
year_pattern = r'20[0-9]{2}'
years = re.findall(year_pattern, content)
unique_years = sorted(set(years))
print(f"\n页面中的年份: {unique_years[:10]}")

# 8. 检查交互元素
interactive_elements = ['select', 'option', 'button', 'click', 'onclick', 'dropdown', 'tab']
print("\n交互元素:")
for element in interactive_elements:
    if element in content.lower():
        print(f"  - 找到 {element} 元素")

print("\n" + "=" * 60)
print("分析完成")