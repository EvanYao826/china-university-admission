import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiResponse } from '@/types';

// 创建 axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.DEV ? '/api' : 'http://localhost:3000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证 token
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }

    // 添加请求时间戳防止缓存
    if (config.method?.toLowerCase() === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now()
      };
    }

    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const { data } = response;

    // 检查 API 响应是否成功
    if (!data.success) {
      console.error('API error:', data.error);
      return Promise.reject(new Error(data.error || '请求失败'));
    }

    return response;
  },
  (error) => {
    console.error('Response error:', error);

    let errorMessage = '网络错误，请稍后重试';

    if (error.response) {
      // 服务器返回了错误状态码
      const { status, data } = error.response;

      switch (status) {
        case 400:
          errorMessage = data?.error || '请求参数错误';
          break;
        case 401:
          errorMessage = '未授权，请重新登录';
          // 可以在这里跳转到登录页
          break;
        case 403:
          errorMessage = '拒绝访问';
          break;
        case 404:
          errorMessage = '请求的资源不存在';
          break;
        case 500:
          errorMessage = '服务器内部错误';
          break;
        case 502:
        case 503:
        case 504:
          errorMessage = '服务暂时不可用，请稍后重试';
          break;
        default:
          errorMessage = data?.error || `请求失败 (${status})`;
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      errorMessage = '网络连接失败，请检查网络设置';
    } else {
      // 请求配置出错
      errorMessage = error.message || '请求配置错误';
    }

    // 显示错误提示（实际项目中可以使用 UI 组件）
    console.error('Error:', errorMessage);

    return Promise.reject(new Error(errorMessage));
  }
);

// API 函数封装
export const api = {
  // 高校相关接口
  universities: {
    // 获取高校列表
    getUniversities: (params?: any) =>
      apiClient.get<ApiResponse>('/universities', { params }),

    // 获取高校详情
    getUniversityById: (id: number) =>
      apiClient.get<ApiResponse>(`/universities/${id}`),

    // 搜索高校
    searchUniversities: (name: string, limit = 10) =>
      apiClient.get<ApiResponse>(`/universities/search/${name}`, { params: { limit } }),

    // 获取筛选选项
    getFilterOptions: () =>
      apiClient.get<ApiResponse>('/universities/options/filters'),

    // 获取统计信息
    getStatistics: () =>
      apiClient.get<ApiResponse>('/universities/statistics/summary'),

    // 获取省份统计
    getProvinceStatistics: (province: string) =>
      apiClient.get<ApiResponse>(`/universities/statistics/by-province/${province}`)
  },

  // 录取数据相关接口
  admissions: {
    // 获取高考录取数据
    getGaokaoAdmissions: (universityId: number, params?: any) =>
      apiClient.get<ApiResponse>(`/admissions/gaokao/${universityId}`, { params }),

    // 获取研究生录取数据
    getGraduateAdmissions: (universityId: number, params?: any) =>
      apiClient.get<ApiResponse>(`/admissions/graduate/${universityId}`, { params }),

    // 根据分数匹配高校
    matchByScore: (params: {
      province: string;
      year: number;
      category: string;
      batch: string;
      score: number;
      limit?: number;
    }) => apiClient.get<ApiResponse>('/admissions/score/match', { params }),

    // 获取录取统计
    getAdmissionStatistics: (universityId: number) =>
      apiClient.get<ApiResponse>(`/admissions/statistics/${universityId}`),

    // 获取录取趋势
    getAdmissionTrends: (universityId: number, province?: string, category?: string) =>
      apiClient.get<ApiResponse>(`/admissions/trends/${universityId}`, {
        params: { province, category }
      }),

    // 获取省份录取数据
    getProvinceAdmissions: (province: string, year?: number, category?: string, batch?: string) =>
      apiClient.get<ApiResponse>(`/admissions/province/${province}`, {
        params: { year, category, batch }
      }),

    // 获取年份选项
    getYearOptions: () =>
      apiClient.get<ApiResponse>('/admissions/options/years'),

    // 获取省份选项
    getProvinceOptions: () =>
      apiClient.get<ApiResponse>('/admissions/options/provinces')
  },

  // 搜索相关接口
  search: {
    // 高级搜索
    advancedSearch: (params?: any) =>
      apiClient.get<ApiResponse>('/search/advanced', { params }),

    // 搜索建议
    getSuggestions: (query: string) =>
      apiClient.get<ApiResponse>('/search/suggestions', { params: { q: query } }),

    // 热门搜索
    getPopularSearches: () =>
      apiClient.get<ApiResponse>('/search/popular'),

    // 搜索统计
    getSearchStatistics: () =>
      apiClient.get<ApiResponse>('/search/statistics')
  },

  // 系统相关接口
  system: {
    // 健康检查
    healthCheck: () =>
      apiClient.get('/health'),

    // API 文档
    getApiDocs: () =>
      apiClient.get('/api')
  }
};

// 导出 axios 实例供其他用途
export default apiClient;