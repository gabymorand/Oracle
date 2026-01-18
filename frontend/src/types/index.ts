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

export type UserRole = 'coach' | 'player' | 'head_coach'

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
