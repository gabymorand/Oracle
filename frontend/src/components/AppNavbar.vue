<template>
  <nav class="bg-gray-800 border-b border-gray-700">
    <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
      <div class="flex items-center gap-6">
        <router-link to="/dashboard">
          <AppLogo size="sm" />
        </router-link>
        <div v-if="showBackButton" class="flex items-center gap-4">
          <span class="text-gray-500">|</span>
          <button @click="router.back()" class="text-blue-400 hover:underline">
            ← Back
          </button>
        </div>
      </div>
      <div class="flex items-center gap-4">
        <span class="text-gray-400 text-sm">{{ authStore.userRole }}</span>
        <button
          @click="handleLogout"
          class="bg-red-600 hover:bg-red-700 px-4 py-2 rounded transition text-sm"
        >
          Logout
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppLogo from './AppLogo.vue'

interface Props {
  showBackButton?: boolean
}

withDefaults(defineProps<Props>(), {
  showBackButton: false,
})

const router = useRouter()
const authStore = useAuthStore()

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>
