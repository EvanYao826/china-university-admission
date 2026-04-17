<template>
  <div id="app">
    <!-- 顶部导航栏 -->
    <el-header class="app-header">
      <div class="header-content">
        <div class="logo" @click="goHome">
          <el-icon size="24"><School /></el-icon>
          <span class="logo-text">中国高校录取数据查询系统</span>
        </div>

        <div class="nav-menu">
          <el-menu
            :default-active="activeMenu"
            mode="horizontal"
            @select="handleMenuSelect"
            class="nav-menu-inner"
          >
            <el-menu-item index="/">
              <template #title>
                <el-icon><House /></el-icon>
                <span>首页</span>
              </template>
            </el-menu-item>
          </el-menu>
        </div>

        <div class="header-actions">
          <el-input
            v-model="searchQuery"
            placeholder="搜索高校、专业..."
            class="search-input"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <el-button
            type="primary"
            @click="handleSearch"
            :icon="Search"
            class="search-btn"
          >
            搜索
          </el-button>
        </div>
      </div>
    </el-header>

    <!-- 主要内容区域 -->
    <el-main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>

    <!-- 底部信息 -->
    <el-footer class="app-footer">
      <div class="footer-content">
        <div class="footer-info">
          <p>© 2024 中国高校录取数据查询系统</p>
          <p>数据仅供参考，请以官方发布为准</p>
          <p class="footer-links">
            <a href="javascript:void(0)" @click="showAbout">关于我们</a>
            <span class="divider">|</span>
            <a href="javascript:void(0)" @click="showHelp">使用帮助</a>
            <span class="divider">|</span>
            <a href="javascript:void(0)" @click="showDisclaimer">免责声明</a>
          </p>
        </div>

        <div class="footer-stats" v-if="stats">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.totalUniversities || 0 }}</div>
                <div class="stat-label">高校数量</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.totalGaokaoRecords || 0 }}</div>
                <div class="stat-label">高考记录</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.totalGraduateRecords || 0 }}</div>
                <div class="stat-label">研究生记录</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.latestYear || '--' }}</div>
                <div class="stat-label">最新数据年份</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-footer>

    <!-- 关于对话框 -->
    <el-dialog
      v-model="aboutDialogVisible"
      title="关于我们"
      width="500px"
    >
      <div class="about-content">
        <h3>中国高校录取数据查询系统</h3>
        <p>本系统提供中国高校录取数据的查询和分析功能，包括高考录取数据和研究生录取数据。</p>

        <h4>主要功能：</h4>
        <ul>
          <li>高校信息查询与筛选</li>
          <li>历年录取数据查看</li>
          <li>录取趋势分析</li>
          <li>分数匹配推荐</li>
          <li>数据统计与可视化</li>
        </ul>

        <h4>数据说明：</h4>
        <p>数据来源于公开渠道，经过整理和标准化处理。数据仅供参考，请以各高校官方发布为准。</p>

        <h4>技术栈：</h4>
        <p>Vue 3 + TypeScript + Element Plus + ECharts + Node.js + Express + SQLite</p>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="aboutDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/api/client'
import {
  School,
  House,
  Search
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// 搜索查询
const searchQuery = ref('')

// 统计数据
const stats = ref<any>(null)

// 对话框控制
const aboutDialogVisible = ref(false)

// 当前激活的菜单
const activeMenu = computed(() => route.path)

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

// 处理菜单选择
const handleMenuSelect = (index: string) => {
  router.push(index)
}

// 处理搜索
const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({
      path: '/search',
      query: { q: searchQuery.value.trim() }
    })
    searchQuery.value = ''
  }
}

// 返回首页
const goHome = () => {
  router.push('/')
}

// 显示关于对话框
const showAbout = () => {
  aboutDialogVisible.value = true
}

// 显示帮助（暂未实现）
const showHelp = () => {
  ElMessage.info('帮助文档正在建设中...')
}

// 显示免责声明（暂未实现）
const showDisclaimer = () => {
  ElMessage.info('免责声明正在建设中...')
}

// 组件挂载时获取统计数据
onMounted(() => {
  fetchStatistics()
})
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  height: 60px;
  padding: 0;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: opacity 0.3s;
}

.logo:hover {
  opacity: 0.9;
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  letter-spacing: 0.5px;
}

.nav-menu {
  flex: 1;
  display: flex;
  justify-content: center;
}

.nav-menu-inner {
  background: transparent;
  border: none;
}

.nav-menu-inner :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.9) !important;
  font-weight: 500;
}

.nav-menu-inner :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.1) !important;
  color: white !important;
}

.nav-menu-inner :deep(.el-menu-item.is-active) {
  background: rgba(255, 255, 255, 0.2) !important;
  color: white !important;
  border-bottom: 2px solid white;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-input {
  width: 300px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 20px;
}

.search-btn {
  border-radius: 20px;
}

.app-main {
  flex: 1;
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.app-footer {
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
  padding: 30px 20px;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
}

.footer-info {
  text-align: center;
  margin-bottom: 30px;
}

.footer-info p {
  margin: 5px 0;
  color: #6c757d;
  font-size: 14px;
}

.footer-links {
  margin-top: 15px;
}

.footer-links a {
  color: #667eea;
  text-decoration: none;
  transition: color 0.3s;
}

.footer-links a:hover {
  color: #764ba2;
  text-decoration: underline;
}

.divider {
  margin: 0 10px;
  color: #dee2e6;
}

.footer-stats {
  margin-top: 20px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #6c757d;
}

.about-content {
  line-height: 1.6;
}

.about-content h3 {
  color: #667eea;
  margin-bottom: 15px;
}

.about-content h4 {
  color: #495057;
  margin: 20px 0 10px;
}

.about-content ul {
  padding-left: 20px;
  margin: 10px 0;
}

.about-content li {
  margin-bottom: 5px;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .header-content {
    flex-wrap: wrap;
    height: auto;
    padding: 10px;
  }

  .nav-menu {
    order: 3;
    width: 100%;
    margin-top: 10px;
  }

  .search-input {
    width: 200px;
  }
}

@media (max-width: 768px) {
  .logo-text {
    font-size: 16px;
  }

  .header-actions {
    flex-direction: column;
    gap: 10px;
  }

  .search-input {
    width: 100%;
  }

  .footer-stats .el-col {
    margin-bottom: 15px;
  }
}
</style>