<template>
  <div class="home-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>中国高校录取数据查询系统</h1>
      <p>一站式查询高考、研究生录取数据</p>
    </div>
    
    <!-- 功能卡片 -->
    <div class="features">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="feature-card" @click="navigateTo('/universities')">
            <template #header>
              <div class="card-header">
                <el-icon><OfficeBuilding /></el-icon>
                <span>高校查询</span>
              </div>
            </template>
            <div class="feature-content">
              <p>按省份、类型、层次筛选高校</p>
              <el-button type="primary" size="small">立即查询</el-button>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="feature-card" @click="navigateTo('/admissions')">
            <template #header>
              <div class="card-header">
                <el-icon><DataAnalysis /></el-icon>
                <span>录取数据</span>
              </div>
            </template>
            <div class="feature-content">
              <p>历年高考、研究生录取分数线</p>
              <el-button type="primary" size="small">查看数据</el-button>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="feature-card" @click="navigateTo('/score-match')">
            <template #header>
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>分数匹配</span>
              </div>
            </template>
            <div class="feature-content">
              <p>根据分数推荐合适的高校</p>
              <el-button type="primary" size="small">开始匹配</el-button>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="feature-card" @click="navigateTo('/compare')">
            <template #header>
              <div class="card-header">
                <el-icon><PieChart /></el-icon>
                <span>高校对比</span>
              </div>
            </template>
            <div class="feature-content">
              <p>多所高校的横向对比分析</p>
              <el-button type="primary" size="small">开始对比</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 数据统计 -->
    <div class="stats-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <el-icon><PieChart /></el-icon>
            <span>数据统计</span>
          </div>
        </template>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ universityCount }}</div>
            <div class="stat-label">高校数量</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ gaokaoCount }}</div>
            <div class="stat-label">高考数据</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ graduateCount }}</div>
            <div class="stat-label">研究生数据</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ years.length }}</div>
            <div class="stat-label">覆盖年份</div>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 最新数据 -->
    <div class="recent-data">
      <el-card>
        <template #header>
          <div class="card-header">
            <el-icon><Timer /></el-icon>
            <span>最新数据</span>
            <el-button type="text" @click="navigateTo('/statistics')">查看更多</el-button>
          </div>
        </template>
        <el-table :data="recentData" style="width: 100%">
          <el-table-column prop="universityName" label="高校名称" width="180" />
          <el-table-column prop="province" label="省份" width="100" />
          <el-table-column prop="year" label="年份" width="80" />
          <el-table-column prop="category" label="科类" width="100" />
          <el-table-column prop="avgScore" label="平均分" width="100" />
          <el-table-column prop="admissionCount" label="招生人数" width="100" />
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  OfficeBuilding,
  DataAnalysis,
  TrendCharts,
  PieChart,
  Timer
} from '@element-plus/icons-vue'

const router = useRouter()
const searchQuery = ref('')

// 统计数据
const universityCount = ref(5)
const gaokaoCount = ref(120)
const graduateCount = ref(240)
const years = ref([2021, 2022, 2023])

// 最新数据
const recentData = ref([
  {
    universityName: '清华大学',
    province: '山东',
    year: 2023,
    category: '理科',
    avgScore: 675,
    admissionCount: 95
  },
  {
    universityName: '北京大学',
    province: '山西',
    year: 2023,
    category: '文科',
    avgScore: 660,
    admissionCount: 85
  },
  {
    universityName: '浙江大学',
    province: '河南',
    year: 2023,
    category: '理科',
    avgScore: 665,
    admissionCount: 90
  },
  {
    universityName: '复旦大学',
    province: '河北',
    year: 2023,
    category: '文科',
    avgScore: 655,
    admissionCount: 80
  }
])

// 导航到指定页面
const navigateTo = (path: string) => {
  router.push(path)
}

// 处理搜索
const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push(`/search?q=${encodeURIComponent(searchQuery.value)}`)
  }
}

// 组件挂载
onMounted(() => {
  console.log('HomePage mounted')
})
</script>

<style scoped>
.home-page {
  padding: 40px 0;
  background-color: #f5f7fa;
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 40px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  margin: 0 20px 40px;
}

.page-header h1 {
  margin: 0 0 10px 0;
  font-size: 36px;
  font-weight: bold;
}

.page-header p {
  margin: 0;
  font-size: 18px;
  opacity: 0.9;
}

/* 功能卡片 */
.features {
  margin: 0 20px 40px;
}

.feature-card {
  height: 200px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.feature-content {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: calc(100% - 48px);
  padding-top: 20px;
}

.feature-content p {
  margin: 0 0 20px 0;
  color: #606266;
}

/* 数据统计 */
.stats-section {
  margin: 0 20px 40px;
}

.stats-grid {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 20px;
  padding: 20px 0;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  min-width: 120px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #667eea;
}

/* 最新数据 */
.recent-data {
  margin: 0 20px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .page-header {
    margin: 0 10px 30px;
    padding: 30px 0;
  }
  
  .page-header h1 {
    font-size: 30px;
  }
  
  .features,
  .stats-section,
  .recent-data {
    margin-left: 10px;
    margin-right: 10px;
  }
}

@media (max-width: 768px) {
  .home-page {
    padding: 20px 0;
  }
  
  .page-header {
    padding: 20px 0;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .page-header p {
    font-size: 16px;
  }
  
  .feature-card {
    height: 180px;
  }
  
  .stats-grid {
    flex-direction: column;
    align-items: center;
  }
  
  .stat-item {
    width: 100%;
    max-width: 200px;
  }
}
</style>
