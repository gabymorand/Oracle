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
          class="bg-gray-800 rounded-lg p-6 hover:bg-gray-750 transition relative"
        >
          <div
            class="cursor-pointer"
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
          <button
            v-if="authStore.userRole !== 'player'"
            @click.stop="confirmDeletePlayer(player)"
            class="absolute top-2 right-2 text-red-400 hover:text-red-300 transition p-1"
            title="Delete player"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Delete Player Confirmation Modal -->
      <div
        v-if="playerToDelete"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
        @click="playerToDelete = null"
      >
        <div
          class="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4"
          @click.stop
        >
          <h3 class="text-xl font-bold mb-4">Delete Player</h3>
          <p class="text-gray-300 mb-6">
            Are you sure you want to delete <strong>{{ playerToDelete.summoner_name }}</strong>?
            This will also delete all associated Riot accounts and stats. This action cannot be undone.
          </p>
          <div class="flex gap-3 justify-end">
            <button
              @click="playerToDelete = null"
              class="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded transition"
            >
              Cancel
            </button>
            <button
              @click="deletePlayer"
              class="px-4 py-2 bg-red-600 hover:bg-red-700 rounded transition"
            >
              Delete
            </button>
          </div>
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
const playerToDelete = ref<Player | null>(null)
const newPlayer = ref({
  summoner_name: '',
  role: 'top',
})

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

async function handleAddPlayer() {
  loading.value = true
  try {
    const response = await playersApi.create(newPlayer.value)
    players.value.push(response.data)
    showAddPlayer.value = false
    newPlayer.value = { summoner_name: '', role: 'top' }
  } catch (error) {
    console.error('Failed to add player:', error)
    alert('Failed to add player. Please try again.')
  } finally {
    loading.value = false
  }
}

function confirmDeletePlayer(player: Player) {
  playerToDelete.value = player
}

async function deletePlayer() {
  if (!playerToDelete.value) return

  try {
    await playersApi.delete(playerToDelete.value.id)
    players.value = players.value.filter((p) => p.id !== playerToDelete.value!.id)
    playerToDelete.value = null
  } catch (error) {
    console.error('Failed to delete player:', error)
    alert('Failed to delete player. Please try again.')
  }
}

onMounted(() => {
  loadPlayers()
})
</script>
