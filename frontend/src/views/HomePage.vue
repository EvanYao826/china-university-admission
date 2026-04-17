<template>
  <div class="home-page">
    <!-- 英雄区域 -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">中国高校录取数据查询系统</h1>
        <p class="hero-subtitle">一站式查询高考、研究生录取数据，助力升学决策</p>

        <!-- 快速搜索 -->
        <div class="quick-search">
          <el-input
            v-model="quickSearchQuery"
            placeholder="输入高校名称、专业或省份..."
            size="large"
            @keyup.enter="handleQuickSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
            <template #append>
              <el-button
                type="primary"
                @click="handleQuickSearch"
                :icon="Search"
              >
                搜索
              </el-button>
            </template>
          </el-input>

          <!-- 热门搜索标签 -->
          <div class="popular-tags">
            <span class="tags-label">热门搜索：</span>
            <el-tag
              v-for="tag in popularTags"
              :key="tag.term"
              class="tag-item"
              @click="handleTagClick(tag)"
            >
              {{ tag.term }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 功能卡片区域 -->
    <div class="features-section">
      <h2 class="section-title">核心功能</h2>
      <div class="features-grid">
        <el-card
          v-for="feature in features"
          :key="feature.title"
          class="feature-card"
          shadow="hover"
          @click="navigateTo(feature.route)"
        >
          <div class="feature-icon">
            <component :is="feature.icon" />
          </div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-desc">{{ feature.description }}</p>
          <el-button type="primary" link class="feature-link">
            立即使用 →
          </el-button>
        </el-card>
      </div>
    </div>

    <!-- 数据统计区域 -->
    <div class="stats-section" v-if="stats">
      <h2 class="section-title">数据概览</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">
            <el-icon><School /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalUniversities || 0 }}</div>
            <div class="stat-label">高校数量</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalGaokaoRecords || 0 }}</div>
            <div class="stat-label">高考录取记录</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <el-icon><Reading /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalGraduateRecords || 0 }}</div>
            <div class="stat-label">研究生录取记录</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <el-icon><Calendar /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.latestYear || '--' }}</div>
            <div class="stat-label">最新数据年份</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 热门高校区域 -->
    <div class="popular-section" v-if="popularUniversities.length > 0">
      <h2 class="section-title">热门高校</h2>
      <div class="universities-grid">
        <el-card
          v-for="uni in popularUniversities"
          :key="uni.id"
          class="university-card"
          shadow="hover"
          @click="viewUniversityDetail(uni.id)"
        >
          <div class="university-header">
            <h3 class="university-name">{{ uni.name }}</h3>
            <el-tag
              :type="getLevelTagType(uni.level)"
              size="small"
              class="level-tag"
            >
              {{ uni.level }}
            </el-tag>
          </div>
          <div class="university-info">
            <div class="info-item">
              <el-icon><Location /></el-icon>
              <span>{{ uni.province }} {{ uni.city }}</span>
            </div>
            <div class="info-item">
              <el-icon><OfficeBuilding /></el-icon>
              <span>{{ uni.type }}</span>
            </div>
          </div>
          <div class="university-actions">
            <el-button type="primary" size="small" @click.stop="viewUniversityDetail(uni.id)">
              查看详情
            </el-button>
            <el-button type="info" size="small" @click.stop="addToCompare(uni)">
              加入对比
            </el-button>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 使用指南区域 -->
    <div class="guide-section">
      <h2 class="section-title">使用指南</h2>
      <div class="guide-steps">
        <div class="step-item" v-for="step in guideSteps" :key="step.title">
          <div class="step-number">{{ step.number }}</div>
          <div class="step-content">
            <h3>{{ step.title }}</h3>
            <p>{{ step.description }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/client'
import {
  Search,
  School,
  Document,
  Reading,
  Calendar,
  Location,
  OfficeBuilding,
  DataAnalysis,
  TrendCharts,
  PieChart,
  List
} from '@element-plus/icons-vue'
import type { University } from '@/types'

const router = useRouter()

// 搜索查询
const quickSearchQuery = ref('')

// 统计数据
const stats = ref<any>(null)

// 热门高校
const popularUniversities = ref<University[]>([])

// 热门搜索标签
const popularTags = ref([
  { term: '清华大学', type: 'university' },
  { term: '北京大学', type: 'university' },
  { term: '计算机科学', type: 'major' },
  { term: '北京', type: 'province' },
  { term: '985高校', type: 'level' },
  { term: '2024年录取', type: 'year' }
])

// 功能卡片
const features = ref([
  {
    title: '高校查询',
    description: '按省份、类型、层次筛选高校，查看详细信息',
    icon: School,
    route: '/universities'
  },
  {
    title: '录取数据',
    description: '查看历年高考、研究生录取分数线和招生人数',
    icon: DataAnalysis,
    route: '/admissions'
  },
  {
    title: '分数匹配',
    description: '根据分数推荐合适的高校和专业',
    icon: TrendCharts,
    route: '/score-match'
  },
  {
    title: '数据统计',
    description: '高校分布、录取趋势等可视化分析',
    icon: PieChart,
    route: '/statistics'
  }
])

// 使用指南步骤
const guideSteps = ref([
  {
    number: '01',
    title: '选择查询方式',
    description: '根据需求选择高校查询、录取数据查询或分数匹配'
  },
  {
    number: '02',
    title: '设置筛选条件',
    description: '按省份、年份、批次等条件筛选数据'
  },
  {
    number: '03',
    title: '查看结果',
    description: '浏览查询结果，查看详细数据和图表分析'
  },
  {
    number: '04',
    title: '对比分析',
    description: '将感兴趣的高校加入对比，进行多维度比较'
  }
])

// 获取统计数据
const fetchStatistics = async () => {
  try {
    const response = await api.search.getSearchStatistics()
    if (response.data.success) {
      stats.value = response.data.data
    }
  } catch (error) {
    console.error('Failed to fetch statistics:', error)
  }
}

// 获取热门高校
const fetchPopularUniversities = async () => {
  try {
    const response = await api.universities.getUniversities({
      limit: 8,
      sortBy: 'name',
      sortOrder: 'asc'
    })
    if (response.data.success) {
      popularUniversities.value = response.data.data
    }
  } catch (error) {
    console.error('Failed to fetch popular universities:', error)
  }
}

// 处理快速搜索
const handleQuickSearch = () => {
  if (quickSearchQuery.value.trim()) {
    router.push({
      path: '/search',
      query: { q: quickSearchQuery.value.trim() }
    })
    quickSearchQuery.value = ''
  }
}

// 处理标签点击
const handleTagClick = (tag: any) => {
  router.push({
    path: '/search',
    query: { q: tag.term }
  })
}

// 导航到指定路由
const navigateTo = (route: string) => {
  router.push(route)
}

// 查看高校详情
const viewUniversityDetail = (id: number) => {
  router.push(`/universities/${id}`)
}

// 添加到对比
const addToCompare = (university: University) => {
  // 这里可以添加到对比列表
  ElMessage.success(`已添加 ${university.name} 到对比列表`)
}

// 获取层次标签类型
const getLevelTagType = (level: string) => {
  switch (level) {
    case '985':
      return 'danger'
    case '211':
      return 'warning'
    case '双一流':
      return 'success'
    default:
      return 'info'
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchStatistics()
  fetchPopularUniversities()
})
</script>

<style scoped>
.home-page {
  padding-bottom: 40px;
}

/* 英雄区域 */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 20px;
  border-radius: 12px;
  margin-bottom: 40px;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 20px;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  margin-bottom: 40px;
}

.quick-search {
  max-width: 600px;
  margin: 0 auto;
}

.quick-search :deep(.el-input-group__append) {
  background-color: #4c51bf;
  border: none;
}

.quick-search :deep(.el-input-group__append .el-button) {
  background-color: #4c51bf;
  border: none;
}

.popular-tags {
  margin-top: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 10px;
}

.tags-label {
  font-size: 14px;
  opacity: 0.8;
}

.tag-item {
  cursor: pointer;
  transition: transform 0.3s;
}

.tag-item:hover {
  transform: translateY(-2px);
}

/* 功能卡片区域 */
.section-title {
  font-size: 1.8rem;
  font-weight: bold;
  text-align: center;
  margin-bottom: 40px;
  color: #2d3748;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 60px;
}

.feature-card {
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  height: 100%;
  border: none;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1) !important;
}

.feature-icon {
  font-size: 48px;
  color: #667eea;
  margin-bottom: 20px;
  text-align: center;
}

.feature-title {
  font-size: 1.3rem;
  font-weight: bold;
  margin-bottom: 12px;
  color: #2d3748;
}

.feature-desc {
  color: #718096;
  line-height: 1.6;
  margin-bottom: 20px;
}

.feature-link {
  color: #667eea;
  font-weight: 500;
}

/* 数据统计区域 */
.stats-section {
  margin-bottom: 60px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 40px;
  color: #667eea;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #2d3748;
  margin-bottom: 5px;
}

.stat-label {
  color: #718096;
  font-size: 14px;
}

/* 热门高校区域 */
.popular-section {
  margin-bottom: 60px;
}

.universities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.university-card {
  cursor: pointer;
  transition: transform 0.3s;
  border: none;
}

.university-card:hover {
  transform: translateY(-3px);
}

.university-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.university-name {
  font-size: 1.1rem;
  font-weight: bold;
  color: #2d3748;
  margin: 0;
  flex: 1;
}

.level-tag {
  margin-left: 10px;
}

.university-info {
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: #718096;
  font-size: 14px;
}

.info-item .el-icon {
  color: #a0aec0;
}

.university-actions {
  display: flex;
  gap: 10px;
}

/* 使用指南区域 */
.guide-section {
  background: #f7fafc;
  border-radius: 12px;
  padding: 40px;
}

.guide-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.step-item {
  display: flex;
  gap: 20px;
}

.step-number {
  font-size: 2rem;
  font-weight: bold;
  color: #667eea;
  min-width: 60px;
}

.step-content h3 {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 10px;
  color: #2d3748;
}

.step-content p {
  color: #718096;
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .features-grid,
  .stats-grid,
  .universities-grid {
    grid-template-columns: 1fr;
  }

  .guide-steps {
    grid-template-columns: 1fr;
  }

  .step-item {
    flex-direction: column;
    text-align: center;
  }

  .step-number {
    margin-bottom: 10px;
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 40px 20px;
  }

  .hero-title {
    font-size: 1.5rem;
  }

  .section-title {
    font-size: 1.5rem;
  }

  .stat-card {
    flex-direction: column;
    text-align: center;
    padding: 20px;
  }

  .stat-icon {
    margin-bottom: 15px;
  }
}
</style>