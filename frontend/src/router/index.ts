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
      path: '/select-role',
      name: 'select-role',
      component: () => import('@/views/RoleSelectionView.vue'),
    },
    {
      path: '/select-coach',
      name: 'select-coach',
      component: () => import('@/views/CoachSelectionView.vue'),
    },
    {
      path: '/select-player',
      name: 'select-player',
      component: () => import('@/views/PlayerSelectionView.vue'),
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
    {
      path: '/sponsors',
      name: 'sponsors',
      component: () => import('@/views/SponsorsView.vue'),
    },
    {
      path: '/coaches',
      name: 'coaches',
      component: () => import('@/views/CoachesManagementView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/planning',
      redirect: { path: '/calendar', query: { tab: 'planning' } },
    },
    {
      path: '/calendar',
      name: 'calendar',
      component: () => import('@/views/CalendarView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/scrims',
      name: 'scrims',
      component: () => import('@/views/ScrimsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/tier-list',
      name: 'tier-list',
      component: () => import('@/views/TierListView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/analytics',
      name: 'analytics',
      component: () => import('@/views/AnalyticsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/soloq',
      name: 'soloq-activity',
      component: () => import('@/views/SoloQActivityView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('@/views/AdminView.vue'),
      meta: { isAdmin: true },
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  authStore.init()

  // Skip auth check for admin routes (admin has its own auth)
  if (to.meta.isAdmin) {
    next()
    return
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/')
  } else if ((to.name === 'login' || to.name === 'select-role') && authStore.isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
