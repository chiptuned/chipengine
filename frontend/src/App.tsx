import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import RockPaperScissors from './games/rps/RockPaperScissors'
import GameSelection from './components/GameSelection'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/" element={<GameSelection />} />
        <Route path="/rps" element={<RockPaperScissors />} />
      </Routes>
      <Toaster />
    </div>
  )
}

export default App