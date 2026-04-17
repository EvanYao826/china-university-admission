# 中国高校录取数据查询系统

一个现代化的中国高校录取数据查询系统，提供高考和研究生录取数据的一站式查询服务。

## 🌟 功能特性

- **高校信息查询**：按省份、类型、层次筛选高校
- **录取数据查看**：历年高考、研究生录取分数线和招生人数
- **分数匹配推荐**：根据分数推荐合适的高校和专业
- **数据可视化**：图表展示录取趋势和统计数据
- **高校对比**：多所高校的横向对比分析
- **响应式设计**：支持桌面和移动设备

## 🏗️ 技术架构

### 后端 (Node.js + Express + TypeScript)
- **框架**：Express.js
- **数据库**：SQLite (better-sqlite3)
- **语言**：TypeScript
- **API 设计**：RESTful API

### 前端 (Vue 3 + TypeScript)
- **框架**：Vue 3 + Composition API
- **UI 组件库**：Element Plus
- **路由**：Vue Router
- **构建工具**：Vite

### 数据层
- **数据库**：SQLite 单文件数据库
- **数据格式**：预打包的 `.db` 文件
- **数据来源**：公开渠道整理（仅供学习参考）

## 🚀 快速开始

### 环境要求
- Node.js >= 18.0.0
- npm >= 8.0.0

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd China-University-Admission
```

2. **安装依赖**
```bash
npm run install:all
```

3. **启动开发服务器**
```bash
npm run dev
```

4. **访问应用**
- 前端：http://localhost:5173
- 后端 API：http://localhost:3000

### 生产部署

1. **构建项目**
```bash
npm run build
```

2. **启动生产服务器**
```bash
npm start
```

## 📁 项目结构

```
China-University-Admission/
├── backend/                    # Node.js 后端
│   ├── src/
│   │   ├── api/               # API 路由层
│   │   ├── db/                # 数据库层
│   │   ├── types/             # TypeScript 类型定义
│   │   └── server.ts          # Express 服务入口
│   ├── package.json
│   └── tsconfig.json
├── crawler/                    # 爬虫模块
│   ├── python/                # Python 爬虫
│   └── typescript/            # TypeScript 爬虫
├── data/                       # 数据库文件
│   ├── university.db          # SQLite 数据库
│   └── schema.sql             # 数据库 schema
├── docs/                       # 文档
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── api/               # API 客户端
│   │   ├── components/        # 可复用组件
│   │   ├── router/            # 路由配置
│   │   ├── types/             # 类型定义
│   │   ├── views/             # 页面组件
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
├── scripts/                    # 辅助脚本
│   ├── start.js               # 启动脚本
│   └── init-db.js             # 数据库初始化
├── package.json               # 根项目配置
├── README.md                  # 项目说明
├── start.bat                  # Windows 启动脚本
└── start.ps1                 # PowerShell 启动脚本
```

## 📊 数据库设计

### 主要数据表

1. **schools** - 学校基本信息
   - id, name, type, level, province, description, nature, education_level, category, address, tags, phone

2. **undergraduate_yearly_scores** - 本科历年整体录取分数线
   - id, school_id, year, province, batch, enrollment_type, category, professional_group, subject_requirement, min_score, min_rank, avg_score, provincial_control, data_source

3. **undergraduate_major_scores** - 本科各专业录取分数线
   - id, school_id, year, province, major_name, batch, avg_score, min_score, min_rank, major_group, subject_requirement

4. **postgraduate_info** - 研究生招生简章/宏观信息
   - id, school_id, year, enrollment_plan, registration_start, registration_end, exam_date_start, exam_date_end, majors_offered, contact_phone, official_website, important_notes, brochure_url

5. **postgraduate_reply_lines** - 研究生复试基本分数线
   - id, school_id, year, line_type, category_name, category_code, politics, foreign_language, 专业课1, 专业课2, total_score, remarks

## 🔧 API 接口

### 学校相关
- `GET /api/schools` - 获取学校列表（支持筛选）
- `GET /api/schools/:id` - 获取学校详情

### 本科录取相关
- `GET /api/undergraduate/yearly` - 获取本科历年分数线
- `GET /api/undergraduate/major` - 获取本科专业分数线

### 研究生录取相关
- `GET /api/postgraduate/info` - 获取研究生招生信息
- `GET /api/postgraduate/reply-lines` - 获取研究生复试线

## 🎨 前端组件

### 核心页面
- `HomePage.vue` - 首页
- `UniversitiesView.vue` - 高校查询页面

## 📈 数据说明

### 数据来源
- 数据来源于公开渠道整理
- 仅供学习和研究参考
- 请以各高校官方发布为准

### 数据更新
1. 运行爬虫脚本获取最新数据
2. 替换 `data/university.db` 文件
3. 重启后端服务

## 🔒 安全与合规

### 数据安全
- 仅提供查询接口，不修改数据
- 无用户认证系统（可扩展）
- 请求频率限制（可配置）

### 合规声明
- 数据仅供参考，不构成报考建议
- 尊重数据来源版权
- 禁止商业用途

## 🛠️ 开发指南

### 环境配置
1. 复制 `.env.example` 到 `.env`
2. 修改环境变量配置
3. 安装开发依赖

### 代码规范
- TypeScript 严格模式
- 组件使用 Composition API
- 接口响应类型安全

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

### 开发规范
- 遵循现有代码风格
- 添加必要的类型定义
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 感谢所有数据提供者
- 感谢开源社区的支持
- 感谢贡献者的付出

---

**注意**：本项目为教育用途，数据仅供参考。实际报考请以各高校官方发布信息为准。
