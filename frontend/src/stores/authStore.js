import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi } from '../services/api'

export const useAuthStore = create(
    persist(
        (set, get) => ({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: true, // Start with true to prevent flash
            isHydrated: false, // Add this to track hydration
            error: null,

            // Login action
            login: async (username, password) => {
                set({ isLoading: true, error: null })
                try {
                    const response = await authApi.login(username, password)
                    const { access_token, user } = response.data

                    localStorage.setItem('token', access_token)

                    set({
                        user,
                        token: access_token,
                        isAuthenticated: true,
                        isLoading: false
                    })

                    return { success: true }
                } catch (error) {
                    console.error('Login error:', error)
                    set({
                        error: error.response?.data?.detail || 'Login failed',
                        isLoading: false
                    })
                    return { success: false, error: error.response?.data?.detail }
                }
            },

            // Register action
            register: async (userData) => {
                set({ isLoading: true, error: null })
                try {
                    await authApi.register(userData)
                    set({ isLoading: false })
                    return { success: true }
                } catch (error) {
                    set({
                        error: error.response?.data?.detail || 'Registration failed',
                        isLoading: false
                    })
                    return { success: false, error: error.response?.data?.detail }
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

            // Check auth action
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

            // Update user data
            updateUser: (userData) => {
                const currentUser = get().user
                if (currentUser) {
                    set({ user: { ...currentUser, ...userData } })
                }
            },

            // Clear error
            clearError: () => set({ error: null }),

            // Set hydration complete (called by persist)
            setHydrated: () => set({ isHydrated: true })
        }),
        {
            name: 'auth-storage',
            storage: localStorage,
            partialize: (state) => ({
                user: state.user,
                token: state.token,
                isAuthenticated: state.isAuthenticated
            }),
            onRehydrateStorage: () => (state) => {
                // This runs after storage is hydrated
                if (state) {
                    state.setHydrated()
                }
            }
        }
    )
)