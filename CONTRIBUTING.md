# 数据贡献指南

感谢你为“中国高校招生数据查询工具”贡献数据。

本项目欢迎社区补充：

- 高校基础信息
- 本科招生/录取数据
- 研究生招生/录取数据

## 一、提交数据前请先了解

为了保证仓库结构清晰、数据格式统一，请优先使用仓库提供的 CSV 模板提交数据。

### 推荐做法

- 使用 `data/templates/` 中的模板文件
- 将你填写后的文件放到 `data/submissions/`
- 通过 Pull Request 提交

### 不推荐做法

- 不要直接修改 `data/university.db`
- 不要只提交截图而不整理成结构化数据
- 不要提交没有来源说明的数据

## 二、你应该选择哪个模板？

### 1. 高校基础信息
使用：`data/templates/universities.template.csv`

适用场景：
- 新增一所还未收录的高校
- 补充学校的类型、层次、省份、城市、简介等信息

### 2. 本科招生/录取数据
使用：`data/templates/undergraduate_admissions.template.csv`

适用场景：
- 补充某高校某省份某年份的本科录取分数、位次、批次等信息

### 3. 研究生招生/录取数据
使用：`data/templates/postgraduate_admissions.template.csv`

适用场景：
- 补充某高校某年份的研究生复试线、调剂信息等数据

## 三、标准提交流程

### 第 1 步：Fork 仓库
先将本仓库 Fork 到你自己的 GitHub 账号下。

### 第 2 步：复制模板
从 `data/templates/` 复制对应模板，不要直接修改模板原文件。

### 第 3 步：填写 CSV
建议将填写后的文件存放到：`data/submissions/`

建议文件名格式：

```text
学校名-省份-年份-数据类型.csv
```

示例：

```text
浙江大学-浙江-2024-本科录取数据.csv
北京大学-全国-2025-研究生复试线.csv
华中科技大学-高校基础信息.csv
```

### 第 4 步：检查内容
提交前请检查：

- 学校名称是否正确，是否与项目中现有学校名称一致
- 年份是否正确
- 省份名称是否规范
- 数值字段是否填写为数字
- 空缺字段是否确实无法获取
- `source_url` 是否填写

### 第 5 步：提交 Pull Request
请在 PR 中说明：

- 本次补充的是哪所学校
- 涉及哪个省份、哪一年
- 数据类型（高校信息 / 本科 / 研究生）
- 数据来源链接
- 是否已自查重复记录和空值

推荐 PR 标题格式：

```text
data: 补充浙江大学 2024 年浙江省本科录取数据
```

## 四、字段填写说明

## 1. universities.template.csv

字段说明：

- `name`：学校名称，必填
- `province`：学校所在省份，必填
- `city`：学校所在城市，建议填写
- `type`：学校类型，如综合、理工、师范、医药等
- `level`：学校层次，如 985、211、双一流、普通本科、专科
- `tags`：标签，多个标签可用英文逗号分隔
- `logo_url`：学校 logo 图片链接，可留空
- `description`：学校简介，可简要填写

## 2. undergraduate_admissions.template.csv

字段说明：

- `university_name`：学校名称，必填
- `province`：招生省份，必填
- `year`：年份，必填
- `category`：科类/选科类别，如物理类、历史类、综合改革
- `batch`：批次，如本科批、本科一批、提前批等
- `enrollment_type`：招生类型，如普通类、国家专项、强基计划等
- `major`：专业名称，没有专业维度时可留空
- `min_score`：最低分
- `min_rank`：最低位次
- `avg_score`：平均分
- `provincial_control_line`：省控线
- `subject_requirements`：选科要求
- `professional_group`：专业组
- `source_url`：数据来源链接，强烈建议填写

## 3. postgraduate_admissions.template.csv

字段说明：

- `university_name`：学校名称，必填
- `year`：年份，必填
- `degree_type`：学位类型，如学术学位、专业学位
- `discipline_category`：学科门类或专业类别
- `admission_type`：数据类型，如普通复试线、调剂信息
- `political_score`：政治分数线
- `foreign_language_score`：外语分数线
- `subject1_score`：业务课一分数线
- `subject2_score`：业务课二分数线
- `total_score`：总分线
- `remarks`：备注
- `adjustment_info`：调剂说明，仅调剂类数据建议填写
- `source_url`：数据来源链接，强烈建议填写

## 五、数据来源要求

请优先使用以下公开来源：

- 高校官方网站
- 各省教育考试院官网
- 中国研究生招生信息网
- 教育部及其公开数据平台

请尽量避免：

- 无法核实的二手转载
- 没有原始出处的截图
- 论坛口口相传的数据
- 明显与官方数据冲突但无法说明原因的数据

## 六、提交时常见问题

### 1. 我需要自己新建数据库吗？
不需要。普通贡献者只需要提交 CSV 即可。

### 2. 我需要直接改 SQLite 文件吗？
不需要，也不建议这样做。

### 3. 以后会支持自动导入 CSV 吗？
可以，后续维护者可以增加 CSV 导入脚本。但当前推荐流程仍然是：**先按模板提交 CSV，再由维护者审核和导入**。

### 4. 如果有些字段查不到怎么办？
可以留空，但不要填写猜测值。请优先保证学校名称、省份、年份、来源链接正确。

### 5. 如果项目里已有这所学校，还能提交吗？
可以。你可以补充新的年份、省份或新的数据类型，也可以修正错误数据。

### 6. 可以一次提交很多学校吗？
可以，但建议按学校、年份或数据类型拆分提交，便于审核。

## 七、维护者审核重点

维护者通常会重点检查：

- 字段是否与模板一致
- 数据是否来自公开可靠来源
- 学校名称是否统一
- 是否存在明显重复记录
- 分数、位次、年份是否异常

## 八、联系方式

如果你不方便提交 Pull Request，也可以先通过 GitHub Issues 提出数据补充建议：

- 项目地址：<https://github.com/EvanYao826/China-University-Admission>
- Issues：<https://github.com/EvanYao826/China-University-Admission/issues>
