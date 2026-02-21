import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, MessageCircle, X, Loader, Heart, TrendingUp, Calendar, Zap, Bot, User, Mic, MicOff } from 'lucide-react'
import { toast } from 'react-hot-toast'
import { aromiApi } from '../services/api'
import { useAuthStore } from '../stores/authStore'

interface Message {
    id: string
    type: 'user' | 'aromi' | 'system'
    content: string
    timestamp: Date
    suggestions?: string[]
}

interface ArogyaCoachProps {
    isOpen: boolean
    onToggle: () => void
}

const ArogyaCoach: React.FC<ArogyaCoachProps> = ({ isOpen, onToggle }) => {
    const { user } = useAuthStore()
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            type: 'aromi',
            content: `👋 Namaste ${user?.full_name || 'friend'}! I'm AROMI, your personal health companion powered by ArogyaMitra! How can I help you today?`,
            timestamp: new Date(),
            suggestions: ['Generate workout', 'Meal ideas', 'Motivate me', 'Track progress']
        }
    ])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [isListening, setIsListening] = useState(false)
    const messagesEndRef = useRef<HTMLDivElement>(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const handleSend = async () => {
        if (!input.trim() || loading) return

        const userMessage: Message = {
            id: Date.now().toString(),
            type: 'user',
            content: input,
            timestamp: new Date()
        }

        setMessages(prev => [...prev, userMessage])
        setInput('')
        setLoading(true)

        try {
            // Call AROMI API
            const response = await aromiApi.chat(input, null)

            const aromiMessage: Message = {
                id: (Date.now() + 1).toString(),
                type: 'aromi',
                content: response.data.response || "I'm here to help with your fitness journey!",
                timestamp: new Date(),
                suggestions: response.data.suggestions
            }

            setMessages(prev => [...prev, aromiMessage])
        } catch (error) {
            console.error('Chat error:', error)

            // Fallback responses based on keywords
            let fallbackResponse = "I'm here to help! You can ask me about workouts, nutrition, or motivation."

            const lowerInput = input.toLowerCase()
            if (lowerInput.includes('workout') || lowerInput.includes('exercise')) {
                fallbackResponse = "I'd be happy to suggest a workout! Based on your profile, I recommend a mix of strength and cardio. Would you like me to generate a personalized plan?"
            } else if (lowerInput.includes('meal') || lowerInput.includes('food') || lowerInput.includes('eat')) {
                fallbackResponse = "For nutrition, focus on protein-rich foods, complex carbs, and healthy fats. I can create a meal plan based on your preferences!"
            } else if (lowerInput.includes('motivat') || lowerInput.includes('tired') || lowerInput.includes('give up')) {
                fallbackResponse = "You're doing amazing! Remember why you started. Every small step counts towards your goal. Stay consistent and you'll see results! 💪"
            } else if (lowerInput.includes('travel') || lowerInput.includes('trip') || lowerInput.includes('vacation')) {
                fallbackResponse = "Traveling soon? I can adjust your workout plan to be travel-friendly with bodyweight exercises you can do anywhere!"
            } else if (lowerInput.includes('injur') || lowerInput.includes('pain') || lowerInput.includes('hurt')) {
                fallbackResponse = "I'm sorry to hear about your injury. Please rest and consult a healthcare professional. I can suggest alternative exercises that won't strain the affected area."
            }

            const aromiMessage: Message = {
                id: (Date.now() + 1).toString(),
                type: 'aromi',
                content: fallbackResponse,
                timestamp: new Date(),
                suggestions: ['Tell me more', 'Generate workout', 'Nutrition tips', 'Motivate me']
            }

            setMessages(prev => [...prev, aromiMessage])
        } finally {
            setLoading(false)
        }
    }

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    const handleSuggestionClick = (suggestion: string) => {
        setInput(suggestion)
    }

    const toggleListening = () => {
        if (!isListening) {
            // Request microphone access
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
                const recognition = new SpeechRecognition()

                recognition.continuous = false
                recognition.interimResults = false
                recognition.lang = 'en-US'

                recognition.onstart = () => {
                    setIsListening(true)
                    toast.success('Listening...')
                }

                recognition.onresult = (event) => {
                    const transcript = event.results[0][0].transcript
                    setInput(transcript)
                }

                recognition.onerror = (event) => {
                    console.error('Speech recognition error:', event.error)
                    setIsListening(false)
                    toast.error('Could not access microphone')
                }

                recognition.onend = () => {
                    setIsListening(false)
                }

                recognition.start()
            } else {
                toast.error('Speech recognition not supported in your browser')
            }
        } else {
            setIsListening(false)
        }
    }

    // Quick action buttons
    const quickActions = [
        { icon: Zap, label: 'Quick Workout', action: 'Give me a 15-minute workout' },
        { icon: Heart, label: 'Motivate Me', action: 'I need motivation' },
        { icon: TrendingUp, label: 'Progress', action: 'How is my progress?' },
        { icon: Calendar, label: 'Adjust Plan', action: 'Adjust my plan for travel' }
    ]

    return (
        <>
            {/* Floating Button */}
            <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={onToggle}
                className="fixed bottom-6 right-6 bg-gradient-to-r from-purple-500 to-pink-500 text-white p-4 rounded-full shadow-lg z-50 hover:shadow-xl transition-shadow"
            >
                {isOpen ? <X className="w-6 h-6" /> : <MessageCircle className="w-6 h-6" />}
            </motion.button>

            {/* Chat Window */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 20, scale: 0.95 }}
                        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                        className="fixed bottom-24 right-6 w-96 bg-white rounded-2xl shadow-2xl z-50 overflow-hidden border border-gray-200"
                    >
                        {/* Header */}
                        <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-4 text-white">
                            <div className="flex items-center gap-3">
                                <div className="bg-white/20 p-2 rounded-full">
                                    <Bot className="w-5 h-5" />
                                </div>
                                <div>
                                    <h3 className="font-semibold">AROMI Coach</h3>
                                    <p className="text-xs opacity-90">AI-Powered Fitness Assistant</p>
                                </div>
                            </div>
                        </div>

                        {/* Messages */}
                        <div className="h-96 overflow-y-auto p-4 space-y-4 bg-gray-50">
                            {messages.map((message) => (
                                <div
                                    key={message.id}
                                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div className={`flex gap-2 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse' : ''}`}>
                                        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${message.type === 'user'
                                                ? 'bg-blue-100'
                                                : message.type === 'system'
                                                    ? 'bg-gray-100'
                                                    : 'bg-gradient-to-r from-purple-500 to-pink-500'
                                            }`}>
                                            {message.type === 'user' ? (
                                                <User className="w-4 h-4 text-blue-600" />
                                            ) : message.type === 'system' ? (
                                                <Bot className="w-4 h-4 text-gray-600" />
                                            ) : (
                                                <Bot className="w-4 h-4 text-white" />
                                            )}
                                        </div>
                                        <div>
                                            <div className={`p-3 rounded-2xl ${message.type === 'user'
                                                    ? 'bg-blue-500 text-white rounded-br-none'
                                                    : message.type === 'system'
                                                        ? 'bg-gray-200 text-gray-800 rounded-bl-none'
                                                        : 'bg-white text-gray-800 rounded-bl-none shadow-sm'
                                                }`}>
                                                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                                            </div>

                                            {/* Suggestions */}
                                            {message.suggestions && message.suggestions.length > 0 && (
                                                <div className="mt-2 flex flex-wrap gap-2">
                                                    {message.suggestions.map((suggestion, idx) => (
                                                        <button
                                                            key={idx}
                                                            onClick={() => handleSuggestionClick(suggestion)}
                                                            className="text-xs bg-gray-200 hover:bg-gray-300 rounded-full px-3 py-1 text-gray-700 transition-colors"
                                                        >
                                                            {suggestion}
                                                        </button>
                                                    ))}
                                                </div>
                                            )}

                                            <p className="text-xs text-gray-400 mt-1">
                                                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))}

                            {loading && (
                                <div className="flex justify-start">
                                    <div className="flex gap-2">
                                        <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
                                            <Bot className="w-4 h-4 text-white" />
                                        </div>
                                        <div className="bg-white p-3 rounded-2xl rounded-bl-none shadow-sm">
                                            <Loader className="w-5 h-5 animate-spin text-purple-500" />
                                        </div>
                                    </div>
                                </div>
                            )}

                            <div ref={messagesEndRef} />
                        </div>

                        {/* Quick Actions */}
                        <div className="p-2 border-t border-gray-100 bg-gray-50">
                            <div className="flex gap-2 overflow-x-auto pb-1">
                                {quickActions.map((action, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => setInput(action.action)}
                                        className="flex items-center gap-1 px-3 py-1.5 bg-white rounded-full shadow-sm text-xs text-gray-700 hover:bg-gray-100 whitespace-nowrap"
                                    >
                                        <action.icon className="w-3 h-3" />
                                        {action.label}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Input Area */}
                        <div className="p-4 border-t border-gray-200 bg-white">
                            <div className="flex gap-2">
                                <button
                                    onClick={toggleListening}
                                    className={`p-2 rounded-lg transition-colors ${isListening
                                            ? 'bg-red-100 text-red-600'
                                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                        }`}
                                >
                                    {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                                </button>

                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    placeholder="Ask AROMI anything..."
                                    className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                                />

                                <button
                                    onClick={handleSend}
                                    disabled={!input.trim() || loading}
                                    className="bg-gradient-to-r from-purple-500 to-pink-500 text-white p-2 rounded-lg hover:from-purple-600 hover:to-pink-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    <Send className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    )
}

export default ArogyaCoach