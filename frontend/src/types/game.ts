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