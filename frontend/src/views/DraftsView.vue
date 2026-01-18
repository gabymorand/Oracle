<template>
  <div class="min-h-screen bg-gray-900">
    <AppNavbar :show-back-button="true" />

    <div class="max-w-7xl mx-auto px-4 py-8">
      <div class="mb-6 flex justify-between items-center">
        <h1 class="text-3xl font-bold">Draft Planner</h1>
        <button
          @click="showCreateSeries = true"
          class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded transition flex items-center gap-2"
        >
          <span>+</span> New Series
        </button>
      </div>

      <!-- Stats Summary -->
      <div class="grid grid-cols-4 gap-4 mb-8">
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-2xl font-bold text-blue-400">{{ stats.total }}</div>
          <div class="text-sm text-gray-400">Total Series</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-2xl font-bold text-green-400">{{ stats.wins }}</div>
          <div class="text-sm text-gray-400">Wins</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-2xl font-bold text-red-400">{{ stats.losses }}</div>
          <div class="text-sm text-gray-400">Losses</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-2xl font-bold" :class="stats.winrate >= 50 ? 'text-green-400' : 'text-red-400'">
            {{ stats.winrate }}%
          </div>
          <div class="text-sm text-gray-400">Win Rate</div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <p class="text-gray-400">Loading draft series...</p>
      </div>

      <!-- Series List -->
      <div v-else class="space-y-4">
        <div
          v-for="series in seriesList"
          :key="series.id"
          class="bg-gray-800 rounded-lg p-6 cursor-pointer hover:bg-gray-750 transition"
          @click="openSeries(series)"
        >
          <div class="flex justify-between items-start">
            <div>
              <div class="flex items-center gap-3 mb-2">
                <h3 class="text-xl font-semibold">vs {{ series.opponent_name }}</h3>
                <span class="text-xs bg-gray-700 px-2 py-1 rounded uppercase">
                  {{ series.format }}
                </span>
              </div>
              <p class="text-gray-400 text-sm">{{ formatDate(series.date) }}</p>
            </div>
            <div class="flex items-center gap-4">
              <div class="text-center">
                <div class="text-2xl font-bold">
                  <span class="text-green-400">{{ series.our_score }}</span>
                  <span class="text-gray-500"> - </span>
                  <span class="text-red-400">{{ series.opponent_score }}</span>
                </div>
                <div class="text-xs text-gray-500">{{ series.games_count }} game(s)</div>
              </div>
              <span
                v-if="series.result"
                :class="series.result === 'win' ? 'bg-green-600' : 'bg-red-600'"
                class="px-4 py-2 rounded uppercase text-sm font-semibold"
              >
                {{ series.result }}
              </span>
              <span v-else class="px-4 py-2 bg-gray-600 rounded text-sm">
                In Progress
              </span>
            </div>
          </div>
          <p v-if="series.notes" class="text-gray-400 text-sm mt-3">{{ series.notes }}</p>
        </div>

        <div v-if="seriesList.length === 0" class="text-center py-12">
          <p class="text-gray-400 mb-4">No draft series yet.</p>
          <button
            @click="showCreateSeries = true"
            class="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded transition"
          >
            Create Your First Series
          </button>
        </div>
      </div>
    </div>

    <!-- Create Series Modal -->
    <div v-if="showCreateSeries" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
      <div class="bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-semibold mb-4">New Draft Series</h2>
        <form @submit.prevent="createSeries" class="space-y-4">
          <div>
            <label class="block text-sm mb-2">Date</label>
            <input
              v-model="newSeries.date"
              type="date"
              class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600"
              required
            />
          </div>
          <div>
            <label class="block text-sm mb-2">Opponent</label>
            <input
              v-model="newSeries.opponent_name"
              type="text"
              placeholder="Team name"
              class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600"
              required
            />
          </div>
          <div>
            <label class="block text-sm mb-2">Format</label>
            <div class="flex gap-2">
              <button
                type="button"
                v-for="format in ['bo1', 'bo3', 'bo5']"
                :key="format"
                @click="newSeries.format = format"
                :class="[
                  'flex-1 py-2 rounded uppercase font-semibold transition',
                  newSeries.format === format ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
                ]"
              >
                {{ format }}
              </button>
            </div>
          </div>
          <div>
            <label class="block text-sm mb-2">Notes (optional)</label>
            <textarea
              v-model="newSeries.notes"
              class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600"
              rows="2"
              placeholder="Tournament, stage, etc."
            ></textarea>
          </div>
          <div class="flex gap-3 pt-2">
            <button
              type="button"
              @click="showCreateSeries = false"
              class="flex-1 py-2 bg-gray-700 hover:bg-gray-600 rounded transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="flex-1 py-2 bg-blue-600 hover:bg-blue-700 rounded transition"
            >
              Create Series
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Series Detail Modal -->
    <div v-if="selectedSeries" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 overflow-y-auto">
      <div class="bg-gray-800 rounded-lg p-6 w-full max-w-4xl my-8 mx-4">
        <div class="flex justify-between items-start mb-6">
          <div>
            <h2 class="text-2xl font-bold">vs {{ selectedSeries.opponent_name }}</h2>
            <p class="text-gray-400">{{ formatDate(selectedSeries.date) }} - {{ selectedSeries.format.toUpperCase() }}</p>
          </div>
          <div class="flex items-center gap-4">
            <div class="text-center">
              <div class="text-3xl font-bold">
                <span class="text-green-400">{{ selectedSeries.our_score }}</span>
                <span class="text-gray-500"> - </span>
                <span class="text-red-400">{{ selectedSeries.opponent_score }}</span>
              </div>
            </div>
            <button
              @click="selectedSeries = null"
              class="text-gray-400 hover:text-white text-2xl"
            >
              &times;
            </button>
          </div>
        </div>

        <!-- Games -->
        <div class="space-y-4 mb-6">
          <div
            v-for="game in selectedSeries.games"
            :key="game.id"
            class="bg-gray-700 rounded-lg p-4"
          >
            <div class="flex justify-between items-center mb-3">
              <div class="flex items-center gap-3">
                <span class="text-lg font-semibold">Game {{ game.game_number }}</span>
                <span class="text-xs bg-gray-600 px-2 py-1 rounded">
                  {{ game.blue_side ? 'Blue Side' : 'Red Side' }}
                </span>
              </div>
              <div class="flex items-center gap-2">
                <span
                  v-if="game.result"
                  :class="game.result === 'win' ? 'text-green-400' : 'text-red-400'"
                  class="font-semibold uppercase"
                >
                  {{ game.result }}
                </span>
                <button
                  @click="editGame(game)"
                  class="text-blue-400 hover:text-blue-300 text-sm"
                >
                  Edit
                </button>
                <button
                  @click="deleteGame(game.id)"
                  class="text-red-400 hover:text-red-300 text-sm"
                >
                  Delete
                </button>
              </div>
            </div>

            <!-- Draft Display -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <div class="text-xs text-gray-400 mb-1">Our Bans</div>
                <div class="flex gap-1">
                  <div
                    v-for="(ban, idx) in game.our_bans"
                    :key="idx"
                    class="w-8 h-8 bg-gray-600 rounded flex items-center justify-center text-xs"
                    :title="getChampName(ban)"
                  >
                    <img
                      v-if="ban"
                      :src="getChampIcon(ban)"
                      :alt="getChampName(ban)"
                      class="w-full h-full rounded opacity-50"
                    />
                    <span v-else>-</span>
                  </div>
                </div>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">Enemy Bans</div>
                <div class="flex gap-1">
                  <div
                    v-for="(ban, idx) in game.opponent_bans"
                    :key="idx"
                    class="w-8 h-8 bg-gray-600 rounded flex items-center justify-center text-xs"
                    :title="getChampName(ban)"
                  >
                    <img
                      v-if="ban"
                      :src="getChampIcon(ban)"
                      :alt="getChampName(ban)"
                      class="w-full h-full rounded opacity-50"
                    />
                    <span v-else>-</span>
                  </div>
                </div>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">Our Picks</div>
                <div class="flex gap-1">
                  <div
                    v-for="(pick, idx) in game.our_picks"
                    :key="idx"
                    class="w-8 h-8 bg-gray-600 rounded flex items-center justify-center text-xs"
                    :title="getChampName(pick)"
                  >
                    <img
                      v-if="pick"
                      :src="getChampIcon(pick)"
                      :alt="getChampName(pick)"
                      class="w-full h-full rounded"
                    />
                    <span v-else>-</span>
                  </div>
                </div>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">Enemy Picks</div>
                <div class="flex gap-1">
                  <div
                    v-for="(pick, idx) in game.opponent_picks"
                    :key="idx"
                    class="w-8 h-8 bg-gray-600 rounded flex items-center justify-center text-xs"
                    :title="getChampName(pick)"
                  >
                    <img
                      v-if="pick"
                      :src="getChampIcon(pick)"
                      :alt="getChampName(pick)"
                      class="w-full h-full rounded"
                    />
                    <span v-else>-</span>
                  </div>
                </div>
              </div>
            </div>

            <p v-if="game.notes" class="text-gray-400 text-sm mt-3">{{ game.notes }}</p>
          </div>
        </div>

        <!-- Add Game Button -->
        <div v-if="canAddMoreGames" class="mb-6">
          <button
            @click="showAddGame = true"
            class="w-full py-3 bg-green-600 hover:bg-green-700 rounded transition flex items-center justify-center gap-2"
          >
            <span>+</span> Add Game {{ (selectedSeries.games?.length || 0) + 1 }}
          </button>
        </div>

        <!-- Actions -->
        <div class="flex justify-between">
          <button
            @click="deleteSeries(selectedSeries.id)"
            class="px-4 py-2 bg-red-600 hover:bg-red-700 rounded transition"
          >
            Delete Series
          </button>
          <button
            @click="selectedSeries = null"
            class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>

    <!-- Add Game Modal -->
    <div v-if="showAddGame && selectedSeries" class="fixed inset-0 bg-black/80 flex items-center justify-center z-[60] overflow-y-auto">
      <div class="bg-gray-800 rounded-lg p-6 w-full max-w-2xl my-8 mx-4">
        <h2 class="text-xl font-semibold mb-4">Add Game {{ (selectedSeries.games?.length || 0) + 1 }}</h2>
        <form @submit.prevent="addGame" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm mb-2">Side</label>
              <div class="flex gap-2">
                <button
                  type="button"
                  @click="newGame.blue_side = true"
                  :class="[
                    'flex-1 py-2 rounded transition',
                    newGame.blue_side ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
                  ]"
                >
                  Blue Side
                </button>
                <button
                  type="button"
                  @click="newGame.blue_side = false"
                  :class="[
                    'flex-1 py-2 rounded transition',
                    !newGame.blue_side ? 'bg-red-600' : 'bg-gray-700 hover:bg-gray-600'
                  ]"
                >
                  Red Side
                </button>
              </div>
            </div>
            <div>
              <label class="block text-sm mb-2">Result</label>
              <div class="flex gap-2">
                <button
                  type="button"
                  @click="newGame.result = 'win'"
                  :class="[
                    'flex-1 py-2 rounded transition',
                    newGame.result === 'win' ? 'bg-green-600' : 'bg-gray-700 hover:bg-gray-600'
                  ]"
                >
                  Win
                </button>
                <button
                  type="button"
                  @click="newGame.result = 'loss'"
                  :class="[
                    'flex-1 py-2 rounded transition',
                    newGame.result === 'loss' ? 'bg-red-600' : 'bg-gray-700 hover:bg-gray-600'
                  ]"
                >
                  Loss
                </button>
              </div>
            </div>
          </div>

          <!-- Import Section -->
          <div class="bg-gray-700 rounded-lg p-4">
            <h3 class="font-semibold mb-3">Import Draft</h3>
            <div class="flex gap-2">
              <input
                v-model="importUrl"
                type="url"
                placeholder="https://draftlol.dawe.gg/draft/..."
                class="flex-1 px-3 py-2 bg-gray-600 rounded border border-gray-500"
              />
              <button
                type="button"
                @click="importDraft"
                :disabled="!importUrl || importing"
                class="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ importing ? 'Importing...' : 'Import' }}
              </button>
            </div>
            <p v-if="importError" class="text-xs text-red-400 mt-1">{{ importError }}</p>
            <p v-else-if="importSuccess" class="text-xs text-green-400 mt-1">{{ importSuccess }}</p>
            <p v-else class="text-xs text-gray-400 mt-1">Paste a draftlol.dawe.gg link to auto-fill picks and bans</p>
          </div>

          <!-- Manual Entry -->
          <div class="text-sm text-gray-400 text-center">- or enter manually -</div>

          <!-- Bans -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm mb-2">Our Bans (5)</label>
              <input
                v-model="newGame.our_bans_text"
                type="text"
                placeholder="Champion IDs separated by comma"
                class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 text-sm"
              />
            </div>
            <div>
              <label class="block text-sm mb-2">Enemy Bans (5)</label>
              <input
                v-model="newGame.opponent_bans_text"
                type="text"
                placeholder="Champion IDs separated by comma"
                class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 text-sm"
              />
            </div>
          </div>

          <!-- Picks -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm mb-2">Our Picks (5)</label>
              <input
                v-model="newGame.our_picks_text"
                type="text"
                placeholder="Champion IDs separated by comma"
                class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 text-sm"
              />
            </div>
            <div>
              <label class="block text-sm mb-2">Enemy Picks (5)</label>
              <input
                v-model="newGame.opponent_picks_text"
                type="text"
                placeholder="Champion IDs separated by comma"
                class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 text-sm"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm mb-2">Notes</label>
            <textarea
              v-model="newGame.notes"
              class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600"
              rows="2"
            ></textarea>
          </div>

          <div class="flex gap-3 pt-2">
            <button
              type="button"
              @click="showAddGame = false"
              class="flex-1 py-2 bg-gray-700 hover:bg-gray-600 rounded transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="flex-1 py-2 bg-blue-600 hover:bg-blue-700 rounded transition"
            >
              Add Game
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { apiClient } from '@/api/client'
import AppNavbar from '@/components/AppNavbar.vue'
import { loadChampionData, getChampionName, getChampionIconUrl } from '@/utils/champions'

interface DraftGame {
  id: number
  series_id: number
  game_number: number
  blue_side: boolean
  our_bans: number[]
  opponent_bans: number[]
  our_picks: number[]
  opponent_picks: number[]
  result: string | null
  import_source: string | null
  import_url: string | null
  notes: string | null
  created_at: string
}

interface DraftSeries {
  id: number
  date: string
  opponent_name: string
  format: string
  our_score: number
  opponent_score: number
  result: string | null
  notes: string | null
  created_at: string
  games_count?: number
  games?: DraftGame[]
}

const seriesList = ref<DraftSeries[]>([])
const loading = ref(true)
const showCreateSeries = ref(false)
const selectedSeries = ref<DraftSeries | null>(null)
const showAddGame = ref(false)
const importUrl = ref('')
const importing = ref(false)
const importError = ref('')
const importSuccess = ref('')

const newSeries = ref({
  date: new Date().toISOString().split('T')[0],
  opponent_name: '',
  format: 'bo1',
  notes: '',
})

const newGame = ref({
  blue_side: true,
  result: null as string | null,
  our_bans_text: '',
  opponent_bans_text: '',
  our_picks_text: '',
  opponent_picks_text: '',
  notes: '',
})

const stats = computed(() => {
  const total = seriesList.value.length
  const wins = seriesList.value.filter(s => s.result === 'win').length
  const losses = seriesList.value.filter(s => s.result === 'loss').length
  const winrate = total > 0 ? Math.round((wins / (wins + losses || 1)) * 100) : 0
  return { total, wins, losses, winrate }
})

const canAddMoreGames = computed(() => {
  if (!selectedSeries.value) return false
  const maxGames = { bo1: 1, bo3: 3, bo5: 5 }[selectedSeries.value.format] || 1
  return (selectedSeries.value.games?.length || 0) < maxGames
})

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

function getChampName(id: number): string {
  return getChampionName(id)
}

function getChampIcon(id: number): string {
  return getChampionIconUrl(id)
}

function parseChampionIds(text: string): number[] {
  if (!text.trim()) return []
  return text.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n))
}

async function loadSeriesList() {
  try {
    loading.value = true
    const response = await apiClient.get('/api/v1/draft-series')
    seriesList.value = response.data
  } catch (error) {
    console.error('Failed to load draft series:', error)
  } finally {
    loading.value = false
  }
}

async function createSeries() {
  try {
    await apiClient.post('/api/v1/draft-series', newSeries.value)
    showCreateSeries.value = false
    newSeries.value = {
      date: new Date().toISOString().split('T')[0],
      opponent_name: '',
      format: 'bo1',
      notes: '',
    }
    await loadSeriesList()
  } catch (error) {
    console.error('Failed to create series:', error)
  }
}

async function openSeries(series: DraftSeries) {
  try {
    const response = await apiClient.get(`/api/v1/draft-series/${series.id}`)
    selectedSeries.value = response.data
  } catch (error) {
    console.error('Failed to load series details:', error)
  }
}

async function deleteSeries(id: number) {
  if (!confirm('Delete this series and all its games?')) return
  try {
    await apiClient.delete(`/api/v1/draft-series/${id}`)
    selectedSeries.value = null
    await loadSeriesList()
  } catch (error) {
    console.error('Failed to delete series:', error)
  }
}

async function addGame() {
  if (!selectedSeries.value) return

  const gameData = {
    game_number: (selectedSeries.value.games?.length || 0) + 1,
    blue_side: newGame.value.blue_side,
    our_bans: parseChampionIds(newGame.value.our_bans_text),
    opponent_bans: parseChampionIds(newGame.value.opponent_bans_text),
    our_picks: parseChampionIds(newGame.value.our_picks_text),
    opponent_picks: parseChampionIds(newGame.value.opponent_picks_text),
    result: newGame.value.result,
    import_source: importUrl.value ? 'url' : 'manual',
    import_url: importUrl.value || null,
    notes: newGame.value.notes,
  }

  try {
    await apiClient.post(`/api/v1/draft-series/${selectedSeries.value.id}/games`, gameData)
    showAddGame.value = false
    // Reset form
    newGame.value = {
      blue_side: true,
      result: null,
      our_bans_text: '',
      opponent_bans_text: '',
      our_picks_text: '',
      opponent_picks_text: '',
      notes: '',
    }
    importUrl.value = ''
    importError.value = ''
    importSuccess.value = ''
    // Reload series
    await openSeries(selectedSeries.value)
    await loadSeriesList()
  } catch (error) {
    console.error('Failed to add game:', error)
  }
}

function editGame(game: DraftGame) {
  // TODO: Implement edit functionality
  console.log('Edit game:', game)
}

async function importDraft() {
  if (!importUrl.value) return

  importing.value = true
  importError.value = ''
  importSuccess.value = ''

  try {
    const response = await apiClient.post('/api/v1/draft-series/import', {
      url: importUrl.value,
      is_blue_side: newGame.value.blue_side,
    })

    if (response.data.success && response.data.data) {
      const data = response.data.data
      // Fill in the form with imported data
      newGame.value.our_bans_text = data.our_bans.join(', ')
      newGame.value.opponent_bans_text = data.opponent_bans.join(', ')
      newGame.value.our_picks_text = data.our_picks.join(', ')
      newGame.value.opponent_picks_text = data.opponent_picks.join(', ')
      importSuccess.value = response.data.message
    } else {
      importError.value = response.data.message || 'Failed to import draft'
    }
  } catch (error: any) {
    console.error('Failed to import draft:', error)
    importError.value = error.response?.data?.detail || 'Failed to import draft from URL'
  } finally {
    importing.value = false
  }
}

async function deleteGame(gameId: number) {
  if (!selectedSeries.value) return
  if (!confirm('Delete this game?')) return

  try {
    await apiClient.delete(`/api/v1/draft-series/${selectedSeries.value.id}/games/${gameId}`)
    await openSeries(selectedSeries.value)
    await loadSeriesList()
  } catch (error) {
    console.error('Failed to delete game:', error)
  }
}

onMounted(async () => {
  await loadChampionData()
  await loadSeriesList()
})
</script>
