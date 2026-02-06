<template>
  <div class="min-h-screen bg-gray-900">
    <AppNavbar :show-back-button="true" />

    <div class="max-w-[1800px] mx-auto px-4 py-6">
      <!-- Header with player selector -->
      <div class="mb-6 flex justify-between items-center">
        <h1 class="text-2xl font-bold">Tier List</h1>

        <div class="flex items-center gap-4">
          <label class="text-gray-400">Joueur:</label>
          <select
            v-model="selectedPlayerId"
            @change="loadTierList"
            class="bg-gray-700 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none min-w-[200px]"
          >
            <option v-for="player in players" :key="player.id" :value="player.id">
              {{ player.summoner_name }} ({{ player.role.toUpperCase() }})
            </option>
          </select>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12 text-gray-400">
        Chargement...
      </div>

      <!-- Main layout: Tier List + Champion Pool -->
      <div v-else class="flex gap-6">
        <!-- Left: Tier List -->
        <div class="flex-1 space-y-3">
          <div
            v-for="tier in tiers"
            :key="tier.level"
            class="bg-gray-800 rounded-lg overflow-hidden"
            @dragover.prevent
            @dragenter.prevent="dragEnterTier(tier.level)"
            @dragleave="dragLeaveTier(tier.level)"
            @drop="dropOnTier(tier.level, $event)"
            :class="{ 'ring-2 ring-blue-500': dragOverTier === tier.level }"
          >
            <!-- Tier header -->
            <div
              :class="[
                'px-4 py-2 font-bold flex items-center gap-3',
                tier.bgColor,
              ]"
            >
              <span class="text-2xl w-8">{{ tier.level }}</span>
              <span class="text-sm opacity-75">{{ tier.label }}</span>
              <span class="ml-auto text-sm opacity-75">
                {{ getChampionsForTier(tier.level).length }}
              </span>
            </div>

            <!-- Tier content - horizontal scrollable -->
            <div class="p-3 min-h-[80px]">
              <div
                v-if="getChampionsForTier(tier.level).length === 0"
                class="text-gray-500 text-sm py-2 text-center"
              >
                Glissez des champions ici
              </div>
              <div v-else class="flex flex-wrap gap-2">
                <div
                  v-for="champ in getChampionsForTier(tier.level)"
                  :key="champ.champion_id"
                  class="relative group cursor-pointer"
                  draggable="true"
                  @dragstart="startDrag(champ.champion_id, $event)"
                  @click="removeFromTier(champ.champion_id)"
                >
                  <!-- Champion icon with stats overlay -->
                  <div class="relative">
                    <img
                      :src="getChampionIconUrl(champ.champion_id)"
                      :alt="champ.champion_name"
                      class="w-14 h-14 rounded border-2 transition"
                      :class="getTierBorderColor(tier.level)"
                    />
                    <!-- Stats badge if played -->
                    <div
                      v-if="champ.games_played > 0"
                      class="absolute -bottom-1 left-1/2 transform -translate-x-1/2 text-[10px] font-bold px-1 rounded whitespace-nowrap"
                      :class="champ.winrate >= 50 ? 'bg-green-600' : 'bg-red-600'"
                    >
                      {{ champ.wins }}W/{{ champ.losses }}L
                    </div>
                    <!-- Performance score badge -->
                    <div
                      v-if="champ.games_played > 0"
                      class="absolute -top-1 -right-1 text-[10px] font-bold px-1 rounded-full"
                      :class="getScoreBadgeColor(champ.performance_score)"
                    >
                      {{ champ.performance_score }}
                    </div>
                    <!-- Remove indicator on hover -->
                    <div
                      class="absolute inset-0 bg-red-600/60 rounded opacity-0 group-hover:opacity-100 transition flex items-center justify-center"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-6 w-6"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M6 18L18 6M6 6l12 12"
                        />
                      </svg>
                    </div>
                  </div>
                  <!-- Tooltip on hover -->
                  <div
                    class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 bg-gray-900 rounded-lg p-2 shadow-xl z-20 w-40 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"
                  >
                    <div class="text-sm font-semibold text-center mb-1">
                      {{ getChampionDisplayName(champ.champion_id) }}
                    </div>
                    <div v-if="champ.games_played > 0" class="text-xs space-y-0.5">
                      <div class="flex justify-between">
                        <span class="text-gray-400">Games:</span>
                        <span>{{ champ.games_played }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-400">WR:</span>
                        <span :class="champ.winrate >= 50 ? 'text-green-400' : 'text-red-400'">
                          {{ champ.winrate }}%
                        </span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-gray-400">KDA:</span>
                        <span>{{ champ.avg_kda }}</span>
                      </div>
                    </div>
                    <div v-else class="text-xs text-gray-400 text-center">
                      Non joué
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: Champion Pool -->
        <div class="w-[400px] bg-gray-800 rounded-lg p-4 h-fit sticky top-4">
          <div class="mb-4">
            <h2 class="text-lg font-semibold mb-3">Champions</h2>
            <!-- Search bar -->
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Rechercher un champion..."
              class="w-full bg-gray-700 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          <!-- Filter tabs -->
          <div class="flex gap-2 mb-4">
            <button
              @click="filterMode = 'all'"
              :class="[
                'px-3 py-1 rounded text-sm transition',
                filterMode === 'all' ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600',
              ]"
            >
              Tous
            </button>
            <button
              @click="filterMode = 'played'"
              :class="[
                'px-3 py-1 rounded text-sm transition',
                filterMode === 'played' ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600',
              ]"
            >
              Joués
            </button>
            <button
              @click="filterMode = 'untiered'"
              :class="[
                'px-3 py-1 rounded text-sm transition',
                filterMode === 'untiered' ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600',
              ]"
            >
              Non classés
            </button>
          </div>

          <!-- Champions grid -->
          <div class="max-h-[calc(100vh-280px)] overflow-y-auto">
            <div class="grid grid-cols-5 gap-2">
              <div
                v-for="champ in filteredChampions"
                :key="champ.id"
                class="relative group cursor-grab active:cursor-grabbing"
                draggable="true"
                @dragstart="startDrag(champ.id, $event)"
              >
                <img
                  :src="getChampionIconUrl(champ.id)"
                  :alt="champ.name"
                  class="w-full aspect-square rounded border-2 transition"
                  :class="getChampionPoolBorder(champ.id)"
                />
                <!-- Stats overlay if played -->
                <div
                  v-if="getChampionStats(champ.id)"
                  class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-1"
                >
                  <div
                    class="text-[9px] font-bold text-center"
                    :class="
                      (getChampionStats(champ.id)?.winrate ?? 0) >= 50
                        ? 'text-green-400'
                        : 'text-red-400'
                    "
                  >
                    {{ getChampionStats(champ.id)?.wins }}W/{{ getChampionStats(champ.id)?.losses }}L
                  </div>
                </div>
                <!-- Score badge -->
                <div
                  v-if="getChampionStats(champ.id)"
                  class="absolute -top-1 -right-1 text-[9px] font-bold px-1 rounded-full"
                  :class="getScoreBadgeColor(getChampionStats(champ.id)?.performance_score ?? 0)"
                >
                  {{ getChampionStats(champ.id)?.performance_score }}
                </div>
                <!-- Tier indicator if already placed -->
                <div
                  v-if="getChampionTier(champ.id)"
                  class="absolute top-0 left-0 text-[10px] font-bold px-1 rounded-br"
                  :class="getTierBadgeColor(getChampionTier(champ.id)!)"
                >
                  {{ getChampionTier(champ.id) }}
                </div>
                <!-- Tooltip -->
                <div
                  class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-1 bg-gray-900 rounded px-2 py-1 text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10"
                >
                  {{ champ.name }}
                </div>
              </div>
            </div>

            <!-- Empty state -->
            <div
              v-if="filteredChampions.length === 0"
              class="text-center py-8 text-gray-500"
            >
              Aucun champion trouvé
            </div>
          </div>

          <!-- Champions count -->
          <div class="mt-3 text-sm text-gray-400 text-center">
            {{ filteredChampions.length }} champion(s)
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppNavbar from '@/components/AppNavbar.vue'
import { playersApi, tierListApi } from '@/api'
import type { Player, PlayerTierList, ChampionStatsWithScore, TierLevel } from '@/types'
import {
  loadChampionData,
  getAllChampions,
  getChampionIconUrl,
  getChampionName,
} from '@/utils/champions'

// State
const players = ref<Player[]>([])
const selectedPlayerId = ref<number | null>(null)
const tierList = ref<PlayerTierList | null>(null)
const loading = ref(true)
const searchQuery = ref('')
const filterMode = ref<'all' | 'played' | 'untiered'>('all')
const dragOverTier = ref<TierLevel | null>(null)

// Tier definitions
const tiers: Array<{ level: TierLevel; label: string; bgColor: string }> = [
  { level: 'S', label: 'Excellent', bgColor: 'bg-yellow-600' },
  { level: 'A', label: 'Très bon', bgColor: 'bg-green-600' },
  { level: 'B', label: 'Bon', bgColor: 'bg-blue-600' },
  { level: 'C', label: 'Moyen', bgColor: 'bg-purple-600' },
  { level: 'D', label: 'À éviter', bgColor: 'bg-red-600' },
]

// All champions from DDragon
const allChampions = computed(() => {
  const data = getAllChampions()
  return Object.entries(data)
    .map(([id, champ]) => ({
      id: parseInt(id),
      name: champ.name,
    }))
    .sort((a, b) => a.name.localeCompare(b.name))
})

// Champions with stats lookup
const championStatsMap = computed(() => {
  const map = new Map<number, ChampionStatsWithScore>()
  if (tierList.value) {
    for (const champ of tierList.value.champions) {
      map.set(champ.champion_id, champ)
    }
  }
  return map
})

// Filtered champions for the pool
const filteredChampions = computed(() => {
  let result = allChampions.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter((c) => c.name.toLowerCase().includes(query))
  }

  // Mode filter
  if (filterMode.value === 'played') {
    result = result.filter((c) => championStatsMap.value.has(c.id))
  } else if (filterMode.value === 'untiered') {
    result = result.filter((c) => !getChampionTier(c.id))
  }

  return result
})

// Helpers
function getChampionsForTier(tier: TierLevel): ChampionStatsWithScore[] {
  if (!tierList.value) return []

  switch (tier) {
    case 'S':
      return tierList.value.tier_s
    case 'A':
      return tierList.value.tier_a
    case 'B':
      return tierList.value.tier_b
    case 'C':
      return tierList.value.tier_c
    case 'D':
      return tierList.value.tier_d
    default:
      return []
  }
}

function getChampionStats(championId: number): ChampionStatsWithScore | undefined {
  return championStatsMap.value.get(championId)
}

function getChampionDisplayName(championId: number): string {
  // Use DDragon name if available (more reliable)
  return getChampionName(championId)
}

function getChampionTier(championId: number): TierLevel | null {
  if (!tierList.value) return null

  for (const tier of ['S', 'A', 'B', 'C', 'D'] as TierLevel[]) {
    const tierChamps = getChampionsForTier(tier)
    if (tierChamps.some((c) => c.champion_id === championId)) {
      return tier
    }
  }
  return null
}

function getTierBorderColor(tier: TierLevel): string {
  switch (tier) {
    case 'S':
      return 'border-yellow-500'
    case 'A':
      return 'border-green-500'
    case 'B':
      return 'border-blue-500'
    case 'C':
      return 'border-purple-500'
    case 'D':
      return 'border-red-500'
    default:
      return 'border-gray-600'
  }
}

function getTierBadgeColor(tier: TierLevel): string {
  switch (tier) {
    case 'S':
      return 'bg-yellow-600 text-yellow-100'
    case 'A':
      return 'bg-green-600 text-green-100'
    case 'B':
      return 'bg-blue-600 text-blue-100'
    case 'C':
      return 'bg-purple-600 text-purple-100'
    case 'D':
      return 'bg-red-600 text-red-100'
    default:
      return 'bg-gray-600'
  }
}

function getChampionPoolBorder(championId: number): string {
  const tier = getChampionTier(championId)
  if (tier) return getTierBorderColor(tier)
  if (championStatsMap.value.has(championId)) return 'border-gray-400'
  return 'border-gray-700'
}

function getScoreBadgeColor(score: number): string {
  if (score >= 80) return 'bg-yellow-500 text-black'
  if (score >= 60) return 'bg-green-500 text-black'
  if (score >= 40) return 'bg-blue-500 text-white'
  if (score >= 20) return 'bg-purple-500 text-white'
  return 'bg-red-500 text-white'
}

// Drag and drop
function startDrag(championId: number, event: DragEvent) {
  if (event.dataTransfer) {
    event.dataTransfer.setData('championId', championId.toString())
    event.dataTransfer.effectAllowed = 'move'
  }
}

function dragEnterTier(tier: TierLevel) {
  dragOverTier.value = tier
}

function dragLeaveTier(tier: TierLevel) {
  if (dragOverTier.value === tier) {
    dragOverTier.value = null
  }
}

async function dropOnTier(tier: TierLevel, event: DragEvent) {
  dragOverTier.value = null

  if (!event.dataTransfer || !selectedPlayerId.value) return

  const championId = parseInt(event.dataTransfer.getData('championId'))
  if (isNaN(championId)) return

  // Get champion name from allChampions or stats
  const champData = allChampions.value.find((c) => c.id === championId)
  const champName = champData?.name || `Champion ${championId}`

  try {
    await tierListApi.setChampionTier(selectedPlayerId.value, championId, tier)
    await loadTierList()
  } catch (error) {
    console.error('Failed to set tier:', error)
    alert(`Erreur lors du placement de ${champName}`)
  }
}

async function removeFromTier(championId: number) {
  if (!selectedPlayerId.value) return

  try {
    await tierListApi.deleteChampionTier(selectedPlayerId.value, championId)
    await loadTierList()
  } catch (error) {
    console.error('Failed to remove tier:', error)
    alert('Erreur lors de la suppression du tier')
  }
}

// Data loading
async function loadPlayers() {
  try {
    const response = await playersApi.getPlayers()
    players.value = response.data
    if (players.value.length > 0) {
      selectedPlayerId.value = players.value[0].id
    }
  } catch (error) {
    console.error('Failed to load players:', error)
  }
}

async function loadTierList() {
  if (!selectedPlayerId.value) return

  loading.value = true
  try {
    const response = await tierListApi.getPlayerTierList(selectedPlayerId.value)
    tierList.value = response.data
  } catch (error) {
    console.error('Failed to load tier list:', error)
    tierList.value = null
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  // Load champion data first
  await loadChampionData()

  // Then load players and tier list
  await loadPlayers()
  if (selectedPlayerId.value) {
    await loadTierList()
  } else {
    loading.value = false
  }
})
</script>
