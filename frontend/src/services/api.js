import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Add token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// Mock data for development
const mockWorkoutPlans = [{
    id: '1',
    title: '4-Week Weight Loss Challenge',
    description: 'A comprehensive plan to kickstart your weight loss journey',
    duration: 4,
    difficulty: 'intermediate',
    weeklySchedule: [
        {
            day: 'Monday',
            dayNumber: 1,
            focus: 'Full Body Strength',
            totalDuration: 45,
            totalCalories: 300,
            exercises: [
                {
                    id: 'e1',
                    name: 'Push-ups',
                    sets: 3,
                    reps: 10,
                    restTime: 60,
                    muscleGroup: 'Chest',
                    difficulty: 'beginner',
                    caloriesBurn: 50
                },
                {
                    id: 'e2',
                    name: 'Squats',
                    sets: 3,
                    reps: 15,
                    restTime: 60,
                    muscleGroup: 'Legs',
                    difficulty: 'beginner',
                    caloriesBurn: 70
                },
                {
                    id: 'e3',
                    name: 'Plank',
                    sets: 3,
                    reps: 0,
                    duration: 30,
                    restTime: 30,
                    muscleGroup: 'Core',
                    difficulty: 'beginner',
                    caloriesBurn: 40
                }
            ]
        },
        {
            day: 'Tuesday',
            dayNumber: 2,
            focus: 'Cardio HIIT',
            totalDuration: 30,
            totalCalories: 250,
            exercises: [
                {
                    id: 'e4',
                    name: 'Jumping Jacks',
                    sets: 3,
                    reps: 0,
                    duration: 45,
                    restTime: 15,
                    muscleGroup: 'Full Body',
                    difficulty: 'beginner',
                    caloriesBurn: 80
                },
                {
                    id: 'e5',
                    name: 'High Knees',
                    sets: 3,
                    reps: 0,
                    duration: 45,
                    restTime: 15,
                    muscleGroup: 'Legs',
                    difficulty: 'beginner',
                    caloriesBurn: 85
                }
            ]
        },
        {
            day: 'Wednesday',
            dayNumber: 3,
            focus: 'Upper Body',
            totalDuration: 40,
            totalCalories: 280,
            exercises: [
                {
                    id: 'e6',
                    name: 'Push-ups',
                    sets: 3,
                    reps: 12,
                    restTime: 60,
                    muscleGroup: 'Chest',
                    difficulty: 'beginner',
                    caloriesBurn: 60
                },
                {
                    id: 'e7',
                    name: 'Tricep Dips',
                    sets: 3,
                    reps: 10,
                    restTime: 60,
                    muscleGroup: 'Arms',
                    difficulty: 'beginner',
                    caloriesBurn: 45
                }
            ]
        }
    ],
    createdAt: new Date().toISOString()
}]

const mockNutritionPlans = [{
    id: '1',
    title: 'Balanced Nutrition Plan',
    description: 'A healthy meal plan for weight management',
    dietType: 'vegetarian',
    calorieTarget: 2000,
    duration: 7,
    dailyPlans: [
        {
            day: 1,
            date: new Date().toISOString(),
            totalCalories: 1950,
            totalProtein: 65,
            totalCarbs: 250,
            totalFats: 70,
            meals: [
                {
                    id: 'm1',
                    name: 'Oatmeal with Fruits',
                    type: 'breakfast',
                    calories: 350,
                    protein: 10,
                    carbs: 60,
                    fats: 8,
                    ingredients: ['Oats', 'Banana', 'Berries', 'Milk'],
                    recipe: 'Cook oats with milk, top with sliced banana and berries.',
                    prepTime: 10,
                    servings: 1
                },
                {
                    id: 'm2',
                    name: 'Quinoa Salad',
                    type: 'lunch',
                    calories: 450,
                    protein: 15,
                    carbs: 65,
                    fats: 12,
                    ingredients: ['Quinoa', 'Cucumber', 'Tomatoes', 'Olive Oil', 'Lemon'],
                    recipe: 'Cook quinoa, mix with chopped vegetables, dress with olive oil and lemon.',
                    prepTime: 20,
                    servings: 1
                },
                {
                    id: 'm3',
                    name: 'Grilled Vegetables with Rice',
                    type: 'dinner',
                    calories: 500,
                    protein: 12,
                    carbs: 80,
                    fats: 15,
                    ingredients: ['Brown Rice', 'Bell Peppers', 'Zucchini', 'Eggplant', 'Olive Oil'],
                    recipe: 'Cook rice, grill vegetables, serve together.',
                    prepTime: 30,
                    servings: 1
                }
            ]
        }
    ],
    createdAt: new Date().toISOString()
}]

const mockProgressStats = {
    currentStreak: 7,
    totalWorkouts: 24,
    totalCaloriesBurned: 5600,
    avgWorkoutDuration: 42,
    completionRate: 85,
    weightChange: -2.5,
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    lastWorkout: new Date().toISOString()
}

const mockProgressHistory = [
    { date: '2026-02-15', weight: 70.5, workouts: 1, calories: 320, water: 2.0, sleep: 7.5 },
    { date: '2026-02-16', weight: 70.2, workouts: 1, calories: 350, water: 2.2, sleep: 8.0 },
    { date: '2026-02-17', weight: 70.0, workouts: 1, calories: 300, water: 2.5, sleep: 7.0 },
    { date: '2026-02-18', weight: 69.8, workouts: 1, calories: 380, water: 2.3, sleep: 7.5 },
    { date: '2026-02-19', weight: 69.5, workouts: 1, calories: 310, water: 2.0, sleep: 8.0 },
    { date: '2026-02-20', weight: 69.3, workouts: 1, calories: 340, water: 2.4, sleep: 7.5 },
    { date: '2026-02-21', weight: 69.0, workouts: 1, calories: 360, water: 2.5, sleep: 8.0 }
]

const mockAchievements = [
    {
        id: '1',
        name: 'First Workout',
        description: 'Completed your first workout',
        icon: '🏆',
        achievedAt: new Date(Date.now() - 28 * 24 * 60 * 60 * 1000).toISOString(),
        category: 'workout'
    },
    {
        id: '2',
        name: '7-Day Streak',
        description: 'Worked out 7 days in a row',
        icon: '🔥',
        achievedAt: new Date(Date.now() - 21 * 24 * 60 * 60 * 1000).toISOString(),
        category: 'streak'
    },
    {
        id: '3',
        name: 'Weight Loss Milestone',
        description: 'Lost 2.5 kg',
        icon: '⭐',
        achievedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        category: 'milestone'
    }
]

// Auth APIs
export const authApi = {
    login: (username, password) =>
        api.post('/auth/login/json', { username, password }),

    register: (userData) =>
        api.post('/auth/register', userData),

    getProfile: () =>
        api.get('/auth/me'),

    refreshToken: (refreshToken) =>
        api.post('/auth/refresh', { refresh_token: refreshToken }),
}

// User APIs
export const userApi = {
    getProfile: () =>
        api.get('/users/me'),

    getActiveWorkout: () =>
        api.get('/workouts/active'),

    getProgressStats: () =>
        api.get('/progress/stats'),

    getUpcomingWorkouts: () =>
        api.get('/workouts/upcoming'),
}

// Workout APIs with mock data fallback
export const workoutApi = {
    getPlans: () => {
        console.log('Fetching workout plans (using mock data)')
        return Promise.resolve({ data: mockWorkoutPlans })
    },

    getPlan: (id) => {
        const plan = mockWorkoutPlans.find(p => p.id === id)
        return Promise.resolve({ data: plan || mockWorkoutPlans[0] })
    },

    generatePlan: (preferences) => {
        console.log('Generating workout plan (using mock data)', preferences)
        return Promise.resolve({ data: mockWorkoutPlans[0] })
    },

    getActiveWorkout: () =>
        api.get('/workouts/active').catch(() => ({ data: mockWorkoutPlans[0] })),

    getUpcomingWorkouts: () =>
        api.get('/workouts/upcoming').catch(() => ({
            data: mockWorkoutPlans[0].weeklySchedule.slice(0, 3)
        })),

    completeWorkout: (id) =>
        api.post(`/workouts/${id}/complete`).catch(() => ({ data: { success: true } })),
}

// Nutrition APIs with mock data fallback
export const nutritionApi = {
    getPlans: () => {
        console.log('Fetching nutrition plans (using mock data)')
        return Promise.resolve({ data: mockNutritionPlans })
    },

    getPlan: (id) => {
        const plan = mockNutritionPlans.find(p => p.id === id)
        return Promise.resolve({ data: plan || mockNutritionPlans[0] })
    },

    generatePlan: (preferences) => {
        console.log('Generating nutrition plan (using mock data)', preferences)
        return Promise.resolve({ data: mockNutritionPlans[0] })
    },

    getGroceryList: (planId) => {
        const ingredients = mockNutritionPlans[0].dailyPlans[0].meals.flatMap(m => m.ingredients)
        const uniqueIngredients = [...new Set(ingredients)]
        return Promise.resolve({
            data: uniqueIngredients.map((item, index) => ({
                id: `g${index}`,
                name: item,
                category: 'Produce',
                quantity: 1,
                unit: 'unit',
                checked: false
            }))
        })
    },
}

// Progress APIs with mock data fallback
export const progressApi = {
    getStats: () => {
        console.log('Fetching progress stats (using mock data)')
        return Promise.resolve({ data: mockProgressStats })
    },

    getHistory: (period) => {
        console.log('Fetching progress history (using mock data)', period)
        return Promise.resolve({ data: mockProgressHistory })
    },

    getAchievements: () => {
        console.log('Fetching achievements (using mock data)')
        return Promise.resolve({ data: mockAchievements })
    },

    trackWorkout: (data) =>
        api.post('/progress/track', data).catch(() => ({ data: { success: true } })),
}

// Health APIs
export const healthApi = {
    submitAssessment: (data) => {
        console.log('Submitting health assessment (mock)', data)
        return Promise.resolve({ data: { success: true, message: 'Assessment submitted' } })
    },

    getAssessment: () =>
        api.get('/health/assessment').catch(() => ({ data: null })),
}

// AROMI APIs
export const aromiApi = {
    chat: (message, sessionId) => {
        console.log('AROMI chat (mock)', message)
        const responses = [
            "I'm here to help! Based on your fitness goals, I recommend focusing on compound exercises like squats and push-ups.",
            "Great question! For weight loss, combining strength training with cardio is most effective.",
            "Remember to stay hydrated and listen to your body. Recovery is just as important as the workout itself!",
            "You're doing amazing! Consistency is key - even a 15-minute workout counts.",
            "For better results, try to increase your protein intake and get at least 7-8 hours of sleep."
        ]
        const randomResponse = responses[Math.floor(Math.random() * responses.length)]
        return Promise.resolve({
            data: {
                response: randomResponse,
                suggestions: ['Tell me more', 'Generate workout', 'Nutrition advice', 'Motivate me']
            }
        })
    },

    getSessions: () =>
        api.get('/aromi/sessions').catch(() => ({ data: [] })),

    getMessages: (sessionId) =>
        api.get(`/aromi/sessions/${sessionId}/messages`).catch(() => ({ data: [] })),
}

// Calendar APIs
export const calendarApi = {
    getStatus: () =>
        api.get('/calendar/status').catch(() => ({
            data: { connected: false, auth_url: 'https://accounts.google.com/o/oauth2/auth?...' }
        })),

    getAuthUrl: () =>
        api.get('/calendar/auth').catch(() => ({ data: { auth_url: 'https://accounts.google.com/o/oauth2/auth?...' } })),

    syncWorkout: (workoutPlanId, startDate) =>
        api.post('/calendar/sync-workout', { workout_plan_id: workoutPlanId, start_date: startDate })
            .catch(() => ({ data: { events: [] } })),

    getUpcomingEvents: () =>
        api.get('/calendar/upcoming').catch(() => ({ data: [] })),
}

export default api