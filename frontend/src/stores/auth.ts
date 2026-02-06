import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserRole, TeamInfo } from '@/types'
import { authApi } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const userRole = ref<UserRole | null>(null)
  const accessToken = ref<string | null>(null)
  const team = ref<TeamInfo | null>(null)

  const teamName = computed(() => team.value?.name || '')
  const teamId = computed(() => team.value?.id || null)

  function init() {
    const token = localStorage.getItem('access_token')
    const role = localStorage.getItem('user_role') as UserRole | null
    const teamData = localStorage.getItem('team')
    if (token && role) {
      accessToken.value = token
      userRole.value = role
      isAuthenticated.value = true
      if (teamData) {
        try {
          team.value = JSON.parse(teamData)
        } catch {
          team.value = null
        }
      }
    }
  }

  async function login(code: string, role: UserRole) {
    try {
      const response = await authApi.validateCode(code, role)
      accessToken.value = response.data.access_token
      userRole.value = role
      team.value = response.data.team
      isAuthenticated.value = true
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('user_role', role)
      if (response.data.team) {
        localStorage.setItem('team', JSON.stringify(response.data.team))
      }
      return true
    } catch (error) {
      return false
    }
  }

  function logout() {
    accessToken.value = null
    userRole.value = null
    team.value = null
    isAuthenticated.value = false
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_role')
    localStorage.removeItem('team')
  }

  return {
    isAuthenticated,
    userRole,
    accessToken,
    team,
    teamName,
    teamId,
    init,
    login,
    logout,
  }
})
