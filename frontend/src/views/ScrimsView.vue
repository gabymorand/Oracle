<template>
  <div class="min-h-screen bg-gray-900">
    <AppNavbar :show-back-button="true" />

    <div class="max-w-7xl mx-auto px-4 py-8">
      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold">Gestion des Scrims</h1>
        <p class="text-gray-400 mt-1">Equipes adverses, prospects et historique</p>
      </div>

      <!-- Dashboard Stats -->
      <div class="grid grid-cols-5 gap-4 mb-8">
        <div class="bg-gray-800 rounded-lg p-4">
          <div class="text-3xl font-bold text-blue-400">{{ dashboard.total_scrims }}</div>
          <div class="text-gray-400 text-sm">Scrims total</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4">
          <div class="text-3xl font-bold text-green-400">{{ dashboard.reviewed_scrims }}</div>
          <div class="text-gray-400 text-sm">Scrims evalues</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4">
          <div class="text-3xl font-bold text-purple-400">{{ dashboard.total_teams }}</div>
          <div class="text-gray-400 text-sm">Equipes</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4">
          <div class="text-3xl font-bold text-yellow-400">{{ dashboard.total_scouted_players }}</div>
          <div class="text-gray-400 text-sm">Joueurs scoutes</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4">
          <div class="text-3xl font-bold text-orange-400">{{ dashboard.prospects_count }}</div>
          <div class="text-gray-400 text-sm">Prospects</div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="mb-6 flex gap-2 border-b border-gray-700">
        <button
          @click="activeTab = 'teams'"
          :class="[
            'px-6 py-3 font-medium transition border-b-2 -mb-px',
            activeTab === 'teams'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-gray-400 hover:text-white',
          ]"
        >
          Equipes
        </button>
        <button
          @click="activeTab = 'prospects'"
          :class="[
            'px-6 py-3 font-medium transition border-b-2 -mb-px',
            activeTab === 'prospects'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-gray-400 hover:text-white',
          ]"
        >
          Prospects
        </button>
        <button
          @click="activeTab = 'history'"
          :class="[
            'px-6 py-3 font-medium transition border-b-2 -mb-px',
            activeTab === 'history'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-gray-400 hover:text-white',
          ]"
        >
          Historique
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12 text-gray-400">
        Chargement...
      </div>

      <!-- Error -->
      <div v-else-if="errorMessage" class="text-center py-12">
        <div class="bg-red-900/50 border border-red-600 rounded-lg p-6 max-w-lg mx-auto">
          <p class="text-red-400 mb-4">{{ errorMessage }}</p>
          <button
            @click="loadData"
            class="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition"
          >
            Reessayer
          </button>
        </div>
      </div>

      <!-- Teams Tab -->
      <div v-else-if="activeTab === 'teams'">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold">Equipes adverses</h2>
          <button
            @click="showAddTeam = true"
            class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition flex items-center gap-2"
          >
            <span class="text-xl">+</span> Ajouter equipe
          </button>
        </div>

        <div class="grid gap-4">
          <div
            v-for="team in teams"
            :key="team.id"
            class="bg-gray-800 rounded-lg p-4 hover:bg-gray-750 transition cursor-pointer"
            @click="openTeamDetail(team)"
          >
            <div class="flex justify-between items-start">
              <div>
                <h3 class="text-lg font-semibold">{{ team.name }}</h3>
                <div class="text-gray-400 text-sm mt-1">
                  <span v-if="team.contact_discord">Discord: {{ team.contact_discord }}</span>
                  <span v-else-if="team.contact_twitter">Twitter: {{ team.contact_twitter }}</span>
                </div>
              </div>
              <div class="text-right">
                <div class="flex items-center gap-2">
                  <span class="text-green-400 font-bold">{{ team.wins }}W</span>
                  <span class="text-gray-500">-</span>
                  <span class="text-red-400 font-bold">{{ team.losses }}L</span>
                </div>
                <div class="text-gray-400 text-sm">{{ team.total_scrims }} scrims</div>
                <div v-if="team.avg_quality" class="text-yellow-400 text-sm">
                  Qualite: {{ team.avg_quality.toFixed(1) }}/5
                </div>
              </div>
            </div>
          </div>
          <div v-if="teams.length === 0" class="text-center py-8 text-gray-500">
            Aucune equipe enregistree
          </div>
        </div>
      </div>

      <!-- Prospects Tab -->
      <div v-else-if="activeTab === 'prospects'">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold">Joueurs scoutes & Prospects</h2>
          <button
            @click="showAddProspect = true"
            class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition flex items-center gap-2"
          >
            <span class="text-xl">+</span> Ajouter joueur
          </button>
        </div>

        <!-- Filter -->
        <div class="mb-4">
          <label class="flex items-center gap-2 text-gray-400">
            <input type="checkbox" v-model="prospectsOnly" class="rounded bg-gray-700 border-gray-600">
            Afficher uniquement les prospects
          </label>
        </div>

        <div class="grid gap-4">
          <div
            v-for="player in scoutedPlayers"
            :key="player.id"
            class="bg-gray-800 rounded-lg p-4"
          >
            <div class="flex justify-between items-start">
              <div>
                <div class="flex items-center gap-2">
                  <h3 class="text-lg font-semibold">{{ player.summoner_name }}</h3>
                  <span v-if="player.tag_line" class="text-gray-500">#{{ player.tag_line }}</span>
                  <span
                    v-if="player.is_prospect"
                    class="bg-orange-600 text-xs px-2 py-0.5 rounded"
                  >
                    PROSPECT
                  </span>
                </div>
                <div class="text-gray-400 text-sm mt-1">
                  <span v-if="player.role" class="uppercase">{{ player.role }}</span>
                  <span v-if="player.team_name" class="ml-2">- {{ player.team_name }}</span>
                </div>
              </div>
              <div class="text-right">
                <div v-if="player.rating" class="text-yellow-400 font-bold">
                  {{ player.rating }}/10
                </div>
                <div v-if="player.potential" class="text-sm mt-1" :class="getPotentialColor(player.potential)">
                  Potentiel: {{ player.potential }}
                </div>
              </div>
            </div>
            <div v-if="player.notes" class="mt-3 text-gray-400 text-sm border-t border-gray-700 pt-3">
              {{ player.notes }}
            </div>
          </div>
          <div v-if="scoutedPlayers.length === 0" class="text-center py-8 text-gray-500">
            Aucun joueur scoute
          </div>
        </div>
      </div>

      <!-- History Tab -->
      <div v-else-if="activeTab === 'history'">
        <h2 class="text-xl font-semibold mb-4">Historique des scrims</h2>

        <div class="space-y-3">
          <div
            v-for="scrim in history"
            :key="scrim.event_id"
            class="bg-gray-800 rounded-lg p-4"
          >
            <div class="flex justify-between items-center">
              <div>
                <div class="font-semibold">{{ scrim.title }}</div>
                <div class="text-gray-400 text-sm">
                  {{ formatDate(scrim.date) }} - {{ getSlotLabel(scrim.slot) }}
                  <span v-if="scrim.opponent_name" class="ml-2">vs {{ scrim.opponent_name }}</span>
                </div>
              </div>
              <div class="flex items-center gap-4">
                <!-- Result -->
                <div v-if="scrim.draft_series_result" class="flex items-center gap-2">
                  <span
                    :class="[
                      'px-3 py-1 rounded font-bold',
                      scrim.draft_series_result === 'win' ? 'bg-green-600' : 'bg-red-600'
                    ]"
                  >
                    {{ scrim.draft_series_result === 'win' ? 'W' : 'L' }}
                  </span>
                  <span class="text-gray-400">{{ scrim.our_score }} - {{ scrim.opponent_score }}</span>
                </div>
                <!-- Review badge -->
                <div v-if="scrim.review" class="flex items-center gap-1">
                  <span :class="getQualityColor(scrim.review.quality)">
                    {{ getQualityLabel(scrim.review.quality) }}
                  </span>
                </div>
                <span v-else class="text-gray-500 text-sm">Non evalue</span>
              </div>
            </div>
          </div>
          <div v-if="history.length === 0" class="text-center py-8 text-gray-500">
            Aucun scrim dans l'historique
          </div>
        </div>
      </div>
    </div>

    <!-- Add Team Modal -->
    <div
      v-if="showAddTeam"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
      @click.self="showAddTeam = false"
    >
      <div class="bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
        <h3 class="text-xl font-semibold mb-4">Ajouter une equipe</h3>
        <form @submit.prevent="createTeam" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Nom de l'equipe *</label>
            <input
              v-model="newTeam.name"
              type="text"
              required
              class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="Ex: Azurix Esport"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Contact Discord</label>
            <input
              v-model="newTeam.contact_discord"
              type="text"
              class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="Username#0000"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Contact Twitter</label>
            <input
              v-model="newTeam.contact_twitter"
              type="text"
              class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="@username"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Notes</label>
            <textarea
              v-model="newTeam.notes"
              rows="2"
              class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            ></textarea>
          </div>
          <div class="flex justify-end gap-3 pt-4">
            <button
              type="button"
              @click="showAddTeam = false"
              class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
            >
              Annuler
            </button>
            <button
              type="submit"
              :disabled="creatingTeam"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition disabled:opacity-50"
            >
              {{ creatingTeam ? 'Creation...' : 'Creer' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Add Prospect Modal -->
    <div
      v-if="showAddProspect"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
      @click.self="showAddProspect = false"
    >
      <div class="bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
        <h3 class="text-xl font-semibold mb-4">Ajouter un joueur</h3>
        <form @submit.prevent="createProspect" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Summoner Name *</label>
              <input
                v-model="newProspect.summoner_name"
                type="text"
                required
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Tag</label>
              <input
                v-model="newProspect.tag_line"
                type="text"
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="EUW"
              />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Role</label>
              <select
                v-model="newProspect.role"
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                <option value="">-</option>
                <option value="top">Top</option>
                <option value="jungle">Jungle</option>
                <option value="mid">Mid</option>
                <option value="adc">ADC</option>
                <option value="support">Support</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Equipe</label>
              <select
                v-model="newProspect.team_id"
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                <option :value="undefined">Aucune</option>
                <option v-for="team in teams" :key="team.id" :value="team.id">
                  {{ team.name }}
                </option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Note globale (1-10)</label>
              <input
                v-model.number="newProspect.rating"
                type="number"
                min="1"
                max="10"
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Potentiel</label>
              <select
                v-model="newProspect.potential"
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                <option value="">-</option>
                <option value="low">Faible</option>
                <option value="medium">Moyen</option>
                <option value="high">Eleve</option>
              </select>
            </div>
          </div>
          <div>
            <label class="flex items-center gap-2">
              <input type="checkbox" v-model="newProspect.is_prospect" class="rounded bg-gray-700 border-gray-600">
              <span class="text-sm">Marquer comme prospect</span>
            </label>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Notes</label>
            <textarea
              v-model="newProspect.notes"
              rows="2"
              class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            ></textarea>
          </div>
          <div class="flex justify-end gap-3 pt-4">
            <button
              type="button"
              @click="showAddProspect = false"
              class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
            >
              Annuler
            </button>
            <button
              type="submit"
              :disabled="creatingProspect"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition disabled:opacity-50"
            >
              {{ creatingProspect ? 'Creation...' : 'Creer' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import AppNavbar from '@/components/AppNavbar.vue'
import { scrimManagementApi } from '@/api'
import type {
  ScrimManagementDashboard,
  OpponentTeamWithStats,
  ScoutedPlayerWithTeam,
  ScrimHistoryItem,
  Potential,
} from '@/types'

// State
const loading = ref(true)
const errorMessage = ref<string | null>(null)
const activeTab = ref<'teams' | 'prospects' | 'history'>('teams')
const dashboard = ref<ScrimManagementDashboard>({
  total_scrims: 0,
  reviewed_scrims: 0,
  total_teams: 0,
  total_scouted_players: 0,
  prospects_count: 0,
  recent_scrims: [],
  top_teams: [],
})
const teams = ref<OpponentTeamWithStats[]>([])
const scoutedPlayers = ref<ScoutedPlayerWithTeam[]>([])
const history = ref<ScrimHistoryItem[]>([])
const prospectsOnly = ref(false)

// Modals
const showAddTeam = ref(false)
const showAddProspect = ref(false)
const creatingTeam = ref(false)
const creatingProspect = ref(false)

const newTeam = ref({
  name: '',
  contact_discord: '',
  contact_twitter: '',
  notes: '',
})

const newProspect = ref({
  summoner_name: '',
  tag_line: '',
  role: '',
  team_id: undefined as number | undefined,
  rating: undefined as number | undefined,
  potential: '' as Potential | '',
  is_prospect: false,
  notes: '',
})

// Helpers
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function getSlotLabel(slot: string): string {
  const labels: Record<string, string> = {
    morning: 'Matin',
    afternoon: 'Apres-midi',
    evening: 'Soir',
  }
  return labels[slot] || slot
}

function getQualityColor(quality: string): string {
  const colors: Record<string, string> = {
    excellent: 'text-green-400',
    good: 'text-blue-400',
    average: 'text-yellow-400',
    poor: 'text-orange-400',
    bad: 'text-red-400',
  }
  return colors[quality] || 'text-gray-400'
}

function getQualityLabel(quality: string): string {
  const labels: Record<string, string> = {
    excellent: 'Excellent',
    good: 'Bon',
    average: 'Moyen',
    poor: 'Faible',
    bad: 'Mauvais',
  }
  return labels[quality] || quality
}

function getPotentialColor(potential: string): string {
  const colors: Record<string, string> = {
    high: 'text-green-400',
    medium: 'text-yellow-400',
    low: 'text-red-400',
  }
  return colors[potential] || 'text-gray-400'
}

function openTeamDetail(team: OpponentTeamWithStats) {
  // TODO: Implement team detail modal
  console.log('Open team detail:', team)
}

// Data loading
async function loadDashboard() {
  const res = await scrimManagementApi.getDashboard()
  dashboard.value = res.data
}

async function loadTeams() {
  const res = await scrimManagementApi.getTeamsWithStats()
  teams.value = res.data
}

async function loadScoutedPlayers() {
  const res = await scrimManagementApi.getScoutedPlayers(prospectsOnly.value)
  scoutedPlayers.value = res.data
}

async function loadHistory() {
  const res = await scrimManagementApi.getHistory(100)
  history.value = res.data
}

async function loadData() {
  loading.value = true
  errorMessage.value = null
  try {
    await Promise.all([
      loadDashboard(),
      loadTeams(),
      loadScoutedPlayers(),
      loadHistory(),
    ])
  } catch (error) {
    console.error('Failed to load scrim data:', error)
    errorMessage.value = 'Erreur lors du chargement des donnees. Verifiez que les migrations ont ete executees.'
  } finally {
    loading.value = false
  }
}

async function createTeam() {
  creatingTeam.value = true
  try {
    await scrimManagementApi.createTeam({
      name: newTeam.value.name,
      contact_discord: newTeam.value.contact_discord || undefined,
      contact_twitter: newTeam.value.contact_twitter || undefined,
      notes: newTeam.value.notes || undefined,
    })
    showAddTeam.value = false
    newTeam.value = { name: '', contact_discord: '', contact_twitter: '', notes: '' }
    await loadTeams()
    await loadDashboard()
  } catch (error) {
    console.error('Failed to create team:', error)
    alert('Erreur lors de la creation')
  } finally {
    creatingTeam.value = false
  }
}

async function createProspect() {
  creatingProspect.value = true
  try {
    await scrimManagementApi.createScoutedPlayer({
      summoner_name: newProspect.value.summoner_name,
      tag_line: newProspect.value.tag_line || undefined,
      role: newProspect.value.role || undefined,
      team_id: newProspect.value.team_id,
      rating: newProspect.value.rating,
      potential: (newProspect.value.potential as Potential) || undefined,
      is_prospect: newProspect.value.is_prospect,
      notes: newProspect.value.notes || undefined,
    })
    showAddProspect.value = false
    newProspect.value = {
      summoner_name: '',
      tag_line: '',
      role: '',
      team_id: undefined,
      rating: undefined,
      potential: '',
      is_prospect: false,
      notes: '',
    }
    await loadScoutedPlayers()
    await loadDashboard()
  } catch (error) {
    console.error('Failed to create prospect:', error)
    alert('Erreur lors de la creation')
  } finally {
    creatingProspect.value = false
  }
}

// Lifecycle
onMounted(loadData)
watch(prospectsOnly, async () => {
  try {
    await loadScoutedPlayers()
  } catch (error) {
    console.error('Failed to reload scouted players:', error)
  }
})
</script>
