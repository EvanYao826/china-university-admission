<template>
  <div class="universities-view">
    <el-container>
      <el-header>
        <h1>高校查询</h1>
        <p>浏览和搜索全国高校信息</p>
      </el-header>
      
      <el-main>
        <el-card class="filter-card">
          <template #header>
            <div class="card-header">
              <span>筛选条件</span>
            </div>
          </template>
          
          <el-form :inline="true" :model="filterForm" class="filter-form">
            <el-form-item label="高校名称">
              <el-input v-model="filterForm.name" placeholder="输入高校名称" style="width: 200px;" />
            </el-form-item>
            
            <el-form-item label="高校类型">
              <el-select v-model="filterForm.type" placeholder="选择高校类型">
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
            
            <el-form-item label="办学层次">
              <el-select v-model="filterForm.level" placeholder="选择办学层次">
                <el-option label="全部" value="" />
                <el-option label="本科" value="undergraduate" />
                <el-option label="专科" value="juniorCollege" />
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
              <span>高校列表</span>
              <span class="result-count">共 {{ total }} 所高校</span>
            </div>
          </template>
          
          <el-table :data="universitiesData" style="width: 100%">
            <el-table-column prop="name" label="高校名称" width="200">
              <template #default="scope">
                <el-link type="primary" @click="viewDetail(scope.row.id)">
                  {{ scope.row.name }}
                </el-link>
              </template>
            </el-table-column>
            <el-table-column prop="province" label="省份" width="100" />
            <el-table-column prop="type" label="类型" width="120">
              <template #default="scope">
                <el-tag v-if="scope.row.type.includes('985')" type="danger">985</el-tag>
                <el-tag v-else-if="scope.row.type.includes('211')" type="warning">211</el-tag>
                <el-tag v-else-if="scope.row.type.includes('doubleFirstClass')" type="success">双一流</el-tag>
                <el-tag v-else type="info">普通</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="level" label="办学层次" width="100" />
            <el-table-column prop="foundedYear" label="建校年份" width="100" />
            <el-table-column prop="studentCount" label="在校生数" width="100" />
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" type="primary" @click="viewDetail(scope.row.id)">
                  详情
                </el-button>
                <el-button size="small" @click="addToCompare(scope.row)">
                  对比
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
import { useRouter } from 'vue-router'

const router = useRouter()

// 筛选表单
const filterForm = reactive({
  name: '',
  type: '',
  province: '',
  level: ''
})

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 数据
const universitiesData = ref([
  {
    id: 1,
    name: '清华大学',
    province: '北京',
    type: '985,211,doubleFirstClass',
    level: '本科',
    foundedYear: 1911,
    studentCount: 40000
  },
  {
    id: 2,
    name: '北京大学',
    province: '北京',
    type: '985,211,doubleFirstClass',
    level: '本科',
    foundedYear: 1898,
    studentCount: 35000
  },
  {
    id: 3,
    name: '浙江大学',
    province: '浙江',
    type: '985,211,doubleFirstClass',
    level: '本科',
    foundedYear: 1897,
    studentCount: 50000
  },
  {
    id: 4,
    name: '复旦大学',
    province: '上海',
    type: '985,211,doubleFirstClass',
    level: '本科',
    foundedYear: 1905,
    studentCount: 30000
  },
  {
    id: 5,
    name: '上海交通大学',
    province: '上海',
    type: '985,211,doubleFirstClass',
    level: '本科',
    foundedYear: 1896,
    studentCount: 38000
  }
])

total.value = universitiesData.value.length

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
    name: '',
    type: '',
    province: '',
    level: ''
  })
}

// 查看详情
const viewDetail = (id: number) => {
  router.push(`/universities/${id}`)
}

// 添加到对比
const addToCompare = (university: any) => {
  console.log('添加到对比:', university)
  // 实际项目中这里会将高校添加到对比列表
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
  console.log('UniversitiesView mounted')
})
</script>

<style scoped>
.universities-view {
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

.result-count {
  font-size: 14px;
  color: #606266;
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
