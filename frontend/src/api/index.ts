import type { Player, RiotAccount, PlayerNote, Draft, PlayerStats, LaneStats, Coach, TeamHighlights, Game } from '@/types'
import apiClient from './client'

export const authApi = {
  validateCode: (code: string, role: string) =>
    apiClient.post('/api/v1/auth/validate-code', { code, role }),
}

export const coachesApi = {
  list: () => apiClient.get<Coach[]>('/api/v1/coaches'),
  get: (id: number) => apiClient.get<Coach>(`/api/v1/coaches/${id}`),
  create: (data: { name: string; role?: string }) =>
    apiClient.post<Coach>('/api/v1/coaches', data),
  update: (id: number, data: Partial<Coach>) =>
    apiClient.patch<Coach>(`/api/v1/coaches/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/v1/coaches/${id}`),
}

export const playersApi = {
  getPlayers: () => apiClient.get<Player[]>('/api/v1/players'),
  get: (id: number) => apiClient.get<Player>(`/api/v1/players/${id}`),
  create: (data: { summoner_name: string; role: string }) =>
    apiClient.post<Player>('/api/v1/players', data),
  update: (id: number, data: Partial<Player>) =>
    apiClient.patch<Player>(`/api/v1/players/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/v1/players/${id}`),
}

export const riotAccountsApi = {
  create: (playerId: number, data: { summoner_name: string; tag_line: string; is_main?: boolean }) =>
    apiClient.post<RiotAccount>(`/api/v1/players/${playerId}/riot-accounts`, data),
  updateRank: (accountId: number, data: any) =>
    apiClient.patch<RiotAccount>(`/api/v1/riot-accounts/${accountId}/rank`, data),
  delete: (id: number) => apiClient.delete(`/api/v1/riot-accounts/${id}`),
}

export const playerNotesApi = {
  list: (playerId: number) => apiClient.get<PlayerNote[]>(`/api/v1/players/${playerId}/notes`),
  create: (playerId: number, data: { author_role: string; note_type: string; content: string }) =>
    apiClient.post<PlayerNote>(`/api/v1/players/${playerId}/notes`, data),
  update: (id: number, data: Partial<PlayerNote>) =>
    apiClient.patch<PlayerNote>(`/api/v1/notes/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/v1/notes/${id}`),
}

export const draftsApi = {
  list: () => apiClient.get<Draft[]>('/api/v1/drafts'),
  get: (id: number) => apiClient.get<Draft>(`/api/v1/drafts/${id}`),
  create: (data: Omit<Draft, 'id' | 'created_at'>) => apiClient.post<Draft>('/api/v1/drafts', data),
  delete: (id: number) => apiClient.delete(`/api/v1/drafts/${id}`),
}

export const statsApi = {
  getPlayerStats: (playerId: number) => apiClient.get<PlayerStats>(`/api/v1/stats/player/${playerId}`),
  getLaneStats: (lane: string) => apiClient.get<LaneStats>(`/api/v1/stats/lane/${lane}`),
  refreshStats: (riotAccountId: number) =>
    apiClient.post(`/api/v1/stats/refresh/${riotAccountId}`),
  getTeamHighlights: () => apiClient.get<TeamHighlights>(`/api/v1/stats/team/highlights`),
}

export const gamesApi = {
  getPentakills: () => apiClient.get<Game[]>('/api/v1/games/pentakills'),
  updateGameTag: (gameId: number, data: { game_type?: string; is_pentakill?: boolean }) =>
    apiClient.patch<Game>(`/api/v1/games/${gameId}/tag`, data),
}
