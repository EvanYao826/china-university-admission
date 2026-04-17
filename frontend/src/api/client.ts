import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiResponse } from '@/types';

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.DEV ? '' : 'http://localhost:3000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

apiClient.interceptors.request.use(
  (config) => {
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

apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const { data } = response;
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
      const { status, data } = error.response;
      switch (status) {
        case 400:
          errorMessage = data?.error || '请求参数错误';
          break;
        case 401:
          errorMessage = '未授权，请重新登录';
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
      errorMessage = '网络连接失败，请检查网络设置';
    } else {
      errorMessage = error.message || '请求配置错误';
    }
    console.error('Error:', errorMessage);
    return Promise.reject(new Error(errorMessage));
  }
);

export const api = {
  get: (url: string, params?: any) =>
    apiClient.get<ApiResponse>(url, { params }),

  universities: {
    getUniversities: (params?: any) =>
      apiClient.get<ApiResponse>('/api/universities', { params }),
    getUniversityById: (id: number) =>
      apiClient.get<ApiResponse>(`/api/universities/${id}`),
    searchUniversities: (name: string, limit = 10) =>
      apiClient.get<ApiResponse>(`/api/universities/search/${name}`, { params: { limit } }),
    getFilterOptions: () =>
      apiClient.get<ApiResponse>('/api/universities/options/filters'),
    getStatistics: () =>
      apiClient.get<ApiResponse>('/api/universities/statistics/summary'),
    getProvinceStatistics: (province: string) =>
      apiClient.get<ApiResponse>(`/api/universities/statistics/by-province/${province}`)
  },

  admissions: {
    getGaokaoAdmissions: (universityId: number, params?: any) =>
      apiClient.get<ApiResponse>(`/api/admissions/gaokao/${universityId}`, { params }),
    getGraduateAdmissions: (universityId: number, params?: any) =>
      apiClient.get<ApiResponse>(`/api/admissions/graduate/${universityId}`, { params }),
    matchByScore: (params: {
      province: string;
      year: number;
      category: string;
      batch: string;
      score: number;
      limit?: number;
    }) => apiClient.get<ApiResponse>('/api/admissions/score/match', { params }),
    getAdmissionStatistics: (universityId: number) =>
      apiClient.get<ApiResponse>(`/api/admissions/statistics/${universityId}`),
    getAdmissionTrends: (universityId: number, province?: string, category?: string) =>
      apiClient.get<ApiResponse>(`/api/admissions/trends/${universityId}`, { params: { province, category } }),
    getProvinceAdmissions: (province: string, year?: number, category?: string, batch?: string) =>
      apiClient.get<ApiResponse>(`/api/admissions/province/${province}`, { params: { year, category, batch } }),
    getYearOptions: () =>
      apiClient.get<ApiResponse>('/api/admissions/options/years'),
    getProvinceOptions: () =>
      apiClient.get<ApiResponse>('/api/admissions/options/provinces')
  },

  search: {
    advancedSearch: (params?: any) =>
      apiClient.get<ApiResponse>('/api/search/advanced', { params }),
    getSuggestions: (query: string) =>
      apiClient.get<ApiResponse>('/api/search/suggestions', { params: { q: query } }),
    getPopularSearches: () =>
      apiClient.get<ApiResponse>('/api/search/popular'),
    getSearchStatistics: () =>
      apiClient.get<ApiResponse>('/api/search/statistics')
  },

  system: {
    healthCheck: () => apiClient.get('/api/health'),
    getApiDocs: () => apiClient.get('/api')
  }
};

export default apiClient;
