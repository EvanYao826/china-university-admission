# 高考数据爬虫系统

基于Selenium的JavaScript渲染页面爬虫，用于爬取gaokao.cn网站的历年分数线和专业分数线数据。

## 功能特性

- ✅ **模块化设计**：易于维护和扩展
- ✅ **参数化爬取**：支持学校ID、年份、省份作为参数
- ✅ **断点续传**：支持从上次中断处恢复
- ✅ **数据验证**：自动验证和标准化数据
- ✅ **数据库集成**：直接保存到SQLite数据库
- ✅ **日志系统**：详细的运行日志
- ✅ **错误处理**：完善的异常处理和重试机制

## 系统架构

```
crawler/
├── main.py              # 主程序入口
├── config.py           # 配置文件
├── database.py         # 数据库操作
├── crawler.py          # 爬虫核心逻辑（Selenium）
├── utils.py           # 工具函数
├── requirements.txt    # 依赖包
└── README.md          # 说明文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 基本使用

爬取单个学校近三年所有省份数据：
```bash
python main.py 140
```

爬取指定年份和省份：
```bash
python main.py 140 -y 2023 2022 -p 北京 上海 广东
```

测试模式（只爬取第一个省份的第一年）：
```bash
python main.py 140 --test
```

断点续传：
```bash
python main.py 140 --resume
```

### 3. 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `school_id` | 学校ID（必需） | - |
| `-y, --years` | 年份列表 | 近三年 |
| `-p, --provinces` | 省份列表 | 所有省份 |
| `-d, --database` | 数据库路径 | config.py配置 |
| `--headless` | 使用无头模式 | True |
| `--no-save` | 仅爬取不保存 | False |
| `--test` | 测试模式 | False |
| `--resume` | 断点续传 | False |

## 数据库结构

系统使用现有的数据库结构（`gaokao_admissions`表）：

```sql
CREATE TABLE gaokao_admissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    province TEXT NOT NULL,
    category TEXT CHECK(category IN ('文科', '理科', '综合改革', '艺术', '体育')) NOT NULL,
    batch TEXT CHECK(batch IN ('本科一批', '本科二批', '专科批', '提前批')) NOT NULL,
    min_score REAL,
    avg_score REAL,
    max_score REAL,
    min_rank INTEGER,
    avg_rank INTEGER,
    max_rank INTEGER,
    admission_count INTEGER,
    major TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE,
    UNIQUE(university_id, year, province, category, batch, major)
);
```

## 数据标准化

爬虫会自动标准化以下数据：

1. **省份名称**：标准化为简称（如"北京市"→"北京"）
2. **批次类型**：自动识别并映射到标准批次
3. **科目类型**：识别文科、理科、综合改革
4. **分数数据**：提取最低分、平均分、最高分
5. **位次数据**：提取最低位次、平均位次、最高位次

## 错误处理

系统包含多层错误处理：

1. **网络请求重试**：失败后自动重试（最多3次）
2. **数据验证**：保存前验证数据有效性
3. **进度保存**：支持断点续传
4. **日志记录**：详细记录所有操作和错误

## 配置说明

### 数据库配置
在`config.py`中修改`DATABASE_CONFIG`：
```python
DATABASE_CONFIG = {
    'path': r'E:\VSproject\China-University-Admission\data\test.db',
    'timeout': 30
}
```

### 爬取配置
```python
# 省份列表
PROVINCES = ['北京', '天津', '河北', ...]

# 年份范围（近三年）
YEARS = [2023, 2022, 2021]

# 请求配置
MAX_RETRIES = 3
RETRY_DELAY = 2  # 秒
TIMEOUT = 30  # 秒
```

## 扩展开发

### 添加新的数据解析器
1. 在`crawler.py`中实现新的解析方法
2. 在`extract_admission_data`方法中调用

### 支持新的网站结构
1. 修改`_parse_table`方法适应新的表格结构
2. 更新`_standardize_row_data`方法处理新字段

### 添加新的输出格式
1. 在`utils.py`中添加新的输出函数
2. 在`main.py`中集成输出选项

## 注意事项

1. **遵守robots.txt**：确保爬取行为符合网站规定
2. **控制请求频率**：避免对服务器造成压力
3. **数据准确性**：定期验证爬取数据的准确性
4. **法律合规**：确保数据使用符合相关法律法规

## 故障排除

### ChromeDriver问题
```bash
# 清理缓存
rm -rf ~/.wdm

# 重新安装
pip install --upgrade webdriver-manager
```

### 内存泄漏
- 确保正确关闭WebDriver
- 定期重启爬虫进程
- 监控内存使用情况

### 数据提取失败
1. 检查页面结构是否变化
2. 查看保存的页面源码（`page_sources/`目录）
3. 调整等待时间和选择器

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规。