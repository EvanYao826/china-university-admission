export interface University {
  id: number;
  name: string;
  province: string;
  city: string;
  type: '综合' | '理工' | '师范' | '农林' | '医药' | '财经' | '政法' | '艺术' | '体育' | '民族' | '语言' | '其他';
  level: '985' | '211' | '双一流' | '普通本科' | '专科';
  website?: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface AdmissionRecord {
  id: number;
  university_id: number;
  year: number;
  province: string;
  category: '文科' | '理科' | '综合改革' | '艺术' | '体育';
  batch: '本科一批' | '本科二批' | '专科批' | '提前批';
  min_score: number;
  avg_score: number;
  max_score: number;
  min_rank: number;
  avg_rank: number;
  max_rank: number;
  admission_count: number;
  major?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface GraduateAdmission {
  id: number;
  university_id: number;
  year: number;
  major: string;
  degree_type: '硕士' | '博士';
  study_mode: '全日制' | '非全日制';
  admission_count: number;
  min_score?: number;
  avg_score?: number;
  max_score?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface SearchParams {
  province?: string;
  type?: string;
  level?: string;
  year?: number;
  category?: string;
  batch?: string;
  minScore?: number;
  maxScore?: number;
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  pagination?: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}