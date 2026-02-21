import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi } from '../services/api'

interface User {
    id: number
    username: string
    email: string
    full_name: string
    role: 'user' | 'admin'
    is_active: boolean
    fitness_level?: string
    fitness_goal?: string
    workout_preference?: string
    diet_preference?: string
    streak_points: number
    total_workouts: number
    charity_donations: number
    phone?: string
    age?: number
    height?: number
    weight?: number
    gender?: string
    bio?: string
    profile_photo_url?: string
}

interface AuthState {
    // State
    user: User | null
    token: string | null
    isAuthenticated: boolean
    isLoading: boolean
    error: string | null

    // Actions
    login: (username: string, password: string) => Promise<void>
    register: (userData: any) => Promise<void>
    logout: () => void
    updateUser: (userData: Partial<User>) => void
    clearError: () => void
    refreshToken: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
            // Initial state
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,

            // Login action
            login: async (username: string, password: string) => {
                set({ isLoading: true, error: null })
                try {
                    const response = await authApi.login(username, password)
                    const { access_token, user } = response.data

                    // Store token in localStorage (already handled by persist)
                    set({
                        user,
                        token: access_token,
                        isAuthenticated: true,
                        isLoading: false
                    })

                    // Also store token separately for API interceptors
                    localStorage.setItem('token', access_token)

                } catch (error: any) {
                    set({
                        error: error.response?.data?.detail || 'Login failed',
                        isLoading: false
                    })
                    throw error
                }
            },

            // Register action
            register: async (userData: any) => {
                set({ isLoading: true, error: null })
                try {
                    const response = await authApi.register(userData)
                    const { access_token, user } = response.data

                    set({
                        user,
                        token: access_token,
                        isAuthenticated: true,
                        isLoading: false
                    })

                    localStorage.setItem('token', access_token)

                } catch (error: any) {
                    set({
                        error: error.response?.data?.detail || 'Registration failed',
                        isLoading: false
                    })
                    throw error
                }
            },

            // Logout action
            logout: () => {
                localStorage.removeItem('token')
                set({
                    user: null,
                    token: null,
                    isAuthenticated: false,
                    error: null
                })
            },

            // Update user data
            updateUser: (userData: Partial<User>) => {
                const currentUser = get().user
                if (currentUser) {
                    set({ user: { ...currentUser, ...userData } })
                }
            },

            // Clear error
            clearError: () => set({ error: null }),

            // Refresh token
            refreshToken: async () => {
                try {
                    const refreshToken = localStorage.getItem('refresh_token')
                    if (!refreshToken) throw new Error('No refresh token')

                    const response = await authApi.refreshToken(refreshToken)
                    const { access_token } = response.data

                    set({ token: access_token })
                    localStorage.setItem('token', access_token)

                } catch (error) {
                    get().logout()
                }
            }
        }),
        {
            name: 'auth-storage', // name in localStorage
            storage: localStorage, // use localStorage
        }
    )
)