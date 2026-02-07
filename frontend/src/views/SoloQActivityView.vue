<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { statsApi } from '@/api'
import type { TeamActivityResponse, PlayerActivitySummary, ActivityGame } from '@/types'
import { getChampionIcon, getChampionName } from '@/utils/champions'

const loading = ref(false)
const refreshing = ref(false)
const activityData = ref<TeamActivityResponse | null>(null)
const weekOffset = ref(0)

// Days of the week (Monday to Sunday)
const dayNames = ['LUN.', 'MAR.', 'MER.', 'JEU.', 'VEN.', 'SAM.', 'DIM.']

async function loadActivity() {
  loading.value = true
  try {
    const res = await statsApi.getTeamActivity(weekOffset.value)
    activityData.value = res.data
  } catch (error) {
    console.error('Failed to load activity:', error)
  } finally {
    loading.value = false
  }
}

async function refreshAllPlayers() {
  refreshing.value = true
  try {
    const res = await statsApi.refreshAllStats()
    alert(`Actualisation terminee: ${res.data.refreshed} succes, ${res.data.failed} echecs`)
    await loadActivity()
  } catch (error) {
    console.error('Failed to refresh:', error)
    alert('Erreur lors de l\'actualisation')
  } finally {
    refreshing.value = false
  }
}

function previousWeek() {
  weekOffset.value--
  loadActivity()
}

function nextWeek() {
  weekOffset.value++
  loadActivity()
}

function currentWeek() {
  weekOffset.value = 0
  loadActivity()
}

// Get the dates for each day of the week
const weekDates = computed(() => {
  if (!activityData.value) return []
  const start = new Date(activityData.value.week_start)
  const dates = []
  for (let i = 0; i < 7; i++) {
    const date = new Date(start)
    date.setDate(start.getDate() + i)
    dates.push({
      dayName: dayNames[i],
      dayNumber: date.getDate(),
      dateKey: date.toISOString().split('T')[0],
    })
  }
  return dates
})

// Format last updated time
const lastUpdatedFormatted = computed(() => {
  if (!activityData.value) return ''
  const date = new Date(activityData.value.last_updated)
  return date.toLocaleString('fr-FR', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
})

// Get games for a specific player and day
function getGamesForDay(player: PlayerActivitySummary, dateKey: string): ActivityGame[] {
  return player.games_by_day[dateKey] || []
}

// Format rank display
function formatRank(tier?: string, division?: string, lp?: number): string {
  if (!tier) return 'Unranked'
  const tierShort = tier.charAt(0)
  if (['MASTER', 'GRANDMASTER', 'CHALLENGER'].includes(tier)) {
    return `${tierShort} - ${lp ?? 0} LP`
  }
  return `${tierShort}${division || ''} - ${lp ?? 0} LP`
}

// Format rank for display with icon style
function getRankIcon(tier?: string): string {
  if (!tier) return ''
  const iconMap: Record<string, string> = {
    IRON: 'I',
    BRONZE: 'B',
    SILVER: 'S',
    GOLD: 'G',
    PLATINUM: 'P',
    EMERALD: 'E',
    DIAMOND: 'D',
    MASTER: 'M',
    GRANDMASTER: 'GM',
    CHALLENGER: 'C',
  }
  return iconMap[tier] || tier.charAt(0)
}

// Get role label
function getRoleLabel(role: string): string {
  const labels: Record<string, string> = {
    top: 'TOP',
    jungle: 'JGL',
    mid: 'MID',
    adc: 'ADC',
    support: 'SUP',
  }
  return labels[role.toLowerCase()] || role.toUpperCase()
}

// Get KDA color class
function getKdaClass(win: boolean): string {
  return win ? 'text-green-400' : 'text-red-400'
}

// Get win/loss badge class
function getWinLossBadge(win: boolean): string {
  return win
    ? 'bg-green-500/20 text-green-400 border-green-500/50'
    : 'bg-red-500/20 text-red-400 border-red-500/50'
}

// Format winrate color
function getWinrateClass(winrate: number): string {
  if (winrate >= 60) return 'text-green-400'
  if (winrate >= 50) return 'text-yellow-400'
  return 'text-red-400'
}

// Format game type badge
function getGameTypeBadge(gameType: string): { label: string; class: string } | null {
  if (gameType === 'competitive') {
    return { label: 'SCRIM', class: 'bg-blue-500/20 text-blue-400 border border-blue-500/50' }
  }
  return null
}

onMounted(loadActivity)
</script>

<template>
  <div class="min-h-screen bg-gray-900 text-white p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold tracking-wider">SUIVI D'ACTIVITE SOLOQ</h1>
        <div v-if="activityData" class="text-gray-400 mt-1 text-sm">
          {{ activityData.total_soloq }} SOLOQS
          <span class="mx-2">•</span>
          {{ activityData.total_scrims }} SCRIMS
          <span class="mx-2">•</span>
          {{ activityData.total_duos }} DUOQ
          <span class="mx-2">•</span>
          <span :class="getWinrateClass(activityData.overall_winrate)">
            {{ activityData.overall_winrate }}% WR TOTAL
          </span>
        </div>
      </div>

      <div class="flex items-center gap-4">
        <span class="text-gray-400 text-sm">
          Actualise {{ lastUpdatedFormatted }}
        </span>
        <button
          @click="refreshAllPlayers"
          :disabled="refreshing"
          class="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition disabled:opacity-50"
        >
          <svg
            :class="{ 'animate-spin': refreshing }"
            class="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          Actualiser
        </button>
      </div>
    </div>

    <!-- Week Navigation -->
    <div class="flex items-center justify-center gap-4 mb-6">
      <button
        @click="previousWeek"
        class="p-2 hover:bg-gray-700 rounded-lg transition"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      <div class="text-center min-w-[200px]">
        <span v-if="activityData" class="text-lg font-medium">
          {{ new Date(activityData.week_start).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' }) }}
          -
          {{ new Date(activityData.week_end).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' }) }}
        </span>
      </div>

      <button
        @click="nextWeek"
        :disabled="weekOffset >= 0"
        class="p-2 hover:bg-gray-700 rounded-lg transition disabled:opacity-30"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>

      <button
        v-if="weekOffset !== 0"
        @click="currentWeek"
        class="px-3 py-1 text-sm bg-blue-600 hover:bg-blue-500 rounded transition"
      >
        Semaine actuelle
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
    </div>

    <!-- Legend -->
    <div v-if="!loading && activityData" class="flex items-center gap-6 mb-4 text-sm text-gray-400">
      <div class="flex items-center gap-2">
        <span class="w-4 h-4 rounded bg-green-500/20 border border-green-500/50 flex items-center justify-center text-xs text-green-400">W</span>
        <span>Victoire</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="w-4 h-4 rounded bg-red-500/20 border border-red-500/50 flex items-center justify-center text-xs text-red-400">L</span>
        <span>Defaite</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="px-2 py-0.5 rounded text-xs bg-blue-500/20 text-blue-400 border border-blue-500/50">SCRIM</span>
        <span>Scrim/Competitive</span>
      </div>
    </div>

    <!-- Activity Grid -->
    <div v-if="!loading && activityData" class="overflow-x-auto">
      <table class="w-full border-collapse">
        <!-- Header Row with Days -->
        <thead>
          <tr>
            <th class="w-48 p-2 text-left"></th>
            <th
              v-for="day in weekDates"
              :key="day.dateKey"
              class="p-2 text-center min-w-[140px] border-l border-gray-700"
            >
              <div class="text-gray-400 text-xs">{{ day.dayName }}</div>
              <div class="text-lg font-bold">{{ day.dayNumber }}</div>
            </th>
          </tr>
        </thead>

        <tbody>
          <!-- Player Rows -->
          <tr
            v-for="player in activityData.players"
            :key="player.player_id"
            class="border-t border-gray-700"
          >
            <!-- Player Info Column -->
            <td class="p-3 bg-gray-800/50">
              <div class="flex flex-col">
                <!-- Name and Role -->
                <div class="flex items-center gap-2 mb-1">
                  <span class="font-bold text-white">{{ player.summoner_name }}</span>
                  <span class="text-xs px-1.5 py-0.5 bg-gray-700 rounded text-gray-300">
                    {{ getRoleLabel(player.role) }}
                  </span>
                </div>

                <!-- Winrate -->
                <div class="flex items-center gap-2 text-sm mb-1">
                  <span
                    class="px-2 py-0.5 rounded text-xs font-medium"
                    :class="player.winrate >= 50 ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'"
                  >
                    {{ player.winrate }}% WR
                  </span>
                  <span class="text-gray-400">
                    {{ player.wins }}W - {{ player.losses }}L
                  </span>
                </div>

                <!-- Rank -->
                <div class="flex items-center gap-1 text-sm text-gray-300">
                  <svg class="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                  {{ formatRank(player.rank_tier, player.rank_division, player.lp) }}
                </div>
              </div>
            </td>

            <!-- Day Columns -->
            <td
              v-for="day in weekDates"
              :key="day.dateKey"
              class="p-2 align-top border-l border-gray-700 min-w-[140px]"
            >
              <div class="space-y-2">
                <div
                  v-for="game in getGamesForDay(player, day.dateKey)"
                  :key="game.id"
                  class="bg-gray-800 rounded-lg p-2 border border-gray-700 hover:border-gray-600 transition"
                >
                  <!-- Time -->
                  <div class="text-xs text-gray-400 mb-1">
                    {{ game.start_time }} — {{ game.end_time }}
                  </div>

                  <!-- Game Type Badge -->
                  <div v-if="getGameTypeBadge(game.game_type)" class="mb-1">
                    <span
                      class="text-xs px-1.5 py-0.5 rounded"
                      :class="getGameTypeBadge(game.game_type)?.class"
                    >
                      {{ getGameTypeBadge(game.game_type)?.label }}
                    </span>
                  </div>

                  <!-- Champion + KDA -->
                  <div class="flex items-center gap-2">
                    <img
                      :src="getChampionIcon(game.champion_id)"
                      :alt="getChampionName(game.champion_id)"
                      class="w-8 h-8 rounded"
                      :class="game.win ? 'ring-2 ring-green-500' : 'ring-2 ring-red-500'"
                    />
                    <div class="flex flex-col">
                      <span class="font-bold" :class="getKdaClass(game.win)">
                        {{ game.kills }}/{{ game.deaths }}/{{ game.assists }}
                      </span>
                    </div>
                    <span
                      class="ml-auto w-5 h-5 rounded flex items-center justify-center text-xs font-bold border"
                      :class="getWinLossBadge(game.win)"
                    >
                      {{ game.win ? 'W' : 'L' }}
                    </span>
                  </div>
                </div>

                <!-- Empty state for no games -->
                <div
                  v-if="getGamesForDay(player, day.dateKey).length === 0"
                  class="h-12 flex items-center justify-center text-gray-600"
                >
                  -
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && activityData && activityData.players.length === 0" class="text-center py-20 text-gray-400">
      <p>Aucun joueur trouve dans l'equipe</p>
    </div>
  </div>
</template>
