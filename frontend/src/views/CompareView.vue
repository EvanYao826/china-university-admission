<template>
  <div class="compare-view">
    <el-container>
      <el-header>
        <h1>高校对比</h1>
        <p>对比不同高校的录取数据和综合实力</p>
      </el-header>
      
      <el-main>
        <el-card class="compare-card">
          <template #header>
            <div class="card-header">
              <span>高校选择</span>
              <el-button type="primary" @click="addUniversity">添加高校</el-button>
            </div>
          </template>
          
          <div class="university-list">
            <el-tag
              v-for="(university, index) in universities"
              :key="university.id"
              closable
              @close="removeUniversity(index)"
              class="university-tag"
            >
              {{ university.name }}
            </el-tag>
            <el-tag v-if="universities.length === 0" class="empty-tag">
              请添加高校进行对比
            </el-tag>
          </div>
        </el-card>
        
        <el-card class="results-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>对比结果</span>
              <el-button type="primary" size="small" @click="exportComparison">导出对比</el-button>
            </div>
          </template>
          
          <div v-if="universities.length > 0" class="comparison-content">
            <el-table :data="comparisonData" style="width: 100%">
              <el-table-column prop="indicator" label="指标" width="150" />
              <el-table-column
                v-for="university in universities"
                :key="university.id"
                :label="university.name"
                :width="180"
              >
                <template #default="scope">
                  {{ scope.row[university.id] }}
                </template>
              </el-table-column>
            </el-table>
            
            <div class="chart-container" style="margin-top: 30px;">
              <h3>录取分数对比</h3>
              <div ref="scoreChart" style="height: 400px;"></div>
            </div>
            
            <div class="chart-container" style="margin-top: 30px;">
              <h3>招生人数对比</h3>
              <div ref="countChart" style="height: 400px;"></div>
            </div>
          </div>
          
          <div v-else class="empty-comparison">
            <el-empty description="请添加至少两所高校进行对比" />
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

// 高校列表
const universities = ref([
  { id: 1, name: '清华大学' },
  { id: 2, name: '北京大学' },
  { id: 3, name: '浙江大学' }
])

// 对比数据
const comparisonData = ref([
  { indicator: '985工程', '1': '是', '2': '是', '3': '是' },
  { indicator: '211工程', '1': '是', '2': '是', '3': '是' },
  { indicator: '双一流', '1': '是', '2': '是', '3': '是' },
  { indicator: '2023年理科最低分', '1': '680', '2': '675', '3': '660' },
  { indicator: '2023年文科最低分', '1': '670', '2': '675', '3': '655' },
  { indicator: '2023年招生人数', '1': '3500', '2': '3000', '3': '5000' },
  { indicator: '全国排名', '1': '1', '2': '2', '3': '3' }
])

// 图表实例
const scoreChart = ref<HTMLElement>()
const countChart = ref<HTMLElement>()
let scoreChartInstance: echarts.ECharts | null = null
let countChartInstance: echarts.ECharts | null = null

// 添加高校
const addUniversity = () => {
  // 实际项目中这里会弹出选择高校的对话框
  const newUniversity = {
    id: Date.now(),
    name: `高校${universities.value.length + 1}`
  }
  universities.value.push(newUniversity)
}

// 移除高校
const removeUniversity = (index: number) => {
  universities.value.splice(index, 1)
}

// 导出对比
const exportComparison = () => {
  console.log('导出对比数据')
  // 实际项目中这里会实现导出功能
}

// 初始化图表
const initCharts = () => {
  if (universities.value.length === 0) return
  
  // 分数对比图表
  if (scoreChart.value) {
    scoreChartInstance = echarts.init(scoreChart.value)
    const scoreOption = {
      title: {
        text: '2023年录取分数对比'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      legend: {
        data: ['理科最低分', '文科最低分']
      },
      xAxis: {
        type: 'category',
        data: universities.value.map(u => u.name)
      },
      yAxis: {
        type: 'value',
        name: '分数'
      },
      series: [
        {
          name: '理科最低分',
          type: 'bar',
          data: [680, 675, 660],
          itemStyle: {
            color: '#409eff'
          }
        },
        {
          name: '文科最低分',
          type: 'bar',
          data: [670, 675, 655],
          itemStyle: {
            color: '#67c23a'
          }
        }
      ]
    }
    scoreChartInstance.setOption(scoreOption)
  }
  
  // 招生人数对比图表
  if (countChart.value) {
    countChartInstance = echarts.init(countChart.value)
    const countOption = {
      title: {
        text: '2023年招生人数对比'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: universities.value.map(u => u.name)
      },
      yAxis: {
        type: 'value',
        name: '人数'
      },
      series: [
        {
          name: '招生人数',
          type: 'bar',
          data: [3500, 3000, 5000],
          itemStyle: {
            color: '#e6a23c'
          }
        }
      ]
    }
    countChartInstance.setOption(countOption)
  }
}

// 监听窗口大小变化
const handleResize = () => {
  scoreChartInstance?.resize()
  countChartInstance?.resize()
}

// 监听高校列表变化
watch(universities, () => {
  setTimeout(() => {
    initCharts()
  }, 100)
}, { deep: true })

// 组件挂载
onMounted(() => {
  initCharts()
  window.addEventListener('resize', handleResize)
})

// 组件卸载
// onUnmounted(() => {
//   window.removeEventListener('resize', handleResize)
//   scoreChartInstance?.dispose()
//   countChartInstance?.dispose()
// })
</script>

<style scoped>
.compare-view {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.el-header {
  background-color: #409eff;
  color: white;
  text-align: center;
  padding: 40px 0;
  margin-bottom: 20px;
}

.el-header h1 {
  margin: 0 0 10px 0;
  font-size: 28px;
}

.el-header p {
  margin: 0;
  font-size: 16px;
  opacity: 0.9;
}

.compare-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.university-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px 0;
}

.university-tag {
  font-size: 14px;
  padding: 8px 16px;
  margin: 5px;
}

.empty-tag {
  font-size: 14px;
  padding: 8px 16px;
  color: #909399;
  background-color: #ecf5ff;
  border-color: #d9ecff;
}

.results-card {
  margin-top: 20px;
}

.comparison-content {
  padding: 20px 0;
}

.chart-container {
  margin-top: 30px;
}

.chart-container h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
}

.empty-comparison {
  padding: 40px 0;
  text-align: center;
}
</style>
