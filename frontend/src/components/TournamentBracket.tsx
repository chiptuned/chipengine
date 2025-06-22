import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Tournament, TournamentMatch, TournamentBracket as TournamentBracketType } from '../types/game'

const TournamentBracket: React.FC = () => {
  const { tournamentId } = useParams<{ tournamentId: string }>()
  const [bracket, setBracket] = useState<TournamentBracketType | null>(null)
  const [loading, setLoading] = useState(true)
  const [view, setView] = useState<'bracket' | 'standings'>('bracket')

  useEffect(() => {
    // Mock data for demo purposes
    const mockBracket: TournamentBracketType = {
      tournament: {
        tournament_id: tournamentId || '1',
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
      matches: [
        // Round 1
        { match_id: '1-1', tournament_id: tournamentId || '1', round: 1, position: 0, player1: 'Alice', player2: 'Bob', winner: 'Alice', status: 'completed', score: { player1: 2, player2: 1 } },
        { match_id: '1-2', tournament_id: tournamentId || '1', round: 1, position: 1, player1: 'Charlie', player2: 'David', winner: 'Charlie', status: 'completed', score: { player1: 2, player2: 0 } },
        { match_id: '1-3', tournament_id: tournamentId || '1', round: 1, position: 2, player1: 'Eve', player2: 'Frank', winner: 'Frank', status: 'completed', score: { player1: 1, player2: 2 } },
        { match_id: '1-4', tournament_id: tournamentId || '1', round: 1, position: 3, player1: 'Grace', player2: 'Henry', winner: 'Grace', status: 'completed', score: { player1: 2, player2: 1 } },
        // Round 2
        { match_id: '2-1', tournament_id: tournamentId || '1', round: 2, position: 0, player1: 'Alice', player2: 'Charlie', winner: 'Alice', status: 'completed', score: { player1: 2, player2: 1 } },
        { match_id: '2-2', tournament_id: tournamentId || '1', round: 2, position: 1, player1: 'Frank', player2: 'Grace', winner: null, status: 'active', score: { player1: 1, player2: 1 } },
        // Round 3 (Finals)
        { match_id: '3-1', tournament_id: tournamentId || '1', round: 3, position: 0, player1: 'Alice', player2: null, winner: null, status: 'pending' },
      ],
      standings: [
        { player: 'Alice', position: 1, wins: 2, losses: 0 },
        { player: 'Charlie', position: 2, wins: 1, losses: 1 },
        { player: 'Frank', position: 3, wins: 1, losses: 0 },
        { player: 'Grace', position: 3, wins: 1, losses: 0 },
        { player: 'Bob', position: 5, wins: 0, losses: 1 },
        { player: 'David', position: 5, wins: 0, losses: 1 },
        { player: 'Eve', position: 5, wins: 0, losses: 1 },
        { player: 'Henry', position: 5, wins: 0, losses: 1 },
      ]
    }

    setTimeout(() => {
      setBracket(mockBracket)
      setLoading(false)
    }, 500)
  }, [tournamentId])

  const getMatchesByRound = (round: number) => {
    return bracket?.matches.filter(m => m.round === round) || []
  }

  const getMatchStatusColor = (status: TournamentMatch['status']) => {
    switch (status) {
      case 'active':
        return 'border-green-500 bg-green-50'
      case 'completed':
        return 'border-gray-300 bg-gray-50'
      case 'pending':
        return 'border-gray-200 bg-white'
      default:
        return 'border-gray-200 bg-white'
    }
  }

  const renderMatch = (match: TournamentMatch) => {
    const isWinner1 = match.winner === match.player1
    const isWinner2 = match.winner === match.player2

    return (
      <motion.div
        key={match.match_id}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className={`border-2 rounded-lg p-4 mb-4 ${getMatchStatusColor(match.status)}`}
      >
        <div className="text-xs text-gray-500 mb-2">
          Match {match.position + 1}
          {match.status === 'active' && (
            <span className="ml-2 text-green-600 font-medium">LIVE</span>
          )}
        </div>
        
        <div className="space-y-2">
          <div className={`flex justify-between items-center p-2 rounded ${isWinner1 ? 'bg-green-100 font-bold' : ''}`}>
            <span>{match.player1 || 'TBD'}</span>
            {match.score && <span>{match.score.player1}</span>}
          </div>
          
          <div className={`flex justify-between items-center p-2 rounded ${isWinner2 ? 'bg-green-100 font-bold' : ''}`}>
            <span>{match.player2 || 'TBD'}</span>
            {match.score && <span>{match.score.player2}</span>}
          </div>
        </div>

        {match.game_id && match.status === 'active' && (
          <Link 
            to={`/rps?gameId=${match.game_id}`}
            className="mt-3 block text-center text-sm text-blue-500 hover:text-blue-700"
          >
            Watch Live →
          </Link>
        )}
      </motion.div>
    )
  }

  const renderBracketView = () => {
    if (!bracket) return null

    const rounds = Array.from({ length: bracket.tournament.total_rounds }, (_, i) => i + 1)
    
    return (
      <div className="overflow-x-auto">
        <div className="flex space-x-8 min-w-max p-4">
          {rounds.map(round => (
            <div key={round} className="flex-1 min-w-[250px]">
              <h3 className="text-lg font-bold mb-4 text-center">
                {round === bracket.tournament.total_rounds ? 'Finals' : `Round ${round}`}
              </h3>
              <div className="space-y-8">
                {getMatchesByRound(round).map(match => renderMatch(match))}
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const renderStandingsView = () => {
    if (!bracket?.standings) return null

    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Position
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Player
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Wins
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Losses
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {bracket.standings.map((standing, index) => (
                <motion.tr
                  key={standing.player}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {standing.position <= 3 && (
                        <span className="text-xl mr-2">
                          {standing.position === 1 && '🥇'}
                          {standing.position === 2 && '🥈'}
                          {standing.position === 3 && '🥉'}
                        </span>
                      )}
                      <span className="text-sm font-medium text-gray-900">
                        #{standing.position}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {standing.player}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    <span className="text-sm text-green-600 font-medium">
                      {standing.wins}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    <span className="text-sm text-red-600 font-medium">
                      {standing.losses}
                    </span>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <p className="text-gray-600 mt-4">Loading tournament...</p>
        </div>
      </div>
    )
  }

  if (!bracket) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Tournament not found</p>
          <Link to="/tournaments" className="mt-4 inline-block text-blue-500 hover:text-blue-700">
            Back to Tournaments
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen">
      <div className="container mx-auto px-4 py-8">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-4xl font-bold gradient-text mb-2">
                {bracket.tournament.name}
              </h1>
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <span className={`px-3 py-1 rounded-full font-medium ${
                  bracket.tournament.status === 'active' ? 'bg-green-100 text-green-800' :
                  bracket.tournament.status === 'completed' ? 'bg-gray-100 text-gray-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {bracket.tournament.status}
                </span>
                <span>Round {bracket.tournament.current_round} of {bracket.tournament.total_rounds}</span>
                <span>{bracket.tournament.participants.length} Players</span>
              </div>
            </div>
            <Link to="/tournaments" className="btn-secondary">
              Back to Tournaments
            </Link>
          </div>

          <div className="flex space-x-2 mb-6">
            <button
              onClick={() => setView('bracket')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                view === 'bracket'
                  ? 'bg-blue-500 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              Bracket View
            </button>
            <button
              onClick={() => setView('standings')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                view === 'standings'
                  ? 'bg-blue-500 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              Standings
            </button>
          </div>
        </motion.div>

        <div className="glass-card">
          {view === 'bracket' ? renderBracketView() : renderStandingsView()}
        </div>

        {bracket.tournament.status === 'active' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="mt-8 text-center"
          >
            <p className="text-sm text-gray-600 mb-2">
              Tournament is live! Refresh to see updates.
            </p>
            <button 
              onClick={() => window.location.reload()} 
              className="text-blue-500 hover:text-blue-700 font-medium"
            >
              Refresh Page
            </button>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default TournamentBracket