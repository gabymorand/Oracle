export interface Player {
  id: number
  summoner_name: string
  role: string
  created_at: string
  updated_at?: string
  riot_accounts: RiotAccount[]
}

export interface RiotAccount {
  id: number
  player_id: number
  puuid: string
  summoner_name: string
  tag_line: string
  is_main: boolean
  rank_tier?: string
  rank_division?: string
  lp?: number
  created_at: string
  updated_at?: string
}

export interface PlayerNote {
  id: number
  player_id: number
  author_role: string
  note_type: string
  content: string
  created_at: string
  updated_at?: string
}

export interface Draft {
  id: number
  date: string
  opponent_name: string
  blue_side: boolean
  picks: number[]
  bans: number[]
  result?: string
  notes?: string
  created_at: string
}

export interface PlayerStats {
  player_id: number
  summoner_name: string
  role: string
  total_games: number
  avg_kda: number
  avg_cs_per_min: number
  avg_gold_per_min: number
  avg_vision_score_per_min: number
  avg_kill_participation: number
  winrate: number
}

export interface LaneStats {
  lane: string
  players: PlayerStats[]
  combined_winrate: number
  total_games: number
}

export type UserRole = 'coach' | 'player' | 'head_coach' | 'manager'

export interface TeamInfo {
  id: number
  name: string
}

export interface Coach {
  id: number
  name: string
  role?: string
  created_at: string
  updated_at: string
}

export interface Game {
  id: number
  riot_account_id: number
  match_id: string
  game_type: string
  champion_id: number
  role: string
  stats: {
    kills: number
    deaths: number
    assists: number
    cs: number
    gold: number
    vision_score: number
    damage_dealt: number
    win: boolean
    [key: string]: any
  }
  game_duration: number
  game_date: string
  is_pentakill: boolean
  created_at: string
}

export interface TeamHighlights {
  total_games: number
  total_wins: number
  winrate: number
  competitive_games: number
  competitive_wins: number
  competitive_winrate: number
  total_pentakills: number
  recent_matches: Game[]
}

// Calendar Types

export type TimeSlot = 'morning' | 'afternoon' | 'evening'

export type EventType = 'scrim' | 'training' | 'official_match' | 'meeting' | 'other'

export interface PlayerAvailability {
  id: number
  player_id: number
  date: string
  slot: TimeSlot
  is_available: boolean
  note?: string
  created_at: string
  updated_at?: string
}

export interface PlayerAvailabilitySummary {
  player_id: number
  player_name: string
  morning: boolean
  afternoon: boolean
  evening: boolean
}

export interface DayAvailabilitySummary {
  date: string
  availabilities: PlayerAvailabilitySummary[]
}

export interface CalendarEvent {
  id: number
  title: string
  event_type: EventType
  date: string
  slot: TimeSlot
  start_time?: string
  end_time?: string
  draft_series_id?: number
  opponent_name?: string
  opponent_players?: string
  description?: string
  location?: string
  created_at: string
  updated_at?: string
}

export interface DraftSeriesInfo {
  id: number
  opponent_name: string
  format: string
  our_score: number
  opponent_score: number
  result?: string
}

export interface CalendarEventWithSeries extends CalendarEvent {
  draft_series_info?: DraftSeriesInfo
}

export interface DayDetail {
  date: string
  events: CalendarEvent[]
  availabilities: PlayerAvailabilitySummary[]
}

// Tier List Types

export type TierLevel = 'S' | 'A' | 'B' | 'C' | 'D'

export interface ChampionStatsWithScore {
  champion_id: number
  champion_name: string
  games_played: number
  wins: number
  losses: number
  winrate: number
  avg_kda: number
  avg_cs_per_min: number
  avg_gold_per_min: number
  avg_vision_per_min: number
  avg_damage_per_min: number
  avg_kill_participation: number
  performance_score: number
  tier?: TierLevel
}

export interface PlayerTierList {
  player_id: number
  player_name: string
  champions: ChampionStatsWithScore[]
  tier_s: ChampionStatsWithScore[]
  tier_a: ChampionStatsWithScore[]
  tier_b: ChampionStatsWithScore[]
  tier_c: ChampionStatsWithScore[]
  tier_d: ChampionStatsWithScore[]
  unranked: ChampionStatsWithScore[]
}

// Scrim Management Types

export type ScrimQuality = 'excellent' | 'good' | 'average' | 'poor' | 'bad'
export type Potential = 'low' | 'medium' | 'high'

export interface OpponentTeam {
  id: number
  name: string
  contact_name?: string
  contact_discord?: string
  contact_email?: string
  contact_twitter?: string
  notes?: string
  created_at: string
  updated_at?: string
}

export interface OpponentTeamWithStats extends OpponentTeam {
  total_scrims: number
  wins: number
  losses: number
  avg_quality?: number
  scouted_players_count: number
}

export interface ScrimReview {
  id: number
  calendar_event_id: number
  opponent_team_id?: number
  quality: ScrimQuality
  punctuality?: number
  communication?: number
  competitiveness?: number
  would_scrim_again?: number
  notes?: string
  created_at: string
  updated_at?: string
}

export interface ScrimReviewWithTeam extends ScrimReview {
  opponent_team_name?: string
}

export interface ScoutedPlayer {
  id: number
  summoner_name: string
  tag_line?: string
  team_id?: number
  role?: string
  rating?: number
  mechanical_skill?: number
  game_sense?: number
  communication?: number
  attitude?: number
  potential?: Potential
  notes?: string
  is_prospect: boolean
  created_at: string
  updated_at?: string
}

export interface ScoutedPlayerWithTeam extends ScoutedPlayer {
  team_name?: string
}

export interface ScrimHistoryItem {
  event_id: number
  title: string
  date: string
  slot: string
  opponent_name?: string
  opponent_team_id?: number
  review?: ScrimReview
  draft_series_result?: string
  our_score?: number
  opponent_score?: number
}

export interface ScrimManagementDashboard {
  total_scrims: number
  reviewed_scrims: number
  total_teams: number
  total_scouted_players: number
  prospects_count: number
  recent_scrims: ScrimHistoryItem[]
  top_teams: OpponentTeamWithStats[]
}

// Draft Series Types for Scrim Calendar
export interface DraftGame {
  id: number
  series_id: number
  game_number: number
  blue_side: boolean
  our_bans: number[]
  opponent_bans: number[]
  our_picks: number[]
  opponent_picks: number[]
  result?: string
  notes?: string
  created_at: string
}

export interface DraftSeriesWithGames {
  id: number
  date: string
  opponent_name: string
  format: string
  our_score: number
  opponent_score: number
  result?: string
  notes?: string
  games: DraftGame[]
  created_at: string
}

export interface ScrimCalendarStats {
  total_scrims: number
  total_games: number
  wins: number
  losses: number
  winrate: number
}
