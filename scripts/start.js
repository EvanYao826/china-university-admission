#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

console.log(`
🎓 中国高校录取数据查询系统
================================
正在启动开发服务器...
`);

// 检查 Node.js 版本
const nodeVersion = process.version;
const requiredVersion = '18.0.0';
if (parseInt(nodeVersion.replace('v', '').split('.')[0]) < 18) {
  console.error(`❌ 需要 Node.js >= ${requiredVersion}，当前版本：${nodeVersion}`);
  process.exit(1);
}

// 启动后端服务器
const backendProcess = spawn('npm', ['run', 'dev'], {
  cwd: path.join(__dirname, '../backend'),
  stdio: 'inherit',
  shell: true
});

// 等待后端启动
setTimeout(() => {
  // 启动前端开发服务器
  const frontendProcess = spawn('npm', ['run', 'dev'], {
    cwd: path.join(__dirname, '../frontend'),
    stdio: 'inherit',
    shell: true
  });

  // 处理进程退出
  const handleExit = (signal) => {
    console.log(`\n${signal} 收到信号，正在关闭服务器...`);

    if (backendProcess) {
      backendProcess.kill('SIGTERM');
    }

    if (frontendProcess) {
      frontendProcess.kill('SIGTERM');
    }

    process.exit(0);
  };

  process.on('SIGINT', () => handleExit('SIGINT'));
  process.on('SIGTERM', () => handleExit('SIGTERM'));

  // 前端进程错误处理
  frontendProcess.on('error', (err) => {
    console.error('❌ 前端启动失败:', err.message);
    handleExit('ERROR');
  });

  // 前端进程退出处理
  frontendProcess.on('exit', (code) => {
    if (code !== 0 && code !== null) {
      console.error(`❌ 前端进程异常退出，代码：${code}`);
      handleExit('EXIT');
    }
  });

}, 2000); // 等待2秒让后端启动

// 后端进程错误处理
backendProcess.on('error', (err) => {
  console.error('❌ 后端启动失败:', err.message);
  console.log('\n请检查：');
  console.log('1. 是否已安装依赖：npm run install:all');
  console.log('2. 端口 3000 是否被占用');
  console.log('3. 数据库文件是否存在：data/university.db');
  process.exit(1);
});

// 后端进程退出处理
backendProcess.on('exit', (code) => {
  if (code !== 0 && code !== null) {
    console.error(`❌ 后端进程异常退出，代码：${code}`);
    process.exit(1);
  }
});

// 显示启动信息
console.log(`
✅ 服务器启动成功！
================================
📊 后端 API：http://localhost:3000
📚 API 文档：http://localhost:3000/api
🌐 前端应用：http://localhost:5173
📈 健康检查：http://localhost:3000/health
================================

📋 可用命令：
• Ctrl+C 停止服务器
• 查看日志请查看终端输出
• 访问上述 URL 开始使用
`);