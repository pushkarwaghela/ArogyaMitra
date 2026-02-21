import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { nutritionApi } from '../services/api'

interface Meal {
    id: string
    name: string
    type: 'breakfast' | 'lunch' | 'dinner' | 'snack'
    calories: number
    protein: number
    carbs: number
    fats: number
    ingredients: string[]
    recipe: string
    imageUrl?: string
    prepTime: number
    servings: number
    completed?: boolean
}

interface DailyMealPlan {
    day: number
    date: string
    totalCalories: number
    totalProtein: number
    totalCarbs: number
    totalFats: number
    meals: Meal[]
    completed?: boolean
}

interface NutritionPlan {
    id: string
    title: string
    description: string
    dietType: string
    calorieTarget: number
    duration: number
    dailyPlans: DailyMealPlan[]
    createdAt: string
}

interface GroceryItem {
    id: string
    name: string
    category: string
    quantity: number
    unit: string
    checked: boolean
}

interface NutritionState {
    // State
    plans: NutritionPlan[]
    currentPlan: NutritionPlan | null
    currentDay: DailyMealPlan | null
    completedMeals: Record<string, boolean>
    groceryList: GroceryItem[]
    isLoading: boolean
    error: string | null

    // Actions
    fetchPlans: () => Promise<void>
    setCurrentPlan: (plan: NutritionPlan | null) => void
    setCurrentDay: (day: DailyMealPlan | null) => void
    completeMeal: (mealId: string) => void
    completeDay: (dayNumber: number) => void
    generatePlan: (preferences: any) => Promise<void>
    addToGroceryList: (ingredients: string[]) => void
    toggleGroceryItem: (itemId: string) => void
    clearGroceryList: () => void
    clearError: () => void
}

export const useNutritionStore = create<NutritionState>()(
    persist(
        (set, get) => ({
            // Initial state
            plans: [],
            currentPlan: null,
            currentDay: null,
            completedMeals: {},
            groceryList: [],
            isLoading: false,
            error: null,

            // Fetch nutrition plans
            fetchPlans: async () => {
                set({ isLoading: true, error: null })
                try {
                    const response = await nutritionApi.getPlans()
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

            // Set current day
            setCurrentDay: (day) => set({ currentDay: day }),

            // Complete a meal
            completeMeal: (mealId) => {
                set((state) => ({
                    completedMeals: {
                        ...state.completedMeals,
                        [mealId]: true
                    }
                }))
            },

            // Complete a day
            completeDay: (dayNumber) => {
                set((state) => {
                    if (!state.currentPlan) return state

                    const updatedDailyPlans = state.currentPlan.dailyPlans.map(day =>
                        day.day === dayNumber ? { ...day, completed: true } : day
                    )

                    return {
                        currentPlan: {
                            ...state.currentPlan,
                            dailyPlans: updatedDailyPlans
                        }
                    }
                })
            },

            // Generate new nutrition plan
            generatePlan: async (preferences) => {
                set({ isLoading: true, error: null })
                try {
                    const response = await nutritionApi.generatePlan(preferences)
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

            // Add ingredients to grocery list
            addToGroceryList: (ingredients) => {
                const newItems: GroceryItem[] = ingredients.map((item, index) => ({
                    id: `g${Date.now()}-${index}`,
                    name: item,
                    category: 'Produce',
                    quantity: 1,
                    unit: 'unit',
                    checked: false
                }))

                set((state) => ({
                    groceryList: [...state.groceryList, ...newItems]
                }))
            },

            // Toggle grocery item checked status
            toggleGroceryItem: (itemId) => {
                set((state) => ({
                    groceryList: state.groceryList.map(item =>
                        item.id === itemId ? { ...item, checked: !item.checked } : item
                    )
                }))
            },

            // Clear grocery list
            clearGroceryList: () => set({ groceryList: [] }),

            // Clear error
            clearError: () => set({ error: null })
        }),
        {
            name: 'nutrition-storage',
            storage: localStorage,
            partialize: (state) => ({
                completedMeals: state.completedMeals,
                groceryList: state.groceryList
            })
        }
    )
)