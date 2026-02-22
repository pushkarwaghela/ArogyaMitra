import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Track if a refresh is already in progress
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle responses and token refresh
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config

    // If error is not 403 or request already retried, reject
    if (error.response?.status !== 403 || originalRequest._retry) {
      return Promise.reject(error)
    }

    // If token refresh is in progress, queue this request
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject })
      })
        .then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        })
        .catch(err => Promise.reject(err))
    }

    originalRequest._retry = true
    isRefreshing = true

    try {
      // Try to refresh the token
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        throw new Error('No refresh token')
      }

      const response = await api.post('/auth/refresh', { refresh_token: refreshToken })
      const { access_token } = response.data

      // Update token in localStorage
      localStorage.setItem('token', access_token)

      // Update Authorization header
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

      // Process queued requests
      processQueue(null, access_token)

      // Retry original request
      originalRequest.headers.Authorization = `Bearer ${access_token}`
      return api(originalRequest)
    } catch (refreshError) {
      // Refresh failed - clear tokens and redirect to login
      processQueue(refreshError, null)
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')

      // Redirect to login page
      window.location.href = '/login'

      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  }
)

// Auth APIs
export const authApi = {
  login: (username, password) => {
    const loginData = { username, password }
    console.log('Sending login data:', loginData)
    return api.post('/auth/login/json', loginData)
  },

  register: (userData) => {
    console.log('Sending register data:', userData)
    return api.post('/auth/register', userData)
  },

  getProfile: () => api.get('/auth/me'),
  refreshToken: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
}

// User APIs
export const userApi = {
  getProfile: () => api.get('/users/me'),
  updateProfile: (data) => api.put('/users/me', data),
}

// Workout APIs
export const workoutApi = {
  getPlans: () => api.get('/workouts/plans'),
  getPlan: (id) => api.get(`/workouts/${id}`),
  generatePlan: (preferences) => api.post('/workouts/generate', preferences),
  getActiveWorkout: () => api.get('/workouts/active'),
  completeWorkout: (id) => api.post(`/workouts/${id}/complete`),
}

// Nutrition APIs
export const nutritionApi = {
  getPlans: () => api.get('/nutrition/plans'),
  generatePlan: (preferences) => api.post('/nutrition/generate', preferences),
  getGroceryList: (planId) => api.get(`/nutrition/${planId}/grocery`),
}

// Progress APIs
export const progressApi = {
  getStats: () => api.get('/progress/stats'),
  getHistory: (period) => api.get(`/progress/history?period=${period}`),
  getAchievements: () => api.get('/progress/achievements'),
  trackWorkout: (data) => api.post('/progress/track', data),
}

// Health APIs
export const healthApi = {
  submitAssessment: (data) => api.post('/health/assessment', data),
  getAssessment: () => api.get('/health/assessment'),
}

// AROMI APIs
export const aromiApi = {
  chat: (message, sessionId) => api.post('/aromi/chat', { message, session_id: sessionId }),
  getSessions: () => api.get('/aromi/sessions'),
  getMessages: (sessionId) => api.get(`/aromi/sessions/${sessionId}/messages`),
  createSession: () => api.post('/aromi/sessions'),
}

// YouTube APIs
export const youtubeApi = {
  searchExercise: (exercise, type, difficulty) =>
    api.get(`/youtube/search?exercise=${exercise}&type=${type}&difficulty=${difficulty}`),
}

export default api