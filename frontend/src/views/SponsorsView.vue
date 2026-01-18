<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-900 via-gray-900 to-purple-900">
    <div class="bg-gray-800/50 border-b border-gray-700 backdrop-blur">
      <div class="max-w-7xl mx-auto px-4 py-6">
        <div class="flex justify-center">
          <AppLogo size="lg" />
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 py-12">
      <h1 class="text-4xl font-bold text-center mb-12 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
        Team Highlights
      </h1>

      <div v-if="loading" class="text-center py-12">
        <p class="text-gray-400">Loading statistics...</p>
      </div>

      <div v-else class="space-y-8">
        <!-- Top Stats Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-gray-800/70 backdrop-blur rounded-xl p-6 border border-blue-500/20">
            <div class="text-center">
              <div class="text-5xl font-bold text-blue-400 mb-2">{{ teamStats.totalGames }}</div>
              <div class="text-gray-400 uppercase text-sm">Total Games</div>
            </div>
          </div>

          <div class="bg-gray-800/70 backdrop-blur rounded-xl p-6 border border-green-500/20">
            <div class="text-center">
              <div class="text-5xl font-bold text-green-400 mb-2">{{ teamStats.winrate }}%</div>
              <div class="text-gray-400 uppercase text-sm">Overall Winrate</div>
            </div>
          </div>

          <div class="bg-gray-800/70 backdrop-blur rounded-xl p-6 border border-purple-500/20">
            <div class="text-center">
              <div class="text-5xl font-bold text-purple-400 mb-2">{{ teamStats.competitiveWR }}%</div>
              <div class="text-gray-400 uppercase text-sm">Competitive Winrate</div>
            </div>
          </div>
        </div>

        <!-- Player Rankings -->
        <div class="bg-gray-800/70 backdrop-blur rounded-xl p-6 border border-gray-700">
          <h2 class="text-2xl font-bold mb-6 text-blue-400">Player Rankings</h2>
          <div class="space-y-4">
            <div
              v-for="(player, index) in playerRankings"
              :key="player.id"
              class="flex items-center justify-between bg-gray-700/50 rounded-lg p-4"
            >
              <div class="flex items-center gap-4">
                <div class="text-2xl font-bold text-gray-400">#{{ index + 1 }}</div>
                <div>
                  <div class="font-semibold text-lg">{{ player.summoner_name }}</div>
                  <div class="text-sm text-gray-400 uppercase">{{ player.role }}</div>
                </div>
              </div>
              <div class="text-right">
                <div class="text-xl font-bold text-blue-400">{{ player.rank || 'Unranked' }}</div>
                <div class="text-sm text-gray-400">{{ player.lp || 0 }} LP</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Matches -->
        <div class="bg-gray-800/70 backdrop-blur rounded-xl p-6 border border-gray-700">
          <h2 class="text-2xl font-bold mb-6 text-blue-400">Recent Matches</h2>
          <div class="space-y-3">
            <div
              v-for="match in recentMatches"
              :key="match.id"
              :class="[
                'flex items-center justify-between rounded-lg p-4',
                match.result === 'win' ? 'bg-green-900/30 border-l-4 border-green-500' : 'bg-red-900/30 border-l-4 border-red-500'
              ]"
            >
              <div>
                <div class="font-semibold">{{ match.opponent }}</div>
                <div class="text-sm text-gray-400">{{ match.date }}</div>
              </div>
              <div :class="match.result === 'win' ? 'text-green-400' : 'text-red-400'" class="font-bold uppercase">
                {{ match.result }}
              </div>
            </div>
          </div>
        </div>

        <!-- Hall of Fame -->
        <div class="bg-gradient-to-br from-yellow-900/20 to-orange-900/20 backdrop-blur rounded-xl p-6 border border-yellow-500/30">
          <h2 class="text-2xl font-bold mb-6 text-yellow-400">Hall of Fame</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-gray-800/50 rounded-lg p-4">
              <div class="text-sm text-gray-400 mb-2">Most Pentakills</div>
              <div class="flex items-center justify-between">
                <div class="font-semibold">{{ hallOfFame.pentakills.player }}</div>
                <div class="text-2xl font-bold text-yellow-400">{{ hallOfFame.pentakills.count }}</div>
              </div>
            </div>

            <div class="bg-gray-800/50 rounded-lg p-4">
              <div class="text-sm text-gray-400 mb-2">Highest KDA</div>
              <div class="flex items-center justify-between">
                <div class="font-semibold">{{ hallOfFame.highestKDA.player }}</div>
                <div class="text-2xl font-bold text-yellow-400">{{ hallOfFame.highestKDA.kda }}</div>
              </div>
            </div>

            <div class="bg-gray-800/50 rounded-lg p-4">
              <div class="text-sm text-gray-400 mb-2">Best CS/min</div>
              <div class="flex items-center justify-between">
                <div class="font-semibold">{{ hallOfFame.bestCS.player }}</div>
                <div class="text-2xl font-bold text-yellow-400">{{ hallOfFame.bestCS.cs }}</div>
              </div>
            </div>

            <div class="bg-gray-800/50 rounded-lg p-4">
              <div class="text-sm text-gray-400 mb-2">Vision King</div>
              <div class="flex items-center justify-between">
                <div class="font-semibold">{{ hallOfFame.bestVision.player }}</div>
                <div class="text-2xl font-bold text-yellow-400">{{ hallOfFame.bestVision.vision }}</div>
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
import { playersApi, draftsApi } from '@/api'
import AppLogo from '@/components/AppLogo.vue'

const loading = ref(true)

const teamStats = ref({
  totalGames: 0,
  winrate: 0,
  competitiveWR: 0,
})

const playerRankings = ref<any[]>([])

const recentMatches = ref<any[]>([])

const hallOfFame = ref({
  pentakills: { player: '-', count: 0 },
  highestKDA: { player: '-', kda: 0 },
  bestCS: { player: '-', cs: 0 },
  bestVision: { player: '-', vision: 0 },
})

async function loadStats() {
  try {
    const [playersRes, draftsRes] = await Promise.all([
      playersApi.list(),
      draftsApi.list(),
    ])

    playerRankings.value = playersRes.data.map((p: any) => ({
      ...p,
      rank: 'Diamond II', // Mock data - à remplacer par vraies données
      lp: Math.floor(Math.random() * 100),
    }))

    const drafts = draftsRes.data
    const wins = drafts.filter((d: any) => d.result === 'win').length
    teamStats.value = {
      totalGames: drafts.length,
      winrate: drafts.length > 0 ? Math.round((wins / drafts.length) * 100) : 0,
      competitiveWR: 65, // Mock data - à calculer depuis les games "competitive"
    }

    recentMatches.value = drafts.slice(0, 5).map((d: any) => ({
      id: d.id,
      opponent: d.opponent_name,
      date: d.date,
      result: d.result || 'pending',
    }))

    // Mock Hall of Fame - à remplacer par vraies stats
    hallOfFame.value = {
      pentakills: { player: playersRes.data[0]?.summoner_name || '-', count: 3 },
      highestKDA: { player: playersRes.data[1]?.summoner_name || '-', kda: 4.2 },
      bestCS: { player: playersRes.data[2]?.summoner_name || '-', cs: 8.5 },
      bestVision: { player: playersRes.data[3]?.summoner_name || '-', vision: 2.1 },
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStats()
})
</script>
