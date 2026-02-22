import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import {
    Calendar,
    ShoppingCart,
    Target,
    CheckCircle,
    Utensils,
    Sparkles,
    Coffee,
    Sun,
    Moon,
    Apple,
    Droplets,
    Zap,
    Award,
    Info,
    Eye,
    RefreshCw,
    ChefHat,
    ListChecks
} from 'lucide-react'
import { toast } from 'react-hot-toast'
import Navbar from '../../components/layout/Navbar'
import BackgroundImage from '../../components/layout/BackgroundImage'
import LoadingSpinner from '../../components/ui/LoadingSpinner'
import { useAuthStore, useNutritionStore } from '../../stores'
import { nutritionApi } from '../../services/api'

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

const NutritionPlans = () => {
    const navigate = useNavigate()
    const { user } = useAuthStore()
    const {
        plans,
        currentPlan,
        fetchPlans,
        generatePlan,
        setCurrentDay,
        completeMeal,
        addToGroceryList,
        isLoading: storeLoading
    } = useNutritionStore()

    const [activeTab, setActiveTab] = useState<'today' | 'week' | 'grocery'>('today')
    const [selectedMeal, setSelectedMeal] = useState<Meal | null>(null)
    const [selectedDay, setSelectedDay] = useState<number | null>(null)
    const [showRecipe, setShowRecipe] = useState(false)
    const [completedMeals, setCompletedMeals] = useState<Record<string, boolean>>({})
    const [groceryItems, setGroceryItems] = useState<GroceryItem[]>([])
    const [generating, setGenerating] = useState(false)
    const [showPreferences, setShowPreferences] = useState(false)
    const [preferences, setPreferences] = useState({
        calorieTarget: 2000,
        dietType: user?.diet_preference || 'vegetarian',
        allergies: user?.allergies || '',
        mealsPerDay: 4
    })

    useEffect(() => {
        fetchPlans()
    }, [fetchPlans])

    useEffect(() => {
        if (currentPlan?.dailyPlans) {
            console.log('Available days:', currentPlan.dailyPlans.map(d => d.day))
        }
    }, [currentPlan])

    const handleGeneratePlan = () => {
        setShowPreferences(true)
    }

    const handleGenerateWithPreferences = async () => {
        setGenerating(true)
        setShowPreferences(false)

        try {
            const response = await nutritionApi.generatePlan({
                calorieTarget: preferences.calorieTarget,
                dietType: preferences.dietType,
                allergies: preferences.allergies.split(',').map(a => a.trim()).filter(a => a),
                mealsPerDay: preferences.mealsPerDay,
                durationDays: 7
            })

            if (response.data.success) {
                toast.success('🎉 New meal plan generated successfully!')
                // Wait a moment then fetch plans
                setTimeout(() => {
                    fetchPlans()
                }, 500)
            }
        } catch (error) {
            console.error('Generation error:', error)
            toast.error('Failed to generate meal plan. Please try again.')
        } finally {
            setGenerating(false)
        }
    }

    const handleMealComplete = (mealId: string) => {
        setCompletedMeals(prev => ({
            ...prev,
            [mealId]: true
        }))
        completeMeal(mealId)
        toast.success('Meal logged! 🍽️')
    }

    const handleAddToGrocery = (meal: Meal) => {
        const newItems: GroceryItem[] = meal.ingredients.map((ingredient, index) => ({
            id: `${meal.id}-${index}-${Date.now()}`,
            name: ingredient,
            category: 'Produce',
            quantity: 1,
            unit: 'unit',
            checked: false
        }))
        setGroceryItems(prev => [...prev, ...newItems])
        addToGroceryList(meal.ingredients)
        toast.success('Added to grocery list! 🛒')
    }

    const toggleGroceryItem = (itemId: string) => {
        setGroceryItems(prev =>
            prev.map(item =>
                item.id === itemId ? { ...item, checked: !item.checked } : item
            )
        )
    }

    const clearGroceryList = () => {
        setGroceryItems([])
        toast.success('Grocery list cleared')
    }

    if (storeLoading || generating) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center">
                <div className="text-center">
                    <LoadingSpinner size="lg" />
                    {generating && (
                        <p className="mt-4 text-gray-600">Creating your personalized meal plan...</p>
                    )}
                </div>
            </div>
        )
    }

    const today = new Date().getDay() || 7 // Convert Sunday (0) to 7
    console.log('Current Plan:', currentPlan)
    console.log('Daily Plans:', currentPlan?.dailyPlans)
    const todayPlan = currentPlan?.dailyPlans?.find(d => d.day === today)
    console.log('Today Plan:', todayPlan)
    console.log('Today number:', today)

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
            <BackgroundImage />
            <Navbar />

            <main className="container mx-auto px-4 py-8">
                {/* Header with Generate Button */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8 flex justify-between items-center"
                >
                    <div>
                        <h1 className="text-4xl font-bold text-gray-800 flex items-center gap-3">
                            <Utensils className="w-8 h-8 text-green-500" />
                            Nutrition Plans
                        </h1>
                        <p className="text-gray-600 mt-2">
                            Personalized meal plans tailored to your dietary preferences and goals
                        </p>
                    </div>
                    <button
                        onClick={handleGeneratePlan}
                        className="bg-gradient-to-r from-green-500 to-blue-500 text-white px-6 py-3 rounded-lg hover:from-green-600 hover:to-blue-600 transition-all flex items-center gap-2 shadow-lg"
                    >
                        <Sparkles className="w-5 h-5" />
                        Generate New Plan
                    </button>
                </motion.div>

                {/* Preferences Modal */}
                <AnimatePresence>
                    {showPreferences && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
                            onClick={() => setShowPreferences(false)}
                        >
                            <motion.div
                                initial={{ scale: 0.9, y: 20 }}
                                animate={{ scale: 1, y: 0 }}
                                exit={{ scale: 0.9, y: 20 }}
                                className="bg-white rounded-2xl max-w-md w-full p-6"
                                onClick={(e) => e.stopPropagation()}
                            >
                                <h2 className="text-2xl font-bold text-gray-800 mb-4">Meal Plan Preferences</h2>

                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Daily Calorie Target
                                        </label>
                                        <input
                                            type="range"
                                            min="1500"
                                            max="3500"
                                            step="50"
                                            value={preferences.calorieTarget}
                                            onChange={(e) => setPreferences({ ...preferences, calorieTarget: parseInt(e.target.value) })}
                                            className="w-full"
                                        />
                                        <div className="text-center text-sm text-gray-600 mt-1">
                                            {preferences.calorieTarget} calories
                                        </div>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Diet Type
                                        </label>
                                        <select
                                            value={preferences.dietType}
                                            onChange={(e) => setPreferences({ ...preferences, dietType: e.target.value })}
                                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                                        >
                                            <option value="vegetarian">Vegetarian</option>
                                            <option value="vegan">Vegan</option>
                                            <option value="non_vegetarian">Non-Vegetarian</option>
                                            <option value="keto">Keto</option>
                                            <option value="paleo">Paleo</option>
                                            <option value="mediterranean">Mediterranean</option>
                                        </select>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Allergies / Restrictions
                                        </label>
                                        <input
                                            type="text"
                                            value={preferences.allergies}
                                            onChange={(e) => setPreferences({ ...preferences, allergies: e.target.value })}
                                            placeholder="e.g., peanuts, dairy, gluten (comma separated)"
                                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Meals per Day
                                        </label>
                                        <select
                                            value={preferences.mealsPerDay}
                                            onChange={(e) => setPreferences({ ...preferences, mealsPerDay: parseInt(e.target.value) })}
                                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                                        >
                                            <option value="3">3 meals (breakfast, lunch, dinner)</option>
                                            <option value="4">4 meals (+ snack)</option>
                                            <option value="5">5 meals (+ 2 snacks)</option>
                                        </select>
                                    </div>
                                </div>

                                <div className="flex gap-3 mt-6">
                                    <button
                                        onClick={() => setShowPreferences(false)}
                                        className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={handleGenerateWithPreferences}
                                        className="flex-1 bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600"
                                    >
                                        Generate Plan
                                    </button>
                                </div>
                            </motion.div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Tabs */}
                <div className="flex space-x-4 mb-6">
                    {['today', 'week', 'grocery'].map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab as any)}
                            className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === tab
                                ? 'bg-green-500 text-white'
                                : 'bg-white text-gray-600 hover:bg-gray-100'
                                }`}
                        >
                            {tab.charAt(0).toUpperCase() + tab.slice(1)}
                        </button>
                    ))}
                </div>

                {!currentPlan ? (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="bg-white rounded-2xl shadow-lg p-12 text-center"
                    >
                        <Utensils className="w-16 h-16 text-green-300 mx-auto mb-4" />
                        <h2 className="text-2xl font-bold text-gray-800 mb-2">No Active Meal Plan</h2>
                        <p className="text-gray-600 mb-6">
                            Click the "Generate New Plan" button above to create your personalized meal plan
                        </p>
                    </motion.div>
                ) : (
                    <>
                        {/* Today's View */}
                        {activeTab === 'today' && todayPlan && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="space-y-6"
                            >
                                {/* Daily Summary */}
                                <div className="bg-white rounded-2xl shadow-lg p-6">
                                    <div className="flex justify-between items-start mb-4">
                                        <div>
                                            <h2 className="text-2xl font-bold text-gray-800">Today's Meals</h2>
                                            <p className="text-gray-600 mt-1">
                                                {todayPlan.totalCalories} calories target
                                            </p>
                                        </div>
                                        <div className="bg-green-100 text-green-600 px-3 py-1 rounded-full text-sm font-medium">
                                            Day {todayPlan.day}
                                        </div>
                                    </div>

                                    {/* Macros */}
                                    <div className="grid grid-cols-4 gap-4 mt-4">
                                        <div className="text-center">
                                            <div className="text-lg font-bold text-gray-800">{todayPlan.totalProtein}g</div>
                                            <div className="text-xs text-gray-500">Protein</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-lg font-bold text-gray-800">{todayPlan.totalCarbs}g</div>
                                            <div className="text-xs text-gray-500">Carbs</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-lg font-bold text-gray-800">{todayPlan.totalFats}g</div>
                                            <div className="text-xs text-gray-500">Fats</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-lg font-bold text-gray-800">{todayPlan.totalCalories}</div>
                                            <div className="text-xs text-gray-500">Calories</div>
                                        </div>
                                    </div>
                                </div>

                                {/* Meals */}
                                <div className="space-y-4">
                                    {todayPlan.meals?.map((meal, index) => (
                                        <motion.div
                                            key={meal.id}
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: index * 0.1 }}
                                            className="bg-white rounded-xl shadow-lg overflow-hidden"
                                        >
                                            <div className="flex">
                                                {/* Meal Image/Icon */}
                                                <div className="w-24 bg-gradient-to-br from-green-500 to-blue-500 flex items-center justify-center">
                                                    {meal.type === 'breakfast' && <Coffee className="w-8 h-8 text-white" />}
                                                    {meal.type === 'lunch' && <Sun className="w-8 h-8 text-white" />}
                                                    {meal.type === 'dinner' && <Moon className="w-8 h-8 text-white" />}
                                                    {meal.type === 'snack' && <Apple className="w-8 h-8 text-white" />}
                                                </div>

                                                {/* Meal Details */}
                                                <div className="flex-1 p-4">
                                                    <div className="flex justify-between items-start">
                                                        <div>
                                                            <h3 className="font-semibold text-gray-800">{meal.name}</h3>
                                                            <p className="text-sm text-gray-500 capitalize">{meal.type}</p>
                                                        </div>
                                                        <span className="text-green-600 font-medium">{meal.calories} cal</span>
                                                    </div>

                                                    {/* Macros */}
                                                    <div className="flex gap-4 mt-2 text-xs">
                                                        <span className="text-gray-600">P: {meal.protein}g</span>
                                                        <span className="text-gray-600">C: {meal.carbs}g</span>
                                                        <span className="text-gray-600">F: {meal.fats}g</span>
                                                        <span className="text-gray-600">Prep: {meal.prepTime}min</span>
                                                    </div>

                                                    {/* Actions */}
                                                    <div className="flex gap-2 mt-3">
                                                        <button
                                                            onClick={() => {
                                                                setSelectedMeal(meal)
                                                                setShowRecipe(true)
                                                            }}
                                                            className="text-sm text-blue-500 hover:text-blue-600 flex items-center gap-1"
                                                        >
                                                            <Info className="w-4 h-4" />
                                                            Recipe
                                                        </button>
                                                        <button
                                                            onClick={() => handleAddToGrocery(meal)}
                                                            className="text-sm text-green-500 hover:text-green-600 flex items-center gap-1"
                                                        >
                                                            <ShoppingCart className="w-4 h-4" />
                                                            Add to Grocery
                                                        </button>
                                                        <button
                                                            onClick={() => handleMealComplete(meal.id)}
                                                            disabled={completedMeals[meal.id]}
                                                            className={`text-sm flex items-center gap-1 ${completedMeals[meal.id]
                                                                ? 'text-green-400 cursor-not-allowed'
                                                                : 'text-orange-500 hover:text-orange-600'
                                                                }`}
                                                        >
                                                            <CheckCircle className="w-4 h-4" />
                                                            {completedMeals[meal.id] ? 'Logged' : 'Log Meal'}
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        </motion.div>
                                    ))}
                                </div>
                            </motion.div>
                        )}

                        {/* Weekly View */}
                        {activeTab === 'week' && (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                {currentPlan.dailyPlans?.map((day, index) => (
                                    <motion.div
                                        key={index}
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: index * 0.1 }}
                                        className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
                                    >
                                        <div className="bg-gradient-to-r from-green-500 to-blue-500 p-4">
                                            <h3 className="text-white font-semibold">Day {day.day}</h3>
                                            <p className="text-white/90 text-sm mt-1">{day.totalCalories} calories</p>
                                        </div>
                                        <div className="p-4">
                                            <div className="space-y-2 mb-4">
                                                {day.meals?.map((meal, idx) => (
                                                    <div key={idx} className="flex justify-between text-sm">
                                                        <span className="text-gray-600 capitalize">{meal.type}</span>
                                                        <span className="text-gray-500">{meal.calories} cal</span>
                                                    </div>
                                                ))}
                                            </div>
                                            <button
                                                onClick={() => setSelectedDay(day.day)}
                                                className="w-full bg-green-50 text-green-600 py-2 rounded-lg hover:bg-green-100 transition-colors flex items-center justify-center gap-2"
                                            >
                                                <Eye className="w-4 h-4" />
                                                View Details
                                            </button>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        )}

                        {/* Grocery List */}
                        {activeTab === 'grocery' && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="bg-white rounded-2xl shadow-lg p-6"
                            >
                                <div className="flex justify-between items-center mb-6">
                                    <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                                        <ShoppingCart className="w-6 h-6 text-green-500" />
                                        Grocery List
                                    </h2>
                                    <button
                                        onClick={clearGroceryList}
                                        className="text-gray-500 hover:text-gray-700 text-sm"
                                    >
                                        Clear All
                                    </button>
                                </div>

                                {groceryItems.length === 0 ? (
                                    <div className="text-center py-12">
                                        <ShoppingCart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                                        <p className="text-gray-500">Your grocery list is empty</p>
                                        <p className="text-sm text-gray-400 mt-2">
                                            Add items from meal recipes
                                        </p>
                                    </div>
                                ) : (
                                    <div className="space-y-2">
                                        {groceryItems.map((item) => (
                                            <div
                                                key={item.id}
                                                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                                            >
                                                <div className="flex items-center gap-3">
                                                    <input
                                                        type="checkbox"
                                                        checked={item.checked}
                                                        onChange={() => toggleGroceryItem(item.id)}
                                                        className="w-4 h-4 text-green-500 rounded"
                                                    />
                                                    <span className={item.checked ? 'line-through text-gray-400' : 'text-gray-700'}>
                                                        {item.name}
                                                    </span>
                                                </div>
                                                <span className="text-sm text-gray-500">
                                                    {item.quantity} {item.unit}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </motion.div>
                        )}
                    </>
                )}
            </main>

            {/* Recipe Modal */}
            <AnimatePresence>
                {showRecipe && selectedMeal && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
                        onClick={() => setShowRecipe(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, y: 20 }}
                            animate={{ scale: 1, y: 0 }}
                            exit={{ scale: 0.9, y: 20 }}
                            className="bg-white rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <div className="p-6">
                                <h2 className="text-2xl font-bold text-gray-800 mb-2">{selectedMeal.name}</h2>
                                <p className="text-gray-600 mb-4 capitalize">{selectedMeal.type} • {selectedMeal.prepTime} min prep</p>

                                <div className="mb-6">
                                    <h3 className="font-semibold text-gray-800 mb-2">Ingredients</h3>
                                    <ul className="list-disc list-inside space-y-1">
                                        {selectedMeal.ingredients.map((ingredient, index) => (
                                            <li key={index} className="text-gray-600">{ingredient}</li>
                                        ))}
                                    </ul>
                                </div>

                                <div className="mb-6">
                                    <h3 className="font-semibold text-gray-800 mb-2">Instructions</h3>
                                    <p className="text-gray-600 whitespace-pre-line">{selectedMeal.recipe}</p>
                                </div>

                                <div className="flex justify-end">
                                    <button
                                        onClick={() => setShowRecipe(false)}
                                        className="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600"
                                    >
                                        Close
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    )
}

export default NutritionPlans