import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import Dashboard from './pages/dashboard/Dashboard'
import Login from './pages/auth/Login'
import { useAuthStore } from './stores/authStore'

// Create a client
const queryClient = new QueryClient()

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <QueryClientProvider client={queryClient}>
      <Router
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true
        }}
      >
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
          <Routes>
            <Route
              path="/"
              element={
                <div className="flex flex-col items-center justify-center min-h-screen">
                  <h1 className="text-4xl font-bold text-gray-800 mb-4">🚀 ArogyaMitra</h1>
                  <p className="text-xl text-gray-600 mb-8">AI-Driven Workout Planning, Nutrition Guidance, and Health Coaching Platform</p>
                  <div className="bg-white p-8 rounded-lg shadow-lg text-center">
                    <h2 className="text-2xl font-semibold text-green-600 mb-4">Frontend Running Successfully! 🎉</h2>
                    <p className="mb-2">Backend API: <a href="http://localhost:8000" className="text-blue-500 hover:underline">http://localhost:8000</a></p>
                    <p>API Docs: <a href="http://localhost:8000/docs" className="text-blue-500 hover:underline">http://localhost:8000/docs</a></p>
                    <button
                      onClick={() => window.location.href = '/login'}
                      className="mt-6 bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors"
                    >
                      Go to Login
                    </button>
                  </div>
                </div>
              }
            />
            <Route path="/login" element={<Login />} />
            <Route
              path="/dashboard"
              element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />}
            />
          </Routes>
        </div>
      </Router>
      <Toaster position="top-right" />
    </QueryClientProvider>
  )
}

export default App