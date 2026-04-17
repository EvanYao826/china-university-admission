#!/usr/bin/env python3
"""
PDF解析工具
使用LLM解析PDF格式的录取分数线

注意：需要OpenAI API密钥或其他LLM服务
"""

import os
import json
import re
import pandas as pd
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

# 尝试导入PDF处理库
try:
    import PyPDF2
    PDF2_AVAILABLE = True
except ImportError:
    PDF2_AVAILABLE = False
    print("警告: PyPDF2 未安装，部分功能受限")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    print("警告: pdfplumber 未安装，部分功能受限")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class PDFAdmissionRecord:
    """从PDF解析的录取记录"""
    university_name: str
    province: str
    year: int
    category: str  # 文科/理科/综合改革
    batch: str     # 本科一批/本科二批/专科批/提前批
    score: Optional[float] = None
    rank: Optional[int] = None
    admission_count: Optional[int] = None
    major: Optional[str] = None
    confidence: float = 0.0  # 解析置信度
    source_text: Optional[str] = None


class PDFParser:
    """PDF解析器基类"""

    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.use_llm = bool(self.openai_api_key)

    def extract_text(self, pdf_path: str) -> str:
        """从PDF提取文本"""
        text = ""

        # 方法1: 使用pdfplumber（更准确）
        if PDFPLUMBER_AVAILABLE:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                logger.info(f"使用pdfplumber提取文本，共 {len(text)} 字符")
                return text
            except Exception as e:
                logger.warning(f"pdfplumber提取失败: {e}")

        # 方法2: 使用PyPDF2（备用）
        if PDF2_AVAILABLE:
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                logger.info(f"使用PyPDF2提取文本，共 {len(text)} 字符")
                return text
            except Exception as e:
                logger.warning(f"PyPDF2提取失败: {e}")

        raise Exception("无法提取PDF文本，请安装pdfplumber或PyPDF2")

    def parse_with_rules(self, text: str, university: str, province: str, year: int) -> List[PDFAdmissionRecord]:
        """
        使用规则解析文本
        适用于格式规范的PDF
        """
        records = []

        # 常见关键词
        keywords = {
            'batch': ['本科一批', '本科二批', '专科批', '提前批', '一批', '二批', '专科'],
            'category': ['文科', '理科', '综合改革', '文史', '理工', '艺术', '体育'],
            'score': ['分数线', '最低分', '最高分', '平均分', '分数', '分'],
            'rank': ['位次', '排名', '名次'],
            'count': ['计划', '招生', '录取', '人数']
        }

        # 按行分割
        lines = text.split('\n')

        current_batch = None
        current_category = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检测批次
            for batch_keyword in keywords['batch']:
                if batch_keyword in line:
                    current_batch = self._normalize_batch(batch_keyword)
                    break

            # 检测类别
            for category_keyword in keywords['category']:
                if category_keyword in line:
                    current_category = self._normalize_category(category_keyword)
                    break

            # 提取数字（分数、位次、人数）
            numbers = self._extract_numbers(line)
            if numbers and current_batch and current_category:
                # 尝试解析记录
                record = self._parse_line(
                    line, numbers, university, province, year,
                    current_batch, current_category
                )
                if record:
                    records.append(record)

        return records

    def _normalize_batch(self, batch: str) -> str:
        """标准化批次名称"""
        if '一批' in batch or '本科一批' in batch:
            return '本科一批'
        elif '二批' in batch or '本科二批' in batch:
            return '本科二批'
        elif '专科' in batch or '专科批' in batch:
            return '专科批'
        elif '提前' in batch or '提前批' in batch:
            return '提前批'
        return batch

    def _normalize_category(self, category: str) -> str:
        """标准化类别名称"""
        if '文史' in category:
            return '文科'
        elif '理工' in category:
            return '理科'
        return category

    def _extract_numbers(self, text: str) -> List[float]:
        """从文本提取数字"""
        # 匹配整数和小数
        pattern = r'\d+\.?\d*'
        numbers = []
        for match in re.finditer(pattern, text):
            try:
                num = float(match.group())
                numbers.append(num)
            except ValueError:
                continue
        return numbers

    def _parse_line(self, line: str, numbers: List[float],
                   university: str, province: str, year: int,
                   batch: str, category: str) -> Optional[PDFAdmissionRecord]:
        """解析单行文本"""
        if len(numbers) >= 1:
            # 假设第一个数字是分数
            score = numbers[0]

            # 尝试提取位次（通常是大数字）
            rank = None
            for num in numbers:
                if num > 1000 and num < 1000000:  # 合理的位次范围
                    rank = int(num)
                    break

            # 尝试提取人数（通常是较小的整数）
            count = None
            for num in numbers:
                if 1 <= num <= 1000 and num != score and (rank is None or num != rank):
                    count = int(num)
                    break

            return PDFAdmissionRecord(
                university_name=university,
                province=province,
                year=year,
                category=category,
                batch=batch,
                score=score,
                rank=rank,
                admission_count=count,
                source_text=line[:200],  # 保存部分原文
                confidence=0.7  # 规则解析的置信度
            )
        return None

    def parse_with_llm(self, text: str, university: str, province: str, year: int) -> List[PDFAdmissionRecord]:
        """
        使用LLM解析文本
        需要OpenAI API密钥
        """
        if not self.use_llm:
            logger.warning("未配置OpenAI API密钥，无法使用LLM解析")
            return []

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)

            # 构建提示
            prompt = f"""请从以下文本中提取高校录取数据，文本来自{province}{year}年高考录取分数线PDF：

{text[:3000]}  # 限制文本长度

请提取{university}的录取数据，包括：
1. 录取批次（本科一批、本科二批、专科批、提前批）
2. 科类（文科、理科、综合改革、艺术、体育）
3. 分数线（分数）
4. 位次（如果有）
5. 招生人数（如果有）

请以JSON数组格式返回，每个对象包含：
- batch: 批次
- category: 科类
- score: 分数线
- rank: 位次（可选）
- admission_count: 招生人数（可选）
- confidence: 提取置信度(0-1)

只返回JSON数组，不要其他内容。"""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的数据提取助手，擅长从文本中提取结构化数据。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )

            result_text = response.choices[0].message.content

            # 解析JSON响应
            try:
                data = json.loads(result_text)
                records = []
                for item in data:
                    record = PDFAdmissionRecord(
                        university_name=university,
                        province=province,
                        year=year,
                        category=item.get('category', ''),
                        batch=item.get('batch', ''),
                        score=item.get('score'),
                        rank=item.get('rank'),
                        admission_count=item.get('admission_count'),
                        confidence=item.get('confidence', 0.8)
                    )
                    records.append(record)
                return records
            except json.JSONDecodeError as e:
                logger.error(f"解析LLM响应失败: {e}")
                return []

        except Exception as e:
            logger.error(f"LLM解析失败: {e}")
            return []

    def parse_pdf(self, pdf_path: str, university: str, province: str, year: int) -> List[PDFAdmissionRecord]:
        """解析PDF文件"""
        logger.info(f"开始解析PDF: {pdf_path}")

        # 提取文本
        text = self.extract_text(pdf_path)
        if not text:
            logger.warning("未提取到文本")
            return []

        # 方法1: 使用LLM解析（如果可用）
        if self.use_llm:
            logger.info("使用LLM解析...")
            llm_records = self.parse_with_llm(text, university, province, year)
            if llm_records:
                logger.info(f"LLM解析到 {len(llm_records)} 条记录")
                return llm_records

        # 方法2: 使用规则解析
        logger.info("使用规则解析...")
        rule_records = self.parse_with_rules(text, university, province, year)
        logger.info(f"规则解析到 {len(rule_records)} 条记录")

        return rule_records

    def save_to_csv(self, records: List[PDFAdmissionRecord], output_path: str):
        """保存到CSV文件"""
        if not records:
            logger.warning("没有记录可保存")
            return

        # 转换为字典列表
        data = []
        for record in records:
            record_dict = asdict(record)
            data.append(record_dict)

        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"已保存 {len(records)} 条记录到 {output_path}")

    def print_summary(self, records: List[PDFAdmissionRecord]):
        """打印解析摘要"""
        if not records:
            print("未解析到任何记录")
            return

        print(f"\n📊 解析摘要:")
        print(f"总记录数: {len(records)}")

        # 按批次统计
        batch_stats = {}
        category_stats = {}
        for record in records:
            batch_stats[record.batch] = batch_stats.get(record.batch, 0) + 1
            category_stats[record.category] = category_stats.get(record.category, 0) + 1

        print(f"批次分布: {batch_stats}")
        print(f"科类分布: {category_stats}")

        # 分数范围
        scores = [r.score for r in records if r.score is not None]
        if scores:
            print(f"分数范围: {min(scores):.1f} - {max(scores):.1f}")
            print(f"平均分数: {sum(scores)/len(scores):.1f}")

        # 显示前几条记录
        print(f"\n📋 示例记录 (前5条):")
        for i, record in enumerate(records[:5]):
            print(f"{i+1}. {record.university_name} - {record.batch} {record.category}")
            if record.score:
                print(f"   分数线: {record.score}")
            if record.rank:
                print(f"   位次: {record.rank}")
            if record.admission_count:
                print(f"   招生人数: {record.admission_count}")
            print(f"   置信度: {record.confidence:.2f}")
            print()


def main():
    """主函数"""
    print("=" * 60)
    print("PDF录取分数线解析工具")
    print("=" * 60)
    print("功能：")
    print("1. 从PDF提取文本")
    print("2. 使用规则解析录取数据")
    print("3. 使用LLM智能解析（需要API密钥）")
    print("4. 导出为CSV格式")
    print("=" * 60)

    # 检查依赖
    if not PDF2_AVAILABLE and not PDFPLUMBER_AVAILABLE:
        print("❌ 错误: 需要安装PDF处理库")
        print("请运行: pip install pdfplumber PyPDF2")
        return

    # 创建解析器
    openai_key = os.getenv("OPENAI_API_KEY")
    parser = PDFParser(openai_api_key=openai_key)

    if parser.use_llm:
        print("✅ 检测到OpenAI API密钥，可使用LLM解析")
    else:
        print("⚠️  未检测到OpenAI API密钥，仅使用规则解析")
        print("   设置环境变量: set OPENAI_API_KEY=your_key")

    # 示例PDF文件（实际使用时需要真实文件）
    pdf_dir = Path("pdf_samples")
    if not pdf_dir.exists():
        print(f"\n📁 创建示例目录: {pdf_dir}")
        pdf_dir.mkdir(exist_ok=True)

        # 创建示例说明文件
        readme_path = pdf_dir / "README.txt"
        readme_path.write_text("""请在此目录放置PDF文件，命名格式：
北京_2023_清华大学.pdf
浙江_2022_浙江大学.pdf

格式：省份_年份_高校名称.pdf
""")
        print(f"✅ 已创建目录，请按说明放置PDF文件")
        print(f"目录路径: {pdf_dir.absolute()}")

    print("\n📋 使用示例:")
    print("1. 将PDF文件放入 pdf_samples/ 目录")
    print("2. 按格式命名: 省份_年份_高校名称.pdf")
    print("3. 运行解析: python parse_pdf.py 北京 2023 清华大学")
    print("\n或直接调用:")
    print("from parse_pdf import PDFParser")
    print('parser = PDFParser(openai_api_key="your_key")')
    print('records = parser.parse_pdf("path/to/pdf", "清华大学", "北京", 2023)')

    print("\n" + "=" * 60)
    print("注意事项:")
    print("1. PDF文件应为文本型PDF（非扫描图片）")
    print("2. 规则解析适用于格式规范的官方文件")
    print("3. LLM解析更智能但需要API密钥")
    print("4. 结果需要人工核对")
    print("=" * 60)


if __name__ == "__main__":
    main()