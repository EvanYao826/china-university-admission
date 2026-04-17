@echo off
echo 🎓 中国高校录取数据查询系统
echo ================================
echo.

echo 🔧 检查环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)

echo ✅ Node.js 已安装
echo.

echo 📦 检查依赖...
if not exist "backend\node_modules" (
    echo ⚠️  后端依赖未安装，正在跳过...
) else (
    echo ✅ 后端依赖已安装
)

if not exist "frontend\node_modules" (
    echo ⚠️  前端依赖未安装，正在跳过...
) else (
    echo ✅ 前端依赖已安装
)

echo.

echo 🚀 启动开发服务器...
echo.

echo 📊 启动后端 API 服务器...
start "后端服务器" cmd /k "cd /d backend && npm run dev"

timeout /t 3 /nobreak >nul

echo 🌐 启动前端开发服务器...
start "前端服务器" cmd /k "cd /d frontend && npm run dev"

timeout /t 2 /nobreak >nul

echo.
echo ================================
echo ✅ 服务器启动成功！
echo.
echo 📊 后端 API：http://localhost:3000
echo 📚 API 文档：http://localhost:3000/api
echo 🌐 前端应用：http://localhost:5173
echo 📈 健康检查：http://localhost:3000/health
echo.
echo 📋 提示：
echo • 请保持这两个命令行窗口打开
echo • 按 Ctrl+C 停止服务器
echo • 访问上述 URL 开始使用
echo ================================
echo.

pause