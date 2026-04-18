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

// 获取省份可用的类别列表
router.get('/schools/categories', (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const province = req.query.province as string;
    if (!province) {
      res.status(400).json({
        success: false,
        message: '省份参数不能为空'
      });
      return;
    }

    const categories = schoolRepo.getCategoriesByProvince(province);
    res.json({
      success: true,
      data: categories
    });
  } catch (error) {
    console.error('获取省份可用类别失败:', error);
    res.status(500).json({
      success: false,
      message: '获取省份可用类别失败'
    });
  }
});

// 获取省份和类别可用的批次列表
router.get('/schools/batches', (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const province = req.query.province as string;
    const category = req.query.category as string;
    const universityId = req.query.university_id ? parseInt(req.query.university_id as string) : undefined;

    if (!province || !category) {
      res.status(400).json({
        success: false,
        message: '省份和类别参数不能为空'
      });
      return;
    }

    const batches = schoolRepo.getBatchesByProvinceAndCategory(province, category, universityId);
    res.json({
      success: true,
      data: batches
    });
  } catch (error) {
    console.error('获取省份可用批次失败:', error);
    res.status(500).json({
      success: false,
      message: '获取省份可用批次失败'
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
