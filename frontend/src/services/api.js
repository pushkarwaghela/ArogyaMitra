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

// Handle errors properly - no mock fallbacks
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.response?.status, error.config?.url)
    return Promise.reject(error)
  }
)

// Auth APIs
export const authApi = {
  login: (username, password) => {
    // Make sure we're sending the exact format the backend expects
    const loginData = { username, password }
    console.log('Sending login data:', loginData) // Debug log
    return api.post('/auth/login/json', loginData)
  },

  register: (userData) => {
    console.log('Sending register data:', userData) // Debug log
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