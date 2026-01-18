<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 to-gray-900">
    <div class="bg-gray-800 p-8 rounded-lg shadow-xl w-96">
      <div class="text-center mb-8">
        <div class="flex justify-center mb-4">
          <AppLogo size="lg" />
        </div>
        <p class="text-gray-400">Select your role</p>
      </div>

      <div class="space-y-3">
        <button
          @click="selectRole('player')"
          class="w-full bg-gray-700 hover:bg-blue-600 text-white font-semibold py-4 px-6 rounded-lg transition transform hover:scale-105"
        >
          <div class="text-xl mb-1">Player</div>
          <div class="text-sm text-gray-300">View stats and objectives</div>
        </button>

        <button
          @click="selectRole('coach')"
          class="w-full bg-gray-700 hover:bg-green-600 text-white font-semibold py-4 px-6 rounded-lg transition transform hover:scale-105"
        >
          <div class="text-xl mb-1">Coach</div>
          <div class="text-sm text-gray-300">Manage players and add notes</div>
        </button>

        <button
          @click="selectRole('head_coach')"
          class="w-full bg-gray-700 hover:bg-purple-600 text-white font-semibold py-4 px-6 rounded-lg transition transform hover:scale-105"
        >
          <div class="text-xl mb-1">Head Coach</div>
          <div class="text-sm text-gray-300">Full access + draft planning</div>
        </button>
      </div>

      <button
        @click="goBack"
        class="w-full mt-6 text-gray-400 hover:text-white text-sm transition"
      >
        ← Back to login
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { UserRole } from '@/types'
import AppLogo from '@/components/AppLogo.vue'

const router = useRouter()
const authStore = useAuthStore()

async function selectRole(role: UserRole) {
  const code = sessionStorage.getItem('temp_access_code')
  if (!code) {
    router.push('/')
    return
  }

  // If coach role, redirect to coach selection
  if (role === 'coach') {
    router.push('/select-coach')
    return
  }

  const success = await authStore.login(code, role)
  if (success) {
    sessionStorage.removeItem('temp_access_code')
    router.push('/dashboard')
  } else {
    router.push('/')
  }
}

function goBack() {
  sessionStorage.removeItem('temp_access_code')
  router.push('/')
}
</script>
