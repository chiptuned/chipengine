import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { apiClient } from '../lib/api'

interface StatCardProps {
  label: string
  value: string
  icon: string
  delay?: number
}

const StatCard: React.FC<StatCardProps> = ({ label, value, icon, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay }}
    className="text-center"
  >
    <div className="text-3xl sm:text-4xl mb-2">{icon}</div>
    <div className="text-xl sm:text-2xl font-bold gradient-text mb-1">{value}</div>
    <div className="text-sm text-gray-600">{label}</div>
  </motion.div>
)

interface FeatureCardProps {
  title: string
  description: string
  icon: string
  delay?: number
}

const FeatureCard: React.FC<FeatureCardProps> = ({ title, description, icon, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay }}
    className="glass-card text-center hover:glow-effect transition-all duration-300"
  >
    <div className="text-4xl sm:text-5xl mb-4">{icon}</div>
    <h3 className="text-lg sm:text-xl font-bold mb-3 text-gray-900">{title}</h3>
    <p className="text-gray-600 text-sm sm:text-base leading-relaxed">{description}</p>
  </motion.div>
)

const LandingPage: React.FC = () => {
  const [health, setHealth] = useState<any>(null)
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [healthData, statsData] = await Promise.all([
          apiClient.healthCheck(),
          apiClient.getStats().catch(() => ({ active_games: 0, finished_games: 0 }))
        ])
        setHealth(healthData)
        setStats(statsData)
      } catch (error) {
        console.error('Failed to fetch data:', error)
      }
    }

    fetchData()
  }, [])

  const features = [
    {
      icon: '⚡',
      title: 'Ultra Fast',
      description: 'Process millions of games per second with optimized algorithms and minimal overhead.'
    },
    {
      icon: '🎯',
      title: 'Bot Ready',
      description: 'Perfect platform for AI competitions, bot tournaments, and strategy testing.'
    },
    {
      icon: '📊',
      title: 'Real-time Analytics',
      description: 'Monitor performance, track metrics, and analyze results in real-time.'
    },
    {
      icon: '🔧',
      title: 'Developer Friendly',
      description: 'Clean APIs, comprehensive docs, and easy integration for your projects.'
    },
    {
      icon: '🎮',
      title: 'Multi-Game Support',
      description: 'Start with Rock Paper Scissors, expand to Poker, and add custom games.'
    },
    {
      icon: '🌐',
      title: 'Cloud Ready',
      description: 'Deploy anywhere with Docker support and horizontal scaling capabilities.'
    }
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="container mx-auto px-4 py-16 sm:py-24 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
              <span className="gradient-text">ChipEngine</span>
              <br />
              <span className="text-gray-700">Game Engine</span>
            </h1>
            
            <p className="text-lg sm:text-xl lg:text-2xl text-gray-600 max-w-4xl mx-auto mb-8 leading-relaxed">
              Fast, lean, and powerful game engine designed for bot competitions and high-performance gaming.
              <br className="hidden sm:block" />
              <span className="font-semibold">Built for speed. Made for developers.</span>
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4 justify-center mb-12"
          >
            <Link to="/rps" className="btn-primary text-lg px-8 py-4">
              🎮 Try Demo Game
            </Link>
            <Link to="/tournaments" className="btn-secondary text-lg px-8 py-4">
              🏆 View Tournaments
            </Link>
          </motion.div>

          {/* Live Stats */}
          {health && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="glass-card max-w-2xl mx-auto"
            >
              <h3 className="text-lg font-semibold mb-4 text-gray-900">🔴 Live Engine Status</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
                <StatCard 
                  icon="✅" 
                  label="Engine Status" 
                  value={health.status === 'healthy' ? 'Online' : 'Offline'} 
                  delay={0.6}
                />
                <StatCard 
                  icon="🎮" 
                  label="Active Games" 
                  value={stats?.active_games?.toString() || '0'} 
                  delay={0.7}
                />
                <StatCard 
                  icon="🏁" 
                  label="Completed" 
                  value={stats?.finished_games?.toString() || '0'} 
                  delay={0.8}
                />
                <StatCard 
                  icon="⚡" 
                  label="Version" 
                  value={health.version} 
                  delay={0.9}
                />
              </div>
            </motion.div>
          )}
        </div>

        {/* Floating Background Elements */}
        <div className="absolute top-20 left-10 w-32 h-32 bg-blue-200 rounded-full opacity-20 floating-animation" />
        <div className="absolute bottom-20 right-10 w-24 h-24 bg-purple-200 rounded-full opacity-20 floating-animation" style={{ animationDelay: '2s' }} />
        <div className="absolute top-1/2 right-20 w-16 h-16 bg-green-200 rounded-full opacity-20 floating-animation" style={{ animationDelay: '4s' }} />
      </section>

      {/* Features Section */}
      <section className="py-16 sm:py-24">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.0 }}
            className="text-center mb-12 sm:mb-16"
          >
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-6 text-gray-900">
              Why Choose <span className="gradient-text">ChipEngine</span>?
            </h2>
            <p className="text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto">
              Engineered for performance, built for scale, designed for developers who demand the best.
            </p>
          </motion.div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8 max-w-7xl mx-auto">
            {features.map((feature, index) => (
              <FeatureCard
                key={feature.title}
                {...feature}
                delay={1.1 + index * 0.1}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Performance Section */}
      <section className="py-16 sm:py-24 bg-gradient-to-r from-gray-50 to-blue-50">
        <div className="container mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.7 }}
          >
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-6 text-gray-900">
              <span className="gradient-text">Blazing Fast</span> Performance
            </h2>
            <p className="text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto mb-12">
              Don't just take our word for it. Test the limits yourself.
            </p>

            <div className="grid sm:grid-cols-3 gap-8 max-w-4xl mx-auto mb-12">
              <div className="glass-card">
                <div className="text-3xl sm:text-4xl font-bold gradient-text mb-2">15M+</div>
                <div className="text-gray-600">Games per second</div>
              </div>
              <div className="glass-card">
                <div className="text-3xl sm:text-4xl font-bold gradient-text mb-2">&lt;1ms</div>
                <div className="text-gray-600">Average latency</div>
              </div>
              <div className="glass-card">
                <div className="text-3xl sm:text-4xl font-bold gradient-text mb-2">99.9%</div>
                <div className="text-gray-600">Uptime</div>
              </div>
            </div>

            <Link to="/stress-test" className="btn-primary text-lg px-8 py-4 glow-effect">
              🚀 Test Performance Now
            </Link>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 sm:py-24">
        <div className="container mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 2.0 }}
            className="max-w-3xl mx-auto"
          >
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-6 text-gray-900">
              Ready to <span className="gradient-text">Get Started</span>?
            </h2>
            <p className="text-lg sm:text-xl text-gray-600 mb-8">
              Jump in and experience the power of ChipEngine. Start with a simple game or push the limits with stress testing.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/rps" className="btn-primary text-lg px-8 py-4">
                🎮 Play Rock Paper Scissors
              </Link>
              <Link to="/tournaments" className="btn-secondary text-lg px-8 py-4">
                🏆 Join Tournaments
              </Link>
              <Link to="/stress-test" className="btn-secondary text-lg px-8 py-4">
                ⚡ Run Performance Test
              </Link>
            </div>

            <p className="text-sm text-gray-500 mt-6">
              Open source • MIT License • Built with ❤️
            </p>
          </motion.div>
        </div>
      </section>
    </div>
  )
}

export default LandingPage