import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { User, Mail, Lock, Phone, Calendar, Ruler, Weight, Dumbbell, Utensils, Heart, AlertCircle } from 'lucide-react'
import { authApi } from '../../services/api'
import { toast } from 'react-hot-toast'

const Register = () => {
    const navigate = useNavigate()
    const [step, setStep] = useState(1)
    const [loading, setLoading] = useState(false)
    const [formData, setFormData] = useState({
        // Account Info
        email: '',
        username: '',
        password: '',
        confirmPassword: '',
        full_name: '',

        // Personal Info
        age: '',
        gender: '',
        height: '',
        weight: '',
        phone: '',

        // Fitness Goals
        fitness_level: 'beginner',
        fitness_goal: 'weight_loss',
        workout_preference: 'moderate',
        diet_preference: 'vegetarian',

        // Health Info
        medical_conditions: '',
        allergies: '',
        injuries: '',
        medications: ''
    })

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        })
    }

    const handleNext = () => {
        // Validate step 1
        if (step === 1) {
            if (!formData.email || !formData.username || !formData.password || !formData.full_name) {
                toast.error('Please fill all required fields')
                return
            }
            if (formData.password !== formData.confirmPassword) {
                toast.error('Passwords do not match')
                return
            }
            if (formData.password.length < 8) {
                toast.error('Password must be at least 8 characters')
                return
            }
        }
        setStep(step + 1)
    }

    const handlePrev = () => {
        setStep(step - 1)
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)

        try {
            const registrationData = {
                email: formData.email,
                username: formData.username,
                password: formData.password,
                full_name: formData.full_name,
                age: parseInt(formData.age) || null,
                gender: formData.gender || null,
                height: parseFloat(formData.height) || null,
                weight: parseFloat(formData.weight) || null,
                phone: formData.phone || null,
                fitness_level: formData.fitness_level,
                fitness_goal: formData.fitness_goal,
                workout_preference: formData.workout_preference,
                diet_preference: formData.diet_preference,
                medical_conditions: formData.medical_conditions || 'None',
                allergies: formData.allergies || 'None',
                injuries: formData.injuries || 'None',
                medications: formData.medications || 'None'
            }

            const response = await authApi.register(registrationData)

            if (response.data) {
                toast.success('Registration successful! Please login.')
                navigate('/login')
            }
        } catch (error) {
            console.error('Registration error:', error)
            toast.error(error.response?.data?.detail || 'Registration failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 py-12 px-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="max-w-3xl mx-auto bg-white rounded-2xl shadow-xl overflow-hidden"
            >
                {/* Header */}
                <div className="bg-gradient-to-r from-blue-500 to-green-500 px-8 py-6">
                    <h1 className="text-3xl font-bold text-white">Create Your Account</h1>
                    <p className="text-blue-100 mt-2">Join ArogyaMitra for personalized fitness journey</p>
                </div>

                {/* Progress Steps */}
                <div className="flex justify-between px-8 pt-6 pb-2 border-b">
                    {[1, 2, 3, 4].map((s) => (
                        <div key={s} className="flex items-center">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= s ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-500'
                                }`}>
                                {s}
                            </div>
                            <div className={`ml-2 text-sm ${step >= s ? 'text-green-600 font-medium' : 'text-gray-400'
                                }`}>
                                {s === 1 && 'Account'}
                                {s === 2 && 'Personal'}
                                {s === 3 && 'Fitness'}
                                {s === 4 && 'Health'}
                            </div>
                            {s < 4 && <div className="w-12 h-0.5 mx-2 bg-gray-200" />}
                        </div>
                    ))}
                </div>

                <form onSubmit={handleSubmit} className="p-8">
                    {/* Step 1: Account Info */}
                    {step === 1 && (
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="space-y-4"
                        >
                            <h2 className="text-xl font-semibold text-gray-800 mb-4">Account Information</h2>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Full Name *</label>
                                <div className="relative">
                                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                                    <input
                                        type="text"
                                        name="full_name"
                                        value={formData.full_name}
                                        onChange={handleChange}
                                        className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                        placeholder="Enter your full name"
                                        required
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Email *</label>
                                <div className="relative">
                                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                                    <input
                                        type="email"
                                        name="email"
                                        value={formData.email}
                                        onChange={handleChange}
                                        className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                        placeholder="Enter your email"
                                        required
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Username *</label>
                                <div className="relative">
                                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                                    <input
                                        type="text"
                                        name="username"
                                        value={formData.username}
                                        onChange={handleChange}
                                        className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                        placeholder="Choose a username"
                                        required
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Password *</label>
                                <div className="relative">
                                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                                    <input
                                        type="password"
                                        name="password"
                                        value={formData.password}
                                        onChange={handleChange}
                                        className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                        placeholder="Create a password"
                                        required
                                    />
                                </div>
                                <p className="text-xs text-gray-500 mt-1">Minimum 8 characters with uppercase, lowercase, number</p>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Confirm Password *</label>
                                <div className="relative">
                                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                                    <input
                                        type="password"
                                        name="confirmPassword"
                                        value={formData.confirmPassword}
                                        onChange={handleChange}
                                        className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                        placeholder="Confirm your password"
                                        required
                                    />
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {/* Step 2: Personal Info */}
                    {step === 2 && (
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="space-y-4"
                        >
                            <h2 className="text-xl font-semibold text-gray-800 mb-4">Personal Information</h2>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Age</label>
                                    <div className="relative">
                                        <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                                        <input
                                            type="number"
                                            name="age"
                                            value={formData.age}
                                            onChange={handleChange}
                                            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                            placeholder="Age"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Gender</label>
                                    <select
                                        name="gender"
                                        value={formData.gender}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                    >
                                        <option value="">Select</option>
                                        <option value="male">Male</option>
                                        <option value="female">Female</option>
                                        <option value="other">Other</option>
                                    </select>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Height (cm)</label>
                                    <div className="relative">
                                        <Ruler className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                                        <input
                                            type="number"
                                            name="height"
                                            value={formData.height}
                                            onChange={handleChange}
                                            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                            placeholder="Height in cm"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Weight (kg)</label>
                                    <div className="relative">
                                        <Weight className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                                        <input
                                            type="number"
                                            name="weight"
                                            value={formData.weight}
                                            onChange={handleChange}
                                            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                            placeholder="Weight in kg"
                                        />
                                    </div>
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
                                <div className="relative">
                                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                                    <input
                                        type="tel"
                                        name="phone"
                                        value={formData.phone}
                                        onChange={handleChange}
                                        className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                        placeholder="Phone number"
                                    />
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {/* Step 3: Fitness Goals */}
                    {step === 3 && (
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="space-y-4"
                        >
                            <h2 className="text-xl font-semibold text-gray-800 mb-4">Fitness Goals</h2>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Fitness Level</label>
                                <select
                                    name="fitness_level"
                                    value={formData.fitness_level}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="beginner">Beginner</option>
                                    <option value="intermediate">Intermediate</option>
                                    <option value="advanced">Advanced</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Primary Fitness Goal</label>
                                <select
                                    name="fitness_goal"
                                    value={formData.fitness_goal}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="weight_loss">Weight Loss</option>
                                    <option value="muscle_gain">Muscle Gain</option>
                                    <option value="maintenance">Maintenance</option>
                                    <option value="endurance">Endurance</option>
                                    <option value="flexibility">Flexibility</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Workout Preference</label>
                                <select
                                    name="workout_preference"
                                    value={formData.workout_preference}
                                    onChange={handleChange}
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
                                <label className="block text-sm font-medium text-gray-700 mb-2">Diet Preference</label>
                                <select
                                    name="diet_preference"
                                    value={formData.diet_preference}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="vegetarian">Vegetarian</option>
                                    <option value="vegan">Vegan</option>
                                    <option value="non_vegetarian">Non-Vegetarian</option>
                                    <option value="keto">Keto</option>
                                    <option value="paleo">Paleo</option>
                                </select>
                            </div>
                        </motion.div>
                    )}

                    {/* Step 4: Health Information */}
                    {step === 4 && (
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="space-y-4"
                        >
                            <h2 className="text-xl font-semibold text-gray-800 mb-4">Health Information</h2>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Medical Conditions</label>
                                <textarea
                                    name="medical_conditions"
                                    value={formData.medical_conditions}
                                    onChange={handleChange}
                                    rows="2"
                                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                    placeholder="e.g., High blood pressure, diabetes, asthma (or 'None')"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Allergies</label>
                                <textarea
                                    name="allergies"
                                    value={formData.allergies}
                                    onChange={handleChange}
                                    rows="2"
                                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                    placeholder="e.g., Peanuts, dairy, gluten (or 'None')"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Injuries</label>
                                <textarea
                                    name="injuries"
                                    value={formData.injuries}
                                    onChange={handleChange}
                                    rows="2"
                                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                    placeholder="e.g., Knee injury, back pain (or 'None')"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Medications</label>
                                <textarea
                                    name="medications"
                                    value={formData.medications}
                                    onChange={handleChange}
                                    rows="2"
                                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                    placeholder="List any medications (or 'None')"
                                />
                            </div>

                            <div className="bg-blue-50 p-4 rounded-lg mt-4">
                                <div className="flex items-start gap-3">
                                    <AlertCircle className="w-5 h-5 text-blue-500 mt-0.5" />
                                    <div>
                                        <p className="text-sm text-blue-700">
                                            This information helps us create personalized and safe workout plans for you.
                                            All data is encrypted and secure.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {/* Navigation Buttons */}
                    <div className="flex justify-between mt-8">
                        {step > 1 && (
                            <button
                                type="button"
                                onClick={handlePrev}
                                className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                            >
                                Previous
                            </button>
                        )}

                        {step < 4 ? (
                            <button
                                type="button"
                                onClick={handleNext}
                                className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors ml-auto"
                            >
                                Next
                            </button>
                        ) : (
                            <button
                                type="submit"
                                disabled={loading}
                                className="px-8 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors ml-auto disabled:opacity-50 flex items-center gap-2"
                            >
                                {loading ? 'Creating Account...' : 'Create Account'}
                                {!loading && <Heart className="w-4 h-4" />}
                            </button>
                        )}
                    </div>

                    <p className="text-center text-gray-600 mt-6">
                        Already have an account?{' '}
                        <Link to="/login" className="text-blue-500 hover:underline">
                            Sign in
                        </Link>
                    </p>
                </form>
            </motion.div>
        </div>
    )
}

export default Register