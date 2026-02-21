import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { progressApi } from '../services/api'

interface ProgressData {
    date: string
    weight?: number
    calories?: number
    workouts?: number
    water?: number
    sleep?: number
    mood?: number
}

interface Achievement {
    id: string
    name: string
    description: string
    icon: string
    achievedAt: string
    category: 'workout' | 'nutrition' | 'streak' | 'milestone'
}

interface BodyMetrics {
    bmi?: number
    bodyFatPercent?: number
    muscleMass?: number
    waistCircumference?: number
    age?: number
    gender?: string
    height?: number
    weight?: number
    timestamp?: string
}

interface ProgressStats {
    currentStreak: number
    totalWorkouts: number
    totalCaloriesBurned: number
    avgWorkoutDuration: number
    completionRate: number
    weightChange: number
    startDate: string
    lastWorkout: string
}

interface ProgressState {
    // State
    stats: ProgressStats | null
    history: ProgressData[]
    achievements: Achievement[]
    bodyMetrics: BodyMetrics | null
    isLoading: boolean
    error: string | null

    // Actions
    fetchStats: () => Promise<void>
    fetchHistory: (period: string) => Promise<void>
    fetchAchievements: () => Promise<void>
    updateBodyMetrics: (metrics: BodyMetrics) => void
    trackWorkout: (data: any) => Promise<void>
    clearError: () => void
}

export const useProgressStore = create<ProgressState>()(
    persist(
        (set, get) => ({
            // Initial state
            stats: null,
            history: [],
            achievements: [],
            bodyMetrics: null,
            isLoading: false,
            error: null,

            // Fetch progress stats
            fetchStats: async () => {
                set({ isLoading: true, error: null })
                try {
                    const response = await progressApi.getStats()
                    set({ stats: response.data, isLoading: false })
                } catch (error: any) {
                    set({
                        error: error.response?.data?.detail || 'Failed to fetch stats',
                        isLoading: false
                    })
                }
            },

            // Fetch progress history
            fetchHistory: async (period) => {
                set({ isLoading: true, error: null })
                try {
                    const response = await progressApi.getHistory(period)
                    set({ history: response.data, isLoading: false })
                } catch (error: any) {
                    set({
                        error: error.response?.data?.detail || 'Failed to fetch history',
                        isLoading: false
                    })
                }
            },

            // Fetch achievements
            fetchAchievements: async () => {
                set({ isLoading: true, error: null })
                try {
                    const response = await progressApi.getAchievements()
                    set({ achievements: response.data, isLoading: false })
                } catch (error: any) {
                    set({
                        error: error.response?.data?.detail || 'Failed to fetch achievements',
                        isLoading: false
                    })
                }
            },

            // Update body metrics
            updateBodyMetrics: (metrics) => {
                set({
                    bodyMetrics: {
                        ...metrics,
                        timestamp: new Date().toISOString()
                    }
                })
            },

            // Track a workout
            trackWorkout: async (data) => {
                set({ isLoading: true, error: null })
                try {
                    await progressApi.trackWorkout(data)
                    // Refresh stats after tracking
                    await get().fetchStats()
                    await get().fetchHistory('month')
                } catch (error: any) {
                    set({
                        error: error.response?.data?.detail || 'Failed to track workout',
                        isLoading: false
                    })
                }
            },

            // Clear error
            clearError: () => set({ error: null })
        }),
        {
            name: 'progress-storage',
            storage: localStorage,
            partialize: (state) => ({
                bodyMetrics: state.bodyMetrics
            })
        }
    )
)