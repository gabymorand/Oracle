<template>
  <div class="min-h-screen bg-gray-900">
    <nav class="bg-gray-800 border-b border-gray-700">
      <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <h1 class="text-2xl font-bold text-blue-400">Oracle</h1>
        <div class="flex items-center gap-4">
          <span class="text-gray-400">{{ authStore.userRole }}</span>
          <button
            @click="handleLogout"
            class="bg-red-600 hover:bg-red-700 px-4 py-2 rounded transition"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 py-8">
      <div class="mb-6 flex justify-between items-center">
        <h2 class="text-2xl font-semibold">Team Roster</h2>
        <router-link
          v-if="authStore.userRole === 'head_coach'"
          to="/drafts"
          class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded transition"
        >
          Draft Planner
        </router-link>
      </div>

      <div v-if="loading" class="text-center py-12">
        <p class="text-gray-400">Loading players...</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="player in players"
          :key="player.id"
          class="bg-gray-800 rounded-lg p-6 hover:bg-gray-750 transition cursor-pointer"
          @click="router.push(`/players/${player.id}`)"
        >
          <div class="flex justify-between items-start mb-2">
            <h3 class="text-xl font-semibold">{{ player.summoner_name }}</h3>
            <span class="text-sm bg-blue-600 px-2 py-1 rounded uppercase">{{ player.role }}</span>
          </div>
          <p class="text-gray-400 text-sm">
            {{ player.riot_accounts.length }} account(s)
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { playersApi } from '@/api'
import type { Player } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const players = ref<Player[]>([])
const loading = ref(true)

async function loadPlayers() {
  try {
    const response = await playersApi.list()
    players.value = response.data
  } catch (error) {
    console.error('Failed to load players:', error)
  } finally {
    loading.value = false
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/')
}

onMounted(() => {
  loadPlayers()
})
</script>
