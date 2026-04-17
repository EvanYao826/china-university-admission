import { Router, Request, Response } from 'express';
import { AdmissionRepository } from '../db/admission.repo';
import { ApiResponse } from '../types';
import { z } from 'zod';

const router = Router();
const admissionRepo = new AdmissionRepository();

// 输入验证 schema
const gaokaoQuerySchema = z.object({
  year: z.coerce.number().int().min(2000).max(2030).optional(),
  province: z.string().optional(),
  category: z.enum(['文科', '理科', '综合改革', '艺术', '体育']).optional(),
  batch: z.enum(['本科一批', '本科二批', '专科批', '提前批']).optional(),
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().min(1).max(100).default(50),
  sortBy: z.enum(['year', 'avg_score', 'admission_count']).default('year'),
  sortOrder: z.enum(['asc', 'desc']).default('desc')
});

const graduateQuerySchema = z.object({
  year: z.coerce.number().int().min(2000).max(2030).optional(),
  major: z.string().optional(),
  degree_type: z.enum(['硕士', '博士']).optional(),
  study_mode: z.enum(['全日制', '非全日制']).optional(),
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().min(1).max(100).default(50),
  sortBy: z.enum(['year', 'major', 'admission_count']).default('year'),
  sortOrder: z.enum(['asc', 'desc']).default('desc')
});

const scoreSearchSchema = z.object({
  province: z.string(),
  year: z.coerce.number().int().min(2000).max(2030),
  category: z.enum(['文科', '理科', '综合改革', '艺术', '体育']),
  batch: z.enum(['本科一批', '本科二批', '专科批', '提前批']),
  score: z.coerce.number().min(0).max(900),
  limit: z.coerce.number().int().min(1).max(50).default(20)
});

// 获取高校的高考录取数据
router.get('/gaokao/:universityId', async (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const universityId = parseInt(req.params.universityId);
    if (isNaN(universityId)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid university ID'
      });
    }

    const params = gaokaoQuerySchema.parse(req.query);
    const { data, total } = admissionRepo.getGaokaoByUniversity(universityId, params);

    const totalPages = Math.ceil(total / params.limit);

    return res.json({
      success: true,
      data,
      pagination: {
        page: params.page,
        limit: params.limit,
        total,
        totalPages
      }
    });
  } catch (error) {
    console.error('Error fetching gaokao admissions:', error);
    return res.status(400).json({
      success: false,
      error: error instanceof Error ? error.message : 'Invalid request parameters'
    });
  }
});

// 获取高校的研究生录取数据
router.get('/graduate/:universityId', async (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const universityId = parseInt(req.params.universityId);
    if (isNaN(universityId)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid university ID'
      });
    }

    const params = graduateQuerySchema.parse(req.query);
    const { data, total } = admissionRepo.getGraduateByUniversity(universityId, params);

    const totalPages = Math.ceil(total / params.limit);

    return res.json({
      success: true,
      data,
      pagination: {
        page: params.page,
        limit: params.limit,
        total,
        totalPages
      }
    });
  } catch (error) {
    console.error('Error fetching graduate admissions:', error);
    return res.status(400).json({
      success: false,
      error: error instanceof Error ? error.message : 'Invalid request parameters'
    });
  }
});

// 根据分数查询匹配的高校
router.get('/score/match', async (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const params = scoreSearchSchema.parse(req.query);
    const results = admissionRepo.searchByScore(params);

    return res.json({
      success: true,
      data: results
    });
  } catch (error) {
    console.error('Error matching by score:', error);
    return res.status(400).json({
      success: false,
      error: error instanceof Error ? error.message : 'Invalid request parameters'
    });
  }
});

// 获取录取数据统计
router.get('/statistics/:universityId', (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const universityId = parseInt(req.params.universityId);
    if (isNaN(universityId)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid university ID'
      });
    }

    const statistics = admissionRepo.getAdmissionStatistics(universityId);
    return res.json({
      success: true,
      data: statistics
    });
  } catch (error) {
    console.error('Error fetching admission statistics:', error);
    return res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// 获取省份录取数据
router.get('/province/:province', (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const { province } = req.params;
    const year = req.query.year ? parseInt(req.query.year as string) : new Date().getFullYear() - 1;
    const category = (req.query.category as string) || '理科';
    const batch = (req.query.batch as string) || '本科一批';

    const data = admissionRepo.getProvinceAdmissions(province, year, category, batch);
    return res.json({
      success: true,
      data
    });
  } catch (error) {
    console.error('Error fetching province admissions:', error);
    return res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// 获取录取趋势数据
router.get('/trends/:universityId', (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const universityId = parseInt(req.params.universityId);
    if (isNaN(universityId)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid university ID'
      });
    }

    const province = req.query.province as string;
    const category = req.query.category as string;

    const trends = admissionRepo.getAdmissionTrends(universityId, province, category);
    return res.json({
      success: true,
      data: trends
    });
  } catch (error) {
    console.error('Error fetching admission trends:', error);
    return res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// 获取可用的年份列表
router.get('/options/years', (_req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const db = require('../db/index').default.getInstance().getDatabase();

    const gaokaoYears = db.prepare(`
      SELECT DISTINCT year FROM gaokao_admissions ORDER BY year DESC
    `).all() as { year: number }[];

    const graduateYears = db.prepare(`
      SELECT DISTINCT year FROM graduate_admissions ORDER BY year DESC
    `).all() as { year: number }[];

    return res.json({
      success: true,
      data: {
        gaokao: gaokaoYears.map(item => item.year),
        graduate: graduateYears.map(item => item.year)
      }
    });
  } catch (error) {
    console.error('Error fetching year options:', error);
    return res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// 获取可用的省份列表（有录取数据的）
router.get('/options/provinces', (_req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const db = require('../db/index').default.getInstance().getDatabase();

    const provinces = db.prepare(`
      SELECT DISTINCT province FROM gaokao_admissions ORDER BY province
    `).all() as { province: string }[];

    return res.json({
      success: true,
      data: provinces.map(item => item.province)
    });
  } catch (error) {
    console.error('Error fetching province options:', error);
    return res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

export default router;