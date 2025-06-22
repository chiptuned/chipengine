import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import RockPaperScissors from './games/rps/RockPaperScissors'
import GameSelection from './components/GameSelection'
import StressTest from './components/StressTest'
import LandingPage from './components/LandingPage'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/games" element={<GameSelection />} />
        <Route path="/rps" element={<RockPaperScissors />} />
        <Route path="/stress-test" element={<StressTest />} />
      </Routes>
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: 'white',
            color: '#374151',
            border: '1px solid #e5e7eb',
            borderRadius: '12px',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
          },
        }}
      />
    </div>
  )
}

export default App