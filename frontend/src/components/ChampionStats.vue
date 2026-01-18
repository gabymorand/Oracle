<template>
  <div class="bg-gray-800 rounded-lg p-6">
    <h3 class="text-xl font-bold mb-4">Champion Statistics</h3>
    <div v-if="loading" class="text-center py-8">
      <p class="text-gray-400">Loading champion stats...</p>
    </div>
    <div v-else-if="champions.length === 0" class="text-center py-8">
      <p class="text-gray-400">No games found. Refresh stats to load champion data.</p>
    </div>
    <div v-else class="overflow-x-auto">
      <table class="w-full">
        <thead>
          <tr class="text-left text-sm text-gray-400 border-b border-gray-700">
            <th class="pb-2">Champion</th>
            <th class="pb-2 text-center">Games</th>
            <th class="pb-2 text-center">W/L</th>
            <th class="pb-2 text-center">WR%</th>
            <th class="pb-2 text-center">KDA</th>
            <th class="pb-2 text-center">CS/min</th>
            <th class="pb-2 text-center">Gold/min</th>
            <th class="pb-2 text-center">Vision/min</th>
            <th class="pb-2 text-center">KP%</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="champ in champions"
            :key="champ.champion_id"
            class="border-b border-gray-700 hover:bg-gray-700 transition"
          >
            <td class="py-3">
              <div class="flex items-center gap-3">
                <img
                  :src="getChampionIcon(champ.champion_id)"
                  :alt="getChampName(champ.champion_id)"
                  class="w-10 h-10 rounded"
                  @error="handleImageError"
                />
                <span class="font-semibold">{{ getChampName(champ.champion_id) }}</span>
              </div>
            </td>
            <td class="text-center">{{ champ.games_played }}</td>
            <td class="text-center">
              <span class="text-green-400">{{ champ.wins }}</span> /
              <span class="text-red-400">{{ champ.losses }}</span>
            </td>
            <td class="text-center">
              <span
                :class="[
                  champ.winrate >= 50 ? 'text-green-400' : 'text-red-400',
                  'font-semibold'
                ]"
              >
                {{ champ.winrate }}%
              </span>
            </td>
            <td class="text-center">{{ champ.avg_kda }}</td>
            <td class="text-center">{{ champ.avg_cs_per_min }}</td>
            <td class="text-center">{{ champ.avg_gold_per_min }}</td>
            <td class="text-center">{{ champ.avg_vision_per_min }}</td>
            <td class="text-center">{{ champ.avg_kp }}%</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiClient } from '@/api/client'
import { loadChampionData, getChampionName, getChampionIconUrl } from '@/utils/champions'

const props = defineProps<{
  riotAccountId: number
}>()

interface ChampionStat {
  champion_id: number
  games_played: number
  wins: number
  losses: number
  winrate: number
  avg_kda: number
  avg_cs_per_min: number
  avg_gold_per_min: number
  avg_vision_per_min: number
  avg_kp: number
  total_kills: number
  total_deaths: number
  total_assists: number
}

const champions = ref<ChampionStat[]>([])
const loading = ref(true)

function getChampName(championId: number): string {
  return getChampionName(championId)
}

function getChampionIcon(championId: number): string {
  return getChampionIconUrl(championId)
}

function handleImageError(event: Event) {
  const img = event.target as HTMLImageElement
  // Fallback to community dragon if DDragon fails
  if (!img.src.includes('communitydragon')) {
    const champId = img.alt
    img.src = `https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/-1.png`
  }
}

async function loadChampionStats() {
  try {
    loading.value = true
    // Load champion data first
    await loadChampionData()
    const response = await apiClient.get(`/api/v1/stats/champions/${props.riotAccountId}`)
    champions.value = response.data
  } catch (error) {
    console.error('Failed to load champion stats:', error)
    champions.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadChampionStats()
})
</script>
