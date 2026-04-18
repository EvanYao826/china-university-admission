<template>
  <div id="app">
    <!-- 顶部导航栏 -->
    <el-header class="app-header">
      <div class="header-content">
        <h1 class="header-title">中国高校录取信息</h1>
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
        </div>
      </div>
    </el-footer>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #e6f7ff 0%, #f0f8ff 100%);
}

.app-header {
  background: linear-gradient(135deg, #4096ff 0%, #667eea 100%);
  color: white;
  height: 50px;
  padding: 0;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.header-title {
  font-size: 20px;
  font-weight: bold;
  letter-spacing: 1px;
  margin: 0;
}

.app-main {
  flex: 1;
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.app-footer {
  background: white;
  border-top: 1px solid #e9ecef;
  padding: 20px;
  margin-top: 20px;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
}

.footer-info {
  text-align: center;
}

.footer-info p {
  margin: 5px 0;
  color: #6c757d;
  font-size: 14px;
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
@media (max-width: 768px) {
  .app-main {
    padding: 10px;
  }

  .header-title {
    font-size: 16px;
  }
}
</style>
