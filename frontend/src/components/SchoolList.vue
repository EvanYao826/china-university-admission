<template>
  <div class="school-list">
    <!-- 筛选工具栏 -->
    <div class="filter-toolbar">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-select
            v-model="filters.province"
            placeholder="选择省份"
            clearable
            @change="handleFilterChange"
          >
            <el-option
              v-for="province in filterOptions.provinces"
              :key="province"
              :label="province"
              :value="province"
            />
          </el-select>
        </el-col>

        <el-col :span="6">
          <el-select
            v-model="filters.type"
            placeholder="选择类型"
            clearable
            @change="handleFilterChange"
          >
            <el-option
              v-for="type in filterOptions.types"
              :key="type"
              :label="type"
              :value="type"
            />
          </el-select>
        </el-col>

        <el-col :span="6">
          <el-select
            v-model="filters.level"
            placeholder="选择层次"
            clearable
            @change="handleFilterChange"
          >
            <el-option
              v-for="level in filterOptions.levels"
              :key="level"
              :label="level"
              :value="level"
            />
          </el-select>
        </el-col>

        <el-col :span="6">
          <div class="filter-actions">
            <el-button @click="resetFilters" :icon="Refresh">重置</el-button>
            <el-button
              type="primary"
              @click="refreshData"
              :icon="Search"
              :loading="loading"
            >
              搜索
            </el-button>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 排序和显示选项 -->
    <div class="list-options">
      <div class="sort-options">
        <span class="sort-label">排序：</span>
        <el-select
          v-model="sortBy"
          placeholder="选择排序字段"
          size="small"
          @change="handleSortChange"
        >
          <el-option label="名称" value="name" />
          <el-option label="省份" value="province" />
          <el-option label="类型" value="type" />
          <el-option label="层次" value="level" />
        </el-select>

        <el-radio-group
          v-model="sortOrder"
          size="small"
          @change="handleSortChange"
        >
          <el-radio-button label="asc">升序</el-radio-button>
          <el-radio-button label="desc">降序</el-radio-button>
        </el-radio-group>
      </div>

      <div class="display-options">
        <span class="display-label">每页显示：</span>
        <el-select
          v-model="pageSize"
          size="small"
          @change="handlePageSizeChange"
        >
          <el-option label="20条" :value="20" />
          <el-option label="50条" :value="50" />
          <el-option label="100条" :value="100" />
        </el-select>
      </div>
    </div>

    <!-- 高校列表 -->
    <div class="schools-container">
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>

      <div v-else-if="schools.length === 0" class="empty-container">
        <el-empty description="暂无高校数据" />
      </div>

      <div v-else class="schools-grid">
        <el-card
          v-for="school in schools"
          :key="school.id"
          class="school-card"
          shadow="hover"
          @click="handleSchoolClick(school)"
        >
          <div class="school-card-header">
            <h3 class="school-name">{{ school.name }}</h3>
            <div class="school-tags">
              <el-tag
                :type="getLevelTagType(school.level)"
                size="small"
                class="level-tag"
              >
                {{ school.level }}
              </el-tag>
              <el-tag type="info" size="small" class="type-tag">
                {{ school.type }}
              </el-tag>
            </div>
          </div>

          <div class="school-info">
            <div class="info-item">
              <el-icon><Location /></el-icon>
              <span>{{ school.province }} {{ school.city }}</span>
            </div>

            <div v-if="school.website" class="info-item">
              <el-icon><Link /></el-icon>
              <a
                :href="school.website"
                target="_blank"
                @click.stop
                class="website-link"
              >
                {{ school.website }}
              </a>
            </div>

            <div v-if="school.description" class="school-desc">
              <p>{{ truncateDescription(school.description) }}</p>
            </div>
          </div>

          <div class="school-actions">
            <el-button
              type="primary"
              size="small"
              @click.stop="handleSchoolClick(school)"
            >
              查看详情
            </el-button>
            <el-button
              type="info"
              size="small"
              @click.stop="handleAddToCompare(school)"
            >
              加入对比
            </el-button>
            <el-button
              type="success"
              size="small"
              @click.stop="handleViewAdmissions(school)"
            >
              录取数据
            </el-button>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-container" v-if="total > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handlePageSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/client'
import {
  Refresh,
  Search,
  Location,
  Link
} from '@element-plus/icons-vue'
import type { University, FilterOptions } from '@/types'

interface Props {
  showFilters?: boolean
  limit?: number
}

const props = withDefaults(defineProps<Props>(), {
  showFilters: true,
  limit: 20
})

const emit = defineEmits<{
  'school-click': [school: University]
  'add-to-compare': [school: University]
}>()

const router = useRouter()

// 数据状态
const schools = ref<University[]>([])
const loading = ref(false)
const total = ref(0)

// 筛选条件
const filters = ref({
  province: '',
  type: '',
  level: ''
})

// 排序条件
const sortBy = ref('name')
const sortOrder = ref('asc')

// 分页
const currentPage = ref(1)
const pageSize = ref(props.limit)

// 筛选选项
const filterOptions = ref<FilterOptions>({
  provinces: [],
  types: [],
  levels: [],
  years: [],
  categories: [],
  batches: []
})

// 获取筛选选项
const fetchFilterOptions = async () => {
  try {
    const response = await api.universities.getFilterOptions()
    if (response.data.success) {
      filterOptions.value = response.data.data
    }
  } catch (error) {
    console.error('Failed to fetch filter options:', error)
  }
}

// 获取高校数据
const fetchSchools = async () => {
  loading.value = true
  try {
    const params = {
      ...filters.value,
      page: currentPage.value,
      limit: pageSize.value,
      sortBy: sortBy.value,
      sortOrder: sortOrder.value
    }

    const response = await api.universities.getUniversities(params)
    if (response.data.success) {
      schools.value = response.data.data
      total.value = response.data.pagination?.total || 0
    }
  } catch (error) {
    console.error('Failed to fetch schools:', error)
    schools.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 处理筛选变化
const handleFilterChange = () => {
  currentPage.value = 1
  fetchSchools()
}

// 处理排序变化
const handleSortChange = () => {
  fetchSchools()
}

// 处理分页变化
const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchSchools()
}

// 处理每页显示数量变化
const handlePageSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchSchools()
}

// 重置筛选条件
const resetFilters = () => {
  filters.value = {
    province: '',
    type: '',
    level: ''
  }
  currentPage.value = 1
  fetchSchools()
}

// 刷新数据
const refreshData = () => {
  fetchSchools()
}

// 处理高校点击
const handleSchoolClick = (school: University) => {
  emit('school-click', school)
  router.push(`/universities/${school.id}`)
}

// 处理添加到对比
const handleAddToCompare = (school: University) => {
  emit('add-to-compare', school)
  ElMessage.success(`已添加 ${school.name} 到对比列表`)
}

// 处理查看录取数据
const handleViewAdmissions = (school: University) => {
  router.push({
    path: '/admissions',
    query: { universityId: school.id }
  })
}

// 获取层次标签类型
const getLevelTagType = (level: string) => {
  switch (level) {
    case '985':
      return 'danger'
    case '211':
      return 'warning'
    case '双一流':
      return 'success'
    default:
      return 'info'
  }
}

// 截断描述文本
const truncateDescription = (desc: string, maxLength = 100) => {
  if (desc.length <= maxLength) return desc
  return desc.substring(0, maxLength) + '...'
}

// 组件挂载时获取数据
onMounted(() => {
  fetchFilterOptions()
  fetchSchools()
})

// 监听 props 变化
watch(() => props.limit, (newLimit) => {
  pageSize.value = newLimit
  fetchSchools()
})
</script>

<style scoped>
.school-list {
  padding: 20px 0;
}

.filter-toolbar {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.filter-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.list-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.sort-options {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sort-label,
.display-label {
  color: #606266;
  font-size: 14px;
}

.display-options {
  display: flex;
  align-items: center;
  gap: 10px;
}

.schools-container {
  min-height: 400px;
}

.loading-container {
  padding: 40px;
  background: white;
  border-radius: 8px;
}

.empty-container {
  padding: 80px 0;
  background: white;
  border-radius: 8px;
}

.schools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.school-card {
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  border: none;
}

.school-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1) !important;
}

.school-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.school-name {
  font-size: 1.1rem;
  font-weight: bold;
  color: #2d3748;
  margin: 0;
  flex: 1;
  line-height: 1.4;
}

.school-tags {
  display: flex;
  gap: 5px;
  margin-left: 10px;
}

.level-tag,
.type-tag {
  font-size: 12px;
}

.school-info {
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  color: #718096;
  font-size: 14px;
}

.info-item .el-icon {
  color: #a0aec0;
  flex-shrink: 0;
}

.website-link {
  color: #667eea;
  text-decoration: none;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.website-link:hover {
  text-decoration: underline;
}

.school-desc {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e9ecef;
}

.school-desc p {
  color: #718096;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

.school-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.pagination-container {
  margin-top: 30px;
  display: flex;
  justify-content: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .schools-grid {
    grid-template-columns: 1fr;
  }

  .list-options {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .sort-options,
  .display-options {
    width: 100%;
    justify-content: space-between;
  }

  .filter-toolbar .el-col {
    margin-bottom: 15px;
  }

  .filter-toolbar .el-col:last-child {
    margin-bottom: 0;
  }

  .filter-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 480px) {
  .school-card-header {
    flex-direction: column;
    gap: 10px;
  }

  .school-tags {
    margin-left: 0;
    align-self: flex-start;
  }

  .school-actions {
    flex-direction: column;
  }

  .school-actions .el-button {
    width: 100%;
  }
}
</style>