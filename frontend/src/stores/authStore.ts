import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi } from '../services/api'

interface User {
    id: number
    username: string
    email: string
    full_name: string
    role?: 'user' | 'admin'
    is_active?: boolean
    fitness_level?: string
    fitness_goal?: string
    workout_preference?: string
    diet_preference?: string
    streak_points?: number
    total_workouts?: number
    charity_donations?: number
    phone?: string
    age?: number
    height?: number
    weight?: number
    gender?: string
    bio?: string
    profile_photo_url?: string
    allergies?: string
    medical_conditions?: string
    injuries?: string
    medications?: string
}

interface AuthState {
    user: User | null
    token: string | null
    isAuthenticated: boolean
    isLoading: boolean
    isHydrated: boolean
    error: string | null
    login: (username: string, password: string) => Promise<{ success: boolean; error?: string }>
    register: (userData: any) => Promise<{ success: boolean; error?: string }>
    logout: () => void
    checkAuth: () => Promise<boolean>
    updateUser: (userData: Partial<User>) => void
    clearError: () => void
    setHydrated: () => void
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: true,
            isHydrated: false,
            error: null,

            login: async (username: string, password: string) => {
                set({ isLoading: true, error: null })
                try {
                    const response = await authApi.login(username, password)
                    const { access_token, refresh_token, user } = response.data

                    localStorage.setItem('token', access_token)
                    if (refresh_token) {
                        localStorage.setItem('refresh_token', refresh_token)
                    }

                    set({
                        user,
                        token: access_token,
                        isAuthenticated: true,
                        isLoading: false
                    })

                    return { success: true }
                } catch (error: any) {
                    console.error('Login error:', error)
                    set({
                        error: error.response?.data?.detail || 'Login failed',
                        isLoading: false
                    })
                    return { success: false, error: error.response?.data?.detail }
                }
            },

            register: async (userData: any) => {
                set({ isLoading: true, error: null })
                try {
                    const response = await authApi.register(userData)
                    set({ isLoading: false })
                    return { success: true }
                } catch (error: any) {
                    set({
                        error: error.response?.data?.detail || 'Registration failed',
                        isLoading: false
                    })
                    return { success: false, error: error.response?.data?.detail }
                }
            },

            logout: () => {
                localStorage.removeItem('token')
                localStorage.removeItem('refresh_token')
                set({
                    user: null,
                    token: null,
                    isAuthenticated: false,
                    error: null
                })
            },

            checkAuth: async () => {
                const token = localStorage.getItem('token')
                if (!token) {
                    set({ isAuthenticated: false, user: null, isLoading: false })
                    return false
                }

                set({ isLoading: true })
                try {
                    const response = await authApi.getProfile()
                    set({
                        user: response.data,
                        token: token,
                        isAuthenticated: true,
                        isLoading: false
                    })
                    return true
                } catch (error) {
                    console.error('Auth check failed:', error)
                    localStorage.removeItem('token')
                    set({
                        user: null,
                        token: null,
                        isAuthenticated: false,
                        isLoading: false
                    })
                    return false
                }
            },

            updateUser: (userData: Partial<User>) => {
                const currentUser = get().user
                if (currentUser) {
                    set({ user: { ...currentUser, ...userData } })
                }
            },

            clearError: () => set({ error: null }),

            setHydrated: () => set({ isHydrated: true })
        }),
        {
            name: 'auth-storage',
            storage: localStorage,
            onRehydrateStorage: () => (state) => {
                if (state) {
                    state.setHydrated()
                }
            }
        }
    )
)