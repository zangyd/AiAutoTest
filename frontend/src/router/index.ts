import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/store/modules/user'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: {
      title: '登录',
      requiresAuth: false
    }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: {
      title: '仪表盘',
      requiresAuth: true
    }
  },
  /* 暂时注释未实现的路由
  {
    path: '/projects',
    name: 'Projects',
    component: () => import('../views/projects/Index.vue'),
    meta: {
      title: '项目管理',
      requiresAuth: true
    }
  },
  {
    path: '/test-plans',
    name: 'TestPlans',
    component: () => import('../views/test-plans/Index.vue'),
    meta: {
      title: '测试计划',
      requiresAuth: true
    }
  },
  {
    path: '/test-cases',
    name: 'TestCases',
    component: () => import('../views/test-cases/Index.vue'),
    meta: {
      title: '测试用例',
      requiresAuth: true
    }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('../views/reports/Index.vue'),
    meta: {
      title: '测试报告',
      requiresAuth: true
    }
  },
  */
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/error/404.vue'),
    meta: {
      title: '404',
      requiresAuth: false
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title} - AI自动化测试平台`

  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    const userStore = useUserStore()
    if (!userStore.isLoggedIn) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
  }
  
  // 如果已登录且访问登录页，重定向到首页
  if (to.name === 'Login') {
    const userStore = useUserStore()
    if (userStore.isLoggedIn) {
      next({ name: 'Dashboard' })
      return
    }
  }
  
  next()
})

export default router 