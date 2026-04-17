import { Router, Request, Response } from 'express';
import { AdmissionRepository } from '../db/admission.repo';
import { ApiResponse } from '../types';
import { z } from 'zod';

const router = Router();
const admissionRepo = new AdmissionRepository();

// 输入验证 schema
const advancedSearchSchema = z.object({
  q: z.string().optional(),
  province: z.string().optional(),
  type: z.string().optional(),
  level: z.string().optional(),
  year: z.coerce.number().int().min(2000).max(2030).optional(),
  minScore: z.coerce.number().min(0).max(900).optional(),
  maxScore: z.coerce.number().min(0).max(900).optional(),
  category: z.enum(['文科', '理科', '综合改革', '艺术', '体育']).optional(),
  batch: z.enum(['本科一批', '本科二批', '专科批', '提前批']).optional(),
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  sortBy: z.enum(['name', 'avg_score', 'admission_count', 'year']).default('name'),
  sortOrder: z.enum(['asc', 'desc']).default('asc')
});

// 综合搜索接口
router.get('/advanced', async (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const params = advancedSearchSchema.parse(req.query);
    const { q, province, type, level, year, minScore, maxScore, category, batch, page, limit, sortBy, sortOrder } = params;

    // 获取数据库连接
    const db = require('../db/index').default.getInstance().getDatabase();

    // 构建基础查询
    let query = `
      SELECT DISTINCT u.*,
             ga.avg_score, ga.year as admission_year,
             ga.province as admission_province,
             ga.category, ga.batch
      FROM universities u
      LEFT JOIN gaokao_admissions ga ON u.id = ga.university_id
      WHERE 1=1
    `;

    const conditions: string[] = [];
    const values: any[] = [];

    // 文本搜索
    if (q && q.trim().length >= 2) {
      conditions.push('(u.name LIKE ? OR u.description LIKE ?)');
      values.push(`%${q}%`, `%${q}%`);
    }

    // 高校属性筛选
    if (province) {
      conditions.push('u.province = ?');
      values.push(province);
    }

    if (type) {
      conditions.push('u.type = ?');
      values.push(type);
    }

    if (level) {
      conditions.push('u.level = ?');
      values.push(level);
    }

    // 录取数据筛选
    if (year) {
      conditions.push('ga.year = ?');
      values.push(year);
    }

    if (category) {
      conditions.push('ga.category = ?');
      values.push(category);
    }

    if (batch) {
      conditions.push('ga.batch = ?');
      values.push(batch);
    }

    if (minScore !== undefined) {
      conditions.push('ga.avg_score >= ?');
      values.push(minScore);
    }

    if (maxScore !== undefined) {
      conditions.push('ga.avg_score <= ?');
      values.push(maxScore);
    }

    // 添加所有条件
    if (conditions.length > 0) {
      query += ' AND ' + conditions.join(' AND ');
    }

    // 获取总数
    const countQuery = `SELECT COUNT(DISTINCT u.id) as total FROM universities u LEFT JOIN gaokao_admissions ga ON u.id = ga.university_id WHERE 1=1 ${conditions.length > 0 ? 'AND ' + conditions.join(' AND ') : ''}`;
    const countStmt = db.prepare(countQuery);
    const countResult = countStmt.get(...values) as { total: number };
    const total = countResult.total;

    // 排序
    let orderBy = 'u.name COLLATE NOCASE';
    if (sortBy === 'avg_score') {
      orderBy = 'ga.avg_score';
    } else if (sortBy === 'admission_count') {
      orderBy = 'ga.admission_count';
    } else if (sortBy === 'year') {
      orderBy = 'ga.year';
    }

    query += ` ORDER BY ${orderBy} ${sortOrder.toUpperCase()}`;

    // 分页
    const offset = (page - 1) * limit;
    query += ` LIMIT ? OFFSET ?`;
    values.push(limit, offset);

    // 执行查询
    const stmt = db.prepare(query);
    const data = stmt.all(...values);

    // 为每个高校获取录取数据统计
    const enhancedData = await Promise.all(
      data.map(async (university: any) => {
        const stats = admissionRepo.getAdmissionStatistics(university.id);
        return {
          ...university,
          statistics: stats
        };
      })
    );

    const totalPages = Math.ceil(total / limit);

    return res.json({
      success: true,
      data: enhancedData,
      pagination: {
        page,
        limit,
        total,
        totalPages
      }
    });
  } catch (error) {
    console.error('Error in advanced search:', error);
    return res.status(400).json({
      success: false,
      error: error instanceof Error ? error.message : 'Invalid request parameters'
    });
  }
});

// 快速搜索建议
router.get('/suggestions', (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const query = req.query.q as string;
    if (!query || query.trim().length < 2) {
      return res.json({
        success: true,
        data: []
      });
    }

    const db = require('../db/index').default.getInstance().getDatabase();

    // 搜索高校名称
    const universityStmt = db.prepare(`
      SELECT id, name, province, level, type
      FROM universities
      WHERE name LIKE ?
      ORDER BY name COLLATE NOCASE
      LIMIT 10
    `);

    const universities = universityStmt.all(`%${query}%`);

    // 搜索专业（研究生）
    const majorStmt = db.prepare(`
      SELECT DISTINCT major
      FROM graduate_admissions
      WHERE major LIKE ?
      ORDER BY major
      LIMIT 5
    `);

    const majors = majorStmt.all(`%${query}%`);

    return res.json({
      success: true,
      data: {
        universities,
        majors: majors.map((m: any) => m.major)
      }
    });
  } catch (error) {
    console.error('Error fetching suggestions:', error);
    return res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// 热门搜索
router.get('/popular', (_req: Request, res: Response<ApiResponse<any>>) => {
  try {
    // 这里可以添加搜索热度统计逻辑
    // 暂时返回一些常见搜索
    const popularSearches = [
      { term: '清华大学', type: 'university' },
      { term: '北京大学', type: 'university' },
      { term: '计算机科学', type: 'major' },
      { term: '北京', type: 'province' },
      { term: '上海', type: 'province' },
      { term: '985高校', type: 'level' },
      { term: '2024年录取', type: 'year' }
    ];

    return res.json({
      success: true,
      data: popularSearches
    });
  } catch (error) {
    console.error('Error fetching popular searches:', error);
    return res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// 搜索历史（简化版，实际应该基于用户会话）
router.get('/history', (_req: Request, res: Response<ApiResponse<any>>) => {
  try {
    // 这里可以添加基于会话的搜索历史
    // 暂时返回空数组
    return res.json({
      success: true,
      data: []
    });
  } catch (error) {
    console.error('Error fetching search history:', error);
    return res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// 搜索统计
router.get('/statistics', (_req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const db = require('../db/index').default.getInstance().getDatabase();

    // 获取搜索相关统计
    const totalUniversitiesResult = db.prepare('SELECT COUNT(*) as count FROM universities').get() as { count: number };
    const totalGaokaoRecordsResult = db.prepare('SELECT COUNT(*) as count FROM gaokao_admissions').get() as { count: number };
    const totalGraduateRecordsResult = db.prepare('SELECT COUNT(*) as count FROM graduate_admissions').get() as { count: number };
    const latestYearResult = db.prepare('SELECT MAX(year) as year FROM gaokao_admissions').get() as { year: number };

    const totalUniversities = totalUniversitiesResult.count;
    const totalGaokaoRecords = totalGaokaoRecordsResult.count;
    const totalGraduateRecords = totalGraduateRecordsResult.count;
    const latestYear = latestYearResult.year;

    return res.json({
      success: true,
      data: {
        totalUniversities,
        totalGaokaoRecords,
        totalGraduateRecords,
        latestYear,
        dataUpdated: new Date().toISOString().split('T')[0]
      }
    });
  } catch (error) {
    console.error('Error fetching search statistics:', error);
    return res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

export default router;