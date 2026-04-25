# 中国高校招生信息系统

一个综合性的中国高校招生信息管理系统，提供高校基本信息、高考招生数据和研究生招生信息的管理与查询功能。

## 项目概述

本系统旨在为用户提供全面的高校招生信息服务，包括高校基本信息管理、高考录取数据查询和研究生招生信息管理。系统采用现代化的技术架构，支持多维度的数据管理和查询。

## 核心功能

### 🎓 高校信息管理
- **全国高校覆盖**：已收录全国1167所高校信息
- **省份全覆盖**：覆盖全国31个省市自治区
- **多类型高校**：包含本科、专科、综合、师范、医药等多种类型
- **详细信息**：学校名称、类型、层次、省份、城市、标签、网站等

### 📊 招生数据管理
- **高考录取数据**：历年分数线、专业录取分数、选科要求
- **研究生招生**：招生专业目录、导师信息、录取数据
- **数据可视化**：招生数据的统计分析和图表展示
- **智能查询**：多条件组合查询和筛选

### 🔧 技术特性
- **模块化设计**：易于维护和扩展
- **数据库优化**：SQLite数据库，支持快速查询
- **数据验证**：自动验证和标准化数据
- **日志系统**：详细的运行日志
- **错误处理**：完善的异常处理机制

## 系统架构

```
China-University-Admission/
├── data/                 # 数据文件
│   └── university.db     # SQLite数据库
├── crawler/              # 数据采集模块
│   ├── python/           # Python爬虫
│   └── README.md         # 爬虫说明
├── frontend/             # 前端界面
│   └── src/              # 前端源码
└── README.md             # 项目说明
```

## 数据现状

### 已完成数据
- **高校基本信息**：1167所高校的基本信息
- **省份覆盖**：31个省市自治区
- **数据类型**：本科、专科、综合、师范、医药等

### 待补充数据
- **高考招生信息**：历年录取分数线、专业分数线、录取位次
- **研究生招生信息**：招生专业目录、导师信息、录取数据

## 数据库结构

### 高校表（universities）

```sql
CREATE TABLE universities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT,
    level TEXT,
    province TEXT NOT NULL,
    city TEXT,
    tags TEXT,
    website TEXT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name)
);
```

### 本科录取数据表（undergraduate_admissions）

```sql
CREATE TABLE undergraduate_admissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_id INTEGER NOT NULL,
    province TEXT NOT NULL,
    year INTEGER NOT NULL,
    category TEXT,
    batch TEXT,
    enrollment_type TEXT,
    major TEXT,
    min_score REAL,
    min_rank INTEGER,
    avg_score REAL,
    provincial_control_line REAL,
    subject_requirements TEXT,
    professional_group TEXT,
    source_url TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (university_id) REFERENCES universities(id) ON DELETE CASCADE,
    UNIQUE(university_id, year, province, category, batch, major)
);
```

## 快速开始

### 1. 系统要求
- Python 3.8+
- SQLite 3.30+
- 现代Web浏览器

### 2. 项目结构
- **data/**：数据库文件和数据存储
- **crawler/**：数据采集模块
- **frontend/**：前端界面

### 3. 基本使用

#### 查看高校信息
```bash
# 查看特定省份的高校
SELECT * FROM universities WHERE province = '广东';

# 查看特定类型的高校
SELECT * FROM universities WHERE type = '综合';
```

#### 管理数据
- 通过前端界面进行数据的增删改查
- 使用SQLite工具直接操作数据库
- 利用Python脚本进行批量数据处理

## 系统展示

### 界面展示

![系统界面1](../images/页面展示1.png)

![系统界面2](../images/页面展示2.png)

## 扩展开发

### 功能扩展
1. **数据采集**：完善爬虫功能，自动采集招生数据
2. **前端界面**：开发现代化的Web界面
3. **数据分析**：增加数据统计和分析功能
4. **API接口**：提供RESTful API接口

### 技术栈
- **后端**：Python, SQLite
- **前端**：Vue.js, JavaScript, CSS
- **数据采集**：Selenium, BeautifulSoup

## 注意事项

1. **数据准确性**：定期验证数据的准确性
2. **系统性能**：优化数据库查询和前端渲染
3. **用户体验**：持续改进界面设计和交互体验
4. **法律合规**：确保数据使用符合相关法律法规

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规。