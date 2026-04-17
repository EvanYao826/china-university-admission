import { Router, Request, Response } from 'express';
import { SchoolRepository } from '../db/school.repo';

const router = Router();
const schoolRepo = new SchoolRepository();

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
}

router.get('/schools', (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const filters = {
      name: req.query.name as string,
      type: req.query.type as string,
      level: req.query.level as string,
      province: req.query.province as string
    };

    const schools = schoolRepo.getAllSchools(filters);

    res.json({
      success: true,
      data: schools
    });
  } catch (error) {
    console.error('获取学校列表失败:', error);
    res.status(500).json({
      success: false,
      message: '获取学校列表失败'
    });
  }
});

router.get('/schools/:id', (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const id = parseInt(req.params.id);
    const school = schoolRepo.getSchoolById(id);

    if (!school) {
      res.status(404).json({
        success: false,
        message: '学校不存在'
      });
      return;
    }

    res.json({
      success: true,
      data: school
    });
  } catch (error) {
    console.error('获取学校详情失败:', error);
    res.status(500).json({
      success: false,
      message: '获取学校详情失败'
    });
  }
});

router.get('/undergraduate/yearly', (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const schoolId = parseInt(req.query.school_id as string);
    const filters = {
      province: req.query.province as string,
      year: req.query.year ? parseInt(req.query.year as string) : undefined,
      category: req.query.category as string,
      batch: req.query.batch as string
    };

    const scores = schoolRepo.getUndergraduateYearlyScores(schoolId, filters);

    res.json({
      success: true,
      data: scores
    });
  } catch (error) {
    console.error('获取本科历年分数失败:', error);
    res.status(500).json({
      success: false,
      message: '获取本科历年分数失败'
    });
  }
});

router.get('/undergraduate/major', (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const schoolId = parseInt(req.query.school_id as string);
    const filters = {
      province: req.query.province as string,
      year: req.query.year ? parseInt(req.query.year as string) : undefined,
      category: req.query.category as string
    };

    const scores = schoolRepo.getUndergraduateMajorScores(schoolId, filters);

    res.json({
      success: true,
      data: scores
    });
  } catch (error) {
    console.error('获取专业分数失败:', error);
    res.status(500).json({
      success: false,
      message: '获取专业分数失败'
    });
  }
});

router.get('/postgraduate/info', (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const schoolId = parseInt(req.query.school_id as string);
    const year = parseInt(req.query.year as string);

    const info = schoolRepo.getPostgraduateInfo(schoolId, year);

    res.json({
      success: true,
      data: info
    });
  } catch (error) {
    console.error('获取研究生信息失败:', error);
    res.status(500).json({
      success: false,
      message: '获取研究生信息失败'
    });
  }
});

router.get('/postgraduate/reply-lines', (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const schoolId = parseInt(req.query.school_id as string);
    const year = parseInt(req.query.year as string);

    const lines = schoolRepo.getPostgraduateReplyLines(schoolId, year);

    res.json({
      success: true,
      data: lines
    });
  } catch (error) {
    console.error('获取研究生复试线失败:', error);
    res.status(500).json({
      success: false,
      message: '获取研究生复试线失败'
    });
  }
});

export default router;
