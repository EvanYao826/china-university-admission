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

from config import HEADERS, MAX_RETRIES, RETRY_DELAY, TIMEOUT, SCHOOL_URL_TEMPLATE

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

            # 方法1: 从页面标题提取（更可靠）
            page_title = self.driver.title
            info['page_title'] = page_title

            # 从标题中提取学校名称（去除"历年分数线"等后缀）
            if page_title:
                # 常见后缀模式
                suffixes = ['历年分数线汇总', '历年分数线', '分数线', '|掌上高考', '-掌上高考']
                school_name = page_title
                for suffix in suffixes:
                    if suffix in school_name:
                        school_name = school_name.split(suffix)[0].strip()

                if school_name and len(school_name) < 20:  # 合理的学校名称长度
                    info['name'] = school_name
                    logger.info(f"从标题提取学校名称: {school_name}")

            # 方法2: 查找页面中的学校名称元素
            if 'name' not in info:
                try:
                    # 查找包含"大学"或"学院"的元素
                    school_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '大学') or contains(text(), '学院')]")
                    for element in school_elements:
                        text = element.text.strip()
                        if text and 2 < len(text) < 30 and ('大学' in text or '学院' in text):
                            # 过滤掉包含"分数线"、"录取"等词的文本
                            if not any(word in text for word in ['分数线', '录取', '计划', '简章', '招生']):
                                info['name'] = text
                                logger.info(f"从元素提取学校名称: {text}")
                                break
                except Exception as e:
                    logger.debug(f"查找学校元素失败: {e}")

            # 方法3: 查找h1标签
            if 'name' not in info:
                try:
                    h1_elements = self.driver.find_elements(By.TAG_NAME, "h1")
                    for element in h1_elements:
                        text = element.text.strip()
                        if text and len(text) < 50:
                            info['name'] = text
                            logger.info(f"从h1提取学校名称: {text}")
                            break
                except Exception as e:
                    logger.debug(f"查找h1失败: {e}")

            info['page_source_length'] = len(self.driver.page_source)

            logger.info(f"学校信息提取完成: {info.get('name', '未知')}")
            return info

        except Exception as e:
            logger.error(f"提取学校信息失败: {e}")
            return {}

    def select_province_and_year(self, province: str, year: int) -> bool:
        """
        选择省份和年份

        Args:
            province: 省份名称
            year: 年份

        Returns:
            bool: 是否选择成功
        """
        try:
            logger.info(f"尝试选择省份: {province}, 年份: {year}")

            # 等待页面加载完成
            time.sleep(2)

            # 方法1: 尝试查找并选择省份下拉框
            try:
                # 查找包含"省份"或"地区"的选择框
                province_selectors = [
                    "select[placeholder*='省']",
                    "select[placeholder*='地区']",
                    "select[title*='省']",
                    "select[title*='地区']",
                    ".province-select",
                    ".area-select",
                    "select"
                ]

                province_selected = False
                for selector in province_selectors:
                    try:
                        selects = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for select in selects:
                            try:
                                # 尝试选择省份
                                from selenium.webdriver.support.select import Select
                                select_obj = Select(select)

                                # 尝试按可见文本选择
                                try:
                                    select_obj.select_by_visible_text(province)
                                    province_selected = True
                                    logger.info(f"通过下拉框选择省份: {province}")
                                    break
                                except:
                                    # 尝试按值选择
                                    try:
                                        select_obj.select_by_value(province)
                                        province_selected = True
                                        logger.info(f"通过值选择省份: {province}")
                                        break
                                    except:
                                        continue
                            except:
                                continue
                        if province_selected:
                            break
                    except:
                        continue

                if not province_selected:
                    logger.warning("未找到省份选择框，尝试其他方法")

            except Exception as e:
                logger.debug(f"选择省份失败: {e}")

            # 方法2: 尝试查找并选择年份
            try:
                year_selectors = [
                    "select[placeholder*='年']",
                    "select[title*='年']",
                    ".year-select",
                    "select"
                ]

                year_selected = False
                for selector in year_selectors:
                    try:
                        selects = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for select in selects:
                            try:
                                from selenium.webdriver.support.select import Select
                                select_obj = Select(select)

                                # 尝试选择年份
                                year_str = str(year)
                                try:
                                    select_obj.select_by_visible_text(year_str)
                                    year_selected = True
                                    logger.info(f"选择年份: {year}")
                                    break
                                except:
                                    try:
                                        select_obj.select_by_value(year_str)
                                        year_selected = True
                                        logger.info(f"通过值选择年份: {year}")
                                        break
                                    except:
                                        continue
                            except:
                                continue
                        if year_selected:
                            break
                    except:
                        continue

                if not year_selected:
                    logger.warning("未找到年份选择框")

            except Exception as e:
                logger.debug(f"选择年份失败: {e}")

            # 等待数据加载
            time.sleep(3)

            # 检查是否有查询/搜索按钮需要点击
            try:
                search_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), '查询') or contains(text(), '搜索') or contains(text(), '确认')]")
                for button in search_buttons:
                    try:
                        button.click()
                        logger.info("点击查询按钮")
                        time.sleep(2)  # 等待查询结果
                        break
                    except:
                        continue
            except:
                pass

            return True

        except Exception as e:
            logger.error(f"选择省份和年份失败: {e}")
            return False

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

        # 先尝试选择省份和年份
        self.select_province_and_year(province, year)

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

            # 方法2: 如果没有表格，尝试查找其他数据容器
            if not data_list:
                data_list = self._find_alternative_data(school_id, year, province)

            # 如果没有找到数据，保存页面源码供分析
            if not data_list:
                logger.warning("未找到表格数据，保存页面源码供分析")
                self._save_page_source(school_id, year, province)

            logger.info(f"数据提取完成，共 {len(data_list)} 条记录")
            return data_list

        except Exception as e:
            logger.error(f"提取录取数据失败: {e}")
            return []

    def _parse_table(self, table, school_id: str, year: int, province: str) -> List[Dict[str, Any]]:
        """解析表格数据"""
        data_list = []

        try:
            # 获取表格所有行
            rows = table.find_elements(By.TAG_NAME, "tr")
            if len(rows) < 2:  # 至少要有表头和数据行
                return []

            # 获取表头
            headers = []
            header_cells = rows[0].find_elements(By.TAG_NAME, "th")
            if not header_cells:
                header_cells = rows[0].find_elements(By.TAG_NAME, "td")

            for cell in header_cells:
                text = cell.text.strip()
                if text:
                    headers.append(text)

            logger.debug(f"表格表头: {headers}")

            # 如果表头为空，尝试从第一行数据推断
            if not headers and len(rows) > 1:
                first_data_cells = rows[1].find_elements(By.TAG_NAME, "td")
                if first_data_cells:
                    # 根据常见格式推断表头
                    cell_texts = [cell.text.strip() for cell in first_data_cells]
                    if any('批次' in text for text in cell_texts):
                        headers = ['录取批次', '科类/选科', '最低分/最低位次', '录取数']
                    elif any('专业' in text for text in cell_texts):
                        headers = ['专业名称', '最低分/最低位次', '录取数', '选科要求']

            # 解析数据行（从第二行开始）
            for i in range(1, len(rows)):
                try:
                    cells = rows[i].find_elements(By.TAG_NAME, "td")
                    if not cells:
                        continue

                    # 构建行数据字典
                    row_data = {}
                    for j, cell in enumerate(cells):
                        if j < len(headers):
                            row_data[headers[j]] = cell.text.strip()
                        else:
                            row_data[f"col_{j}"] = cell.text.strip()

                    logger.debug(f"行数据 {i}: {row_data}")

                    # 转换为标准格式
                    standardized = self._standardize_row_data(row_data, school_id, year, province)
                    if standardized:
                        data_list.append(standardized)
                        logger.debug(f"标准化数据: {standardized}")

                except Exception as e:
                    logger.debug(f"解析行 {i} 失败: {e}")
                    continue

            logger.info(f"表格解析完成，提取到 {len(data_list)} 条数据")

        except Exception as e:
            logger.warning(f"表格解析失败: {e}")

        return data_list

    def _standardize_row_data(self, row_data: Dict[str, str],
                             school_id: int, year: int, province: str) -> Optional[Dict[str, Any]]:
        """标准化行数据 - 适配实际页面格式"""
        try:
            # 调试：记录原始数据
            logger.debug(f"原始行数据: {row_data}")

            # 根据表头类型采用不同的解析策略
            headers = list(row_data.keys())
            logger.debug(f"表头: {headers}")

            # 策略1: 院校分数线格式 (年份, 录取批次, 招生类型, 最低分/最低位次, 录取数)
            # 新格式：包含"年份"和"录取批次"，可能没有"科类/选科"
            has_batch = any('批次' in h for h in headers)
            has_year = any('年份' in h for h in headers)
            has_category = any('科类' in h or '选科' in h for h in headers)
            has_major = any('专业' in h for h in headers)

            logger.debug(f"解析策略判断: 有批次={has_batch}, 有年份={has_year}, 有科类={has_category}, 有专业={has_major}")

            if has_batch and has_year:
                logger.debug("使用策略1: _parse_institution_score_v2 (新格式)")
                return self._parse_institution_score_v2(row_data, school_id, year, province)

            # 策略2: 旧院校分数线格式 (录取批次, 科类/选科, 最低分/最低位次, 录取数)
            elif has_batch and has_category:
                logger.debug("使用策略2: _parse_institution_score (旧格式)")
                return self._parse_institution_score(row_data, school_id, year, province)

            # 策略3: 专业分数线格式 (专业名称, 最低分/最低位次, 录取数, 选科要求)
            elif has_major:
                logger.debug("使用策略3: _parse_major_score (专业格式)")
                return self._parse_major_score(row_data, school_id, year, province)

            # 策略4: 通用解析
            else:
                logger.debug("使用策略4: _parse_general_data (通用格式)")
                return self._parse_general_data(row_data, school_id, year, province)

        except Exception as e:
            logger.debug(f"数据标准化失败: {e}")
            return None

    def _parse_institution_score(self, row_data: Dict[str, str],
                                school_id: str, year: int, province: str) -> Optional[Dict[str, Any]]:
        """解析院校分数线数据"""
        try:
            # 提取批次
            batch = None
            batch_keywords = {
                '本科一批': ['一批', '一本', '第一批', '本科一批'],
                '本科二批': ['二批', '二本', '第二批', '本科二批'],
                '本科批': ['本科', '本科批', '普通本科'],
                '提前批': ['提前', '提前批'],
                '专科批': ['专科', '高职', '专科批']
            }

            batch_value = row_data.get('录取批次') or row_data.get('批次') or ''
            for batch_name, keywords in batch_keywords.items():
                if any(keyword in batch_value for keyword in keywords):
                    batch = batch_name
                    break

            if not batch:
                batch = '本科一批'

            # 提取科类
            category = '理科'
            category_value = row_data.get('科类/选科') or row_data.get('科类') or ''
            if '文科' in category_value:
                category = '文科'
            elif '综合' in category_value:
                category = '综合改革'
            elif '物理' in category_value:
                category = '物理类'
            elif '历史' in category_value:
                category = '历史类'

            # 提取分数和位次
            score_rank_value = row_data.get('最低分/最低位次') or row_data.get('分数') or ''
            min_score = min_rank = None

            # 解析格式如 "688/156" 或 "688 分 / 156 位"
            import re
            # 匹配数字/数字格式
            match = re.search(r'(\d+(?:\.\d+)?)\s*/\s*(\d+)', score_rank_value)
            if match:
                min_score = float(match.group(1))
                min_rank = int(match.group(2))
            else:
                # 尝试单独提取数字并进行验证
                numbers = self._extract_numbers_with_validation(score_rank_value)
                if numbers:
                    if len(numbers) >= 2:
                        # 第一个应该是分数，第二个是位次
                        min_score = numbers[0]
                        min_rank = numbers[1]
                    elif len(numbers) == 1:
                        # 只有一个数字，判断是分数还是位次
                        num = numbers[0]
                        if 200 <= num <= 750:
                            min_score = num
                        elif 1 <= num <= 1000000:
                            min_rank = num

            # 提取录取数
            admission_count = None
            count_value = row_data.get('录取数') or row_data.get('人数') or ''
            numbers = self._extract_numbers(count_value)
            if numbers:
                admission_count = int(numbers[0])

            # 构建数据
            standardized = {
                'university_id': int(school_id) if school_id.isdigit() else 1,
                'province': province,
                'year': year,
                'category': category,
                'batch': batch,
                'enrollment_type': '普通类',
                'major': None,  # 院校分数线，专业为空
                'min_score': min_score,
                'min_rank': min_rank,
                'avg_score': None,
                'provincial_control_line': None,
                'subject_requirements': None,
                'professional_group': None,
                'source_url': f"https://www.gaokao.cn/school/{school_id}/provinceline"
            }

            # 至少需要分数或位次
            if min_score is not None or min_rank is not None:
                logger.debug(f"院校分数线解析成功: {standardized}")
                return standardized

        except Exception as e:
            logger.debug(f"解析院校分数线失败: {e}")

        return None

    def _parse_institution_score_v2(self, row_data: Dict[str, str],
                                   school_id: str, year: int, province: str) -> Optional[Dict[str, Any]]:
        """解析院校分数线数据（新格式：年份, 录取批次, 招生类型, 最低分/最低位次, 录取数）"""
        try:
            # 提取批次
            batch = None
            batch_keywords = {
                '本科一批': ['一批', '一本', '第一批', '本科一批'],
                '本科二批': ['二批', '二本', '第二批', '本科二批'],
                '本科批': ['本科', '本科批', '普通本科'],
                '提前批': ['提前', '提前批'],
                '专科批': ['专科', '高职', '专科批']
            }

            batch_value = row_data.get('录取批次') or row_data.get('批次') or ''
            for batch_name, keywords in batch_keywords.items():
                if any(keyword in batch_value for keyword in keywords):
                    batch = batch_name
                    break

            if not batch:
                batch = '本科一批'

            # 提取招生类型
            enrollment_type = row_data.get('招生类型') or '普通类'

            # 提取分数和位次
            score_rank_value = row_data.get('最低分/最低位次') or row_data.get('分数') or ''
            min_score = min_rank = None

            # 解析格式如 "688/156" 或 "688 分 / 156 位"
            import re
            # 匹配数字/数字格式
            match = re.search(r'(\d+(?:\.\d+)?)\s*/\s*(\d+)', score_rank_value)
            if match:
                score = float(match.group(1))
                rank = int(match.group(2))

                # 验证数字合理性
                # 分数应该在200-750之间，位次在1-1000000之间
                if 200 <= score <= 750:
                    min_score = score
                if 1 <= rank <= 1000000:
                    min_rank = rank
            else:
                # 尝试单独提取数字并验证
                numbers = self._extract_numbers_with_validation(score_rank_value)
                if numbers:
                    if len(numbers) >= 2:
                        # 第一个应该是分数，第二个是位次
                        if 200 <= numbers[0] <= 750:
                            min_score = numbers[0]
                        if 1 <= numbers[1] <= 1000000:
                            min_rank = numbers[1]
                    elif len(numbers) == 1:
                        # 只有一个数字，判断是分数还是位次
                        num = numbers[0]
                        if 200 <= num <= 750:
                            min_score = num
                        elif 1 <= num <= 1000000:
                            min_rank = num

            # 提取录取数
            admission_count = None
            count_value = row_data.get('录取数') or row_data.get('人数') or ''
            numbers = self._extract_numbers(count_value)
            if numbers:
                admission_count = int(numbers[0])

            # 推断科类（理科/文科）
            # 新格式没有科类信息，需要根据学校/省份/批次推断
            # 暂时使用默认值"理科"，实际应该从上下文推断
            category = '理科'

            # 简单推断：如果批次包含"文科"或专业名称包含文科相关词
            if '文科' in batch_value or '文史' in batch_value:
                category = '文科'
            # 检查其他字段中是否包含科类信息
            for value in row_data.values():
                if '文科' in value:
                    category = '文科'
                    break
                elif '理科' in value:
                    category = '理科'
                    break
                elif '综合' in value:
                    category = '综合改革'
                    break
                elif '物理' in value:
                    category = '物理类'
                    break
                elif '历史' in value:
                    category = '历史类'
                    break

            # 构建数据
            standardized = {
                'university_id': int(school_id) if school_id.isdigit() else 1,
                'province': province,
                'year': year,
                'category': category,
                'batch': batch,
                'enrollment_type': enrollment_type,
                'major': None,  # 院校分数线，专业为空
                'min_score': min_score,
                'min_rank': min_rank,
                'avg_score': None,
                'provincial_control_line': None,
                'subject_requirements': None,
                'professional_group': None,
                'source_url': f"https://www.gaokao.cn/school/{school_id}/provinceline"
            }

            # 至少需要分数或位次
            if min_score is not None or min_rank is not None:
                logger.debug(f"院校分数线解析成功(v2): {standardized}")
                return standardized

        except Exception as e:
            logger.debug(f"解析院校分数线(v2)失败: {e}")

        return None

    def _parse_major_score(self, row_data: Dict[str, str],
                          school_id: str, year: int, province: str) -> Optional[Dict[str, Any]]:
        """解析专业分数线数据"""
        try:
            # 提取专业名称
            major = row_data.get('专业名称') or row_data.get('专业') or ''
            if not major or len(major) > 100:  # 专业名称过长可能不是真正的专业
                return None

            # 提取分数和位次
            score_rank_value = row_data.get('最低分/最低位次') or row_data.get('分数') or ''
            min_score = min_rank = None

            import re
            # 匹配数字/数字格式
            match = re.search(r'(\d+(?:\.\d+)?)\s*/\s*(\d+)', score_rank_value)
            if match:
                min_score = float(match.group(1))
                min_rank = int(match.group(2))
            else:
                numbers = self._extract_numbers_with_validation(score_rank_value)
                if numbers:
                    if len(numbers) >= 2:
                        # 第一个应该是分数，第二个是位次
                        min_score = numbers[0]
                        min_rank = numbers[1]
                    elif len(numbers) == 1:
                        # 只有一个数字，判断是分数还是位次
                        num = numbers[0]
                        if 200 <= num <= 750:
                            min_score = num
                        elif 1 <= num <= 1000000:
                            min_rank = num

            # 提取录取数
            admission_count = None
            count_value = row_data.get('录取数') or row_data.get('人数') or ''
            numbers = self._extract_numbers(count_value)
            if numbers:
                admission_count = int(numbers[0])

            # 提取选科要求
            subject_requirements = row_data.get('选科要求') or row_data.get('科目要求') or ''

            # 推断批次和科类（专业分数线通常与院校分数线一致，这里需要上下文）
            # 暂时使用默认值，实际应该从上下文获取
            batch = '本科一批'
            category = '理科'

            # 构建数据
            standardized = {
                'university_id': int(school_id) if school_id.isdigit() else 1,
                'province': province,
                'year': year,
                'category': category,
                'batch': batch,
                'enrollment_type': '普通类',
                'major': major,
                'min_score': min_score,
                'min_rank': min_rank,
                'avg_score': None,
                'provincial_control_line': None,
                'subject_requirements': subject_requirements,
                'professional_group': None,
                'source_url': f"https://www.gaokao.cn/school/{school_id}/provinceline"
            }

            # 需要专业名称和分数/位次
            if major and (min_score is not None or min_rank is not None):
                logger.debug(f"专业分数线解析成功: {standardized}")
                return standardized

        except Exception as e:
            logger.debug(f"解析专业分数线失败: {e}")

        return None

    def _parse_general_data(self, row_data: Dict[str, str],
                           school_id: str, year: int, province: str) -> Optional[Dict[str, Any]]:
        """通用数据解析"""
        try:
            # 尝试识别批次
            batch = None
            batch_keywords = {
                '本科一批': ['一批', '一本', '第一批', '本科一批'],
                '本科二批': ['二批', '二本', '第二批', '本科二批'],
                '本科批': ['本科', '本科批', '普通本科'],
                '提前批': ['提前', '提前批'],
                '专科批': ['专科', '高职', '专科批']
            }

            for value in row_data.values():
                for batch_name, keywords in batch_keywords.items():
                    if any(keyword in value for keyword in keywords):
                        batch = batch_name
                        break
                if batch:
                    break

            if not batch:
                batch = '本科一批'

            # 尝试识别科类
            category = '理科'
            for value in row_data.values():
                if '文科' in value:
                    category = '文科'
                    break
                elif '综合' in value:
                    category = '综合改革'
                    break
                elif '物理' in value:
                    category = '物理类'
                    break
                elif '历史' in value:
                    category = '历史类'
                    break

            # 提取所有数字
            all_numbers = []
            for value in row_data.values():
                all_numbers.extend(self._extract_numbers(value))

            min_score = min_rank = None
            if all_numbers:
                if len(all_numbers) >= 2:
                    min_score = all_numbers[0]
                    min_rank = all_numbers[1]
                elif len(all_numbers) == 1:
                    min_score = all_numbers[0]

            # 尝试识别专业
            major = None
            for key, value in row_data.items():
                if '专业' in key and value and 2 < len(value) < 50:
                    major = value
                    break

            # 构建数据
            standardized = {
                'university_id': int(school_id) if school_id.isdigit() else 1,
                'province': province,
                'year': year,
                'category': category,
                'batch': batch,
                'enrollment_type': '普通类',
                'major': major,
                'min_score': min_score,
                'min_rank': min_rank,
                'avg_score': None,
                'provincial_control_line': None,
                'subject_requirements': None,
                'professional_group': None,
                'source_url': f"https://www.gaokao.cn/school/{school_id}/provinceline"
            }

            # 至少需要一些数据
            if min_score is not None or min_rank is not None or major:
                logger.debug(f"通用解析成功: {standardized}")
                return standardized

        except Exception as e:
            logger.debug(f"通用解析失败: {e}")

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

    def _extract_numbers_with_validation(self, text: str) -> List[float]:
        """从文本中提取数字，并进行合理性验证"""
        import re
        from datetime import datetime
        numbers = []
        # 匹配整数和小数
        matches = re.findall(r'\d+\.?\d*', text)
        for match in matches:
            try:
                num = float(match)

                # 过滤不合理的数字
                # 高考分数通常在200-750之间
                # 位次通常在1-1000000之间
                # 年份在2000-当前年份之间
                current_year = datetime.now().year

                # 如果是合理的分数或位次，添加到列表
                if 200 <= num <= 750:  # 分数范围
                    numbers.append(num)
                elif 1 <= num <= 1000000:  # 位次范围
                    numbers.append(num)
                # 年份和其他数字不添加

            except:
                continue
        return numbers

    def _find_alternative_data(self, school_id: int, year: int, province: str) -> List[Dict[str, Any]]:
        """查找替代数据源（非表格数据）"""
        data_list = []

        try:
            # 查找所有可能包含数据的元素
            data_containers = [
                ("div", "class", "table"),  # div模拟的表格
                ("div", "class", "list"),   # 列表
                ("div", "class", "data"),   # 数据容器
                ("ul", "class", "list"),    # 无序列表
                ("tbody", "", ""),          # 表格体
                ("tr", "", ""),             # 表格行
            ]

            for tag, attr, value in data_containers:
                try:
                    if attr and value:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, f"{tag}[{attr}*='{value}']")
                    else:
                        elements = self.driver.find_elements(By.TAG_NAME, tag)

                    for element in elements:
                        try:
                            text = element.text.strip()
                            if text and any(keyword in text for keyword in ['分', '位次', '录取', '批次', '专业']):
                                # 尝试解析文本数据
                                parsed_data = self._parse_text_data(text, school_id, year, province)
                                if parsed_data:
                                    data_list.extend(parsed_data)
                        except:
                            continue

                    if data_list:
                        logger.info(f"从 {tag} 元素找到 {len(data_list)} 条数据")
                        break

                except:
                    continue

        except Exception as e:
            logger.debug(f"查找替代数据失败: {e}")

        return data_list

    def _parse_text_data(self, text: str, school_id: int, year: int, province: str) -> List[Dict[str, Any]]:
        """解析文本数据"""
        data_list = []

        try:
            # 按行分割
            lines = text.split('\n')

            current_data = {}
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 尝试识别数据行
                if any(keyword in line for keyword in ['分', '位次', '录取']):
                    # 这里可以添加更复杂的文本解析逻辑
                    # 暂时简单处理
                    pass

            # 如果有多行数据，尝试整体解析
            if len(lines) >= 3:  # 至少有表头和数据行
                # 简单尝试：查找数字模式
                import re
                score_pattern = r'(\d+(?:\.\d+)?)\s*分'
                rank_pattern = r'位次\s*(\d+)'

                scores = re.findall(score_pattern, text)
                ranks = re.findall(rank_pattern, text)

                if scores:
                    # 创建简单数据记录
                    data = {
                        'university_id': int(school_id) if school_id.isdigit() else 1,
                        'province': province,
                        'year': year,
                        'category': '理科',  # 默认
                        'batch': '本科一批',  # 默认
                        'enrollment_type': '普通类',
                        'min_score': float(scores[0]) if scores else None,
                        'min_rank': int(ranks[0]) if ranks else None,
                        'source_url': f"https://www.gaokao.cn/school/{school_id}/provinceline"
                    }
                    data_list.append(data)

        except Exception as e:
            logger.debug(f"解析文本数据失败: {e}")

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