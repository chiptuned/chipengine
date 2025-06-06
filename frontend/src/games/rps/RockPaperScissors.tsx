import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import { apiClient } from '../../lib/api'
import type { GameState, GameResult } from '../../types/game'

const choices = [
  { value: 'rock', emoji: '🪨', name: 'Rock' },
  { value: 'paper', emoji: '📄', name: 'Paper' },
  { value: 'scissors', emoji: '✂️', name: 'Scissors' }
]

const RockPaperScissors: React.FC = () => {
  const [gameState, setGameState] = useState<GameState | null>(null)
  const [gameResult, setGameResult] = useState<GameResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [playerName, setPlayerName] = useState('Player')

  const createNewGame = async () => {
    setLoading(true)
    try {
      const response = await apiClient.createGame({
        game_type: 'rps',
        players: [playerName, 'SimpleBot'],
        config: { total_rounds: 1 }
      })
      
      const state = await apiClient.getGameState(response.game_id)
      setGameState(state)
      setGameResult(null)
      toast.success('New game created!')
    } catch (error) {
      toast.error(`Failed to create game: ${error}`)
    } finally {
      setLoading(false)
    }
  }

  const makeMove = async (choice: string) => {
    if (!gameState || loading) return
    
    setLoading(true)
    try {
      const response = await apiClient.makeMove(gameState.game_id, {
        player: playerName,
        action: choice
      })
      
      setGameState(response.game_state)
      
      // Make bot move automatically
      if (!response.game_state.game_over && response.game_state.valid_moves['SimpleBot']?.length > 0) {
        setTimeout(async () => {
          try {
            const botChoice = ['rock', 'paper', 'scissors'][Math.floor(Math.random() * 3)]
            const botResponse = await apiClient.makeMove(gameState.game_id, {
              player: 'SimpleBot',
              action: botChoice
            })
            setGameState(botResponse.game_state)
            
            // Check if game is finished
            if (botResponse.game_state.game_over) {
              const result = await apiClient.getGameResult(gameState.game_id)
              setGameResult(result)
            }
          } catch (error) {
            toast.error(`Bot move failed: ${error}`)
          }
        }, 1000)
      }
    } catch (error) {
      toast.error(`Move failed: ${error}`)
    } finally {
      setLoading(false)
    }
  }

  const getChoiceEmoji = (choice: string) => {
    return choices.find(c => c.value === choice)?.emoji || '❓'
  }

  const getWinnerMessage = () => {
    if (!gameResult) return ''
    
    if (gameResult.winner === null) {
      return "It's a tie! 🤝"
    } else if (gameResult.winner === playerName) {
      return "You win! 🎉"
    } else {
      return "Bot wins! 🤖"
    }
  }

  const getLastRound = () => {
    if (!gameState?.metadata?.rounds) return null
    return gameState.metadata.rounds[gameState.metadata.rounds.length - 1]
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-4">
            ← Back to Games
          </Link>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            ✂️ Rock Paper Scissors
          </h1>
          <p className="text-gray-600">Test your strategy against our bot!</p>
        </div>

        {/* Player Name Input */}
        {!gameState && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-md mx-auto mb-8"
          >
            <div className="card">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Name
              </label>
              <input
                type="text"
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value || 'Player')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your name"
              />
            </div>
          </motion.div>
        )}

        {/* Game Area */}
        <div className="max-w-2xl mx-auto">
          {!gameState ? (
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center"
            >
              <div className="card">
                <div className="text-6xl mb-4">🎮</div>
                <h2 className="text-2xl font-bold mb-4">Ready to Play?</h2>
                <button 
                  onClick={createNewGame}
                  disabled={loading}
                  className="btn-primary text-lg px-8 py-3"
                >
                  {loading ? 'Creating Game...' : 'Start New Game'}
                </button>
              </div>
            </motion.div>
          ) : (
            <div className="space-y-6">
              {/* Game Status */}
              <div className="card text-center">
                <div className="text-sm text-gray-600 mb-2">Game ID: {gameState.game_id}</div>
                <div className="text-lg font-semibold">
                  {gameState.game_over ? 'Game Over!' : 'Make Your Choice'}
                </div>
                {gameResult && (
                  <div className="text-2xl font-bold mt-2 text-blue-600">
                    {getWinnerMessage()}
                  </div>
                )}
              </div>

              {/* Last Round Result */}
              <AnimatePresence>
                {getLastRound() && (
                  <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="card"
                  >
                    <h3 className="text-lg font-semibold mb-4 text-center">Last Round</h3>
                    <div className="flex justify-center items-center space-x-8">
                      <div className="text-center">
                        <div className="text-4xl mb-2">
                          {getChoiceEmoji(getLastRound()?.moves[playerName])}
                        </div>
                        <div className="font-medium">{playerName}</div>
                        <div className="text-sm text-gray-600">
                          {getLastRound()?.moves[playerName]}
                        </div>
                      </div>
                      
                      <div className="text-2xl">VS</div>
                      
                      <div className="text-center">
                        <div className="text-4xl mb-2">
                          {getChoiceEmoji(getLastRound()?.moves['SimpleBot'])}
                        </div>
                        <div className="font-medium">SimpleBot</div>
                        <div className="text-sm text-gray-600">
                          {getLastRound()?.moves['SimpleBot']}
                        </div>
                      </div>
                    </div>
                    
                    <div className="text-center mt-4 text-lg font-semibold">
                      {getLastRound()?.winner === null ? 'Tie!' : 
                       getLastRound()?.winner === playerName ? 'You Win!' : 'Bot Wins!'}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Choice Buttons */}
              {!gameState.game_over && gameState.valid_moves[playerName]?.length > 0 && (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="card"
                >
                  <h3 className="text-lg font-semibold mb-4 text-center">Choose Your Move</h3>
                  <div className="grid grid-cols-3 gap-4">
                    {choices.map((choice) => (
                      <motion.button
                        key={choice.value}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => makeMove(choice.value)}
                        disabled={loading}
                        className="game-button flex-col space-y-2 h-24"
                      >
                        <div className="text-3xl">{choice.emoji}</div>
                        <div className="text-sm font-medium">{choice.name}</div>
                      </motion.button>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* Actions */}
              <div className="flex justify-center space-x-4">
                <button 
                  onClick={createNewGame}
                  disabled={loading}
                  className="btn-primary"
                >
                  {loading ? 'Loading...' : 'New Game'}
                </button>
                
                {gameState.game_over && (
                  <Link to="/" className="btn-secondary">
                    Back to Games
                  </Link>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default RockPaperScissors