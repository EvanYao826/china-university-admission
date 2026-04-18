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

router.get('/undergraduate/admissions', (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const universityId = parseInt(req.query.university_id as string);
    const filters = {
      province: req.query.province as string,
      year: req.query.year ? parseInt(req.query.year as string) : undefined,
      category: req.query.category as string,
      batch: req.query.batch as string
    };

    const admissions = schoolRepo.getUndergraduateAdmissions(universityId, filters);

    res.json({
      success: true,
      data: admissions
    });
  } catch (error) {
    console.error('获取本科录取数据失败:', error);
    res.status(500).json({
      success: false,
      message: '获取本科录取数据失败'
    });
  }
});

router.get('/postgraduate/admissions', (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const universityId = parseInt(req.query.university_id as string);
    const filters = {
      year: req.query.year ? parseInt(req.query.year as string) : undefined,
      degree_type: req.query.degree_type as string,
      admission_type: req.query.admission_type as string
    };

    const admissions = schoolRepo.getPostgraduateAdmissions(universityId, filters);

    res.json({
      success: true,
      data: admissions
    });
  } catch (error) {
    console.error('获取研究生录取数据失败:', error);
    res.status(500).json({
      success: false,
      message: '获取研究生录取数据失败'
    });
  }
});

export default router;
