<template>
  <div class="not-found">
    <div class="error-container">
      <div class="error-code">404</div>
      <h1>页面未找到</h1>
      <p>抱歉，您访问的页面不存在或已被移除</p>
      <div class="error-actions">
        <el-button type="primary" @click="goHome">返回首页</el-button>
        <el-button @click="goBack">返回上一页</el-button>
      </div>
      <div class="error-suggestions">
        <h3>您可以尝试：</h3>
        <ul>
          <li>检查URL是否正确</li>
          <li>返回首页重新导航</li>
          <li>使用搜索功能查找内容</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

// 返回首页
const goHome = () => {
  router.push('/')
}

// 返回上一页
const goBack = () => {
  router.back()
}
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
}

.error-container {
  text-align: center;
  padding: 60px 40px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  width: 100%;
}

.error-code {
  font-size: 80px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 20px;
  line-height: 1;
}

.error-container h1 {
  font-size: 24px;
  margin: 0 0 16px 0;
  color: #303133;
}

.error-container p {
  font-size: 16px;
  color: #606266;
  margin: 0 0 30px 0;
  line-height: 1.5;
}

.error-actions {
  margin-bottom: 30px;
  display: flex;
  justify-content: center;
  gap: 10px;
}

.error-suggestions {
  text-align: left;
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

.error-suggestions h3 {
  font-size: 14px;
  margin: 0 0 10px 0;
  color: #303133;
}

.error-suggestions ul {
  margin: 0;
  padding-left: 20px;
}

.error-suggestions li {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .error-container {
    padding: 40px 20px;
    margin: 0 20px;
  }
  
  .error-code {
    font-size: 60px;
  }
  
  .error-container h1 {
    font-size: 20px;
  }
  
  .error-container p {
    font-size: 14px;
  }
}
</style>
