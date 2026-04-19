"""
修复数据解析问题
"""
import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from crawler import GaokaoCrawler

def analyze_data_parsing():
    """分析数据解析问题"""
    print("分析数据解析问题")
    print("=" * 60)

    # 从错误日志看，问题可能是：
    # 1. university_id应该是整数但传入了字符串
    # 2. 年份被误解析为分数（min_score: 2025.0）

    # 测试数据解析
    crawler = GaokaoCrawler(headless=True)

    # 测试用例1：院校分数线数据
    print("\n测试用例1: 院校分数线数据")
    test_data_1 = {
        '录取批次': '本科一批',
        '科类/选科': '理科',
        '最低分/最低位次': '688/156',
        '录取数': '10'
    }

    result = crawler._parse_institution_score(test_data_1, 140, 2024, "北京")
    print(f"解析结果: {result}")

    if result:
        print(f"  university_id类型: {type(result['university_id'])}")
        print(f"  min_score值: {result['min_score']} (类型: {type(result['min_score'])})")
        print(f"  min_rank值: {result['min_rank']} (类型: {type(result['min_rank'])})")

    # 测试用例2：可能的问题数据
    print("\n测试用例2: 可能的问题数据")
    test_data_2 = {
        '录取批次': '2025',
        '科类/选科': '理科',
        '最低分/最低位次': '2025/156',  # 年份被误认为分数
        '录取数': '10'
    }

    result = crawler._parse_institution_score(test_data_2, 140, 2024, "北京")
    print(f"解析结果: {result}")

    # 测试数字提取
    print("\n测试数字提取:")
    test_texts = [
        '688/156',
        '2025/156',  # 这可能被误解析
        '2025年',
        '分数: 688'
    ]

    for text in test_texts:
        numbers = crawler._extract_numbers(text)
        print(f"  '{text}' -> {numbers}")

    crawler.close_driver()

def fix_extract_numbers():
    """修复数字提取方法"""
    print("\n修复数字提取方法")
    print("=" * 60)

    # 当前问题：年份2025被提取为分数
    # 解决方案：过滤掉不合理的分数（高考分数通常在200-750之间）

    original_code = '''
    def _extract_numbers(self, text: str) -> List[float]:
        """从文本中提取数字"""
        import re
        numbers = []
        # 匹配整数和小数
        matches = re.findall(r'\\d+\\.?\\d*', text)
        for match in matches:
            try:
                num = float(match)
                numbers.append(num)
            except:
                continue
        return numbers
    '''

    fixed_code = '''
    def _extract_numbers(self, text: str) -> List[float]:
        """从文本中提取数字"""
        import re
        numbers = []
        # 匹配整数和小数
        matches = re.findall(r'\\d+\\.?\\d*', text)
        for match in matches:
            try:
                num = float(match)

                # 过滤不合理的数字
                # 高考分数通常在200-750之间
                # 位次通常在1-1000000之间
                # 年份在2000-当前年份之间
                current_year = 2026  # 应该从datetime获取

                # 如果是分数范围外的数字，可能是年份或其他标识
                if 200 <= num <= 750:
                    numbers.append(num)
                elif 1 <= num <= 1000000:  # 合理的位次范围
                    numbers.append(num)
                # 其他数字（如年份）不添加到分数/位次列表

            except:
                continue
        return numbers
    '''

    print("原始代码:")
    print(original_code)
    print("\n修复后的代码:")
    print(fixed_code)

def create_quick_fix():
    """创建快速修复"""
    print("\n创建快速修复方案")
    print("=" * 60)

    fix_suggestions = """
    需要修复的问题：

    1. university_id类型问题
       - 问题：传入字符串'140'，但数据库期望整数
       - 修复：在保存数据前转换为整数

    2. 年份误解析为分数
       - 问题：2025被提取为min_score
       - 修复：在_extract_numbers方法中添加合理性检查

    3. 学校信息保存
       - 问题：学校信息缺少必要字段
       - 修复：提供合理的默认值或从其他来源获取

    立即修复步骤：

    1. 修改_extract_numbers方法，添加分数范围检查
    2. 在main.py中确保university_id为整数
    3. 完善学校信息保存逻辑

    临时解决方案：

    可以先运行爬虫但不保存数据，检查提取的数据是否正确：
    python main.py 140 --test --no-save

    然后手动检查提取的数据质量。
    """

    print(fix_suggestions)

def main():
    """主函数"""
    print("数据解析问题分析和修复")
    print("=" * 60)

    analyze_data_parsing()
    fix_extract_numbers()
    create_quick_fix()

    print("\n" + "=" * 60)
    print("建议的修复步骤：")
    print("1. 先运行测试模式查看数据：python main.py 140 --test --no-save")
    print("2. 检查提取的数据是否正确")
    print("3. 根据问题修改相应代码")
    print("4. 重新测试直到数据正确")
    print("5. 运行完整爬取：python main.py 140")

if __name__ == "__main__":
    main()