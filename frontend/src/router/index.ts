import { createRouter, createWebHistory } from 'vue-router'

// 路由组件（使用懒加载）
const HomePage = () => import('@/views/HomePage.vue')
const CompareView = () => import('@/views/CompareView.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
      meta: {
        title: '首页 - 中国高校录取数据查询系统'
      }
    },
    {
      path: '/universities',
      name: 'universities',
      component: () => import('@/views/UniversitiesView.vue'),
      meta: {
        title: '高校查询 - 中国高校录取数据查询系统'
      }
    },
    {
      path: '/universities/:id',
      name: 'university-detail',
      component: () => import('@/views/UniversityDetail.vue'),
      meta: {
        title: '高校详情 - 中国高校录取数据查询系统'
      }
    },
    {
      path: '/admissions',
      name: 'admissions',
      component: () => import('@/views/AdmissionsView.vue'),
      meta: {
        title: '录取数据 - 中国高校录取数据查询系统'
      }
    },
    {
      path: '/score-match',
      name: 'score-match',
      component: () => import('@/views/ScoreMatchView.vue'),
      meta: {
        title: '分数匹配 - 中国高校录取数据查询系统'
      }
    },
    {
      path: '/statistics',
      name: 'statistics',
      component: () => import('@/views/StatisticsView.vue'),
      meta: {
        title: '数据统计 - 中国高校录取数据查询系统'
      }
    },
    {
      path: '/search',
      name: 'search',
      component: () => import('@/views/SearchView.vue'),
      meta: {
        title: '搜索结果 - 中国高校录取数据查询系统'
      }
    },
    {
      path: '/compare',
      name: 'compare',
      component: CompareView,
      meta: {
        title: '高校对比 - 中国高校录取数据查询系统'
      }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFound.vue'),
      meta: {
        title: '页面未找到 - 中国高校录取数据查询系统'
      }
    }
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title as string
  }

  // 可以在这里添加权限验证等逻辑
  next()
})

// 全局后置钩子
router.afterEach((to, from) => {
  // 可以在这里添加页面访问统计等逻辑
  console.log(`Navigated from ${from.path} to ${to.path}`)
})

export default router