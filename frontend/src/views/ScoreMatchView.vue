<template>
  <div class="score-match-view">
    <el-container>
      <el-header>
        <h1>分数匹配</h1>
        <p>根据分数查询匹配的高校</p>
      </el-header>
      
      <el-main>
        <el-card class="match-card">
          <template #header>
            <div class="card-header">
              <span>分数匹配</span>
            </div>
          </template>
          
          <el-form :model="matchForm" class="match-form">
            <el-form-item label="省份" :label-width="formLabelWidth">
              <el-select v-model="matchForm.province" placeholder="选择省份" style="width: 100%">
                <el-option label="北京" value="北京" />
                <el-option label="上海" value="上海" />
                <el-option label="浙江" value="浙江" />
                <el-option label="江苏" value="江苏" />
                <el-option label="广东" value="广东" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="年份" :label-width="formLabelWidth">
              <el-select v-model="matchForm.year" placeholder="选择年份" style="width: 100%">
                <el-option label="2023" value="2023" />
                <el-option label="2022" value="2022" />
                <el-option label="2021" value="2021" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="科类" :label-width="formLabelWidth">
              <el-select v-model="matchForm.category" placeholder="选择科类" style="width: 100%">
                <el-option label="理科" value="理科" />
                <el-option label="文科" value="文科" />
                <el-option label="综合改革" value="综合改革" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="分数" :label-width="formLabelWidth">
              <el-input-number
                v-model="matchForm.score"
                :min="0"
                :max="750"
                :step="1"
                placeholder="输入分数"
                style="width: 100%"
              />
            </el-form-item>
            
            <el-form-item label="位次" :label-width="formLabelWidth">
              <el-input-number
                v-model="matchForm.rank"
                :min="0"
                :max="1000000"
                :step="1"
                placeholder="输入位次（可选）"
                style="width: 100%"
              />
            </el-form-item>
            
            <el-form-item label="批次" :label-width="formLabelWidth">
              <el-select v-model="matchForm.batch" placeholder="选择批次" style="width: 100%">
                <el-option label="本科一批" value="本科一批" />
                <el-option label="本科二批" value="本科二批" />
                <el-option label="专科批" value="专科批" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="高校类型" :label-width="formLabelWidth">
              <el-select v-model="matchForm.universityType" placeholder="选择高校类型" style="width: 100%">
                <el-option label="全部" value="" />
                <el-option label="985工程" value="985" />
                <el-option label="211工程" value="211" />
                <el-option label="双一流" value="doubleFirstClass" />
                <el-option label="普通本科" value="regular" />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="match" style="width: 100%">开始匹配</el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <el-card class="results-card" style="margin-top: 20px;" v-if="showResults">
          <template #header>
            <div class="card-header">
              <span>匹配结果</span>
              <span class="result-count">共 {{ matchResults.length }} 所高校</span>
            </div>
          </template>
          
          <el-table :data="matchResults" style="width: 100%">
            <el-table-column prop="universityName" label="高校名称" width="180">
              <template #default="scope">
                <el-link type="primary" @click="viewDetail(scope.row.universityId)">
                  {{ scope.row.universityName }}
                </el-link>
              </template>
            </el-table-column>
            <el-table-column prop="province" label="省份" width="100" />
            <el-table-column prop="batch" label="批次" width="100" />
            <el-table-column prop="minScore" label="最低分" width="100" />
            <el-table-column prop="avgScore" label="平均分" width="100" />
            <el-table-column prop="scoreDifference" label="分数差" width="100">
              <template #default="scope">
                <span :class="scope.row.scoreDifference >= 0 ? 'positive' : 'negative'">
                  {{ scope.row.scoreDifference >= 0 ? '+' : '' }}{{ scope.row.scoreDifference }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="minRank" label="最低位次" width="100" />
            <el-table-column prop="matchLevel" label="匹配度" width="100">
              <template #default="scope">
                <el-tag :type="getMatchLevelType(scope.row.matchLevel)">
                  {{ scope.row.matchLevel }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" type="primary" @click="viewDetail(scope.row.universityId)">
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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 表单标签宽度
const formLabelWidth = '100px'

// 匹配表单
const matchForm = reactive({
  province: '北京',
  year: '2023',
  category: '理科',
  score: 650,
  rank: null,
  batch: '本科一批',
  universityType: ''
})

// 显示结果
const showResults = ref(false)

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 匹配结果
const matchResults = ref([
  {
    universityId: 1,
    universityName: '清华大学',
    province: '北京',
    batch: '本科一批',
    minScore: 680,
    avgScore: 690,
    minRank: 100,
    scoreDifference: -30,
    matchLevel: '冲刺'
  },
  {
    universityId: 2,
    universityName: '北京大学',
    province: '北京',
    batch: '本科一批',
    minScore: 675,
    avgScore: 685,
    minRank: 150,
    scoreDifference: -25,
    matchLevel: '冲刺'
  },
  {
    universityId: 3,
    universityName: '浙江大学',
    province: '浙江',
    batch: '本科一批',
    minScore: 660,
    avgScore: 670,
    minRank: 200,
    scoreDifference: -10,
    matchLevel: '冲刺'
  },
  {
    universityId: 4,
    universityName: '复旦大学',
    province: '上海',
    batch: '本科一批',
    minScore: 655,
    avgScore: 665,
    minRank: 300,
    scoreDifference: -5,
    matchLevel: '稳妥'
  },
  {
    universityId: 5,
    universityName: '上海交通大学',
    province: '上海',
    batch: '本科一批',
    minScore: 650,
    avgScore: 660,
    minRank: 350,
    scoreDifference: 0,
    matchLevel: '稳妥'
  }
])

total.value = matchResults.value.length

// 开始匹配
const match = () => {
  // 实际项目中这里会调用API获取匹配结果
  console.log('匹配条件:', matchForm)
  showResults.value = true
  currentPage.value = 1
}

// 查看详情
const viewDetail = (id: number) => {
  router.push(`/universities/${id}`)
}

// 添加到对比
const addToCompare = (item: any) => {
  console.log('添加到对比:', item)
  // 实际项目中这里会将高校添加到对比列表
}

// 获取匹配度标签类型
const getMatchLevelType = (level: string) => {
  switch (level) {
    case '冲刺':
      return 'danger'
    case '稳妥':
      return 'warning'
    case '保底':
      return 'success'
    default:
      return 'info'
  }
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
.score-match-view {
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

.match-card {
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

.match-form {
  max-width: 600px;
  margin: 0 auto;
}

.results-card {
  margin-top: 20px;
}

.positive {
  color: #67c23a;
  font-weight: 500;
}

.negative {
  color: #f56c6c;
  font-weight: 500;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
