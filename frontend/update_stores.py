#!/usr/bin/env python3
import os
import re
import shutil
from pathlib import Path

print("🚀 Updating TypeScript components to use Zustand stores...")

# Function to backup file
def backup_file(file_path):
    backup_path = str(file_path) + ".backup"
    shutil.copy2(str(file_path), backup_path)
    print(f"  ✅ Backup created: {backup_path}")

# Update Dashboard.tsx
dashboard_path = Path("src/pages/dashboard/Dashboard.jsx")
if dashboard_path.exists():
    print("  📝 Updating Dashboard.jsx...")
    backup_file(dashboard_path)
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add new imports
    new_imports = "import { useAuthStore, useWorkoutStore, useProgressStore } from '../stores'\n"
    
    # Remove old imports and add new ones
    content = re.sub(r'import { useAuthStore } from [\'"][^\'"]+[\'"]', new_imports, content)
    content = re.sub(r'import { userApi } from [\'"][^\'"]+[\'"]', '', content)
    
    # Replace the component
    new_component = '''const Dashboard = () => {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { currentPlan, fetchPlans, isLoading: workoutLoading } = useWorkoutStore()
  const { stats, fetchStats, isLoading: progressLoading } = useProgressStore()
  const [greeting, setGreeting] = useState('')

  useEffect(() => {
    const hour = new Date().getHours()
    if (hour < 12) setGreeting('Good morning')
    else if (hour < 18) setGreeting('Good afternoon')
    else setGreeting('Good evening')
    
    // Fetch data from stores
    fetchPlans()
    fetchStats()
  }, [])

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: 'spring',
        stiffness: 100
      }
    }
  }

  if (workoutLoading || progressLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return ('''
    
    # Replace the component definition
    pattern = r'const Dashboard = \(\) => \{(.*?)(?=return \()'
    content = re.sub(pattern, new_component, content, flags=re.DOTALL)
    
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  ✅ Dashboard.jsx updated successfully")
else:
    print("  ⚠️ Dashboard.jsx not found")

# Update WorkoutPlans.tsx
workout_path = Path("src/pages/workouts/WorkoutPlans.tsx")
if workout_path.exists():
    print("  📝 Updating WorkoutPlans.tsx...")
    backup_file(workout_path)
    
    with open(workout_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add new imports
    new_imports = "import { useAuthStore, useWorkoutStore } from '../stores'\n"
    content = re.sub(r'import { useAuthStore } from [\'"][^\'"]+[\'"]', new_imports, content)
    content = re.sub(r'import { workoutApi } from [\'"][^\'"]+[\'"]', '', content)
    
    # Replace the component
    new_component = '''const WorkoutPlans: React.FC = () => {
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
    isLoading 
  } = useWorkoutStore()
  
  const [selectedDay, setSelectedDay] = useState<any>(null)
  const [selectedExercise, setSelectedExercise] = useState<any>(null)
  const [activeTab, setActiveTab] = useState<'overview' | 'week' | 'history'>('overview')
  const [showPlayer, setShowPlayer] = useState(false)

  useEffect(() => {
    fetchPlans()
  }, [])

  const handleGeneratePlan = () => {
    generatePlan({
      fitnessLevel: user?.fitness_level || 'beginner',
      goal: user?.fitness_goal || 'weight_loss',
      preference: user?.workout_preference || 'moderate',
      daysPerWeek: 5,
      duration: 45
    })
  }

  const handleStartExercise = (exercise: any, day: any) => {
    setCurrentExercise(exercise)
    setActiveWorkout(day)
    setSelectedExercise(exercise)
    setSelectedDay(day)
    setShowPlayer(true)
  }

  const handleExerciseComplete = (exerciseId: string) => {
    completeExercise(exerciseId)
  }

  const handleDayComplete = (day: any) => {
    completeWorkout(day.dayNumber)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return ('''
    
    pattern = r'const WorkoutPlans: React\.FC = \(\) => \{(.*?)(?=return \()'
    content = re.sub(pattern, new_component, content, flags=re.DOTALL)
    
    with open(workout_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  ✅ WorkoutPlans.tsx updated successfully")
else:
    print("  ⚠️ WorkoutPlans.tsx not found")

# Update NutritionPlans.tsx
nutrition_path = Path("src/pages/nutrition/NutritionPlans.tsx")
if nutrition_path.exists():
    print("  📝 Updating NutritionPlans.tsx...")
    backup_file(nutrition_path)
    
    with open(nutrition_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add new imports
    new_imports = "import { useAuthStore, useNutritionStore } from '../stores'\n"
    content = re.sub(r'import { useAuthStore } from [\'"][^\'"]+[\'"]', new_imports, content)
    content = re.sub(r'import { nutritionApi } from [\'"][^\'"]+[\'"]', '', content)
    
    # Replace the component
    new_component = '''const NutritionPlans: React.FC = () => {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { 
    plans, 
    currentPlan, 
    fetchPlans, 
    generatePlan,
    setCurrentDay,
    completeMeal,
    addToGroceryList,
    isLoading 
  } = useNutritionStore()
  
  const [activeTab, setActiveTab] = useState<'today' | 'week' | 'grocery'>('today')
  const [selectedMeal, setSelectedMeal] = useState<any>(null)
  const [showRecipe, setShowRecipe] = useState(false)

  useEffect(() => {
    fetchPlans()
  }, [])

  const handleGeneratePlan = () => {
    generatePlan({
      calorieTarget: 2000,
      dietType: user?.diet_preference || 'vegetarian',
      allergies: user?.allergies?.split(',') || [],
      duration: 7
    })
  }

  const handleMealComplete = (mealId: string) => {
    completeMeal(mealId)
  }

  const handleAddToGrocery = (meal: any) => {
    addToGroceryList(meal.ingredients)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return ('''
    
    pattern = r'const NutritionPlans: React\.FC = \(\) => \{(.*?)(?=return \()'
    content = re.sub(pattern, new_component, content, flags=re.DOTALL)
    
    with open(nutrition_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  ✅ NutritionPlans.tsx updated successfully")
else:
    print("  ⚠️ NutritionPlans.tsx not found")

# Update HealthAssessment.tsx
health_path = Path("src/pages/health-assessment/HealthAssessment.tsx")
if health_path.exists():
    print("  📝 Updating HealthAssessment.tsx...")
    backup_file(health_path)
    
    with open(health_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add new imports
    new_imports = "import { useAuthStore, useProgressStore } from '../stores'\n"
    content = re.sub(r'import { useAuthStore } from [\'"][^\'"]+[\'"]', new_imports, content)
    content = re.sub(r'import { healthApi } from [\'"][^\'"]+[\'"]', '', content)
    
    # Replace the component
    new_component = '''const HealthAssessment: React.FC = () => {
  const navigate = useNavigate()
  const { user, updateUser } = useAuthStore()
  const { updateBodyMetrics } = useProgressStore()
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

  const handleSubmit = () => {
    // Update user data in auth store
    updateUser({
      age: bodyMetrics.age,
      gender: bodyMetrics.gender,
      height: bodyMetrics.height,
      weight: bodyMetrics.weight,
      fitness_level: answers.fitness_level?.toLowerCase() || 'beginner',
      fitness_goal: answers.fitness_goal || 'weight_loss',
      workout_preference: answers.workout_preference || 'moderate',
      diet_preference: answers.diet_type || 'vegetarian'
    })
    
    // Update body metrics in progress store
    updateBodyMetrics({
      age: bodyMetrics.age,
      gender: bodyMetrics.gender,
      height: bodyMetrics.height,
      weight: bodyMetrics.weight,
      bmi: bodyMetrics.bmi
    })
    
    toast.success('Health assessment completed!')
    navigate('/dashboard')
  }

  return ('''
    
    pattern = r'const HealthAssessment: React\.FC = \(\) => \{(.*?)(?=return \()'
    content = re.sub(pattern, new_component, content, flags=re.DOTALL)
    
    with open(health_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  ✅ HealthAssessment.tsx updated successfully")
else:
    print("  ⚠️ HealthAssessment.tsx not found")

# Update ProgressTracking.tsx
progress_path = Path("src/pages/progress/ProgressTracking.tsx")
if progress_path.exists():
    print("  📝 Updating ProgressTracking.tsx...")
    backup_file(progress_path)
    
    with open(progress_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add new imports
    new_imports = "import { useAuthStore, useProgressStore } from '../stores'\n"
    content = re.sub(r'import { useAuthStore } from [\'"][^\'"]+[\'"]', new_imports, content)
    content = re.sub(r'import { progressApi } from [\'"][^\'"]+[\'"]', '', content)
    
    # Replace the component
    new_component = '''const ProgressTracking: React.FC = () => {
  const { user } = useAuthStore()
  const { 
    stats, 
    history, 
    achievements, 
    bodyMetrics,
    fetchStats, 
    fetchHistory, 
    fetchAchievements,
    isLoading 
  } = useProgressStore()
  
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | '3months' | 'year'>('month')
  const [activeTab, setActiveTab] = useState<'overview' | 'workouts' | 'nutrition' | 'body' | 'achievements'>('overview')

  useEffect(() => {
    fetchStats()
    fetchHistory(selectedPeriod)
    fetchAchievements()
  }, [selectedPeriod])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return ('''
    
    pattern = r'const ProgressTracking: React\.FC = \(\) => \{(.*?)(?=return \()'
    content = re.sub(pattern, new_component, content, flags=re.DOTALL)
    
    with open(progress_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  ✅ ProgressTracking.tsx updated successfully")
else:
    print("  ⚠️ ProgressTracking.tsx not found")

# Update AromiCoach.jsx
aromi_path = Path("src/pages/aromi/AromiCoach.jsx")
if aromi_path.exists():
    print("  📝 Updating AromiCoach.jsx...")
    backup_file(aromi_path)
    
    with open(aromi_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add new imports
    new_imports = "import { useAuthStore, useChatStore } from '../stores'\n"
    content = re.sub(r'import { useAuthStore } from [\'"][^\'"]+[\'"]', new_imports, content)
    content = re.sub(r'import { aromiApi } from [\'"][^\'"]+[\'"]', '', content)
    
    # Replace the component
    new_component = '''const AromiCoach = () => {
  const { user } = useAuthStore()
  const { 
    messages, 
    currentSessionId,
    sendMessage, 
    createSession,
    loadMessages,
    isLoading 
  } = useChatStore()
  
  const [input, setInput] = useState('')
  const [isListening, setIsListening] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!currentSessionId) {
      createSession()
    }
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return
    await sendMessage(currentSessionId, input)
    setInput('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const toggleListening = () => {
    setIsListening(!isListening)
  }

  return ('''
    
    pattern = r'const AromiCoach = \(\) => \{(.*?)(?=return \()'
    content = re.sub(pattern, new_component, content, flags=re.DOTALL)
    
    with open(aromi_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  ✅ AromiCoach.jsx updated successfully")
else:
    print("  ⚠️ AromiCoach.jsx not found")

print("\n🎉 All TypeScript components updated successfully!")
print("Backup files created with .backup extension")
print("To restore any file, rename the .backup file to .tsx or .jsx")