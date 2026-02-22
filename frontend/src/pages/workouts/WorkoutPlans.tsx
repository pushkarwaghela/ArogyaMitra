import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import {
    Calendar,
    Clock,
    Dumbbell,
    Target,
    Play,
    CheckCircle,
    Flame,
    Activity,
    ArrowLeft,
    Award,
    Sparkles,
    RefreshCw,
    Video,
    Info,
    ChevronRight
} from 'lucide-react'
import { toast } from 'react-hot-toast'
import Navbar from '../../components/layout/Navbar'
import BackgroundImage from '../../components/layout/BackgroundImage'
import LoadingSpinner from '../../components/ui/LoadingSpinner'
import ExercisePlayer from './ExercisePlayer'
import { useAuthStore, useWorkoutStore } from "../../stores"
import { workoutApi } from '../../services/api'

interface Exercise {
    id: string
    name: string
    sets: number
    reps: number
    duration?: number
    restTime: number
    videoUrl?: string
    videoTitle?: string
    muscleGroup: string
    difficulty: string
    caloriesBurn: number
}

interface DayWorkout {
    day: string
    dayNumber: number
    focus: string
    exercises: Exercise[]
    totalDuration: number
    totalCalories: number
    isRestDay?: boolean
    completed?: boolean
}

interface WorkoutPlan {
    id: string
    title: string
    description: string
    duration: number
    difficulty: string
    weeklySchedule: DayWorkout[]
    createdAt: string
}

const WorkoutPlans = () => {
    const navigate = useNavigate()
    const { user } = useAuthStore()
    const {
        plans,
        currentPlan,
        fetchPlans,
        generatePlan,
        setActiveWorkout,
        setCurrentExercise,
        completeExercise,
        completeWorkout,
        isLoading: storeLoading
    } = useWorkoutStore()

    const [selectedDay, setSelectedDay] = useState<DayWorkout | null>(null)
    const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null)
    const [activeTab, setActiveTab] = useState('overview')
    const [showPlayer, setShowPlayer] = useState(false)
    const [completedExercises, setCompletedExercises] = useState<Record<string, boolean>>({})
    const [generating, setGenerating] = useState(false)
    const [preferences, setPreferences] = useState({
        fitnessLevel: user?.fitness_level || 'beginner',
        goal: user?.fitness_goal || 'weight_loss',
        preference: user?.workout_preference || 'moderate',
        daysPerWeek: 5,
        duration: 45
    })
    const [showPreferences, setShowPreferences] = useState(false)
    const [loadingDetails, setLoadingDetails] = useState(false)

    useEffect(() => {
        fetchPlans()
    }, [fetchPlans])

    const handleGeneratePlan = () => {
        setShowPreferences(true)
    }

    const handleGenerateWithPreferences = async () => {
        setGenerating(true)
        setShowPreferences(false)

        try {
            const response = await workoutApi.generatePlan(preferences)

            if (response.data.success) {
                toast.success('🎉 New workout plan generated successfully!')
                fetchPlans() // Refresh the list
            }
        } catch (error) {
            console.error('Generation error:', error)
            toast.error('Failed to generate workout plan. Please try again.')
        } finally {
            setGenerating(false)
        }
    }

    const handleStartExercise = (exercise: Exercise, day: DayWorkout) => {
        setCurrentExercise(exercise)
        setActiveWorkout(day)
        setSelectedExercise(exercise)
        setSelectedDay(day)
        setShowPlayer(true)
    }

    const handleExerciseComplete = (exerciseId: string) => {
        setCompletedExercises(prev => ({
            ...prev,
            [exerciseId]: true
        }))
        completeExercise(exerciseId)
        toast.success('Exercise completed! 🎯')
    }

    const handleDayComplete = (day: DayWorkout) => {
        day.exercises.forEach(ex => {
            setCompletedExercises(prev => ({
                ...prev,
                [ex.id]: true
            }))
        })
        completeWorkout(day.dayNumber)
        toast.success(`Day ${day.dayNumber} completed! Great job! 💪`)
    }

    const handleViewPlan = async (plan: WorkoutPlan) => {
        setLoadingDetails(true)
        await fetchPlanDetails(plan.id)
        setLoadingDetails(false)
    }

    if (storeLoading || generating) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center">
                <div className="text-center">
                    <LoadingSpinner size="lg" />
                    {generating && (
                        <p className="mt-4 text-gray-600">AI is creating your personalized workout plan...</p>
                    )}
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
            <BackgroundImage />
            <Navbar />

            <main className="container mx-auto px-4 py-8">
                {/* Header with Generate Button */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8 flex justify-between items-center"
                >
                    <div>
                        <h1 className="text-4xl font-bold text-gray-800 flex items-center gap-3">
                            <Dumbbell className="w-8 h-8 text-blue-500" />
                            Workout Plans
                        </h1>
                        <p className="text-gray-600 mt-2">
                            AI-powered workout routines personalized for your goals
                        </p>
                    </div>
                    <button
                        onClick={handleGeneratePlan}
                        className="bg-gradient-to-r from-blue-500 to-green-500 text-white px-6 py-3 rounded-lg hover:from-blue-600 hover:to-green-600 transition-all flex items-center gap-2 shadow-lg"
                    >
                        <Sparkles className="w-5 h-5" />
                        Generate New Plan
                    </button>
                </motion.div>

                {/* Preferences Modal */}
                <AnimatePresence>
                    {showPreferences && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
                            onClick={() => setShowPreferences(false)}
                        >
                            <motion.div
                                initial={{ scale: 0.9, y: 20 }}
                                animate={{ scale: 1, y: 0 }}
                                exit={{ scale: 0.9, y: 20 }}
                                className="bg-white rounded-2xl max-w-md w-full p-6"
                                onClick={(e) => e.stopPropagation()}
                            >
                                <h2 className="text-2xl font-bold text-gray-800 mb-4">Workout Preferences</h2>

                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Fitness Level
                                        </label>
                                        <select
                                            value={preferences.fitnessLevel}
                                            onChange={(e) => setPreferences({ ...preferences, fitnessLevel: e.target.value })}
                                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                        >
                                            <option value="beginner">Beginner</option>
                                            <option value="intermediate">Intermediate</option>
                                            <option value="advanced">Advanced</option>
                                        </select>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Fitness Goal
                                        </label>
                                        <select
                                            value={preferences.goal}
                                            onChange={(e) => setPreferences({ ...preferences, goal: e.target.value })}
                                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                        >
                                            <option value="weight_loss">Weight Loss</option>
                                            <option value="muscle_gain">Muscle Gain</option>
                                            <option value="maintenance">Maintenance</option>
                                            <option value="endurance">Endurance</option>
                                        </select>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Workout Preference
                                        </label>
                                        <select
                                            value={preferences.preference}
                                            onChange={(e) => setPreferences({ ...preferences, preference: e.target.value })}
                                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                        >
                                            <option value="moderate">Moderate</option>
                                            <option value="high_intensity">High Intensity</option>
                                            <option value="low_intensity">Low Intensity</option>
                                            <option value="yoga">Yoga</option>
                                            <option value="cardio">Cardio</option>
                                        </select>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Days per Week
                                        </label>
                                        <input
                                            type="range"
                                            min="3"
                                            max="7"
                                            value={preferences.daysPerWeek}
                                            onChange={(e) => setPreferences({ ...preferences, daysPerWeek: parseInt(e.target.value) })}
                                            className="w-full"
                                        />
                                        <div className="text-center text-sm text-gray-600 mt-1">
                                            {preferences.daysPerWeek} days/week
                                        </div>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Workout Duration (minutes)
                                        </label>
                                        <input
                                            type="range"
                                            min="20"
                                            max="90"
                                            step="5"
                                            value={preferences.duration}
                                            onChange={(e) => setPreferences({ ...preferences, duration: parseInt(e.target.value) })}
                                            className="w-full"
                                        />
                                        <div className="text-center text-sm text-gray-600 mt-1">
                                            {preferences.duration} minutes
                                        </div>
                                    </div>
                                </div>

                                <div className="flex gap-3 mt-6">
                                    <button
                                        onClick={() => setShowPreferences(false)}
                                        className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={handleGenerateWithPreferences}
                                        className="flex-1 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
                                    >
                                        Generate Plan
                                    </button>
                                </div>
                            </motion.div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Tabs */}
                <div className="flex space-x-4 mb-6">
                    {['overview', 'week', 'history'].map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === tab
                                ? 'bg-blue-500 text-white'
                                : 'bg-white text-gray-600 hover:bg-gray-100'
                                }`}
                        >
                            {tab.charAt(0).toUpperCase() + tab.slice(1)}
                        </button>
                    ))}
                </div>

                {!currentPlan ? (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="bg-white rounded-2xl shadow-lg p-12 text-center"
                    >
                        <Dumbbell className="w-16 h-16 text-blue-300 mx-auto mb-4" />
                        <h2 className="text-2xl font-bold text-gray-800 mb-2">No Active Workout Plan</h2>
                        <p className="text-gray-600 mb-6">
                            Click the "Generate New Plan" button above to create your personalized AI workout plan
                        </p>
                    </motion.div>
                ) : (
                    <>
                        {/* Plan Overview */}
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-white rounded-2xl shadow-lg p-6 mb-8"
                        >
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h2 className="text-2xl font-bold text-gray-800">{currentPlan.title}</h2>
                                    <p className="text-gray-600 mt-1">{currentPlan.description}</p>
                                </div>
                                <span className="bg-blue-100 text-blue-600 px-3 py-1 rounded-full text-sm font-medium">
                                    {currentPlan.difficulty}
                                </span>
                            </div>

                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                                <div className="bg-gray-50 rounded-lg p-3 text-center">
                                    <Calendar className="w-5 h-5 text-blue-500 mx-auto mb-1" />
                                    <p className="text-sm text-gray-500">Duration</p>
                                    <p className="font-semibold">{currentPlan.duration} weeks</p>
                                </div>
                                <div className="bg-gray-50 rounded-lg p-3 text-center">
                                    <Activity className="w-5 h-5 text-green-500 mx-auto mb-1" />
                                    <p className="text-sm text-gray-500">Workouts</p>
                                    <p className="font-semibold">{currentPlan.weeklySchedule?.length || 0}/week</p>
                                </div>
                                <div className="bg-gray-50 rounded-lg p-3 text-center">
                                    <Flame className="w-5 h-5 text-orange-500 mx-auto mb-1" />
                                    <p className="text-sm text-gray-500">Calories/Week</p>
                                    <p className="font-semibold">
                                        {currentPlan.weeklySchedule?.reduce((acc, day) => acc + (day.totalCalories || 0), 0) || 0}
                                    </p>
                                </div>
                                <div className="bg-gray-50 rounded-lg p-3 text-center">
                                    <Target className="w-5 h-5 text-purple-500 mx-auto mb-1" />
                                    <p className="text-sm text-gray-500">Focus</p>
                                    <p className="font-semibold capitalize">{currentPlan.weeklySchedule?.[0]?.focus || 'Full Body'}</p>
                                </div>
                            </div>
                        </motion.div>

                        {/* Weekly Schedule */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            {currentPlan.weeklySchedule?.map((day, index) => (
                                <motion.div
                                    key={index}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                    className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
                                >
                                    <div className={`p-4 ${day.isRestDay ? 'bg-gray-100' : 'bg-gradient-to-r from-blue-500 to-green-500'}`}>
                                        <div className="flex justify-between items-center">
                                            <h3 className={`font-semibold ${day.isRestDay ? 'text-gray-700' : 'text-white'}`}>
                                                Day {day.dayNumber}: {day.focus}
                                            </h3>
                                            {day.completed && (
                                                <CheckCircle className="w-5 h-5 text-green-300" />
                                            )}
                                        </div>
                                        {!day.isRestDay && (
                                            <p className={`text-sm mt-1 ${day.isRestDay ? 'text-gray-600' : 'text-white/90'}`}>
                                                {day.totalDuration} min • {day.exercises?.length || 0} exercises
                                            </p>
                                        )}
                                    </div>

                                    {!day.isRestDay ? (
                                        <div className="p-4">
                                            <div className="space-y-2 mb-4">
                                                {day.exercises?.slice(0, 3).map((exercise, idx) => (
                                                    <div key={idx} className="flex items-center justify-between text-sm">
                                                        <span className="text-gray-600">{exercise.name}</span>
                                                        <span className="text-gray-500">
                                                            {exercise.sets}x{exercise.reps}
                                                        </span>
                                                    </div>
                                                ))}
                                                {(day.exercises?.length || 0) > 3 && (
                                                    <p className="text-xs text-gray-400 text-center mt-2">
                                                        +{(day.exercises?.length || 0) - 3} more exercises
                                                    </p>
                                                )}
                                            </div>

                                            <button
                                                onClick={() => setSelectedDay(day)}
                                                className="w-full bg-blue-50 text-blue-600 py-2 rounded-lg hover:bg-blue-100 transition-colors flex items-center justify-center gap-2"
                                            >
                                                <Play className="w-4 h-4" />
                                                View Workout
                                            </button>
                                        </div>
                                    ) : (
                                        <div className="p-4 text-center text-gray-500">
                                            <p className="text-sm">Rest Day - Recovery</p>
                                        </div>
                                    )}
                                </motion.div>
                            ))}
                        </div>
                    </>
                )}
            </main>

            {/* Exercise Player Modal */}
            <AnimatePresence>
                {showPlayer && selectedExercise && selectedDay && (
                    <ExercisePlayer
                        exercise={selectedExercise}
                        dayWorkout={selectedDay}
                        onClose={() => setShowPlayer(false)}
                        onComplete={() => handleExerciseComplete(selectedExercise.id)}
                    />
                )}
            </AnimatePresence>

            {/* Day Workout Modal */}
            <AnimatePresence>
                {selectedDay && !showPlayer && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
                        onClick={() => setSelectedDay(null)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, y: 20 }}
                            animate={{ scale: 1, y: 0 }}
                            exit={{ scale: 0.9, y: 20 }}
                            className="bg-white rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <div className="p-6">
                                <div className="flex justify-between items-start mb-4">
                                    <div>
                                        <h2 className="text-2xl font-bold text-gray-800">
                                            Day {selectedDay.dayNumber}: {selectedDay.focus}
                                        </h2>
                                        <p className="text-gray-600 mt-1">
                                            {selectedDay.totalDuration} minutes • {selectedDay.exercises?.length || 0} exercises
                                        </p>
                                    </div>
                                    <button
                                        onClick={() => setSelectedDay(null)}
                                        className="text-gray-400 hover:text-gray-600"
                                    >
                                        <ArrowLeft className="w-5 h-5" />
                                    </button>
                                </div>

                                <div className="space-y-4">
                                    {selectedDay.exercises?.map((exercise, idx) => (
                                        <motion.div
                                            key={idx}
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: idx * 0.05 }}
                                            className={`p-4 rounded-lg border ${completedExercises[exercise.id]
                                                ? 'bg-green-50 border-green-200'
                                                : 'bg-gray-50 border-gray-200'
                                                }`}
                                        >
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-2">
                                                        <h3 className="font-semibold text-gray-800">{exercise.name}</h3>
                                                        {completedExercises[exercise.id] && (
                                                            <CheckCircle className="w-4 h-4 text-green-500" />
                                                        )}
                                                    </div>
                                                    <p className="text-sm text-gray-600 mt-1">
                                                        {exercise.sets} sets × {exercise.reps} reps • Rest: {exercise.restTime}s
                                                    </p>
                                                    <p className="text-xs text-gray-500 mt-1">
                                                        {exercise.muscleGroup} • 🔥 {exercise.caloriesBurn} cal
                                                        {exercise.videoUrl && (
                                                            <span className="ml-2 text-blue-500 flex items-center gap-1">
                                                                <Video className="w-3 h-3" /> Video available
                                                            </span>
                                                        )}
                                                    </p>
                                                </div>
                                                <button
                                                    onClick={() => handleStartExercise(exercise, selectedDay)}
                                                    disabled={completedExercises[exercise.id]}
                                                    className={`px-4 py-2 rounded-lg flex items-center gap-2 ${completedExercises[exercise.id]
                                                        ? 'bg-green-100 text-green-600 cursor-not-allowed'
                                                        : 'bg-blue-500 text-white hover:bg-blue-600'
                                                        }`}
                                                >
                                                    <Play className="w-4 h-4" />
                                                    {completedExercises[exercise.id] ? 'Completed' : 'Start'}
                                                </button>
                                            </div>
                                        </motion.div>
                                    ))}
                                </div>

                                <div className="mt-6 flex justify-between">
                                    <button
                                        onClick={() => setSelectedDay(null)}
                                        className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                                    >
                                        Close
                                    </button>
                                    <button
                                        onClick={() => handleDayComplete(selectedDay)}
                                        className="bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600 transition-colors flex items-center gap-2"
                                    >
                                        <Award className="w-4 h-4" />
                                        Complete Day
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    )
}

export default WorkoutPlans