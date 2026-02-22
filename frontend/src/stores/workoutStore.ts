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
    videoTitle?: string
    muscleGroup: string
    difficulty: string
    caloriesBurn: number
    completed?: boolean
}

interface DayWorkout {
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
    completedWorkouts: Record<number, boolean>
    completedExercises: Record<string, boolean>
    isLoading: boolean
    error: string | null

    // Actions
    fetchPlans: () => Promise<void>
    fetchPlanDetails: (planId: string) => Promise<void>
    generatePlan: (preferences: any) => Promise<void>
    setCurrentPlan: (plan: WorkoutPlan | null) => void
    setActiveWorkout: (workout: DayWorkout | null) => void
    setCurrentExercise: (exercise: Exercise | null) => void
    completeExercise: (exerciseId: string) => void
    completeWorkout: (dayNumber: number) => void
    clearError: () => void
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

            // Fetch all plans
            fetchPlans: async () => {
                set({ isLoading: true, error: null })
                try {
                    const response = await workoutApi.getPlans()
                    console.log('✅ Fetched plans:', response.data)

                    const plans = response.data.map((plan: any) => ({
                        id: plan.id,
                        title: plan.title,
                        description: plan.description,
                        duration: plan.duration || 4,
                        difficulty: plan.difficulty || 'beginner',
                        weeklySchedule: plan.weeklySchedule || [],
                        createdAt: plan.created_at || new Date().toISOString()
                    }))

                    set({
                        plans,
                        currentPlan: plans[0] || null,
                        isLoading: false
                    })

                    // Fetch details for the current plan if needed
                    if (plans[0] && (!plans[0].weeklySchedule || plans[0].weeklySchedule.length === 0)) {
                        console.log('Fetching details for plan:', plans[0].id)
                        await get().fetchPlanDetails(plans[0].id)
                    }
                } catch (error: any) {
                    console.error('❌ Fetch plans error:', error)
                    set({
                        error: error.response?.data?.detail || 'Failed to fetch plans',
                        isLoading: false
                    })
                }
            },

            // Fetch detailed plan with exercises
            fetchPlanDetails: async (planId: string) => {
                set({ isLoading: true, error: null })
                try {
                    const response = await workoutApi.getPlan(planId)
                    console.log('✅ Fetched plan details:', response.data)

                    set((state) => {
                        const updatedPlans = state.plans.map(plan =>
                            plan.id === planId
                                ? { ...plan, ...response.data }
                                : plan
                        )

                        return {
                            plans: updatedPlans,
                            currentPlan: updatedPlans.find(p => p.id === planId) || state.currentPlan,
                            isLoading: false
                        }
                    })
                } catch (error: any) {
                    console.error('❌ Fetch plan details error:', error)
                    set({
                        error: error.response?.data?.detail || 'Failed to fetch plan details',
                        isLoading: false
                    })
                }
            },

            // Generate new workout plan
            generatePlan: async (preferences) => {
                set({ isLoading: true, error: null })
                try {
                    const response = await workoutApi.generatePlan(preferences)
                    console.log('✅ Generated plan response:', response.data)

                    await get().fetchPlans()
                    set({ isLoading: false })
                    return response.data
                } catch (error: any) {
                    console.error('❌ Generate plan error:', error)
                    set({
                        error: error.response?.data?.detail || 'Failed to generate plan',
                        isLoading: false
                    })
                    throw error
                }
            },

            // Set current plan
            setCurrentPlan: (plan) => {
                set({ currentPlan: plan })
                if (plan && (!plan.weeklySchedule || plan.weeklySchedule.length === 0)) {
                    get().fetchPlanDetails(plan.id)
                }
            },

            // Set active workout (current day being viewed)
            setActiveWorkout: (workout) => set({ activeWorkout: workout }),

            // Set current exercise being performed
            setCurrentExercise: (exercise) => set({ currentExercise: exercise }),

            // Mark an exercise as complete
            completeExercise: (exerciseId) => {
                set((state) => ({
                    completedExercises: {
                        ...state.completedExercises,
                        [exerciseId]: true
                    }
                }))

                // Also update the exercise in the current plan if it exists
                set((state) => {
                    if (!state.currentPlan) return state

                    const updatedWeeklySchedule = state.currentPlan.weeklySchedule.map(day => ({
                        ...day,
                        exercises: day.exercises.map(ex =>
                            ex.id === exerciseId ? { ...ex, completed: true } : ex
                        )
                    }))

                    return {
                        currentPlan: {
                            ...state.currentPlan,
                            weeklySchedule: updatedWeeklySchedule
                        }
                    }
                })
            },

            // Mark an entire workout day as complete
            completeWorkout: (dayNumber) => {
                set((state) => ({
                    completedWorkouts: {
                        ...state.completedWorkouts,
                        [dayNumber]: true
                    }
                }))

                // Also mark all exercises in that day as complete
                set((state) => {
                    if (!state.currentPlan) return state

                    const targetDay = state.currentPlan.weeklySchedule.find(d => d.dayNumber === dayNumber)
                    if (!targetDay) return state

                    const exerciseIds = targetDay.exercises.map(ex => ex.id)
                    const newCompletedExercises = { ...state.completedExercises }
                    exerciseIds.forEach(id => { newCompletedExercises[id] = true })

                    return {
                        completedExercises: newCompletedExercises
                    }
                })
            },

            // Clear error
            clearError: () => set({ error: null })
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