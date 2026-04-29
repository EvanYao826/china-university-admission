import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

import schoolRoutes from './api/school';
import universityRoutes from './api/university';
import admissionRoutes from './api/admission';
import searchRoutes from './api/search';

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors({
  origin: process.env.NODE_ENV === 'production'
    ? ['http://localhost:5173', 'http://localhost:4173']
    : '*',
  credentials: true
}));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

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

app.use('/api', schoolRoutes);
app.use('/api', universityRoutes);
app.use('/api', admissionRoutes);
app.use('/api', searchRoutes);

app.get('/health', (_req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'university-admission-api',
    version: '1.0.0'
  });
});

app.get('/api', (_req: Request, res: Response) => {
  res.json({
    name: 'University Admission API',
    version: '1.0.0',
    description: '中国高校录取数据查询系统 API',
    endpoints: {
      schools: {
        base: '/api/schools',
        endpoints: [
          'GET / - 获取所有学校',
          'GET /schools/:id - 获取学校详情'
        ]
      },
      undergraduate: {
        base: '/api/undergraduate',
        endpoints: [
          'GET /yearly - 获取本科历年分数',
          'GET /major - 获取专业分数'
        ]
      },
      postgraduate: {
        base: '/api/postgraduate',
        endpoints: [
          'GET /info - 获取研究生招生信息',
          'GET /reply-lines - 获取复试分数线'
        ]
      }
    }
  });
});

app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  console.error('Unhandled error:', err);

  res.status(500).json({
    success: false,
    error: process.env.NODE_ENV === 'development'
      ? err.message
      : 'Internal server error',
    timestamp: new Date().toISOString()
  });
});

app.use((req: Request, res: Response) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found',
    path: req.url,
    method: req.method
  });
});

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

process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully...');
  process.exit(0);
});

export default app;
