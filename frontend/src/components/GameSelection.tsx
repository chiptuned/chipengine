import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'

const GameSelection: React.FC = () => {
  const games = [
    {
      id: 'rps',
      name: 'Rock Paper Scissors',
      description: 'Classic game perfect for testing bot strategies',
      emoji: '✂️',
      path: '/rps',
      status: 'available'
    },
    {
      id: 'poker',
      name: 'Texas Hold\'em',
      description: 'Coming soon - Advanced poker gameplay',
      emoji: '🃏',
      path: '/poker',
      status: 'coming_soon'
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🎮 ChipEngine
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Fast, lean game engine for bot competitions. 
            Start with Rock Paper Scissors, expand to Poker and beyond.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {games.map((game, index) => (
            <motion.div
              key={game.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`card ${game.status === 'available' ? 'hover:shadow-lg cursor-pointer' : 'opacity-60'}`}
            >
              {game.status === 'available' ? (
                <Link to={game.path} className="block">
                  <div className="text-center">
                    <div className="text-6xl mb-4">{game.emoji}</div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">
                      {game.name}
                    </h2>
                    <p className="text-gray-600 mb-4">
                      {game.description}
                    </p>
                    <button className="btn-primary">
                      Play Now
                    </button>
                  </div>
                </Link>
              ) : (
                <div className="text-center">
                  <div className="text-6xl mb-4">{game.emoji}</div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    {game.name}
                  </h2>
                  <p className="text-gray-600 mb-4">
                    {game.description}
                  </p>
                  <button className="btn-secondary" disabled>
                    Coming Soon
                  </button>
                </div>
              )}
            </motion.div>
          ))}
        </div>

        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center mt-16"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Development Workflow
          </h3>
          <div className="flex justify-center space-x-4 text-sm text-gray-600">
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full">
              ✅ RPS MVP
            </span>
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full">
              🔄 Multi-game Platform
            </span>
            <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full">
              📅 Scale & Polish
            </span>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default GameSelection