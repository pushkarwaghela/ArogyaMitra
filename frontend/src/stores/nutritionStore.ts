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
    fetchPlanDetails: (planId: string) => Promise<void>
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
                    console.log('Fetching nutrition plans...')
                    const response = await nutritionApi.getPlans()
                    console.log('✅ Fetched nutrition plans:', response.data)

                    // Transform snake_case to camelCase
                    const plans = response.data.map((plan: any) => ({
                        id: plan.id,
                        title: plan.title,
                        description: plan.description,
                        dietType: plan.diet_type || 'vegetarian',
                        calorieTarget: plan.calorie_target || 2000,
                        duration: plan.duration || 7,
                        dailyPlans: (plan.daily_plans || []).map((day: any) => ({
                            day: day.day,
                            totalCalories: day.total_calories,
                            totalProtein: day.total_protein,
                            totalCarbs: day.total_carbs,
                            totalFats: day.total_fats,
                            meals: (day.meals || []).map((meal: any) => ({
                                id: meal.id,
                                name: meal.name,
                                type: meal.type,
                                calories: meal.calories,
                                protein: meal.protein || 0,
                                carbs: meal.carbs || 0,
                                fats: meal.fats || 0,
                                ingredients: meal.ingredients || [],
                                recipe: meal.recipe || '',
                                prepTime: meal.prep_time || 30,
                                imageUrl: meal.image_url,
                                servings: meal.servings || 1
                            }))
                        })),
                        createdAt: plan.created_at
                    }))

                    set({
                        plans,
                        currentPlan: plans[0] || null,
                        isLoading: false
                    })

                    if (plans[0]) {
                        console.log('Current plan (transformed):', plans[0])
                    }
                } catch (error: any) {
                    console.error('❌ Fetch plans error:', error)
                    set({
                        error: error.response?.data?.detail || 'Failed to fetch plans',
                        isLoading: false
                    })
                }
            },

            // Fetch plan details (if needed for more details)
            fetchPlanDetails: async (planId: string) => {
                set({ isLoading: true, error: null })
                try {
                    // You might need a separate endpoint for this
                    // For now, just find the plan in the existing list
                    const plan = get().plans.find(p => p.id === planId)
                    if (plan) {
                        set({ currentPlan: plan, isLoading: false })
                    }
                } catch (error: any) {
                    console.error('❌ Fetch plan details error:', error)
                    set({
                        error: error.response?.data?.detail || 'Failed to fetch plan details',
                        isLoading: false
                    })
                }
            },

            // Set current plan
            setCurrentPlan: (plan) => {
                set({ currentPlan: plan })
                if (plan) {
                    get().fetchPlanDetails(plan.id)
                }
            },

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
                    console.log('Generating nutrition plan with preferences:', preferences)
                    const response = await nutritionApi.generatePlan(preferences)
                    console.log('✅ Generate plan response:', response.data)

                    // After generation, fetch all plans again to get the updated list
                    await get().fetchPlans()

                    set({ isLoading: false })

                } catch (error: any) {
                    console.error('❌ Generate plan error:', error)
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