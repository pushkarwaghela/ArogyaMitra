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
    videoUrl?: string
    muscleGroup: string
    difficulty: string
    caloriesBurn: number
    completed?: boolean
}

interface DayWorkout {
    day: string
    dayNumber: number
    focus: string
    exercises: Exercise[]
    totalDuration: number
    totalCalories: number
    isRestDay?: boolean
    completed?: boolean
}

interface WorkoutPlan {
    id: string
    title: string
    description: string
    duration: number
    difficulty: string
    weeklySchedule: DayWorkout[]
    createdAt: string
}

interface WorkoutState {
    // State
    plans: WorkoutPlan[]
    currentPlan: WorkoutPlan | null
    activeWorkout: DayWorkout | null
    currentExercise: Exercise | null
    completedWorkouts: Record<string, boolean>
    completedExercises: Record<string, boolean>
    isLoading: boolean
    error: string | null

    // Actions
    fetchPlans: () => Promise<void>
    setCurrentPlan: (plan: WorkoutPlan | null) => void
    setActiveWorkout: (workout: DayWorkout | null) => void
    setCurrentExercise: (exercise: Exercise | null) => void
    completeExercise: (exerciseId: string) => void
    completeWorkout: (dayNumber: number) => void
    generatePlan: (preferences: any) => Promise<void>
    clearError: () => void
    resetProgress: () => void
}

export const useWorkoutStore = create<WorkoutState>()(
    persist(
        (set, get) => ({
            // Initial state
            plans: [],
            currentPlan: null,
            activeWorkout: null,
            currentExercise: null,
            completedWorkouts: {},
            completedExercises: {},
            isLoading: false,
            error: null,

            // Fetch workout plans
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

            // Set current plan
            setCurrentPlan: (plan) => set({ currentPlan: plan }),

            // Set active workout
            setActiveWorkout: (workout) => set({ activeWorkout: workout }),

            // Set current exercise
            setCurrentExercise: (exercise) => set({ currentExercise: exercise }),

            // Complete an exercise
            completeExercise: (exerciseId) => {
                set((state) => ({
                    completedExercises: {
                        ...state.completedExercises,
                        [exerciseId]: true
                    }
                }))
            },

            // Complete a workout day
            completeWorkout: (dayNumber) => {
                set((state) => ({
                    completedWorkouts: {
                        ...state.completedWorkouts,
                        [dayNumber]: true
                    }
                }))
            },

            // Generate new workout plan
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

            // Clear error
            clearError: () => set({ error: null }),

            // Reset progress
            resetProgress: () => set({
                completedWorkouts: {},
                completedExercises: {}
            })
        }),
        {
            name: 'workout-storage',
            storage: localStorage,
            partialize: (state) => ({
                completedWorkouts: state.completedWorkouts,
                completedExercises: state.completedExercises
            })
        }
    )
)