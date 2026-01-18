<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-900 via-gray-900 to-purple-900">
    <div class="bg-gray-800/50 border-b border-gray-700 backdrop-blur">
      <div class="max-w-7xl mx-auto px-4 py-6">
        <div class="flex justify-between items-center">
          <div class="flex-1"></div>
          <div class="flex justify-center flex-1">
            <AppLogo size="lg" />
          </div>
          <div class="flex-1 flex justify-end">
            <router-link
              to="/"
              class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded transition text-sm font-medium"
            >
              Staff Login
            </router-link>
          </div>
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
import { playersApi, statsApi, gamesApi } from '@/api'
import AppLogo from '@/components/AppLogo.vue'
import type { Player, Game } from '@/types'

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
    const [playersRes, highlightsRes] = await Promise.all([
      playersApi.list(),
      statsApi.getTeamHighlights(),
    ])

    const players: Player[] = playersRes.data
    const highlights = highlightsRes.data

    // Update team stats with real data
    teamStats.value = {
      totalGames: highlights.total_games,
      winrate: highlights.winrate,
      competitiveWR: highlights.competitive_winrate,
    }

    // Get player rankings with rank info from their main accounts
    playerRankings.value = players
      .map((p) => {
        const mainAccount = p.riot_accounts.find((acc) => acc.is_main) || p.riot_accounts[0]
        return {
          ...p,
          rank: mainAccount?.rank_tier
            ? `${mainAccount.rank_tier} ${mainAccount.rank_division || ''}`
            : 'Unranked',
          lp: mainAccount?.lp || 0,
        }
      })
      .sort((a, b) => (b.lp || 0) - (a.lp || 0))

    // Recent matches from team highlights
    recentMatches.value = highlights.recent_matches.slice(0, 5).map((match) => ({
      id: match.id,
      opponent: 'Ranked Match', // Generic since we don't track opponent for soloq
      date: new Date(match.game_date).toLocaleDateString(),
      result: match.stats.win ? 'win' : 'loss',
    }))

    // Hall of Fame - pentakills
    const pentakills = await gamesApi.getPentakills()
    const pentakillsByPlayer = new Map<number, number>()

    for (const game of pentakills.data) {
      const player = players.find((p) =>
        p.riot_accounts.some((acc) => acc.id === game.riot_account_id)
      )
      if (player) {
        pentakillsByPlayer.set(player.id, (pentakillsByPlayer.get(player.id) || 0) + 1)
      }
    }

    // Get player with most pentakills
    let maxPentakills = 0
    let pentakillKing = '-'
    pentakillsByPlayer.forEach((count, playerId) => {
      if (count > maxPentakills) {
        maxPentakills = count
        const player = players.find((p) => p.id === playerId)
        pentakillKing = player?.summoner_name || '-'
      }
    })

    // Compute best stats from player stats
    const playerStatsList = await Promise.all(
      players.map(async (p) => {
        try {
          const statsRes = await statsApi.getPlayerStats(p.id)
          return { player: p.summoner_name, stats: statsRes.data }
        } catch {
          return null
        }
      })
    )

    const validStats = playerStatsList.filter((s) => s !== null)

    const bestKDA = validStats.reduce(
      (best, current) =>
        current!.stats.avg_kda > (best?.stats.avg_kda || 0) ? current : best,
      validStats[0]
    )

    const bestCS = validStats.reduce(
      (best, current) =>
        current!.stats.avg_cs_per_min > (best?.stats.avg_cs_per_min || 0) ? current : best,
      validStats[0]
    )

    const bestVision = validStats.reduce(
      (best, current) =>
        current!.stats.avg_vision_score_per_min > (best?.stats.avg_vision_score_per_min || 0)
          ? current
          : best,
      validStats[0]
    )

    hallOfFame.value = {
      pentakills: { player: pentakillKing, count: maxPentakills },
      highestKDA: {
        player: bestKDA?.player || '-',
        kda: bestKDA?.stats.avg_kda || 0,
      },
      bestCS: {
        player: bestCS?.player || '-',
        cs: bestCS?.stats.avg_cs_per_min || 0,
      },
      bestVision: {
        player: bestVision?.player || '-',
        vision: bestVision?.stats.avg_vision_score_per_min || 0,
      },
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
