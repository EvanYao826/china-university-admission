import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import path from 'path';
import dotenv from 'dotenv';

// 加载环境变量
dotenv.config();

// 导入路由
import universityRoutes from './api/university';
import admissionRoutes from './api/admission';
import searchRoutes from './api/search';

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件配置
app.use(cors({
  origin: process.env.NODE_ENV === 'production'
    ? ['http://localhost:5173', 'http://localhost:4173']
    : '*',
  credentials: true
}));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 请求日志中间件
app.use((req: Request, res: Response, next: NextFunction) => {
  const start = Date.now();
  const { method, url, ip } = req;

  res.on('finish', () => {
    const duration = Date.now() - start;
    const { statusCode } = res;
    console.log(`${method} ${url} ${statusCode} ${duration}ms - ${ip}`);
  });

  next();
});

// API 路由
app.use('/api/universities', universityRoutes);
app.use('/api/admissions', admissionRoutes);
app.use('/api/search', searchRoutes);

// 健康检查端点
app.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'university-admission-api',
    version: '1.0.0'
  });
});

// API 文档端点
app.get('/api', (req: Request, res: Response) => {
  res.json({
    name: 'University Admission API',
    version: '1.0.0',
    description: '中国高校录取数据查询系统 API',
    endpoints: {
      universities: {
        base: '/api/universities',
        endpoints: [
          'GET / - 获取所有高校（支持分页和筛选）',
          'GET /:id - 获取高校详情',
          'GET /search/:name - 按名称搜索高校',
          'GET /options/filters - 获取筛选选项',
          'GET /statistics/summary - 获取统计信息'
        ]
      },
      admissions: {
        base: '/api/admissions',
        endpoints: [
          'GET /gaokao/:universityId - 获取高校高考录取数据',
          'GET /graduate/:universityId - 获取高校研究生录取数据',
          'GET /score/match - 根据分数查询匹配高校',
          'GET /statistics/:universityId - 获取录取数据统计',
          'GET /trends/:universityId - 获取录取趋势数据'
        ]
      },
      search: {
        base: '/api/search',
        endpoints: [
          'GET /advanced - 综合搜索',
          'GET /suggestions - 搜索建议',
          'GET /popular - 热门搜索',
          'GET /statistics - 搜索统计'
        ]
      }
    }
  });
});

// 错误处理中间件
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error('Unhandled error:', err);

  res.status(500).json({
    success: false,
    error: process.env.NODE_ENV === 'development'
      ? err.message
      : 'Internal server error',
    timestamp: new Date().toISOString()
  });
});

// 404 处理
app.use((req: Request, res: Response) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found',
    path: req.url,
    method: req.method
  });
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`
  🚀 University Admission API Server
  =================================
  📍 Environment: ${process.env.NODE_ENV || 'development'}
  🌐 Server URL: http://localhost:${PORT}
  📊 Health Check: http://localhost:${PORT}/health
  📚 API Docs: http://localhost:${PORT}/api
  🕐 Started at: ${new Date().toISOString()}
  =================================
  `);
});

// 优雅关闭
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully...');
  process.exit(0);
});

export default app;