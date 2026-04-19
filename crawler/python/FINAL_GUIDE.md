# 爬虫系统最终指南

## 🎯 已完成的所有改进

### 1. **数据库适配完成**
- ✅ 完全适配新的三表结构：
  - `universities` - 高校基本信息
  - `undergraduate_admissions` - 本科录取数据
  - `postgraduate_admissions` - 研究生数据（暂未使用）
- ✅ 更新了所有数据库操作方法
- ✅ 添加了兼容旧接口的支持

### 2. **爬虫核心功能增强**
- ✅ **学校名称智能提取**：从页面标题、元素等多渠道提取
- ✅ **省份年份交互选择**：自动选择下拉框中的省份和年份
- ✅ **智能表格解析**：支持两种表格格式：
  - 院校分数线表格（批次/科类/分数位次/录取数）
  - 专业分数线表格（专业/分数位次/录取数/选科要求）
- ✅ **多策略数据提取**：
  - 表格数据解析（主要）
  - 替代数据源查找（备用）
  - 文本数据解析（容错）

### 3. **数据标准化优化**
- ✅ **三种解析策略**：
  - `_parse_institution_score()` - 院校分数线
  - `_parse_major_score()` - 专业分数线  
  - `_parse_general_data()` - 通用数据
- ✅ **智能字段识别**：
  - 批次识别（本科一批、本科批、提前批等）
  - 科类识别（理科、文科、综合改革、物理类、历史类）
  - 招生类型识别（普通类、专项计划、中外合作等）
  - 选科要求提取

### 4. **错误处理和日志**
- ✅ 详细的调试日志
- ✅ 页面源码保存（失败时自动保存）
- ✅ 完善的异常处理
- ✅ 断点续传支持

## 🚀 使用方法

### 基本命令
```bash
# 进入代码目录
cd E:\VSproject\China-University-Admission\crawler\python

# 1. 测试模式（推荐先运行）
python main.py 140 --test

# 2. 完整爬取（学校140，近三年所有省份）
python main.py 140

# 3. 指定年份和省份
python main.py 140 -y 2024 2023 -p 北京 上海 广东

# 4. 断点续传
python main.py 140 --resume

# 5. 仅爬取不保存（调试）
python main.py 140 --no-save
```

### 命令行参数
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `school_id` | 学校ID（必需） | - |
| `-y, --years` | 年份列表 | [2025, 2024, 2023] |
| `-p, --provinces` | 省份列表 | 所有31省份 |
| `--test` | 测试模式 | False |
| `--resume` | 断点续传 | False |
| `--no-save` | 仅爬取不保存 | False |
| `--headless` | 无头模式 | True |

## 📊 数据流程

### 1. **访问页面**
```
https://www.gaokao.cn/school/{id}/provinceline
```

### 2. **提取学校信息**
- 从页面标题提取学校名称
- 去除"历年分数线"等后缀
- 保存到`universities`表

### 3. **选择省份和年份**
- 查找下拉框元素
- 选择指定省份
- 选择指定年份
- 点击查询按钮（如果存在）

### 4. **提取和解析数据**
#### 院校分数线表格：
```
录取批次     科类/选科     最低分/最低位次     录取数
本科一批     理科          688/156           10
```

#### 专业分数线表格：
```
专业名称               最低分/最低位次     录取数     选科要求
计算机科学与技术       694/72            5         物理必选
临床医学              688/156           8         化学必选
```

### 5. **数据标准化**
```python
{
    'university_id': 学校ID,
    'province': '北京',
    'year': 2024,
    'category': '理科',           # 科类
    'batch': '本科一批',          # 批次
    'enrollment_type': '普通类',  # 招生类型
    'major': '计算机科学与技术',  # 专业（NULL表示院校分数线）
    'min_score': 694.0,          # 最低分
    'min_rank': 72,              # 最低位次
    'avg_score': None,           # 平均分（页面通常不提供）
    'provincial_control_line': None,  # 省控线
    'subject_requirements': '物理必选',  # 选科要求
    'professional_group': None,  # 专业组
    'source_url': 'https://www.gaokao.cn/school/140/provinceline'
}
```

### 6. **保存到数据库**
- 使用`INSERT OR REPLACE`避免重复
- 唯一约束：学校+省份+年份+科类+批次+专业+招生类型
- 自动维护`created_at`和`updated_at`

## 🔧 故障排除

### 常见问题

#### 1. **数据提取失败**
```
症状：找到表格但提取0条数据
解决：
1. 检查 page_sources/ 目录下的页面源码
2. 确认页面显示了正确省份和年份的数据
3. 可能需要调整等待时间（修改config.py中的TIMEOUT）
```

#### 2. **省份年份选择失败**
```
症状：日志显示"未找到省份选择框"
解决：
1. 页面结构可能变化，需要更新选择器
2. 尝试禁用无头模式查看页面：--headless=false
3. 手动检查页面中的下拉框元素
```

#### 3. **学校名称提取错误**
```
症状：提取到"XX大学2026年强基计划招生简章"
解决：
1. 系统会从页面标题重新提取
2. 自动去除"历年分数线"等后缀
3. 最终保存的是纯学校名称
```

#### 4. **ChromeDriver问题**
```bash
# 清理缓存
rm -rf ~/.wdm

# 重新安装
pip install --upgrade webdriver-manager selenium
```

### 调试技巧

#### 查看详细日志
```bash
# 运行并保存日志
python main.py 140 --test 2>&1 | tee debug.log

# 查看关键信息
grep -i "表格\|提取\|成功\|失败" debug.log
```

#### 分析页面源码
```python
# 页面源码保存在 page_sources/ 目录
# 文件名格式：page_source_{学校}_{年份}_{省份}_{时间}.html

# 查看表格结构
with open('page_sources/page_source_140_2024_北京_xxx.html', 'r') as f:
    content = f.read()
    # 搜索表格
    import re
    tables = re.findall(r'<table[^>]*>(.*?)</table>', content, re.DOTALL)
```

#### 手动测试选择器
```python
# 在爬虫代码中添加调试
print(f"找到 {len(selects)} 个下拉框")
for select in selects:
    print(f"  下拉框: {select.get_attribute('outerHTML')[:200]}")
```

## 📈 性能优化建议

### 1. **分批处理**
```bash
# 不要一次性爬取太多学校
# 建议每次处理3-5个学校

# 使用批量处理器（examples目录）
cd ../examples
python batch_processor.py schools.txt --test
```

### 2. **合理延迟**
```python
# 在config.py中调整
RETRY_DELAY = 2      # 重试延迟（秒）
TIMEOUT = 30         # 请求超时（秒）

# 在代码中适当添加sleep
time.sleep(1)  # 避免请求过快
```

### 3. **资源管理**
```python
# 使用上下文管理器确保资源释放
with GaokaoCrawler(headless=True) as crawler:
    with DatabaseManager() as db:
        # 爬取和保存数据
        pass
```

### 4. **监控进度**
- 查看 `crawler.log` 日志文件
- 使用 `--resume` 参数支持断点续传
- 进度文件：`progress_{school_id}.json`

## 🎯 下一步建议

### 1. **运行测试验证**
```bash
# 第一步：运行测试模式
python main.py 140 --test

# 第二步：检查日志
tail -f crawler.log

# 第三步：验证数据库
sqlite3 E:\VSproject\China-University-Admission\data\test_university.db
> SELECT * FROM universities;
> SELECT COUNT(*) FROM undergraduate_admissions;
```

### 2. **小规模爬取**
```bash
# 爬取一个学校的两个省份
python main.py 140 -y 2024 -p 北京 上海

# 检查数据质量
sqlite3 test_university.db
> SELECT year, province, category, batch, major, min_score, min_rank 
  FROM undergraduate_admissions 
  ORDER BY province, batch, major;
```

### 3. **批量处理**
```bash
# 创建学校列表
echo -e "140\n141\n142" > schools.txt

# 使用批量处理器
cd examples
python batch_processor.py ../schools.txt --test
```

### 4. **监控和维护**
- 定期检查页面结构变化
- 更新选择器以适应网站改版
- 备份数据库重要数据
- 监控爬取成功率

## ⚠️ 重要注意事项

### 法律合规
1. **遵守robots.txt**：尊重网站爬取规则
2. **控制频率**：避免对服务器造成压力
3. **数据使用**：仅用于学习和研究
4. **版权尊重**：尊重数据版权

### 技术限制
1. **JavaScript依赖**：页面需要JS渲染
2. **页面结构变化**：网站可能改版
3. **反爬措施**：注意可能的反爬机制
4. **数据完整性**：部分数据可能缺失

### 最佳实践
1. **先测试后生产**：先用--test模式验证
2. **分批处理**：不要一次性爬取太多
3. **定期备份**：爬取前备份数据库
4. **监控日志**：关注错误和警告信息

---

**系统已完全适配新数据库结构，可以开始正式爬取数据！**

如果遇到问题，请：
1. 检查 `crawler.log` 日志文件
2. 查看 `page_sources/` 中的页面源码
3. 运行测试模式排查问题
4. 根据需要调整配置参数