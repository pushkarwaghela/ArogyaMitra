import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import {
    Heart,
    Activity,
    AlertCircle,
    CheckCircle,
    ArrowLeft,
    ArrowRight,
    User,
    Scale,
    Ruler,
    Calendar,
    Droplets,
    Brain,
    Shield,
    Info,
    Loader2
} from 'lucide-react'
import { toast } from 'react-hot-toast'
import Navbar from '../../components/layout/Navbar'
import BackgroundImage from '../../components/layout/BackgroundImage'
import { healthApi } from '../../services/api'
import { useAuthStore } from '../../stores/authStore'

interface Question {
    id: string
    text: string
    type: 'text' | 'select' | 'multiselect' | 'yesno' | 'number'
    options?: string[]
    placeholder?: string
    category: 'medical' | 'lifestyle' | 'fitness' | 'dietary'
    required?: boolean
}

interface HealthAssessmentData {
    // Personal Info
    age: number
    gender: string
    height: number
    weight: number

    // Medical History
    medicalConditions: string[]
    injuries: string[]
    medications: string[]
    allergies: string[]

    // Lifestyle
    sleepHours: number
    stressLevel: number
    waterIntake: number
    smoking: boolean
    alcohol: boolean

    // Fitness
    fitnessLevel: 'beginner' | 'intermediate' | 'advanced'
    workoutFrequency: number
    preferredWorkoutTime: 'morning' | 'afternoon' | 'evening'
    previousExperience: string

    // Dietary
    dietType: string
    foodAllergies: string[]
    mealPrepTime: number
    cookingSkill: 'beginner' | 'intermediate' | 'advanced'
}

const HealthAssessment: React.FC = () => {
    const navigate = useNavigate()
    const { user } = useAuthStore()
    const [currentStep, setCurrentStep] = useState(0)
    const [answers, setAnswers] = useState<Record<string, any>>({})
    const [bodyMetrics, setBodyMetrics] = useState({
        age: user?.age || 30,
        gender: user?.gender || 'male',
        height: user?.height || 170,
        weight: user?.weight || 70,
        bmi: 0
    })

    // Calculate BMI
    useEffect(() => {
        const heightInM = bodyMetrics.height / 100
        const bmi = bodyMetrics.weight / (heightInM * heightInM)
        setBodyMetrics(prev => ({ ...prev, bmi: parseFloat(bmi.toFixed(1)) }))
    }, [bodyMetrics.height, bodyMetrics.weight])

    const questions: Question[] = [
        // Medical History
        {
            id: 'medical_conditions',
            text: 'Do you have any existing medical conditions?',
            type: 'multiselect',
            options: ['None', 'High Blood Pressure', 'Diabetes', 'Heart Disease', 'Asthma', 'Arthritis', 'Thyroid Issues', 'Other'],
            category: 'medical'
        },
        {
            id: 'injuries',
            text: 'Do you have any current or past injuries?',
            type: 'multiselect',
            options: ['None', 'Back Pain', 'Knee Injury', 'Shoulder Injury', 'Ankle Sprain', 'Muscle Strain', 'Joint Pain', 'Other'],
            category: 'medical'
        },
        {
            id: 'medications',
            text: 'Are you taking any medications?',
            type: 'multiselect',
            options: ['None', 'Blood Pressure Meds', 'Diabetes Meds', 'Pain Relievers', 'Antidepressants', 'Allergy Meds', 'Other'],
            category: 'medical'
        },
        {
            id: 'allergies',
            text: 'Do you have any allergies?',
            type: 'multiselect',
            options: ['None', 'Peanuts', 'Tree Nuts', 'Dairy', 'Eggs', 'Gluten', 'Shellfish', 'Soy', 'Other'],
            category: 'medical'
        },

        // Lifestyle
        {
            id: 'sleep_hours',
            text: 'How many hours of sleep do you typically get?',
            type: 'select',
            options: ['Less than 5', '5-6 hours', '7-8 hours', '9+ hours'],
            category: 'lifestyle'
        },
        {
            id: 'stress_level',
            text: 'How would you rate your stress level?',
            type: 'select',
            options: ['Very Low', 'Low', 'Moderate', 'High', 'Very High'],
            category: 'lifestyle'
        },
        {
            id: 'water_intake',
            text: 'How many glasses of water do you drink daily?',
            type: 'select',
            options: ['Less than 3', '3-5 glasses', '6-8 glasses', '8+ glasses'],
            category: 'lifestyle'
        },
        {
            id: 'smoking',
            text: 'Do you smoke?',
            type: 'yesno',
            category: 'lifestyle'
        },
        {
            id: 'alcohol',
            text: 'Do you consume alcohol?',
            type: 'yesno',
            category: 'lifestyle'
        },

        // Fitness
        {
            id: 'fitness_level',
            text: 'How would you describe your current fitness level?',
            type: 'select',
            options: ['Beginner', 'Intermediate', 'Advanced'],
            category: 'fitness'
        },
        {
            id: 'workout_frequency',
            text: 'How many days per week can you workout?',
            type: 'select',
            options: ['1-2 days', '3-4 days', '5-6 days', 'Daily'],
            category: 'fitness'
        },
        {
            id: 'workout_time',
            text: 'What time of day do you prefer to workout?',
            type: 'select',
            options: ['Morning', 'Afternoon', 'Evening'],
            category: 'fitness'
        },
        {
            id: 'previous_experience',
            text: 'Do you have any previous fitness experience?',
            type: 'text',
            placeholder: 'E.g., gym training, sports, yoga, etc.',
            category: 'fitness'
        },

        // Dietary
        {
            id: 'diet_type',
            text: 'What type of diet do you follow?',
            type: 'select',
            options: ['Vegetarian', 'Vegan', 'Non-Vegetarian', 'Keto', 'Paleo', 'Mediterranean', 'None'],
            category: 'dietary'
        },
        {
            id: 'food_allergies',
            text: 'Do you have any food allergies?',
            type: 'multiselect',
            options: ['None', 'Peanuts', 'Tree Nuts', 'Dairy', 'Eggs', 'Gluten', 'Shellfish', 'Soy'],
            category: 'dietary'
        },
        {
            id: 'meal_prep_time',
            text: 'How much time can you spend on meal prep?',
            type: 'select',
            options: ['Less than 30 mins', '30-60 mins', '1-2 hours', '2+ hours'],
            category: 'dietary'
        },
        {
            id: 'cooking_skill',
            text: 'How would you rate your cooking skills?',
            type: 'select',
            options: ['Beginner', 'Intermediate', 'Advanced'],
            category: 'dietary'
        }
    ]

    const categories = [
        { id: 'medical', label: 'Medical History', icon: Heart, color: 'red' },
        { id: 'lifestyle', label: 'Lifestyle', icon: Activity, color: 'blue' },
        { id: 'fitness', label: 'Fitness', icon: Brain, color: 'green' },
        { id: 'dietary', label: 'Dietary', icon: Droplets, color: 'purple' }
    ]

    const submitAssessmentMutation = useMutation({
        mutationFn: (assessmentData: any) => healthApi.submitAssessment(assessmentData),
        onSuccess: () => {
            toast.success('✅ Health assessment completed successfully!')
            navigate('/dashboard')
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.detail || 'Failed to submit assessment')
        }
    })

    const handleNext = () => {
        if (currentStep < questions.length - 1) {
            setCurrentStep(prev => prev + 1)
        } else {
            handleSubmit()
        }
    }

    const handlePrevious = () => {
        if (currentStep > 0) {
            setCurrentStep(prev => prev - 1)
        }
    }

    const handleAnswer = (questionId: string, value: any) => {
        setAnswers(prev => ({ ...prev, [questionId]: value }))
    }

    const handleSubmit = () => {
        const assessmentData: HealthAssessmentData = {
            age: bodyMetrics.age,
            gender: bodyMetrics.gender,
            height: bodyMetrics.height,
            weight: bodyMetrics.weight,
            medicalConditions: answers['medical_conditions'] || ['None'],
            injuries: answers['injuries'] || ['None'],
            medications: answers['medications'] || ['None'],
            allergies: answers['allergies'] || ['None'],
            sleepHours: answers['sleep_hours'] || '7-8 hours',
            stressLevel: answers['stress_level'] || 'Moderate',
            waterIntake: answers['water_intake'] || '6-8 glasses',
            smoking: answers['smoking'] === 'yes',
            alcohol: answers['alcohol'] === 'yes',
            fitnessLevel: (answers['fitness_level'] || 'Beginner').toLowerCase() as any,
            workoutFrequency: parseInt(answers['workout_frequency']?.split('-')[0] || '3'),
            preferredWorkoutTime: (answers['workout_time'] || 'Morning').toLowerCase() as any,
            previousExperience: answers['previous_experience'] || '',
            dietType: answers['diet_type'] || 'Vegetarian',
            foodAllergies: answers['food_allergies'] || ['None'],
            mealPrepTime: parseInt(answers['meal_prep_time']?.split(' ')[0] || '30'),
            cookingSkill: (answers['cooking_skill'] || 'Intermediate').toLowerCase() as any
        }

        // Call the AI-powered health analysis endpoint
        const analysisData = {
            age: bodyMetrics.age,
            gender: bodyMetrics.gender,
            height: bodyMetrics.height,
            weight: bodyMetrics.weight,
            bmi: bodyMetrics.bmi,
            medical_history: answers['medical_conditions']?.join(', ') || 'None',
            injuries: answers['injuries']?.join(', ') || 'None',
            allergies: answers['allergies']?.join(', ') || 'None',
            medications: answers['medications']?.join(', ') || 'None',
            health_conditions: answers['medical_conditions']?.join(', ') || 'None',
            fitness_level: assessmentData.fitnessLevel,
            fitness_goal: user?.fitness_goal || 'general fitness'
        }

        submitAssessmentMutation.mutate(analysisData)
    }

    const currentQuestion = questions[currentStep]
    const currentCategory = categories.find(c => c.id === currentQuestion?.category)

    const progress = ((currentStep + 1) / questions.length) * 100

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
            <BackgroundImage />
            <Navbar />

            <main className="container mx-auto px-4 py-8 max-w-3xl">
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8"
                >
                    <h1 className="text-4xl font-bold text-gray-800 flex items-center gap-3">
                        <Heart className="w-8 h-8 text-red-500" />
                        Health Assessment
                    </h1>
                    <p className="text-gray-600 mt-2">
                        Help us understand your health profile for personalized recommendations
                    </p>
                </motion.div>

                {/* Progress Bar */}
                <div className="bg-white rounded-full h-2 mb-8">
                    <motion.div
                        className="h-full bg-gradient-to-r from-blue-500 to-green-500 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${progress}%` }}
                        transition={{ duration: 0.3 }}
                    />
                </div>

                {/* Body Metrics Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white rounded-2xl shadow-lg p-6 mb-6"
                >
                    <h2 className="text-xl font-semibold text-gray-800 mb-4">Body Metrics</h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                            <label className="block text-sm text-gray-600 mb-1">Age</label>
                            <div className="flex items-center gap-2">
                                <Calendar className="w-5 h-5 text-gray-400" />
                                <input
                                    type="number"
                                    value={bodyMetrics.age}
                                    onChange={(e) => setBodyMetrics(prev => ({ ...prev, age: parseInt(e.target.value) }))}
                                    className="w-20 px-2 py-1 border rounded"
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm text-gray-600 mb-1">Gender</label>
                            <select
                                value={bodyMetrics.gender}
                                onChange={(e) => setBodyMetrics(prev => ({ ...prev, gender: e.target.value }))}
                                className="px-2 py-1 border rounded"
                            >
                                <option value="male">Male</option>
                                <option value="female">Female</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm text-gray-600 mb-1">Height (cm)</label>
                            <div className="flex items-center gap-2">
                                <Ruler className="w-5 h-5 text-gray-400" />
                                <input
                                    type="number"
                                    value={bodyMetrics.height}
                                    onChange={(e) => setBodyMetrics(prev => ({ ...prev, height: parseInt(e.target.value) }))}
                                    className="w-20 px-2 py-1 border rounded"
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm text-gray-600 mb-1">Weight (kg)</label>
                            <div className="flex items-center gap-2">
                                <Scale className="w-5 h-5 text-gray-400" />
                                <input
                                    type="number"
                                    value={bodyMetrics.weight}
                                    onChange={(e) => setBodyMetrics(prev => ({ ...prev, weight: parseInt(e.target.value) }))}
                                    className="w-20 px-2 py-1 border rounded"
                                />
                            </div>
                        </div>
                    </div>
                    <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                        <p className="text-sm text-blue-700">
                            Your BMI: <span className="font-bold">{bodyMetrics.bmi}</span> -
                            {bodyMetrics.bmi < 18.5 ? ' Underweight' :
                                bodyMetrics.bmi < 25 ? ' Normal weight' :
                                    bodyMetrics.bmi < 30 ? ' Overweight' : ' Obese'}
                        </p>
                    </div>
                </motion.div>

                {/* Question Card */}
                <AnimatePresence mode="wait">
                    <motion.div
                        key={currentStep}
                        initial={{ opacity: 0, x: 50 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -50 }}
                        className="bg-white rounded-2xl shadow-lg p-8"
                    >
                        {/* Category Badge */}
                        {currentCategory && (
                            <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm mb-6 bg-${currentCategory.color}-100 text-${currentCategory.color}-600`}>
                                <currentCategory.icon className="w-4 h-4" />
                                {currentCategory.label}
                            </div>
                        )}

                        {/* Question */}
                        <h2 className="text-2xl font-bold text-gray-800 mb-6">
                            {currentQuestion.text}
                        </h2>

                        {/* Answer Input */}
                        <div className="space-y-4">
                            {currentQuestion.type === 'select' && (
                                <select
                                    value={answers[currentQuestion.id] || ''}
                                    onChange={(e) => handleAnswer(currentQuestion.id, e.target.value)}
                                    className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="">Select an option</option>
                                    {currentQuestion.options?.map(opt => (
                                        <option key={opt} value={opt}>{opt}</option>
                                    ))}
                                </select>
                            )}

                            {currentQuestion.type === 'multiselect' && (
                                <div className="space-y-2">
                                    {currentQuestion.options?.map(opt => (
                                        <label key={opt} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100">
                                            <input
                                                type="checkbox"
                                                checked={answers[currentQuestion.id]?.includes(opt) || false}
                                                onChange={(e) => {
                                                    const current = answers[currentQuestion.id] || []
                                                    const newValue = e.target.checked
                                                        ? [...current, opt]
                                                        : current.filter((v: string) => v !== opt)
                                                    handleAnswer(currentQuestion.id, newValue)
                                                }}
                                                className="w-4 h-4 text-blue-500"
                                            />
                                            <span className="text-gray-700">{opt}</span>
                                        </label>
                                    ))}
                                </div>
                            )}

                            {currentQuestion.type === 'yesno' && (
                                <div className="flex gap-4">
                                    <button
                                        onClick={() => handleAnswer(currentQuestion.id, 'yes')}
                                        className={`flex-1 py-3 rounded-lg border-2 transition-colors ${answers[currentQuestion.id] === 'yes'
                                                ? 'border-green-500 bg-green-50 text-green-700'
                                                : 'border-gray-200 hover:border-gray-300'
                                            }`}
                                    >
                                        Yes
                                    </button>
                                    <button
                                        onClick={() => handleAnswer(currentQuestion.id, 'no')}
                                        className={`flex-1 py-3 rounded-lg border-2 transition-colors ${answers[currentQuestion.id] === 'no'
                                                ? 'border-red-500 bg-red-50 text-red-700'
                                                : 'border-gray-200 hover:border-gray-300'
                                            }`}
                                    >
                                        No
                                    </button>
                                </div>
                            )}

                            {currentQuestion.type === 'text' && (
                                <input
                                    type="text"
                                    value={answers[currentQuestion.id] || ''}
                                    onChange={(e) => handleAnswer(currentQuestion.id, e.target.value)}
                                    placeholder={currentQuestion.placeholder}
                                    className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            )}

                            {currentQuestion.type === 'number' && (
                                <input
                                    type="number"
                                    value={answers[currentQuestion.id] || ''}
                                    onChange={(e) => handleAnswer(currentQuestion.id, parseInt(e.target.value))}
                                    placeholder={currentQuestion.placeholder}
                                    className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                />
                            )}
                        </div>

                        {/* Navigation */}
                        <div className="flex justify-between mt-8">
                            <button
                                onClick={handlePrevious}
                                disabled={currentStep === 0}
                                className="px-6 py-2 text-gray-600 hover:bg-gray-100 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                            >
                                <ArrowLeft className="w-4 h-4" />
                                Previous
                            </button>
                            <button
                                onClick={handleNext}
                                disabled={submitAssessmentMutation.isPending}
                                className="px-6 py-2 bg-gradient-to-r from-blue-500 to-green-500 text-white rounded-lg hover:from-blue-600 hover:to-green-600 disabled:opacity-50 flex items-center gap-2"
                            >
                                {currentStep === questions.length - 1 ? (
                                    submitAssessmentMutation.isPending ? (
                                        <>
                                            <Loader2 className="w-4 h-4 animate-spin" />
                                            Submitting...
                                        </>
                                    ) : (
                                        <>
                                            Submit
                                            <CheckCircle className="w-4 h-4" />
                                        </>
                                    )
                                ) : (
                                    <>
                                        Next
                                        <ArrowRight className="w-4 h-4" />
                                    </>
                                )}
                            </button>
                        </div>
                    </motion.div>
                </AnimatePresence>
            </main>
        </div>
    )
}

export default HealthAssessment