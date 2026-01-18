<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 to-gray-900">
    <div class="bg-gray-800 p-8 rounded-lg shadow-xl w-[500px]">
      <div class="text-center mb-8">
        <div class="flex justify-center mb-4">
          <AppLogo size="lg" />
        </div>
        <p class="text-gray-400">Select your coach profile</p>
      </div>

      <div v-if="loading" class="text-center py-8">
        <p class="text-gray-400">Loading coaches...</p>
      </div>

      <div v-else>
        <div class="space-y-3 mb-6">
          <button
            v-for="coach in coaches"
            :key="coach.id"
            @click="selectCoach(coach)"
            class="w-full bg-gray-700 hover:bg-green-600 text-white font-semibold py-4 px-6 rounded-lg transition transform hover:scale-105 text-left"
          >
            <div class="text-xl mb-1">{{ coach.name }}</div>
            <div v-if="coach.role" class="text-sm text-gray-300 uppercase">{{ coach.role }} Coach</div>
            <div v-else class="text-sm text-gray-300">Head Coach</div>
          </button>
        </div>

        <div v-if="coaches.length === 0" class="text-center py-8">
          <p class="text-gray-400 mb-4">No coach profiles available yet.</p>
          <p class="text-sm text-gray-500">Contact the head coach to create one.</p>
        </div>
      </div>

      <button
        @click="goBack"
        class="w-full mt-6 text-gray-400 hover:text-white text-sm transition"
      >
        ← Back to role selection
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { coachesApi } from '@/api'
import type { Coach } from '@/types'
import AppLogo from '@/components/AppLogo.vue'

const router = useRouter()
const authStore = useAuthStore()

const coaches = ref<Coach[]>([])
const loading = ref(true)

async function loadCoaches() {
  try {
    const response = await coachesApi.list()
    coaches.value = response.data
  } catch (error) {
    console.error('Failed to load coaches:', error)
  } finally {
    loading.value = false
  }
}

async function selectCoach(coach: Coach) {
  const code = sessionStorage.getItem('temp_access_code')
  if (!code) {
    router.push('/')
    return
  }

  // Store coach ID in sessionStorage for later use
  sessionStorage.setItem('selected_coach_id', coach.id.toString())
  sessionStorage.setItem('selected_coach_name', coach.name)

  const success = await authStore.login(code, 'coach')
  if (success) {
    sessionStorage.removeItem('temp_access_code')
    router.push('/dashboard')
  } else {
    router.push('/')
  }
}

function goBack() {
  router.push('/select-role')
}

onMounted(() => {
  const code = sessionStorage.getItem('temp_access_code')
  if (!code) {
    router.push('/')
    return
  }
  loadCoaches()
})
</script>
