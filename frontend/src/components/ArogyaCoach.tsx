import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Bot, X, Send, MessageCircle } from 'lucide-react'

const ArogyaCoach = () => {
    const [isOpen, setIsOpen] = useState(false)
    const [messages, setMessages] = useState<Array<{ text: string; isUser: boolean }>>([
        { text: "Hi! I'm AROMI, your AI fitness coach. How can I help you today?", isUser: false }
    ])
    const [input, setInput] = useState('')

    const handleSend = () => {
        if (!input.trim()) return

        // Add user message
        setMessages(prev => [...prev, { text: input, isUser: true }])

        // Simulate AI response
        setTimeout(() => {
            setMessages(prev => [...prev, {
                text: "Thanks for your message! I'm here to help with your fitness journey. What would you like to know about?",
                isUser: false
            }])
        }, 1000)

        setInput('')
    }

    return (
        <>
            {/* Chat Button */}
            <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => setIsOpen(true)}
                className="fixed bottom-6 right-6 bg-gradient-to-r from-purple-500 to-pink-500 text-white p-4 rounded-full shadow-lg z-50"
            >
                <MessageCircle className="w-6 h-6" />
            </motion.button>

            {/* Chat Window */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 50, scale: 0.9 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 50, scale: 0.9 }}
                        className="fixed bottom-20 right-6 w-96 bg-white rounded-2xl shadow-2xl z-50 overflow-hidden"
                    >
                        {/* Header */}
                        <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-4 text-white flex justify-between items-center">
                            <div className="flex items-center gap-2">
                                <Bot className="w-5 h-5" />
                                <span className="font-semibold">AROMI Coach</span>
                            </div>
                            <button
                                onClick={() => setIsOpen(false)}
                                className="hover:bg-white/20 rounded-lg p-1 transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Messages */}
                        <div className="h-96 overflow-y-auto p-4 space-y-4">
                            {messages.map((msg, index) => (
                                <div
                                    key={index}
                                    className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div
                                        className={`max-w-[80%] p-3 rounded-lg ${msg.isUser
                                                ? 'bg-purple-500 text-white rounded-br-none'
                                                : 'bg-gray-100 text-gray-800 rounded-bl-none'
                                            }`}
                                    >
                                        {msg.text}
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Input */}
                        <div className="p-4 border-t">
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                                    placeholder="Ask me anything..."
                                    className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                                />
                                <button
                                    onClick={handleSend}
                                    className="bg-purple-500 text-white p-2 rounded-lg hover:bg-purple-600 transition-colors"
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