# 爬虫系统使用指南（适配新数据库结构）

## 🎯 更新摘要

爬虫系统已成功适配新的数据库结构，包含以下三个表：

### 1. `universities` - 高校基本信息表
- `id` - 主键
- `name` - 学校名称（唯一）
- `province` - 所在省份
- `type` - 学校类型（综合/理工/师范等）
- `level` - 学校层次（985/211/双一流等）
- `city` - 所在城市
- `tags` - 标签（逗号分隔）
- `logo_url` - 校徽URL
- `description` - 学校简介
- `website` - 学校官网

### 2. `undergraduate_admissions` - 本科录取数据表
- `university_id` - 关联高校ID
- `province` - 生源地省份
- `year` - 录取年份（近5年）
- `category` - 科类（理科/文科/综合改革等）
- `batch` - 录取批次（本科一批/本科批等）
- `enrollment_type` - 招生类型（普通类/专项计划等）
- `major` - 专业名称（NULL表示院校分数线）
- `min_score` - 最低录取分数
- `min_rank` - 最低位次
- `avg_score` - 平均分
- `provincial_control_line` - 省控线

### 3. `postgraduate_admissions` - 研究生录取数据表
- （当前爬虫专注于本科数据，研究生表暂未使用）

## 🚀 快速开始

### 1. 安装依赖
```bash
cd E:\VSproject\China-University-Admission\crawler\python
pip install -r requirements.txt
```

### 2. 基本使用

#### 爬取单个学校（近三年所有省份）
```bash
python main.py 140
```

#### 指定年份和省份
```bash
python main.py 140 -y 2024 2023 -p 北京 上海 广东
```

#### 测试模式（只爬取第一个省份的第一年）
```bash
python main.py 140 --test
```

#### 断点续传
```bash
python main.py 140 --resume
```

#### 仅爬取不保存（调试用）
```bash
python main.py 140 --no-save
```

### 3. 命令行参数详解

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `school_id` | 学校ID（必需） | - |
| `-y, --years` | 年份列表 | [2025, 2024, 2023] |
| `-p, --provinces` | 省份列表 | 所有31个省份 |
| `-d, --database` | 数据库路径 | config.py配置 |
| `--headless` | 使用无头模式 | True |
| `--no-save` | 仅爬取不保存 | False |
| `--test` | 测试模式 | False |
| `--resume` | 断点续传 | False |

## 📊 数据爬取逻辑

### 数据提取流程
1. **学校信息提取**：从页面获取学校名称等基本信息
2. **表格数据解析**：查找并解析HTML表格
3. **数据标准化**：
   - 识别批次（本科一批/本科批/提前批等）
   - 识别科类（理科/文科/综合改革）
   - 识别招生类型（普通类/专项计划/中外合作）
   - 提取分数、位次、省控线
   - 识别专业名称

### 数据存储规则
1. **院校分数线**：`major`字段为NULL
2. **专业分数线**：`major`字段为专业名称
3. **唯一约束**：防止重复数据（学校+省份+年份+科类+批次+专业+招生类型）

## 🔧 配置调整

### 修改数据库路径
编辑 `config.py`：
```python
DATABASE_CONFIG = {
    'path': r'你的数据库路径.db',
    'timeout': 30
}
```

### 调整爬取范围
```python
# 年份范围
YEARS = [2025, 2024, 2023]

# 省份列表
PROVINCES = ['北京', '天津', '河北', ...]

# 批次类型（适配新高考）
BATCH_TYPES = ['本科一批', '本科二批', '本科批', '提前批', '专科批']
```

### 请求配置
```python
MAX_RETRIES = 3      # 最大重试次数
RETRY_DELAY = 2      # 重试延迟（秒）
TIMEOUT = 30         # 请求超时（秒）
```

## 🐛 故障排除

### 常见问题

#### 1. ChromeDriver错误
```bash
# 清理缓存
rm -rf ~/.wdm

# 重新安装
pip install --upgrade webdriver-manager selenium
```

#### 2. 数据提取失败
- 检查页面结构是否变化
- 查看 `page_sources/` 目录下的页面源码
- 调整等待时间（修改config.py中的`TIMEOUT`）

#### 3. 数据库连接失败
- 检查数据库文件路径是否正确
- 确保文件未被其他程序占用
- 检查文件权限

#### 4. 编码问题（Windows）
```python
# 在代码开头添加
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

### 调试模式

#### 查看详细日志
```bash
python main.py 140 --test 2>&1 | tee debug.log
```

#### 禁用无头模式（查看浏览器）
```bash
python main.py 140 --headless=false --test
```

#### 保存页面源码
爬虫会自动在 `page_sources/` 目录保存失败的页面源码，用于分析页面结构。

## 📈 数据验证

### 检查爬取结果
1. **查看日志文件**：`crawler.log`
2. **查询数据库**：
```sql
-- 查看某学校数据统计
SELECT COUNT(*) as 总记录数,
       COUNT(DISTINCT province) as 省份数,
       COUNT(DISTINCT year) as 年份数
FROM undergraduate_admissions
WHERE university_id = (SELECT id FROM universities WHERE name = '学校名称');

-- 查看具体数据
SELECT year, province, category, batch, major, min_score, min_rank
FROM undergraduate_admissions
WHERE university_id = (SELECT id FROM universities WHERE name = '学校名称')
ORDER BY year DESC, province, category;
```

### 数据质量检查
1. **分数范围**：0-750分（高考总分）
2. **位次范围**：1-1000000（合理位次）
3. **年份范围**：近5年
4. **省份验证**：31个标准省份

## 🔄 批量处理

### 创建学校列表文件
创建 `schools.txt`：
```
140
141
142
```

### 使用批量处理器
```bash
# 进入examples目录
cd ../examples

# 运行批量处理器
python batch_processor.py schools.txt

# 使用配置文件
python batch_processor.py schools.txt -c config.json

# 测试模式
python batch_processor.py schools.txt --test
```

## ⚠️ 注意事项

### 法律与道德
1. **遵守robots.txt**：尊重网站爬取规则
2. **控制请求频率**：避免对服务器造成压力
3. **数据使用**：仅用于学习和研究目的
4. **版权尊重**：尊重数据版权

### 技术注意事项
1. **定期备份**：爬取前备份数据库
2. **监控进度**：使用进度文件实现断点续传
3. **更新维护**：定期检查页面结构变化
4. **错误处理**：系统包含完善的错误处理和重试机制

### 性能优化
1. **分批处理**：不要一次性爬取太多学校
2. **合理延迟**：设置适当的请求间隔
3. **资源管理**：及时关闭数据库和浏览器连接
4. **内存监控**：监控内存使用，避免泄漏

## 📞 技术支持

### 问题反馈
1. 查看 `crawler.log` 日志文件
2. 检查 `page_sources/` 中的页面源码
3. 运行测试脚本验证功能

### 代码结构
- `main.py` - 主程序入口
- `config.py` - 配置文件
- `database.py` - 数据库操作（已适配新表结构）
- `crawler.py` - 爬虫核心（已更新数据标准化）
- `utils.py` - 工具函数
- `test_new_db.py` - 数据库适配测试

### 扩展开发
如需支持新的网站结构或数据字段，请修改：
1. `crawler.py` 中的 `_standardize_row_data` 方法
2. `database.py` 中的数据库操作方法
3. `config.py` 中的配置项

---

**系统已成功适配新数据库结构，可以开始爬取数据！**