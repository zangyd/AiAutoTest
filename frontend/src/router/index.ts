import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/auth/Login.vue'),
    meta: {
      title: '登录',
      requiresAuth: false
    }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/dashboard/Index.vue'),
    meta: {
      title: '仪表盘',
      requiresAuth: true
    }
  },
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
  document.title = `${to.meta.title} - 自动化测试平台`

  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('token')
    if (!token) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
  }
  next()
})

export default router 