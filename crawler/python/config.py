"""
爬虫配置文件
"""

# 数据库配置
DATABASE_CONFIG = {
    'path': r'E:\VSproject\China-University-Admission\data\test_university.db',
    'timeout': 30
}

# 网站配置
BASE_URL = "https://www.gaokao.cn"
SCHOOL_URL_TEMPLATE = BASE_URL + "/school/{school_id}/provinceline"

# 请求配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# 爬取配置
MAX_RETRIES = 3
RETRY_DELAY = 2  # 秒
TIMEOUT = 30  # 秒

# 省份列表（完整）
PROVINCES = [
    '北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江',
    '上海', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南',
    '湖北', '湖南', '广东', '广西', '海南', '重庆', '四川', '贵州',
    '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆'
]

# 年份范围（近三年）
YEARS = [2025, 2024, 2023]

# 批次类型
BATCH_TYPES = ['本科一批', '本科二批', '本科三批', '提前批']

# 科目类型
SUBJECT_TYPES = ['文科', '理科', '综合改革']