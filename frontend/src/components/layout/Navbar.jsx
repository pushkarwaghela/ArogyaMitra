import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
    Home,
    Dumbbell,
    Utensils,
    BarChart3,
    MessageCircle,
    User,
    LogOut,
    Menu,
    X,
    HeartPulse // Add this for Health Assessment
} from 'lucide-react'
import { useState } from 'react'
import { useAuthStore } from '../../stores/authStore'
import { toast } from 'react-hot-toast'

const Navbar = () => {
    const navigate = useNavigate()
    const { user, logout } = useAuthStore()
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

    const handleLogout = () => {
        logout()
        toast.success('Logged out successfully')
        navigate('/login')
    }

    const navItems = [
        { path: '/dashboard', icon: Home, label: 'Dashboard' },
        { path: '/workouts', icon: Dumbbell, label: 'Workouts' },
        { path: '/nutrition', icon: Utensils, label: 'Nutrition' },
        { path: '/health-assessment', icon: HeartPulse, label: 'Health Assessment' }, // ADD THIS
        { path: '/progress', icon: BarChart3, label: 'Progress' },
        { path: '/aromi', icon: MessageCircle, label: 'AROMI' },
    ]

    return (
        <nav className="bg-white shadow-lg sticky top-0 z-50">
            <div className="container mx-auto px-4">
                <div className="flex justify-between items-center h-16">
                    {/* Logo */}
                    <Link to="/dashboard" className="flex items-center space-x-2">
                        <span className="text-2xl font-bold bg-gradient-to-r from-blue-500 to-green-500 bg-clip-text text-transparent">
                            ArogyaMitra
                        </span>
                    </Link>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center space-x-1">
                        {navItems.map((item) => (
                            <Link
                                key={item.path}
                                to={item.path}
                                className="flex items-center px-4 py-2 text-gray-700 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors"
                            >
                                <item.icon className="w-5 h-5 mr-2" />
                                <span>{item.label}</span>
                            </Link>
                        ))}
                    </div>

                    {/* User Menu */}
                    <div className="hidden md:flex items-center space-x-4">
                        <Link
                            to="/profile"
                            className="flex items-center space-x-2 text-gray-700 hover:text-blue-500"
                        >
                            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-green-500 rounded-full flex items-center justify-center text-white font-semibold">
                                {user?.full_name?.charAt(0) || 'U'}
                            </div>
                            <span className="text-sm font-medium">{user?.full_name || 'User'}</span>
                        </Link>
                        <button
                            onClick={handleLogout}
                            className="p-2 text-gray-500 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                        >
                            <LogOut className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                        className="md:hidden p-2 text-gray-600 hover:text-gray-900"
                    >
                        {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                    </button>
                </div>

                {/* Mobile Navigation */}
                {isMobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="md:hidden py-4 border-t"
                    >
                        {navItems.map((item) => (
                            <Link
                                key={item.path}
                                to={item.path}
                                onClick={() => setIsMobileMenuOpen(false)}
                                className="flex items-center px-4 py-3 text-gray-700 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors"
                            >
                                <item.icon className="w-5 h-5 mr-3" />
                                <span>{item.label}</span>
                            </Link>
                        ))}
                        <div className="border-t my-2 pt-2">
                            <Link
                                to="/profile"
                                onClick={() => setIsMobileMenuOpen(false)}
                                className="flex items-center px-4 py-3 text-gray-700 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors"
                            >
                                <User className="w-5 h-5 mr-3" />
                                <span>Profile</span>
                            </Link>
                            <button
                                onClick={() => {
                                    handleLogout()
                                    setIsMobileMenuOpen(false)
                                }}
                                className="w-full flex items-center px-4 py-3 text-gray-700 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                            >
                                <LogOut className="w-5 h-5 mr-3" />
                                <span>Logout</span>
                            </button>
                        </div>
                    </motion.div>
                )}
            </div>
        </nav>
    )
}

export default Navbar