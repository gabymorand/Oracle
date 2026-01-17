import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { UserRole } from '@/types'
import { authApi } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const userRole = ref<UserRole | null>(null)
  const accessToken = ref<string | null>(null)

  function init() {
    const token = localStorage.getItem('access_token')
    const role = localStorage.getItem('user_role') as UserRole | null
    if (token && role) {
      accessToken.value = token
      userRole.value = role
      isAuthenticated.value = true
    }
  }

  async function login(code: string, role: UserRole) {
    try {
      const response = await authApi.validateCode(code, role)
      accessToken.value = response.data.access_token
      userRole.value = role
      isAuthenticated.value = true
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('user_role', role)
      return true
    } catch (error) {
      return false
    }
  }

  function logout() {
    accessToken.value = null
    userRole.value = null
    isAuthenticated.value = false
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_role')
  }

  return {
    isAuthenticated,
    userRole,
    accessToken,
    init,
    login,
    logout,
  }
})
