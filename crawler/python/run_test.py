import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler import GaokaoCrawler

crawler = GaokaoCrawler(headless=True)

# Test the new method
row_data = {
    '年份': '2025',
    '录取批次': '本科一批',
    '招生类型': '普通类',
    '最低分/最低位次': '688/156',
    '录取数': '录取数'
}

print("Testing _parse_institution_score_v2:")
result = crawler._parse_institution_score_v2(row_data, 140, 2025, "北京")
print(f"Result: {result}")

print("\nTesting _extract_numbers_with_validation:")
test_texts = [
    ('688/156', [688.0, 156.0]),
    ('2025/156', [156.0]),
    ('2025年', []),
]

for text, expected in test_texts:
    result = crawler._extract_numbers_with_validation(text)
    print(f"  '{text}': {result} (expected: {expected})")

crawler.close_driver()