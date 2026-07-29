import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AppProvider } from './context/AppContext'
import Navbar from './components/Navbar'
import Landing from './pages/Landing'
import Upload from './pages/Upload'
import Dashboard from './pages/Dashboard'
import Benchmark from './pages/Benchmark'
import Analytics from './pages/Analytics'

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col">
          <Navbar />
          <main className="flex-1">
            <Routes>
              <Route path="/"           element={<Landing />} />
              <Route path="/upload"     element={<Upload />} />
              <Route path="/dashboard"  element={<Dashboard />} />
              <Route path="/benchmark"  element={<Benchmark />} />
              <Route path="/analytics"  element={<Analytics />} />
              <Route path="*"           element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AppProvider>
  )
}
