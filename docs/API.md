# API 文档

## 概述

中国高校录取数据查询系统提供 RESTful API 接口，支持高校信息查询、录取数据获取、搜索等功能。

## 基础信息

- **基础URL**: `http://localhost:3000/api`
- **响应格式**: JSON
- **认证**: 当前版本无需认证
- **分页**: 所有列表接口支持分页

## 响应格式

### 成功响应
```json
{
  "success": true,
  "data": {...},
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

### 错误响应
```json
{
  "success": false,
  "error": "错误描述"
}
```

## 高校相关接口

### 获取高校列表
```
GET /universities
```

**查询参数**:
- `province` (可选): 省份筛选
- `type` (可选): 高校类型
- `level` (可选): 高校层次
- `page` (可选, 默认1): 页码
- `limit` (可选, 默认20): 每页数量
- `sortBy` (可选): 排序字段 (name/province/type/level)
- `sortOrder` (可选): 排序方向 (asc/desc)

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "清华大学",
      "province": "北京",
      "city": "北京",
      "type": "综合",
      "level": "985",
      "website": "https://www.tsinghua.edu.cn",
      "description": "中国著名高等学府",
      "created_at": "2024-01-01T00:00:00.000Z",
      "updated_at": "2024-01-01T00:00:00.000Z"
    }
  ],
  "pagination": {...}
}
```

### 获取高校详情
```
GET /universities/{id}
```

### 搜索高校
```
GET /universities/search/{name}
```

### 获取筛选选项
```
GET /universities/options/filters
```

## 录取数据接口

### 获取高考录取数据
```
GET /admissions/gaokao/{universityId}
```

**查询参数**:
- `year` (可选): 年份
- `province` (可选): 省份
- `category` (可选): 科类 (文科/理科/综合改革/艺术/体育)
- `batch` (可选): 批次 (本科一批/本科二批/专科批/提前批)

### 获取研究生录取数据
```
GET /admissions/graduate/{universityId}
```

### 分数匹配
```
GET /admissions/score/match
```

**查询参数**:
- `province` (必需): 省份
- `year` (必需): 年份
- `category` (必需): 科类
- `batch` (必需): 批次
- `score` (必需): 分数
- `limit` (可选, 默认20): 返回数量

## 搜索接口

### 高级搜索
```
GET /search/advanced
```

### 搜索建议
```
GET /search/suggestions
```

## 系统接口

### 健康检查
```
GET /health
```

### API 文档
```
GET /api
```

## 错误码

| 状态码 | 描述 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 使用示例

### JavaScript (Fetch)
```javascript
// 获取高校列表
fetch('http://localhost:3000/api/universities?province=北京&limit=10')
  .then(response => response.json())
  .then(data => console.log(data));

// 获取录取数据
fetch('http://localhost:3000/api/admissions/gaokao/1?year=2023')
  .then(response => response.json())
  .then(data => console.log(data));
```

### Python (requests)
```python
import requests

# 获取高校列表
response = requests.get('http://localhost:3000/api/universities', params={
    'province': '北京',
    'limit': 10
})
data = response.json()
```

## 注意事项

1. 所有时间字段使用 ISO 8601 格式
2. 分页参数 page 从 1 开始
3. 字符串参数使用 UTF-8 编码
4. 建议设置合理的请求频率