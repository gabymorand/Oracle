<template>
  <div class="min-h-screen bg-gray-900">
    <AppNavbar :show-back-button="true" />

    <div class="max-w-7xl mx-auto px-4 py-8">
      <div class="mb-6 flex justify-between items-center">
        <h1 class="text-3xl font-bold">Coaches Management</h1>
        <button
          @click="showAddForm = !showAddForm"
          class="bg-green-600 hover:bg-green-700 px-4 py-2 rounded transition"
        >
          {{ showAddForm ? 'Cancel' : 'Add Coach' }}
        </button>
      </div>

      <!-- Add Coach Form -->
      <div v-if="showAddForm" class="bg-gray-800 rounded-lg p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">New Coach Profile</h2>
        <form @submit.prevent="addCoach" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-2">Coach Name</label>
              <input
                v-model="newCoach.name"
                type="text"
                class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
                placeholder="Enter coach name"
                required
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-2">Specialized Role (Optional)</label>
              <select
                v-model="newCoach.role"
                class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
              >
                <option :value="null">None (Head Coach)</option>
                <option value="Assistant">Assistant Coach</option>
                <option value="top">Top</option>
                <option value="jungle">Jungle</option>
                <option value="mid">Mid</option>
                <option value="adc">ADC</option>
                <option value="support">Support</option>
              </select>
            </div>
          </div>
          <button
            type="submit"
            class="bg-green-600 hover:bg-green-700 px-6 py-2 rounded transition"
            :disabled="loading"
          >
            {{ loading ? 'Creating...' : 'Create Coach' }}
          </button>
        </form>
      </div>

      <!-- Coaches List -->
      <div v-if="loadingCoaches" class="text-center py-12">
        <p class="text-gray-400">Loading coaches...</p>
      </div>

      <div v-else-if="coaches.length === 0" class="text-center py-12">
        <p class="text-gray-400">No coaches yet. Create the first one above!</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="coach in coaches"
          :key="coach.id"
          class="bg-gray-800 rounded-lg p-6 hover:bg-gray-750 transition"
        >
          <div class="flex justify-between items-start mb-4">
            <div>
              <h3 class="text-xl font-semibold mb-1">{{ coach.name }}</h3>
              <span v-if="coach.role" class="text-sm bg-blue-600 px-2 py-1 rounded uppercase">
                {{ coach.role }} Coach
              </span>
              <span v-else class="text-sm bg-purple-600 px-2 py-1 rounded">
                Head Coach
              </span>
            </div>
            <button
              @click="confirmDelete(coach)"
              class="text-red-400 hover:text-red-300 transition"
              title="Delete coach"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
          <p class="text-sm text-gray-400">
            Created {{ new Date(coach.created_at).toLocaleDateString() }}
          </p>
        </div>
      </div>

      <!-- Delete Confirmation Modal -->
      <div
        v-if="coachToDelete"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
        @click="coachToDelete = null"
      >
        <div
          class="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4"
          @click.stop
        >
          <h3 class="text-xl font-bold mb-4">Delete Coach</h3>
          <p class="text-gray-300 mb-6">
            Are you sure you want to delete <strong>{{ coachToDelete.name }}</strong>?
            This action cannot be undone.
          </p>
          <div class="flex gap-3 justify-end">
            <button
              @click="coachToDelete = null"
              class="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded transition"
            >
              Cancel
            </button>
            <button
              @click="deleteCoach"
              class="px-4 py-2 bg-red-600 hover:bg-red-700 rounded transition"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { coachesApi } from '@/api'
import type { Coach } from '@/types'
import AppNavbar from '@/components/AppNavbar.vue'

const coaches = ref<Coach[]>([])
const loadingCoaches = ref(true)
const loading = ref(false)
const showAddForm = ref(false)
const coachToDelete = ref<Coach | null>(null)

const newCoach = ref({
  name: '',
  role: null as string | null,
})

async function loadCoaches() {
  loadingCoaches.value = true
  try {
    const response = await coachesApi.list()
    coaches.value = response.data
  } catch (error) {
    console.error('Failed to load coaches:', error)
  } finally {
    loadingCoaches.value = false
  }
}

async function addCoach() {
  loading.value = true
  try {
    const response = await coachesApi.create({
      name: newCoach.value.name,
      role: newCoach.value.role || undefined,
    })
    coaches.value.push(response.data)
    showAddForm.value = false
    newCoach.value = { name: '', role: null }
  } catch (error: any) {
    console.error('Failed to create coach:', error)
    if (error.response?.status === 400) {
      alert('A coach with this name already exists!')
    } else {
      alert('Failed to create coach. Please try again.')
    }
  } finally {
    loading.value = false
  }
}

function confirmDelete(coach: Coach) {
  coachToDelete.value = coach
}

async function deleteCoach() {
  if (!coachToDelete.value) return

  try {
    await coachesApi.delete(coachToDelete.value.id)
    coaches.value = coaches.value.filter((c: Coach) => c.id !== coachToDelete.value!.id)
    coachToDelete.value = null
  } catch (error) {
    console.error('Failed to delete coach:', error)
    alert('Failed to delete coach. Please try again.')
  }
}

onMounted(() => {
  loadCoaches()
})
</script>
