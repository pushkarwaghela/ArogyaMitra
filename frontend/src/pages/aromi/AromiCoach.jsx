import React, { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
    Bot,
    Send,
    User,
    Mic,
    MicOff,
    Sparkles,
    Dumbbell,
    Utensils,
    Heart,
    Calendar,
    X
} from 'lucide-react'
import Navbar from '../../components/layout/Navbar'
import BackgroundImage from '../../components/layout/BackgroundImage'
import { aromiApi } from '../../services/api'
import { toast } from 'react-hot-toast'
import { useAuthStore } from '../../stores/authStore'

const AromiCoach = () => {
    const { user } = useAuthStore()
    const [messages, setMessages] = useState([
        {
            id: 1,
            type: 'bot',
            content: `Hi ${user?.full_name || 'there'}! I'm AROMI, your AI fitness coach. How can I help you today?`,
            timestamp: new Date().toISOString()
        }
    ])
    const [input, setInput] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [isListening, setIsListening] = useState(false)
    const messagesEndRef = useRef(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const handleSend = async () => {
        if (!input.trim() || isLoading) return

        const userMessage = {
            id: messages.length + 1,
            type: 'user',
            content: input,
            timestamp: new Date().toISOString()
        }

        setMessages(prev => [...prev, userMessage])
        setInput('')
        setIsLoading(true)

        try {
            const response = await aromiApi.chat(input, null)

            const botMessage = {
                id: messages.length + 2,
                type: 'bot',
                content: response.data.response,
                timestamp: new Date().toISOString(),
                suggestions: response.data.suggestions
            }

            setMessages(prev => [...prev, botMessage])
        } catch (error) {
            console.error('Chat error:', error)
            // Fallback response
            setMessages(prev => [...prev, {
                id: messages.length + 2,
                type: 'bot',
                content: "I'm here to help! You can ask me about workouts, nutrition, motivation, or adjusting your plan.",
                timestamp: new Date().toISOString()
            }])
        } finally {
            setIsLoading(false)
        }
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
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

    const quickQuestions = [
        { icon: Dumbbell, text: 'Generate a workout' },
        { icon: Utensils, text: 'Meal plan suggestions' },
        { icon: Heart, text: 'I need motivation' },
        { icon: Calendar, text: 'Adjust for travel' }
    ]

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
            <BackgroundImage />
            <Navbar />

            <main className="container mx-auto px-4 py-8 max-w-4xl">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8"
                >
                    <h1 className="text-4xl font-bold text-gray-800 flex items-center gap-3">
                        <Bot className="w-8 h-8 text-purple-500" />
                        AROMI AI Coach
                    </h1>
                    <p className="text-gray-600 mt-2">
                        Your personal AI fitness assistant - ask me anything!
                    </p>
                </motion.div>

                {/* Quick Questions */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
                    {quickQuestions.map((q, index) => (
                        <button
                            key={index}
                            onClick={() => setInput(q.text)}
                            className="bg-white p-3 rounded-lg shadow hover:shadow-md transition-shadow flex items-center justify-center gap-2 text-gray-700"
                        >
                            <q.icon className="w-4 h-4 text-purple-500" />
                            <span className="text-sm">{q.text}</span>
                        </button>
                    ))}
                </div>

                {/* Chat Container */}
                <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
                    {/* Messages */}
                    <div className="h-[500px] overflow-y-auto p-6 space-y-4">
                        {messages.map((message) => (
                            <motion.div
                                key={message.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div className={`flex gap-3 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse' : ''}`}>
                                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${message.type === 'user'
                                            ? 'bg-blue-100'
                                            : 'bg-gradient-to-r from-purple-500 to-pink-500'
                                        }`}>
                                        {message.type === 'user'
                                            ? <User className="w-4 h-4 text-blue-600" />
                                            : <Bot className="w-4 h-4 text-white" />
                                        }
                                    </div>
                                    <div>
                                        <div className={`p-4 rounded-2xl ${message.type === 'user'
                                                ? 'bg-blue-500 text-white rounded-br-none'
                                                : 'bg-gray-100 text-gray-800 rounded-bl-none'
                                            }`}>
                                            <p className="whitespace-pre-wrap">{message.content}</p>
                                        </div>
                                        {message.suggestions && message.suggestions.length > 0 && (
                                            <div className="mt-2 flex flex-wrap gap-2">
                                                {message.suggestions.map((suggestion, idx) => (
                                                    <button
                                                        key={idx}
                                                        onClick={() => setInput(suggestion)}
                                                        className="text-xs bg-gray-200 hover:bg-gray-300 rounded-full px-3 py-1 text-gray-700"
                                                    >
                                                        {suggestion}
                                                    </button>
                                                ))}
                                            </div>
                                        )}
                                        <p className="text-xs text-gray-400 mt-1">
                                            {new Date(message.timestamp).toLocaleTimeString()}
                                        </p>
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="flex gap-3">
                                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
                                        <Bot className="w-4 h-4 text-white" />
                                    </div>
                                    <div className="bg-gray-100 rounded-2xl rounded-bl-none p-4">
                                        <div className="flex gap-1">
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area */}
                    <div className="p-4 border-t">
                        <div className="flex gap-2">
                            <button
                                onClick={toggleListening}
                                className={`p-3 rounded-lg transition-colors ${isListening
                                        ? 'bg-red-500 text-white'
                                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                    }`}
                            >
                                {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                            </button>

                            <textarea
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder="Ask me anything about your fitness journey..."
                                className="flex-1 px-4 py-3 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                                rows="1"
                                style={{ minHeight: '50px', maxHeight: '150px' }}
                            />

                            <button
                                onClick={handleSend}
                                disabled={!input.trim() || isLoading}
                                className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                            >
                                <Send className="w-5 h-5" />
                                Send
                            </button>
                        </div>
                        <p className="text-xs text-gray-400 mt-2 text-center">
                            AROMI is here to help with workouts, nutrition, motivation, and plan adjustments
                        </p>
                    </div>
                </div>
            </main>
        </div>
    )
}

export default AromiCoach