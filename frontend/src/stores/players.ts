import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Player } from '@/types'
import { playersApi } from '@/api'

export const usePlayersStore = defineStore('players', () => {
  const players = ref<Player[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchPlayers() {
    loading.value = true
    error.value = null
    try {
      const response = await playersApi.list()
      players.value = response.data
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function createPlayer(data: { summoner_name: string; role: string }) {
    loading.value = true
    error.value = null
    try {
      const response = await playersApi.create(data)
      players.value.push(response.data)
      return response.data
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updatePlayer(id: number, data: Partial<Player>) {
    loading.value = true
    error.value = null
    try {
      const response = await playersApi.update(id, data)
      const index = players.value.findIndex((p) => p.id === id)
      if (index !== -1) {
        players.value[index] = response.data
      }
      return response.data
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deletePlayer(id: number) {
    loading.value = true
    error.value = null
    try {
      await playersApi.delete(id)
      players.value = players.value.filter((p) => p.id !== id)
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    players,
    loading,
    error,
    fetchPlayers,
    createPlayer,
    updatePlayer,
    deletePlayer,
  }
})
