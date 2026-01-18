<template>
  <div class="min-h-screen bg-gray-900">
    <AppNavbar :show-back-button="true" />

    <div class="max-w-7xl mx-auto px-4 py-8">
      <div class="mb-6 flex justify-between items-center">
        <h1 class="text-3xl font-bold">Draft Planner</h1>
        <button
          @click="showAddForm = !showAddForm"
          class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded transition"
        >
          {{ showAddForm ? 'Cancel' : 'Add Draft' }}
        </button>
      </div>

      <div v-if="showAddForm" class="bg-gray-800 rounded-lg p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">New Draft</h2>
        <form @submit.prevent="addDraft" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm mb-2">Date</label>
              <input
                v-model="newDraft.date"
                type="date"
                class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600"
                required
              />
            </div>
            <div>
              <label class="block text-sm mb-2">Opponent</label>
              <input
                v-model="newDraft.opponent_name"
                type="text"
                class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600"
                required
              />
            </div>
            <div>
              <label class="block text-sm mb-2">Side</label>
              <select v-model="newDraft.blue_side" class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600">
                <option :value="true">Blue Side</option>
                <option :value="false">Red Side</option>
              </select>
            </div>
            <div>
              <label class="block text-sm mb-2">Result</label>
              <select v-model="newDraft.result" class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600">
                <option :value="null">Pending</option>
                <option value="win">Win</option>
                <option value="loss">Loss</option>
              </select>
            </div>
          </div>
          <div>
            <label class="block text-sm mb-2">Notes</label>
            <textarea
              v-model="newDraft.notes"
              class="w-full px-3 py-2 bg-gray-700 rounded border border-gray-600"
              rows="3"
            ></textarea>
          </div>
          <button type="submit" class="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded transition">
            Save Draft
          </button>
        </form>
      </div>

      <div v-if="loading" class="text-center py-12">
        <p class="text-gray-400">Loading drafts...</p>
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="draft in drafts"
          :key="draft.id"
          class="bg-gray-800 rounded-lg p-6"
        >
          <div class="flex justify-between items-start mb-4">
            <div>
              <h3 class="text-xl font-semibold">vs {{ draft.opponent_name }}</h3>
              <p class="text-gray-400 text-sm">{{ draft.date }} - {{ draft.blue_side ? 'Blue Side' : 'Red Side' }}</p>
            </div>
            <span
              v-if="draft.result"
              :class="draft.result === 'win' ? 'bg-green-600' : 'bg-red-600'"
              class="px-3 py-1 rounded uppercase text-sm"
            >
              {{ draft.result }}
            </span>
          </div>
          <p v-if="draft.notes" class="text-gray-300">{{ draft.notes }}</p>
        </div>

        <div v-if="drafts.length === 0" class="text-center py-12">
          <p class="text-gray-400">No drafts yet. Add your first draft above.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { draftsApi } from '@/api'
import type { Draft } from '@/types'
import AppNavbar from '@/components/AppNavbar.vue'

const router = useRouter()
const authStore = useAuthStore()

const drafts = ref<Draft[]>([])
const loading = ref(true)
const showAddForm = ref(false)
const newDraft = ref({
  date: new Date().toISOString().split('T')[0],
  opponent_name: '',
  blue_side: true,
  picks: [],
  bans: [],
  result: null as string | null,
  notes: '',
})

async function loadDrafts() {
  try {
    const response = await draftsApi.list()
    drafts.value = response.data
  } catch (error) {
    console.error('Failed to load drafts:', error)
  } finally {
    loading.value = false
  }
}

async function addDraft() {
  try {
    await draftsApi.create(newDraft.value as any)
    showAddForm.value = false
    newDraft.value = {
      date: new Date().toISOString().split('T')[0],
      opponent_name: '',
      blue_side: true,
      picks: [],
      bans: [],
      result: null,
      notes: '',
    }
    await loadDrafts()
  } catch (error) {
    console.error('Failed to add draft:', error)
  }
}

onMounted(() => {
  loadDrafts()
})
</script>
