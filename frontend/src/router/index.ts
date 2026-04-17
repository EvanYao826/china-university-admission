import { createRouter, createWebHistory } from 'vue-router'

// 路由组件（使用懒加载）
const UniversitiesView = () => import('@/views/UniversitiesView.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: UniversitiesView,
      meta: {
        title: '院校招生信息查询系统'
      }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      redirect: '/'
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
  next()
})

// 全局后置钩子
router.afterEach((to, from) => {
  console.log(`Navigated from ${from.path} to ${to.path}`)
})

export default router
