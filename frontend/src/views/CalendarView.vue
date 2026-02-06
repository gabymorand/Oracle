<template>
  <div class="min-h-screen bg-gray-900">
    <AppNavbar :show-back-button="true" />

    <div class="max-w-7xl mx-auto px-4 py-8">
      <!-- Tabs -->
      <div class="mb-6 flex gap-2 border-b border-gray-700">
        <button
          @click="activeTab = 'calendar'"
          :class="[
            'px-6 py-3 font-medium transition border-b-2 -mb-px',
            activeTab === 'calendar'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-gray-400 hover:text-white',
          ]"
        >
          Calendrier
        </button>
        <button
          @click="activeTab = 'planning'"
          :class="[
            'px-6 py-3 font-medium transition border-b-2 -mb-px',
            activeTab === 'planning'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-gray-400 hover:text-white',
          ]"
        >
          Disponibilites
        </button>
      </div>

      <!-- Calendar Tab -->
      <div v-if="activeTab === 'calendar'">
        <!-- Header with Month Navigation -->
        <div class="mb-6 flex justify-between items-center">
          <div class="flex items-center gap-4">
            <button
              @click="previousMonth"
              class="p-2 hover:bg-gray-800 rounded-lg transition"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 19l-7-7 7-7"
                />
              </svg>
            </button>
            <h1 class="text-3xl font-bold min-w-64 text-center">
              {{ monthName }} {{ currentYear }}
            </h1>
            <button
              @click="nextMonth"
              class="p-2 hover:bg-gray-800 rounded-lg transition"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </button>
          </div>
          <button
            @click="showCreateEvent = true"
            class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition flex items-center gap-2"
          >
            <span class="text-xl">+</span> Nouvel Event
          </button>
        </div>

      <!-- Loading state -->
      <div v-if="loading" class="text-center py-12 text-gray-400">
        Chargement du calendrier...
      </div>

      <!-- Calendar Grid -->
      <div v-else class="bg-gray-800 rounded-lg p-4 mb-6">
        <!-- Day headers -->
        <div class="grid grid-cols-7 gap-1 mb-2">
          <div
            v-for="day in ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']"
            :key="day"
            class="text-center text-gray-400 text-sm py-2 font-medium"
          >
            {{ day }}
          </div>
        </div>

        <!-- Calendar days -->
        <div class="grid grid-cols-7 gap-1">
          <div
            v-for="(day, index) in calendarDays"
            :key="index"
            @click="selectDay(day)"
            :class="[
              'min-h-24 p-2 rounded-lg cursor-pointer transition',
              day.isCurrentMonth
                ? 'bg-gray-700 hover:bg-gray-650'
                : 'bg-gray-800/50 text-gray-600',
              day.isToday ? 'ring-2 ring-blue-500' : '',
              selectedDate === day.date ? 'ring-2 ring-blue-400' : '',
            ]"
          >
            <div class="text-sm font-semibold mb-1">{{ day.dayNumber }}</div>

            <!-- Event indicators -->
            <div class="space-y-1">
              <div
                v-for="event in getEventsForDay(day.date).slice(0, 2)"
                :key="event.id"
                class="flex items-center gap-1"
              >
                <!-- W/L badges for scrims with draft series -->
                <template v-if="event.event_type === 'scrim' && getScrimResultBadges(event).length > 0">
                  <span
                    v-for="badge in getScrimResultBadges(event)"
                    :key="badge.key"
                    :class="[
                      'w-5 h-5 rounded text-xs font-bold flex items-center justify-center flex-shrink-0',
                      badge.result === 'win' ? 'bg-green-600 text-white' :
                      badge.result === 'loss' ? 'bg-red-600 text-white' : 'bg-gray-600 text-gray-300'
                    ]"
                  >
                    {{ badge.result === 'win' ? 'W' : badge.result === 'loss' ? 'L' : '?' }}
                  </span>
                  <span class="text-xs text-gray-400 truncate">{{ event.opponent_name || '' }}</span>
                </template>
                <!-- Regular event display -->
                <div
                  v-else
                  :class="[
                    'text-xs px-1 py-0.5 rounded truncate w-full',
                    getEventColor(event.event_type),
                  ]"
                >
                  {{ event.title }}
                </div>
              </div>
              <div
                v-if="getEventsForDay(day.date).length > 2"
                class="text-xs text-gray-400"
              >
                +{{ getEventsForDay(day.date).length - 2 }} more
              </div>
            </div>

            <!-- Availability indicator (colored dots) -->
            <div
              v-if="day.isCurrentMonth"
              class="flex gap-1 mt-1"
              :title="getAvailabilityTooltip(day.date)"
            >
              <div
                v-for="slot in ['morning', 'afternoon', 'evening'] as const"
                :key="slot"
                :class="[
                  'w-2 h-2 rounded-full',
                  getSlotAvailabilityColor(day.date, slot),
                ]"
              />
            </div>

            <!-- Full team available indicator -->
            <div
              v-if="day.isCurrentMonth && hasFullTeamSlot(day.date)"
              class="mt-1"
            >
              <div
                class="text-xs px-1 py-0.5 rounded bg-emerald-600/80 text-emerald-100 font-medium text-center animate-pulse"
                :title="getFullTeamTooltip(day.date)"
              >
                5/5
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Legend -->
      <div class="flex flex-wrap gap-4 mb-6 text-sm text-gray-400">
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 rounded bg-red-600"></div>
          <span>Scrim</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 rounded bg-yellow-600"></div>
          <span>Match Officiel</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 rounded bg-green-600"></div>
          <span>Entrainement</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 rounded bg-purple-600"></div>
          <span>Meeting</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 rounded bg-gray-600"></div>
          <span>Autre</span>
        </div>
        <div class="ml-4 flex items-center gap-2">
          <div class="flex gap-0.5">
            <div class="w-2 h-2 rounded-full bg-green-500"></div>
            <div class="w-2 h-2 rounded-full bg-yellow-500"></div>
            <div class="w-2 h-2 rounded-full bg-red-500"></div>
          </div>
          <span>Disponibilites (M/AM/S)</span>
        </div>
      </div>

      <!-- Selected Day Detail Panel -->
      <div
        v-if="selectedDate && selectedDayDetail"
        class="bg-gray-800 rounded-lg p-6"
      >
        <h2 class="text-xl font-semibold mb-4">{{ formatDate(selectedDate) }}</h2>

        <!-- Events for the day -->
        <div class="mb-6">
          <h3 class="text-lg font-medium mb-3 flex items-center gap-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            Events
          </h3>
          <div
            v-if="selectedDayDetail.events.length === 0"
            class="text-gray-400 text-sm"
          >
            Aucun event prevu
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="event in selectedDayDetail.events"
              :key="event.id"
              @click="openEvent(event)"
              :class="[
                'p-3 rounded-lg cursor-pointer transition border-l-4',
                getEventBorderColor(event.event_type),
                'bg-gray-700 hover:bg-gray-650',
              ]"
            >
              <div class="flex justify-between items-start">
                <div class="flex-1">
                  <div class="flex items-center gap-2">
                    <span class="font-semibold">{{ event.title }}</span>
                    <!-- W/L badges for scrims -->
                    <template v-if="event.event_type === 'scrim' && getScrimResultBadges(event).length > 0">
                      <span
                        v-for="badge in getScrimResultBadges(event)"
                        :key="badge.key"
                        :class="[
                          'w-6 h-6 rounded text-xs font-bold flex items-center justify-center',
                          badge.result === 'win' ? 'bg-green-600 text-white' :
                          badge.result === 'loss' ? 'bg-red-600 text-white' : 'bg-gray-600 text-gray-300'
                        ]"
                      >
                        {{ badge.result === 'win' ? 'W' : badge.result === 'loss' ? 'L' : '?' }}
                      </span>
                    </template>
                  </div>
                  <div class="text-sm text-gray-300">
                    {{ getSlotLabel(event.slot) }}
                    <span v-if="event.opponent_name">
                      vs {{ event.opponent_name }}</span
                    >
                  </div>
                  <div
                    v-if="event.description"
                    class="text-sm text-gray-400 mt-1"
                  >
                    {{ event.description }}
                  </div>
                </div>
                <span
                  :class="[
                    'text-xs px-2 py-1 rounded',
                    getEventColor(event.event_type),
                  ]"
                >
                  {{ getEventTypeLabel(event.event_type) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Games Section (from scrims) -->
        <div v-if="getGamesForSelectedDay().length > 0" class="mb-6">
          <h3 class="text-lg font-medium mb-3 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Matchs ({{ getGamesForSelectedDay().length }})
          </h3>
          <div class="space-y-2">
            <div
              v-for="{ game, series, event } in getGamesForSelectedDay()"
              :key="game.id"
              @click="openGameDetail(game, series)"
              class="bg-gray-700 hover:bg-gray-650 rounded-lg p-3 cursor-pointer transition flex items-center gap-3"
            >
              <!-- W/L Badge -->
              <span
                :class="[
                  'w-8 h-8 rounded flex items-center justify-center font-bold text-lg',
                  game.result === 'win' ? 'bg-green-600 text-white' :
                  game.result === 'loss' ? 'bg-red-600 text-white' : 'bg-gray-600 text-gray-300'
                ]"
              >
                {{ game.result === 'win' ? 'W' : game.result === 'loss' ? 'L' : '?' }}
              </span>

              <!-- Time -->
              <span v-if="game.created_at" class="text-gray-400 text-sm w-12">
                {{ formatGameTime(game.created_at) }}
              </span>

              <!-- Champion Icons (our picks) -->
              <div class="flex items-center gap-1">
                <img
                  v-for="(pick, idx) in (game.our_picks || []).slice(0, 5)"
                  :key="idx"
                  :src="getChampionIconUrl(pick)"
                  :alt="getChampionName(pick)"
                  :title="getChampionName(pick)"
                  class="w-8 h-8 rounded border border-gray-600"
                  @error="(e: Event) => (e.target as HTMLImageElement).src = 'https://ddragon.leagueoflegends.com/cdn/14.1.1/img/champion/Aatrox.png'"
                />
              </div>

              <!-- Opponent info -->
              <span v-if="event.opponent_name" class="text-gray-400 text-sm ml-auto">
                vs {{ event.opponent_name }}
              </span>

              <!-- Arrow -->
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
        </div>

        <!-- Full Team Available Alert -->
        <div
          v-if="getFullTeamSlotsForDay(selectedDate).length > 0"
          class="mb-6 p-4 bg-emerald-900/50 border border-emerald-600 rounded-lg"
        >
          <h3 class="text-lg font-medium mb-2 flex items-center gap-2 text-emerald-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Equipe complete disponible !
          </h3>
          <p class="text-sm text-emerald-300 mb-3">
            Tous les joueurs sont disponibles sur ce(s) creneau(x) :
          </p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="slot in getFullTeamSlotsForDay(selectedDate)"
              :key="slot"
              @click="quickCreateEvent(slot)"
              class="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 px-3 py-2 rounded-lg text-sm font-medium transition"
            >
              <span>{{ getSlotLabel(slot) }}</span>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Planifier
            </button>
          </div>
        </div>

        <!-- Availabilities for the day -->
        <div>
          <h3 class="text-lg font-medium mb-3 flex items-center gap-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
              />
            </svg>
            Disponibilites de l'equipe
          </h3>
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="text-gray-400 text-sm">
                  <th class="text-left py-2 px-3">Joueur</th>
                  <th class="text-center py-2 px-3">Matin</th>
                  <th class="text-center py-2 px-3">Apres-midi</th>
                  <th class="text-center py-2 px-3">Soir</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="player in selectedDayDetail.availabilities"
                  :key="player.player_id"
                  :class="[
                    'border-t border-gray-700',
                    player.player_id === currentPlayerId ? 'bg-blue-900/20' : '',
                  ]"
                >
                  <td class="py-2 px-3 font-medium">
                    {{ player.player_name }}
                    <span v-if="player.player_id === currentPlayerId" class="text-blue-400 text-xs">(moi)</span>
                  </td>
                  <td class="text-center py-2 px-3">
                    <span
                      :class="
                        player.morning ? 'text-green-400' : 'text-red-400'
                      "
                    >
                      {{ player.morning ? 'Dispo' : 'Indispo' }}
                    </span>
                  </td>
                  <td class="text-center py-2 px-3">
                    <span
                      :class="
                        player.afternoon ? 'text-green-400' : 'text-red-400'
                      "
                    >
                      {{ player.afternoon ? 'Dispo' : 'Indispo' }}
                    </span>
                  </td>
                  <td class="text-center py-2 px-3">
                    <span
                      :class="
                        player.evening ? 'text-green-400' : 'text-red-400'
                      "
                    >
                      {{ player.evening ? 'Dispo' : 'Indispo' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      </div>

      <!-- Planning Tab -->
      <div v-else-if="activeTab === 'planning'">
        <!-- Week navigation -->
        <div class="mb-6 flex items-center gap-4">
          <button
            @click="previousWeek"
            class="p-2 hover:bg-gray-800 rounded-lg transition"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <span class="text-lg font-medium min-w-48 text-center">
            {{ weekRangeLabel }}
          </span>
          <button
            @click="nextWeek"
            class="p-2 hover:bg-gray-800 rounded-lg transition"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
          <button
            @click="goToCurrentWeek"
            class="ml-4 px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm transition"
          >
            Aujourd'hui
          </button>
        </div>

        <!-- Loading -->
        <div v-if="loadingPlanning" class="text-center py-12 text-gray-400">
          Chargement...
        </div>

        <!-- Planning Table - Player View -->
        <div v-else-if="isPlayer && currentPlayerId" class="bg-gray-800 rounded-lg overflow-hidden">
          <table class="w-full">
            <thead>
              <tr class="bg-gray-700">
                <th class="py-3 px-4 text-left font-medium">Jour</th>
                <th class="py-3 px-4 text-center font-medium">
                  <div>Matin</div>
                  <div class="text-xs text-gray-400 font-normal">9h-12h</div>
                </th>
                <th class="py-3 px-4 text-center font-medium">
                  <div>Apres-midi</div>
                  <div class="text-xs text-gray-400 font-normal">14h-18h</div>
                </th>
                <th class="py-3 px-4 text-center font-medium">
                  <div>Soir</div>
                  <div class="text-xs text-gray-400 font-normal">18h-22h</div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="day in weekDays"
                :key="day.date"
                :class="[
                  'border-t border-gray-700 transition',
                  day.isToday ? 'bg-blue-900/20' : 'hover:bg-gray-750',
                  day.isPast ? 'opacity-50' : '',
                ]"
              >
                <td class="py-4 px-4">
                  <div class="font-medium" :class="day.isToday ? 'text-blue-400' : ''">
                    {{ day.dayName }}
                    <span v-if="day.isToday" class="text-xs ml-1">(aujourd'hui)</span>
                  </div>
                  <div class="text-sm text-gray-400">{{ day.dateLabel }}</div>
                </td>
                <td class="py-4 px-4 text-center">
                  <button
                    @click="togglePlanningAvailability(day.date, 'morning')"
                    :disabled="day.isPast || savingPlanningSlot === `${day.date}-morning`"
                    :class="[
                      'w-16 h-10 rounded-lg font-medium transition',
                      getPlanningAvailability(day.date, 'morning')
                        ? 'bg-green-600 hover:bg-green-700 text-white'
                        : 'bg-gray-600 hover:bg-gray-500 text-gray-300',
                      day.isPast ? 'cursor-not-allowed opacity-50' : 'cursor-pointer',
                    ]"
                  >
                    {{ savingPlanningSlot === `${day.date}-morning` ? '...' : (getPlanningAvailability(day.date, 'morning') ? 'Oui' : 'Non') }}
                  </button>
                </td>
                <td class="py-4 px-4 text-center">
                  <button
                    @click="togglePlanningAvailability(day.date, 'afternoon')"
                    :disabled="day.isPast || savingPlanningSlot === `${day.date}-afternoon`"
                    :class="[
                      'w-16 h-10 rounded-lg font-medium transition',
                      getPlanningAvailability(day.date, 'afternoon')
                        ? 'bg-green-600 hover:bg-green-700 text-white'
                        : 'bg-gray-600 hover:bg-gray-500 text-gray-300',
                      day.isPast ? 'cursor-not-allowed opacity-50' : 'cursor-pointer',
                    ]"
                  >
                    {{ savingPlanningSlot === `${day.date}-afternoon` ? '...' : (getPlanningAvailability(day.date, 'afternoon') ? 'Oui' : 'Non') }}
                  </button>
                </td>
                <td class="py-4 px-4 text-center">
                  <button
                    @click="togglePlanningAvailability(day.date, 'evening')"
                    :disabled="day.isPast || savingPlanningSlot === `${day.date}-evening`"
                    :class="[
                      'w-16 h-10 rounded-lg font-medium transition',
                      getPlanningAvailability(day.date, 'evening')
                        ? 'bg-green-600 hover:bg-green-700 text-white'
                        : 'bg-gray-600 hover:bg-gray-500 text-gray-300',
                      day.isPast ? 'cursor-not-allowed opacity-50' : 'cursor-pointer',
                    ]"
                  >
                    {{ savingPlanningSlot === `${day.date}-evening` ? '...' : (getPlanningAvailability(day.date, 'evening') ? 'Oui' : 'Non') }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Planning Table - Coach/All Players View -->
        <div v-else class="bg-gray-800 rounded-lg overflow-hidden">
          <table class="w-full">
            <thead>
              <tr class="bg-gray-700">
                <th class="py-3 px-4 text-left font-medium">Jour</th>
                <th class="py-3 px-4 text-center font-medium">
                  <div>Matin</div>
                  <div class="text-xs text-gray-400 font-normal">9h-12h</div>
                </th>
                <th class="py-3 px-4 text-center font-medium">
                  <div>Apres-midi</div>
                  <div class="text-xs text-gray-400 font-normal">14h-18h</div>
                </th>
                <th class="py-3 px-4 text-center font-medium">
                  <div>Soir</div>
                  <div class="text-xs text-gray-400 font-normal">18h-22h</div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="day in weekDays"
                :key="day.date"
                :class="[
                  'border-t border-gray-700',
                  day.isToday ? 'bg-blue-900/20' : '',
                ]"
              >
                <td class="py-4 px-4">
                  <div class="font-medium" :class="day.isToday ? 'text-blue-400' : ''">
                    {{ day.dayName }}
                    <span v-if="day.isToday" class="text-xs ml-1">(aujourd'hui)</span>
                  </div>
                  <div class="text-sm text-gray-400">{{ day.dateLabel }}</div>
                </td>
                <td class="py-4 px-4">
                  <div class="flex flex-col items-center gap-1">
                    <div
                      :class="[
                        'text-lg font-bold px-3 py-1 rounded',
                        getPlanningSlotStatus(day.date, 'morning').class,
                      ]"
                    >
                      {{ getPlanningSlotStatus(day.date, 'morning').count }}/{{ players.length }}
                    </div>
                    <div class="text-xs text-gray-400">
                      {{ getPlanningSlotStatus(day.date, 'morning').names }}
                    </div>
                  </div>
                </td>
                <td class="py-4 px-4">
                  <div class="flex flex-col items-center gap-1">
                    <div
                      :class="[
                        'text-lg font-bold px-3 py-1 rounded',
                        getPlanningSlotStatus(day.date, 'afternoon').class,
                      ]"
                    >
                      {{ getPlanningSlotStatus(day.date, 'afternoon').count }}/{{ players.length }}
                    </div>
                    <div class="text-xs text-gray-400">
                      {{ getPlanningSlotStatus(day.date, 'afternoon').names }}
                    </div>
                  </div>
                </td>
                <td class="py-4 px-4">
                  <div class="flex flex-col items-center gap-1">
                    <div
                      :class="[
                        'text-lg font-bold px-3 py-1 rounded',
                        getPlanningSlotStatus(day.date, 'evening').class,
                      ]"
                    >
                      {{ getPlanningSlotStatus(day.date, 'evening').count }}/{{ players.length }}
                    </div>
                    <div class="text-xs text-gray-400">
                      {{ getPlanningSlotStatus(day.date, 'evening').names }}
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Legend -->
        <div class="mt-6 flex flex-wrap gap-6 text-sm text-gray-400">
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded bg-green-600 flex items-center justify-center text-white text-xs font-bold">5/5</div>
            <span>Equipe complete</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded bg-yellow-600 flex items-center justify-center text-black text-xs font-bold">3/5</div>
            <span>Partiel</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded bg-red-600 flex items-center justify-center text-white text-xs font-bold">1/5</div>
            <span>Peu de dispos</span>
          </div>
        </div>

        <!-- Quick actions for full team slots (coach view) -->
        <div v-if="!isPlayer && fullTeamSlots.length > 0" class="mt-6 p-4 bg-emerald-900/30 border border-emerald-600 rounded-lg">
          <h3 class="text-lg font-medium mb-3 text-emerald-400 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Creneaux avec equipe complete
          </h3>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="slot in fullTeamSlots"
              :key="`${slot.date}-${slot.slot}`"
              @click="quickCreateEventFromPlanning(slot.date, slot.slot)"
              class="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 px-3 py-2 rounded-lg text-sm font-medium transition"
            >
              <span>{{ formatSlotDate(slot.date) }} - {{ getPlanningSlotLabel(slot.slot) }}</span>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Event Modal -->
    <div
      v-if="showCreateEvent"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
    >
      <div class="bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
        <h3 class="text-xl font-semibold mb-4">Nouvel Evenement</h3>
        <form @submit.prevent="createEvent" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Titre *</label>
            <input
              v-model="newEvent.title"
              type="text"
              required
              class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="Ex: Scrim vs Team X"
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Type *</label>
            <select
              v-model="newEvent.event_type"
              required
              class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            >
              <option value="scrim">Scrim</option>
              <option value="training">Entrainement</option>
              <option value="official_match">Match Officiel</option>
              <option value="meeting">Meeting</option>
              <option value="other">Autre</option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Date *</label>
              <input
                v-model="newEvent.date"
                type="date"
                required
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Creneau *</label>
              <select
                v-model="newEvent.slot"
                required
                class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                <option value="morning">Matin (9h-12h)</option>
                <option value="afternoon">Apres-midi (14h-18h)</option>
                <option value="evening">Soir (18h-22h)</option>
              </select>
            </div>
          </div>

          <div v-if="newEvent.event_type === 'scrim' || newEvent.event_type === 'official_match'">
            <label class="block text-sm font-medium mb-1">Adversaire</label>
            <input
              v-model="newEvent.opponent_name"
              type="text"
              class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="Nom de l'equipe adverse"
            />
          </div>

          <div v-if="newEvent.event_type === 'scrim' || newEvent.event_type === 'official_match'">
            <label class="block text-sm font-medium mb-1">Joueurs adverses (pour op.gg)</label>
            <input
              v-model="newEvent.opponent_players"
              type="text"
              class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="Player1, Player2, Player3, Player4, Player5"
            />
            <p class="text-xs text-gray-500 mt-1">Separes par des virgules</p>
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Description</label>
            <textarea
              v-model="newEvent.description"
              rows="2"
              class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="Details supplementaires..."
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Lieu</label>
            <input
              v-model="newEvent.location"
              type="text"
              class="w-full bg-gray-700 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="Ex: Discord, Gaming House..."
            />
          </div>

          <div class="flex justify-end gap-3 pt-4">
            <button
              type="button"
              @click="showCreateEvent = false"
              class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
            >
              Annuler
            </button>
            <button
              type="submit"
              :disabled="creatingEvent"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition disabled:opacity-50"
            >
              {{ creatingEvent ? 'Creation...' : 'Creer' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Event Detail Modal -->
    <div
      v-if="selectedEvent"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
    >
      <div class="bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
        <div class="flex justify-between items-start mb-4">
          <h3 class="text-xl font-semibold">{{ selectedEvent.title }}</h3>
          <button
            @click="selectedEvent = null"
            class="text-gray-400 hover:text-white"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <div class="space-y-3 mb-6">
          <div class="flex items-center gap-2">
            <span
              :class="[
                'text-xs px-2 py-1 rounded',
                getEventColor(selectedEvent.event_type),
              ]"
            >
              {{ getEventTypeLabel(selectedEvent.event_type) }}
            </span>
          </div>

          <div class="text-gray-300">
            <span class="text-gray-400">Date:</span>
            {{ formatDate(selectedEvent.date) }}
          </div>

          <div class="text-gray-300">
            <span class="text-gray-400">Creneau:</span>
            {{ getSlotLabel(selectedEvent.slot) }}
          </div>

          <div v-if="selectedEvent.opponent_name" class="text-gray-300">
            <span class="text-gray-400">Adversaire:</span>
            {{ selectedEvent.opponent_name }}
          </div>

          <div v-if="selectedEvent.location" class="text-gray-300">
            <span class="text-gray-400">Lieu:</span>
            {{ selectedEvent.location }}
          </div>

          <div v-if="selectedEvent.description" class="text-gray-300">
            <span class="text-gray-400">Description:</span>
            {{ selectedEvent.description }}
          </div>
        </div>

        <div class="flex justify-between gap-3">
          <button
            v-if="selectedEvent.event_type === 'scrim'"
            @click="goToScrimDetail"
            class="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition flex items-center gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            Gerer Scrim
          </button>
          <div v-else></div>
          <div class="flex gap-3">
            <button
              @click="deleteEventConfirm"
              class="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition"
            >
              Supprimer
            </button>
            <button
              @click="selectedEvent = null"
              class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
            >
              Fermer
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Game Detail Modal -->
    <div
      v-if="selectedGameDetail"
      class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
    >
      <div class="bg-gray-800 rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="sticky top-0 bg-gray-800 border-b border-gray-700 p-4 flex justify-between items-center">
          <div class="flex items-center gap-3">
            <span
              :class="[
                'w-10 h-10 rounded flex items-center justify-center font-bold text-xl',
                selectedGameDetail.game.result === 'win' ? 'bg-green-600 text-white' :
                selectedGameDetail.game.result === 'loss' ? 'bg-red-600 text-white' : 'bg-gray-600 text-gray-300'
              ]"
            >
              {{ selectedGameDetail.game.result === 'win' ? 'W' : selectedGameDetail.game.result === 'loss' ? 'L' : '?' }}
            </span>
            <div>
              <h3 class="text-xl font-semibold">
                Game {{ selectedGameDetail.game.game_number || 1 }}
              </h3>
              <p v-if="selectedGameDetail.series.opponent_name" class="text-gray-400 text-sm">
                vs {{ selectedGameDetail.series.opponent_name }}
              </p>
            </div>
          </div>
          <button
            @click="selectedGameDetail = null"
            class="text-gray-400 hover:text-white p-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Game Content -->
        <div class="p-6 space-y-6">
          <!-- Side Information -->
          <div class="flex items-center gap-4 text-sm">
            <span
              :class="[
                'px-3 py-1 rounded font-medium',
                selectedGameDetail.game.blue_side ? 'bg-blue-600 text-white' : 'bg-red-600 text-white'
              ]"
            >
              {{ selectedGameDetail.game.blue_side ? 'Blue Side' : 'Red Side' }}
            </span>
          </div>

          <!-- Ally Team Draft -->
          <div class="bg-gray-700/50 rounded-lg p-4">
            <h4 class="text-lg font-medium mb-3 flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-blue-500"></span>
              Notre equipe
            </h4>

            <!-- Bans -->
            <div v-if="selectedGameDetail.game.our_bans && selectedGameDetail.game.our_bans.length > 0" class="mb-4">
              <p class="text-xs text-gray-400 mb-2">BANS</p>
              <div class="flex gap-2">
                <div
                  v-for="(ban, idx) in selectedGameDetail.game.our_bans"
                  :key="'our-ban-' + idx"
                  class="relative"
                >
                  <img
                    :src="getChampionIconUrl(ban)"
                    :alt="getChampionName(ban)"
                    :title="getChampionName(ban)"
                    class="w-10 h-10 rounded grayscale opacity-60"
                    @error="(e: Event) => (e.target as HTMLImageElement).src = 'https://ddragon.leagueoflegends.com/cdn/14.1.1/img/champion/Aatrox.png'"
                  />
                  <div class="absolute inset-0 flex items-center justify-center">
                    <span class="text-red-500 text-2xl font-bold">×</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Picks -->
            <div>
              <p class="text-xs text-gray-400 mb-2">PICKS</p>
              <div class="flex gap-3">
                <div
                  v-for="(pick, idx) in (selectedGameDetail.game.our_picks || [])"
                  :key="'our-pick-' + idx"
                  class="flex flex-col items-center gap-1"
                >
                  <img
                    :src="getChampionIconUrl(pick)"
                    :alt="getChampionName(pick)"
                    :title="getChampionName(pick)"
                    class="w-14 h-14 rounded border-2 border-blue-500"
                    @error="(e: Event) => (e.target as HTMLImageElement).src = 'https://ddragon.leagueoflegends.com/cdn/14.1.1/img/champion/Aatrox.png'"
                  />
                  <span class="text-xs text-gray-300">{{ getChampionName(pick) }}</span>
                  <span class="text-xs text-gray-500">{{ ['TOP', 'JGL', 'MID', 'ADC', 'SUP'][idx] || '' }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Opponent Team Draft -->
          <div class="bg-gray-700/50 rounded-lg p-4">
            <h4 class="text-lg font-medium mb-3 flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-red-500"></span>
              Equipe adverse
            </h4>

            <!-- Bans -->
            <div v-if="selectedGameDetail.game.opponent_bans && selectedGameDetail.game.opponent_bans.length > 0" class="mb-4">
              <p class="text-xs text-gray-400 mb-2">BANS</p>
              <div class="flex gap-2">
                <div
                  v-for="(ban, idx) in selectedGameDetail.game.opponent_bans"
                  :key="'opponent-ban-' + idx"
                  class="relative"
                >
                  <img
                    :src="getChampionIconUrl(ban)"
                    :alt="getChampionName(ban)"
                    :title="getChampionName(ban)"
                    class="w-10 h-10 rounded grayscale opacity-60"
                    @error="(e: Event) => (e.target as HTMLImageElement).src = 'https://ddragon.leagueoflegends.com/cdn/14.1.1/img/champion/Aatrox.png'"
                  />
                  <div class="absolute inset-0 flex items-center justify-center">
                    <span class="text-red-500 text-2xl font-bold">×</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Picks -->
            <div>
              <p class="text-xs text-gray-400 mb-2">PICKS</p>
              <div class="flex gap-3">
                <div
                  v-for="(pick, idx) in (selectedGameDetail.game.opponent_picks || [])"
                  :key="'opponent-pick-' + idx"
                  class="flex flex-col items-center gap-1"
                >
                  <img
                    :src="getChampionIconUrl(pick)"
                    :alt="getChampionName(pick)"
                    :title="getChampionName(pick)"
                    class="w-14 h-14 rounded border-2 border-red-500"
                    @error="(e: Event) => (e.target as HTMLImageElement).src = 'https://ddragon.leagueoflegends.com/cdn/14.1.1/img/champion/Aatrox.png'"
                  />
                  <span class="text-xs text-gray-300">{{ getChampionName(pick) }}</span>
                  <span class="text-xs text-gray-500">{{ ['TOP', 'JGL', 'MID', 'ADC', 'SUP'][idx] || '' }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Notes -->
          <div v-if="selectedGameDetail.game.notes" class="bg-gray-700/50 rounded-lg p-4">
            <h4 class="text-sm font-medium text-gray-400 mb-2">Notes</h4>
            <p class="text-gray-200 whitespace-pre-wrap">{{ selectedGameDetail.game.notes }}</p>
          </div>
        </div>

        <!-- Footer -->
        <div class="sticky bottom-0 bg-gray-800 border-t border-gray-700 p-4 flex justify-end">
          <button
            @click="selectedGameDetail = null"
            class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppNavbar from '@/components/AppNavbar.vue'
import { useAuthStore } from '@/stores/auth'
import { calendarApi, playersApi, draftSeriesApi } from '@/api'
import { getChampionIconUrl, getChampionName, loadChampionData } from '@/utils/champions'
import type {
  CalendarEvent,
  CalendarEventWithSeries,
  DayDetail,
  DayAvailabilitySummary,
  EventType,
  TimeSlot,
  Player,
  DraftSeriesWithGames,
  DraftGame,
} from '@/types'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

// Player identification
const isPlayer = computed(() => authStore.userRole === 'player')
const currentPlayerId = computed(() => {
  const id = sessionStorage.getItem('selected_player_id')
  return id ? parseInt(id, 10) : null
})

// Availability slots config
const availabilitySlots = [
  { key: 'morning' as TimeSlot, label: 'Matin (9h-12h)' },
  { key: 'afternoon' as TimeSlot, label: 'Apres-midi (14h-18h)' },
  { key: 'evening' as TimeSlot, label: 'Soir (18h-22h)' },
]

// State
const activeTab = ref<'calendar' | 'planning'>('calendar')
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)
const events = ref<CalendarEvent[]>([])
const monthAvailabilities = ref<DayAvailabilitySummary[]>([])
const draftSeriesMap = ref<Map<number, DraftSeriesWithGames>>(new Map())
const selectedDate = ref<string | null>(null)
const selectedDayDetail = ref<DayDetail | null>(null)
const selectedEvent = ref<CalendarEvent | null>(null)
const selectedGameDetail = ref<{ game: DraftGame; series: DraftSeriesWithGames } | null>(null)
const showCreateEvent = ref(false)
const loading = ref(true)
const creatingEvent = ref(false)
const savingAvailability = ref(false)

// Planning tab state
const players = ref<Player[]>([])
const weekOffset = ref(0)
const planningAvailabilities = ref<DayAvailabilitySummary[]>([])
const loadingPlanning = ref(false)
const savingPlanningSlot = ref<string | null>(null)

const newEvent = ref({
  title: '',
  event_type: 'scrim' as EventType,
  date: new Date().toISOString().split('T')[0],
  slot: 'evening' as TimeSlot,
  opponent_name: '',
  opponent_players: '',
  description: '',
  location: '',
})

// Computed
const monthName = computed(() => {
  const months = [
    'Janvier',
    'Fevrier',
    'Mars',
    'Avril',
    'Mai',
    'Juin',
    'Juillet',
    'Aout',
    'Septembre',
    'Octobre',
    'Novembre',
    'Decembre',
  ]
  return months[currentMonth.value - 1]
})

interface CalendarDay {
  date: string
  dayNumber: number
  isCurrentMonth: boolean
  isToday: boolean
}

const calendarDays = computed((): CalendarDay[] => {
  const year = currentYear.value
  const month = currentMonth.value - 1 // JS months are 0-indexed
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const days: CalendarDay[] = []

  // Get day of week for first day (0=Sunday, adjust for Monday start)
  let startDayOfWeek = firstDay.getDay()
  if (startDayOfWeek === 0) startDayOfWeek = 7
  startDayOfWeek-- // Now 0=Monday

  // Add days from previous month
  const prevMonthLastDay = new Date(year, month, 0).getDate()
  for (let i = startDayOfWeek - 1; i >= 0; i--) {
    const day = prevMonthLastDay - i
    const date = new Date(year, month - 1, day)
    days.push({
      date: formatDateISO(date),
      dayNumber: day,
      isCurrentMonth: false,
      isToday: false,
    })
  }

  // Add days from current month
  const today = new Date()
  for (let day = 1; day <= lastDay.getDate(); day++) {
    const date = new Date(year, month, day)
    days.push({
      date: formatDateISO(date),
      dayNumber: day,
      isCurrentMonth: true,
      isToday:
        date.getDate() === today.getDate() &&
        date.getMonth() === today.getMonth() &&
        date.getFullYear() === today.getFullYear(),
    })
  }

  // Add days from next month to complete the grid (6 rows)
  const remainingDays = 42 - days.length
  for (let day = 1; day <= remainingDays; day++) {
    const date = new Date(year, month + 1, day)
    days.push({
      date: formatDateISO(date),
      dayNumber: day,
      isCurrentMonth: false,
      isToday: false,
    })
  }

  return days
})

// Helper functions
function formatDateISO(date: Date): string {
  return date.toISOString().split('T')[0]
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

function getEventsForDay(dateStr: string): CalendarEvent[] {
  return events.value.filter((e) => e.date === dateStr)
}

function getDraftSeriesForEvent(event: CalendarEvent): DraftSeriesWithGames | undefined {
  if (!event.draft_series_id) return undefined
  return draftSeriesMap.value.get(event.draft_series_id)
}

function getScrimResultBadges(event: CalendarEvent): Array<{ result: string; key: number }> {
  const series = getDraftSeriesForEvent(event)
  if (!series || !series.games || series.games.length === 0) return []
  return series.games.map((game, idx) => ({
    result: game.result || 'unknown',
    key: game.id || idx,
  }))
}

// Get all games for the selected day from scrim events
function getGamesForSelectedDay(): Array<{ game: DraftGame; series: DraftSeriesWithGames; event: CalendarEvent }> {
  if (!selectedDayDetail.value) return []

  const games: Array<{ game: DraftGame; series: DraftSeriesWithGames; event: CalendarEvent }> = []

  for (const event of selectedDayDetail.value.events) {
    if (event.event_type === 'scrim' && event.draft_series_id) {
      const series = draftSeriesMap.value.get(event.draft_series_id)
      if (series && series.games) {
        for (const game of series.games) {
          games.push({ game, series, event })
        }
      }
    }
  }

  return games
}

function openGameDetail(game: DraftGame, series: DraftSeriesWithGames) {
  selectedGameDetail.value = { game, series }
}

function formatGameTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
}

function getEventColor(eventType: EventType): string {
  const colors: Record<EventType, string> = {
    scrim: 'bg-red-600 text-white',
    training: 'bg-green-600 text-white',
    official_match: 'bg-yellow-600 text-black',
    meeting: 'bg-purple-600 text-white',
    other: 'bg-gray-600 text-white',
  }
  return colors[eventType] || colors.other
}

function getEventBorderColor(eventType: EventType): string {
  const colors: Record<EventType, string> = {
    scrim: 'border-red-600',
    training: 'border-green-600',
    official_match: 'border-yellow-600',
    meeting: 'border-purple-600',
    other: 'border-gray-600',
  }
  return colors[eventType] || colors.other
}

function getEventTypeLabel(eventType: EventType): string {
  const labels: Record<EventType, string> = {
    scrim: 'Scrim',
    training: 'Entrainement',
    official_match: 'Match Officiel',
    meeting: 'Meeting',
    other: 'Autre',
  }
  return labels[eventType] || eventType
}

function getSlotLabel(slot: TimeSlot): string {
  const labels: Record<TimeSlot, string> = {
    morning: 'Matin (9h-12h)',
    afternoon: 'Apres-midi (14h-18h)',
    evening: 'Soir (18h-22h)',
  }
  return labels[slot] || slot
}

function getSlotAvailabilityColor(dateStr: string, slot: TimeSlot): string {
  const dayAvail = monthAvailabilities.value.find((d) => d.date === dateStr)
  if (!dayAvail) return 'bg-gray-500'

  const availableCount = dayAvail.availabilities.filter(
    (a) => a[slot]
  ).length
  const total = dayAvail.availabilities.length

  if (total === 0) return 'bg-gray-500'
  if (availableCount === total) return 'bg-green-500'
  if (availableCount >= total / 2) return 'bg-yellow-500'
  return 'bg-red-500'
}

function getAvailabilityTooltip(dateStr: string): string {
  const dayAvail = monthAvailabilities.value.find((d) => d.date === dateStr)
  if (!dayAvail) return ''

  const total = dayAvail.availabilities.length
  const morning = dayAvail.availabilities.filter((a) => a.morning).length
  const afternoon = dayAvail.availabilities.filter((a) => a.afternoon).length
  const evening = dayAvail.availabilities.filter((a) => a.evening).length

  return `Matin: ${morning}/${total}, AM: ${afternoon}/${total}, Soir: ${evening}/${total}`
}

function hasFullTeamSlot(dateStr: string): boolean {
  const dayAvail = monthAvailabilities.value.find((d) => d.date === dateStr)
  if (!dayAvail || dayAvail.availabilities.length < 5) return false

  const total = dayAvail.availabilities.length
  const morning = dayAvail.availabilities.filter((a) => a.morning).length
  const afternoon = dayAvail.availabilities.filter((a) => a.afternoon).length
  const evening = dayAvail.availabilities.filter((a) => a.evening).length

  return morning === total || afternoon === total || evening === total
}

function getFullTeamTooltip(dateStr: string): string {
  const dayAvail = monthAvailabilities.value.find((d) => d.date === dateStr)
  if (!dayAvail) return ''

  const total = dayAvail.availabilities.length
  const slots: string[] = []

  if (dayAvail.availabilities.filter((a) => a.morning).length === total) {
    slots.push('Matin')
  }
  if (dayAvail.availabilities.filter((a) => a.afternoon).length === total) {
    slots.push('Apres-midi')
  }
  if (dayAvail.availabilities.filter((a) => a.evening).length === total) {
    slots.push('Soir')
  }

  return `Equipe complete: ${slots.join(', ')}`
}

function getFullTeamSlotsForDay(dateStr: string | null): TimeSlot[] {
  if (!dateStr || !selectedDayDetail.value) return []

  const avails = selectedDayDetail.value.availabilities
  if (avails.length < 5) return []

  const total = avails.length
  const slots: TimeSlot[] = []

  if (avails.filter((a) => a.morning).length === total) {
    slots.push('morning')
  }
  if (avails.filter((a) => a.afternoon).length === total) {
    slots.push('afternoon')
  }
  if (avails.filter((a) => a.evening).length === total) {
    slots.push('evening')
  }

  return slots
}

function quickCreateEvent(slot: TimeSlot) {
  if (!selectedDate.value) return
  newEvent.value.date = selectedDate.value
  newEvent.value.slot = slot
  newEvent.value.event_type = 'scrim'
  newEvent.value.title = ''
  showCreateEvent.value = true
}

// Navigation
function previousMonth() {
  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

function nextMonth() {
  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

// Data loading
async function loadMonthData() {
  loading.value = true
  try {
    const [eventsRes, availRes, seriesRes] = await Promise.all([
      calendarApi.getEvents(currentYear.value, currentMonth.value),
      calendarApi.getMonthAvailabilities(currentYear.value, currentMonth.value),
      draftSeriesApi.listWithGames(0, 200),
    ])
    events.value = eventsRes.data
    monthAvailabilities.value = availRes.data
    // Create map of draft series by ID for quick lookup
    draftSeriesMap.value = new Map(seriesRes.data.map(s => [s.id, s]))
  } catch (error) {
    console.error('Failed to load calendar data:', error)
  } finally {
    loading.value = false
  }
}

async function selectDay(day: CalendarDay) {
  if (!day.isCurrentMonth) return
  selectedDate.value = day.date
  try {
    const res = await calendarApi.getDayDetail(day.date)
    selectedDayDetail.value = res.data
  } catch (error) {
    console.error('Failed to load day detail:', error)
  }
}

function openEvent(event: CalendarEvent) {
  selectedEvent.value = event
}

function goToScrimDetail() {
  if (!selectedEvent.value) return
  router.push({
    path: '/scrims',
    query: { event_id: selectedEvent.value.id.toString() }
  })
}

async function createEvent() {
  creatingEvent.value = true
  try {
    const eventData = {
      title: newEvent.value.title,
      event_type: newEvent.value.event_type,
      date: newEvent.value.date,
      slot: newEvent.value.slot,
      opponent_name: newEvent.value.opponent_name || undefined,
      opponent_players: newEvent.value.opponent_players || undefined,
      description: newEvent.value.description || undefined,
      location: newEvent.value.location || undefined,
    }
    await calendarApi.createEvent(eventData)
    showCreateEvent.value = false
    // Reset form
    newEvent.value = {
      title: '',
      event_type: 'scrim',
      date: new Date().toISOString().split('T')[0],
      slot: 'evening',
      opponent_name: '',
      opponent_players: '',
      description: '',
      location: '',
    }
    await loadMonthData()
    // Refresh selected day if it matches
    if (selectedDate.value === eventData.date) {
      const res = await calendarApi.getDayDetail(selectedDate.value)
      selectedDayDetail.value = res.data
    }
  } catch (error) {
    console.error('Failed to create event:', error)
    alert('Erreur lors de la creation de l\'evenement')
  } finally {
    creatingEvent.value = false
  }
}

async function deleteEventConfirm() {
  if (!selectedEvent.value) return
  if (!confirm('Supprimer cet evenement ?')) return

  try {
    await calendarApi.deleteEvent(selectedEvent.value.id)
    selectedEvent.value = null
    await loadMonthData()
    // Refresh selected day
    if (selectedDate.value) {
      const res = await calendarApi.getDayDetail(selectedDate.value)
      selectedDayDetail.value = res.data
    }
  } catch (error) {
    console.error('Failed to delete event:', error)
    alert('Erreur lors de la suppression')
  }
}

// Player availability functions
function getMyAvailability(slot: TimeSlot): boolean {
  if (!selectedDayDetail.value || !currentPlayerId.value) return false
  const myAvail = selectedDayDetail.value.availabilities.find(
    (a) => a.player_id === currentPlayerId.value
  )
  if (!myAvail) return false
  return myAvail[slot] ?? false
}

async function toggleMyAvailability(slot: TimeSlot) {
  if (!selectedDate.value || !currentPlayerId.value) return

  savingAvailability.value = true
  const currentValue = getMyAvailability(slot)

  try {
    await calendarApi.setPlayerAvailability(currentPlayerId.value, {
      date: selectedDate.value,
      slot: slot,
      is_available: !currentValue,
    })

    // Refresh day detail
    const res = await calendarApi.getDayDetail(selectedDate.value)
    selectedDayDetail.value = res.data

    // Also refresh month availabilities for the calendar dots
    await loadMonthData()
  } catch (error) {
    console.error('Failed to update availability:', error)
    alert('Erreur lors de la mise a jour de la disponibilite')
  } finally {
    savingAvailability.value = false
  }
}

// ================== PLANNING TAB LOGIC ==================

// Week calculation
const weekStart = computed(() => {
  const today = new Date()
  const dayOfWeek = today.getDay()
  const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek // Monday start
  const monday = new Date(today)
  monday.setDate(today.getDate() + diff + weekOffset.value * 7)
  monday.setHours(0, 0, 0, 0)
  return monday
})

const weekEnd = computed(() => {
  const end = new Date(weekStart.value)
  end.setDate(end.getDate() + 6)
  return end
})

const weekRangeLabel = computed(() => {
  const start = weekStart.value
  const end = weekEnd.value
  const formatOptions: Intl.DateTimeFormatOptions = { day: 'numeric', month: 'short' }
  return `${start.toLocaleDateString('fr-FR', formatOptions)} - ${end.toLocaleDateString('fr-FR', formatOptions)}`
})

interface WeekDay {
  date: string
  dayName: string
  dateLabel: string
  isToday: boolean
  isPast: boolean
}

const weekDays = computed((): WeekDay[] => {
  const days: WeekDay[] = []
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const dayNames = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

  for (let i = 0; i < 7; i++) {
    const date = new Date(weekStart.value)
    date.setDate(date.getDate() + i)

    days.push({
      date: formatDateISO(date),
      dayName: dayNames[i],
      dateLabel: date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' }),
      isToday: date.getTime() === today.getTime(),
      isPast: date < today,
    })
  }

  return days
})

// Full team slots
const fullTeamSlots = computed(() => {
  const slots: Array<{ date: string; slot: TimeSlot }> = []
  const total = players.value.length

  if (total < 5) return slots

  for (const day of weekDays.value) {
    if (day.isPast) continue

    const dayAvail = planningAvailabilities.value.find((a) => a.date === day.date)
    if (!dayAvail) continue

    for (const slot of ['morning', 'afternoon', 'evening'] as TimeSlot[]) {
      const count = dayAvail.availabilities.filter((a) => a[slot]).length
      if (count === total) {
        slots.push({ date: day.date, slot })
      }
    }
  }

  return slots
})

// Planning helpers
function formatSlotDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric', month: 'short' })
}

function getPlanningSlotLabel(slot: TimeSlot): string {
  const labels: Record<TimeSlot, string> = {
    morning: 'Matin',
    afternoon: 'Apres-midi',
    evening: 'Soir',
  }
  return labels[slot]
}

function getPlanningAvailability(dateStr: string, slot: TimeSlot): boolean {
  const dayAvail = planningAvailabilities.value.find((a) => a.date === dateStr)
  if (!dayAvail) return false

  const myAvail = dayAvail.availabilities.find((a) => a.player_id === currentPlayerId.value)
  if (!myAvail) return false

  return myAvail[slot] ?? false
}

function getPlanningSlotStatus(dateStr: string, slot: TimeSlot): { count: number; class: string; names: string } {
  const dayAvail = planningAvailabilities.value.find((a) => a.date === dateStr)
  if (!dayAvail) return { count: 0, class: 'bg-gray-600', names: '-' }

  const available = dayAvail.availabilities.filter((a) => a[slot])
  const count = available.length
  const total = players.value.length

  let colorClass = 'bg-red-600 text-white'
  if (count === total && total >= 5) {
    colorClass = 'bg-green-600 text-white'
  } else if (count >= total / 2) {
    colorClass = 'bg-yellow-600 text-black'
  }

  const names = available.map((a) => a.player_name.split(' ')[0]).join(', ') || '-'

  return { count, class: colorClass, names }
}

// Planning navigation
function previousWeek() {
  weekOffset.value--
}

function nextWeek() {
  weekOffset.value++
}

function goToCurrentWeek() {
  weekOffset.value = 0
}

// Planning data loading
async function loadPlanningData() {
  loadingPlanning.value = true
  try {
    // Load players
    const playersRes = await playersApi.getPlayers()
    players.value = playersRes.data

    // Load availabilities for the week
    await loadWeekAvailabilities()
  } catch (error) {
    console.error('Failed to load planning data:', error)
  } finally {
    loadingPlanning.value = false
  }
}

async function loadWeekAvailabilities() {
  const promises = weekDays.value.map((day) =>
    calendarApi.getDayAvailabilities(day.date).catch(() => ({ data: { date: day.date, availabilities: [] } }))
  )
  const results = await Promise.all(promises)
  planningAvailabilities.value = results.map((r) => r.data)
}

async function togglePlanningAvailability(dateStr: string, slot: TimeSlot) {
  if (!currentPlayerId.value) return

  savingPlanningSlot.value = `${dateStr}-${slot}`
  const currentValue = getPlanningAvailability(dateStr, slot)

  try {
    await calendarApi.setPlayerAvailability(currentPlayerId.value, {
      date: dateStr,
      slot: slot,
      is_available: !currentValue,
    })

    // Refresh availabilities
    await loadWeekAvailabilities()
  } catch (error) {
    console.error('Failed to update availability:', error)
    alert('Erreur lors de la mise a jour')
  } finally {
    savingPlanningSlot.value = null
  }
}

function quickCreateEventFromPlanning(date: string, slot: TimeSlot) {
  newEvent.value.date = date
  newEvent.value.slot = slot
  newEvent.value.event_type = 'scrim'
  newEvent.value.title = ''
  showCreateEvent.value = true
}

// Lifecycle
onMounted(() => {
  // Check if tab query param is set
  if (route.query.tab === 'planning') {
    activeTab.value = 'planning'
  }
  loadChampionData() // Load champion names for display
  loadMonthData()
  loadPlanningData()
})
watch([currentYear, currentMonth], loadMonthData)
watch(weekOffset, loadWeekAvailabilities)
watch(activeTab, (tab) => {
  if (tab === 'planning' && players.value.length === 0) {
    loadPlanningData()
  }
})
</script>
