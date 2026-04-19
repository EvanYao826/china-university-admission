"""
爬虫核心模块 - 使用Selenium处理JavaScript渲染
"""
import time
import logging
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from .config import HEADERS, MAX_RETRIES, RETRY_DELAY, TIMEOUT, SCHOOL_URL_TEMPLATE

logger = logging.getLogger(__name__)

class GaokaoCrawler:
    """高考数据爬虫"""

    def __init__(self, headless: bool = True):
        """
        初始化爬虫

        Args:
            headless: 是否使用无头模式
        """
        self.headless = headless
        self.driver = None
        self.wait = None

    def setup_driver(self):
        """设置WebDriver"""
        try:
            chrome_options = Options()

            if self.headless:
                chrome_options.add_argument("--headless")

            # 基本配置
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")

            # 模拟真实浏览器
            chrome_options.add_argument(f"user-agent={HEADERS['User-Agent']}")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")

            # 禁用自动化控制标志
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # 使用webdriver-manager自动管理驱动
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # 隐藏自动化特征
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            self.wait = WebDriverWait(self.driver, TIMEOUT)
            logger.info("WebDriver初始化成功")

        except Exception as e:
            logger.error(f"WebDriver初始化失败: {e}")
            raise

    def close_driver(self):
        """关闭WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("WebDriver已关闭")

    def __enter__(self):
        self.setup_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_driver()

    def get_page(self, url: str, retry_count: int = 0) -> bool:
        """
        获取页面内容

        Args:
            url: 目标URL
            retry_count: 重试次数

        Returns:
            bool: 是否成功
        """
        if retry_count >= MAX_RETRIES:
            logger.error(f"达到最大重试次数: {url}")
            return False

        try:
            logger.info(f"正在访问: {url}")
            self.driver.get(url)

            # 等待页面加载完成
            time.sleep(3)  # 基础等待

            # 检查页面是否正常加载
            if "javascript" in self.driver.page_source.lower() and "启用" in self.driver.page_source:
                logger.warning("页面可能依赖JavaScript，尝试等待更长时间")
                time.sleep(5)

            # 等待主要内容加载
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                logger.warning("页面加载超时，但继续处理")

            logger.info(f"页面加载成功: {url}")
            return True

        except Exception as e:
            logger.error(f"页面访问失败 (尝试 {retry_count + 1}/{MAX_RETRIES}): {e}")
            time.sleep(RETRY_DELAY * (retry_count + 1))
            return self.get_page(url, retry_count + 1)

    def extract_school_info(self, school_id: str) -> Dict[str, Any]:
        """
        提取学校基本信息

        Args:
            school_id: 学校ID

        Returns:
            学校信息字典
        """
        url = SCHOOL_URL_TEMPLATE.format(school_id=school_id)

        if not self.get_page(url):
            return {}

        try:
            info = {
                'school_id': school_id,
                'url': url
            }

            # 尝试提取学校名称
            try:
                # 查找可能的标题元素
                title_selectors = [
                    "h1", "h2", ".school-name", ".title",
                    "[class*='name']", "[class*='title']"
                ]

                for selector in title_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            text = element.text.strip()
                            if text and len(text) < 50:  # 合理的标题长度
                                info['name'] = text
                                logger.info(f"找到学校名称: {text}")
                                break
                        if 'name' in info:
                            break
                    except:
                        continue
            except Exception as e:
                logger.warning(f"提取学校名称失败: {e}")

            # 提取页面其他有用信息
            info['page_title'] = self.driver.title
            info['page_source_length'] = len(self.driver.page_source)

            logger.info(f"学校信息提取完成: {info.get('name', '未知')}")
            return info

        except Exception as e:
            logger.error(f"提取学校信息失败: {e}")
            return {}

    def extract_admission_data(self, school_id: str, year: int, province: str) -> List[Dict[str, Any]]:
        """
        提取录取数据

        Args:
            school_id: 学校ID
            year: 年份
            province: 省份

        Returns:
            录取数据列表
        """
        url = SCHOOL_URL_TEMPLATE.format(school_id=school_id)

        if not self.get_page(url):
            return []

        data_list = []
        try:
            logger.info(f"开始提取数据 - 学校: {school_id}, 年份: {year}, 省份: {province}")

            # 方法1: 查找表格数据
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            logger.info(f"找到 {len(tables)} 个表格")

            for i, table in enumerate(tables):
                try:
                    table_data = self._parse_table(table, school_id, year, province)
                    if table_data:
                        data_list.extend(table_data)
                        logger.info(f"表格 {i+1} 解析成功，提取到 {len(table_data)} 条数据")
                except Exception as e:
                    logger.warning(f"解析表格 {i+1} 失败: {e}")

            # 方法2: 查找列表数据
            if not data_list:
                list_data = self._find_list_data(school_id, year, province)
                if list_data:
                    data_list.extend(list_data)
                    logger.info(f"从列表提取到 {len(list_data)} 条数据")

            # 方法3: 尝试查找特定元素
            if not data_list:
                element_data = self._find_element_data(school_id, year, province)
                if element_data:
                    data_list.extend(element_data)
                    logger.info(f"从元素提取到 {len(element_data)} 条数据")

            # 如果没有找到数据，保存页面源码供分析
            if not data_list:
                logger.warning("未找到表格数据，保存页面源码供分析")
                self._save_page_source(school_id, year, province)

            logger.info(f"数据提取完成，共 {len(data_list)} 条记录")
            return data_list

        except Exception as e:
            logger.error(f"提取录取数据失败: {e}")
            return []

    def _parse_table(self, table, school_id: int, year: int, province: str) -> List[Dict[str, Any]]:
        """解析表格数据"""
        data_list = []

        try:
            # 获取表头
            headers = []
            header_rows = table.find_elements(By.TAG_NAME, "th")
            if not header_rows:
                header_rows = table.find_elements(By.TAG_NAME, "td")

            for header in header_rows:
                text = header.text.strip()
                if text:
                    headers.append(text)

            if not headers:
                return []

            # 获取数据行
            rows = table.find_elements(By.TAG_NAME, "tr")

            for row in rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= len(headers):
                        row_data = {}
                        for j, cell in enumerate(cells[:len(headers)]):
                            header = headers[j] if j < len(headers) else f"col_{j}"
                            row_data[header] = cell.text.strip()

                        # 转换为标准格式
                        standardized = self._standardize_row_data(row_data, school_id, year, province)
                        if standardized:
                            data_list.append(standardized)
                except Exception as e:
                    logger.debug(f"解析行失败: {e}")
                    continue

        except Exception as e:
            logger.warning(f"表格解析失败: {e}")

        return data_list

    def _standardize_row_data(self, row_data: Dict[str, str],
                             school_id: int, year: int, province: str) -> Optional[Dict[str, Any]]:
        """标准化行数据"""
        try:
            # 尝试识别批次
            batch = None
            batch_keywords = {
                '本科一批': ['一批', '一本', '第一批'],
                '本科二批': ['二批', '二本', '第二批'],
                '本科三批': ['三批', '三本', '第三批'],
                '专科批': ['专科', '高职'],
                '提前批': ['提前', '提前批']
            }

            for batch_name, keywords in batch_keywords.items():
                for value in row_data.values():
                    if any(keyword in value for keyword in keywords):
                        batch = batch_name
                        break
                if batch:
                    break

            if not batch:
                batch = '本科一批'  # 默认值

            # 尝试识别科目类型
            category = '理科'  # 默认值
            for value in row_data.values():
                if '文科' in value:
                    category = '文科'
                    break
                elif '综合' in value:
                    category = '综合改革'
                    break

            # 提取分数
            min_score = avg_score = max_score = None
            min_rank = avg_rank = max_rank = None
            admission_count = None

            for key, value in row_data.items():
                # 分数提取
                if '分数' in key or '分' in key:
                    numbers = self._extract_numbers(value)
                    if numbers:
                        if '最低' in key or 'min' in key.lower():
                            min_score = numbers[0]
                        elif '平均' in key or 'avg' in key.lower():
                            avg_score = numbers[0]
                        elif '最高' in key or 'max' in key.lower():
                            max_score = numbers[0]
                        else:
                            if min_score is None:
                                min_score = numbers[0]
                            elif avg_score is None:
                                avg_score = numbers[0]
                            elif max_score is None:
                                max_score = numbers[0]

                # 位次提取
                elif '位次' in key or '排名' in key or 'rank' in key.lower():
                    numbers = self._extract_numbers(value)
                    if numbers:
                        if '最低' in key or 'min' in key.lower():
                            min_rank = numbers[0]
                        elif '平均' in key or 'avg' in key.lower():
                            avg_rank = numbers[0]
                        elif '最高' in key or 'max' in key.lower():
                            max_rank = numbers[0]

                # 人数提取
                elif '人数' in key or '计划' in key:
                    numbers = self._extract_numbers(value)
                    if numbers:
                        admission_count = numbers[0]

            # 专业名称
            major = None
            for value in row_data.values():
                if len(value) > 2 and len(value) < 50:  # 合理的专业名称长度
                    # 排除明显的非专业名称
                    if not any(x in value for x in ['分数', '位次', '排名', '人数', '计划', '批次']):
                        major = value
                        break

            standardized = {
                'university_id': school_id,
                'year': year,
                'province': province,
                'category': category,
                'batch': batch,
                'min_score': min_score,
                'avg_score': avg_score,
                'max_score': max_score,
                'min_rank': min_rank,
                'avg_rank': avg_rank,
                'max_rank': max_rank,
                'admission_count': admission_count,
                'major': major,
                'notes': str(row_data)  # 保存原始数据供参考
            }

            # 至少需要有一些数据
            if any([min_score, avg_score, max_score, min_rank, avg_rank, max_rank, admission_count]):
                return standardized

        except Exception as e:
            logger.debug(f"数据标准化失败: {e}")

        return None

    def _extract_numbers(self, text: str) -> List[float]:
        """从文本中提取数字"""
        import re
        numbers = []
        # 匹配整数和小数
        matches = re.findall(r'\d+\.?\d*', text)
        for match in matches:
            try:
                num = float(match)
                numbers.append(num)
            except:
                continue
        return numbers

    def _find_list_data(self, school_id: int, year: int, province: str) -> List[Dict[str, Any]]:
        """查找列表数据"""
        data_list = []
        # 实现列表数据查找逻辑
        return data_list

    def _find_element_data(self, school_id: int, year: int, province: str) -> List[Dict[str, Any]]:
        """查找元素数据"""
        data_list = []
        # 实现元素数据查找逻辑
        return data_list

    def _save_page_source(self, school_id: int, year: int, province: str):
        """保存页面源码供分析"""
        try:
            import os
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"page_source_{school_id}_{year}_{province}_{timestamp}.html"
            directory = "page_sources"

            if not os.path.exists(directory):
                os.makedirs(directory)

            filepath = os.path.join(directory, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)

            logger.info(f"页面源码已保存: {filepath}")
        except Exception as e:
            logger.error(f"保存页面源码失败: {e}")

    def crawl_school_data(self, school_id: str, years: List[int],
                         provinces: List[str]) -> Dict[str, Any]:
        """
        爬取学校数据

        Args:
            school_id: 学校ID
            years: 年份列表
            provinces: 省份列表

        Returns:
            爬取结果统计
        """
        results = {
            'school_id': school_id,
            'total_provinces': len(provinces),
            'total_years': len(years),
            'data_extracted': 0,
            'errors': [],
            'province_results': {}
        }

        # 先获取学校基本信息
        school_info = self.extract_school_info(school_id)
        results['school_info'] = school_info

        # 遍历省份和年份
        for province in provinces:
            province_results = {
                'province': province,
                'years_processed': 0,
                'data_count': 0,
                'errors': []
            }

            for year in years:
                try:
                    logger.info(f"开始爬取: 学校={school_id}, 省份={province}, 年份={year}")

                    data = self.extract_admission_data(school_id, year, province)

                    if data:
                        province_results['data_count'] += len(data)
                        results['data_extracted'] += len(data)
                        logger.info(f"成功提取 {len(data)} 条数据")
                    else:
                        logger.warning(f"未提取到数据")

                    province_results['years_processed'] += 1

                    # 避免请求过快
                    time.sleep(1)

                except Exception as e:
                    error_msg = f"省份={province}, 年份={year}: {e}"
                    logger.error(error_msg)
                    province_results['errors'].append(error_msg)
                    results['errors'].append(error_msg)

            results['province_results'][province] = province_results

        logger.info(f"爬取完成: 学校={school_id}, 提取数据={results['data_extracted']}条")
        return results