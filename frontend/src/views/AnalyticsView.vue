<template>
  <div class="min-h-screen bg-gray-900">
    <AppNavbar :show-back-button="true" />

    <div class="max-w-7xl mx-auto px-4 py-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold">Analytics</h1>
        <p class="text-gray-400 mt-1">Statistiques detaillees de l'equipe</p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12 text-gray-400">
        Chargement des statistiques...
      </div>

      <div v-else>
        <!-- Team Overview Cards -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div class="bg-gray-800 rounded-xl p-4">
            <div class="text-3xl font-bold text-blue-400">{{ teamStats.totalGames }}</div>
            <div class="text-sm text-gray-400">Games totales</div>
          </div>
          <div class="bg-gray-800 rounded-xl p-4">
            <div class="text-3xl font-bold" :class="teamStats.winrate >= 50 ? 'text-green-400' : 'text-red-400'">
              {{ teamStats.winrate.toFixed(1) }}%
            </div>
            <div class="text-sm text-gray-400">Winrate global</div>
          </div>
          <div class="bg-gray-800 rounded-xl p-4">
            <div class="text-3xl font-bold text-yellow-400">{{ teamStats.avgKDA.toFixed(2) }}</div>
            <div class="text-sm text-gray-400">KDA moyen</div>
          </div>
          <div class="bg-gray-800 rounded-xl p-4">
            <div class="text-3xl font-bold text-purple-400">{{ teamStats.avgCS.toFixed(1) }}</div>
            <div class="text-sm text-gray-400">CS/min moyen</div>
          </div>
        </div>

        <!-- Player Comparison Table -->
        <div class="bg-gray-800 rounded-xl p-6 mb-8">
          <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Comparaison Joueurs
          </h2>

          <div class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="text-gray-400 text-sm border-b border-gray-700">
                  <th class="text-left py-3 px-4">Joueur</th>
                  <th class="text-center py-3 px-4 cursor-pointer hover:text-white" @click="sortBy('total_games')">
                    Games {{ getSortIcon('total_games') }}
                  </th>
                  <th class="text-center py-3 px-4 cursor-pointer hover:text-white" @click="sortBy('winrate')">
                    Winrate {{ getSortIcon('winrate') }}
                  </th>
                  <th class="text-center py-3 px-4 cursor-pointer hover:text-white" @click="sortBy('avg_kda')">
                    KDA {{ getSortIcon('avg_kda') }}
                  </th>
                  <th class="text-center py-3 px-4 cursor-pointer hover:text-white" @click="sortBy('avg_cs_per_min')">
                    CS/min {{ getSortIcon('avg_cs_per_min') }}
                  </th>
                  <th class="text-center py-3 px-4 cursor-pointer hover:text-white" @click="sortBy('avg_gold_per_min')">
                    Gold/min {{ getSortIcon('avg_gold_per_min') }}
                  </th>
                  <th class="text-center py-3 px-4 cursor-pointer hover:text-white" @click="sortBy('avg_vision_score_per_min')">
                    Vision/min {{ getSortIcon('avg_vision_score_per_min') }}
                  </th>
                  <th class="text-center py-3 px-4 cursor-pointer hover:text-white" @click="sortBy('avg_kill_participation')">
                    KP% {{ getSortIcon('avg_kill_participation') }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="player in sortedPlayerStats"
                  :key="player.player_id"
                  class="border-b border-gray-700/50 hover:bg-gray-700/30"
                >
                  <td class="py-3 px-4">
                    <div class="flex items-center gap-3">
                      <div :class="['w-3 h-3 rounded-full', getRoleBgColor(player.role)]"></div>
                      <div>
                        <div class="font-medium">{{ player.summoner_name }}</div>
                        <div class="text-xs text-gray-500 uppercase">{{ player.role }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="text-center py-3 px-4">{{ player.total_games }}</td>
                  <td class="text-center py-3 px-4">
                    <span :class="getStatColor(player.winrate, 50, 55)">
                      {{ player.winrate.toFixed(1) }}%
                    </span>
                  </td>
                  <td class="text-center py-3 px-4">
                    <span :class="getStatColor(player.avg_kda, 2.5, 3.5)">
                      {{ player.avg_kda.toFixed(2) }}
                    </span>
                  </td>
                  <td class="text-center py-3 px-4">
                    <span :class="getStatColor(player.avg_cs_per_min, 6, 8, player.role)">
                      {{ player.avg_cs_per_min.toFixed(1) }}
                    </span>
                  </td>
                  <td class="text-center py-3 px-4">
                    <span :class="getStatColor(player.avg_gold_per_min, 350, 400)">
                      {{ player.avg_gold_per_min.toFixed(0) }}
                    </span>
                  </td>
                  <td class="text-center py-3 px-4">
                    <span :class="getStatColor(player.avg_vision_score_per_min, 0.8, 1.2, player.role)">
                      {{ player.avg_vision_score_per_min.toFixed(2) }}
                    </span>
                  </td>
                  <td class="text-center py-3 px-4">
                    <span :class="getStatColor(player.avg_kill_participation, 50, 65)">
                      {{ player.avg_kill_participation.toFixed(1) }}%
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="playerStats.length === 0" class="text-center py-8 text-gray-500">
            Aucune donnee disponible. Rafraichissez les stats des joueurs.
          </div>
        </div>

        <!-- Stats by Role -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <!-- Role Performance -->
          <div class="bg-gray-800 rounded-xl p-6">
            <h2 class="text-xl font-semibold mb-4">Performance par Role</h2>
            <div class="space-y-4">
              <div v-for="role in roleOrder" :key="role" class="flex items-center gap-4">
                <div :class="['w-20 text-sm font-medium uppercase', getRoleTextColor(role)]">
                  {{ role }}
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2">
                    <div class="flex-1 bg-gray-700 rounded-full h-3">
                      <div
                        :class="['h-3 rounded-full', getRoleBgColor(role)]"
                        :style="{ width: `${getRoleWinrate(role)}%` }"
                      ></div>
                    </div>
                    <span class="text-sm w-14 text-right">{{ getRoleWinrate(role).toFixed(1) }}%</span>
                  </div>
                </div>
                <div class="text-sm text-gray-400 w-20 text-right">
                  {{ getRoleGames(role) }} games
                </div>
              </div>
            </div>
          </div>

          <!-- Stat Leaders -->
          <div class="bg-gray-800 rounded-xl p-6">
            <h2 class="text-xl font-semibold mb-4">Leaders</h2>
            <div class="space-y-4">
              <div v-for="stat in statLeaders" :key="stat.name" class="flex items-center justify-between">
                <div>
                  <div class="text-sm text-gray-400">{{ stat.label }}</div>
                  <div class="font-medium">{{ stat.player }}</div>
                </div>
                <div :class="['text-xl font-bold', stat.color]">
                  {{ stat.value }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Benchmarks -->
        <div class="bg-gray-800 rounded-xl p-6">
          <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            Benchmarks (vs moyenne Diamond+)
          </h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div v-for="benchmark in benchmarks" :key="benchmark.name" class="bg-gray-700/50 rounded-lg p-4">
              <div class="text-sm text-gray-400 mb-1">{{ benchmark.label }}</div>
              <div class="flex items-center gap-2">
                <span class="text-2xl font-bold">{{ benchmark.teamValue }}</span>
                <span :class="benchmark.diff >= 0 ? 'text-green-400' : 'text-red-400'" class="text-sm">
                  {{ benchmark.diff >= 0 ? '+' : '' }}{{ benchmark.diff.toFixed(1) }}%
                </span>
              </div>
              <div class="text-xs text-gray-500">Benchmark: {{ benchmark.benchValue }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppNavbar from '@/components/AppNavbar.vue'
import { playersApi, statsApi } from '@/api'
import type { Player, PlayerStats } from '@/types'

const roleOrder = ['top', 'jungle', 'mid', 'adc', 'support'] as const

const loading = ref(true)
const players = ref<Player[]>([])
const playerStats = ref<PlayerStats[]>([])
const sortColumn = ref<string>('winrate')
const sortDirection = ref<'asc' | 'desc'>('desc')

// Computed team stats
const teamStats = computed(() => {
  if (playerStats.value.length === 0) {
    return { totalGames: 0, winrate: 0, avgKDA: 0, avgCS: 0 }
  }

  const totalGames = playerStats.value.reduce((sum, p) => sum + p.total_games, 0)
  const weightedWinrate = playerStats.value.reduce((sum, p) => sum + p.winrate * p.total_games, 0) / totalGames
  const avgKDA = playerStats.value.reduce((sum, p) => sum + p.avg_kda, 0) / playerStats.value.length
  const avgCS = playerStats.value.reduce((sum, p) => sum + p.avg_cs_per_min, 0) / playerStats.value.length

  return {
    totalGames,
    winrate: weightedWinrate || 0,
    avgKDA,
    avgCS,
  }
})

// Sorted player stats
const sortedPlayerStats = computed(() => {
  const stats = [...playerStats.value]
  stats.sort((a, b) => {
    const aVal = a[sortColumn.value as keyof PlayerStats] as number
    const bVal = b[sortColumn.value as keyof PlayerStats] as number
    return sortDirection.value === 'desc' ? bVal - aVal : aVal - bVal
  })
  return stats
})

// Stat leaders
const statLeaders = computed(() => {
  if (playerStats.value.length === 0) return []

  const leaders = [
    {
      name: 'winrate',
      label: 'Meilleur Winrate',
      player: '',
      value: '',
      color: 'text-green-400',
    },
    {
      name: 'kda',
      label: 'Meilleur KDA',
      player: '',
      value: '',
      color: 'text-yellow-400',
    },
    {
      name: 'cs',
      label: 'Meilleur CS/min',
      player: '',
      value: '',
      color: 'text-blue-400',
    },
    {
      name: 'kp',
      label: 'Meilleure KP',
      player: '',
      value: '',
      color: 'text-purple-400',
    },
  ]

  const bestWinrate = [...playerStats.value].filter(p => p.total_games >= 5).sort((a, b) => b.winrate - a.winrate)[0]
  const bestKDA = [...playerStats.value].sort((a, b) => b.avg_kda - a.avg_kda)[0]
  const bestCS = [...playerStats.value].sort((a, b) => b.avg_cs_per_min - a.avg_cs_per_min)[0]
  const bestKP = [...playerStats.value].sort((a, b) => b.avg_kill_participation - a.avg_kill_participation)[0]

  if (bestWinrate) {
    leaders[0].player = bestWinrate.summoner_name
    leaders[0].value = `${bestWinrate.winrate.toFixed(1)}%`
  }
  if (bestKDA) {
    leaders[1].player = bestKDA.summoner_name
    leaders[1].value = bestKDA.avg_kda.toFixed(2)
  }
  if (bestCS) {
    leaders[2].player = bestCS.summoner_name
    leaders[2].value = bestCS.avg_cs_per_min.toFixed(1)
  }
  if (bestKP) {
    leaders[3].player = bestKP.summoner_name
    leaders[3].value = `${bestKP.avg_kill_participation.toFixed(1)}%`
  }

  return leaders.filter(l => l.player)
})

// Benchmarks (Diamond+ averages)
const benchmarks = computed(() => {
  const diamondBenchmarks = {
    kda: 2.8,
    csPerMin: 7.2,
    goldPerMin: 380,
    visionPerMin: 1.0,
  }

  if (playerStats.value.length === 0) return []

  const teamKDA = teamStats.value.avgKDA
  const teamCS = teamStats.value.avgCS
  const teamGold = playerStats.value.reduce((sum, p) => sum + p.avg_gold_per_min, 0) / playerStats.value.length
  const teamVision = playerStats.value.reduce((sum, p) => sum + p.avg_vision_score_per_min, 0) / playerStats.value.length

  return [
    {
      name: 'kda',
      label: 'KDA',
      teamValue: teamKDA.toFixed(2),
      benchValue: diamondBenchmarks.kda.toFixed(2),
      diff: ((teamKDA - diamondBenchmarks.kda) / diamondBenchmarks.kda) * 100,
    },
    {
      name: 'cs',
      label: 'CS/min',
      teamValue: teamCS.toFixed(1),
      benchValue: diamondBenchmarks.csPerMin.toFixed(1),
      diff: ((teamCS - diamondBenchmarks.csPerMin) / diamondBenchmarks.csPerMin) * 100,
    },
    {
      name: 'gold',
      label: 'Gold/min',
      teamValue: teamGold.toFixed(0),
      benchValue: diamondBenchmarks.goldPerMin.toFixed(0),
      diff: ((teamGold - diamondBenchmarks.goldPerMin) / diamondBenchmarks.goldPerMin) * 100,
    },
    {
      name: 'vision',
      label: 'Vision/min',
      teamValue: teamVision.toFixed(2),
      benchValue: diamondBenchmarks.visionPerMin.toFixed(2),
      diff: ((teamVision - diamondBenchmarks.visionPerMin) / diamondBenchmarks.visionPerMin) * 100,
    },
  ]
})

// Helper functions
function sortBy(column: string) {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'desc' ? 'asc' : 'desc'
  } else {
    sortColumn.value = column
    sortDirection.value = 'desc'
  }
}

function getSortIcon(column: string): string {
  if (sortColumn.value !== column) return ''
  return sortDirection.value === 'desc' ? '↓' : '↑'
}

function getRoleBgColor(role: string): string {
  const colors: Record<string, string> = {
    top: 'bg-red-500',
    jungle: 'bg-green-500',
    mid: 'bg-blue-500',
    adc: 'bg-yellow-500',
    support: 'bg-purple-500',
  }
  return colors[role.toLowerCase()] || 'bg-gray-500'
}

function getRoleTextColor(role: string): string {
  const colors: Record<string, string> = {
    top: 'text-red-400',
    jungle: 'text-green-400',
    mid: 'text-blue-400',
    adc: 'text-yellow-400',
    support: 'text-purple-400',
  }
  return colors[role.toLowerCase()] || 'text-gray-400'
}

function getRoleWinrate(role: string): number {
  const player = playerStats.value.find(p => p.role.toLowerCase() === role.toLowerCase())
  return player?.winrate || 0
}

function getRoleGames(role: string): number {
  const player = playerStats.value.find(p => p.role.toLowerCase() === role.toLowerCase())
  return player?.total_games || 0
}

function getStatColor(value: number, mid: number, high: number, role?: string): string {
  // Adjust thresholds for support (lower CS expected)
  if (role?.toLowerCase() === 'support' && mid === 6) {
    mid = 1.5
    high = 2.5
  }

  if (value >= high) return 'text-green-400'
  if (value >= mid) return 'text-yellow-400'
  return 'text-red-400'
}

async function loadData() {
  loading.value = true
  try {
    const playersRes = await playersApi.getPlayers()
    players.value = playersRes.data

    // Load stats for each player
    const statsPromises = players.value.map(p =>
      statsApi.getPlayerStats(p.id).catch(() => ({ data: null }))
    )
    const statsResults = await Promise.all(statsPromises)
    playerStats.value = statsResults
      .map(res => res.data)
      .filter((s): s is PlayerStats => s !== null)
  } catch (error) {
    console.error('Failed to load analytics:', error)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>
