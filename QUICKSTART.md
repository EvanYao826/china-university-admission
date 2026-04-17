# 快速开始指南

## 🚀 一键启动（推荐）

### Windows 用户
1. 下载项目到本地
2. 双击 `start.bat`（如果存在）或执行以下命令：
```bash
npm run install:all
npm run dev
```

### macOS/Linux 用户
```bash
chmod +x scripts/*.js
npm run install:all
npm run dev
```

## 📦 手动安装步骤

### 1. 安装 Node.js
确保已安装 Node.js 18+ 和 npm 8+
```bash
node --version  # 应该显示 v18.x.x 或更高
npm --version   # 应该显示 8.x.x 或更高
```

### 2. 安装依赖
```bash
# 安装根项目依赖
npm install

# 安装后端依赖
cd backend
npm install

# 安装前端依赖
cd ../frontend
npm install

# 返回根目录
cd ..
```

### 3. 初始化数据库
```bash
# 创建示例数据库
node scripts/init-db.js
```

### 4. 启动开发服务器
```bash
# 方法1：使用启动脚本（推荐）
npm run dev

# 方法2：分别启动
npm run dev:backend  # 在第一个终端
npm run dev:frontend # 在第二个终端
```

## 🌐 访问应用

启动成功后，打开浏览器访问：

- **前端应用**：http://localhost:5173
- **后端 API**：http://localhost:3000
- **API 文档**：http://localhost:3000/api
- **健康检查**：http://localhost:3000/health

## 🔧 常见问题

### 1. 端口被占用
如果端口 3000 或 5173 被占用，可以修改配置文件：

**后端端口**：修改 `backend/.env` 中的 `PORT`
**前端端口**：修改 `frontend/vite.config.ts` 中的 `server.port`

### 2. 数据库连接失败
确保 `data/university.db` 文件存在，或者运行：
```bash
node scripts/init-db.js
```

### 3. 依赖安装失败
尝试清理缓存后重新安装：
```bash
npm cache clean --force
npm run install:all
```

### 4. 启动脚本错误
如果 `npm run dev` 失败，可以手动启动：
```bash
# 终端1：启动后端
cd backend
npm run dev

# 终端2：启动前端
cd frontend
npm run dev
```

## 📁 项目结构说明

```
china-university-admission-hub/
├── backend/          # Node.js 后端服务
├── frontend/         # Vue 3 前端应用
├── data/             # 数据库文件
├── scripts/          # 辅助脚本
├── docs/             # 文档
└── README.md         # 详细文档
```

## 🎯 功能测试

启动后，可以测试以下功能：

1. **首页**：查看系统概览和热门高校
2. **高校查询**：按条件筛选高校
3. **录取数据**：查看历年录取分数线
4. **分数匹配**：根据分数推荐高校
5. **数据统计**：查看可视化图表

## 🔄 更新数据

### 更新数据库
1. 替换 `data/university.db` 文件
2. 重启后端服务

### 导入自定义数据
1. 准备 CSV 格式数据
2. 使用数据库工具导入
3. 重启服务生效

## 🛠️ 开发工具推荐

- **代码编辑器**：VS Code
- **数据库工具**：DB Browser for SQLite
- **API 测试**：Postman 或 Insomnia
- **浏览器**：Chrome 或 Edge

## 📞 获取帮助

如果遇到问题：

1. 查看 `README.md` 获取详细文档
2. 检查控制台错误信息
3. 确保所有依赖已正确安装
4. 验证数据库文件完整性

---

**提示**：首次启动可能需要几分钟时间安装依赖，请耐心等待。