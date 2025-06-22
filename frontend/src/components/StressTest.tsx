import React, { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import { apiClient } from '../lib/api'
import type { StressTestRequest, StressTestStatus, StressTestMetrics } from '../types/game'

interface MetricCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: string
  color?: 'blue' | 'green' | 'red' | 'yellow' | 'purple'
  trend?: 'up' | 'down' | 'stable'
}

const MetricCard: React.FC<MetricCardProps> = ({ 
  title, 
  value, 
  subtitle, 
  icon, 
  color = 'blue',
  trend 
}) => {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    red: 'from-red-500 to-red-600',
    yellow: 'from-yellow-500 to-yellow-600',
    purple: 'from-purple-500 to-purple-600'
  }

  const trendIcons = {
    up: '↗️',
    down: '↘️',
    stable: '→'
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-card relative overflow-hidden"
    >
      <div className={`absolute top-0 right-0 w-20 h-20 bg-gradient-to-br ${colorClasses[color]} opacity-10 rounded-full -mr-10 -mt-10`} />
      
      <div className="relative">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-600">{title}</span>
          <span className="text-xl">{icon}</span>
        </div>
        
        <div className="flex items-end gap-2">
          <span className="text-2xl sm:text-3xl font-bold text-gray-900">{value}</span>
          {trend && (
            <span className="text-sm text-gray-500 mb-1">
              {trendIcons[trend]}
            </span>
          )}
        </div>
        
        {subtitle && (
          <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
        )}
      </div>
    </motion.div>
  )
}

const StressTest: React.FC = () => {
  const [config, setConfig] = useState<StressTestRequest>({
    game_type: 'rps',
    concurrent_games: 100,
    games_per_second: 50,
    duration_seconds: 60
  })
  
  const [currentTest, setCurrentTest] = useState<StressTestStatus | null>(null)
  const [metrics, setMetrics] = useState<StressTestMetrics | null>(null)
  const [isRunning, setIsRunning] = useState(false)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  // Real-time updates
  useEffect(() => {
    if (currentTest?.status === 'running') {
      intervalRef.current = setInterval(async () => {
        try {
          const [status, metricsData] = await Promise.all([
            apiClient.getStressTestStatus(currentTest.test_id),
            apiClient.getStressTestMetrics(currentTest.test_id)
          ])
          
          setCurrentTest(status)
          setMetrics(metricsData)
          
          if (status.status !== 'running') {
            setIsRunning(false)
            if (intervalRef.current) {
              clearInterval(intervalRef.current)
              intervalRef.current = null
            }
          }
        } catch (error) {
          console.error('Failed to fetch test data:', error)
        }
      }, 1000)
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [currentTest?.test_id, currentTest?.status])

  const startTest = async () => {
    try {
      setIsRunning(true)
      const response = await apiClient.startStressTest(config)
      
      // Get initial status
      const status = await apiClient.getStressTestStatus(response.test_id)
      setCurrentTest(status)
      
      toast.success('Stress test started! 🚀')
    } catch (error) {
      setIsRunning(false)
      toast.error(`Failed to start test: ${error}`)
    }
  }

  const stopTest = async () => {
    if (!currentTest) return
    
    try {
      await apiClient.stopStressTest(currentTest.test_id)
      setIsRunning(false)
      toast.success('Stress test stopped')
    } catch (error) {
      toast.error(`Failed to stop test: ${error}`)
    }
  }

  const resetTest = () => {
    setCurrentTest(null)
    setMetrics(null)
    setIsRunning(false)
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }

  const formatNumber = (num: number, decimals = 0) => {
    return new Intl.NumberFormat('en-US', { 
      maximumFractionDigits: decimals,
      minimumFractionDigits: decimals 
    }).format(num)
  }

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="min-h-screen">
      <div className="container mx-auto px-4 py-6 sm:py-8">
        {/* Header */}
        <div className="text-center mb-6 sm:mb-8">
          <Link to="/games" className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-4 transition-colors duration-200">
            ← Back to Games
          </Link>
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-2">
            <span className="gradient-text">⚡ Stress Test</span>
          </h1>
          <p className="text-gray-600 text-sm sm:text-base">
            Test your game engine's performance under load
          </p>
        </div>

        {/* Configuration Panel */}
        {!currentTest && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-2xl mx-auto mb-8"
          >
            <div className="glass-card">
              <h2 className="text-xl font-bold mb-6 gradient-text">⚙️ Test Configuration</h2>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Games per Second
                  </label>
                  <input
                    type="number"
                    value={config.games_per_second}
                    onChange={(e) => setConfig(prev => ({ 
                      ...prev, 
                      games_per_second: parseInt(e.target.value) || 1 
                    }))}
                    className="input-field"
                    min="1"
                    max="1000"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Duration (seconds)
                  </label>
                  <input
                    type="number"
                    value={config.duration_seconds}
                    onChange={(e) => setConfig(prev => ({ 
                      ...prev, 
                      duration_seconds: parseInt(e.target.value) || 1 
                    }))}
                    className="input-field"
                    min="1"
                    max="3600"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Concurrent Games
                  </label>
                  <input
                    type="number"
                    value={config.concurrent_games}
                    onChange={(e) => setConfig(prev => ({ 
                      ...prev, 
                      concurrent_games: parseInt(e.target.value) || 1 
                    }))}
                    className="input-field"
                    min="1"
                    max="10000"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Game Type
                  </label>
                  <select
                    value={config.game_type}
                    onChange={(e) => setConfig(prev => ({ 
                      ...prev, 
                      game_type: e.target.value 
                    }))}
                    className="input-field"
                  >
                    <option value="rps">Rock Paper Scissors</option>
                  </select>
                </div>
              </div>

              <div className="text-center">
                <p className="text-sm text-gray-600 mb-4">
                  Target: <strong>{formatNumber(config.games_per_second * config.duration_seconds)}</strong> total games
                </p>
                
                <button 
                  onClick={startTest}
                  disabled={isRunning}
                  className="btn-primary text-lg px-8 py-3"
                >
                  {isRunning ? 'Starting...' : '🚀 Start Stress Test'}
                </button>
              </div>
            </div>
          </motion.div>
        )}

        {/* Live Test Dashboard */}
        <AnimatePresence>
          {currentTest && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              {/* Status Banner */}
              <div className={`glass-card text-center ${
                currentTest.status === 'running' ? 'glow-effect' : ''
              }`}>
                <div className="flex items-center justify-center gap-2 mb-2">
                  <span className="text-2xl">
                    {currentTest.status === 'running' ? '⚡' : 
                     currentTest.status === 'completed' ? '✅' : 
                     currentTest.status === 'failed' ? '❌' : '⏸️'}
                  </span>
                  <h2 className="text-xl font-bold">
                    Test {currentTest.status.charAt(0).toUpperCase() + currentTest.status.slice(1)}
                  </h2>
                </div>
                
                <p className="text-gray-600">
                  ID: {currentTest.test_id.slice(0, 8)}...
                </p>

                {currentTest.status === 'running' && (
                  <div className="mt-4">
                    <button 
                      onClick={stopTest}
                      className="btn-secondary mr-4"
                    >
                      ⏹️ Stop Test
                    </button>
                  </div>
                )}

                {currentTest.status !== 'running' && (
                  <div className="mt-4">
                    <button 
                      onClick={resetTest}
                      className="btn-primary"
                    >
                      🔄 New Test
                    </button>
                  </div>
                )}
              </div>

              {/* Progress Bar */}
              {metrics && (
                <div className="glass-card">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium">Progress</span>
                    <span className="text-sm text-gray-600">
                      {formatNumber(metrics.timing.progress_percentage, 1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(metrics.timing.progress_percentage, 100)}%` }}
                      transition={{ duration: 0.5 }}
                      className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full"
                    />
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>{formatDuration(metrics.timing.elapsed_seconds)}</span>
                    <span>{formatDuration(metrics.timing.target_duration)}</span>
                  </div>
                </div>
              )}

              {/* Metrics Grid */}
              {metrics && (
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                  <MetricCard
                    title="Games/Second"
                    value={formatNumber(metrics.performance.games_per_second, 1)}
                    subtitle={`Peak: ${formatNumber(metrics.performance.peak_games_per_second, 1)}`}
                    icon="⚡"
                    color="blue"
                    trend="stable"
                  />
                  
                  <MetricCard
                    title="Success Rate"
                    value={`${formatNumber(metrics.performance.success_rate, 1)}%`}
                    icon="✅"
                    color="green"
                  />
                  
                  <MetricCard
                    title="Games Created"
                    value={formatNumber(metrics.counters.games_created)}
                    subtitle={`of ${formatNumber(metrics.counters.total_games_target)}`}
                    icon="🎮"
                    color="purple"
                  />
                  
                  <MetricCard
                    title="Avg Duration"
                    value={`${formatNumber(metrics.performance.average_game_duration_ms, 1)}ms`}
                    icon="⏱️"
                    color="yellow"
                  />
                  
                  <MetricCard
                    title="Completed"
                    value={formatNumber(metrics.counters.games_completed)}
                    icon="🏁"
                    color="green"
                  />
                  
                  <MetricCard
                    title="Failed"
                    value={formatNumber(metrics.counters.games_failed)}
                    icon="❌"
                    color="red"
                  />
                  
                  <MetricCard
                    title="Completion"
                    value={`${formatNumber(metrics.performance.completion_rate, 1)}%`}
                    icon="📊"
                    color="blue"
                  />
                  
                  <MetricCard
                    title="Elapsed"
                    value={formatDuration(metrics.timing.elapsed_seconds)}
                    icon="⏰"
                    color="purple"
                  />
                </div>
              )}

              {/* Errors */}
              {currentTest.errors.length > 0 && (
                <div className="glass-card">
                  <h3 className="text-lg font-semibold mb-4 text-red-600">⚠️ Recent Errors</h3>
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {currentTest.errors.slice(-5).map((error, index) => (
                      <div key={index} className="text-sm bg-red-50 text-red-700 p-2 rounded border-l-4 border-red-400">
                        {error}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

export default StressTest