<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 to-gray-900">
    <div class="bg-gray-800 p-8 rounded-lg shadow-xl w-[500px]">
      <div class="text-center mb-8">
        <div class="flex justify-center mb-4">
          <AppLogo size="lg" />
        </div>
        <p class="text-gray-400">Select your player profile</p>
      </div>

      <div v-if="loading" class="text-center py-8">
        <p class="text-gray-400">Loading players...</p>
      </div>

      <div v-else>
        <div class="space-y-3 mb-6">
          <button
            v-for="player in players"
            :key="player.id"
            @click="selectPlayer(player)"
            class="w-full bg-gray-700 hover:bg-blue-600 text-white font-semibold py-4 px-6 rounded-lg transition transform hover:scale-105 text-left flex items-center gap-4"
          >
            <span
              class="w-3 h-3 rounded-full"
              :class="getRoleColor(player.role)"
            ></span>
            <div class="flex-1">
              <div class="text-xl mb-1">{{ player.summoner_name }}</div>
              <div class="text-sm text-gray-300 uppercase">{{ player.role }}</div>
            </div>
          </button>
        </div>

        <div v-if="players.length === 0" class="text-center py-8">
          <p class="text-gray-400 mb-4">No player profiles available yet.</p>
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
import { playersApi } from '@/api'
import type { Player } from '@/types'
import AppLogo from '@/components/AppLogo.vue'

const router = useRouter()
const authStore = useAuthStore()

const players = ref<Player[]>([])
const loading = ref(true)

function getRoleColor(role: string): string {
  const colors: Record<string, string> = {
    top: 'bg-red-400',
    jungle: 'bg-green-400',
    mid: 'bg-blue-400',
    adc: 'bg-yellow-400',
    support: 'bg-purple-400'
  }
  return colors[role.toLowerCase()] || 'bg-gray-400'
}

async function loadPlayers() {
  try {
    const response = await playersApi.getPlayers()
    players.value = response.data
  } catch (error) {
    console.error('Failed to load players:', error)
  } finally {
    loading.value = false
  }
}

async function selectPlayer(player: Player) {
  const code = sessionStorage.getItem('temp_access_code')
  if (!code) {
    router.push('/')
    return
  }

  // Store player ID in sessionStorage for later use
  sessionStorage.setItem('selected_player_id', player.id.toString())
  sessionStorage.setItem('selected_player_name', player.summoner_name)

  const success = await authStore.login(code, 'player')
  if (success) {
    sessionStorage.removeItem('temp_access_code')
    // Redirect to player's own profile
    router.push(`/players/${player.id}`)
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
  loadPlayers()
})
</script>
