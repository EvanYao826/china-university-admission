<template>
  <div class="university-detail">
    <el-container>
      <el-header>
        <h1>{{ university.name || '高校详情' }}</h1>
        <p>{{ university.province }} | {{ university.typeText }}</p>
      </el-header>
      
      <el-main>
        <!-- 高校基本信息 -->
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <el-button type="primary" size="small" @click="addToCompare">添加到对比</el-button>
            </div>
          </template>
          
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">高校名称：</span>
              <span class="info-value">{{ university.name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">所在省份：</span>
              <span class="info-value">{{ university.province }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">高校类型：</span>
              <span class="info-value">{{ university.typeText }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">办学层次：</span>
              <span class="info-value">{{ university.level }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">建校年份：</span>
              <span class="info-value">{{ university.foundedYear }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">在校生数：</span>
              <span class="info-value">{{ university.studentCount }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">学校地址：</span>
              <span class="info-value">{{ university.address }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">联系电话：</span>
              <span class="info-value">{{ university.phone }}</span>
            </div>
          </div>
        </el-card>
        
        <!-- 录取数据 -->
        <el-card class="admission-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>录取数据</span>
              <el-select v-model="selectedYear" placeholder="选择年份" size="small">
                <el-option label="2023" value="2023" />
                <el-option label="2022" value="2022" />
                <el-option label="2021" value="2021" />
              </el-select>
            </div>
          </template>
          
          <el-tabs>
            <el-tab-pane label="高考录取">
              <el-table :data="gaokaoData" style="width: 100%">
                <el-table-column prop="category" label="科类" width="100" />
                <el-table-column prop="batch" label="批次" width="100" />
                <el-table-column prop="minScore" label="最低分" width="100" />
                <el-table-column prop="avgScore" label="平均分" width="100" />
                <el-table-column prop="maxScore" label="最高分" width="100" />
                <el-table-column prop="minRank" label="最低位次" width="100" />
                <el-table-column prop="avgRank" label="平均位次" width="100" />
                <el-table-column prop="admissionCount" label="招生人数" width="100" />
              </el-table>
            </el-tab-pane>
            
            <el-tab-pane label="研究生录取">
              <el-table :data="graduateData" style="width: 100%">
                <el-table-column prop="major" label="专业" width="180" />
                <el-table-column prop="degreeType" label="学位类型" width="100" />
                <el-table-column prop="studyMode" label="学习方式" width="100" />
                <el-table-column prop="minScore" label="最低分" width="100" />
                <el-table-column prop="avgScore" label="平均分" width="100" />
                <el-table-column prop="admissionCount" label="招生人数" width="100" />
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-card>
        
        <!-- 数据统计 -->
        <el-card class="stats-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>数据统计</span>
            </div>
          </template>
          
          <div class="stats-container">
            <div class="stat-item">
              <div class="stat-value">{{ university.ranking }}</div>
              <div class="stat-label">全国排名</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ university.majorCount }}</div>
              <div class="stat-label">专业数量</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ university.teacherCount }}</div>
              <div class="stat-label">教师数量</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ university.phdPrograms }}</div>
              <div class="stat-label">博士点</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ university.masterPrograms }}</div>
              <div class="stat-label">硕士点</div>
            </div>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const universityId = route.params.id

// 高校信息
const university = reactive({
  id: 1,
  name: '清华大学',
  province: '北京',
  type: '985,211,doubleFirstClass',
  typeText: '985工程 · 211工程 · 双一流',
  level: '本科',
  foundedYear: 1911,
  studentCount: 40000,
  address: '北京市海淀区清华园1号',
  phone: '010-62782114',
  ranking: 1,
  majorCount: 80,
  teacherCount: 3000,
  phdPrograms: 50,
  masterPrograms: 60
})

// 选择年份
const selectedYear = ref('2023')

// 高考录取数据
const gaokaoData = ref([
  {
    category: '理科',
    batch: '本科一批',
    minScore: 680,
    avgScore: 690,
    maxScore: 710,
    minRank: 100,
    avgRank: 50,
    admissionCount: 120
  },
  {
    category: '文科',
    batch: '本科一批',
    minScore: 670,
    avgScore: 680,
    maxScore: 700,
    minRank: 50,
    avgRank: 30,
    admissionCount: 80
  }
])

// 研究生录取数据
const graduateData = ref([
  {
    major: '计算机科学与技术',
    degreeType: '硕士',
    studyMode: '全日制',
    minScore: 380,
    avgScore: 390,
    admissionCount: 50
  },
  {
    major: '软件工程',
    degreeType: '硕士',
    studyMode: '全日制',
    minScore: 370,
    avgScore: 380,
    admissionCount: 40
  },
  {
    major: '电子信息工程',
    degreeType: '硕士',
    studyMode: '全日制',
    minScore: 375,
    avgScore: 385,
    admissionCount: 45
  }
])

// 添加到对比
const addToCompare = () => {
  console.log('添加到对比:', university)
  // 实际项目中这里会将高校添加到对比列表
}

// 组件挂载
onMounted(() => {
  // 实际项目中这里会根据ID获取高校详情
  console.log('UniversityDetail mounted, id:', universityId)
})
</script>

<style scoped>
.university-detail {
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

.info-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
  padding: 10px 0;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-label {
  font-weight: 500;
  color: #606266;
  width: 100px;
  flex-shrink: 0;
}

.info-value {
  color: #303133;
  flex: 1;
}

.admission-card {
  margin-top: 20px;
}

.stats-card {
  margin-top: 20px;
}

.stats-container {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 20px;
  padding: 20px 0;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
  min-width: 120px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-container {
    flex-direction: column;
    align-items: center;
  }
  
  .stat-item {
    width: 100%;
    max-width: 200px;
  }
}
</style>
