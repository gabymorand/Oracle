import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/players/:id',
      name: 'player',
      component: () => import('@/views/PlayerView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/drafts',
      name: 'drafts',
      component: () => import('@/views/DraftsView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  authStore.init()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/')
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
