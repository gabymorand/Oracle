<template>
  <nav class="bg-gray-800 border-b border-gray-700">
    <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
      <div class="flex items-center gap-6">
        <router-link to="/dashboard">
          <AppLogo size="sm" />
        </router-link>
        <div v-if="showBackButton" class="flex items-center gap-4">
          <span class="text-gray-500">|</span>
          <button @click="router.back()" class="text-blue-400 hover:underline">
            ← Back
          </button>
        </div>
      </div>
      <div class="flex items-center gap-4">
        <!-- Players Dropdown -->
        <div class="relative" ref="dropdownRef">
          <button
            @click="togglePlayersDropdown"
            class="flex items-center gap-2 text-gray-300 hover:text-white text-sm transition px-3 py-2 rounded hover:bg-gray-700"
          >
            <span>Players</span>
            <svg
              class="w-4 h-4 transition-transform"
              :class="{ 'rotate-180': showPlayersDropdown }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          <div
            v-if="showPlayersDropdown"
            class="absolute top-full left-0 mt-1 w-56 bg-gray-700 rounded-lg shadow-lg py-2 z-50"
          >
            <div v-if="loadingPlayers" class="px-4 py-2 text-gray-400 text-sm">
              Loading...
            </div>
            <template v-else>
              <router-link
                v-for="player in players"
                :key="player.id"
                :to="`/players/${player.id}`"
                class="flex items-center gap-3 px-4 py-2 hover:bg-gray-600 transition"
                @click="showPlayersDropdown = false"
              >
                <span
                  class="w-2 h-2 rounded-full"
                  :class="getRoleColor(player.role)"
                ></span>
                <span class="text-sm">{{ player.summoner_name }}</span>
                <span class="text-xs text-gray-400 uppercase">{{ player.role }}</span>
              </router-link>
              <div v-if="players.length === 0" class="px-4 py-2 text-gray-400 text-sm">
                No players found
              </div>
            </template>
          </div>
        </div>

        <!-- Drafts Link -->
        <router-link
          to="/drafts"
          class="text-gray-300 hover:text-white text-sm transition px-3 py-2 rounded hover:bg-gray-700"
        >
          Drafts
        </router-link>

        <!-- Calendar Link -->
        <router-link
          to="/calendar"
          class="text-gray-300 hover:text-white text-sm transition px-3 py-2 rounded hover:bg-gray-700"
        >
          Calendrier
        </router-link>

        <!-- Scrims Link -->
        <router-link
          to="/scrims"
          class="text-gray-300 hover:text-white text-sm transition px-3 py-2 rounded hover:bg-gray-700"
        >
          Scrims
        </router-link>

        <!-- Tier List Link -->
        <router-link
          to="/tier-list"
          class="text-gray-300 hover:text-white text-sm transition px-3 py-2 rounded hover:bg-gray-700"
        >
          Tier List
        </router-link>

        <!-- Analytics Link -->
        <router-link
          to="/analytics"
          class="text-gray-300 hover:text-white text-sm transition px-3 py-2 rounded hover:bg-gray-700"
        >
          Analytics
        </router-link>

        <router-link
          to="/sponsors"
          class="text-blue-400 hover:text-blue-300 text-sm transition"
        >
          Team Highlights
        </router-link>
        <span class="text-gray-400 text-sm">{{ authStore.userRole }}</span>
        <button
          @click="handleLogout"
          class="bg-red-600 hover:bg-red-700 px-4 py-2 rounded transition text-sm"
        >
          Logout
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { playersApi } from '@/api'
import AppLogo from './AppLogo.vue'
import type { Player } from '@/types'

interface Props {
  showBackButton?: boolean
}

withDefaults(defineProps<Props>(), {
  showBackButton: false,
})

const router = useRouter()
const authStore = useAuthStore()

const showPlayersDropdown = ref(false)
const loadingPlayers = ref(false)
const players = ref<Player[]>([])
const dropdownRef = ref<HTMLElement | null>(null)

function togglePlayersDropdown() {
  showPlayersDropdown.value = !showPlayersDropdown.value
  if (showPlayersDropdown.value && players.value.length === 0) {
    loadPlayers()
  }
}

async function loadPlayers() {
  try {
    loadingPlayers.value = true
    const response = await playersApi.getPlayers()
    players.value = response.data
  } catch (error) {
    console.error('Failed to load players:', error)
  } finally {
    loadingPlayers.value = false
  }
}

function getRoleColor(role: string): string {
  const colors: Record<string, string> = {
    top: 'bg-red-400',
    jungle: 'bg-green-400',
    mid: 'bg-blue-400',
    adc: 'bg-yellow-400',
    support: 'bg-purple-400'
  }
  return colors[role.toLowerCase()] || 'bg-gray-400'
}

function handleClickOutside(event: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    showPlayersDropdown.value = false
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/')
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
