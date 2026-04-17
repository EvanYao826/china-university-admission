<template>
  <div class="statistics-view">
    <el-container>
      <el-header>
        <h1>数据统计</h1>
        <p>查看高校录取数据的统计分析</p>
      </el-header>
      
      <el-main>
        <el-card class="filter-card">
          <template #header>
            <div class="card-header">
              <span>统计筛选</span>
            </div>
          </template>
          
          <el-form :inline="true" :model="filterForm" class="filter-form">
            <el-form-item label="统计类型">
              <el-select v-model="filterForm.statType" placeholder="选择统计类型">
                <el-option label="分数分布" value="scoreDistribution" />
                <el-option label="招生人数" value="admissionCount" />
                <el-option label="高校类型分布" value="universityType" />
                <el-option label="省份分布" value="provinceDistribution" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="年份">
              <el-select v-model="filterForm.year" placeholder="选择年份">
                <el-option label="2023" value="2023" />
                <el-option label="2022" value="2022" />
                <el-option label="2021" value="2021" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="省份">
              <el-select v-model="filterForm.province" placeholder="选择省份">
                <el-option label="全部" value="" />
                <el-option label="北京" value="北京" />
                <el-option label="上海" value="上海" />
                <el-option label="浙江" value="浙江" />
                <el-option label="江苏" value="江苏" />
                <el-option label="广东" value="广东" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="科类">
              <el-select v-model="filterForm.category" placeholder="选择科类">
                <el-option label="全部" value="" />
                <el-option label="理科" value="理科" />
                <el-option label="文科" value="文科" />
                <el-option label="综合改革" value="综合改革" />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="generateStatistics">生成统计</el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <el-card class="stats-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>统计结果</span>
              <el-button type="primary" size="small" @click="exportStatistics">导出统计</el-button>
            </div>
          </template>
          
          <div class="stats-content">
            <div v-if="filterForm.statType === 'scoreDistribution'" class="chart-container">
              <h3>分数分布</h3>
              <div ref="scoreDistributionChart" style="height: 400px;"></div>
            </div>
            
            <div v-else-if="filterForm.statType === 'admissionCount'" class="chart-container">
              <h3>招生人数统计</h3>
              <div ref="admissionCountChart" style="height: 400px;"></div>
            </div>
            
            <div v-else-if="filterForm.statType === 'universityType'" class="chart-container">
              <h3>高校类型分布</h3>
              <div ref="universityTypeChart" style="height: 400px;"></div>
            </div>
            
            <div v-else-if="filterForm.statType === 'provinceDistribution'" class="chart-container">
              <h3>省份分布</h3>
              <div ref="provinceDistributionChart" style="height: 400px;"></div>
            </div>
            
            <div v-else class="empty-stats">
              <el-empty description="请选择统计类型并生成统计" />
            </div>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

// 筛选表单
const filterForm = reactive({
  statType: 'scoreDistribution',
  year: '2023',
  province: '',
  category: ''
})

// 图表实例
const scoreDistributionChart = ref<HTMLElement>()
const admissionCountChart = ref<HTMLElement>()
const universityTypeChart = ref<HTMLElement>()
const provinceDistributionChart = ref<HTMLElement>()

let scoreDistributionChartInstance: echarts.ECharts | null = null
let admissionCountChartInstance: echarts.ECharts | null = null
let universityTypeChartInstance: echarts.ECharts | null = null
let provinceDistributionChartInstance: echarts.ECharts | null = null

// 生成统计
const generateStatistics = () => {
  // 实际项目中这里会调用API获取统计数据
  console.log('生成统计:', filterForm)
  initCharts()
}

// 导出统计
const exportStatistics = () => {
  console.log('导出统计')
  // 实际项目中这里会实现导出功能
}

// 初始化图表
const initCharts = () => {
  switch (filterForm.statType) {
    case 'scoreDistribution':
      initScoreDistributionChart()
      break
    case 'admissionCount':
      initAdmissionCountChart()
      break
    case 'universityType':
      initUniversityTypeChart()
      break
    case 'provinceDistribution':
      initProvinceDistributionChart()
      break
  }
}

// 分数分布图表
const initScoreDistributionChart = () => {
  if (scoreDistributionChart.value) {
    scoreDistributionChartInstance = echarts.init(scoreDistributionChart.value)
    const option = {
      title: {
        text: '2023年高考录取分数分布'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      legend: {
        data: ['理科', '文科']
      },
      xAxis: {
        type: 'category',
        data: ['600以下', '600-620', '620-640', '640-660', '660-680', '680以上']
      },
      yAxis: {
        type: 'value',
        name: '高校数量'
      },
      series: [
        {
          name: '理科',
          type: 'bar',
          data: [120, 80, 50, 30, 15, 5],
          itemStyle: {
            color: '#409eff'
          }
        },
        {
          name: '文科',
          type: 'bar',
          data: [100, 70, 40, 20, 10, 3],
          itemStyle: {
            color: '#67c23a'
          }
        }
      ]
    }
    scoreDistributionChartInstance.setOption(option)
  }
}

// 招生人数图表
const initAdmissionCountChart = () => {
  if (admissionCountChart.value) {
    admissionCountChartInstance = echarts.init(admissionCountChart.value)
    const option = {
      title: {
        text: '2023年高校招生人数统计'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: ['清华大学', '北京大学', '浙江大学', '复旦大学', '上海交通大学']
      },
      yAxis: {
        type: 'value',
        name: '招生人数'
      },
      series: [
        {
          name: '招生人数',
          type: 'bar',
          data: [3500, 3000, 5000, 3200, 3800],
          itemStyle: {
            color: '#e6a23c'
          }
        }
      ]
    }
    admissionCountChartInstance.setOption(option)
  }
}

// 高校类型分布图表
const initUniversityTypeChart = () => {
  if (universityTypeChart.value) {
    universityTypeChartInstance = echarts.init(universityTypeChart.value)
    const option = {
      title: {
        text: '高校类型分布'
      },
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '高校类型',
          type: 'pie',
          radius: '50%',
          data: [
            { value: 39, name: '985工程' },
            { value: 116, name: '211工程' },
            { value: 137, name: '双一流' },
            { value: 1800, name: '普通本科' }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
    universityTypeChartInstance.setOption(option)
  }
}

// 省份分布图表
const initProvinceDistributionChart = () => {
  if (provinceDistributionChart.value) {
    provinceDistributionChartInstance = echarts.init(provinceDistributionChart.value)
    const option = {
      title: {
        text: '高校省份分布'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: ['北京', '上海', '江苏', '广东', '浙江', '湖北', '四川', '山东', '辽宁', '陕西'],
        axisLabel: {
          rotate: 45
        }
      },
      yAxis: {
        type: 'value',
        name: '高校数量'
      },
      series: [
        {
          name: '高校数量',
          type: 'bar',
          data: [68, 64, 167, 154, 107, 129, 134, 146, 114, 96],
          itemStyle: {
            color: '#909399'
          }
        }
      ]
    }
    provinceDistributionChartInstance.setOption(option)
  }
}

// 监听窗口大小变化
const handleResize = () => {
  scoreDistributionChartInstance?.resize()
  admissionCountChartInstance?.resize()
  universityTypeChartInstance?.resize()
  provinceDistributionChartInstance?.resize()
}

// 监听统计类型变化
watch(() => filterForm.statType, () => {
  setTimeout(() => {
    initCharts()
  }, 100)
})

// 组件挂载
onMounted(() => {
  initCharts()
  window.addEventListener('resize', handleResize)
})

// 组件卸载
// onUnmounted(() => {
//   window.removeEventListener('resize', handleResize)
//   scoreDistributionChartInstance?.dispose()
//   admissionCountChartInstance?.dispose()
//   universityTypeChartInstance?.dispose()
//   provinceDistributionChartInstance?.dispose()
// })
</script>

<style scoped>
.statistics-view {
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

.filter-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.stats-card {
  margin-top: 20px;
}

.stats-content {
  padding: 20px 0;
}

.chart-container {
  margin: 20px 0;
}

.chart-container h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
}

.empty-stats {
  padding: 40px 0;
  text-align: center;
}
</style>
