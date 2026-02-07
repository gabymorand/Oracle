<template>
  <div class="min-h-screen bg-gray-900">
    <AppNavbar />

    <div class="max-w-7xl mx-auto px-4 py-8">
      <!-- Header -->
      <div class="mb-8 flex justify-between items-center">
        <div>
          <h1 class="text-3xl font-bold">Team Composition</h1>
          <p class="text-gray-400 mt-1">Vue d'ensemble de l'equipe</p>
        </div>
        <div class="flex gap-2">
          <button
            v-if="authStore.userRole !== 'player'"
            @click="showAddPlayer = true"
            class="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg transition flex items-center gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Add Player
          </button>
          <router-link
            v-if="authStore.userRole === 'head_coach'"
            to="/coaches"
            class="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg transition"
          >
            Manage Coaches
          </router-link>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12 text-gray-400">
        Chargement de l'equipe...
      </div>

      <div v-else>
        <!-- Team Visual Layout -->
        <div class="bg-gray-800 rounded-xl p-6 mb-8">
          <h2 class="text-xl font-semibold mb-6 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            Roster
          </h2>

          <!-- 5 Position Layout -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <div
              v-for="role in roleOrder"
              :key="role"
              @click="navigateToPlayer(getPlayerByRole(role))"
              :class="[
                'relative rounded-xl p-4 transition cursor-pointer border-2 group',
                getPlayerByRole(role)
                  ? 'bg-gray-700 hover:bg-gray-650 border-transparent'
                  : 'bg-gray-800/50 border-dashed border-gray-600',
              ]"
            >
              <!-- Role Badge -->
              <div
                :class="[
                  'absolute -top-3 left-4 px-3 py-1 rounded-full text-xs font-bold uppercase',
                  getRoleBgColor(role),
                ]"
              >
                {{ role }}
              </div>

              <!-- Player Content -->
              <div v-if="getPlayerByRole(role)" class="pt-2">
                <div class="flex items-center gap-3 mb-3">
                  <!-- Rank Icon (or role fallback if unranked) -->
                  <div :class="['w-12 h-12 rounded-lg flex items-center justify-center', getRoleBgColor(role) + '/20']">
                    <img
                      v-if="getPlayerRankIcon(getPlayerByRole(role)!)"
                      :src="getPlayerRankIcon(getPlayerByRole(role)!)"
                      :alt="getMainAccountRank(getPlayerByRole(role)!)"
                      class="w-10 h-10"
                    />
                    <span v-else class="text-2xl">{{ getRoleEmoji(role) }}</span>
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="font-bold text-lg truncate">{{ getPlayerByRole(role)!.summoner_name }}</div>
                    <div class="text-sm text-gray-400">
                      {{ getMainAccountRank(getPlayerByRole(role)!) }}
                    </div>
                  </div>
                </div>

                <!-- Quick Stats -->
                <div v-if="getPlayerStats(getPlayerByRole(role)!.id)" class="grid grid-cols-2 gap-2 text-sm">
                  <div class="bg-gray-800/50 rounded px-2 py-1">
                    <span class="text-gray-400">Games:</span>
                    <span class="ml-1 font-medium">{{ getPlayerStats(getPlayerByRole(role)!.id)!.total_games }}</span>
                  </div>
                  <div class="bg-gray-800/50 rounded px-2 py-1">
                    <span class="text-gray-400">WR:</span>
                    <span
                      :class="[
                        'ml-1 font-medium',
                        getPlayerStats(getPlayerByRole(role)!.id)!.winrate >= 50 ? 'text-green-400' : 'text-red-400',
                      ]"
                    >
                      {{ getPlayerStats(getPlayerByRole(role)!.id)!.winrate.toFixed(0) }}%
                    </span>
                  </div>
                </div>

                <!-- Delete button -->
                <button
                  v-if="authStore.userRole !== 'player'"
                  @click.stop="confirmDeletePlayer(getPlayerByRole(role)!)"
                  class="absolute top-2 right-2 text-red-400 hover:text-red-300 p-1 opacity-0 group-hover:opacity-100 transition"
                  title="Supprimer"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                </button>
              </div>

              <!-- Empty Slot -->
              <div v-else class="pt-2 text-center py-6">
                <div class="text-gray-500 text-sm">Poste vacant</div>
                <button
                  v-if="authStore.userRole !== 'player'"
                  @click.stop="openAddPlayerForRole(role)"
                  class="mt-2 text-blue-400 hover:text-blue-300 text-sm"
                >
                  + Ajouter
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Team Stats Overview -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <!-- Quick Stats -->
          <div class="bg-gray-800 rounded-xl p-6">
            <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Stats Equipe
            </h2>
            <div v-if="teamHighlights" class="grid grid-cols-2 gap-4">
              <div class="bg-gray-700/50 rounded-lg p-4">
                <div class="text-3xl font-bold text-blue-400">{{ teamHighlights.total_games }}</div>
                <div class="text-sm text-gray-400">Games totales</div>
              </div>
              <div class="bg-gray-700/50 rounded-lg p-4">
                <div class="text-3xl font-bold" :class="teamHighlights.winrate >= 50 ? 'text-green-400' : 'text-red-400'">
                  {{ teamHighlights.winrate.toFixed(1) }}%
                </div>
                <div class="text-sm text-gray-400">Winrate SoloQ</div>
              </div>
              <div class="bg-gray-700/50 rounded-lg p-4">
                <div class="text-3xl font-bold text-purple-400">{{ teamHighlights.competitive_games }}</div>
                <div class="text-sm text-gray-400">Games Compet</div>
              </div>
              <div class="bg-gray-700/50 rounded-lg p-4">
                <div class="text-3xl font-bold text-yellow-400">{{ teamHighlights.total_pentakills }}</div>
                <div class="text-sm text-gray-400">Pentakills</div>
              </div>
            </div>
            <div v-else class="text-gray-500 text-center py-8">
              Aucune donnee disponible
            </div>
          </div>

          <!-- Coaches -->
          <div class="bg-gray-800 rounded-xl p-6">
            <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              Staff
            </h2>
            <div v-if="coaches.length > 0" class="space-y-3">
              <div
                v-for="coach in coaches"
                :key="coach.id"
                class="flex items-center justify-between bg-gray-700/50 rounded-lg p-3"
              >
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-full bg-purple-600 flex items-center justify-center font-bold">
                    {{ coach.name.charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <div class="font-medium">{{ coach.name }}</div>
                    <div class="text-sm text-gray-400">{{ coach.role || 'Coach' }}</div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-gray-500 text-center py-8">
              Aucun coach enregistre
            </div>
          </div>
        </div>

        <!-- Quick Links -->
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <router-link
            to="/calendar"
            class="bg-gray-800 hover:bg-gray-750 rounded-xl p-4 transition flex items-center gap-3"
          >
            <div class="w-12 h-12 rounded-lg bg-blue-600/20 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <div class="font-semibold">Calendrier</div>
              <div class="text-sm text-gray-400">Planning & dispos</div>
            </div>
          </router-link>

          <router-link
            to="/scrims"
            class="bg-gray-800 hover:bg-gray-750 rounded-xl p-4 transition flex items-center gap-3"
          >
            <div class="w-12 h-12 rounded-lg bg-red-600/20 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <div class="font-semibold">Scrims</div>
              <div class="text-sm text-gray-400">Historique & liens</div>
            </div>
          </router-link>

          <router-link
            to="/drafts"
            class="bg-gray-800 hover:bg-gray-750 rounded-xl p-4 transition flex items-center gap-3"
          >
            <div class="w-12 h-12 rounded-lg bg-green-600/20 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div>
              <div class="font-semibold">Drafts</div>
              <div class="text-sm text-gray-400">Historique picks</div>
            </div>
          </router-link>

          <router-link
            to="/tier-list"
            class="bg-gray-800 hover:bg-gray-750 rounded-xl p-4 transition flex items-center gap-3"
          >
            <div class="w-12 h-12 rounded-lg bg-yellow-600/20 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
            </div>
            <div>
              <div class="font-semibold">Tier List</div>
              <div class="text-sm text-gray-400">Champions par joueur</div>
            </div>
          </router-link>

          <router-link
            to="/analytics"
            class="bg-gray-800 hover:bg-gray-750 rounded-xl p-4 transition flex items-center gap-3"
          >
            <div class="w-12 h-12 rounded-lg bg-cyan-600/20 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <div class="font-semibold">Analytics</div>
              <div class="text-sm text-gray-400">Stats detaillees</div>
            </div>
          </router-link>
        </div>
      </div>
    </div>

    <!-- Add Player Modal -->
    <div
      v-if="showAddPlayer"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
      @click.self="showAddPlayer = false"
    >
      <div class="bg-gray-800 rounded-xl p-6 w-full max-w-md mx-4">
        <h3 class="text-xl font-semibold mb-4">Ajouter un joueur</h3>
        <form @submit.prevent="handleAddPlayer" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-2">Summoner Name</label>
            <input
              v-model="newPlayer.summoner_name"
              type="text"
              class="w-full px-4 py-2 bg-gray-700 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
              required
              placeholder="Pseudo du joueur"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2">Role</label>
            <div class="grid grid-cols-5 gap-2">
              <button
                v-for="role in roleOrder"
                :key="role"
                type="button"
                @click="newPlayer.role = role"
                :class="[
                  'py-2 px-3 rounded-lg text-sm font-medium transition border-2',
                  newPlayer.role === role
                    ? getRoleBorderColor(role)
                    : 'bg-gray-700 border-transparent hover:bg-gray-600',
                ]"
              >
                {{ role.toUpperCase() }}
              </button>
            </div>
          </div>
          <div class="flex gap-3 pt-2">
            <button
              type="button"
              @click="showAddPlayer = false"
              class="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
            >
              Annuler
            </button>
            <button
              type="submit"
              class="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition"
              :disabled="addingPlayer"
            >
              {{ addingPlayer ? 'Ajout...' : 'Ajouter' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="playerToDelete"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
      @click.self="playerToDelete = null"
    >
      <div class="bg-gray-800 rounded-xl p-6 w-full max-w-md mx-4">
        <h3 class="text-xl font-bold mb-4">Supprimer le joueur</h3>
        <p class="text-gray-300 mb-6">
          Supprimer <strong>{{ playerToDelete.summoner_name }}</strong> ?
          Cela supprimera aussi tous les comptes Riot et statistiques associes.
        </p>
        <div class="flex gap-3">
          <button
            @click="playerToDelete = null"
            class="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
          >
            Annuler
          </button>
          <button
            @click="deletePlayer"
            class="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition"
          >
            Supprimer
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { playersApi, statsApi, coachesApi } from '@/api'
import type { Player, PlayerStats, TeamHighlights, Coach } from '@/types'
import AppNavbar from '@/components/AppNavbar.vue'
import { getRankEmblemIcon } from '@/utils/champions'

const router = useRouter()
const authStore = useAuthStore()

const roleOrder = ['top', 'jungle', 'mid', 'adc', 'support'] as const

const players = ref<Player[]>([])
const playerStatsMap = ref<Map<number, PlayerStats>>(new Map())
const teamHighlights = ref<TeamHighlights | null>(null)
const coaches = ref<Coach[]>([])
const loading = ref(true)
const showAddPlayer = ref(false)
const addingPlayer = ref(false)
const playerToDelete = ref<Player | null>(null)
const newPlayer = ref({
  summoner_name: '',
  role: 'top',
})

function getPlayerByRole(role: string): Player | undefined {
  return players.value.find((p) => p.role.toLowerCase() === role.toLowerCase())
}

function getPlayerStats(playerId: number): PlayerStats | undefined {
  return playerStatsMap.value.get(playerId)
}

function getMainAccountRank(player: Player): string {
  const mainAccount = player.riot_accounts.find((a) => a.is_main) || player.riot_accounts[0]
  if (!mainAccount || !mainAccount.rank_tier) return 'Unranked'
  return `${mainAccount.rank_tier} ${mainAccount.rank_division || ''} ${mainAccount.lp ? `(${mainAccount.lp} LP)` : ''}`.trim()
}

function getPlayerRankIcon(player: Player): string {
  const mainAccount = player.riot_accounts.find((a) => a.is_main) || player.riot_accounts[0]
  if (!mainAccount || !mainAccount.rank_tier) return ''
  return getRankEmblemIcon(mainAccount.rank_tier)
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

function getRoleBorderColor(role: string): string {
  const colors: Record<string, string> = {
    top: 'border-red-500 bg-red-500/20 text-red-400',
    jungle: 'border-green-500 bg-green-500/20 text-green-400',
    mid: 'border-blue-500 bg-blue-500/20 text-blue-400',
    adc: 'border-yellow-500 bg-yellow-500/20 text-yellow-400',
    support: 'border-purple-500 bg-purple-500/20 text-purple-400',
  }
  return colors[role.toLowerCase()] || 'border-gray-500'
}

function getRoleEmoji(role: string): string {
  const emojis: Record<string, string> = {
    top: '🗡️',
    jungle: '🌲',
    mid: '⚡',
    adc: '🎯',
    support: '🛡️',
  }
  return emojis[role.toLowerCase()] || '👤'
}

function navigateToPlayer(player: Player | undefined) {
  if (player) {
    router.push(`/players/${player.id}`)
  }
}

function openAddPlayerForRole(role: string) {
  newPlayer.value.role = role
  showAddPlayer.value = true
}

function confirmDeletePlayer(player: Player) {
  playerToDelete.value = player
}

async function loadData() {
  loading.value = true
  try {
    const [playersRes, highlightsRes, coachesRes] = await Promise.all([
      playersApi.getPlayers(),
      statsApi.getTeamHighlights().catch(() => ({ data: null })),
      coachesApi.list().catch(() => ({ data: [] })),
    ])

    players.value = playersRes.data
    teamHighlights.value = highlightsRes.data
    coaches.value = coachesRes.data

    // Load stats for each player
    const statsPromises = players.value.map((p) =>
      statsApi.getPlayerStats(p.id).catch(() => ({ data: null }))
    )
    const statsResults = await Promise.all(statsPromises)
    statsResults.forEach((res, index) => {
      if (res.data) {
        playerStatsMap.value.set(players.value[index].id, res.data)
      }
    })
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

async function handleAddPlayer() {
  addingPlayer.value = true
  try {
    const response = await playersApi.create(newPlayer.value)
    players.value.push(response.data)
    showAddPlayer.value = false
    newPlayer.value = { summoner_name: '', role: 'top' }
  } catch (error) {
    console.error('Failed to add player:', error)
    alert('Erreur lors de l\'ajout du joueur')
  } finally {
    addingPlayer.value = false
  }
}

async function deletePlayer() {
  if (!playerToDelete.value) return

  try {
    await playersApi.delete(playerToDelete.value.id)
    players.value = players.value.filter((p) => p.id !== playerToDelete.value!.id)
    playerStatsMap.value.delete(playerToDelete.value.id)
    playerToDelete.value = null
  } catch (error) {
    console.error('Failed to delete player:', error)
    alert('Erreur lors de la suppression')
  }
}

onMounted(loadData)
</script>
