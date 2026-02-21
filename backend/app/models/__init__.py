# backend/app/models/__init__.py
from .user import User, UserRole, FitnessGoal, WorkoutPreference, DietPreference, ActivityLevel
from .health import HealthAssessment
from .workout import WorkoutPlan, Exercise, WeeklySchedule, ExerciseInstance, DifficultyLevel, WorkoutType
from .nutrition import NutritionPlan, Meal, DailyMealPlan, DailyMealInstance, MealType, CuisineType
from .progress import ProgressRecord, Achievement
from .chat import ChatSession, ChatMessage, MessageType

__all__ = [
    # User models
    "User", "UserRole", "FitnessGoal", "WorkoutPreference", "DietPreference", "ActivityLevel",
    
    # Health models
    "HealthAssessment",
    
    # Workout models
    "WorkoutPlan", "Exercise", "WeeklySchedule", "ExerciseInstance", "DifficultyLevel", "WorkoutType",
    
    # Nutrition models
    "NutritionPlan", "Meal", "DailyMealPlan", "DailyMealInstance", "MealType", "CuisineType",
    
    # Progress models
    "ProgressRecord", "Achievement",
    
    # Chat models
    "ChatSession", "ChatMessage", "MessageType"
]