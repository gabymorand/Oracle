<template>
  <div class="min-h-screen bg-gray-900">
    <AppNavbar :show-back-button="true" />

    <div class="max-w-7xl mx-auto px-4 py-8">
      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold mb-2">Mes Disponibilites</h1>
        <p class="text-gray-400">
          Coche les creneaux ou tu es disponible pour les prochains jours
        </p>
      </div>

      <!-- Player selector (for coaches viewing player availabilities) -->
      <div v-if="!isPlayer" class="mb-6 flex items-center gap-4">
        <label class="text-gray-400">Voir les dispos de:</label>
        <select
          v-model="viewingPlayerId"
          class="bg-gray-700 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
        >
          <option :value="null">Tous les joueurs</option>
          <option v-for="player in players" :key="player.id" :value="player.id">
            {{ player.summoner_name }} ({{ player.role.toUpperCase() }})
          </option>
        </select>
      </div>

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
      <div v-if="loading" class="text-center py-12 text-gray-400">
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
                  @click="toggleAvailability(day.date, 'morning')"
                  :disabled="day.isPast || savingSlot === `${day.date}-morning`"
                  :class="[
                    'w-16 h-10 rounded-lg font-medium transition',
                    getMyAvailability(day.date, 'morning')
                      ? 'bg-green-600 hover:bg-green-700 text-white'
                      : 'bg-gray-600 hover:bg-gray-500 text-gray-300',
                    day.isPast ? 'cursor-not-allowed opacity-50' : 'cursor-pointer',
                  ]"
                >
                  {{ savingSlot === `${day.date}-morning` ? '...' : (getMyAvailability(day.date, 'morning') ? 'Oui' : 'Non') }}
                </button>
              </td>
              <td class="py-4 px-4 text-center">
                <button
                  @click="toggleAvailability(day.date, 'afternoon')"
                  :disabled="day.isPast || savingSlot === `${day.date}-afternoon`"
                  :class="[
                    'w-16 h-10 rounded-lg font-medium transition',
                    getMyAvailability(day.date, 'afternoon')
                      ? 'bg-green-600 hover:bg-green-700 text-white'
                      : 'bg-gray-600 hover:bg-gray-500 text-gray-300',
                    day.isPast ? 'cursor-not-allowed opacity-50' : 'cursor-pointer',
                  ]"
                >
                  {{ savingSlot === `${day.date}-afternoon` ? '...' : (getMyAvailability(day.date, 'afternoon') ? 'Oui' : 'Non') }}
                </button>
              </td>
              <td class="py-4 px-4 text-center">
                <button
                  @click="toggleAvailability(day.date, 'evening')"
                  :disabled="day.isPast || savingSlot === `${day.date}-evening`"
                  :class="[
                    'w-16 h-10 rounded-lg font-medium transition',
                    getMyAvailability(day.date, 'evening')
                      ? 'bg-green-600 hover:bg-green-700 text-white'
                      : 'bg-gray-600 hover:bg-gray-500 text-gray-300',
                    day.isPast ? 'cursor-not-allowed opacity-50' : 'cursor-pointer',
                  ]"
                >
                  {{ savingSlot === `${day.date}-evening` ? '...' : (getMyAvailability(day.date, 'evening') ? 'Oui' : 'Non') }}
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
                      getSlotStatus(day.date, 'morning').class,
                    ]"
                  >
                    {{ getSlotStatus(day.date, 'morning').count }}/{{ players.length }}
                  </div>
                  <div class="text-xs text-gray-400">
                    {{ getSlotStatus(day.date, 'morning').names }}
                  </div>
                </div>
              </td>
              <td class="py-4 px-4">
                <div class="flex flex-col items-center gap-1">
                  <div
                    :class="[
                      'text-lg font-bold px-3 py-1 rounded',
                      getSlotStatus(day.date, 'afternoon').class,
                    ]"
                  >
                    {{ getSlotStatus(day.date, 'afternoon').count }}/{{ players.length }}
                  </div>
                  <div class="text-xs text-gray-400">
                    {{ getSlotStatus(day.date, 'afternoon').names }}
                  </div>
                </div>
              </td>
              <td class="py-4 px-4">
                <div class="flex flex-col items-center gap-1">
                  <div
                    :class="[
                      'text-lg font-bold px-3 py-1 rounded',
                      getSlotStatus(day.date, 'evening').class,
                    ]"
                  >
                    {{ getSlotStatus(day.date, 'evening').count }}/{{ players.length }}
                  </div>
                  <div class="text-xs text-gray-400">
                    {{ getSlotStatus(day.date, 'evening').names }}
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
          <RouterLink
            v-for="slot in fullTeamSlots"
            :key="`${slot.date}-${slot.slot}`"
            :to="`/calendar?date=${slot.date}&slot=${slot.slot}`"
            class="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 px-3 py-2 rounded-lg text-sm font-medium transition"
          >
            <span>{{ formatSlotDate(slot.date) }} - {{ getSlotLabel(slot.slot) }}</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { RouterLink } from 'vue-router'
import AppNavbar from '@/components/AppNavbar.vue'
import { useAuthStore } from '@/stores/auth'
import { calendarApi, playersApi } from '@/api'
import type { Player, DayAvailabilitySummary, TimeSlot } from '@/types'

const authStore = useAuthStore()

// Player identification
const isPlayer = computed(() => authStore.userRole === 'player')
const currentPlayerId = computed(() => {
  const id = sessionStorage.getItem('selected_player_id')
  return id ? parseInt(id, 10) : null
})

// State
const players = ref<Player[]>([])
const viewingPlayerId = ref<number | null>(null)
const weekOffset = ref(0) // 0 = current week, 1 = next week, -1 = previous week
const availabilities = ref<DayAvailabilitySummary[]>([])
const loading = ref(true)
const savingSlot = ref<string | null>(null)

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

    const dayAvail = availabilities.value.find((a) => a.date === day.date)
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

// Helpers
function formatDateISO(date: Date): string {
  return date.toISOString().split('T')[0]
}

function formatSlotDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric', month: 'short' })
}

function getSlotLabel(slot: TimeSlot): string {
  const labels: Record<TimeSlot, string> = {
    morning: 'Matin',
    afternoon: 'Apres-midi',
    evening: 'Soir',
  }
  return labels[slot]
}

function getMyAvailability(dateStr: string, slot: TimeSlot): boolean {
  const dayAvail = availabilities.value.find((a) => a.date === dateStr)
  if (!dayAvail) return false

  const myAvail = dayAvail.availabilities.find((a) => a.player_id === currentPlayerId.value)
  if (!myAvail) return false

  return myAvail[slot] ?? false
}

function getSlotStatus(dateStr: string, slot: TimeSlot): { count: number; class: string; names: string } {
  const dayAvail = availabilities.value.find((a) => a.date === dateStr)
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

// Navigation
function previousWeek() {
  weekOffset.value--
}

function nextWeek() {
  weekOffset.value++
}

function goToCurrentWeek() {
  weekOffset.value = 0
}

// Data loading
async function loadData() {
  loading.value = true
  try {
    // Load players
    const playersRes = await playersApi.getPlayers()
    players.value = playersRes.data

    // Load availabilities for the week
    await loadWeekAvailabilities()
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

async function loadWeekAvailabilities() {
  const promises = weekDays.value.map((day) =>
    calendarApi.getDayAvailabilities(day.date).catch(() => ({ data: { date: day.date, availabilities: [] } }))
  )
  const results = await Promise.all(promises)
  availabilities.value = results.map((r) => r.data)
}

async function toggleAvailability(dateStr: string, slot: TimeSlot) {
  if (!currentPlayerId.value) return

  savingSlot.value = `${dateStr}-${slot}`
  const currentValue = getMyAvailability(dateStr, slot)

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
    savingSlot.value = null
  }
}

// Lifecycle
onMounted(loadData)
watch(weekOffset, loadWeekAvailabilities)
</script>
