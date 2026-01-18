<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 to-gray-900">
    <div class="bg-gray-800 p-8 rounded-lg shadow-xl w-96">
      <div class="flex justify-center mb-6">
        <AppLogo size="lg" />
      </div>
      <p class="text-gray-400 text-center mb-6">Oracle Coaching Platform</p>

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

        <button
          type="submit"
          class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded transition"
          :disabled="loading"
        >
          {{ loading ? 'Verifying...' : 'Continue' }}
        </button>

        <p v-if="error" class="text-red-400 text-sm text-center">{{ error }}</p>
      </form>

      <div class="mt-6 pt-6 border-t border-gray-700 text-center">
        <router-link
          to="/sponsors"
          class="text-sm text-blue-400 hover:text-blue-300 transition"
        >
          View Team Highlights →
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api'
import AppLogo from '@/components/AppLogo.vue'

const router = useRouter()

const code = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''

  try {
    // Just validate the code with a temporary role
    await authApi.validateCode(code.value, 'player')
    // Store the code temporarily and redirect to role selection
    sessionStorage.setItem('temp_access_code', code.value)
    router.push('/select-role')
  } catch {
    error.value = 'Invalid access code'
  } finally {
    loading.value = false
  }
}
</script>
