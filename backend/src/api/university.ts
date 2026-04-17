import { Router, Request, Response } from 'express';
import { UniversityRepository } from '../db/university.repo';
import { SearchParams, ApiResponse } from '../types';
import { z } from 'zod';

const router = Router();
const universityRepo = new UniversityRepository();

// 输入验证 schema
const searchSchema = z.object({
  province: z.string().optional(),
  type: z.string().optional(),
  level: z.string().optional(),
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  sortBy: z.enum(['name', 'province', 'type', 'level']).default('name'),
  sortOrder: z.enum(['asc', 'desc']).default('asc')
});

// 获取所有高校
router.get('/', async (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const params = searchSchema.parse(req.query);
    const { data, total } = universityRepo.getAll(params);

    const totalPages = Math.ceil(total / params.limit);

    res.json({
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
    console.error('Error fetching universities:', error);
    res.status(400).json({
      success: false,
      error: error instanceof Error ? error.message : 'Invalid request parameters'
    });
  }
});

// 获取高校详情
router.get('/:id', (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const id = parseInt(req.params.id);
    if (isNaN(id)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid university ID'
      });
    }

    const university = universityRepo.getById(id);
    if (!university) {
      return res.status(404).json({
        success: false,
        error: 'University not found'
      });
    }

    res.json({
      success: true,
      data: university
    });
  } catch (error) {
    console.error('Error fetching university:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// 搜索高校（按名称）
router.get('/search/:name', (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const { name } = req.params;
    const limit = req.query.limit ? parseInt(req.query.limit as string) : 10;

    if (!name || name.trim().length < 2) {
      return res.status(400).json({
        success: false,
        error: 'Search term must be at least 2 characters'
      });
    }

    const results = universityRepo.searchByName(name, limit);
    res.json({
      success: true,
      data: results
    });
  } catch (error) {
    console.error('Error searching universities:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// 获取筛选选项
router.get('/options/filters', (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const provinces = universityRepo.getProvinces();
    const types = universityRepo.getTypes();
    const levels = universityRepo.getLevels();

    res.json({
      success: true,
      data: {
        provinces,
        types,
        levels
      }
    });
  } catch (error) {
    console.error('Error fetching filter options:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// 获取统计信息
router.get('/statistics/summary', (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const statistics = universityRepo.getStatistics();
    res.json({
      success: true,
      data: statistics
    });
  } catch (error) {
    console.error('Error fetching statistics:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// 按省份获取高校统计
router.get('/statistics/by-province/:province', (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const { province } = req.params;
    const params: SearchParams = { province, limit: 1000 };
    const { data } = universityRepo.getAll(params);

    const byType = data.reduce((acc, uni) => {
      acc[uni.type] = (acc[uni.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const byLevel = data.reduce((acc, uni) => {
      acc[uni.level] = (acc[uni.level] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    res.json({
      success: true,
      data: {
        total: data.length,
        byType,
        byLevel,
        universities: data
      }
    });
  } catch (error) {
    console.error('Error fetching province statistics:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

export default router;