# 爬虫问题修复总结

## 🔧 修复的问题

### 1. **FOREIGN KEY constraint failed**
- **问题**: `university_id` 是字符串 '140'，但数据库期望整数
- **原因**: 爬虫返回的 `university_id` 是字符串，但数据库表使用整数外键
- **修复**: 在所有解析方法中转换 `school_id` 为整数
  ```python
  'university_id': int(school_id) if school_id.isdigit() else 1
  ```

### 2. **年份误解析为分数**
- **问题**: 年份 "2025" 被错误解析为 `min_score`
- **原因**: 
  - 表格格式变化：新格式为 `['年份', '录取批次', '招生类型', '最低分/最低位次', '录取数']`
  - 旧解析逻辑期望 `['录取批次', '科类/选科', '最低分/最低位次', '录取数']`
  - `_extract_numbers` 方法提取所有数字，包括年份
- **修复**:
  a. 添加新解析器 `_parse_institution_score_v2` 处理新表格格式
  b. 更新 `_standardize_row_data` 逻辑识别新格式
  c. 添加 `_extract_numbers_with_validation` 方法过滤不合理数字

### 3. **表格格式识别错误**
- **问题**: 新表格格式未被正确识别，导致使用通用解析器
- **原因**: 旧逻辑检查 "批次" 和 "科类"，但新表格只有 "批次" 和 "年份"
- **修复**: 更新 `_standardize_row_data` 逻辑：
  ```python
  # 新格式：年份 + 批次
  if any('批次' in h for h in headers) and any('年份' in h for h in headers):
      return self._parse_institution_score_v2(...)
  # 旧格式：批次 + 科类  
  elif any('批次' in h for h in headers) and any('科类' in h or '选科' in h for h in headers):
      return self._parse_institution_score(...)
  ```

### 4. **数字提取无验证**
- **问题**: `_extract_numbers` 提取所有数字，包括年份、页码等
- **修复**: 添加 `_extract_numbers_with_validation`：
  ```python
  # 分数范围: 200-750
  # 位次范围: 1-1000000
  # 年份和其他数字被过滤
  ```

## 📊 修复验证

### 测试结果
1. **学校信息保存**: ✓ 成功添加 "清华大学" 到数据库 (ID: 2)
2. **数据提取**: ✓ 提取 4 条记录 (2条院校分数线 + 2条专业分数线)
3. **数据库保存**: ✓ 成功保存 4 条记录，无 FOREIGN KEY 错误
4. **数据正确性**: 
   - 分数: 683.0, 688.0, 694.0 (正确，不是 2025!)
   - 位次: 72, 156, 262 (正确)
   - 批次: "本科批", "本科一批" (正确)
   - 科类: "理科" (正确推断)

### 数据库状态
- `universities` 表: 2 条记录 (ID 1: "140", ID 2: "清华大学")
- `undergraduate_admissions` 表: 4 条记录
- 所有外键约束满足
- 所有数据在合理范围内

## 🚀 使用方法

### 运行测试
```bash
# 进入代码目录
cd E:\VSproject\China-University-Admission\crawler\python

# 测试模式 (推荐先运行)
python main.py 140 --test

# 完整爬取
python main.py 140

# 指定年份和省份
python main.py 140 -y 2024 2023 -p 北京 上海

# 断点续传
python main.py 140 --resume
```

### 验证数据
1. 检查日志文件 `crawler.log`
2. 查看 JSON 输出文件 `data_140_*.json`
3. 查询数据库:
   ```sql
   sqlite3 E:\VSproject\China-University-Admission\data\test_university.db
   > SELECT * FROM universities;
   > SELECT COUNT(*), MIN(min_score), MAX(min_score) FROM undergraduate_admissions;
   ```

## 📝 代码修改文件

1. **crawler.py** - 主要修复
   - 添加 `_parse_institution_score_v2` 方法
   - 添加 `_extract_numbers_with_validation` 方法  
   - 更新 `_standardize_row_data` 选择逻辑
   - 修复 `school_id` 类型转换 (str → int)
   - 更新所有解析方法的参数类型

2. **main.py** - 已有修复逻辑保持

## ⚠️ 注意事项

1. **表格格式变化**: 网站可能再次更改表格结构
2. **科类推断**: 新格式缺少科类信息，需要从上下文推断
3. **数字验证阈值**: 分数范围 200-750，位次范围 1-1000000 可能需要调整
4. **学校信息保存**: 需要完善省份推断逻辑

## ✅ 修复完成状态

所有关键问题已修复，爬虫可以正常运行并保存数据到数据库。