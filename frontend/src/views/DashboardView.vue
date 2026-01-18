<template>
  <div class="min-h-screen bg-gray-900">
    <AppNavbar />

    <div class="max-w-7xl mx-auto px-4 py-8">
      <div class="mb-6 flex justify-between items-center">
        <h2 class="text-2xl font-semibold">Team Roster</h2>
        <div class="flex gap-2">
          <button
            v-if="authStore.userRole !== 'player'"
            @click="showAddPlayer = true"
            class="bg-green-600 hover:bg-green-700 px-4 py-2 rounded transition"
          >
            Add Player
          </button>
          <router-link
            v-if="authStore.userRole === 'head_coach'"
            to="/coaches"
            class="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded transition"
          >
            Manage Coaches
          </router-link>
          <router-link
            to="/drafts"
            class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded transition"
          >
            Draft Planner
          </router-link>
        </div>
      </div>

      <div v-if="showAddPlayer" class="mb-6 bg-gray-800 rounded-lg p-6">
        <h3 class="text-xl font-semibold mb-4">Add New Player</h3>
        <form @submit.prevent="handleAddPlayer" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-2">Summoner Name</label>
              <input
                v-model="newPlayer.summoner_name"
                type="text"
                class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
                required
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-2">Role</label>
              <select
                v-model="newPlayer.role"
                class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
                required
              >
                <option value="top">Top</option>
                <option value="jungle">Jungle</option>
                <option value="mid">Mid</option>
                <option value="adc">ADC</option>
                <option value="support">Support</option>
              </select>
            </div>
          </div>
          <div class="flex gap-2">
            <button
              type="submit"
              class="bg-green-600 hover:bg-green-700 px-4 py-2 rounded transition"
              :disabled="loading"
            >
              Add
            </button>
            <button
              type="button"
              @click="showAddPlayer = false"
              class="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded transition"
            >
              Cancel
            </button>
          </div>
        </form>
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
import AppNavbar from '@/components/AppNavbar.vue'

const router = useRouter()
const authStore = useAuthStore()

const players = ref<Player[]>([])
const loading = ref(true)
const showAddPlayer = ref(false)
const newPlayer = ref({
  summoner_name: '',
  role: 'top',
})

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

async function handleAddPlayer() {
  loading.value = true
  try {
    const response = await playersApi.create(newPlayer.value)
    players.value.push(response.data)
    showAddPlayer.value = false
    newPlayer.value = { summoner_name: '', role: 'top' }
  } catch (error) {
    console.error('Failed to add player:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPlayers()
})
</script>
