@echo off
chcp 65001 >nul

echo.
echo 🎓 中国高校录取数据查询系统
echo ================================
echo 正在启动开发服务器...
echo.

:: 检查 Node.js 版本
echo 检查环境...
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
set NODE_MAJOR_VERSION=%NODE_VERSION:~1,2%
if %NODE_MAJOR_VERSION% LSS 18 (
    echo ❌ 需要 Node.js ^>= 18.0.0，当前版本：%NODE_VERSION%
    pause
    exit /b 1
)
echo OK: Node.js 已安装

:: 检查依赖
echo.
echo 检查依赖...
if not exist "backend\node_modules" (
    echo WARNING: 后端依赖未安装，正在安装...
    cmd /c "cd backend && npm install"
) else (
    echo OK: 后端依赖已安装
)

if not exist "frontend\node_modules" (
    echo WARNING: 前端依赖未安装，正在安装...
    cmd /c "cd frontend && npm install"
) else (
    echo OK: 前端依赖已安装
)

echo.
echo 启动开发服务器...
echo.
echo 启动后端 API 服务器...
start "Backend Server" cmd /k "cd /d backend && npm run dev"

timeout /t 3 /nobreak >nul

echo 启动前端开发服务器...
start "Frontend Server" cmd /k "cd /d frontend && npm run dev"

timeout /t 2 /nobreak >nul

echo.
echo ✅ 服务器启动成功！
echo ================================
echo 📊 后端 API：http://localhost:3000
echo 📚 API 文档：http://localhost:3000/api
echo 🌐 前端应用：http://localhost:5173
echo 📈 健康检查：http://localhost:3000/health
echo ================================
echo.
echo 📋 可用命令：
echo • Ctrl+C 停止服务器
echo • 查看日志请查看终端输出
echo • 访问上述 URL 开始使用
echo.

pause