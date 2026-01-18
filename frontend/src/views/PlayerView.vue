<template>
  <div class="min-h-screen bg-gray-900">
    <AppNavbar :show-back-button="true" />

    <div class="max-w-7xl mx-auto px-4 py-8">
      <div v-if="loading" class="text-center py-12">
        <p class="text-gray-400">Loading player data...</p>
      </div>

      <div v-else-if="player">
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
          <div class="flex justify-between items-start mb-4">
            <div>
              <h1 class="text-3xl font-bold mb-2">{{ player.summoner_name }}</h1>
              <span class="bg-blue-600 px-3 py-1 rounded uppercase text-sm">{{ player.role }}</span>
            </div>
          </div>

          <div class="mt-4">
            <h3 class="text-lg font-semibold mb-2">Riot Accounts</h3>
            <div class="space-y-2">
              <div
                v-for="account in player.riot_accounts"
                :key="account.id"
                class="flex justify-between items-center bg-gray-700 p-3 rounded"
              >
                <div>
                  <span class="font-medium">{{ account.summoner_name }}#{{ account.tag_line }}</span>
                  <span v-if="account.is_main" class="ml-2 text-xs bg-yellow-600 px-2 py-1 rounded">Main</span>
                </div>
                <button
                  v-if="authStore.userRole !== 'player'"
                  @click="refreshStats(account.id)"
                  class="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm transition"
                >
                  Refresh Stats
                </button>
              </div>
            </div>

            <div v-if="authStore.userRole !== 'player' && !showAddAccount" class="mt-3">
              <button
                @click="showAddAccount = true"
                class="bg-green-600 hover:bg-green-700 px-4 py-2 rounded text-sm transition"
              >
                + Add Riot Account
              </button>
            </div>

            <div v-if="showAddAccount" class="mt-3 bg-gray-700 p-4 rounded">
              <h4 class="font-semibold mb-2">Add Riot Account</h4>
              <div class="grid grid-cols-2 gap-2">
                <input
                  v-model="newAccount.summoner_name"
                  type="text"
                  placeholder="Summoner Name"
                  class="px-3 py-2 bg-gray-600 rounded border border-gray-500"
                />
                <input
                  v-model="newAccount.tag_line"
                  type="text"
                  placeholder="Tag (e.g., EUW)"
                  class="px-3 py-2 bg-gray-600 rounded border border-gray-500"
                />
              </div>
              <div class="flex items-center gap-2 mt-2">
                <label class="flex items-center">
                  <input v-model="newAccount.is_main" type="checkbox" class="mr-2" />
                  <span class="text-sm">Main Account</span>
                </label>
              </div>
              <div class="flex gap-2 mt-3">
                <button
                  @click="addRiotAccount"
                  class="bg-green-600 hover:bg-green-700 px-4 py-2 rounded text-sm transition"
                >
                  Add
                </button>
                <button
                  @click="showAddAccount = false"
                  class="bg-gray-600 hover:bg-gray-500 px-4 py-2 rounded text-sm transition"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-gray-800 rounded-lg p-6">
            <h2 class="text-xl font-semibold mb-4">Stats</h2>
            <div v-if="stats" class="space-y-2">
              <div class="flex justify-between">
                <span class="text-gray-400">Games:</span>
                <span>{{ stats.total_games }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Winrate:</span>
                <span>{{ stats.winrate }}%</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">KDA:</span>
                <span>{{ stats.avg_kda }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">CS/min:</span>
                <span>{{ stats.avg_cs_per_min }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Gold/min:</span>
                <span>{{ stats.avg_gold_per_min }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Vision/min:</span>
                <span>{{ stats.avg_vision_score_per_min }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">KP:</span>
                <span>{{ stats.avg_kill_participation }}%</span>
              </div>
            </div>
            <p v-else class="text-gray-400">No stats available</p>
          </div>

          <div class="bg-gray-800 rounded-lg p-6">
            <h2 class="text-xl font-semibold mb-4">Notes & Objectives</h2>
            <div class="space-y-4 mb-4 max-h-96 overflow-y-auto">
              <div
                v-for="note in notes"
                :key="note.id"
                class="bg-gray-700 p-4 rounded"
              >
                <div class="flex justify-between items-start mb-2">
                  <span class="text-xs text-blue-400 uppercase">{{ note.note_type }}</span>
                  <span class="text-xs text-gray-400">{{ note.author_role }}</span>
                </div>
                <p>{{ note.content }}</p>
              </div>
            </div>
            <div v-if="authStore.userRole !== 'player'" class="pt-4 border-t border-gray-700">
              <textarea
                v-model="newNote"
                class="w-full bg-gray-700 rounded p-2 mb-2"
                placeholder="Add note or objective..."
                rows="3"
              ></textarea>
              <div class="flex gap-2">
                <select v-model="noteType" class="bg-gray-700 rounded px-3 py-2">
                  <option value="note">Note</option>
                  <option value="objective">Objective</option>
                </select>
                <button
                  @click="addNote"
                  class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded transition"
                >
                  Add
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { playersApi, statsApi, playerNotesApi, riotAccountsApi } from '@/api'
import type { Player, PlayerStats, PlayerNote } from '@/types'
import AppNavbar from '@/components/AppNavbar.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const player = ref<Player | null>(null)
const stats = ref<PlayerStats | null>(null)
const notes = ref<PlayerNote[]>([])
const loading = ref(true)
const newNote = ref('')
const noteType = ref<'note' | 'objective'>('note')
const showAddAccount = ref(false)
const newAccount = ref({
  summoner_name: '',
  tag_line: '',
  is_main: false,
})

async function loadPlayerData() {
  const playerId = Number(route.params.id)
  try {
    const [playerRes, notesRes] = await Promise.all([
      playersApi.get(playerId),
      playerNotesApi.list(playerId),
    ])
    player.value = playerRes.data
    notes.value = notesRes.data

    try {
      const statsRes = await statsApi.getPlayerStats(playerId)
      stats.value = statsRes.data
    } catch {
      stats.value = null
    }
  } catch (error) {
    console.error('Failed to load player data:', error)
  } finally {
    loading.value = false
  }
}

async function addNote() {
  if (!newNote.value.trim() || !player.value) return

  try {
    await playerNotesApi.create(player.value.id, {
      author_role: authStore.userRole!,
      note_type: noteType.value,
      content: newNote.value,
    })
    newNote.value = ''
    const notesRes = await playerNotesApi.list(player.value.id)
    notes.value = notesRes.data
  } catch (error) {
    console.error('Failed to add note:', error)
  }
}

async function addRiotAccount() {
  if (!newAccount.value.summoner_name || !newAccount.value.tag_line || !player.value) return

  try {
    await riotAccountsApi.create(player.value.id, newAccount.value)
    const playerRes = await playersApi.get(player.value.id)
    player.value = playerRes.data
    showAddAccount.value = false
    newAccount.value = { summoner_name: '', tag_line: '', is_main: false }
  } catch (error) {
    console.error('Failed to add Riot account:', error)
  }
}

async function refreshStats(riotAccountId: number) {
  try {
    await statsApi.refreshStats(riotAccountId)
    if (player.value) {
      const statsRes = await statsApi.getPlayerStats(player.value.id)
      stats.value = statsRes.data
    }
  } catch (error) {
    console.error('Failed to refresh stats:', error)
  }
}

onMounted(() => {
  loadPlayerData()
})
</script>
