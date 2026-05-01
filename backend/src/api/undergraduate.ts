import { Router, Request, Response } from 'express';
import { AdmissionRepository } from '../db/admission.repo';
import { ApiResponse } from '../types';

const router = Router();
const admissionRepo = new AdmissionRepository();

// 获取高校的高考录取数据
router.get('/admissions', async (req: Request, res: Response<ApiResponse<any>>) => {
  try {
    const universityId = parseInt(req.query.university_id as string);
    const year = req.query.year ? parseInt(req.query.year as string) : undefined;
    const province = req.query.province as string;
    const category = req.query.category as string;
    const batch = req.query.batch as string;
    const page = req.query.page ? parseInt(req.query.page as string) : 1;
    const limit = req.query.limit ? parseInt(req.query.limit as string) : 50;

    if (isNaN(universityId)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid university ID'
      });
    }

    const params: any = { page, limit };
    if (year) params.year = year;
    if (province) params.province = province;
    if (category) params.category = category;
    if (batch) params.batch = batch;

    const { data, total } = admissionRepo.getGaokaoByUniversity(universityId, params);

    const totalPages = Math.ceil(total / limit);

    return res.json({
      success: true,
      data,
      pagination: {
        page,
        limit,
        total,
        totalPages
      }
    });
  } catch (error) {
    console.error('Error fetching undergraduate admissions:', error);
    return res.status(400).json({
      success: false,
      error: error instanceof Error ? error.message : 'Invalid request parameters'
    });
  }
});

export default router;