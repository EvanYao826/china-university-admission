<template>
  <div class="universities-page">
    <div class="top-search-row">
      <div class="search-item">
        <label>学校名称</label>
        <el-input v-model="filters.name" placeholder="输入学校名称查询" clearable @clear="fetchSchools" @blur="handleSearch" @keyup.enter="handleSearch">
          <template #append>
            <el-button @click="handleSearch" :icon="Search" circle />
          </template>
        </el-input>
      </div>
      <div class="search-item">
        <label>学校类型</label>
        <el-select v-model="filters.type" placeholder="请选择类型" clearable @change="fetchSchools" style="width: 100%;">
          <el-option label="综合类" value="综合" />
          <el-option label="理工类" value="理工" />
          <el-option label="师范类" value="师范" />
          <el-option label="医药类" value="医药" />
          <el-option label="农林类" value="农林" />
          <el-option label="财经类" value="财经" />
          <el-option label="政法类" value="政法" />
          <el-option label="艺术类" value="艺术" />
          <el-option label="体育类" value="体育" />
          <el-option label="民族类" value="民族" />
          <el-option label="语言类" value="语言" />
          <el-option label="其他" value="其他" />
        </el-select>
      </div>
      <div class="search-item">
        <label>学校层次</label>
        <el-select v-model="filters.level" placeholder="请选择层次" clearable @change="fetchSchools" style="width: 100%;">
          <el-option label="985工程" value="985" />
          <el-option label="211工程" value="211" />
          <el-option label="双一流" value="双一流" />
          <el-option label="普通本科" value="普通本科" />
          <el-option label="专科" value="专科" />
        </el-select>
      </div>
      <div class="search-item">
        <label>所在省份</label>
        <el-select v-model="filters.province" placeholder="请选择省份" clearable @change="fetchSchools" style="width: 100%;">
          <el-option v-for="p in provinces" :key="p" :label="p" :value="p" />
        </el-select>
      </div>
    </div>

    <div class="main-container">
      <div class="school-list-box">
        <div class="school-list-title">院校列表</div>
        <div class="school-list-content">
          <div
            v-for="school in schools"
            :key="school.id"
            class="school-item"
            :class="{ active: selectedSchool?.id === school.id }"
            @click="selectSchool(school)"
          >
            {{ school.name }}
            <span class="school-tag">{{ getSchoolLevel(school.level) }}</span>
          </div>
          <el-empty v-if="schools.length === 0" description="暂无数据" />
        </div>
      </div>

      <div class="content-box">
        <div class="tab-nav">
          <div
            class="tab-item"
            :class="{ active: activeTab === 'intro' }"
            @click="activeTab = 'intro'"
          >
            学校概况
          </div>
          <div
            class="tab-item"
            :class="{ active: activeTab === 'undergraduate' }"
            @click="activeTab = 'undergraduate'"
          >
            本科生招生
          </div>
          <div
            class="tab-item"
            :class="{ active: activeTab === 'postgrad' }"
            @click="activeTab = 'postgrad'"
          >
            研究生招生
          </div>
        </div>

        <div class="tab-content-container">
          <div v-show="activeTab === 'intro'" class="tab-content">
            <div class="tab-panel">
              <template v-if="selectedSchool">
                <h3>学校简介</h3>
                <div class="intro-box">
                  {{ selectedSchool.description || '暂无学校简介' }}
                </div>

                <h3>基本信息</h3>
                <table class="info-table">
                  <tbody>
                      <tr>
                        <td>学校类型</td>
                        <td>{{ selectedSchool.type || '-' }}</td>
                      </tr>
                      <tr>
                        <td>学校层次</td>
                        <td>{{ selectedSchool.level || '-' }}</td>
                      </tr>
                      <tr>
                        <td>所在省份</td>
                        <td>{{ selectedSchool.province || '-' }}</td>
                      </tr>
                      <tr>
                        <td>所在城市</td>
                        <td>{{ selectedSchool.city || '-' }}</td>
                      </tr>
                      <tr>
                        <td>特色标签</td>
                        <td>{{ selectedSchool.tags || '-' }}</td>
                      </tr>
                      <tr>
                        <td>学校官网</td>
                        <td>
                          <a v-if="selectedSchool.website" :href="selectedSchool.website" target="_blank" class="website-link">
                            {{ selectedSchool.website }}
                          </a>
                          <span v-else>-</span>
                        </td>
                      </tr>
                    </tbody>
                </table>
              </template>
              <el-empty v-else description="请选择学校" />
            </div>
          </div>

          <div v-show="activeTab === 'undergraduate'" class="tab-content">
            <div class="tab-panel">
              <template v-if="selectedSchool">
                <h3>历年本科录取分数线</h3>
                <div class="filter-row">
                  <el-select v-model="undergraduateFilters.province" placeholder="选择省份" @change="async (value) => { await fetchAvailableCategories(value); fetchUndergraduateScores(); }">
                    <el-option v-for="p in provinces" :key="p" :label="p" :value="p" />
                  </el-select>
                  <el-select v-model="undergraduateFilters.category" placeholder="选择科类" @change="async (value) => { await fetchAvailableBatches(undergraduateFilters.province, value); fetchUndergraduateScores(); }">
                    <el-option v-for="c in availableCategories" :key="c" :label="c" :value="c" />
                  </el-select>
                  <el-select v-model="undergraduateFilters.batch" placeholder="选择批次" @change="fetchUndergraduateScores">
                    <el-option v-for="b in availableBatches" :key="b" :label="b" :value="b" />
                  </el-select>
                </div>

                <el-table :data="undergraduateScores" stripe border>
                  <el-table-column prop="year" label="年份" width="80" />
                  <el-table-column prop="batch" label="录取批次" width="100" />
                  <el-table-column prop="enrollment_type" label="招生类型" width="100" />
                  <el-table-column v-if="showProfessionalGroupColumns" prop="professional_group" label="专业组" width="100" />
                  <el-table-column label="最低分/最低位次" min-width="150">
                    <template #default="{ row }">
                      {{ row.min_score }}{{ row.min_rank ? `/${row.min_rank}` : '' }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="avg_score" label="平均分" width="80">
                    <template #default="{ row }">
                      {{ row.avg_score || '-' }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="provincial_control_line" label="省控线" width="80" />
                  <el-table-column v-if="showProfessionalGroupColumns" prop="subject_requirements" label="选科要求" min-width="120" />
                </el-table>

                <h3>各专业本科录取分数线</h3>
                <div class="filter-row">
                  <el-select v-model="majorFilters.province" placeholder="选择省份" @change="async (value) => { await fetchAvailableCategories(value); fetchMajorScores(); }">
                    <el-option v-for="p in provinces" :key="p" :label="p" :value="p" />
                  </el-select>
                  <el-select v-model="majorFilters.year" placeholder="选择年份" @change="fetchMajorScores">
                    <el-option v-for="y in years" :key="y" :label="`${y}年`" :value="y" />
                  </el-select>
                  <el-select v-model="majorFilters.category" placeholder="选择科类" @change="fetchMajorScores">
                    <el-option v-for="c in availableCategories" :key="c" :label="c" :value="c" />
                  </el-select>
                </div>

                <el-table :data="majorScores" stripe border>
                  <el-table-column prop="major" label="专业名称" min-width="200" />
                  <el-table-column prop="batch" label="录取批次" width="100" />
                  <el-table-column v-if="showProfessionalGroupColumns" prop="professional_group" label="专业组" width="100" />
                  <el-table-column prop="avg_score" label="平均分" width="80">
                    <template #default="{ row }">
                      {{ row.avg_score || '-' }}
                    </template>
                  </el-table-column>
                  <el-table-column label="最低分/最低位次" min-width="150">
                    <template #default="{ row }">
                      {{ row.min_score }}{{ row.min_rank ? `/${row.min_rank}` : '' }}
                    </template>
                  </el-table-column>
                  <el-table-column v-if="showProfessionalGroupColumns" prop="subject_requirements" label="选科要求" min-width="120" />
                </el-table>
              </template>
              <el-empty v-else description="请选择学校" />
            </div>
          </div>

          <div v-show="activeTab === 'postgrad'" class="tab-content">
            <div class="tab-panel">
              <template v-if="selectedSchool">
                <div class="pg-filter-row">
                  <div class="filter-item">
                    <span>选择年份：</span>
                    <el-select v-model="postgradFilters.year" @change="fetchPostgradInfo">
                      <el-option v-for="y in years" :key="y" :label="`${y}年`" :value="y" />
                    </el-select>
                  </div>
                  <div class="filter-item">
                    <span>招生类型：</span>
                    <el-select v-model="postgradFilters.type" @change="postgradTypeChange">
                      <el-option label="普通复试线" value="normal" />
                      <el-option label="调剂信息" value="adjust" />
                    </el-select>
                  </div>
                </div>

                <div v-show="postgradFilters.type === 'normal'">
                  <h3>{{ selectedSchool.name }}{{ postgradFilters.year }}年硕士研究生招生复试基本分数线</h3>

                  <el-table :data="postgradData" stripe border>
                    <el-table-column prop="discipline_category" label="学科门类" min-width="150" />
                    <el-table-column prop="admission_type" label="招生类型" width="120" />
                    <el-table-column prop="political_score" label="政治" width="80" />
                    <el-table-column prop="foreign_language_score" label="外国语" width="80" />
                    <el-table-column prop="subject1_score" label="专业课1" width="100" />
                    <el-table-column prop="subject2_score" label="专业课2" width="100" />
                    <el-table-column prop="total_score" label="总分" width="80" />
                    <el-table-column prop="remarks" label="备注" min-width="150" />
                  </el-table>
                </div>

                <div v-show="postgradFilters.type === 'adjust'">
                  <h3>{{ selectedSchool.name }}{{ postgradFilters.year }}年研究生调剂相关政策说明</h3>
                  <div class="text-block">
                    <p><strong>1. 调剂基本要求：</strong>考生初试成绩须达到国家线及我校相关门类复试基本线，符合调入专业报考条件。</p>
                    <p><strong>2. 调剂规则：</strong>校内调剂优先，跨院、跨门类调剂需满足专业相近、统考科目相同或相近。</p>
                    <p><strong>3. 专项计划考生调剂：</strong>援藏计划、少干计划、士兵计划仅可在同类专项内进行调剂。</p>
                    <p><strong>4. 调剂流程：</strong>研招网调剂系统开放后，考生填报志愿，招生院系择优遴选、组织复试录取。</p>
                    <p><strong>5. 注意事项：</strong>最终调剂缺额、接收专业、截止时间以各校研招网及各院系官方通知为准。</p>
                  </div>
                </div>
              </template>
              <el-empty v-else description="请选择学校" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { api } from '@/api/client'

const schools = ref<any[]>([])
const selectedSchool = ref<any>(null)
const activeTab = ref('intro')

const provinces = ['北京', '上海', '天津', '重庆', '江苏', '浙江', '广东', '河南', '山东', '山西', '河北', '四川', '湖北', '湖南', '安徽', '福建', '江西', '辽宁', '吉林', '黑龙江', '内蒙古', '广西', '宁夏', '新疆', '西藏', '云南', '贵州', '陕西', '甘肃', '青海', '海南', '香港', '澳门', '台湾']
const years = [2024, 2023, 2022, 2021, 2020]

const filters = reactive({
  name: '',
  type: '',
  level: '',
  province: ''
})

const getSchoolLevel = (level: string | undefined) => {
  if (!level) return ''
  // 提取985、211、双一流
  const levels = []
  if (level.includes('985')) levels.push('985')
  if (level.includes('211')) levels.push('211')
  if (level.includes('双一流')) levels.push('双一流')
  return levels.join(' ')
}

const undergraduateFilters = reactive({
  province: '北京',
  category: '物理类',
  batch: '本科批'
})

const majorFilters = reactive({
  province: '北京',
  year: 2024,
  category: '物理类'
})

const postgradFilters = reactive({
  year: 2025,
  type: 'normal'
})

// 存储可用的类别和批次列表
const availableCategories = ref<string[]>([])
const availableBatches = ref<string[]>([])

// 判断是否显示专业组和选科要求列
const showProfessionalGroupColumns = computed(() => {
  return undergraduateFilters.category === '综合改革'
})

const undergraduateScores = ref<any[]>([])
const majorScores = ref<any[]>([])
const postgradData = ref<any[]>([])

const fetchSchools = async () => {
  try {
    console.log('开始获取学校列表，过滤条件:', filters)
    const params: any = {}
    if (filters.name) params.name = filters.name
    if (filters.type) params.type = filters.type
    if (filters.level) params.level = filters.level
    if (filters.province) params.province = filters.province

    console.log('构建的参数:', params)
    const response = await api.get('/api/schools', params)
    console.log('API响应:', response.data)
    if (response.data.success) {
      schools.value = response.data.data
      console.log('获取到的学校数量:', schools.value.length)
      if (schools.value.length > 0) {
        if (!selectedSchool.value) {
          selectSchool(schools.value[0])
        } else {
          // 检查当前选中的学校是否在新的列表中
          const schoolExists = schools.value.some(school => school.id === selectedSchool.value.id)
          if (!schoolExists) {
            selectedSchool.value = null
          }
        }
      } else {
        // 当列表为空时，清空选中的学校
        selectedSchool.value = null
      }
    }
  } catch (error) {
    console.error('获取学校列表失败:', error)
  }
}

const selectSchool = async (school: any) => {
  selectedSchool.value = school
  activeTab.value = 'intro'
  await Promise.all([
    fetchUndergraduateScores(),
    fetchMajorScores(),
    fetchPostgradInfo()
  ])
}

// 获取省份可用的类别列表
const fetchAvailableCategories = async (province: string) => {
  try {
    const response = await api.get('/api/schools/categories', { province })
    if (response.data.success) {
      availableCategories.value = response.data.data
      // 如果当前选中的类别不在可用列表中，重置为第一个类别
      if (availableCategories.value.length > 0 && !availableCategories.value.includes(undergraduateFilters.category)) {
        undergraduateFilters.category = availableCategories.value[0]
        // 同时更新专业筛选的类别
        majorFilters.category = availableCategories.value[0]
        // 获取新的批次列表
        await fetchAvailableBatches(province, availableCategories.value[0])
      }
    }
  } catch (error) {
    console.error('获取省份可用类别失败:', error)
  }
}

// 获取省份和类别可用的批次列表
const fetchAvailableBatches = async (province: string, category: string) => {
  try {
    const params = {
      province,
      category
    }
    if (selectedSchool.value) {
      params.university_id = selectedSchool.value.id
    }
    const response = await api.get('/api/schools/batches', params)
    if (response.data.success) {
      availableBatches.value = response.data.data
      // 如果当前选中的批次不在可用列表中，重置为第一个批次
      if (availableBatches.value.length > 0 && !availableBatches.value.includes(undergraduateFilters.batch)) {
        undergraduateFilters.batch = availableBatches.value[0]
      }
    }
  } catch (error) {
    console.error('获取省份可用批次失败:', error)
  }
}

const fetchUndergraduateScores = async () => {
  if (!selectedSchool.value) return
  try {
    const params = {
      university_id: selectedSchool.value.id,
      ...undergraduateFilters
    }
    const response = await api.get('/api/undergraduate/admissions', params)
    if (response.data.success) {
      undergraduateScores.value = response.data.data
    }
  } catch (error) {
    console.error('获取本科录取数据失败:', error)
  }
}

const fetchMajorScores = async () => {
  if (!selectedSchool.value) return
  try {
    const params = {
      university_id: selectedSchool.value.id,
      ...majorFilters
    }
    const response = await api.get('/api/undergraduate/admissions', params)
    if (response.data.success) {
      majorScores.value = response.data.data
    }
  } catch (error) {
    console.error('获取本科录取数据失败:', error)
  }
}

const fetchPostgradInfo = async () => {
  if (!selectedSchool.value) return
  try {
    const params = {
      university_id: selectedSchool.value.id,
      year: postgradFilters.year
    }
    const response = await api.get('/api/postgraduate/admissions', params)
    if (response.data.success) {
      postgradData.value = response.data.data
    }
  } catch (error) {
    console.error('获取研究生录取数据失败:', error)
  }
}

const postgradTypeChange = () => {
}

const handleSearch = () => {
  console.log('搜索被触发，搜索条件:', filters)
  fetchSchools()
}

onMounted(async () => {
  fetchSchools()
  // 初始化获取当前省份的可用类别
  await fetchAvailableCategories(undergraduateFilters.province)
  // 初始化获取当前省份和类别的可用批次
  if (availableCategories.value.length > 0) {
    await fetchAvailableBatches(undergraduateFilters.province, availableCategories.value[0])
  }
})
</script>

<style scoped>
.universities-page {
  padding: 30px;
  background: transparent;
  min-height: 100%;
}

.top-search-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
}

.search-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.search-item :deep(.el-input__wrapper) {
    height: 50px;
    border-radius: 8px;
    border: 1px solid #e4e7ed;
    transition: all 0.3s ease;
  }

  .search-item :deep(.el-select) {
    width: 100%;
  }

  .search-item :deep(.el-select__wrapper) {
    height: 50px;
    border-radius: 8px;
    border: 1px solid #e4e7ed;
    transition: all 0.3s ease;
  }

  .search-item :deep(.el-input__wrapper):hover,
  .search-item :deep(.el-select__wrapper):hover {
    border-color: #4096ff;
    box-shadow: 0 0 0 2px rgba(64, 150, 255, 0.2);
  }

  .search-item :deep(.el-input__wrapper.is-focus),
  .search-item :deep(.el-select__wrapper.is-focus) {
    border-color: #4096ff;
    box-shadow: 0 0 0 2px rgba(64, 150, 255, 0.2);
  }

  .search-item :deep(.el-input__inner) {
    height: 50px;
    line-height: 50px;
    font-size: 16px;
    border-radius: 8px;
  }

  .search-item :deep(.el-select__input) {
    height: 48px;
    line-height: 48px;
    font-size: 16px;
  }

  .search-item :deep(.el-select__inner) {
    font-size: 16px;
  }

  .search-item :deep(.el-select-dropdown) {
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border: 1px solid #e4e7ed;
  }

  .search-item :deep(.el-select-dropdown__item) {
    padding: 10px 15px;
    transition: all 0.2s ease;
  }

  .search-item :deep(.el-select-dropdown__item:hover) {
    background-color: #f0f5ff;
    color: #4096ff;
  }

  .search-item :deep(.el-select-dropdown__item.selected) {
    background-color: #e6f7ff;
    color: #4096ff;
  }

.main-container {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 30px;
  min-height: 600px;
  height: auto;
  min-height: 80vh;
}

.school-list-box {
  background: white;
  border-radius: 6px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  height: 80vh;
  min-height: 600px;
  max-height: 800px;
  display: flex;
  flex-direction: column;
}

.school-list-title {
  margin-bottom: 10px;
  font-weight: bold;
  font-size: 16px;
  flex-shrink: 0;
}

.school-list-content {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

/* 滚动条样式 */
.school-list-content::-webkit-scrollbar,
.tab-content::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.school-list-content::-webkit-scrollbar-track,
.tab-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.school-list-content::-webkit-scrollbar-thumb,
.tab-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
  transition: background 0.3s ease;
}

.school-list-content::-webkit-scrollbar-thumb:hover,
.tab-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.school-list-content::-webkit-scrollbar-thumb:active,
.tab-content::-webkit-scrollbar-thumb:active {
  background: #888;
}

.school-item {
  padding: 12px 8px;
  border-bottom: 1px solid #eee;
  font-size: 16px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.school-item:hover {
  background-color: #e8f0fe;
}

.school-item.active {
  background-color: #4096ff;
  color: white;
}

.school-tag {
  font-size: 14px;
  margin-left: 8px;
  color: #999;
}

.school-item.active .school-tag {
  color: white;
}

.content-box {
  background: white;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  overflow: hidden;
  min-height: 600px;
  display: flex;
  flex-direction: column;
}

.tab-nav {
  display: flex;
  border-bottom: 1px solid #eee;
  flex-shrink: 0;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 18px 0;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  background: #eee;
  transition: all 0.2s;
}

.tab-item.active {
  background: #4096ff;
  color: white;
}

.tab-content-container {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.tab-content {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 25px;
  overflow-y: auto;
  transition: opacity 0.3s ease;
}

.tab-content.v-enter-active,
.tab-content.v-leave-active {
  transition: opacity 0.3s ease;
}

.tab-content.v-enter-from,
.tab-content.v-leave-to {
  opacity: 0;
}

.tab-panel h3 {
  font-size: 20px;
  margin: 25px 0 18px;
  color: #333;
  padding-left: 12px;
  border-left: 5px solid #4096ff;
}

.tab-panel h4 {
  font-size: 16px;
  margin: 20px 0 15px;
  color: #666;
}

.intro-box {
  line-height: 1.8;
  font-size: 15px;
  color: #333;
  margin-bottom: 20px;
}

.info-table {
  width: 100%;
  margin: 15px 0;
  border-collapse: collapse;
}

.info-table td {
  padding: 10px 12px;
  border: 1px solid #eee;
  font-size: 15px;
}

.info-table td:first-child {
  width: 140px;
  background: #f7f9fc;
  font-weight: 500;
}

.filter-row {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-bottom: 15px;
}

.pg-filter-row {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-item span {
  font-size: 14px;
  min-width: 80px;
  text-align: right;
}

.filter-item :deep(.el-select) {
  width: 180px;
}

.tip-text {
  font-size: 13px;
  color: #888;
  margin: 8px 0 20px;
}

.text-block {
  line-height: 1.8;
  font-size: 15px;
  margin-bottom: 15px;
}

.text-block p {
  margin-bottom: 10px;
}

a {
  color: #4096ff;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

@media (max-width: 1200px) {
  .top-search-row {
    grid-template-columns: 1fr 1fr;
  }

  .main-container {
    grid-template-columns: 1fr;
    height: auto;
    min-height: 600px;
  }

  .school-list-box {
    max-height: 300px;
    height: auto;
  }
}

@media (max-width: 768px) {
  .top-search-row {
    grid-template-columns: 1fr;
  }

  .tab-item {
    font-size: 18px;
    padding: 15px 0;
  }

  .pg-filter-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .filter-item {
    width: 100%;
  }

  .filter-item :deep(.el-select) {
    flex: 1;
  }
}
</style>
