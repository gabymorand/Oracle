<template>
  <div class="min-h-screen bg-gray-900">
    <nav class="bg-gray-800 border-b border-gray-700">
      <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <button @click="router.push('/dashboard')" class="text-blue-400 hover:underline">
          ← Back to Dashboard
        </button>
        <button @click="handleLogout" class="bg-red-600 hover:bg-red-700 px-4 py-2 rounded transition">
          Logout
        </button>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 py-8">
      <div v-if="loading" class="text-center py-12">
        <p class="text-gray-400">Loading player data...</p>
      </div>

      <div v-else-if="player">
        <div class="bg-gray-800 rounded-lg p-6 mb-6">
          <div class="flex justify-between items-start">
            <div>
              <h1 class="text-3xl font-bold mb-2">{{ player.summoner_name }}</h1>
              <span class="bg-blue-600 px-3 py-1 rounded uppercase text-sm">{{ player.role }}</span>
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
import { playersApi, statsApi, playerNotesApi } from '@/api'
import type { Player, PlayerStats, PlayerNote } from '@/types'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const player = ref<Player | null>(null)
const stats = ref<PlayerStats | null>(null)
const notes = ref<PlayerNote[]>([])
const loading = ref(true)
const newNote = ref('')
const noteType = ref<'note' | 'objective'>('note')

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

function handleLogout() {
  authStore.logout()
  router.push('/')
}

onMounted(() => {
  loadPlayerData()
})
</script>
