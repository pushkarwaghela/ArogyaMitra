import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { aromiApi } from '../services/api'

interface Message {
    id: string
    type: 'user' | 'aromi' | 'system'
    content: string
    timestamp: Date
    suggestions?: string[]
}

interface ChatSession {
    id: number
    title: string
    created_at: string
    message_count: number
}

interface ChatState {
    // State
    sessions: ChatSession[]
    currentSessionId: number | null
    messages: Record<number, Message[]>
    isLoading: boolean
    error: string | null

    // Actions
    fetchSessions: () => Promise<void>
    createSession: () => Promise<number>
    loadMessages: (sessionId: number) => Promise<void>
    sendMessage: (sessionId: number | null, content: string) => Promise<void>
    clearMessages: () => void
    clearError: () => void
}

export const useChatStore = create<ChatState>()(
    persist(
        (set, get) => ({
            // Initial state
            sessions: [],
            currentSessionId: null,
            messages: {},
            isLoading: false,
            error: null,

            // Fetch all chat sessions
            fetchSessions: async () => {
                set({ isLoading: true, error: null })
                try {
                    const response = await aromiApi.getSessions()
                    set({ sessions: response.data, isLoading: false })
                } catch (error: any) {
                    set({
                        error: error.response?.data?.detail || 'Failed to fetch sessions',
                        isLoading: false
                    })
                }
            },

            // Create a new chat session
            createSession: async () => {
                set({ isLoading: true, error: null })
                try {
                    const response = await aromiApi.createSession()
                    const newSession = response.data

                    set((state) => ({
                        sessions: [newSession, ...state.sessions],
                        currentSessionId: newSession.id,
                        messages: {
                            ...state.messages,
                            [newSession.id]: []
                        },
                        isLoading: false
                    }))

                    return newSession.id
                } catch (error: any) {
                    set({
                        error: error.response?.data?.detail || 'Failed to create session',
                        isLoading: false
                    })
                    return 0
                }
            },

            // Load messages for a session
            loadMessages: async (sessionId) => {
                set({ isLoading: true, error: null })
                try {
                    const response = await aromiApi.getMessages(sessionId)
                    set((state) => ({
                        messages: {
                            ...state.messages,
                            [sessionId]: response.data.map((msg: any) => ({
                                ...msg,
                                timestamp: new Date(msg.timestamp)
                            }))
                        },
                        currentSessionId: sessionId,
                        isLoading: false
                    }))
                } catch (error: any) {
                    set({
                        error: error.response?.data?.detail || 'Failed to load messages',
                        isLoading: false
                    })
                }
            },

            // Send a message
            sendMessage: async (sessionId, content) => {
                if (!content.trim()) return

                const userMessage: Message = {
                    id: Date.now().toString(),
                    type: 'user',
                    content,
                    timestamp: new Date()
                }

                // If no session, create one
                let currentSessionId = sessionId
                if (!currentSessionId) {
                    currentSessionId = await get().createSession()
                }

                // Add user message to state
                set((state) => ({
                    messages: {
                        ...state.messages,
                        [currentSessionId]: [
                            ...(state.messages[currentSessionId] || []),
                            userMessage
                        ]
                    }
                }))

                set({ isLoading: true })

                try {
                    const response = await aromiApi.chat(content, currentSessionId)

                    const aromiMessage: Message = {
                        id: (Date.now() + 1).toString(),
                        type: 'aromi',
                        content: response.data.response,
                        timestamp: new Date(),
                        suggestions: response.data.suggestions
                    }

                    set((state) => ({
                        messages: {
                            ...state.messages,
                            [currentSessionId]: [
                                ...(state.messages[currentSessionId] || []),
                                aromiMessage
                            ]
                        },
                        isLoading: false
                    }))

                } catch (error: any) {
                    // Add fallback response
                    const fallbackMessage: Message = {
                        id: (Date.now() + 1).toString(),
                        type: 'aromi',
                        content: "I'm here to help! How can I assist with your fitness journey?",
                        timestamp: new Date(),
                        suggestions: ['Generate workout', 'Meal ideas', 'Motivate me']
                    }

                    set((state) => ({
                        messages: {
                            ...state.messages,
                            [currentSessionId]: [
                                ...(state.messages[currentSessionId] || []),
                                fallbackMessage
                            ]
                        },
                        error: error.response?.data?.detail || 'Failed to send message',
                        isLoading: false
                    }))
                }
            },

            // Clear all messages
            clearMessages: () => set({ messages: {}, currentSessionId: null }),

            // Clear error
            clearError: () => set({ error: null })
        }),
        {
            name: 'chat-storage',
            storage: localStorage,
            partialize: (state) => ({
                sessions: state.sessions,
                currentSessionId: state.currentSessionId
            })
        }
    )
)