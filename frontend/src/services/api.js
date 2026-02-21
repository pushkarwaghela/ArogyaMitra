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

// Handle 404 errors gracefully
api.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 404) {
            console.log('API endpoint not found:', error.config.url)
            // Return mock data or empty response
            return Promise.resolve({ data: {} })
        }
        return Promise.reject(error)
    }
)

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

export default api