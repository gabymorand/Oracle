<template>
  <div class="bg-gray-800 rounded-lg p-6">
    <h3 class="text-xl font-bold mb-4">Performance Over Time (Last 50 Games)</h3>
    <div v-if="loading" class="text-center py-8">
      <p class="text-gray-400">Loading game stats...</p>
    </div>
    <div v-else-if="games.length === 0" class="text-center py-8">
      <p class="text-gray-400">No games found. Refresh stats to load recent games.</p>
    </div>
    <div v-else>
      <!-- Stat Selection -->
      <div class="flex gap-2 mb-4">
        <button
          v-for="stat in availableStats"
          :key="stat.key"
          @click="selectedStat = stat.key"
          :class="[
            'px-4 py-2 rounded transition',
            selectedStat === stat.key
              ? 'bg-blue-600 hover:bg-blue-700'
              : 'bg-gray-700 hover:bg-gray-600'
          ]"
        >
          {{ stat.label }}
        </button>
      </div>

      <!-- Chart -->
      <div class="h-80">
        <Line :data="chartData" :options="chartOptions" />
      </div>
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

interface Game {
  id: number
  match_id: string
  champion_id: number
  role: string
  stats: {
    kda: number
    cs_per_min: number
    vision_per_min: number
    gold_per_min: number
    kp: number
    win: boolean
  }
  game_date: string
}

const games = ref<Game[]>([])
const loading = ref(true)
const selectedStat = ref<string>('kda')

const availableStats = [
  { key: 'kda', label: 'KDA', color: 'rgb(59, 130, 246)' },
  { key: 'winrate', label: 'Winrate', color: 'rgb(34, 197, 94)' },
  { key: 'cs_per_min', label: 'CS/min', color: 'rgb(249, 115, 22)' },
  { key: 'vision_per_min', label: 'Vision/min', color: 'rgb(168, 85, 247)' },
  { key: 'kp', label: 'KP%', color: 'rgb(236, 72, 153)' }
]

function calculateMovingAverage(data: number[], windowSize: number = 5): number[] {
  const result: number[] = []
  for (let i = 0; i < data.length; i++) {
    const start = Math.max(0, i - windowSize + 1)
    const window = data.slice(start, i + 1)
    const average = window.reduce((sum, val) => sum + val, 0) / window.length
    result.push(average)
  }
  return result
}

const chartData = computed(() => {
  if (games.value.length === 0) {
    return {
      labels: [],
      datasets: []
    }
  }

  // Sort games by date (oldest first)
  const sortedGames = [...games.value].sort(
    (a, b) => new Date(a.game_date).getTime() - new Date(b.game_date).getTime()
  )

  const labels = sortedGames.map((_, index) => `Game ${index + 1}`)

  let dataPoints: number[]
  let label: string
  let color: string

  const currentStat = availableStats.find(s => s.key === selectedStat.value)!
  color = currentStat.color
  label = currentStat.label

  if (selectedStat.value === 'winrate') {
    // Calculate cumulative winrate
    let wins = 0
    dataPoints = sortedGames.map((game, index) => {
      if (game.stats.win) wins++
      return (wins / (index + 1)) * 100
    })
  } else {
    // Get raw stat values
    dataPoints = sortedGames.map(game => {
      if (selectedStat.value === 'kda') return game.stats.kda
      if (selectedStat.value === 'cs_per_min') return game.stats.cs_per_min
      if (selectedStat.value === 'vision_per_min') return game.stats.vision_per_min
      if (selectedStat.value === 'kp') return game.stats.kp
      return 0
    })
  }

  // Calculate moving average for smoothing (except winrate which is already cumulative)
  const smoothedData = selectedStat.value === 'winrate'
    ? dataPoints
    : calculateMovingAverage(dataPoints, 3)

  return {
    labels,
    datasets: [
      {
        label,
        data: smoothedData,
        borderColor: color,
        backgroundColor: color.replace('rgb', 'rgba').replace(')', ', 0.1)'),
        fill: true,
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 5
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
          if (selectedStat.value === 'winrate' || selectedStat.value === 'kp') {
            return `${value.toFixed(1)}%`
          }
          return value.toFixed(2)
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: selectedStat.value !== 'kda',
      ticks: {
        callback: (value: any) => {
          if (selectedStat.value === 'winrate' || selectedStat.value === 'kp') {
            return `${value}%`
          }
          return value
        },
        color: 'rgb(156, 163, 175)'
      },
      grid: {
        color: 'rgba(75, 85, 99, 0.3)'
      }
    },
    x: {
      ticks: {
        color: 'rgb(156, 163, 175)',
        maxTicksLimit: 10
      },
      grid: {
        color: 'rgba(75, 85, 99, 0.3)'
      }
    }
  }
}))

async function loadGames() {
  try {
    loading.value = true
    const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const response = await axios.get(`${apiUrl}/api/v1/stats/games/${props.riotAccountId}?limit=50`)
    games.value = response.data
  } catch (error) {
    console.error('Failed to load games:', error)
    games.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadGames()
})
</script>
