import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import Dashboard from './pages/dashboard/Dashboard'
import Login from './pages/auth/Login'
import WorkoutPlans from './pages/workouts/WorkoutPlans'
import NutritionPlans from './pages/nutrition/NutritionPlans'
import HealthAssessment from './pages/health-assessment/HealthAssessment'
import ProgressTracking from './pages/progress/ProgressTracking'
import AromiCoach from './pages/aromi/AromiCoach'  // Add this import
import { useAuthStore } from './stores/authStore'

// Create a client
const queryClient = new QueryClient()

// Protected Route wrapper
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? children : <Navigate to="/login" />
}

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <QueryClientProvider client={queryClient}>
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />

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
            {/* Add this missing route */}
            <Route
              path="/aromi"
              element={
                <ProtectedRoute>
                  <AromiCoach />
                </ProtectedRoute>
              }
            />
          </Routes>

          {/* AROMI Coach Floating Button - This will be handled by the AromiCoach component itself */}
        </div>
      </Router>
      <Toaster position="top-right" />
    </QueryClientProvider>
  )
}

export default App