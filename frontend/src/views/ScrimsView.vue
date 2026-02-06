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
      <div v-if="!loading && !errorMessage" class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
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
            class="bg-gray-800 rounded-lg p-4 hover:bg-gray-750 transition cursor-pointer"
            @click="openPlayerDetail(player)"
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
                  {{ player.rating }}/5
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
            class="bg-gray-800 rounded-lg p-4 hover:bg-gray-750 transition cursor-pointer"
            @click="openScrimReview(scrim)"
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
              <label class="block text-sm font-medium mb-1">Note globale (1-5)</label>
              <input
                v-model.number="newProspect.rating"
                type="number"
                min="1"
                max="5"
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

    <!-- Team Detail Modal -->
    <div
      v-if="showTeamDetail && selectedTeam"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
      @click.self="closeTeamDetail"
    >
      <div class="bg-gray-800 rounded-lg p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-start mb-4">
          <h3 class="text-xl font-semibold">{{ selectedTeam.name }}</h3>
          <button @click="closeTeamDetail" class="text-gray-400 hover:text-white">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Stats -->
        <div class="grid grid-cols-3 gap-4 mb-6">
          <div class="bg-gray-700 rounded-lg p-3 text-center">
            <div class="text-2xl font-bold text-blue-400">{{ selectedTeam.total_scrims }}</div>
            <div class="text-gray-400 text-sm">Scrims</div>
          </div>
          <div class="bg-gray-700 rounded-lg p-3 text-center">
            <div class="text-2xl font-bold">
              <span class="text-green-400">{{ selectedTeam.wins }}</span>
              <span class="text-gray-500"> - </span>
              <span class="text-red-400">{{ selectedTeam.losses }}</span>
            </div>
            <div class="text-gray-400 text-sm">W/L</div>
          </div>
          <div class="bg-gray-700 rounded-lg p-3 text-center">
            <div class="text-2xl font-bold text-yellow-400">
              {{ selectedTeam.avg_quality ? selectedTeam.avg_quality.toFixed(1) : '-' }}
            </div>
            <div class="text-gray-400 text-sm">Qualite</div>
          </div>
        </div>

        <!-- Edit Form -->
        <form @submit.prevent="updateTeam" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Nom de l'equipe</label>
            <input
              v-model="editTeam.name"
              type="text"
              required
              class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Contact (nom)</label>
            <input
              v-model="editTeam.contact_name"
              type="text"
              class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Discord</label>
              <input
                v-model="editTeam.contact_discord"
                type="text"
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Twitter</label>
              <input
                v-model="editTeam.contact_twitter"
                type="text"
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Email</label>
            <input
              v-model="editTeam.contact_email"
              type="email"
              class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Notes</label>
            <textarea
              v-model="editTeam.notes"
              rows="3"
              class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            ></textarea>
          </div>
          <div class="flex justify-between pt-4">
            <button
              type="button"
              @click="confirmDeleteTeam"
              class="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition"
            >
              Supprimer
            </button>
            <div class="flex gap-3">
              <button
                type="button"
                @click="closeTeamDetail"
                class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
              >
                Annuler
              </button>
              <button
                type="submit"
                :disabled="updatingTeam"
                class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition disabled:opacity-50"
              >
                {{ updatingTeam ? 'Sauvegarde...' : 'Sauvegarder' }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Player Detail Modal -->
    <div
      v-if="showPlayerDetail && selectedPlayer"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
      @click.self="closePlayerDetail"
    >
      <div class="bg-gray-800 rounded-lg p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-xl font-semibold">
              {{ selectedPlayer.summoner_name }}
              <span v-if="selectedPlayer.tag_line" class="text-gray-500">#{{ selectedPlayer.tag_line }}</span>
            </h3>
            <span
              v-if="selectedPlayer.is_prospect"
              class="bg-orange-600 text-xs px-2 py-0.5 rounded mt-1 inline-block"
            >
              PROSPECT
            </span>
          </div>
          <button @click="closePlayerDetail" class="text-gray-400 hover:text-white">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Edit Form -->
        <form @submit.prevent="updatePlayer" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Summoner Name</label>
              <input
                v-model="editPlayer.summoner_name"
                type="text"
                required
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Tag</label>
              <input
                v-model="editPlayer.tag_line"
                type="text"
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Role</label>
              <select
                v-model="editPlayer.role"
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
                v-model="editPlayer.team_id"
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
              <label class="block text-sm font-medium mb-1">Note globale (1-5)</label>
              <input
                v-model.number="editPlayer.rating"
                type="number"
                min="1"
                max="5"
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Potentiel</label>
              <select
                v-model="editPlayer.potential"
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                <option value="">-</option>
                <option value="low">Faible</option>
                <option value="medium">Moyen</option>
                <option value="high">Eleve</option>
              </select>
            </div>
          </div>
          <!-- Skill ratings -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Mecanique (1-5)</label>
              <input
                v-model.number="editPlayer.mechanical_skill"
                type="number"
                min="1"
                max="5"
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Game Sense (1-5)</label>
              <input
                v-model.number="editPlayer.game_sense"
                type="number"
                min="1"
                max="5"
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Communication (1-5)</label>
              <input
                v-model.number="editPlayer.communication"
                type="number"
                min="1"
                max="5"
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Attitude (1-5)</label>
              <input
                v-model.number="editPlayer.attitude"
                type="number"
                min="1"
                max="5"
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
          </div>
          <div>
            <label class="flex items-center gap-2">
              <input type="checkbox" v-model="editPlayer.is_prospect" class="rounded bg-gray-700 border-gray-600">
              <span class="text-sm">Marquer comme prospect</span>
            </label>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Notes</label>
            <textarea
              v-model="editPlayer.notes"
              rows="3"
              class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            ></textarea>
          </div>
          <div class="flex justify-between pt-4">
            <button
              type="button"
              @click="confirmDeletePlayer"
              class="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition"
            >
              Supprimer
            </button>
            <div class="flex gap-3">
              <button
                type="button"
                @click="closePlayerDetail"
                class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
              >
                Annuler
              </button>
              <button
                type="submit"
                :disabled="updatingPlayer"
                class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition disabled:opacity-50"
              >
                {{ updatingPlayer ? 'Sauvegarde...' : 'Sauvegarder' }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Scrim Review Modal -->
    <div
      v-if="showScrimReview && selectedScrim"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
      @click.self="closeScrimReview"
    >
      <div class="bg-gray-800 rounded-lg p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-xl font-semibold">{{ selectedScrim.title }}</h3>
            <div class="text-gray-400 text-sm mt-1">
              {{ formatDate(selectedScrim.date) }} - {{ getSlotLabel(selectedScrim.slot) }}
              <span v-if="selectedScrim.opponent_name" class="ml-2">vs {{ selectedScrim.opponent_name }}</span>
            </div>
          </div>
          <button @click="closeScrimReview" class="text-gray-400 hover:text-white">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Result display -->
        <div v-if="selectedScrim.draft_series_result" class="mb-6 flex items-center gap-4">
          <span
            :class="[
              'px-4 py-2 rounded font-bold text-lg',
              selectedScrim.draft_series_result === 'win' ? 'bg-green-600' : 'bg-red-600'
            ]"
          >
            {{ selectedScrim.draft_series_result === 'win' ? 'VICTOIRE' : 'DEFAITE' }}
          </span>
          <span class="text-xl">{{ selectedScrim.our_score }} - {{ selectedScrim.opponent_score }}</span>
        </div>

        <!-- Review Form -->
        <form @submit.prevent="saveScrimReview" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-2">Qualite globale du scrim</label>
            <div class="flex gap-2">
              <button
                v-for="q in ['bad', 'poor', 'average', 'good', 'excellent']"
                :key="q"
                type="button"
                @click="scrimReview.quality = q"
                :class="[
                  'px-3 py-2 rounded-lg transition text-sm',
                  scrimReview.quality === q
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 hover:bg-gray-600'
                ]"
              >
                {{ getQualityLabel(q) }}
              </button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium mb-2">Equipe adverse</label>
            <select
              v-model="scrimReview.opponent_team_id"
              class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            >
              <option :value="undefined">-- Selectionner --</option>
              <option v-for="team in teams" :key="team.id" :value="team.id">
                {{ team.name }}
              </option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Ponctualite (1-5)</label>
              <input
                v-model.number="scrimReview.punctuality"
                type="number"
                min="1"
                max="5"
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="A l'heure?"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Communication (1-5)</label>
              <input
                v-model.number="scrimReview.communication"
                type="number"
                min="1"
                max="5"
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="Discord, annonces..."
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Competitivite (1-5)</label>
              <input
                v-model.number="scrimReview.competitiveness"
                type="number"
                min="1"
                max="5"
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="Niveau de jeu"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Rejouer avec eux? (1-5)</label>
              <input
                v-model.number="scrimReview.would_scrim_again"
                type="number"
                min="1"
                max="5"
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="1=Non, 5=Absolument"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Notes / Commentaires</label>
            <textarea
              v-model="scrimReview.notes"
              rows="3"
              class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="Points forts, points faibles, comportement..."
            ></textarea>
          </div>

          <div class="flex justify-end gap-3 pt-4">
            <button
              type="button"
              @click="closeScrimReview"
              class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
            >
              Annuler
            </button>
            <button
              type="submit"
              :disabled="savingReview || !scrimReview.quality"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition disabled:opacity-50"
            >
              {{ savingReview ? 'Sauvegarde...' : (selectedScrim.review ? 'Mettre a jour' : 'Enregistrer') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
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
const showTeamDetail = ref(false)
const showPlayerDetail = ref(false)
const showScrimReview = ref(false)
const creatingTeam = ref(false)
const creatingProspect = ref(false)
const updatingTeam = ref(false)
const updatingPlayer = ref(false)
const savingReview = ref(false)

// Selected items for detail modals
const selectedTeam = ref<OpponentTeamWithStats | null>(null)
const selectedPlayer = ref<ScoutedPlayerWithTeam | null>(null)
const selectedScrim = ref<ScrimHistoryItem | null>(null)

const scrimReview = ref({
  quality: '' as string,
  opponent_team_id: undefined as number | undefined,
  punctuality: undefined as number | undefined,
  communication: undefined as number | undefined,
  competitiveness: undefined as number | undefined,
  would_scrim_again: undefined as number | undefined,
  notes: '',
})

const newTeam = ref({
  name: '',
  contact_discord: '',
  contact_twitter: '',
  notes: '',
})

const editTeam = ref({
  name: '',
  contact_name: '',
  contact_discord: '',
  contact_twitter: '',
  contact_email: '',
  notes: '',
})

const editPlayer = ref({
  summoner_name: '',
  tag_line: '',
  role: '',
  team_id: undefined as number | undefined,
  rating: undefined as number | undefined,
  mechanical_skill: undefined as number | undefined,
  game_sense: undefined as number | undefined,
  communication: undefined as number | undefined,
  attitude: undefined as number | undefined,
  potential: '' as Potential | '',
  is_prospect: false,
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
  selectedTeam.value = team
  editTeam.value = {
    name: team.name,
    contact_name: team.contact_name || '',
    contact_discord: team.contact_discord || '',
    contact_twitter: team.contact_twitter || '',
    contact_email: team.contact_email || '',
    notes: team.notes || '',
  }
  showTeamDetail.value = true
}

function closeTeamDetail() {
  showTeamDetail.value = false
  selectedTeam.value = null
}

function openPlayerDetail(player: ScoutedPlayerWithTeam) {
  selectedPlayer.value = player
  editPlayer.value = {
    summoner_name: player.summoner_name,
    tag_line: player.tag_line || '',
    role: player.role || '',
    team_id: player.team_id,
    rating: player.rating,
    mechanical_skill: player.mechanical_skill,
    game_sense: player.game_sense,
    communication: player.communication,
    attitude: player.attitude,
    potential: (player.potential as Potential) || '',
    is_prospect: player.is_prospect || false,
    notes: player.notes || '',
  }
  showPlayerDetail.value = true
}

function closePlayerDetail() {
  showPlayerDetail.value = false
  selectedPlayer.value = null
}

async function updateTeam() {
  if (!selectedTeam.value) return
  updatingTeam.value = true
  try {
    await scrimManagementApi.updateTeam(selectedTeam.value.id, {
      name: editTeam.value.name,
      contact_name: editTeam.value.contact_name || undefined,
      contact_discord: editTeam.value.contact_discord || undefined,
      contact_twitter: editTeam.value.contact_twitter || undefined,
      contact_email: editTeam.value.contact_email || undefined,
      notes: editTeam.value.notes || undefined,
    })
    closeTeamDetail()
    await loadTeams()
    await loadDashboard()
  } catch (error) {
    console.error('Failed to update team:', error)
    alert('Erreur lors de la mise a jour')
  } finally {
    updatingTeam.value = false
  }
}

async function confirmDeleteTeam() {
  if (!selectedTeam.value) return
  if (!confirm(`Supprimer l'equipe "${selectedTeam.value.name}" ?`)) return
  try {
    await scrimManagementApi.deleteTeam(selectedTeam.value.id)
    closeTeamDetail()
    await loadTeams()
    await loadDashboard()
  } catch (error) {
    console.error('Failed to delete team:', error)
    alert('Erreur lors de la suppression')
  }
}

async function updatePlayer() {
  if (!selectedPlayer.value) return
  updatingPlayer.value = true
  try {
    await scrimManagementApi.updateScoutedPlayer(selectedPlayer.value.id, {
      summoner_name: editPlayer.value.summoner_name,
      tag_line: editPlayer.value.tag_line || undefined,
      role: editPlayer.value.role || undefined,
      team_id: editPlayer.value.team_id,
      rating: editPlayer.value.rating,
      mechanical_skill: editPlayer.value.mechanical_skill,
      game_sense: editPlayer.value.game_sense,
      communication: editPlayer.value.communication,
      attitude: editPlayer.value.attitude,
      potential: (editPlayer.value.potential as Potential) || undefined,
      is_prospect: editPlayer.value.is_prospect,
      notes: editPlayer.value.notes || undefined,
    })
    closePlayerDetail()
    await loadScoutedPlayers()
    await loadDashboard()
  } catch (error) {
    console.error('Failed to update player:', error)
    alert('Erreur lors de la mise a jour')
  } finally {
    updatingPlayer.value = false
  }
}

async function confirmDeletePlayer() {
  if (!selectedPlayer.value) return
  if (!confirm(`Supprimer le joueur "${selectedPlayer.value.summoner_name}" ?`)) return
  try {
    await scrimManagementApi.deleteScoutedPlayer(selectedPlayer.value.id)
    closePlayerDetail()
    await loadScoutedPlayers()
    await loadDashboard()
  } catch (error) {
    console.error('Failed to delete player:', error)
    alert('Erreur lors de la suppression')
  }
}

function openScrimReview(scrim: ScrimHistoryItem) {
  selectedScrim.value = scrim
  // Pre-fill with existing review data if available
  if (scrim.review) {
    scrimReview.value = {
      quality: scrim.review.quality,
      opponent_team_id: scrim.opponent_team_id,
      punctuality: scrim.review.punctuality,
      communication: scrim.review.communication,
      competitiveness: scrim.review.competitiveness,
      would_scrim_again: scrim.review.would_scrim_again,
      notes: scrim.review.notes || '',
    }
  } else {
    scrimReview.value = {
      quality: '',
      opponent_team_id: scrim.opponent_team_id,
      punctuality: undefined,
      communication: undefined,
      competitiveness: undefined,
      would_scrim_again: undefined,
      notes: '',
    }
  }
  showScrimReview.value = true
}

function closeScrimReview() {
  showScrimReview.value = false
  selectedScrim.value = null
}

async function saveScrimReview() {
  if (!selectedScrim.value || !scrimReview.value.quality) return
  savingReview.value = true
  try {
    await scrimManagementApi.createOrUpdateReview(selectedScrim.value.event_id, {
      quality: scrimReview.value.quality,
      opponent_team_id: scrimReview.value.opponent_team_id,
      punctuality: scrimReview.value.punctuality,
      communication: scrimReview.value.communication,
      competitiveness: scrimReview.value.competitiveness,
      would_scrim_again: scrimReview.value.would_scrim_again,
      notes: scrimReview.value.notes || undefined,
    })
    closeScrimReview()
    await loadHistory()
    await loadDashboard()
  } catch (error) {
    console.error('Failed to save review:', error)
    alert('Erreur lors de la sauvegarde')
  } finally {
    savingReview.value = false
  }
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
