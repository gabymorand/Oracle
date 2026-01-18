<template>
  <div class="bg-gray-800 rounded-lg p-6">
    <h3 class="text-xl font-bold mb-4">Rank Evolution</h3>
    <div v-if="loading" class="text-center py-8">
      <p class="text-gray-400">Loading rank history...</p>
    </div>
    <div v-else-if="rankHistory.length === 0" class="text-center py-8">
      <p class="text-gray-400">No rank history available yet. Rank history will be tracked after the next refresh.</p>
    </div>
    <div v-else class="h-80">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import axios from 'axios'
import { apiClient } from '@/api/client'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps<{
  riotAccountId: number
}>()

interface RankHistoryEntry {
  id: number
  tier: string
  division: string
  lp: number
  wins: number
  losses: number
  recorded_at: string
}

const rankHistory = ref<RankHistoryEntry[]>([])
const loading = ref(true)

const tierValues: Record<string, number> = {
  IRON: 0,
  BRONZE: 1,
  SILVER: 2,
  GOLD: 3,
  PLATINUM: 4,
  EMERALD: 5,
  DIAMOND: 6,
  MASTER: 7,
  GRANDMASTER: 8,
  CHALLENGER: 9
}

const divisionValues: Record<string, number> = {
  IV: 0,
  III: 1,
  II: 2,
  I: 3
}

function rankToValue(tier: string, division: string, lp: number): number {
  const base = tierValues[tier] * 400
  if (['MASTER', 'GRANDMASTER', 'CHALLENGER'].includes(tier)) {
    return base + lp
  }
  return base + divisionValues[division] * 100 + lp
}

function valueToRankLabel(value: number): string {
  const tier = Math.floor(value / 400)
  const tierName = Object.keys(tierValues).find(key => tierValues[key] === tier) || 'IRON'

  if (['MASTER', 'GRANDMASTER', 'CHALLENGER'].includes(tierName)) {
    const lp = value % 400
    return `${tierName} ${lp} LP`
  }

  const remainder = value % 400
  const division = Math.floor(remainder / 100)
  const divisionName = Object.keys(divisionValues).find(key => divisionValues[key] === division) || 'IV'
  const lp = remainder % 100

  return `${tierName} ${divisionName} (${lp} LP)`
}

const chartData = computed(() => {
  if (rankHistory.value.length === 0) {
    return {
      labels: [],
      datasets: []
    }
  }

  const labels = rankHistory.value.map(entry => {
    const date = new Date(entry.recorded_at)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  })

  const dataPoints = rankHistory.value.map(entry =>
    rankToValue(entry.tier, entry.division, entry.lp)
  )

  return {
    labels,
    datasets: [
      {
        label: 'Rank',
        data: dataPoints,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6
      }
    ]
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: (context: any) => {
          const value = context.parsed.y
          return valueToRankLabel(value)
        }
      }
    }
  },
  scales: {
    y: {
      ticks: {
        callback: (value: any) => valueToRankLabel(value),
        color: 'rgb(156, 163, 175)'
      },
      grid: {
        color: 'rgba(75, 85, 99, 0.3)'
      }
    },
    x: {
      ticks: {
        color: 'rgb(156, 163, 175)'
      },
      grid: {
        color: 'rgba(75, 85, 99, 0.3)'
      }
    }
  }
}))

async function loadRankHistory() {
  try {
    loading.value = true
    const response = await apiClient.get(`/api/v1/stats/rank-history/${props.riotAccountId}`)
    rankHistory.value = response.data
  } catch (error) {
    console.error('Failed to load rank history:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadRankHistory()
})
</script>
