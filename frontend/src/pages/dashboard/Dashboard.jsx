import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import {
    Sparkles, TrendingUp, Target, Calendar, Heart, Zap, Award,
    Clock, ArrowRight, Plus, Play, MessageCircle, ClipboardList,
    Bot, Flame, Activity, HeartPulse, Salad
} from 'lucide-react'
import Navbar from '../../components/layout/Navbar'
import LoadingSpinner from '../../components/ui/LoadingSpinner'
import CharityImpactCard from '../../components/CharityImpactCard'
import BackgroundImage from '../../components/layout/BackgroundImage'
import { userApi, workoutApi, progressApi } from '../../services/api'
import { useAuthStore } from '../../stores/authStore'

const Dashboard = () => {
    const navigate = useNavigate()
    const { user, isAuthenticated } = useAuthStore()
    const [greeting, setGreeting] = useState('')

    // Fetch user profile
    const { data: profile, isLoading: profileLoading } = useQuery({
        queryKey: ['profile'],
        queryFn: async () => {
            const response = await userApi.getProfile()
            return response.data
        },
        enabled: isAuthenticated
    })

    // Fetch progress stats
    const { data: stats, isLoading: statsLoading } = useQuery({
        queryKey: ['stats'],
        queryFn: async () => {
            const response = await progressApi.getStats()
            return response.data
        },
        enabled: isAuthenticated
    })

    // Fetch active workout
    const { data: activeWorkout, isLoading: workoutLoading } = useQuery({
        queryKey: ['activeWorkout'],
        queryFn: async () => {
            try {
                const response = await workoutApi.getActiveWorkout()
                return response.data
            } catch {
                return null
            }
        },
        enabled: isAuthenticated
    })

    // Fetch upcoming workouts
    const { data: upcomingWorkouts } = useQuery({
        queryKey: ['upcomingWorkouts'],
        queryFn: async () => {
            try {
                const response = await workoutApi.getPlans()
                const plan = response.data[0]
                return plan?.weeklySchedule?.slice(0, 3) || []
            } catch {
                return []
            }
        },
        enabled: isAuthenticated
    })

    useEffect(() => {
        const hour = new Date().getHours()
        if (hour < 12) setGreeting('Good morning')
        else if (hour < 18) setGreeting('Good afternoon')
        else setGreeting('Good evening')
    }, [])

    if (profileLoading || statsLoading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center">
                <LoadingSpinner size="lg" />
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
            <BackgroundImage />
            <Navbar />

            <main className="container mx-auto px-4 py-8">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8"
                >
                    <h1 className="text-4xl font-bold text-gray-800">
                        {greeting}, {profile?.full_name || user?.full_name || 'Fitness Warrior'}! 👋
                    </h1>
                    <p className="text-gray-600 mt-2">
                        Ready to crush your fitness goals today?
                    </p>
                </motion.div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <div className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-orange-500">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-gray-500 text-sm">Current Streak</p>
                                <p className="text-3xl font-bold text-gray-800">{stats?.currentStreak || 0} days</p>
                            </div>
                            <div className="bg-orange-100 p-3 rounded-full">
                                <Flame className="w-6 h-6 text-orange-500" />
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-green-500">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-gray-500 text-sm">Calories Burned</p>
                                <p className="text-3xl font-bold text-gray-800">{stats?.totalCaloriesBurned || 0}</p>
                            </div>
                            <div className="bg-green-100 p-3 rounded-full">
                                <Zap className="w-6 h-6 text-green-500" />
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-blue-500">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-gray-500 text-sm">Total Workouts</p>
                                <p className="text-3xl font-bold text-gray-800">{stats?.totalWorkouts || 0}</p>
                            </div>
                            <div className="bg-blue-100 p-3 rounded-full">
                                <Activity className="w-6 h-6 text-blue-500" />
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-purple-500">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-gray-500 text-sm">Current Weight</p>
                                <p className="text-3xl font-bold text-gray-800">{profile?.weight || user?.weight || '--'} kg</p>
                            </div>
                            <div className="bg-purple-100 p-3 rounded-full">
                                <Target className="w-6 h-6 text-purple-500" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Left Column - Active Plan & Progress */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Active Workout Plan */}
                        <div className="bg-white rounded-2xl shadow-lg p-6">
                            <div className="flex justify-between items-center mb-4">
                                <h2 className="text-xl font-semibold text-gray-800 flex items-center gap-2">
                                    <Activity className="w-5 h-5 text-blue-500" />
                                    Active Workout Plan
                                </h2>
                                <Link
                                    to="/workouts"
                                    className="text-blue-500 hover:text-blue-600 text-sm flex items-center gap-1"
                                >
                                    View All <ArrowRight className="w-4 h-4" />
                                </Link>
                            </div>
                            {activeWorkout ? (
                                <div>
                                    <h3 className="font-semibold text-lg text-gray-800">{activeWorkout.title}</h3>
                                    <p className="text-gray-600 mt-2">{activeWorkout.description}</p>
                                    <button className="mt-4 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2">
                                        <Play className="w-4 h-4" /> Start Today's Workout
                                    </button>
                                </div>
                            ) : (
                                <div className="text-center py-8">
                                    <p className="text-gray-500 mb-4">No active workout plan</p>
                                    <Link
                                        to="/workouts"
                                        className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 inline-flex items-center gap-2"
                                    >
                                        <Plus className="w-4 h-4" /> Generate Plan
                                    </Link>
                                </div>
                            )}
                        </div>

                        {/* Upcoming Workouts */}
                        <div className="bg-white rounded-2xl shadow-lg p-6">
                            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                                <Calendar className="w-5 h-5 text-green-500" />
                                Upcoming Workouts
                            </h2>
                            {upcomingWorkouts?.length > 0 ? (
                                <div className="space-y-3">
                                    {upcomingWorkouts.map((workout, idx) => (
                                        <div key={idx} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                                            <div>
                                                <p className="font-medium text-gray-800">Day {workout.dayNumber}: {workout.focus}</p>
                                                <p className="text-sm text-gray-500">{workout.exercises?.length || 0} exercises</p>
                                            </div>
                                            <button className="text-blue-500 hover:text-blue-600">
                                                <Play className="w-5 h-5" />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-gray-500 text-center py-4">No upcoming workouts</p>
                            )}
                        </div>
                    </div>

                    {/* Right Column - AROMI, Health Assessment & Charity */}
                    <div className="space-y-6">
                        {/* AROMI Coach Card */}
                        <div className="bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl shadow-lg p-6 text-white">
                            <h2 className="text-xl font-semibold mb-2 flex items-center gap-2">
                                <Bot className="w-6 h-6" />
                                AROMI AI Coach
                            </h2>
                            <p className="text-sm opacity-90 mb-4">
                                Ask me anything about workouts, nutrition, or motivation!
                            </p>
                            <Link
                                to="/aromi"
                                className="block w-full bg-white text-purple-600 text-center py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors"
                            >
                                Chat with AROMI
                            </Link>
                        </div>

                        {/* Health Assessment Card */}
                        <div className="bg-gradient-to-br from-green-500 to-teal-500 rounded-2xl shadow-lg p-6 text-white">
                            <h2 className="text-xl font-semibold mb-2 flex items-center gap-2">
                                <HeartPulse className="w-6 h-6" />
                                Health Assessment
                            </h2>
                            <p className="text-sm opacity-90 mb-4">
                                Complete your health profile for personalized plans
                            </p>
                            <Link
                                to="/health-assessment"
                                className="block w-full bg-white text-green-600 text-center py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors"
                            >
                                Start Assessment
                            </Link>
                        </div>

                        {/* Charity Impact Card */}
                        <CharityImpactCard
                            totalWorkouts={stats?.totalWorkouts || 0}
                            streak={stats?.currentStreak || 0}
                            caloriesBurned={stats?.totalCaloriesBurned || 0}
                        />
                    </div>
                </div>
            </main>
        </div>
    )
}

export default Dashboard