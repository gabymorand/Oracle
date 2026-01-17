<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 to-gray-900">
    <div class="bg-gray-800 p-8 rounded-lg shadow-xl w-96">
      <h1 class="text-3xl font-bold text-center mb-6 text-blue-400">Oracle</h1>
      <p class="text-gray-400 text-center mb-6">League of Legends Coaching Platform</p>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-2">Access Code</label>
          <input
            v-model="code"
            type="password"
            class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            placeholder="Enter access code"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-2">Role</label>
          <select
            v-model="role"
            class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            required
          >
            <option value="player">Player</option>
            <option value="coach">Coach</option>
            <option value="head_coach">Head Coach</option>
          </select>
        </div>

        <button
          type="submit"
          class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded transition"
          :disabled="loading"
        >
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>

        <p v-if="error" class="text-red-400 text-sm text-center">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { UserRole } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const code = ref('')
const role = ref<UserRole>('player')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''

  const success = await authStore.login(code.value, role.value)

  if (success) {
    router.push('/dashboard')
  } else {
    error.value = 'Invalid access code'
  }

  loading.value = false
}
</script>
