export interface GameState {
  game_id: string
  players: string[]
  current_player: string | null
  game_over: boolean
  winner: string | null
  valid_moves: Record<string, string[]>
  metadata: Record<string, any>
}

export interface CreateGameRequest {
  game_type: string
  players: string[]
  config?: Record<string, any>
}

export interface CreateGameResponse {
  game_id: string
  game_type: string
  players: string[]
  status: string
}

export interface MakeMoveRequest {
  player: string
  action: string
  data?: Record<string, any>
}

export interface MakeMoveResponse {
  success: boolean
  message: string
  game_state: GameState
}

export interface GameResult {
  game_id: string
  winner: string | null
  players: string[]
  duration_seconds: number
  metadata: Record<string, any>
}

export interface StressTestRequest {
  game_type: string
  concurrent_games: number
  games_per_second: number
  duration_seconds: number
  total_games?: number
}

export interface StressTestResponse {
  test_id: string
  status: string
  config: StressTestRequest
  started_at: string
}

export interface StressTestStatus {
  test_id: string
  status: string
  started_at: string
  elapsed_seconds: number
  games_created: number
  games_completed: number
  games_failed: number
  current_rps: number
  peak_rps: number
  avg_game_duration: number
  errors: string[]
  config: StressTestRequest
}

export interface StressTestMetrics {
  test_id: string
  performance: {
    games_per_second: number
    peak_games_per_second: number
    average_game_duration_ms: number
    success_rate: number
    completion_rate: number
  }
  counters: {
    games_created: number
    games_completed: number
    games_failed: number
    total_games_target: number
  }
  timing: {
    elapsed_seconds: number
    target_duration: number
    progress_percentage: number
  }
  errors: string[]
}