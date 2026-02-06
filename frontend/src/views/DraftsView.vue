<template>
  <div class="min-h-screen bg-gray-900">
    <AppNavbar :show-back-button="true" />

    <div class="max-w-7xl mx-auto px-4 py-8">
      <div class="mb-6 flex justify-between items-center">
        <h1 class="text-3xl font-bold">Draft Planner</h1>
        <button
          @click="showCreateSeries = true"
          class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded transition flex items-center gap-2"
        >
          <span>+</span> New Series
        </button>
      </div>

      <!-- Stats Summary -->
      <div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-2xl font-bold text-blue-400">{{ stats.totalGames }}</div>
          <div class="text-sm text-gray-400">Games</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-2xl font-bold text-green-400">{{ stats.wins }}</div>
          <div class="text-sm text-gray-400">Wins</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-2xl font-bold text-red-400">{{ stats.losses }}</div>
          <div class="text-sm text-gray-400">Losses</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-2xl font-bold" :class="stats.winrate >= 50 ? 'text-green-400' : 'text-red-400'">
            {{ stats.winrate }}%
          </div>
          <div class="text-sm text-gray-400">Win Rate</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 text-center">
          <div class="text-2xl font-bold">
            <span :class="stats.blueWinrate >= 50 ? 'text-blue-400' : 'text-red-400'">{{ stats.blueWinrate }}%</span>
            <span class="text-gray-500 mx-1">/</span>
            <span :class="stats.redWinrate >= 50 ? 'text-red-400' : 'text-gray-400'">{{ stats.redWinrate }}%</span>
          </div>
          <div class="text-sm text-gray-400">Blue / Red</div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex gap-2 mb-6 border-b border-gray-700">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-4 py-3 font-medium transition border-b-2 -mb-px',
            activeTab === tab.id
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-gray-400 hover:text-white'
          ]"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <p class="text-gray-400">Chargement...</p>
      </div>

      <!-- Tab: Historique -->
      <div v-else-if="activeTab === 'history'" class="space-y-4">
        <div
          v-for="series in seriesList"
          :key="series.id"
          class="bg-gray-800 rounded-lg p-6 cursor-pointer hover:bg-gray-750 transition"
          @click="openSeries(series)"
        >
          <div class="flex justify-between items-start">
            <div>
              <div class="flex items-center gap-3 mb-2">
                <h3 class="text-xl font-semibold">vs {{ series.opponent_name }}</h3>
                <span class="text-xs bg-gray-700 px-2 py-1 rounded uppercase">
                  {{ series.format }}
                </span>
              </div>
              <p class="text-gray-400 text-sm">{{ formatDate(series.date) }}</p>
            </div>
            <div class="flex items-center gap-4">
              <div class="text-center">
                <div class="text-2xl font-bold">
                  <span class="text-green-400">{{ series.our_score }}</span>
                  <span class="text-gray-500"> - </span>
                  <span class="text-red-400">{{ series.opponent_score }}</span>
                </div>
                <div class="text-xs text-gray-500">{{ series.games_count }} game(s)</div>
              </div>
              <span
                v-if="series.result"
                :class="series.result === 'win' ? 'bg-green-600' : 'bg-red-600'"
                class="px-4 py-2 rounded uppercase text-sm font-semibold"
              >
                {{ series.result }}
              </span>
              <span v-else class="px-4 py-2 bg-gray-600 rounded text-sm">
                En cours
              </span>
            </div>
          </div>
        </div>

        <div v-if="seriesList.length === 0" class="text-center py-12">
          <p class="text-gray-400 mb-4">Aucune serie enregistree.</p>
          <button
            @click="showCreateSeries = true"
            class="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded transition"
          >
            Creer votre premiere serie
          </button>
        </div>
      </div>

      <!-- Tab: Analyse Champions -->
      <div v-else-if="activeTab === 'champions'" class="space-y-6">
        <div v-if="loadingAnalytics" class="text-center py-12">
          <p class="text-gray-400">Chargement des analyses...</p>
        </div>
        <template v-else>
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Nos picks -->
            <div class="bg-gray-800 rounded-xl p-5">
              <h3 class="font-semibold mb-4 text-lg flex items-center gap-2">
                <span class="w-3 h-3 rounded-full bg-green-500"></span>
                Nos Picks
              </h3>
              <div class="space-y-2 max-h-96 overflow-y-auto">
                <div
                  v-for="champ in analytics.ourPicks.slice(0, 15)"
                  :key="champ.id"
                  class="flex items-center gap-3 bg-gray-700/50 rounded-lg p-2 hover:bg-gray-700 transition"
                >
                  <img :src="getChampIcon(champ.id)" :alt="getChampName(champ.id)" class="w-10 h-10 rounded" />
                  <div class="flex-1 min-w-0">
                    <div class="font-medium">{{ getChampName(champ.id) }}</div>
                    <div class="text-xs text-gray-400">{{ champ.games }} games</div>
                  </div>
                  <div class="text-right">
                    <div :class="champ.winrate >= 50 ? 'text-green-400' : 'text-red-400'" class="font-bold text-lg">
                      {{ champ.winrate.toFixed(0) }}%
                    </div>
                    <div class="text-xs text-gray-500">{{ champ.wins }}W {{ champ.games - champ.wins }}L</div>
                  </div>
                </div>
                <div v-if="analytics.ourPicks.length === 0" class="text-gray-500 text-center py-8">
                  Pas assez de donnees
                </div>
              </div>
            </div>

            <!-- Champions ennemis dangereux -->
            <div class="bg-gray-800 rounded-xl p-5">
              <h3 class="font-semibold mb-4 text-lg flex items-center gap-2">
                <span class="w-3 h-3 rounded-full bg-red-500"></span>
                Menaces (champions adverses)
              </h3>
              <p class="text-xs text-gray-400 mb-3">Champions qui nous ont battus le plus souvent</p>
              <div class="space-y-2 max-h-96 overflow-y-auto">
                <div
                  v-for="champ in analytics.threats.slice(0, 15)"
                  :key="champ.id"
                  class="flex items-center gap-3 bg-gray-700/50 rounded-lg p-2 hover:bg-gray-700 transition"
                >
                  <img :src="getChampIcon(champ.id)" :alt="getChampName(champ.id)" class="w-10 h-10 rounded" />
                  <div class="flex-1 min-w-0">
                    <div class="font-medium">{{ getChampName(champ.id) }}</div>
                    <div class="text-xs text-gray-400">{{ champ.games }} games contre</div>
                  </div>
                  <div class="text-right">
                    <div class="text-red-400 font-bold text-lg">
                      {{ champ.winrateAgainstUs.toFixed(0) }}%
                    </div>
                    <div class="text-xs text-gray-500">WR contre nous</div>
                  </div>
                </div>
                <div v-if="analytics.threats.length === 0" class="text-gray-500 text-center py-8">
                  Pas assez de donnees
                </div>
              </div>
            </div>
          </div>

          <!-- Nos bans -->
          <div class="bg-gray-800 rounded-xl p-5">
            <h3 class="font-semibold mb-4 text-lg flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-purple-500"></span>
              Nos Bans Frequents
            </h3>
            <div class="flex flex-wrap gap-3">
              <div
                v-for="champ in analytics.ourBans.slice(0, 10)"
                :key="champ.id"
                class="flex items-center gap-2 bg-gray-700/50 rounded-lg px-3 py-2"
              >
                <img :src="getChampIcon(champ.id)" :alt="getChampName(champ.id)" class="w-8 h-8 rounded opacity-60" />
                <span class="font-medium">{{ getChampName(champ.id) }}</span>
                <span class="text-purple-400 font-bold">{{ champ.count }}x</span>
              </div>
              <div v-if="analytics.ourBans.length === 0" class="text-gray-500 w-full text-center py-4">
                Aucun ban enregistre
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Tab: Synergies -->
      <div v-else-if="activeTab === 'synergies'" class="space-y-6">
        <div v-if="loadingAnalytics" class="text-center py-12">
          <p class="text-gray-400">Chargement des synergies...</p>
        </div>
        <template v-else>
          <p class="text-gray-400 text-sm mb-4">
            Analyse des duos de champions que vous pickez ensemble et leur taux de victoire.
          </p>

          <!-- Best Synergies -->
          <div class="bg-gray-800 rounded-xl p-5">
            <h3 class="font-semibold mb-4 text-lg flex items-center gap-2">
              <span class="text-green-400">Meilleures Synergies</span>
              <span class="text-xs text-gray-500">(min 2 games)</span>
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              <div
                v-for="(synergy, idx) in analytics.bestSynergies.slice(0, 12)"
                :key="idx"
                class="flex items-center gap-3 bg-gray-700/50 rounded-lg p-3"
              >
                <div class="flex -space-x-2">
                  <img :src="getChampIcon(synergy.champ1)" :alt="getChampName(synergy.champ1)" class="w-10 h-10 rounded border-2 border-gray-800" />
                  <img :src="getChampIcon(synergy.champ2)" :alt="getChampName(synergy.champ2)" class="w-10 h-10 rounded border-2 border-gray-800" />
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium truncate">
                    {{ getChampName(synergy.champ1) }} + {{ getChampName(synergy.champ2) }}
                  </div>
                  <div class="text-xs text-gray-400">{{ synergy.games }} games</div>
                </div>
                <div :class="synergy.winrate >= 50 ? 'text-green-400' : 'text-red-400'" class="font-bold">
                  {{ synergy.winrate.toFixed(0) }}%
                </div>
              </div>
            </div>
            <div v-if="analytics.bestSynergies.length === 0" class="text-gray-500 text-center py-8">
              Pas assez de donnees (min 2 games par duo)
            </div>
          </div>

          <!-- Worst Synergies -->
          <div class="bg-gray-800 rounded-xl p-5">
            <h3 class="font-semibold mb-4 text-lg flex items-center gap-2">
              <span class="text-red-400">Synergies a eviter</span>
              <span class="text-xs text-gray-500">(min 2 games)</span>
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              <div
                v-for="(synergy, idx) in analytics.worstSynergies.slice(0, 6)"
                :key="idx"
                class="flex items-center gap-3 bg-gray-700/50 rounded-lg p-3"
              >
                <div class="flex -space-x-2">
                  <img :src="getChampIcon(synergy.champ1)" :alt="getChampName(synergy.champ1)" class="w-10 h-10 rounded border-2 border-gray-800 opacity-60" />
                  <img :src="getChampIcon(synergy.champ2)" :alt="getChampName(synergy.champ2)" class="w-10 h-10 rounded border-2 border-gray-800 opacity-60" />
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium truncate">
                    {{ getChampName(synergy.champ1) }} + {{ getChampName(synergy.champ2) }}
                  </div>
                  <div class="text-xs text-gray-400">{{ synergy.games }} games</div>
                </div>
                <div class="text-red-400 font-bold">
                  {{ synergy.winrate.toFixed(0) }}%
                </div>
              </div>
            </div>
            <div v-if="analytics.worstSynergies.length === 0" class="text-gray-500 text-center py-8">
              Pas assez de donnees
            </div>
          </div>
        </template>
      </div>

      <!-- Tab: Compositions -->
      <div v-else-if="activeTab === 'comps'" class="space-y-6">
        <div v-if="loadingAnalytics" class="text-center py-12">
          <p class="text-gray-400">Chargement des compositions...</p>
        </div>
        <template v-else>
          <p class="text-gray-400 text-sm mb-4">
            Toutes les compositions que vous avez jouees, triees par winrate.
          </p>

          <div class="space-y-3">
            <div
              v-for="(comp, idx) in analytics.compositions"
              :key="idx"
              class="bg-gray-800 rounded-xl p-4 hover:bg-gray-750 transition"
            >
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-2">
                  <span
                    :class="comp.result === 'win' ? 'bg-green-600' : 'bg-red-600'"
                    class="px-2 py-1 rounded text-xs font-semibold uppercase"
                  >
                    {{ comp.result }}
                  </span>
                  <span class="text-gray-400 text-sm">vs {{ comp.opponent }}</span>
                  <span class="text-gray-500 text-xs">{{ formatDate(comp.date) }}</span>
                </div>
                <span class="text-xs bg-gray-700 px-2 py-1 rounded">
                  {{ comp.side === 'blue' ? 'Blue Side' : 'Red Side' }}
                </span>
              </div>

              <div class="flex items-center gap-2">
                <div
                  v-for="(champId, champIdx) in comp.picks"
                  :key="champIdx"
                  class="relative group"
                >
                  <img
                    :src="getChampIcon(champId)"
                    :alt="getChampName(champId)"
                    class="w-12 h-12 rounded-lg border-2"
                    :class="comp.result === 'win' ? 'border-green-500/50' : 'border-red-500/50'"
                  />
                  <div class="absolute -bottom-1 left-1/2 -translate-x-1/2 text-[10px] bg-gray-900 px-1 rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap">
                    {{ getChampName(champId) }}
                  </div>
                </div>
                <div class="text-gray-500 mx-2">vs</div>
                <div
                  v-for="(champId, champIdx) in comp.enemyPicks"
                  :key="'e'+champIdx"
                  class="relative group"
                >
                  <img
                    :src="getChampIcon(champId)"
                    :alt="getChampName(champId)"
                    class="w-12 h-12 rounded-lg border-2 border-gray-600 opacity-70"
                  />
                  <div class="absolute -bottom-1 left-1/2 -translate-x-1/2 text-[10px] bg-gray-900 px-1 rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap">
                    {{ getChampName(champId) }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="analytics.compositions.length === 0" class="text-gray-500 text-center py-12">
            Aucune composition enregistree
          </div>
        </template>
      </div>
    </div>

    <!-- Create Series Modal -->
    <div v-if="showCreateSeries" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
      <div class="bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-semibold mb-4">Nouvelle Serie</h2>
        <form @submit.prevent="createSeries" class="space-y-4">
          <div>
            <label class="block text-sm mb-2">Date</label>
            <input
              v-model="newSeries.date"
              type="date"
              class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600"
              required
            />
          </div>
          <div>
            <label class="block text-sm mb-2">Adversaire</label>
            <input
              v-model="newSeries.opponent_name"
              type="text"
              placeholder="Nom de l'equipe"
              class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600"
              required
            />
          </div>
          <div>
            <label class="block text-sm mb-2">Format</label>
            <div class="flex gap-2">
              <button
                type="button"
                v-for="format in ['bo1', 'bo3', 'bo5']"
                :key="format"
                @click="newSeries.format = format"
                :class="[
                  'flex-1 py-2 rounded uppercase font-semibold transition',
                  newSeries.format === format ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
                ]"
              >
                {{ format }}
              </button>
            </div>
          </div>
          <div>
            <label class="block text-sm mb-2">Notes (optionnel)</label>
            <textarea
              v-model="newSeries.notes"
              class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600"
              rows="2"
              placeholder="Tournoi, phase, etc."
            ></textarea>
          </div>
          <div class="flex gap-3 pt-2">
            <button
              type="button"
              @click="showCreateSeries = false"
              class="flex-1 py-2 bg-gray-700 hover:bg-gray-600 rounded transition"
            >
              Annuler
            </button>
            <button
              type="submit"
              class="flex-1 py-2 bg-blue-600 hover:bg-blue-700 rounded transition"
            >
              Creer
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Series Detail Modal -->
    <div v-if="selectedSeries" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 overflow-y-auto">
      <div class="bg-gray-800 rounded-lg p-6 w-full max-w-4xl my-8 mx-4">
        <div class="flex justify-between items-start mb-6">
          <div>
            <h2 class="text-2xl font-bold">vs {{ selectedSeries.opponent_name }}</h2>
            <p class="text-gray-400">{{ formatDate(selectedSeries.date) }} - {{ selectedSeries.format.toUpperCase() }}</p>
          </div>
          <div class="flex items-center gap-4">
            <div class="text-center">
              <div class="text-3xl font-bold">
                <span class="text-green-400">{{ selectedSeries.our_score }}</span>
                <span class="text-gray-500"> - </span>
                <span class="text-red-400">{{ selectedSeries.opponent_score }}</span>
              </div>
            </div>
            <button
              @click="selectedSeries = null"
              class="text-gray-400 hover:text-white text-2xl"
            >
              &times;
            </button>
          </div>
        </div>

        <!-- Games -->
        <div class="space-y-4 mb-6">
          <div
            v-for="game in selectedSeries.games"
            :key="game.id"
            class="bg-gray-700 rounded-lg p-4"
          >
            <div class="flex justify-between items-center mb-3">
              <div class="flex items-center gap-3">
                <span class="text-lg font-semibold">Game {{ game.game_number }}</span>
                <span class="text-xs bg-gray-600 px-2 py-1 rounded">
                  {{ game.blue_side ? 'Blue Side' : 'Red Side' }}
                </span>
              </div>
              <div class="flex items-center gap-2">
                <span
                  v-if="game.result"
                  :class="game.result === 'win' ? 'text-green-400' : 'text-red-400'"
                  class="font-semibold uppercase"
                >
                  {{ game.result }}
                </span>
                <button
                  @click="editGame(game)"
                  class="text-blue-400 hover:text-blue-300 text-sm"
                >
                  Edit
                </button>
                <button
                  @click="deleteGame(game.id)"
                  class="text-red-400 hover:text-red-300 text-sm"
                >
                  Delete
                </button>
              </div>
            </div>

            <!-- Draft Display -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <div class="text-xs text-gray-400 mb-1">Nos Bans</div>
                <div class="flex gap-1">
                  <div
                    v-for="(ban, idx) in game.our_bans"
                    :key="idx"
                    class="w-8 h-8 bg-gray-600 rounded flex items-center justify-center text-xs"
                    :title="getChampName(ban)"
                  >
                    <img
                      v-if="ban"
                      :src="getChampIcon(ban)"
                      :alt="getChampName(ban)"
                      class="w-full h-full rounded opacity-50"
                    />
                    <span v-else>-</span>
                  </div>
                </div>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">Bans Adverses</div>
                <div class="flex gap-1">
                  <div
                    v-for="(ban, idx) in game.opponent_bans"
                    :key="idx"
                    class="w-8 h-8 bg-gray-600 rounded flex items-center justify-center text-xs"
                    :title="getChampName(ban)"
                  >
                    <img
                      v-if="ban"
                      :src="getChampIcon(ban)"
                      :alt="getChampName(ban)"
                      class="w-full h-full rounded opacity-50"
                    />
                    <span v-else>-</span>
                  </div>
                </div>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">Nos Picks</div>
                <div class="flex gap-1">
                  <div
                    v-for="(pick, idx) in game.our_picks"
                    :key="idx"
                    class="w-8 h-8 bg-gray-600 rounded flex items-center justify-center text-xs"
                    :title="getChampName(pick)"
                  >
                    <img
                      v-if="pick"
                      :src="getChampIcon(pick)"
                      :alt="getChampName(pick)"
                      class="w-full h-full rounded"
                    />
                    <span v-else>-</span>
                  </div>
                </div>
              </div>
              <div>
                <div class="text-xs text-gray-400 mb-1">Picks Adverses</div>
                <div class="flex gap-1">
                  <div
                    v-for="(pick, idx) in game.opponent_picks"
                    :key="idx"
                    class="w-8 h-8 bg-gray-600 rounded flex items-center justify-center text-xs"
                    :title="getChampName(pick)"
                  >
                    <img
                      v-if="pick"
                      :src="getChampIcon(pick)"
                      :alt="getChampName(pick)"
                      class="w-full h-full rounded"
                    />
                    <span v-else>-</span>
                  </div>
                </div>
              </div>
            </div>

            <p v-if="game.notes" class="text-gray-400 text-sm mt-3">{{ game.notes }}</p>
          </div>
        </div>

        <!-- Add Game Button -->
        <div v-if="canAddMoreGames" class="mb-6">
          <button
            @click="showAddGame = true"
            class="w-full py-3 bg-green-600 hover:bg-green-700 rounded transition flex items-center justify-center gap-2"
          >
            <span>+</span> Ajouter Game {{ (selectedSeries.games?.length || 0) + 1 }}
          </button>
        </div>

        <!-- Actions -->
        <div class="flex justify-between">
          <button
            @click="deleteSeries(selectedSeries.id)"
            class="px-4 py-2 bg-red-600 hover:bg-red-700 rounded transition"
          >
            Supprimer Serie
          </button>
          <button
            @click="selectedSeries = null"
            class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded transition"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>

    <!-- Add Game Modal -->
    <div v-if="showAddGame && selectedSeries" class="fixed inset-0 bg-black/80 flex items-center justify-center z-[60] overflow-y-auto">
      <div class="bg-gray-800 rounded-lg p-6 w-full max-w-2xl my-8 mx-4">
        <h2 class="text-xl font-semibold mb-4">Ajouter Game {{ (selectedSeries.games?.length || 0) + 1 }}</h2>
        <form @submit.prevent="addGame" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm mb-2">Side</label>
              <div class="flex gap-2">
                <button
                  type="button"
                  @click="newGame.blue_side = true"
                  :class="[
                    'flex-1 py-2 rounded transition',
                    newGame.blue_side ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
                  ]"
                >
                  Blue Side
                </button>
                <button
                  type="button"
                  @click="newGame.blue_side = false"
                  :class="[
                    'flex-1 py-2 rounded transition',
                    !newGame.blue_side ? 'bg-red-600' : 'bg-gray-700 hover:bg-gray-600'
                  ]"
                >
                  Red Side
                </button>
              </div>
            </div>
            <div>
              <label class="block text-sm mb-2">Resultat</label>
              <div class="flex gap-2">
                <button
                  type="button"
                  @click="newGame.result = 'win'"
                  :class="[
                    'flex-1 py-2 rounded transition',
                    newGame.result === 'win' ? 'bg-green-600' : 'bg-gray-700 hover:bg-gray-600'
                  ]"
                >
                  Victoire
                </button>
                <button
                  type="button"
                  @click="newGame.result = 'loss'"
                  :class="[
                    'flex-1 py-2 rounded transition',
                    newGame.result === 'loss' ? 'bg-red-600' : 'bg-gray-700 hover:bg-gray-600'
                  ]"
                >
                  Defaite
                </button>
              </div>
            </div>
          </div>

          <!-- Import Section -->
          <div class="bg-gray-700 rounded-lg p-4">
            <h3 class="font-semibold mb-3">Importer Draft</h3>
            <div class="flex gap-2">
              <input
                v-model="importUrl"
                type="url"
                placeholder="https://draftlol.dawe.gg/draft/..."
                class="flex-1 px-3 py-2 bg-gray-600 rounded border border-gray-500"
              />
              <button
                type="button"
                @click="importDraft"
                :disabled="!importUrl || importing"
                class="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ importing ? 'Import...' : 'Importer' }}
              </button>
            </div>
            <p v-if="importError" class="text-xs text-red-400 mt-1">{{ importError }}</p>
            <p v-else-if="importSuccess" class="text-xs text-green-400 mt-1">{{ importSuccess }}</p>
            <p v-else class="text-xs text-gray-400 mt-1">Coller un lien draftlol.dawe.gg pour remplir automatiquement</p>
          </div>

          <!-- Manual Entry -->
          <div class="text-sm text-gray-400 text-center">- ou saisir manuellement -</div>

          <!-- Bans -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm mb-2">Nos Bans (5)</label>
              <input
                v-model="newGame.our_bans_text"
                type="text"
                placeholder="Ex: Aatrox, Ahri, Zed"
                class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 text-sm"
              />
            </div>
            <div>
              <label class="block text-sm mb-2">Bans Adverses (5)</label>
              <input
                v-model="newGame.opponent_bans_text"
                type="text"
                placeholder="Ex: Aatrox, Ahri, Zed"
                class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 text-sm"
              />
            </div>
          </div>

          <!-- Picks -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm mb-2">Nos Picks (5)</label>
              <input
                v-model="newGame.our_picks_text"
                type="text"
                placeholder="Ex: Aatrox, Ahri, Zed"
                class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 text-sm"
              />
            </div>
            <div>
              <label class="block text-sm mb-2">Picks Adverses (5)</label>
              <input
                v-model="newGame.opponent_picks_text"
                type="text"
                placeholder="Ex: Aatrox, Ahri, Zed"
                class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 text-sm"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm mb-2">Notes</label>
            <textarea
              v-model="newGame.notes"
              class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600"
              rows="2"
            ></textarea>
          </div>

          <div class="flex gap-3 pt-2">
            <button
              type="button"
              @click="showAddGame = false"
              class="flex-1 py-2 bg-gray-700 hover:bg-gray-600 rounded transition"
            >
              Annuler
            </button>
            <button
              type="submit"
              class="flex-1 py-2 bg-blue-600 hover:bg-blue-700 rounded transition"
            >
              Ajouter
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { apiClient } from '@/api/client'
import AppNavbar from '@/components/AppNavbar.vue'
import { loadChampionData, getChampionName, getChampionIconUrl, parseChampionInput } from '@/utils/champions'

interface DraftGame {
  id: number
  series_id: number
  game_number: number
  blue_side: boolean
  our_bans: number[]
  opponent_bans: number[]
  our_picks: number[]
  opponent_picks: number[]
  result: string | null
  import_source: string | null
  import_url: string | null
  notes: string | null
  created_at: string
}

interface DraftSeries {
  id: number
  date: string
  opponent_name: string
  format: string
  our_score: number
  opponent_score: number
  result: string | null
  notes: string | null
  created_at: string
  games_count?: number
  games?: DraftGame[]
}

interface ChampionStat {
  id: number
  games: number
  wins: number
  winrate: number
}

interface ThreatStat {
  id: number
  games: number
  winsAgainstUs: number
  winrateAgainstUs: number
}

interface SynergyStat {
  champ1: number
  champ2: number
  games: number
  wins: number
  winrate: number
}

interface CompositionStat {
  picks: number[]
  enemyPicks: number[]
  result: string
  opponent: string
  date: string
  side: string
}

// Tabs
const tabs = [
  { id: 'history', label: 'Historique' },
  { id: 'champions', label: 'Champions' },
  { id: 'synergies', label: 'Synergies' },
  { id: 'comps', label: 'Compositions' },
]
const activeTab = ref('history')

// State
const seriesList = ref<DraftSeries[]>([])
const loading = ref(true)
const showCreateSeries = ref(false)
const selectedSeries = ref<DraftSeries | null>(null)
const showAddGame = ref(false)
const importUrl = ref('')
const importing = ref(false)
const importError = ref('')
const importSuccess = ref('')

// Analytics state
const allGames = ref<DraftGame[]>([])
const allGamesLoaded = ref(false)
const loadingAnalytics = ref(false)

const newSeries = ref({
  date: new Date().toISOString().split('T')[0],
  opponent_name: '',
  format: 'bo1',
  notes: '',
})

const newGame = ref({
  blue_side: true,
  result: null as string | null,
  our_bans_text: '',
  opponent_bans_text: '',
  our_picks_text: '',
  opponent_picks_text: '',
  notes: '',
})

// Stats computed
const stats = computed(() => {
  const totalGames = allGames.value.length
  const wins = allGames.value.filter(g => g.result === 'win').length
  const losses = allGames.value.filter(g => g.result === 'loss').length
  const winrate = totalGames > 0 ? Math.round((wins / totalGames) * 100) : 0

  const blueGames = allGames.value.filter(g => g.blue_side)
  const blueWins = blueGames.filter(g => g.result === 'win').length
  const blueWinrate = blueGames.length > 0 ? Math.round((blueWins / blueGames.length) * 100) : 0

  const redGames = allGames.value.filter(g => !g.blue_side)
  const redWins = redGames.filter(g => g.result === 'win').length
  const redWinrate = redGames.length > 0 ? Math.round((redWins / redGames.length) * 100) : 0

  return { totalGames, wins, losses, winrate, blueWinrate, redWinrate }
})

const canAddMoreGames = computed(() => {
  if (!selectedSeries.value) return false
  const maxGames = { bo1: 1, bo3: 3, bo5: 5 }[selectedSeries.value.format] || 1
  return (selectedSeries.value.games?.length || 0) < maxGames
})

// Analytics computed
const analytics = computed(() => {
  // Our picks stats
  const picksMap = new Map<number, { games: number; wins: number }>()
  for (const game of allGames.value) {
    for (const pickId of game.our_picks || []) {
      if (!pickId) continue
      const existing = picksMap.get(pickId) || { games: 0, wins: 0 }
      existing.games++
      if (game.result === 'win') existing.wins++
      picksMap.set(pickId, existing)
    }
  }
  const ourPicks: ChampionStat[] = Array.from(picksMap.entries())
    .map(([id, data]) => ({
      id,
      games: data.games,
      wins: data.wins,
      winrate: data.games > 0 ? (data.wins / data.games) * 100 : 0,
    }))
    .sort((a, b) => b.games - a.games)

  // Our bans stats
  const bansMap = new Map<number, number>()
  for (const game of allGames.value) {
    for (const banId of game.our_bans || []) {
      if (!banId) continue
      bansMap.set(banId, (bansMap.get(banId) || 0) + 1)
    }
  }
  const ourBans = Array.from(bansMap.entries())
    .map(([id, count]) => ({ id, count }))
    .sort((a, b) => b.count - a.count)

  // Threats (enemy picks that beat us)
  const threatsMap = new Map<number, { games: number; winsAgainstUs: number }>()
  for (const game of allGames.value) {
    for (const pickId of game.opponent_picks || []) {
      if (!pickId) continue
      const existing = threatsMap.get(pickId) || { games: 0, winsAgainstUs: 0 }
      existing.games++
      if (game.result === 'loss') existing.winsAgainstUs++
      threatsMap.set(pickId, existing)
    }
  }
  const threats: ThreatStat[] = Array.from(threatsMap.entries())
    .map(([id, data]) => ({
      id,
      games: data.games,
      winsAgainstUs: data.winsAgainstUs,
      winrateAgainstUs: data.games > 0 ? (data.winsAgainstUs / data.games) * 100 : 0,
    }))
    .filter(t => t.games >= 2) // At least 2 games
    .sort((a, b) => b.winrateAgainstUs - a.winrateAgainstUs)

  // Synergies (champion pairs)
  const synergyMap = new Map<string, { champ1: number; champ2: number; games: number; wins: number }>()
  for (const game of allGames.value) {
    const picks = (game.our_picks || []).filter(p => p)
    for (let i = 0; i < picks.length; i++) {
      for (let j = i + 1; j < picks.length; j++) {
        const key = [picks[i], picks[j]].sort((a, b) => a - b).join('-')
        const existing = synergyMap.get(key) || { champ1: Math.min(picks[i], picks[j]), champ2: Math.max(picks[i], picks[j]), games: 0, wins: 0 }
        existing.games++
        if (game.result === 'win') existing.wins++
        synergyMap.set(key, existing)
      }
    }
  }
  const allSynergies: SynergyStat[] = Array.from(synergyMap.values())
    .map(s => ({
      ...s,
      winrate: s.games > 0 ? (s.wins / s.games) * 100 : 0,
    }))
    .filter(s => s.games >= 2) // At least 2 games

  const bestSynergies = [...allSynergies].sort((a, b) => b.winrate - a.winrate)
  const worstSynergies = [...allSynergies].sort((a, b) => a.winrate - b.winrate)

  // Compositions
  const compositions: CompositionStat[] = allGames.value
    .filter(g => g.our_picks?.length === 5)
    .map(g => {
      const series = seriesList.value.find(s => s.id === g.series_id)
      return {
        picks: g.our_picks,
        enemyPicks: g.opponent_picks || [],
        result: g.result || 'unknown',
        opponent: series?.opponent_name || 'Unknown',
        date: series?.date || '',
        side: g.blue_side ? 'blue' : 'red',
      }
    })
    .sort((a, b) => {
      // Sort wins first, then by date
      if (a.result === 'win' && b.result !== 'win') return -1
      if (a.result !== 'win' && b.result === 'win') return 1
      return new Date(b.date).getTime() - new Date(a.date).getTime()
    })

  return {
    ourPicks,
    ourBans,
    threats,
    bestSynergies,
    worstSynergies,
    compositions,
  }
})

// Functions
function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

function getChampName(id: number): string {
  return getChampionName(id)
}

function getChampIcon(id: number): string {
  return getChampionIconUrl(id)
}

function parseChampionNames(text: string): number[] {
  return parseChampionInput(text)
}

async function loadSeriesList() {
  try {
    loading.value = true
    const response = await apiClient.get('/api/v1/draft-series')
    seriesList.value = response.data
  } catch (error) {
    console.error('Failed to load draft series:', error)
  } finally {
    loading.value = false
  }
}

async function loadAllGames() {
  if (allGamesLoaded.value || loadingAnalytics.value) return
  loadingAnalytics.value = true
  try {
    const gamesData: DraftGame[] = []
    for (const series of seriesList.value) {
      const response = await apiClient.get(`/api/v1/draft-series/${series.id}`)
      if (response.data.games) {
        gamesData.push(...response.data.games)
      }
    }
    allGames.value = gamesData
    allGamesLoaded.value = true
  } catch (error) {
    console.error('Failed to load all games:', error)
  } finally {
    loadingAnalytics.value = false
  }
}

async function createSeries() {
  try {
    await apiClient.post('/api/v1/draft-series', newSeries.value)
    showCreateSeries.value = false
    newSeries.value = {
      date: new Date().toISOString().split('T')[0],
      opponent_name: '',
      format: 'bo1',
      notes: '',
    }
    await loadSeriesList()
  } catch (error) {
    console.error('Failed to create series:', error)
  }
}

async function openSeries(series: DraftSeries) {
  try {
    const response = await apiClient.get(`/api/v1/draft-series/${series.id}`)
    selectedSeries.value = response.data
  } catch (error) {
    console.error('Failed to load series details:', error)
  }
}

async function deleteSeries(id: number) {
  if (!confirm('Supprimer cette serie et toutes ses games ?')) return
  try {
    await apiClient.delete(`/api/v1/draft-series/${id}`)
    selectedSeries.value = null
    allGamesLoaded.value = false
    await loadSeriesList()
  } catch (error) {
    console.error('Failed to delete series:', error)
  }
}

async function addGame() {
  if (!selectedSeries.value) return

  const gameData = {
    game_number: (selectedSeries.value.games?.length || 0) + 1,
    blue_side: newGame.value.blue_side,
    our_bans: parseChampionNames(newGame.value.our_bans_text),
    opponent_bans: parseChampionNames(newGame.value.opponent_bans_text),
    our_picks: parseChampionNames(newGame.value.our_picks_text),
    opponent_picks: parseChampionNames(newGame.value.opponent_picks_text),
    result: newGame.value.result,
    import_source: importUrl.value ? 'url' : 'manual',
    import_url: importUrl.value || null,
    notes: newGame.value.notes,
  }

  try {
    await apiClient.post(`/api/v1/draft-series/${selectedSeries.value.id}/games`, gameData)
    showAddGame.value = false
    newGame.value = {
      blue_side: true,
      result: null,
      our_bans_text: '',
      opponent_bans_text: '',
      our_picks_text: '',
      opponent_picks_text: '',
      notes: '',
    }
    importUrl.value = ''
    importError.value = ''
    importSuccess.value = ''
    allGamesLoaded.value = false
    await openSeries(selectedSeries.value)
    await loadSeriesList()
  } catch (error) {
    console.error('Failed to add game:', error)
  }
}

function editGame(game: DraftGame) {
  console.log('Edit game:', game)
}

async function importDraft() {
  if (!importUrl.value) return

  importing.value = true
  importError.value = ''
  importSuccess.value = ''

  try {
    const response = await apiClient.post('/api/v1/draft-series/import', {
      url: importUrl.value,
      is_blue_side: newGame.value.blue_side,
    })

    if (response.data.success && response.data.data) {
      const data = response.data.data
      newGame.value.our_bans_text = data.our_bans.join(', ')
      newGame.value.opponent_bans_text = data.opponent_bans.join(', ')
      newGame.value.our_picks_text = data.our_picks.join(', ')
      newGame.value.opponent_picks_text = data.opponent_picks.join(', ')
      importSuccess.value = response.data.message
    } else {
      importError.value = response.data.message || 'Echec de l\'import'
    }
  } catch (error: any) {
    console.error('Failed to import draft:', error)
    importError.value = error.response?.data?.detail || 'Echec de l\'import depuis l\'URL'
  } finally {
    importing.value = false
  }
}

async function deleteGame(gameId: number) {
  if (!selectedSeries.value) return
  if (!confirm('Supprimer cette game ?')) return

  try {
    await apiClient.delete(`/api/v1/draft-series/${selectedSeries.value.id}/games/${gameId}`)
    allGamesLoaded.value = false
    await openSeries(selectedSeries.value)
    await loadSeriesList()
  } catch (error) {
    console.error('Failed to delete game:', error)
  }
}

// Watch tab changes to load analytics data
watch(activeTab, async (newTab) => {
  if (['champions', 'synergies', 'comps'].includes(newTab) && !allGamesLoaded.value) {
    await loadAllGames()
  }
})

onMounted(async () => {
  await loadChampionData()
  await loadSeriesList()
  // Pre-load games for stats
  if (seriesList.value.length > 0) {
    await loadAllGames()
  }
})
</script>
