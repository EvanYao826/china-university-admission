"""
阳光高考网 Selenium 爬虫
用于抓取高校录取数据（院校分数线和专业分数线）

使用方法：
    python selenium_gaokao_crawler.py --school_id 140 --province 北京 --year 2025
    python selenium_gaokao_crawler.py --all  # 爬取所有学校
    python selenium_gaokao_crawler.py --school_name 清华大学  # 通过学校名称爬取
"""

import sqlite3
import time
import logging
import argparse
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

from webdriver_manager.chrome import ChromeDriverManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 数据库路径
DB_PATH = r'E:\VSproject\China-University-Admission\test_university.db'

# 网站基础URL
BASE_URL = 'https://www.gaokao.cn'
SCHOOL_URL_TEMPLATE = BASE_URL + '/school/{school_id}'

# 默认爬取的年份范围
DEFAULT_YEARS = [2025, 2024, 2023]


@dataclass
class AdmissionRecord:
    """录取数据记录"""
    university_id: int
    province: str
    year: int
    category: str
    batch: str
    enrollment_type: str
    professional_group: str
    min_score: Optional[int]
    min_rank: Optional[int]
    avg_score: Optional[int]
    major: Optional[str]
    source_url: str


class SeleniumGaokaoCrawler:
    """阳光高考网 Selenium 爬虫"""

    def __init__(self, headless: bool = True):
        """初始化爬虫
        
        Args:
            headless: 是否使用无头模式（不显示浏览器窗口）
        """
        self.driver = None
        self.headless = headless
        self.wait = None

    def setup_driver(self):
        """设置 Chrome WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        logger.info("WebDriver 初始化完成")

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            logger.info("浏览器已关闭")

    def get_school_id_by_name(self, school_name: str) -> Optional[int]:
        """通过学校名称查询学校ID
        
        Args:
            school_name: 学校名称
            
        Returns:
            学校ID，如果不存在则返回 None
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM universities WHERE name LIKE ?', (f'%{school_name}%',))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def get_university_id(self, school_id: str, school_name: str) -> Optional[int]:
        """获取或创建大学ID
        
        Args:
            school_id: 阳光高考网学校ID
            school_name: 学校名称
            
        Returns:
            大学ID
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 先尝试通过名称查找
        cursor.execute('SELECT id FROM universities WHERE name LIKE ?', (f'%{school_name}%',))
        result = cursor.fetchone()
        
        if result:
            university_id = result[0]
            logger.info(f"找到已有大学: {school_name}, ID: {university_id}")
        else:
            # 创建新记录
            cursor.execute('''
                INSERT INTO universities (name, province)
                VALUES (?, ?)
            ''', (school_name, ''))
            university_id = cursor.lastrowid
            logger.info(f"创建新大学: {school_name}, ID: {university_id}")
        
        conn.commit()
        conn.close()
        return university_id

    def insert_admission_record(self, record: AdmissionRecord):
        """插入录取记录
        
        Args:
            record: 录取数据记录
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO undergraduate_admissions (
                    university_id, province, year, category, batch,
                    enrollment_type, professional_group, min_score,
                    min_rank, avg_score, major, source_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.university_id,
                record.province,
                record.year,
                record.category,
                record.batch,
                record.enrollment_type,
                record.professional_group,
                record.min_score,
                record.min_rank,
                record.avg_score,
                record.major,
                record.source_url
            ))
            conn.commit()
            logger.debug(f"插入成功: {record.province} {record.year} {record.category}")
        except Exception as e:
            logger.error(f"插入失败: {e}")
        finally:
            conn.close()

    def wait_and_find_element(self, by: By, value: str, timeout: int = 10):
        """等待并查找元素
        
        Args:
            by: 定位方式
            value: 定位值
            timeout: 超时时间（秒）
            
        Returns:
            WebElement
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def click_element(self, by: By, value: str):
        """点击元素
        
        Args:
            by: 定位方式
            value: 定位值
        """
        element = self.wait_and_find_element(by, value)
        element.click()
        time.sleep(1)

    def select_dropdown_option(self, dropdown_xpath: str, option_text: str):
        """选择下拉框选项
        
        Args:
            dropdown_xpath: 下拉框 XPath
            option_text: 选项文本
        """
        try:
            # 点击下拉框
            dropdown = self.wait_and_find_element(By.XPATH, dropdown_xpath)
            dropdown.click()
            time.sleep(0.5)
            
            # 查找选项
            option_xpath = f"{dropdown_xpath}/following-sibling::div//li[contains(text(), '{option_text}')]"
            option = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, option_xpath))
            )
            option.click()
            time.sleep(1)
            logger.info(f"选择选项: {option_text}")
        except Exception as e:
            logger.warning(f"选择选项失败 {option_text}: {e}")

    def get_dropdown_options(self, dropdown_xpath: str) -> List[str]:
        """获取下拉框的所有选项
        
        Args:
            dropdown_xpath: 下拉框 XPath
            
        Returns:
            选项文本列表
        """
        try:
            dropdown = self.wait_and_find_element(By.XPATH, dropdown_xpath)
            dropdown.click()
            time.sleep(0.5)
            
            options_xpath = f"{dropdown_xpath}/following-sibling::div//li"
            options = self.wait_and_find_element(By.XPATH, options_xpath)
            options_elements = self.driver.find_elements(By.XPATH, options_xpath)
            
            result = [opt.text.strip() for opt in options_elements if opt.text.strip()]
            
            # 点击空白处关闭下拉框
            self.driver.find_element(By.TAG_NAME, 'body').click()
            time.sleep(0.5)
            
            return result
        except Exception as e:
            logger.warning(f"获取下拉框选项失败: {e}")
            return []

    def parse_score_table(self, table_xpath: str, is_major_table: bool = False) -> List[Dict[str, Any]]:
        """解析分数表格
        
        Args:
            table_xpath: 表格 XPath
            is_major_table: 是否为专业分数线表格
            
        Returns:
            解析后的数据列表
        """
        try:
            table = self.wait_and_find_element(By.XPATH, table_xpath)
            rows = table.find_elements(By.TAG_NAME, 'tr')
            
            data = []
            for row in rows[1:]:  # 跳过表头
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) < 4:
                    continue
                
                row_data = {
                    'professional_group': cells[0].text.strip() if len(cells) > 0 else '',
                    'subject_requirements': cells[1].text.strip() if len(cells) > 1 else '',
                    'min_score': self._parse_score(cells[2].text.strip()) if len(cells) > 2 else None,
                    'min_rank': self._parse_rank(cells[3].text.strip()) if len(cells) > 3 else None,
                    'avg_score': self._parse_score(cells[4].text.strip()) if is_major_table and len(cells) > 4 else None,
                    'major': cells[5].text.strip() if is_major_table and len(cells) > 5 else None,
                    'batch': cells[-1].text.strip() if len(cells) > 0 else '',
                    'enrollment_type': '普通类'
                }
                data.append(row_data)
            
            return data
        except Exception as e:
            logger.warning(f"解析分数表格失败: {e}")
            return []

    def _parse_score(self, text: str) -> Optional[int]:
        """解析分数文本"""
        if not text or text == '-':
            return None
        try:
            return int(text.replace(',', '').strip())
        except ValueError:
            return None

    def _parse_rank(self, text: str) -> Optional[int]:
        """解析位次文本"""
        if not text or text == '-':
            return None
        try:
            return int(text.replace(',', '').strip())
        except ValueError:
            return None

    def crawl_school_scores(self, school_id: str, school_name: str, 
                           provinces: Optional[List[str]] = None,
                           years: Optional[List[int]] = None):
        """爬取学校录取分数
        
        Args:
            school_id: 阳光高考网学校ID
            school_name: 学校名称
            provinces: 要爬取的省份列表，None 表示所有省份
            years: 要爬取的年份列表，None 表示默认年份
        """
        if years is None:
            years = DEFAULT_YEARS

        # 获取大学ID
        university_id = self.get_university_id(school_id, school_name)
        if not university_id:
            logger.error(f"无法获取大学ID: {school_name}")
            return

        # 访问学校页面
        url = SCHOOL_URL_TEMPLATE.format(school_id=school_id)
        logger.info(f"访问学校页面: {url}")
        self.driver.get(url)
        time.sleep(3)

        try:
            # 点击"历年分数"选项卡
            self.click_element(By.XPATH, '//span[contains(text(), "历年分数")]')
            time.sleep(2)

            # 获取所有省份（如果未指定）
            if provinces is None:
                provinces = self.get_dropdown_options('//div[@class="province-select"]')
                logger.info(f"找到省份列表: {provinces}")

            # 遍历省份
            for province in provinces:
                logger.info(f"正在爬取省份: {province}")
                
                # 选择省份
                self.select_dropdown_option('//div[@class="province-select"]', province)
                
                # 获取该省份的所有年份
                available_years = self.get_dropdown_options('//div[@class="year-select"]')
                if not available_years:
                    available_years = [str(y) for y in years]
                
                # 遍历年份
                for year in years:
                    year_str = str(year)
                    if year_str not in available_years:
                        continue
                    
                    logger.info(f"正在爬取年份: {year}")
                    
                    # 选择年份
                    self.select_dropdown_option('//div[@class="year-select"]', year_str)
                    
                    # 获取该年份的所有科类
                    categories = self.get_dropdown_options('//div[@class="category-select"]')
                    if not categories:
                        categories = ['综合']
                    
                    # 遍历科类
                    for category in categories:
                        logger.info(f"正在爬科目: {category}")
                        
                        # 选择科类
                        self.select_dropdown_option('//div[@class="category-select"]', category)
                        time.sleep(1)
                        
                        # 抓取院校分数线
                        self.crawl_school_table(university_id, province, year, category, url)
                        
                        # 抓取专业分数线
                        self.crawl_major_table(university_id, province, year, category, url)
                        
        except Exception as e:
            logger.error(f"爬取过程出错: {e}")

    def crawl_school_table(self, university_id: int, province: str, 
                          year: int, category: str, source_url: str):
        """抓取院校分数线表格
        
        Args:
            university_id: 大学ID
            province: 省份
            year: 年份
            category: 科类
            source_url: 数据来源URL
        """
        try:
            # 等待表格加载
            table_xpath = '//table[contains(@class, "school-score-table")]'
            self.wait_and_find_element(By.XPATH, table_xpath, timeout=5)
            
            # 解析表格
            rows_data = self.parse_score_table(table_xpath, is_major_table=False)
            
            for row in rows_data:
                record = AdmissionRecord(
                    university_id=university_id,
                    province=province,
                    year=year,
                    category=category,
                    batch=row.get('batch', ''),
                    enrollment_type=row.get('enrollment_type', '普通类'),
                    professional_group=row.get('professional_group', ''),
                    min_score=row.get('min_score'),
                    min_rank=row.get('min_rank'),
                    avg_score=None,
                    major=None,
                    source_url=source_url
                )
                self.insert_admission_record(record)
                
        except TimeoutException:
            logger.warning(f"院校分数线表格未找到或超时: {province} {year} {category}")
        except Exception as e:
            logger.error(f"抓取院校分数线失败: {e}")

    def crawl_major_table(self, university_id: int, province: str,
                         year: int, category: str, source_url: str):
        """抓取专业分数线表格
        
        Args:
            university_id: 大学ID
            province: 省份
            year: 年份
            category: 科类
            source_url: 数据来源URL
        """
        try:
            # 点击"专业分数线"选项卡
            self.click_element(By.XPATH, '//span[contains(text(), "专业分数线")]')
            time.sleep(2)
            
            # 等待表格加载
            table_xpath = '//table[contains(@class, "major-score-table")]'
            self.wait_and_find_element(By.XPATH, table_xpath, timeout=5)
            
            # 解析表格
            rows_data = self.parse_score_table(table_xpath, is_major_table=True)
            
            for row in rows_data:
                record = AdmissionRecord(
                    university_id=university_id,
                    province=province,
                    year=year,
                    category=category,
                    batch=row.get('batch', ''),
                    enrollment_type=row.get('enrollment_type', '普通类'),
                    professional_group=row.get('professional_group', ''),
                    min_score=row.get('min_score'),
                    min_rank=row.get('min_rank'),
                    avg_score=row.get('avg_score'),
                    major=row.get('major'),
                    source_url=source_url
                )
                self.insert_admission_record(record)
                
        except TimeoutException:
            logger.warning(f"专业分数线表格未找到或超时: {province} {year} {category}")
        except Exception as e:
            logger.error(f"抓取专业分数线失败: {e}")

    def run(self, school_id: Optional[str] = None, school_name: Optional[str] = None,
            provinces: Optional[List[str]] = None, years: Optional[List[int]] = None):
        """运行爬虫
        
        Args:
            school_id: 阳光高考网学校ID
            school_name: 学校名称（用于查找school_id）
            provinces: 要爬取的省份列表
            years: 要爬取的年份列表
        """
        try:
            self.setup_driver()
            
            # 如果没有提供 school_id，尝试通过学校名称查找
            if not school_id and school_name:
                # 这里需要先访问搜索页面获取 school_id
                # 简化处理：直接使用学校名称作为查询
                logger.info(f"通过学校名称查找: {school_name}")
                school_id = input("请输入学校ID（或按回车使用搜索）: ") or None
            
            if not school_id:
                logger.error("必须提供 school_id 或 school_name")
                return
            
            self.crawl_school_scores(school_id, school_name or school_id, provinces, years)
            
        finally:
            self.close()


def main():
    parser = argparse.ArgumentParser(description='阳光高考网 Selenium 爬虫')
    parser.add_argument('--school_id', type=str, help='阳光高考网学校ID')
    parser.add_argument('--school_name', type=str, help='学校名称（用于查找ID）')
    parser.add_argument('--province', type=str, help='要爬取的省份')
    parser.add_argument('--year', type=int, help='要爬取的年份')
    parser.add_argument('--all', action='store_true', help='爬取所有学校')
    parser.add_argument('--headless', action='store_true', default=True, help='使用无头模式')
    
    args = parser.parse_args()
    
    # 构建省份和年份列表
    provinces = [args.province] if args.province else None
    years = [args.year] if args.year else None
    
    # 创建并运行爬虫
    crawler = SeleniumGaokaoCrawler(headless=args.headless)
    
    if args.school_id:
        crawler.run(school_id=args.school_id, school_name=args.school_name,
                   provinces=provinces, years=years)
    elif args.school_name:
        crawler.run(school_name=args.school_name, provinces=provinces, years=years)
    elif args.all:
        # 爬取所有学校
        # 这里需要从数据库获取所有学校列表
        logger.info("开始爬取所有学校...")
        # TODO: 实现爬取所有学校的逻辑
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
