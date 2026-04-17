# 中国高校录取数据查询系统

一个现代化的中国高校录取数据查询系统，提供高考和研究生录取数据的一站式查询服务，支持数据可视化分析和智能推荐。

## 🌟 功能特性

- **高校信息查询**：按省份、类型、层次筛选高校
- **录取数据查看**：历年高考、研究生录取分数线和招生人数
- **分数匹配推荐**：根据分数推荐合适的高校和专业
- **数据可视化**：图表展示录取趋势和统计数据
- **高校对比**：多所高校的横向对比分析
- **搜索功能**：支持高校、专业的快速搜索
- **响应式设计**：支持桌面和移动设备
- **数据爬虫**：内置Python和TypeScript爬虫脚本

## 🏗️ 技术架构

### 后端 (Node.js + Express + TypeScript)
- **框架**：Express.js
- **数据库**：SQLite (better-sqlite3)
- **语言**：TypeScript
- **验证**：Zod
- **API 文档**：自动生成

### 前端 (Vue 3 + TypeScript)
- **框架**：Vue 3 + Composition API
- **UI 组件库**：Element Plus
- **图表库**：ECharts
- **路由**：Vue Router
- **构建工具**：Vite

### 爬虫模块
- **Python 爬虫**：数据抓取和清洗
- **TypeScript 爬虫**：与后端集成
- **数据处理**：PDF解析、数据清洗

### 数据层
- **数据库**：SQLite 单文件数据库
- **数据格式**：预打包的 `.db` 文件
- **数据来源**：公开渠道整理（仅供学习参考）

## 🚀 快速开始

### 环境要求
- Node.js >= 18.0.0
- npm >= 8.0.0
- Python 3.8+ (可选，用于爬虫)

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd china-university-admission-hub
```

2. **安装依赖**
```bash
npm run install:all

# 安装Python爬虫依赖（可选）
cd crawler/python
pip install -r requirements.txt
```

3. **启动开发服务器**
```bash
# 方法1：使用npm命令
npm run dev

# 方法2：使用启动脚本
# Windows
./start.bat
# PowerShell
./start.ps1
```

4. **访问应用**
- 前端：http://localhost:5173
- 后端 API：http://localhost:3000
- API 文档：http://localhost:3000/api
- 健康检查：http://localhost:3000/health

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
china-university-admission-hub/
├── backend/                    # Node.js 后端
│   ├── data/                  # 后端数据库
│   ├── src/
│   │   ├── api/               # API 路由层
│   │   ├── db/                # 数据库层
│   │   ├── types/             # TypeScript 类型定义
│   │   └── server.ts          # Express 服务入口
│   ├── package.json
│   └── tsconfig.json
├── crawler/                    # 爬虫模块
│   ├── python/                # Python 爬虫
│   │   ├── data_clean.py      # 数据清洗
│   │   ├── fetch_gaokao.py    # 高考数据抓取
│   │   ├── fetch_graduate.py  # 研究生数据抓取
│   │   ├── parse_pdf.py       # PDF解析
│   │   └── requirements.txt   # Python依赖
│   └── typescript/            # TypeScript 爬虫
│       ├── crawl_ts.ts        # TS爬虫实现
│       ├── package.json
│       └── tsconfig.json
├── data/                       # 数据库文件
│   ├── sample.csv             # 示例数据
│   ├── schema.sql             # 数据库结构
│   └── university.db          # SQLite 数据库
├── docs/                       # 文档
│   ├── API.md                 # API文档
│   ├── CRAWLER_GUIDE.md       # 爬虫指南
│   └── DATA_SOURCES.md        # 数据源说明
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── api/               # API 客户端
│   │   ├── components/        # 可复用组件
│   │   ├── router/            # 路由配置
│   │   ├── types/             # 类型定义
│   │   ├── views/             # 页面组件
│   │   ├── App.vue
│   │   └── main.ts
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
├── scripts/                    # 辅助脚本
│   ├── build-frontend.js      # 前端构建脚本
│   ├── init-db.js             # 数据库初始化
│   └── start.js               # 启动脚本
├── .gitignore
├── LICENSE
├── QUICKSTART.md              # 快速启动指南
├── README.md                  # 项目说明
├── package.json               # 根项目配置
├── start.bat                  # Windows启动脚本
└── start.ps1                  # PowerShell启动脚本
```

## 📊 数据库设计

### 主要数据表

1. **universities** - 高校基本信息
   - id, name, province, city, type, level, website, description, created_at, updated_at

2. **gaokao_admissions** - 高考录取数据
   - id, university_id, year, province, category, batch, min_score, avg_score, max_score, min_rank, avg_rank, max_rank, admission_count, major, notes, created_at, updated_at

3. **graduate_admissions** - 研究生录取数据
   - id, university_id, year, major, degree_type, study_mode, admission_count, min_score, avg_score, max_score, notes, created_at, updated_at

### 数据关系
```
universities (1) ── (n) gaokao_admissions
                └── (n) graduate_admissions
```

## 🔧 API 接口

### 高校相关
- `GET /api/universities` - 获取高校列表（支持分页筛选）
- `GET /api/universities/:id` - 获取高校详情
- `GET /api/universities/search/:name` - 搜索高校
- `GET /api/universities/options/filters` - 获取筛选选项
- `GET /api/universities/statistics/summary` - 获取高校统计信息

### 录取数据相关
- `GET /api/admissions/gaokao/:universityId` - 获取高考录取数据
- `GET /api/admissions/graduate/:universityId` - 获取研究生录取数据
- `GET /api/admissions/score/match` - 根据分数匹配高校
- `GET /api/admissions/statistics/:universityId` - 获取录取统计
- `GET /api/admissions/province/:province` - 获取省份录取数据
- `GET /api/admissions/trends/:universityId` - 获取录取趋势数据
- `GET /api/admissions/options/years` - 获取可用年份列表
- `GET /api/admissions/options/provinces` - 获取可用省份列表

### 搜索相关
- `GET /api/search/advanced` - 高级搜索
- `GET /api/search/suggestions` - 搜索建议
- `GET /api/search/popular` - 热门搜索
- `GET /api/search/history` - 搜索历史
- `GET /api/search/statistics` - 搜索统计

## 🎨 前端组件

### 核心组件
- `SchoolList.vue` - 高校列表（支持筛选、分页）

### 页面视图
- `HomePage.vue` - 首页（功能概览）
- `UniversitiesView.vue` - 高校查询页面
- `UniversityDetail.vue` - 高校详情页面
- `AdmissionsView.vue` - 录取数据页面
- `ScoreMatchView.vue` - 分数匹配页面
- `StatisticsView.vue` - 数据统计页面
- `SearchView.vue` - 搜索结果页面
- `CompareView.vue` - 高校对比页面
- `NotFound.vue` - 404页面

## 🕷️ 爬虫使用

### Python 爬虫
```bash
# 抓取高考数据
cd crawler/python
python fetch_gaokao.py

# 抓取研究生数据
python fetch_graduate.py

# 数据清洗
python data_clean.py
```

### TypeScript 爬虫
```bash
# 安装依赖
cd crawler/typescript
npm install

# 运行爬虫
npm run crawl
```

### 爬虫配置
- 详细配置请参考 [CRAWLER_GUIDE.md](docs/CRAWLER_GUIDE.md)
- 数据源说明请参考 [DATA_SOURCES.md](docs/DATA_SOURCES.md)

## 📈 数据说明

### 数据来源
- 数据来源于公开渠道整理
- 仅供学习和研究参考
- 请以各高校官方发布为准

### 数据更新
1. 使用爬虫脚本抓取最新数据
2. 替换 `data/university.db` 文件
3. 重启后端服务

### 数据格式
- 数据库：SQLite 格式
- 备份：可导出为 CSV/JSON
- 导入：支持 CSV 数据导入

## 🔒 安全与合规

### 数据安全
- 仅提供查询接口，不修改数据
- 无用户认证系统（可扩展）
- 请求频率限制（可配置）

### 合规声明
- 数据仅供参考，不构成报考建议
- 尊重数据来源版权
- 禁止商业用途
- 爬虫使用需遵守相关网站的robots.txt规则

## 🛠️ 开发指南

### 环境配置
1. 复制 `.env.example` 到 `.env`（如果存在）
2. 修改环境变量配置
3. 安装开发依赖

### 代码规范
- TypeScript 严格模式
- 组件使用 Composition API
- 接口响应类型安全
- 遵循现有代码风格

### 测试
```bash
# 运行测试（待实现）
npm test

# 代码检查
npm run lint
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

### 开发规范
- 遵循现有代码风格
- 添加必要的类型定义
- 更新相关文档
- 编写测试用例

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 感谢所有数据提供者
- 感谢开源社区的支持
- 感谢贡献者的付出

## 📞 支持与反馈

- 问题反馈：[GitHub Issues](https://github.com/your-username/china-university-admission-hub/issues)
- 功能建议：[GitHub Discussions](https://github.com/your-username/china-university-admission-hub/discussions)
- 文档更新：提交 Pull Request

---

**注意**：本项目为教育用途，数据仅供参考。实际报考请以各高校官方发布信息为准。

**爬虫使用声明**：请遵守相关法律法规和网站使用条款，合理使用爬虫功能。