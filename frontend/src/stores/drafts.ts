import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Draft } from '@/types'
import { draftsApi } from '@/api'

export const useDraftsStore = defineStore('drafts', () => {
  const drafts = ref<Draft[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchDrafts() {
    loading.value = true
    error.value = null
    try {
      const response = await draftsApi.list()
      drafts.value = response.data
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function createDraft(data: Omit<Draft, 'id' | 'created_at'>) {
    loading.value = true
    error.value = null
    try {
      const response = await draftsApi.create(data)
      drafts.value.push(response.data)
      return response.data
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteDraft(id: number) {
    loading.value = true
    error.value = null
    try {
      await draftsApi.delete(id)
      drafts.value = drafts.value.filter((d) => d.id !== id)
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    drafts,
    loading,
    error,
    fetchDrafts,
    createDraft,
    deleteDraft,
  }
})
