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
- **验证**：Zod
- **API 文档**：自动生成

### 前端 (Vue 3 + TypeScript)
- **框架**：Vue 3 + Composition API
- **UI 组件库**：Element Plus
- **图表库**：ECharts + vue-echarts
- **路由**：Vue Router
- **状态管理**：Pinia
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
cd china-university-admission-hub
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
- API 文档：http://localhost:3000/api

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
university-admission-hub/
├── backend/                    # Node.js 后端
│   ├── src/
│   │   ├── api/               # API 路由层
│   │   ├── db/                # 数据库层
│   │   ├── types/             # TypeScript 类型定义
│   │   └── server.ts          # Express 服务入口
│   ├── package.json
│   └── tsconfig.json
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── components/        # 可复用组件
│   │   ├── views/             # 页面组件
│   │   ├── api/               # API 客户端
│   │   ├── types/             # 类型定义
│   │   ├── router/            # 路由配置
│   │   ├── App.vue
│   │   └── main.ts
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── data/                       # 数据库文件
│   └── university.db          # SQLite 数据库
├── scripts/                    # 辅助脚本
│   ├── start.js               # 启动脚本
│   └── init-db.js             # 数据库初始化
├── docs/                       # 文档
├── package.json               # 根项目配置
└── README.md                  # 项目说明
```

## 📊 数据库设计

### 主要数据表

1. **universities** - 高校基本信息
   - id, name, province, city, type, level, website, description

2. **gaokao_admissions** - 高考录取数据
   - university_id, year, province, category, batch, scores, ranks, admission_count

3. **graduate_admissions** - 研究生录取数据
   - university_id, year, major, degree_type, study_mode, admission_count, scores

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

### 录取数据相关
- `GET /api/admissions/gaokao/:universityId` - 获取高考录取数据
- `GET /api/admissions/graduate/:universityId` - 获取研究生录取数据
- `GET /api/admissions/score/match` - 根据分数匹配高校
- `GET /api/admissions/statistics/:universityId` - 获取录取统计

### 搜索相关
- `GET /api/search/advanced` - 高级搜索
- `GET /api/search/suggestions` - 搜索建议
- `GET /api/search/statistics` - 搜索统计

## 🎨 前端组件

### 核心组件
- `SchoolList.vue` - 高校列表（支持筛选、分页）
- `SchoolDetail.vue` - 高校详情（含图表）
- `AdmissionTable.vue` - 录取数据表格
- `TrendChart.vue` - ECharts 趋势图

### 页面视图
- `HomePage.vue` - 首页（功能概览）
- `UniversitiesView.vue` - 高校查询页面
- `UniversityDetail.vue` - 高校详情页面
- `AdmissionsView.vue` - 录取数据页面
- `ScoreMatchView.vue` - 分数匹配页面
- `StatisticsView.vue` - 数据统计页面

## 📈 数据说明

### 数据来源
- 数据来源于公开渠道整理
- 仅供学习和研究参考
- 请以各高校官方发布为准

### 数据更新
1. 替换 `data/university.db` 文件
2. 重启后端服务

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

## 🛠️ 开发指南

### 环境配置
1. 复制 `.env.example` 到 `.env`
2. 修改环境变量配置
3. 安装开发依赖

### 代码规范
- TypeScript 严格模式
- ESLint + Prettier（可配置）
- 组件使用 Composition API
- 接口响应类型安全

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