<template>
  <div class="min-h-screen bg-gray-900 text-white">
    <!-- Login Screen -->
    <div v-if="!isAuthenticated" class="flex items-center justify-center min-h-screen">
      <div class="bg-gray-800 p-8 rounded-lg shadow-xl max-w-md w-full">
        <h1 class="text-2xl font-bold mb-6 text-center">Admin Panel</h1>
        <form @submit.prevent="handleLogin">
          <div class="mb-4">
            <label class="block text-gray-400 text-sm mb-2">Admin Code</label>
            <input
              v-model="adminCode"
              type="password"
              class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-blue-500"
              placeholder="Enter admin code..."
              required
            />
          </div>
          <p v-if="loginError" class="text-red-400 text-sm mb-4">{{ loginError }}</p>
          <button
            type="submit"
            :disabled="isLoggingIn"
            class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 py-2 rounded font-medium transition"
          >
            {{ isLoggingIn ? 'Connecting...' : 'Login' }}
          </button>
        </form>
        <div class="mt-4 text-center">
          <router-link to="/" class="text-gray-400 hover:text-white text-sm">
            Back to main login
          </router-link>
        </div>
      </div>
    </div>

    <!-- Admin Dashboard -->
    <div v-else class="p-8">
      <!-- Header -->
      <div class="flex justify-between items-center mb-8">
        <div>
          <h1 class="text-3xl font-bold">Admin Dashboard</h1>
          <p class="text-gray-400">Manage all teams and their data</p>
        </div>
        <button
          @click="handleLogout"
          class="bg-red-600 hover:bg-red-700 px-4 py-2 rounded transition"
        >
          Logout
        </button>
      </div>

      <!-- Stats Overview -->
      <div v-if="dashboard" class="grid grid-cols-4 gap-4 mb-8">
        <div class="bg-gray-800 p-4 rounded-lg">
          <p class="text-gray-400 text-sm">Total Teams</p>
          <p class="text-3xl font-bold text-blue-400">{{ dashboard.total_teams }}</p>
        </div>
        <div class="bg-gray-800 p-4 rounded-lg">
          <p class="text-gray-400 text-sm">Total Players</p>
          <p class="text-3xl font-bold text-green-400">{{ dashboard.total_players }}</p>
        </div>
        <div class="bg-gray-800 p-4 rounded-lg">
          <p class="text-gray-400 text-sm">Total Coaches</p>
          <p class="text-3xl font-bold text-yellow-400">{{ dashboard.total_coaches }}</p>
        </div>
        <div class="bg-gray-800 p-4 rounded-lg">
          <p class="text-gray-400 text-sm">Total Drafts</p>
          <p class="text-3xl font-bold text-purple-400">{{ dashboard.total_drafts }}</p>
        </div>
      </div>

      <!-- Actions -->
      <div class="mb-6">
        <button
          @click="showCreateTeamModal = true"
          class="bg-green-600 hover:bg-green-700 px-4 py-2 rounded transition"
        >
          + New Team
        </button>
      </div>

      <!-- Teams List -->
      <div v-if="dashboard" class="space-y-4">
        <div
          v-for="team in dashboard.teams"
          :key="team.id"
          class="bg-gray-800 rounded-lg overflow-hidden"
        >
          <!-- Team Header -->
          <div
            class="p-4 flex items-center justify-between cursor-pointer hover:bg-gray-750"
            @click="toggleTeam(team.id)"
          >
            <div class="flex items-center gap-4">
              <svg
                class="w-5 h-5 transition-transform"
                :class="{ 'rotate-90': expandedTeams.has(team.id) }"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
              <div>
                <h3 class="text-xl font-semibold">{{ team.name }}</h3>
                <p class="text-gray-400 text-sm">
                  Code: <span class="font-mono bg-gray-700 px-2 py-0.5 rounded">{{ team.access_code }}</span>
                </p>
              </div>
            </div>
            <div class="flex items-center gap-6">
              <div class="text-center">
                <p class="text-lg font-semibold">{{ team.players_count }}</p>
                <p class="text-xs text-gray-400">Players</p>
              </div>
              <div class="text-center">
                <p class="text-lg font-semibold">{{ team.coaches_count }}</p>
                <p class="text-xs text-gray-400">Coaches</p>
              </div>
              <div class="text-center">
                <p class="text-lg font-semibold">{{ team.drafts_count }}</p>
                <p class="text-xs text-gray-400">Drafts</p>
              </div>
              <div class="text-center">
                <p class="text-lg font-semibold">{{ team.events_count }}</p>
                <p class="text-xs text-gray-400">Events</p>
              </div>
              <div class="flex gap-2" @click.stop>
                <button
                  @click="openEditTeam(team)"
                  class="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm transition"
                >
                  Edit
                </button>
                <button
                  @click="confirmDeleteTeam(team)"
                  class="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm transition"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>

          <!-- Team Details (expanded) -->
          <div v-if="expandedTeams.has(team.id)" class="border-t border-gray-700 p-4">
            <div v-if="loadingTeamDetails[team.id]" class="text-center py-4 text-gray-400">
              Loading details...
            </div>
            <div v-else-if="teamDetails[team.id]" class="grid grid-cols-2 gap-6">
              <!-- Players -->
              <div>
                <h4 class="text-lg font-semibold mb-3">Players ({{ teamDetails[team.id].players.length }})</h4>
                <div v-if="teamDetails[team.id].players.length === 0" class="text-gray-400 text-sm">
                  No players
                </div>
                <div v-else class="space-y-2">
                  <div
                    v-for="player in teamDetails[team.id].players"
                    :key="player.id"
                    class="flex items-center justify-between bg-gray-700 p-2 rounded"
                  >
                    <div class="flex items-center gap-3">
                      <span
                        class="w-2 h-2 rounded-full"
                        :class="getRoleColor(player.role)"
                      ></span>
                      <span>{{ player.summoner_name }}</span>
                      <span class="text-xs text-gray-400 uppercase">{{ player.role }}</span>
                      <span class="text-xs text-gray-500">({{ player.riot_accounts_count }} accounts)</span>
                    </div>
                    <button
                      @click="confirmDeletePlayer(player, team)"
                      class="text-red-400 hover:text-red-300 text-sm"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>

              <!-- Coaches -->
              <div>
                <h4 class="text-lg font-semibold mb-3">Coaches ({{ teamDetails[team.id].coaches.length }})</h4>
                <div v-if="teamDetails[team.id].coaches.length === 0" class="text-gray-400 text-sm">
                  No coaches
                </div>
                <div v-else class="space-y-2">
                  <div
                    v-for="coach in teamDetails[team.id].coaches"
                    :key="coach.id"
                    class="flex items-center justify-between bg-gray-700 p-2 rounded"
                  >
                    <div>
                      <span>{{ coach.name }}</span>
                      <span v-if="coach.role" class="text-xs text-gray-400 ml-2">({{ coach.role }})</span>
                    </div>
                    <button
                      @click="confirmDeleteCoach(coach, team)"
                      class="text-red-400 hover:text-red-300 text-sm"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoadingDashboard" class="text-center py-12 text-gray-400">
        Loading dashboard...
      </div>
    </div>

    <!-- Create Team Modal -->
    <div
      v-if="showCreateTeamModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showCreateTeamModal = false"
    >
      <div class="bg-gray-800 p-6 rounded-lg w-full max-w-md">
        <h2 class="text-xl font-semibold mb-4">Create New Team</h2>
        <form @submit.prevent="handleCreateTeam">
          <div class="mb-4">
            <label class="block text-gray-400 text-sm mb-2">Team Name</label>
            <input
              v-model="newTeam.name"
              type="text"
              class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-blue-500"
              placeholder="e.g., Team Alpha"
              required
            />
          </div>
          <div class="mb-4">
            <label class="block text-gray-400 text-sm mb-2">Access Code</label>
            <input
              v-model="newTeam.access_code"
              type="text"
              class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-blue-500"
              placeholder="e.g., ALPHA2026"
              required
            />
          </div>
          <p v-if="createTeamError" class="text-red-400 text-sm mb-4">{{ createTeamError }}</p>
          <div class="flex gap-3 justify-end">
            <button
              type="button"
              @click="showCreateTeamModal = false"
              class="px-4 py-2 bg-gray-600 hover:bg-gray-500 rounded transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="isCreatingTeam"
              class="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-800 rounded transition"
            >
              {{ isCreatingTeam ? 'Creating...' : 'Create Team' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Team Modal -->
    <div
      v-if="showEditTeamModal && editingTeam"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showEditTeamModal = false"
    >
      <div class="bg-gray-800 p-6 rounded-lg w-full max-w-md">
        <h2 class="text-xl font-semibold mb-4">Edit Team</h2>
        <form @submit.prevent="handleUpdateTeam">
          <div class="mb-4">
            <label class="block text-gray-400 text-sm mb-2">Team Name</label>
            <input
              v-model="editingTeam.name"
              type="text"
              class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-blue-500"
              required
            />
          </div>
          <div class="mb-4">
            <label class="block text-gray-400 text-sm mb-2">Access Code</label>
            <input
              v-model="editingTeam.access_code"
              type="text"
              class="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-blue-500"
              required
            />
          </div>
          <p v-if="editTeamError" class="text-red-400 text-sm mb-4">{{ editTeamError }}</p>
          <div class="flex gap-3 justify-end">
            <button
              type="button"
              @click="showEditTeamModal = false"
              class="px-4 py-2 bg-gray-600 hover:bg-gray-500 rounded transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="isUpdatingTeam"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 rounded transition"
            >
              {{ isUpdatingTeam ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="showDeleteModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showDeleteModal = false"
    >
      <div class="bg-gray-800 p-6 rounded-lg w-full max-w-md">
        <h2 class="text-xl font-semibold mb-4 text-red-400">Confirm Delete</h2>
        <p class="text-gray-300 mb-6">{{ deleteConfirmMessage }}</p>
        <div class="flex gap-3 justify-end">
          <button
            @click="showDeleteModal = false"
            class="px-4 py-2 bg-gray-600 hover:bg-gray-500 rounded transition"
          >
            Cancel
          </button>
          <button
            @click="executeDelete"
            :disabled="isDeleting"
            class="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-red-800 rounded transition"
          >
            {{ isDeleting ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { adminApi } from '@/api'
import type { AdminDashboard, AdminTeamStats, AdminTeamDetails, AdminPlayerSummary, AdminCoachSummary } from '@/types'

// Auth state
const isAuthenticated = ref(false)
const adminCode = ref('')
const isLoggingIn = ref(false)
const loginError = ref('')

// Dashboard state
const dashboard = ref<AdminDashboard | null>(null)
const isLoadingDashboard = ref(false)
const expandedTeams = ref(new Set<number>())
const teamDetails = ref<Record<number, AdminTeamDetails>>({})
const loadingTeamDetails = ref<Record<number, boolean>>({})

// Create team modal
const showCreateTeamModal = ref(false)
const newTeam = reactive({ name: '', access_code: '' })
const isCreatingTeam = ref(false)
const createTeamError = ref('')

// Edit team modal
const showEditTeamModal = ref(false)
const editingTeam = ref<{ id: number; name: string; access_code: string } | null>(null)
const isUpdatingTeam = ref(false)
const editTeamError = ref('')

// Delete modal
const showDeleteModal = ref(false)
const deleteConfirmMessage = ref('')
const deleteCallback = ref<(() => Promise<void>) | null>(null)
const isDeleting = ref(false)

onMounted(() => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    isAuthenticated.value = true
    loadDashboard()
  }
})

async function handleLogin() {
  isLoggingIn.value = true
  loginError.value = ''
  try {
    const response = await adminApi.login(adminCode.value)
    localStorage.setItem('admin_token', response.data.access_token)
    isAuthenticated.value = true
    adminCode.value = ''
    await loadDashboard()
  } catch (error: any) {
    loginError.value = error.response?.data?.detail || 'Invalid admin code'
  } finally {
    isLoggingIn.value = false
  }
}

function handleLogout() {
  localStorage.removeItem('admin_token')
  isAuthenticated.value = false
  dashboard.value = null
}

async function loadDashboard() {
  isLoadingDashboard.value = true
  try {
    const response = await adminApi.getDashboard()
    dashboard.value = response.data
  } catch (error) {
    console.error('Failed to load dashboard:', error)
  } finally {
    isLoadingDashboard.value = false
  }
}

async function toggleTeam(teamId: number) {
  if (expandedTeams.value.has(teamId)) {
    expandedTeams.value.delete(teamId)
  } else {
    expandedTeams.value.add(teamId)
    if (!teamDetails.value[teamId]) {
      loadingTeamDetails.value[teamId] = true
      try {
        const response = await adminApi.getTeamDetails(teamId)
        teamDetails.value[teamId] = response.data
      } catch (error) {
        console.error('Failed to load team details:', error)
      } finally {
        loadingTeamDetails.value[teamId] = false
      }
    }
  }
}

function getRoleColor(role: string): string {
  const colors: Record<string, string> = {
    top: 'bg-red-400',
    jungle: 'bg-green-400',
    mid: 'bg-blue-400',
    adc: 'bg-yellow-400',
    support: 'bg-purple-400',
  }
  return colors[role.toLowerCase()] || 'bg-gray-400'
}

async function handleCreateTeam() {
  isCreatingTeam.value = true
  createTeamError.value = ''
  try {
    await adminApi.createTeam(newTeam)
    showCreateTeamModal.value = false
    newTeam.name = ''
    newTeam.access_code = ''
    await loadDashboard()
  } catch (error: any) {
    createTeamError.value = error.response?.data?.detail || 'Failed to create team'
  } finally {
    isCreatingTeam.value = false
  }
}

function openEditTeam(team: AdminTeamStats) {
  editingTeam.value = {
    id: team.id,
    name: team.name,
    access_code: team.access_code,
  }
  editTeamError.value = ''
  showEditTeamModal.value = true
}

async function handleUpdateTeam() {
  if (!editingTeam.value) return
  isUpdatingTeam.value = true
  editTeamError.value = ''
  try {
    await adminApi.updateTeam(editingTeam.value.id, {
      name: editingTeam.value.name,
      access_code: editingTeam.value.access_code,
    })
    showEditTeamModal.value = false
    editingTeam.value = null
    await loadDashboard()
  } catch (error: any) {
    editTeamError.value = error.response?.data?.detail || 'Failed to update team'
  } finally {
    isUpdatingTeam.value = false
  }
}

function confirmDeleteTeam(team: AdminTeamStats) {
  deleteConfirmMessage.value = `Are you sure you want to delete team "${team.name}"? This will delete ALL associated data (${team.players_count} players, ${team.coaches_count} coaches, ${team.drafts_count} drafts, ${team.events_count} events).`
  deleteCallback.value = async () => {
    await adminApi.deleteTeam(team.id)
    delete teamDetails.value[team.id]
    expandedTeams.value.delete(team.id)
    await loadDashboard()
  }
  showDeleteModal.value = true
}

function confirmDeletePlayer(player: AdminPlayerSummary, team: AdminTeamStats) {
  deleteConfirmMessage.value = `Are you sure you want to delete player "${player.summoner_name}" from team "${team.name}"?`
  deleteCallback.value = async () => {
    await adminApi.deletePlayer(player.id)
    // Reload team details
    const response = await adminApi.getTeamDetails(team.id)
    teamDetails.value[team.id] = response.data
    await loadDashboard()
  }
  showDeleteModal.value = true
}

function confirmDeleteCoach(coach: AdminCoachSummary, team: AdminTeamStats) {
  deleteConfirmMessage.value = `Are you sure you want to delete coach "${coach.name}" from team "${team.name}"?`
  deleteCallback.value = async () => {
    await adminApi.deleteCoach(coach.id)
    // Reload team details
    const response = await adminApi.getTeamDetails(team.id)
    teamDetails.value[team.id] = response.data
    await loadDashboard()
  }
  showDeleteModal.value = true
}

async function executeDelete() {
  if (!deleteCallback.value) return
  isDeleting.value = true
  try {
    await deleteCallback.value()
    showDeleteModal.value = false
  } catch (error) {
    console.error('Delete failed:', error)
  } finally {
    isDeleting.value = false
  }
}
</script>
