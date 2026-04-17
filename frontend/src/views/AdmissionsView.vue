<template>
  <div class="admissions-view">
    <el-container>
      <el-header>
        <h1>录取数据查询</h1>
        <p>查询各高校的录取分数线和招生情况</p>
      </el-header>
      
      <el-main>
        <el-card class="filter-card">
          <template #header>
            <div class="card-header">
              <span>筛选条件</span>
            </div>
          </template>
          
          <el-form :inline="true" :model="filterForm" class="filter-form">
            <el-form-item label="高校类型">
              <el-select v-model="filterForm.universityType" placeholder="选择高校类型">
                <el-option label="全部" value="" />
                <el-option label="985工程" value="985" />
                <el-option label="211工程" value="211" />
                <el-option label="双一流" value="doubleFirstClass" />
                <el-option label="普通本科" value="regular" />
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
            
            <el-form-item label="年份">
              <el-select v-model="filterForm.year" placeholder="选择年份">
                <el-option label="2023" value="2023" />
                <el-option label="2022" value="2022" />
                <el-option label="2021" value="2021" />
                <el-option label="2020" value="2020" />
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
              <el-button type="primary" @click="search">查询</el-button>
              <el-button @click="reset">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <el-card class="results-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>录取数据列表</span>
              <el-button type="primary" size="small" @click="exportData">导出数据</el-button>
            </div>
          </template>
          
          <el-table :data="admissionsData" style="width: 100%">
            <el-table-column prop="universityName" label="高校名称" width="180" />
            <el-table-column prop="province" label="省份" width="100" />
            <el-table-column prop="year" label="年份" width="80" />
            <el-table-column prop="category" label="科类" width="100" />
            <el-table-column prop="batch" label="批次" width="100" />
            <el-table-column prop="minScore" label="最低分" width="100" />
            <el-table-column prop="avgScore" label="平均分" width="100" />
            <el-table-column prop="minRank" label="最低位次" width="100" />
            <el-table-column prop="admissionCount" label="招生人数" width="100" />
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" type="primary" @click="viewDetails(scope.row)">
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination" style="margin-top: 20px;">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="total"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import type { FormInstance } from 'element-plus'

// 筛选表单
const filterForm = reactive({
  universityType: '',
  province: '',
  year: '2023',
  category: ''
})

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 数据
const admissionsData = ref([
  {
    universityName: '清华大学',
    province: '北京',
    year: '2023',
    category: '理科',
    batch: '本科一批',
    minScore: 680,
    avgScore: 690,
    minRank: 100,
    admissionCount: 120
  },
  {
    universityName: '北京大学',
    province: '北京',
    year: '2023',
    category: '文科',
    batch: '本科一批',
    minScore: 670,
    avgScore: 680,
    minRank: 50,
    admissionCount: 100
  },
  {
    universityName: '浙江大学',
    province: '浙江',
    year: '2023',
    category: '综合改革',
    batch: '本科一批',
    minScore: 660,
    avgScore: 670,
    minRank: 200,
    admissionCount: 150
  }
])

total.value = admissionsData.value.length

// 搜索
const search = () => {
  // 实际项目中这里会调用API获取数据
  console.log('搜索条件:', filterForm)
  // 模拟搜索结果
  currentPage.value = 1
}

// 重置
const reset = () => {
  Object.assign(filterForm, {
    universityType: '',
    province: '',
    year: '2023',
    category: ''
  })
}

// 查看详情
const viewDetails = (row: any) => {
  console.log('查看详情:', row)
  // 实际项目中这里会跳转到详情页面
}

// 导出数据
const exportData = () => {
  console.log('导出数据')
  // 实际项目中这里会实现导出功能
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
}

const handleCurrentChange = (current: number) => {
  currentPage.value = current
}

// 组件挂载
onMounted(() => {
  // 实际项目中这里会初始化数据
  console.log('AdmissionsView mounted')
})
</script>

<style scoped>
.admissions-view {
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

.results-card {
  margin-top: 20px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
