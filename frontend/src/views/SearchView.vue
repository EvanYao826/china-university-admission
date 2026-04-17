<template>
  <div class="search-view">
    <el-container>
      <el-header>
        <h1>搜索结果</h1>
        <p>根据关键词搜索高校和录取数据</p>
      </el-header>
      
      <el-main>
        <el-card class="search-card">
          <template #header>
            <div class="card-header">
              <span>搜索</span>
            </div>
          </template>
          
          <el-form :inline="true" :model="searchForm" class="search-form">
            <el-form-item>
              <el-input
                v-model="searchForm.keyword"
                placeholder="输入高校名称或专业"
                style="width: 300px;"
                prefix-icon="el-icon-search"
              />
            </el-form-item>
            
            <el-form-item>
              <el-select v-model="searchForm.type" placeholder="搜索类型">
                <el-option label="高校" value="university" />
                <el-option label="专业" value="major" />
                <el-option label="录取数据" value="admission" />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="search">搜索</el-button>
              <el-button @click="reset">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <el-card class="results-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>搜索结果</span>
              <span class="result-count">共 {{ total }} 条结果</span>
            </div>
          </template>
          
          <div v-if="searchResults.length > 0">
            <el-tabs>
              <el-tab-pane label="高校" v-if="universityResults.length > 0">
                <el-table :data="universityResults" style="width: 100%">
                  <el-table-column prop="name" label="高校名称" width="200">
                    <template #default="scope">
                      <el-link type="primary" @click="viewUniversity(scope.row.id)">
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
                  <el-table-column label="操作" width="100">
                    <template #default="scope">
                      <el-button size="small" type="primary" @click="viewUniversity(scope.row.id)">
                        详情
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-tab-pane>
              
              <el-tab-pane label="专业" v-if="majorResults.length > 0">
                <el-table :data="majorResults" style="width: 100%">
                  <el-table-column prop="name" label="专业名称" width="200" />
                  <el-table-column prop="universityName" label="所属高校" width="200">
                    <template #default="scope">
                      <el-link type="primary" @click="viewUniversity(scope.row.universityId)">
                        {{ scope.row.universityName }}
                      </el-link>
                    </template>
                  </el-table-column>
                  <el-table-column prop="category" label="专业类别" width="120" />
                  <el-table-column prop="level" label="层次" width="100" />
                </el-table>
              </el-tab-pane>
              
              <el-tab-pane label="录取数据" v-if="admissionResults.length > 0">
                <el-table :data="admissionResults" style="width: 100%">
                  <el-table-column prop="universityName" label="高校名称" width="200">
                    <template #default="scope">
                      <el-link type="primary" @click="viewUniversity(scope.row.universityId)">
                        {{ scope.row.universityName }}
                      </el-link>
                    </template>
                  </el-table-column>
                  <el-table-column prop="province" label="省份" width="100" />
                  <el-table-column prop="year" label="年份" width="80" />
                  <el-table-column prop="category" label="科类" width="100" />
                  <el-table-column prop="batch" label="批次" width="100" />
                  <el-table-column prop="minScore" label="最低分" width="100" />
                  <el-table-column prop="minRank" label="最低位次" width="100" />
                </el-table>
              </el-tab-pane>
            </el-tabs>
            
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
          </div>
          
          <div v-else class="empty-results">
            <el-empty description="未找到相关结果" />
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 搜索表单
const searchForm = reactive({
  keyword: route.query.keyword as string || '',
  type: 'university'
})

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 搜索结果
const searchResults = ref([
  // 高校结果
  {
    type: 'university',
    id: 1,
    name: '清华大学',
    province: '北京',
    type: '985,211,doubleFirstClass',
    level: '本科'
  },
  {
    type: 'university',
    id: 2,
    name: '北京大学',
    province: '北京',
    type: '985,211,doubleFirstClass',
    level: '本科'
  },
  // 专业结果
  {
    type: 'major',
    id: 1,
    name: '计算机科学与技术',
    universityId: 1,
    universityName: '清华大学',
    category: '工学',
    level: '本科'
  },
  {
    type: 'major',
    id: 2,
    name: '软件工程',
    universityId: 1,
    universityName: '清华大学',
    category: '工学',
    level: '本科'
  },
  // 录取数据结果
  {
    type: 'admission',
    id: 1,
    universityId: 1,
    universityName: '清华大学',
    province: '北京',
    year: '2023',
    category: '理科',
    batch: '本科一批',
    minScore: 680,
    minRank: 100
  }
])

// 按类型分类结果
const universityResults = computed(() => {
  return searchResults.value.filter(item => item.type === 'university')
})

const majorResults = computed(() => {
  return searchResults.value.filter(item => item.type === 'major')
})

const admissionResults = computed(() => {
  return searchResults.value.filter(item => item.type === 'admission')
})

total.value = searchResults.value.length

// 搜索
const search = () => {
  // 实际项目中这里会调用API搜索数据
  console.log('搜索:', searchForm)
  // 模拟搜索结果
  currentPage.value = 1
}

// 重置
const reset = () => {
  Object.assign(searchForm, {
    keyword: '',
    type: 'university'
  })
}

// 查看高校详情
const viewUniversity = (id: number) => {
  router.push(`/universities/${id}`)
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
}

const handleCurrentChange = (current: number) => {
  currentPage.value = current
}
</script>

<style scoped>
.search-view {
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

.search-card {
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

.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.results-card {
  margin-top: 20px;
}

.empty-results {
  padding: 40px 0;
  text-align: center;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
