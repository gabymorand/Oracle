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

          <!-- Email for Calendar Invitations -->
          <div class="mt-4 p-4 bg-gray-700 rounded-lg">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="text-gray-400 text-sm">Email (for calendar invitations):</span>
                <span v-if="player.email && !editingEmail" class="text-white">{{ player.email }}</span>
                <span v-else-if="!editingEmail" class="text-gray-500 text-sm italic">Not set</span>
              </div>
              <button
                v-if="!editingEmail"
                @click="startEditEmail"
                class="text-blue-400 hover:text-blue-300 text-sm"
              >
                {{ player.email ? 'Edit' : 'Add Email' }}
              </button>
            </div>
            <div v-if="editingEmail" class="mt-2 flex gap-2">
              <input
                v-model="emailInput"
                type="email"
                placeholder="player@gmail.com"
                class="flex-1 bg-gray-600 border border-gray-500 rounded px-3 py-2 text-sm"
              />
              <button
                @click="saveEmail"
                :disabled="savingEmail"
                class="bg-green-600 hover:bg-green-700 disabled:bg-green-800 px-3 py-1 rounded text-sm"
              >
                {{ savingEmail ? 'Saving...' : 'Save' }}
              </button>
              <button
                @click="cancelEditEmail"
                class="bg-gray-600 hover:bg-gray-500 px-3 py-1 rounded text-sm"
              >
                Cancel
              </button>
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
                <div class="flex-1">
                  <div class="flex items-center gap-2">
                    <span class="font-medium">{{ account.summoner_name }}#{{ account.tag_line }}</span>
                    <span v-if="account.is_main" class="text-xs bg-yellow-600 px-2 py-1 rounded">Main</span>
                  </div>
                  <div v-if="account.rank_tier" class="text-sm mt-1 space-y-1">
                    <div class="flex items-center gap-3">
                      <RankBadge
                        :tier="account.rank_tier"
                        :division="account.rank_division"
                        :lp="account.lp"
                      />
                      <span v-if="account.wins && account.losses" class="text-xs text-gray-500">
                        {{ account.wins }}W {{ account.losses }}L
                        ({{ Math.round((account.wins / (account.wins + account.losses)) * 100) }}%)
                      </span>
                    </div>
                    <div v-if="account.peak_tier" class="text-xs text-yellow-400 flex items-center gap-2">
                      🏆 Peak:
                      <RankBadge
                        :tier="account.peak_tier"
                        :division="account.peak_division"
                        :lp="account.peak_lp"
                        :show-lp="false"
                      />
                    </div>
                  </div>
                  <div v-else class="text-sm mt-1 flex items-center gap-2">
                    <span class="text-gray-500">Unranked</span>
                    <span class="text-xs text-orange-400">(API unavailable - click Refresh Stats)</span>
                  </div>
                </div>
                <div v-if="authStore.userRole !== 'player'" class="flex gap-2">
                  <button
                    @click="refreshStats(account.id)"
                    :disabled="refreshingAccounts.has(account.id)"
                    class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed px-3 py-1 rounded text-sm transition flex items-center gap-2"
                  >
                    <span v-if="refreshingAccounts.has(account.id)" class="animate-spin">⟳</span>
                    {{ refreshingAccounts.has(account.id) ? 'Refreshing...' : 'Refresh Stats' }}
                  </button>
                  <button
                    v-if="!account.rank_tier"
                    @click="openManualRankDialog(account)"
                    class="bg-orange-600 hover:bg-orange-700 px-3 py-1 rounded text-sm transition"
                    title="Enter rank manually when API is unavailable"
                  >
                    Manual Entry
                  </button>
                  <button
                    @click="deleteRiotAccount(account.id)"
                    class="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm transition"
                    title="Delete account"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>

            <div v-if="authStore.userRole !== 'player' && !showAddAccount" class="mt-3 flex gap-2">
              <button
                @click="showAddAccount = true"
                class="bg-green-600 hover:bg-green-700 px-4 py-2 rounded text-sm transition"
              >
                + Add Riot Account
              </button>
              <button
                v-if="player?.riot_accounts?.some(account => !account.rank_tier)"
                @click="refreshAllUnrankedAccounts"
                :disabled="isRefreshingAll"
                class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed px-4 py-2 rounded text-sm transition flex items-center gap-2"
              >
                <span v-if="isRefreshingAll" class="animate-spin">⟳</span>
                {{ isRefreshingAll ? 'Refreshing All...' : 'Refresh All Unranked' }}
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

        <!-- Detailed Stats Tabs -->
        <div v-if="player.riot_accounts.length > 0" class="mt-6 space-y-6">
          <div v-for="account in player.riot_accounts" :key="`tabs-${account.id}`">
            <h2 class="text-2xl font-bold mb-4">
              {{ account.summoner_name }}#{{ account.tag_line }} - Detailed Analytics
            </h2>

            <!-- Tabs -->
            <div class="flex gap-2 mb-6 border-b border-gray-700">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                @click="activeTab = tab.id"
                :class="[
                  'px-6 py-3 font-semibold transition relative',
                  activeTab === tab.id
                    ? 'text-blue-400 border-b-2 border-blue-400'
                    : 'text-gray-400 hover:text-gray-200'
                ]"
              >
                {{ tab.label }}
              </button>
            </div>

            <!-- Tab Content -->
            <div v-if="activeTab === 'overview'">
              <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <RankGraph :riot-account-id="account.id" />
                <StatsGraph :riot-account-id="account.id" />
              </div>
            </div>

            <div v-else-if="activeTab === 'champions'">
              <ChampionStats :riot-account-id="account.id" />
            </div>

            <div v-else-if="activeTab === 'performance'">
              <div class="space-y-6">
                <RankGraph :riot-account-id="account.id" />
                <StatsGraph :riot-account-id="account.id" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Manual Rank Entry Dialog -->
  <div v-if="showManualRankDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-gray-800 p-6 rounded-lg w-full max-w-md">
      <h3 class="text-lg font-semibold mb-4">Manual Rank Entry</h3>
      <p class="text-sm text-gray-400 mb-4">
        Enter rank information for {{ manualRankAccount?.summoner_name }}#{{ manualRankAccount?.tag_line }}
      </p>

      <div class="mb-4 p-3 bg-blue-900/20 border border-blue-500/30 rounded">
        <p class="text-sm text-blue-300 mb-2">💡 Pro tip: If you know the Summoner ID, enter it below to enable automatic stats refresh later.</p>
        <div>
          <label class="block text-sm font-medium mb-1">Summoner ID (Optional)</label>
          <input
            v-model="manualRankData.summoner_id"
            type="text"
            placeholder="e.g., abc123def456"
            class="w-full bg-gray-700 rounded px-3 py-2"
          />
        </div>
      </div>

      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Tier</label>
            <select v-model="manualRankData.rank_tier" class="w-full bg-gray-700 rounded px-3 py-2">
              <option value="">Select Tier</option>
              <option value="IRON">Iron</option>
              <option value="BRONZE">Bronze</option>
              <option value="SILVER">Silver</option>
              <option value="GOLD">Gold</option>
              <option value="PLATINUM">Platinum</option>
              <option value="EMERALD">Emerald</option>
              <option value="DIAMOND">Diamond</option>
              <option value="MASTER">Master</option>
              <option value="GRANDMASTER">Grandmaster</option>
              <option value="CHALLENGER">Challenger</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Division</label>
            <select v-model="manualRankData.rank_division" class="w-full bg-gray-700 rounded px-3 py-2">
              <option value="">Select Division</option>
              <option value="IV">IV</option>
              <option value="III">III</option>
              <option value="II">II</option>
              <option value="I">I</option>
            </select>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">LP</label>
          <input
            v-model.number="manualRankData.lp"
            type="number"
            min="0"
            max="100"
            class="w-full bg-gray-700 rounded px-3 py-2"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Wins</label>
            <input
              v-model.number="manualRankData.wins"
              type="number"
              min="0"
              class="w-full bg-gray-700 rounded px-3 py-2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Losses</label>
            <input
              v-model.number="manualRankData.losses"
              type="number"
              min="0"
              class="w-full bg-gray-700 rounded px-3 py-2"
            />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Peak Tier</label>
            <select v-model="manualRankData.peak_tier" class="w-full bg-gray-700 rounded px-3 py-2">
              <option value="">Select Tier</option>
              <option value="IRON">Iron</option>
              <option value="BRONZE">Bronze</option>
              <option value="SILVER">Silver</option>
              <option value="GOLD">Gold</option>
              <option value="PLATINUM">Platinum</option>
              <option value="EMERALD">Emerald</option>
              <option value="DIAMOND">Diamond</option>
              <option value="MASTER">Master</option>
              <option value="GRANDMASTER">Grandmaster</option>
              <option value="CHALLENGER">Challenger</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Peak Division</label>
            <select v-model="manualRankData.peak_division" class="w-full bg-gray-700 rounded px-3 py-2">
              <option value="">Select Division</option>
              <option value="IV">IV</option>
              <option value="III">III</option>
              <option value="II">II</option>
              <option value="I">I</option>
            </select>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Peak LP</label>
          <input
            v-model.number="manualRankData.peak_lp"
            type="number"
            min="0"
            max="100"
            class="w-full bg-gray-700 rounded px-3 py-2"
          />
        </div>
      </div>

      <div class="flex gap-2 mt-6">
        <button
          @click="saveManualRank"
          class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded transition flex-1"
        >
          Save Rank
        </button>
        <button
          @click="closeManualRankDialog"
          class="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded transition"
        >
          Cancel
        </button>
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
import RankBadge from '@/components/RankBadge.vue'
import RankGraph from '@/components/RankGraph.vue'
import StatsGraph from '@/components/StatsGraph.vue'
import ChampionStats from '@/components/ChampionStats.vue'

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
const activeTab = ref('overview')

// Manual rank entry
const showManualRankDialog = ref(false)
const manualRankAccount = ref<any>(null)
const manualRankData = ref({
  rank_tier: '',
  rank_division: '',
  lp: 0,
  wins: 0,
  losses: 0,
  peak_tier: '',
  peak_division: '',
  peak_lp: 0,
  summoner_id: '' // Optional summoner ID for future API calls
})

// Loading states
const refreshingAccounts = ref<Set<number>>(new Set())
const isRefreshingAll = ref(false)

// Email editing
const editingEmail = ref(false)
const emailInput = ref('')
const savingEmail = ref(false)

function startEditEmail() {
  emailInput.value = player.value?.email || ''
  editingEmail.value = true
}

function cancelEditEmail() {
  editingEmail.value = false
  emailInput.value = ''
}

async function saveEmail() {
  if (!player.value) return
  savingEmail.value = true
  try {
    await playersApi.update(player.value.id, { email: emailInput.value || null })
    player.value.email = emailInput.value || undefined
    editingEmail.value = false
  } catch (error) {
    console.error('Failed to save email:', error)
    alert('Failed to save email')
  } finally {
    savingEmail.value = false
  }
}

const tabs = [
  { id: 'overview', label: 'Overview' },
  { id: 'champions', label: 'Champions' },
  { id: 'performance', label: 'Performance' }
]
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

    // Auto-refresh stats for accounts without rank info (disabled for performance)
    // TODO: Add manual "Refresh All" button instead of auto-refresh
    /*
    if (player.value?.riot_accounts) {
      const accountsToRefresh = player.value.riot_accounts.filter(account => !account.rank_tier)
      if (accountsToRefresh.length > 0) {
        console.log(`Auto-refreshing stats for ${accountsToRefresh.length} account(s) without rank info`)
        try {
          await Promise.all(
            accountsToRefresh.map(account => refreshStats(account.id, false))
          )
          // Reload player data after refresh
          const updatedPlayerRes = await playersApi.get(playerId)
          player.value = updatedPlayerRes.data
        } catch (error) {
          console.warn('Auto-refresh failed, but continuing with existing data:', error)
        }
      }
    }
    */
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
  if (!player.value) return

  let summonerName = newAccount.value.summoner_name
  let tagLine = newAccount.value.tag_line

  // Auto-parse if user entered "name#tag" format
  if (summonerName && summonerName.includes('#') && !tagLine) {
    const parts = summonerName.split('#')
    summonerName = parts[0]
    tagLine = parts[1]
  }

  if (!summonerName || !tagLine) {
    alert('Please enter both summoner name and tag line (or use format: name#tag)')
    return
  }

  try {
    await riotAccountsApi.create(player.value.id, {
      summoner_name: summonerName,
      tag_line: tagLine,
      is_main: newAccount.value.is_main
    })
    const playerRes = await playersApi.get(player.value.id)
    player.value = playerRes.data
    showAddAccount.value = false
    newAccount.value = { summoner_name: '', tag_line: '', is_main: false }
    alert('Riot account added successfully!')
  } catch (error: any) {
    console.error('Failed to add Riot account:', error)
    const errorMsg = error.response?.data?.detail || 'Failed to add Riot account. Please check the summoner name and tag.'
    alert(errorMsg)
  }
}

async function deleteRiotAccount(accountId: number) {
  if (!player.value) return

  if (!confirm('Are you sure you want to delete this Riot account? This will also delete all associated game stats.')) {
    return
  }

  try {
    await riotAccountsApi.delete(accountId)
    const playerRes = await playersApi.get(player.value.id)
    player.value = playerRes.data
    alert('Riot account deleted successfully!')
  } catch (error) {
    console.error('Failed to delete Riot account:', error)
    alert('Failed to delete Riot account. Please try again.')
  }
}

async function refreshStats(riotAccountId: number, showSuccessAlert = true) {
  refreshingAccounts.value.add(riotAccountId)
  try {
    await statsApi.refreshStats(riotAccountId)
    if (player.value) {
      // Reload both player data (for rank info) and stats
      const [playerRes, statsRes] = await Promise.all([
        playersApi.get(player.value.id),
        statsApi.getPlayerStats(player.value.id)
      ])
      player.value = playerRes.data
      stats.value = statsRes.data
    }
    if (showSuccessAlert) {
      alert('Stats refreshed successfully!')
    }
  } catch (error: any) {
    console.error('Failed to refresh stats:', error)
    const errorMsg = error.response?.data?.detail || 'Failed to refresh stats. The Riot API may be unavailable or the account may not be valid.'
    
    // Check for specific API errors
    let displayMsg = errorMsg
    if (errorMsg.includes('401') || errorMsg.includes('Unauthorized')) {
      displayMsg = '❌ Riot API Error: The API key is invalid or expired.\n\nPlease contact an administrator to configure a valid Riot API key.'
    } else if (errorMsg.includes('403') || errorMsg.includes('Forbidden')) {
      displayMsg = '❌ Riot API Error: Access forbidden. Please check API key permissions.'
    } else if (errorMsg.includes('404')) {
      displayMsg = '❌ Account not found: The summoner name/tag may be incorrect.'
    }
    
    if (showSuccessAlert) {
      const accountName = player.value?.riot_accounts.find(a => a.id === riotAccountId)?.summoner_name || 'Unknown'
      alert(`${displayMsg}\n\nAccount: ${accountName}`)
    } else {
      console.warn(`Stats refresh failed for account ${riotAccountId}:`, errorMsg)
    }
  } finally {
    refreshingAccounts.value.delete(riotAccountId)
  }
}

async function refreshAllUnrankedAccounts() {
  if (!player.value?.riot_accounts) return

  const accountsToRefresh = player.value.riot_accounts.filter(account => !account.rank_tier)
  if (accountsToRefresh.length === 0) return

  isRefreshingAll.value = true
  try {
    console.log(`Manually refreshing stats for ${accountsToRefresh.length} unranked account(s)`)
    await Promise.all(
      accountsToRefresh.map(account => refreshStats(account.id, false))
    )
    // Reload player data after refresh
    const playerId = Number(route.params.id)
    const updatedPlayerRes = await playersApi.get(playerId)
    player.value = updatedPlayerRes.data
    alert(`Successfully refreshed ${accountsToRefresh.length} account(s)!`)
  } catch (error) {
    console.warn('Manual refresh failed:', error)
    alert('Some accounts failed to refresh. Check the console for details.')
  } finally {
    isRefreshingAll.value = false
  }
}

function openManualRankDialog(account: any) {
  manualRankAccount.value = account
  manualRankData.value = {
    rank_tier: account.rank_tier || '',
    rank_division: account.rank_division || '',
    lp: account.lp || 0,
    wins: account.wins || 0,
    losses: account.losses || 0,
    peak_tier: account.peak_tier || '',
    peak_division: account.peak_division || '',
    peak_lp: account.peak_lp || 0
  }
  showManualRankDialog.value = true
}

function closeManualRankDialog() {
  showManualRankDialog.value = false
  manualRankAccount.value = null
}

async function saveManualRank() {
  if (!manualRankAccount.value || !player.value) return

  try {
    await riotAccountsApi.updateRank(manualRankAccount.value.id, manualRankData.value)
    
    // Reload player data to reflect changes
    const playerRes = await playersApi.get(player.value.id)
    player.value = playerRes.data
    
    alert('Rank information saved successfully!')
    closeManualRankDialog()
  } catch (error) {
    console.error('Failed to save manual rank:', error)
    alert('Failed to save rank information.')
  }
}

onMounted(() => {
  loadPlayerData()
})
</script>
