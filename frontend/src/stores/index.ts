export { useAuthStore } from './TSAuthStore'
export { useWorkoutStore } from './workoutStore'
export { useNutritionStore } from './nutritionStore'
export { useProgressStore } from './progressStore'
export { useChatStore } from './chatStore'

// Optional: Create a combined store for easy access
import { useAuthStore } from './TSAuthStore'
import { useWorkoutStore } from './workoutStore'
import { useNutritionStore } from './nutritionStore'
import { useProgressStore } from './progressStore'
import { useChatStore } from './chatStore'

export const useStore = () => ({
    auth: useAuthStore(),
    workout: useWorkoutStore(),
    nutrition: useNutritionStore(),
    progress: useProgressStore(),
    chat: useChatStore()
})