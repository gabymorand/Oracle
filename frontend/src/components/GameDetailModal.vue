<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { gamesApi } from '@/api'
import type { MatchDetailResponse, MatchParticipant } from '@/types'
import { getChampionIcon, getChampionName, getSummonerSpellIcon, getItemIcon, getRankEmblemIcon } from '@/utils/champions'

interface Props {
  gameId: number | null
  externalMatchData?: MatchDetailResponse | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

const loading = ref(false)
const error = ref<string | null>(null)
const matchData = ref<MatchDetailResponse | null>(null)

// Load match data when gameId changes or external data is provided
watch(
  () => [props.gameId, props.externalMatchData] as const,
  async ([newGameId, newExternalData]) => {
    // If external data is provided, use it directly
    if (newExternalData) {
      matchData.value = newExternalData
      loading.value = false
      error.value = null
      return
    }

    if (!newGameId) {
      matchData.value = null
      return
    }

    loading.value = true
    error.value = null

    try {
      const response = await gamesApi.getMatchDetails(newGameId)
      matchData.value = response.data
    } catch (e) {
      console.error('Failed to load match details:', e)
      error.value = 'Impossible de charger les details du match'
    } finally {
      loading.value = false
    }
  },
  { immediate: true }
)

// Formatted game date
const formattedDate = computed(() => {
  if (!matchData.value) return ''
  const date = new Date(matchData.value.game_date)
  return date.toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
})

// Get max damage in the match for percentage bars
const maxDamage = computed(() => {
  if (!matchData.value) return 1
  const allParticipants = [
    ...matchData.value.blue_team.participants,
    ...matchData.value.red_team.participants,
  ]
  return Math.max(...allParticipants.map((p) => p.damage_dealt), 1)
})

// Format KDA string
function formatKda(p: MatchParticipant): string {
  return `${p.kills}/${p.deaths}/${p.assists}`
}

// Get KDA color
function getKdaColor(kda: number): string {
  if (kda >= 5) return 'text-yellow-400'
  if (kda >= 3) return 'text-green-400'
  if (kda >= 2) return 'text-gray-300'
  return 'text-red-400'
}

// Get damage percentage for bar width
function getDamagePercent(damage: number): number {
  return (damage / maxDamage.value) * 100
}

// Format gold amount
function formatGold(gold: number): string {
  if (gold >= 1000) {
    return `${(gold / 1000).toFixed(1)}k`
  }
  return gold.toString()
}

// Close modal when clicking outside
function handleBackdropClick(e: MouseEvent) {
  if (e.target === e.currentTarget) {
    emit('close')
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="gameId !== null || externalMatchData"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-[70] p-4"
      @click="handleBackdropClick"
    >
      <div class="bg-gray-800 rounded-lg shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="flex items-center justify-between p-4 border-b border-gray-700">
          <div class="flex items-center gap-4">
            <h2 class="text-xl font-bold">Details du Match</h2>
            <span v-if="matchData" class="text-gray-400">
              {{ matchData.game_duration_formatted }} - {{ formattedDate }}
            </span>
          </div>
          <button
            @click="emit('close')"
            class="text-gray-400 hover:text-white transition p-1"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="flex items-center justify-center py-20">
          <div class="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
        </div>

        <!-- Error -->
        <div v-else-if="error" class="text-center py-20 text-red-400">
          {{ error }}
        </div>

        <!-- Match Content -->
        <div v-else-if="matchData" class="p-4 space-y-4">
          <!-- Blue Team -->
          <div class="rounded-lg overflow-hidden">
            <div class="flex items-center gap-2 px-4 py-2 bg-blue-900/30 border-l-4 border-blue-500">
              <span class="font-bold">EQUIPE BLEUE</span>
              <span
                v-if="matchData.blue_team.win"
                class="px-2 py-0.5 rounded text-xs font-bold bg-green-500/20 text-green-400"
              >
                VICTOIRE
              </span>
              <span
                v-else
                class="px-2 py-0.5 rounded text-xs font-bold bg-red-500/20 text-red-400"
              >
                DEFAITE
              </span>
            </div>

            <div class="bg-gray-900/50">
              <div
                v-for="participant in matchData.blue_team.participants"
                :key="participant.puuid"
                class="flex items-center gap-3 px-4 py-2 border-b border-gray-700/50 last:border-b-0"
                :class="{ 'bg-blue-500/10': participant.is_our_player }"
              >
                <!-- Rank Emblem (for our players) -->
                <div class="w-6 flex items-center justify-center">
                  <img
                    v-if="participant.rank_tier"
                    :src="getRankEmblemIcon(participant.rank_tier)"
                    :alt="participant.rank_tier"
                    class="w-6 h-6"
                    :title="`${participant.rank_tier} ${participant.rank_division || ''} ${participant.rank_lp || 0} LP`"
                  />
                </div>

                <!-- Champion + Spells -->
                <div class="flex items-center gap-1">
                  <img
                    :src="getChampionIcon(participant.champion_id)"
                    :alt="getChampionName(participant.champion_id)"
                    class="w-10 h-10 rounded"
                  />
                  <div class="flex flex-col gap-0.5">
                    <img
                      :src="getSummonerSpellIcon(participant.summoner_spell1)"
                      class="w-4 h-4 rounded"
                    />
                    <img
                      :src="getSummonerSpellIcon(participant.summoner_spell2)"
                      class="w-4 h-4 rounded"
                    />
                  </div>
                </div>

                <!-- Name -->
                <div class="w-32 truncate">
                  <span
                    class="font-medium"
                    :class="participant.is_our_player ? 'text-blue-400' : 'text-white'"
                  >
                    {{ participant.summoner_name }}
                  </span>
                  <span v-if="participant.tag_line" class="text-gray-500 text-xs">
                    #{{ participant.tag_line }}
                  </span>
                </div>

                <!-- KDA -->
                <div class="w-24 text-center">
                  <div class="font-bold" :class="getKdaColor(participant.kda)">
                    {{ formatKda(participant) }}
                  </div>
                  <div class="text-xs text-gray-400">
                    {{ participant.kda.toFixed(2) }} KDA
                    <span class="mx-1">-</span>
                    {{ participant.vision_score }} VS
                  </div>
                </div>

                <!-- CS -->
                <div class="w-16 text-center">
                  <div class="font-medium">{{ participant.cs }} CS</div>
                  <div class="text-xs text-gray-400">{{ participant.cs_per_min }}/m</div>
                </div>

                <!-- Items -->
                <div class="flex gap-0.5">
                  <template v-for="(itemId, idx) in participant.items.slice(0, 6)" :key="idx">
                    <div
                      class="w-7 h-7 rounded bg-gray-700"
                      :class="{ 'ring-1 ring-yellow-500': idx === 5 && itemId > 0 }"
                    >
                      <img
                        v-if="itemId > 0"
                        :src="getItemIcon(itemId)"
                        class="w-full h-full rounded"
                      />
                    </div>
                  </template>
                  <!-- Trinket -->
                  <div class="w-7 h-7 rounded bg-gray-700 ring-1 ring-gray-600">
                    <img
                      v-if="participant.items[6] > 0"
                      :src="getItemIcon(participant.items[6])"
                      class="w-full h-full rounded"
                    />
                  </div>
                </div>

                <!-- Damage Bar -->
                <div class="flex-1 flex items-center gap-2">
                  <div class="flex-1 h-4 bg-gray-700 rounded overflow-hidden">
                    <div
                      class="h-full bg-red-500"
                      :style="{ width: getDamagePercent(participant.damage_dealt) + '%' }"
                    ></div>
                  </div>
                  <span class="text-sm text-gray-300 w-24 text-right">
                    {{ formatGold(participant.damage_dealt) }}
                    <span class="text-gray-500">({{ Math.round(participant.damage_dealt / matchData.blue_team.total_damage * 100) }}%)</span>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Red Team -->
          <div class="rounded-lg overflow-hidden">
            <div class="flex items-center gap-2 px-4 py-2 bg-red-900/30 border-l-4 border-red-500">
              <span class="font-bold">EQUIPE ROUGE</span>
              <span
                v-if="matchData.red_team.win"
                class="px-2 py-0.5 rounded text-xs font-bold bg-green-500/20 text-green-400"
              >
                VICTOIRE
              </span>
              <span
                v-else
                class="px-2 py-0.5 rounded text-xs font-bold bg-red-500/20 text-red-400"
              >
                DEFAITE
              </span>
            </div>

            <div class="bg-gray-900/50">
              <div
                v-for="participant in matchData.red_team.participants"
                :key="participant.puuid"
                class="flex items-center gap-3 px-4 py-2 border-b border-gray-700/50 last:border-b-0"
                :class="{ 'bg-red-500/10': participant.is_our_player }"
              >
                <!-- Rank Emblem (for our players) -->
                <div class="w-6 flex items-center justify-center">
                  <img
                    v-if="participant.rank_tier"
                    :src="getRankEmblemIcon(participant.rank_tier)"
                    :alt="participant.rank_tier"
                    class="w-6 h-6"
                    :title="`${participant.rank_tier} ${participant.rank_division || ''} ${participant.rank_lp || 0} LP`"
                  />
                </div>

                <!-- Champion + Spells -->
                <div class="flex items-center gap-1">
                  <img
                    :src="getChampionIcon(participant.champion_id)"
                    :alt="getChampionName(participant.champion_id)"
                    class="w-10 h-10 rounded"
                  />
                  <div class="flex flex-col gap-0.5">
                    <img
                      :src="getSummonerSpellIcon(participant.summoner_spell1)"
                      class="w-4 h-4 rounded"
                    />
                    <img
                      :src="getSummonerSpellIcon(participant.summoner_spell2)"
                      class="w-4 h-4 rounded"
                    />
                  </div>
                </div>

                <!-- Name -->
                <div class="w-32 truncate">
                  <span
                    class="font-medium"
                    :class="participant.is_our_player ? 'text-blue-400' : 'text-white'"
                  >
                    {{ participant.summoner_name }}
                  </span>
                  <span v-if="participant.tag_line" class="text-gray-500 text-xs">
                    #{{ participant.tag_line }}
                  </span>
                </div>

                <!-- KDA -->
                <div class="w-24 text-center">
                  <div class="font-bold" :class="getKdaColor(participant.kda)">
                    {{ formatKda(participant) }}
                  </div>
                  <div class="text-xs text-gray-400">
                    {{ participant.kda.toFixed(2) }} KDA
                    <span class="mx-1">-</span>
                    {{ participant.vision_score }} VS
                  </div>
                </div>

                <!-- CS -->
                <div class="w-16 text-center">
                  <div class="font-medium">{{ participant.cs }} CS</div>
                  <div class="text-xs text-gray-400">{{ participant.cs_per_min }}/m</div>
                </div>

                <!-- Items -->
                <div class="flex gap-0.5">
                  <template v-for="(itemId, idx) in participant.items.slice(0, 6)" :key="idx">
                    <div
                      class="w-7 h-7 rounded bg-gray-700"
                      :class="{ 'ring-1 ring-yellow-500': idx === 5 && itemId > 0 }"
                    >
                      <img
                        v-if="itemId > 0"
                        :src="getItemIcon(itemId)"
                        class="w-full h-full rounded"
                      />
                    </div>
                  </template>
                  <!-- Trinket -->
                  <div class="w-7 h-7 rounded bg-gray-700 ring-1 ring-gray-600">
                    <img
                      v-if="participant.items[6] > 0"
                      :src="getItemIcon(participant.items[6])"
                      class="w-full h-full rounded"
                    />
                  </div>
                </div>

                <!-- Damage Bar -->
                <div class="flex-1 flex items-center gap-2">
                  <div class="flex-1 h-4 bg-gray-700 rounded overflow-hidden">
                    <div
                      class="h-full bg-red-500"
                      :style="{ width: getDamagePercent(participant.damage_dealt) + '%' }"
                    ></div>
                  </div>
                  <span class="text-sm text-gray-300 w-24 text-right">
                    {{ formatGold(participant.damage_dealt) }}
                    <span class="text-gray-500">({{ Math.round(participant.damage_dealt / matchData.red_team.total_damage * 100) }}%)</span>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
