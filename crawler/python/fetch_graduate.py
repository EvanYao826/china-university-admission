#!/usr/bin/env python3
"""
研究生录取数据爬虫示例
从研招网和各校官网抓取研究生录取数据

注意：本代码仅供学习参考，实际使用时请遵守网站robots.txt和法律法规
"""

import requests
import pandas as pd
import sqlite3
import time
import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class GraduateRecord:
    """研究生录取记录"""
    university_name: str
    year: int
    major: str
    degree_type: str  # 硕士/博士
    study_mode: str   # 全日制/非全日制
    admission_count: int
    min_score: Optional[float] = None
    avg_score: Optional[float] = None
    max_score: Optional[float] = None
    notes: Optional[str] = None


class GraduateCrawler:
    """研究生数据爬虫基类"""

    def __init__(self, db_path: str = "../data/university.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })

    def fetch_university_data(self, university_name: str, year: int) -> List[GraduateRecord]:
        """
        获取指定高校和年份的研究生数据
        需要子类实现具体的抓取逻辑
        """
        raise NotImplementedError("子类必须实现此方法")

    def parse_admission_page(self, html: str) -> List[GraduateRecord]:
        """
        解析录取公示页面
        这是一个通用解析器，子类可以重写
        """
        soup = BeautifulSoup(html, 'html.parser')
        records = []

        # 这里是一个示例解析逻辑
        # 实际项目中需要根据具体网站结构调整

        # 查找表格
        tables = soup.find_all('table')
        for table in tables:
            try:
                # 尝试解析表格数据
                rows = table.find_all('tr')[1:]  # 跳过表头
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        record = GraduateRecord(
                            university_name="",  # 需要在外部设置
                            year=0,  # 需要在外部设置
                            major=self._clean_text(cols[0].text),
                            degree_type=self._parse_degree_type(cols[1].text),
                            study_mode=self._parse_study_mode(cols[2].text),
                            admission_count=self._parse_number(cols[3].text),
                            notes="自动解析"
                        )
                        records.append(record)
            except Exception as e:
                logger.warning(f"解析表格失败: {e}")
                continue

        return records

    def _clean_text(self, text: str) -> str:
        """清理文本"""
        return re.sub(r'\s+', ' ', text).strip()

    def _parse_degree_type(self, text: str) -> str:
        """解析学位类型"""
        text = text.lower()
        if '博士' in text:
            return '博士'
        elif '硕士' in text:
            return '硕士'
        else:
            return '硕士'  # 默认

    def _parse_study_mode(self, text: str) -> str:
        """解析学习方式"""
        text = text.lower()
        if '非全' in text or '在职' in text:
            return '非全日制'
        else:
            return '全日制'

    def _parse_number(self, text: str) -> int:
        """解析数字"""
        try:
            # 提取数字
            numbers = re.findall(r'\d+', text)
            if numbers:
                return int(numbers[0])
        except:
            pass
        return 0

    def save_to_database(self, records: List[GraduateRecord]):
        """保存数据到SQLite数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 确保表存在
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS graduate_admissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                university_id INTEGER,
                year INTEGER,
                major TEXT,
                degree_type TEXT,
                study_mode TEXT,
                admission_count INTEGER,
                min_score REAL,
                avg_score REAL,
                max_score REAL,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (university_id) REFERENCES universities(id)
            )
        ''')

        for record in records:
            # 先查找高校ID
            cursor.execute(
                "SELECT id FROM universities WHERE name LIKE ?",
                (f"%{record.university_name}%",)
            )
            result = cursor.fetchone()

            if result:
                university_id = result[0]

                # 插入数据
                cursor.execute('''
                    INSERT OR REPLACE INTO graduate_admissions
                    (university_id, year, major, degree_type, study_mode,
                     admission_count, min_score, avg_score, max_score, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    university_id, record.year, record.major, record.degree_type,
                    record.study_mode, record.admission_count,
                    record.min_score, record.avg_score, record.max_score,
                    record.notes
                ))

        conn.commit()
        conn.close()
        logger.info(f"已保存 {len(records)} 条研究生记录到数据库")

    def run(self, universities: List[str], years: List[int]):
        """运行爬虫"""
        all_records = []

        for university in universities:
            for year in years:
                logger.info(f"正在抓取 {university} {year}年 研究生数据...")
                try:
                    records = self.fetch_university_data(university, year)
                    # 设置高校名称和年份
                    for record in records:
                        record.university_name = university
                        record.year = year
                    all_records.extend(records)
                    logger.info(f"抓取到 {len(records)} 条记录")
                    time.sleep(3)  # 礼貌延迟
                except Exception as e:
                    logger.error(f"抓取 {university} {year}年 数据失败: {e}")

        if all_records:
            self.save_to_database(all_records)

        return all_records


class ExampleUniversityCrawler(GraduateCrawler):
    """示例高校爬虫（模拟数据）"""

    def fetch_university_data(self, university_name: str, year: int) -> List[GraduateRecord]:
        """
        示例实现：实际项目中需要根据具体网站实现
        这里返回模拟数据
        """
        # 常见专业列表
        majors = [
            "计算机科学与技术", "软件工程", "电子信息工程",
            "机械工程", "材料科学与工程", "电气工程",
            "经济学", "金融学", "工商管理",
            "法学", "临床医学", "药学",
            "数学", "物理学", "化学",
            "外国语言文学", "新闻传播学", "教育学"
        ]

        records = []
        for i, major in enumerate(majors[:10]):  # 只取前10个专业
            base_count = 20 + i * 3
            base_score = 350 + i * 5

            # 硕士
            records.append(GraduateRecord(
                university_name=university_name,
                year=year,
                major=major,
                degree_type="硕士",
                study_mode="全日制",
                admission_count=base_count,
                min_score=base_score - 10,
                avg_score=base_score,
                max_score=base_score + 10,
                notes=f"模拟数据 - {university_name} {year}年"
            ))

            # 部分专业有博士
            if i % 3 == 0:
                records.append(GraduateRecord(
                    university_name=university_name,
                    year=year,
                    major=major,
                    degree_type="博士",
                    study_mode="全日制",
                    admission_count=max(5, base_count // 4),
                    min_score=base_score + 5,
                    avg_score=base_score + 15,
                    max_score=base_score + 25,
                    notes=f"模拟数据 - {university_name} {year}年"
                ))

            # 部分专业有非全日制硕士
            if i % 4 == 0:
                records.append(GraduateRecord(
                    university_name=university_name,
                    year=year,
                    major=major,
                    degree_type="硕士",
                    study_mode="非全日制",
                    admission_count=max(10, base_count // 2),
                    min_score=base_score - 20,
                    avg_score=base_score - 10,
                    max_score=base_score,
                    notes=f"模拟数据 - {university_name} {year}年（非全日制）"
                ))

        return records


def main():
    """主函数"""
    print("=" * 60)
    print("研究生录取数据爬虫示例")
    print("=" * 60)
    print("注意：本代码仅供学习参考")
    print("实际使用时请遵守网站规定和法律法规")
    print("=" * 60)

    # 创建爬虫实例
    crawler = ExampleUniversityCrawler()

    # 配置抓取参数
    universities = [
        "清华大学",
        "北京大学",
        "浙江大学",
        "复旦大学",
        "上海交通大学"
    ]
    years = [2023, 2022]

    # 运行爬虫
    print(f"\n开始抓取数据...")
    print(f"高校: {', '.join(universities)}")
    print(f"年份: {', '.join(map(str, years))}")

    try:
        records = crawler.run(universities, years)
        print(f"\n✅ 抓取完成！共获取 {len(records)} 条记录")
        print(f"数据已保存到: {crawler.db_path}")

        # 按高校统计
        if records:
            print("\n📊 数据统计:")
            stats = {}
            for record in records:
                key = (record.university_name, record.year)
                if key not in stats:
                    stats[key] = 0
                stats[key] += 1

            for (uni, year), count in stats.items():
                print(f"  {uni} {year}年: {count} 条记录")

            # 显示前5条记录
            print("\n📋 示例数据:")
            for i, record in enumerate(records[:5]):
                print(f"{i+1}. {record.university_name} - {record.major}")
                print(f"   类型: {record.degree_type}{record.study_mode}")
                print(f"   招生人数: {record.admission_count}")
                if record.avg_score:
                    print(f"   平均分: {record.avg_score}")
                print()

    except Exception as e:
        print(f"\n❌ 抓取失败: {e}")
        import traceback
        traceback.print_exc()

    print("=" * 60)
    print("使用说明:")
    print("1. 修改 ExampleUniversityCrawler 类实现实际网站抓取")
    print("2. 常见数据源:")
    print("   - 研招网 (https://yz.chsi.com.cn)")
    print("   - 各高校研究生院官网")
    print("   - 各高校招生信息网")
    print("3. 注意处理动态加载内容（可能需要Selenium）")
    print("4. 尊重网站访问频率限制")
    print("=" * 60)


if __name__ == "__main__":
    main()