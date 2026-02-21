import React, { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import Dashboard from './pages/dashboard/Dashboard'
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import WorkoutPlans from './pages/workouts/WorkoutPlans'
import NutritionPlans from './pages/nutrition/NutritionPlans'
import HealthAssessment from './pages/health-assessment/HealthAssessment'
import ProgressTracking from './pages/progress/ProgressTracking'
import AromiCoach from './pages/aromi/AromiCoach'
import Profile from './pages/profile/Profile'
import { useAuthStore } from './stores/authStore'

// Create a client
const queryClient = new QueryClient()

// Loading component
const LoadingScreen = () => (
  <div className="min-h-screen flex items-center justify-center">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
  </div>
)

// Protected Route wrapper
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading, isHydrated } = useAuthStore()

  // Wait for hydration to complete
  if (!isHydrated || isLoading) {
    return <LoadingScreen />
  }

  return isAuthenticated ? children : <Navigate to="/login" />
}

function App() {
  const { checkAuth, isHydrated } = useAuthStore()
  const [initialCheckDone, setInitialCheckDone] = useState(false)

  useEffect(() => {
    const verifyAuth = async () => {
      await checkAuth()
      setInitialCheckDone(true)
    }

    verifyAuth()
  }, [checkAuth])

  // Don't render anything until initial check is done and store is hydrated
  if (!initialCheckDone || !isHydrated) {
    return <LoadingScreen />
  }

  return (
    <QueryClientProvider client={queryClient}>
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected Routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              }
            />
            <Route
              path="/workouts"
              element={
                <ProtectedRoute>
                  <WorkoutPlans />
                </ProtectedRoute>
              }
            />
            <Route
              path="/nutrition"
              element={
                <ProtectedRoute>
                  <NutritionPlans />
                </ProtectedRoute>
              }
            />
            <Route
              path="/health-assessment"
              element={
                <ProtectedRoute>
                  <HealthAssessment />
                </ProtectedRoute>
              }
            />
            <Route
              path="/progress"
              element={
                <ProtectedRoute>
                  <ProgressTracking />
                </ProtectedRoute>
              }
            />
            <Route
              path="/aromi"
              element={
                <ProtectedRoute>
                  <AromiCoach />
                </ProtectedRoute>
              }
            />
          </Routes>
        </div>
      </Router>
      <Toaster position="top-right" />
    </QueryClientProvider>
  )
}

export default App