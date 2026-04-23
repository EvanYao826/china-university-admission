# CLAUDE.md

本文件为 Claude Code（claude.ai/code）在此仓库中工作时提供指导。

## Commands

```bash
# 安装所有依赖（根目录 + backend + frontend）
npm run install:all

# 同时启动后端（3000 端口）和前端（5173 端口）开发服务器
npm run dev

# 分别启动
npm run dev:backend   # ts-node src/server.ts
npm run dev:frontend  # vite

# 构建
npm run build         # tsc（backend）+ vite build（frontend）

# 初始化数据库
npm run init-db       # node scripts/init-db.js

# 爬虫（Python）
cd crawler/python
pip install -r requirements.txt
python main.py <school_id> [-y years] [-p provinces]
```

## Project Structure

使用 npm workspaces 的 Monorepo（`backend/` 和 `frontend/`）：

```
China-University-Admission/
├── backend/           # Express + TypeScript + better-sqlite3
│   └── src/
│       ├── server.ts              # Express 应用入口，/api/* 路由
│       ├── api/                   # 路由处理器
│       │   ├── school.ts          # /api/schools, /api/undergraduate/admissions, /api/postgraduate/admissions
│       │   ├── university.ts      # /api/universities（CRUD + search + filters）
│       │   ├── admission.ts       # /api/admissions/*（gaokao/graduate/score-match/trends）
│       │   └── search.ts          # /api/search/*（advanced/suggestions/popular）
│       ├── db/                    # 数据库层
│       │   ├── index.ts           # DatabaseManager 单例 - universities、gaokao_admissions、graduate_admissions 表
│       │   ├── school.repo.ts     # SchoolRepository - undergraduate_admissions、postgraduate_admissions 表
│       │   ├── university.repo.ts # UniversityRepository
│       │   └── admission.repo.ts  # AdmissionRepository
│       └── types/index.ts         # 共享 TypeScript 接口
├── frontend/          # Vue 3 + Element Plus + TypeScript + Vite
│   └── src/
│       ├── App.vue                # 根布局（header/main/footer）
│       ├── main.ts                # Vue 应用启动入口（Pinia + Router + Element Plus）
│       ├── router/index.ts        # 单一路由：/ → UniversitiesView
│       ├── api/client.ts          # Axios 封装（baseURL: http://localhost:3000）
│       ├── types/index.ts         # 与后端对应的重复类型定义
│       └── views/UniversitiesView.vue  # 主页面：学校列表 + 标签页（intro/undergrad/postgrad）
├── crawler/python/    # Python Selenium 爬虫（独立于 npm）
│   ├── main.py        # 带 CLI 参数的入口文件
│   ├── crawler.py     # 基于 Selenium 的页面解析
│   ├── database.py    # SQLite 保存逻辑
│   └── config.py      # 省份列表、重试配置
├── data/university.db # SQLite 数据库
└── scripts/           # start.js（并发开发启动器）、init-db.js
```

## Architecture

- **Backend** 路由挂载在 Express 服务器的 `/api` 下。主服务器（`server.ts`）将 `schoolRoutes` 挂载到 `/api`（处理 `/api/schools/*`、`/api/undergraduate/*`、`/api/postgraduate/*`）。`admission.ts` 和 `university.ts` 路由虽然已声明，但没有在主服务器中挂载——当前只有 `schoolRoutes` 处于启用状态。
- **Frontend** 是一个单页应用，只有一个主视图（`UniversitiesView.vue`），包含学校列表侧边栏和三个标签页：学校概览、本科录取、研究生录取。
- **Database** 有两套表结构：旧 schema（`universities`、`gaokao_admissions`、`graduate_admissions`）由 `DatabaseManager` 使用；新 schema（`undergraduate_admissions`、`postgraduate_admissions`）由 `SchoolRepository` 使用。两者都连接到同一个 `data/university.db` 文件。
- **Type definitions** 在 `backend/src/types/index.ts` 和 `frontend/src/types/index.ts` 中各维护了一份——修改时要保持同步。
- **API client**（`frontend/src/api/client.ts`）使用绝对地址 `http://localhost:3000`（而不是 Vite 代理），并且会在 GET 请求中附加用于防缓存的 `_t` 参数。

## Key Patterns

- 后端路由遵循统一模式：使用 zod 校验参数，调用 repo 方法，并将响应包装为 `{ success, data, pagination? }`
- 前端在组件数据中大量使用 `any` 类型——新代码应尽量改用明确类型
- 爬虫是一个独立的 Python 项目，拥有自己的依赖体系，不与 npm 构建流水线集成
