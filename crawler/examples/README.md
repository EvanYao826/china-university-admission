# 使用示例

本目录包含高考数据爬虫系统的各种使用示例。

## 文件说明

### 基础示例
- `basic_usage.py` - 基本使用示例，展示命令行参数的各种用法
- `advanced_usage.py` - 高级使用示例，直接使用模块API进行精细控制

### 批量处理
- `batch_processor.py` - 批量处理器，用于处理多个学校
- `create_school_list.py` - 创建学校ID列表文件的工具

## 快速开始

### 1. 运行基础示例

```bash
# 进入示例目录
cd examples

# 运行基础示例
python basic_usage.py

# 运行高级示例
python advanced_usage.py
```

### 2. 创建学校列表

```bash
# 创建示例学校列表
python create_school_list.py
```

这会创建以下文件：
- `schools.txt` - 基本学校列表
- `schools_from_json.txt` - 从JSON创建的学校列表
- `test_schools.txt` - 测试用学校列表（包含错误测试）
- `schools_north/east/central/south/west.txt` - 按地区分组的学校列表

### 3. 使用批量处理器

```bash
# 使用基本学校列表
python batch_processor.py schools.txt

# 使用配置文件
python batch_processor.py schools.txt -c config.json

# 测试模式（只处理前2个学校）
python batch_processor.py schools.txt --test

# 不保存到数据库
python batch_processor.py schools.txt --no-db
```

## 示例详解

### basic_usage.py

展示6种使用场景：
1. 爬取单个学校的基本数据
2. 爬取指定年份
3. 使用自定义数据库
4. 断点续传功能
5. 仅爬取不保存模式
6. 批量处理多个学校

### advanced_usage.py

展示4种高级功能：
1. **高级爬取**：完全控制爬取过程，实时显示进度
2. **增量爬取**：只爬取数据库中不存在的新数据
3. **错误处理**：测试各种错误情况的处理
4. **性能测试**：测量爬取性能指标

### batch_processor.py

功能特性：
- 从文件加载学校列表
- 支持配置文件自定义参数
- 分批处理避免资源耗尽
- 详细的处理报告
- 错误恢复和重试机制

配置文件示例 (`config.json`)：
```json
{
    "years": [2023, 2022],
    "provinces": ["北京", "上海", "广东"],
    "batch_size": 3,
    "delay_between_schools": 5,
    "delay_between_requests": 1,
    "max_retries": 2,
    "save_to_database": true,
    "save_to_json": true,
    "output_dir": "my_output"
}
```

### create_school_list.py

创建不同类型的学校列表文件：
- 基本列表：简单的ID列表
- JSON源列表：从结构化数据创建
- 地区分组列表：按地区分组
- 测试列表：包含错误测试用例

## 自定义配置

### 创建自定义配置文件

1. 创建 `my_config.json`：
```json
{
    "schools": ["150", "151", "152"],
    "years": [2023],
    "provinces": ["北京", "上海"],
    "batch_size": 2
}
```

2. 运行批量处理器：
```bash
python batch_processor.py schools.txt -c my_config.json
```

### 创建学校列表文件

1. 创建 `my_schools.txt`：
```
150
151
152
153
```

2. 运行处理：
```bash
python batch_processor.py my_schools.txt
```

## 输出文件

### 数据文件
- `school_<id>_<timestamp>.json` - 单个学校的爬取数据
- `batch_report_<timestamp>.json` - 批量处理报告

### 日志文件
- `crawler.log` - 主程序日志
- `batch_processor.log` - 批量处理器日志

### 进度文件
- `progress_<school_id>.json` - 断点续传进度文件

## 故障排除

### 常见问题

1. **ChromeDriver错误**
   ```bash
   # 清理缓存
   rm -rf ~/.wdm
   
   # 重新安装依赖
   pip install --upgrade webdriver-manager selenium
   ```

2. **内存不足**
   - 减少 `batch_size`
   - 增加 `delay_between_schools`
   - 定期重启处理器

3. **数据提取失败**
   - 检查页面结构是否变化
   - 查看保存的页面源码
   - 调整等待时间

### 调试模式

```bash
# 显示详细日志
python basic_usage.py 2>&1 | tee debug.log

# 使用非无头模式查看浏览器
python main.py 140 --headless=false --test
```

## 最佳实践

1. **分批次处理**：不要一次性处理太多学校
2. **合理延迟**：设置适当的请求间隔
3. **定期备份**：处理前备份数据库
4. **监控进度**：使用进度文件实现断点续传
5. **验证数据**：定期检查爬取数据的质量

## 扩展开发

### 添加新的示例

1. 创建新的Python文件
2. 导入必要的模块
3. 实现具体功能
4. 更新README文档

### 自定义数据处理

可以修改以下模块：
- `utils.py` - 添加新的数据处理函数
- `crawler.py` - 修改数据提取逻辑
- `database.py` - 添加新的数据库操作

## 注意事项

1. 遵守网站的使用条款
2. 控制爬取频率，避免对服务器造成压力
3. 尊重数据版权和隐私
4. 定期更新代码以适应网站变化