import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { workoutApi } from '../services/api'

interface Exercise {
    id: string
    name: string
    sets: number
    reps: number
    duration?: number
    restTime: number
    muscleGroup: string
    difficulty: string
    caloriesBurn: number
}

interface WorkoutPlan {
    id: string
    title: string
    description: string
    workout_type: string
    difficulty: string
    duration_weeks: number
    sessions_per_week: number
    session_duration: number
    is_active: boolean
    created_at: string
}

interface WorkoutState {
    plans: WorkoutPlan[]
    currentPlan: WorkoutPlan | null
    isLoading: boolean
    error: string | null
    fetchPlans: () => Promise<void>
    generatePlan: (preferences: any) => Promise<void>
    clearError: () => void
}

export const useWorkoutStore = create<WorkoutState>()(
    persist(
        (set, get) => ({
            plans: [],
            currentPlan: null,
            isLoading: false,
            error: null,

            fetchPlans: async () => {
                set({ isLoading: true, error: null })
                try {
                    const response = await workoutApi.getPlans()
                    set({
                        plans: response.data,
                        currentPlan: response.data[0] || null,
                        isLoading: false
                    })
                } catch (error: any) {
                    set({
                        error: error.response?.data?.detail || 'Failed to fetch plans',
                        isLoading: false
                    })
                }
            },

            generatePlan: async (preferences) => {
                set({ isLoading: true, error: null })
                try {
                    const response = await workoutApi.generatePlan(preferences)
                    set((state) => ({
                        plans: [response.data, ...state.plans],
                        currentPlan: response.data,
                        isLoading: false
                    }))
                } catch (error: any) {
                    set({
                        error: error.response?.data?.detail || 'Failed to generate plan',
                        isLoading: false
                    })
                }
            },

            clearError: () => set({ error: null })
        }),
        {
            name: 'workout-storage',
            storage: localStorage
        }
    )
)