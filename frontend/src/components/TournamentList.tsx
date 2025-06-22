import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Tournament } from '../types/game'

const TournamentList: React.FC = () => {
  const [tournaments, setTournaments] = useState<Tournament[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'active' | 'pending' | 'completed'>('all')

  // Mock data for demo purposes
  useEffect(() => {
    // In a real app, this would fetch from the API
    const mockTournaments: Tournament[] = [
      {
        tournament_id: '1',
        name: 'RPS Championship 2024',
        game_type: 'rps',
        status: 'active',
        format: 'single_elimination',
        participants: ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry'],
        max_participants: 8,
        created_at: new Date(Date.now() - 3600000).toISOString(),
        started_at: new Date(Date.now() - 1800000).toISOString(),
        current_round: 2,
        total_rounds: 3
      },
      {
        tournament_id: '2',
        name: 'Weekly RPS Tournament',
        game_type: 'rps',
        status: 'pending',
        format: 'single_elimination',
        participants: ['Player1', 'Player2', 'Player3'],
        max_participants: 16,
        created_at: new Date(Date.now() - 300000).toISOString(),
        current_round: 0,
        total_rounds: 4
      },
      {
        tournament_id: '3',
        name: 'RPS Masters Cup',
        game_type: 'rps',
        status: 'completed',
        format: 'double_elimination',
        participants: ['Winner1', 'Winner2', 'Winner3', 'Winner4'],
        max_participants: 4,
        created_at: new Date(Date.now() - 86400000).toISOString(),
        started_at: new Date(Date.now() - 82800000).toISOString(),
        completed_at: new Date(Date.now() - 7200000).toISOString(),
        current_round: 3,
        total_rounds: 3
      }
    ]

    setTimeout(() => {
      setTournaments(mockTournaments)
      setLoading(false)
    }, 500)
  }, [])

  const filteredTournaments = tournaments.filter(t => 
    filter === 'all' || t.status === filter
  )

  const getStatusColor = (status: Tournament['status']) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'completed':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getFormatIcon = (format: Tournament['format']) => {
    switch (format) {
      case 'single_elimination':
        return '🏆'
      case 'double_elimination':
        return '🎯'
      case 'round_robin':
        return '🔄'
      default:
        return '🎮'
    }
  }

  return (
    <div className="min-h-screen">
      <div className="container mx-auto px-4 py-8">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-4xl font-bold gradient-text">Tournaments</h1>
            <Link to="/games" className="btn-secondary">
              Back to Games
            </Link>
          </div>

          <div className="flex space-x-2 mb-6">
            {(['all', 'active', 'pending', 'completed'] as const).map((status) => (
              <button
                key={status}
                onClick={() => setFilter(status)}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  filter === status
                    ? 'bg-blue-500 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </button>
            ))}
          </div>
        </motion.div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            <p className="text-gray-600 mt-4">Loading tournaments...</p>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {filteredTournaments.map((tournament, index) => (
              <motion.div
                key={tournament.tournament_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="glass-card glow-effect"
              >
                <Link to={`/tournaments/${tournament.tournament_id}`}>
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-gray-900 mb-1">
                        {tournament.name}
                      </h3>
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(tournament.status)}`}>
                        {tournament.status}
                      </span>
                    </div>
                    <div className="text-3xl">
                      {getFormatIcon(tournament.format)}
                    </div>
                  </div>

                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex justify-between">
                      <span>Format:</span>
                      <span className="font-medium text-gray-900">
                        {tournament.format.replace('_', ' ')}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Players:</span>
                      <span className="font-medium text-gray-900">
                        {tournament.participants.length}/{tournament.max_participants}
                      </span>
                    </div>
                    {tournament.status === 'active' && (
                      <div className="flex justify-between">
                        <span>Round:</span>
                        <span className="font-medium text-gray-900">
                          {tournament.current_round}/{tournament.total_rounds}
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-500">
                        {new Date(tournament.created_at).toLocaleDateString()}
                      </span>
                      <button className="text-blue-500 hover:text-blue-700 font-medium text-sm">
                        View Details →
                      </button>
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        )}

        {filteredTournaments.length === 0 && !loading && (
          <div className="text-center py-12">
            <p className="text-gray-600">No {filter !== 'all' ? filter : ''} tournaments found.</p>
          </div>
        )}

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-12 text-center"
        >
          <button className="btn-primary">
            Create New Tournament
          </button>
        </motion.div>
      </div>
    </div>
  )
}

export default TournamentList