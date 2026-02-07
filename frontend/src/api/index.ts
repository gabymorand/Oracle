import type {
  Player,
  RiotAccount,
  PlayerNote,
  Draft,
  PlayerStats,
  LaneStats,
  Coach,
  TeamHighlights,
  Game,
  CalendarEvent,
  CalendarEventWithSeries,
  DayAvailabilitySummary,
  DayDetail,
  PlayerAvailability,
  PlayerTierList,
  ChampionStatsWithScore,
  TierLevel,
  OpponentTeam,
  OpponentTeamWithStats,
  ScrimReview,
  ScrimReviewWithTeam,
  ScoutedPlayer,
  ScoutedPlayerWithTeam,
  ScrimHistoryItem,
  ScrimManagementDashboard,
  DraftSeriesWithGames,
  AdminDashboard,
  AdminTeamDetails,
  AdminTeamStats,
  TeamActivityResponse,
  MatchDetailResponse,
} from '@/types'
import apiClient from './client'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Separate client for admin (uses admin_token)
const adminClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

adminClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

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

export const draftSeriesApi = {
  list: (skip = 0, limit = 50) =>
    apiClient.get<DraftSeriesWithGames[]>(`/api/v1/draft-series?skip=${skip}&limit=${limit}`),
  listWithGames: (skip = 0, limit = 50) =>
    apiClient.get<DraftSeriesWithGames[]>(`/api/v1/draft-series/with-games?skip=${skip}&limit=${limit}`),
  get: (id: number) =>
    apiClient.get<DraftSeriesWithGames>(`/api/v1/draft-series/${id}`),
}

export const statsApi = {
  getPlayerStats: (playerId: number) => apiClient.get<PlayerStats>(`/api/v1/stats/player/${playerId}`),
  getLaneStats: (lane: string) => apiClient.get<LaneStats>(`/api/v1/stats/lane/${lane}`),
  refreshStats: (riotAccountId: number) =>
    apiClient.post(`/api/v1/stats/refresh/${riotAccountId}`),
  refreshAllStats: () =>
    apiClient.post<{
      message: string
      refreshed: number
      failed: number
      results: Array<{ account: string; status: string; error?: string }>
    }>('/api/v1/stats/refresh-all'),
  getTeamHighlights: () => apiClient.get<TeamHighlights>(`/api/v1/stats/team/highlights`),
  getTeamActivity: (weekOffset = 0) =>
    apiClient.get<TeamActivityResponse>(`/api/v1/stats/activity?week_offset=${weekOffset}`),
}

export const gamesApi = {
  getPentakills: () => apiClient.get<Game[]>('/api/v1/games/pentakills'),
  updateGameTag: (gameId: number, data: { game_type?: string; is_pentakill?: boolean }) =>
    apiClient.patch<Game>(`/api/v1/games/${gameId}/tag`, data),
  getMatchDetails: (gameId: number) =>
    apiClient.get<MatchDetailResponse>(`/api/v1/games/${gameId}/details`),
}

export const calendarApi = {
  // Events
  getEvents: (year: number, month: number) =>
    apiClient.get<CalendarEvent[]>(`/api/v1/calendar/events?year=${year}&month=${month}`),
  getEvent: (id: number) =>
    apiClient.get<CalendarEventWithSeries>(`/api/v1/calendar/events/${id}`),
  createEvent: (data: Omit<CalendarEvent, 'id' | 'created_at' | 'updated_at'>) =>
    apiClient.post<CalendarEvent>('/api/v1/calendar/events', data),
  updateEvent: (id: number, data: Partial<CalendarEvent>) =>
    apiClient.patch<CalendarEvent>(`/api/v1/calendar/events/${id}`, data),
  deleteEvent: (id: number) => apiClient.delete(`/api/v1/calendar/events/${id}`),

  // Availabilities
  getDayAvailabilities: (date: string) =>
    apiClient.get<DayAvailabilitySummary>(`/api/v1/calendar/availabilities?date=${date}`),
  getMonthAvailabilities: (year: number, month: number) =>
    apiClient.get<DayAvailabilitySummary[]>(
      `/api/v1/calendar/availabilities/month?year=${year}&month=${month}`
    ),
  setPlayerAvailability: (
    playerId: number,
    data: { date: string; slot: string; is_available: boolean; note?: string }
  ) =>
    apiClient.post<PlayerAvailability>(
      `/api/v1/calendar/availabilities/player/${playerId}`,
      data
    ),
  setPlayerAvailabilityBulk: (
    playerId: number,
    data: Array<{ date: string; slot: string; is_available: boolean; note?: string }>
  ) =>
    apiClient.post<PlayerAvailability[]>(
      `/api/v1/calendar/availabilities/player/${playerId}/bulk`,
      data
    ),

  // Day detail (combined view)
  getDayDetail: (date: string) =>
    apiClient.get<DayDetail>(`/api/v1/calendar/day?date=${date}`),

  // Scrims
  getScrims: (limit = 50) =>
    apiClient.get<CalendarEventWithSeries[]>(`/api/v1/calendar/scrims?limit=${limit}`),

  // Calendar Invitations
  getSmtpStatus: () =>
    apiClient.get<{ configured: boolean }>('/api/v1/calendar/smtp-status'),
  sendInvitation: (eventId: number, playerIds?: number[]) =>
    apiClient.post<{ sent_to: string[]; failed: string[]; smtp_configured: boolean }>(
      `/api/v1/calendar/events/${eventId}/send-invitation`,
      { player_ids: playerIds || null }
    ),
}

export const tierListApi = {
  getPlayerTierList: (playerId: number) =>
    apiClient.get<PlayerTierList>(`/api/v1/tier-list/player/${playerId}`),
  getPlayerChampionStats: (playerId: number) =>
    apiClient.get<ChampionStatsWithScore[]>(`/api/v1/tier-list/player/${playerId}/champions`),
  setChampionTier: (playerId: number, championId: number, tier: TierLevel) =>
    apiClient.post(`/api/v1/tier-list/player/${playerId}/champion/${championId}`, {
      champion_id: championId,
      tier: tier,
    }),
  deleteChampionTier: (playerId: number, championId: number) =>
    apiClient.delete(`/api/v1/tier-list/player/${playerId}/champion/${championId}`),
}

export const scrimManagementApi = {
  // Dashboard
  getDashboard: () =>
    apiClient.get<ScrimManagementDashboard>('/api/v1/scrim-management/dashboard'),
  getHistory: (limit = 50) =>
    apiClient.get<ScrimHistoryItem[]>(`/api/v1/scrim-management/history?limit=${limit}`),

  // Teams
  getTeams: () =>
    apiClient.get<OpponentTeam[]>('/api/v1/scrim-management/teams'),
  getTeamsWithStats: () =>
    apiClient.get<OpponentTeamWithStats[]>('/api/v1/scrim-management/teams/with-stats'),
  getTeam: (id: number) =>
    apiClient.get<OpponentTeamWithStats>(`/api/v1/scrim-management/teams/${id}`),
  createTeam: (data: Omit<OpponentTeam, 'id' | 'created_at' | 'updated_at'>) =>
    apiClient.post<OpponentTeam>('/api/v1/scrim-management/teams', data),
  updateTeam: (id: number, data: Partial<OpponentTeam>) =>
    apiClient.patch<OpponentTeam>(`/api/v1/scrim-management/teams/${id}`, data),
  deleteTeam: (id: number) =>
    apiClient.delete(`/api/v1/scrim-management/teams/${id}`),

  // Reviews
  getReviews: () =>
    apiClient.get<ScrimReview[]>('/api/v1/scrim-management/reviews'),
  getReviewByEvent: (eventId: number) =>
    apiClient.get<ScrimReviewWithTeam | null>(`/api/v1/scrim-management/reviews/event/${eventId}`),
  getReview: (id: number) =>
    apiClient.get<ScrimReviewWithTeam>(`/api/v1/scrim-management/reviews/${id}`),
  createReview: (data: {
    calendar_event_id: number
    opponent_team_id?: number
    quality: string
    punctuality?: number
    communication?: number
    competitiveness?: number
    would_scrim_again?: number
    notes?: string
  }) =>
    apiClient.post<ScrimReview>('/api/v1/scrim-management/reviews', data),
  updateReview: (id: number, data: Partial<ScrimReview>) =>
    apiClient.patch<ScrimReview>(`/api/v1/scrim-management/reviews/${id}`, data),
  deleteReview: (id: number) =>
    apiClient.delete(`/api/v1/scrim-management/reviews/${id}`),
  createOrUpdateReview: async (eventId: number, data: {
    quality: string
    opponent_team_id?: number
    punctuality?: number
    communication?: number
    competitiveness?: number
    would_scrim_again?: number
    notes?: string
  }) => {
    // Check if review exists for this event
    try {
      const existing = await apiClient.get<ScrimReviewWithTeam>(`/api/v1/scrim-management/reviews/event/${eventId}`)
      if (existing.data && existing.data.id) {
        // Update existing review
        return apiClient.patch<ScrimReview>(`/api/v1/scrim-management/reviews/${existing.data.id}`, data)
      }
    } catch {
      // No existing review, create new one
    }
    return apiClient.post<ScrimReview>('/api/v1/scrim-management/reviews', {
      calendar_event_id: eventId,
      ...data,
    })
  },

  // Scouted Players
  getScoutedPlayers: (prospectsOnly = false) =>
    apiClient.get<ScoutedPlayer[]>(
      `/api/v1/scrim-management/scouted-players?prospects_only=${prospectsOnly}`
    ),
  getScoutedByTeam: (teamId: number) =>
    apiClient.get<ScoutedPlayer[]>(`/api/v1/scrim-management/scouted-players/team/${teamId}`),
  getScoutedPlayer: (id: number) =>
    apiClient.get<ScoutedPlayerWithTeam>(`/api/v1/scrim-management/scouted-players/${id}`),
  createScoutedPlayer: (data: Omit<ScoutedPlayer, 'id' | 'created_at' | 'updated_at'>) =>
    apiClient.post<ScoutedPlayer>('/api/v1/scrim-management/scouted-players', data),
  updateScoutedPlayer: (id: number, data: Partial<ScoutedPlayer>) =>
    apiClient.patch<ScoutedPlayer>(`/api/v1/scrim-management/scouted-players/${id}`, data),
  deleteScoutedPlayer: (id: number) =>
    apiClient.delete(`/api/v1/scrim-management/scouted-players/${id}`),
}

export const adminApi = {
  login: (code: string) =>
    adminClient.post<{ access_token: string }>('/api/v1/admin/login', { code }),

  getDashboard: () =>
    adminClient.get<AdminDashboard>('/api/v1/admin/dashboard'),

  getTeamDetails: (teamId: number) =>
    adminClient.get<AdminTeamDetails>(`/api/v1/admin/teams/${teamId}`),

  createTeam: (data: { name: string; access_code: string }) =>
    adminClient.post<AdminTeamStats>('/api/v1/admin/teams', data),

  updateTeam: (teamId: number, data: { name?: string; access_code?: string }) =>
    adminClient.patch<AdminTeamDetails>(`/api/v1/admin/teams/${teamId}`, data),

  deleteTeam: (teamId: number) =>
    adminClient.delete(`/api/v1/admin/teams/${teamId}`),

  deletePlayer: (playerId: number) =>
    adminClient.delete(`/api/v1/admin/players/${playerId}`),

  deleteCoach: (coachId: number) =>
    adminClient.delete(`/api/v1/admin/coaches/${coachId}`),
}
