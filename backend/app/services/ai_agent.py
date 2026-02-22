import asyncio
import json
import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from groq import Groq

# Add these missing imports
from app.config import settings
from app.models.user import User, FitnessGoal, WorkoutPreference, DietPreference
from app.models.workout import WorkoutPlan, Exercise, WeeklySchedule, ExerciseInstance, DifficultyLevel, WorkoutType
from app.models.nutrition import NutritionPlan, Meal, DailyMealPlan, DailyMealInstance, MealType, CuisineType
from app.models.progress import ProgressRecord

logger = logging.getLogger(__name__)

class ArogyaMitraAgent:
    """
    ArogyaMitra AI Agent - Your Personal Fitness Companion
    """
    
    def __init__(self):
        self.groq_client = None
        self.initialize_ai_clients()
    
    def initialize_ai_clients(self):
        """Initialize AI service clients"""
        try:
            if settings.GROQ_API_KEY:
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
                logger.info("✅ Groq AI client initialized")
            else:
                logger.warning("⚠️ No Groq API key found")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Groq client: {e}")
    
    async def generate_workout_plan(self, user: User, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a personalized workout plan using Groq AI
        """
        try:
            # Construct prompt for Groq
            prompt = self._build_workout_prompt(user, preferences)
            
            # Call Groq API with real key
            if self.groq_client and settings.GROQ_API_KEY:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are AROMI, an expert fitness and wellness AI coach. Generate detailed, personalized workout plans based on user data. Return ONLY valid JSON without any additional text, markdown, or explanation."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000,
                )
                
                # Get the response content
                content = response.choices[0].message.content
                
                # Clean the response - remove markdown code blocks if present
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.startswith('```'):
                    content = content[3:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()
                
                # Parse JSON response
                try:
                    plan_data = json.loads(content)
                    logger.info(f"AI generated workout plan for user {user.id}")
                    return plan_data
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}. Content: {content[:200]}")
                    # Try to extract JSON from text
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                    else:
                        # Return a structured default plan
                        return self._generate_template_workout(user, preferences)
            else:
                logger.error("Groq client not initialized or API key missing")
                return self._generate_template_workout(user, preferences)
                
        except Exception as e:
            logger.error(f"Error generating workout plan: {e}")
            return self._generate_template_workout(user, preferences)
    
    async def generate_nutrition_plan(self, user: User, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a personalized nutrition plan using Groq AI
        """
        try:
            # Calculate BMR and calorie needs
            bmr = self._calculate_bmr(user)
            calorie_target = self._calculate_calorie_target(bmr, user.activity_level, user.fitness_goal)
            
            # Construct prompt for Groq
            prompt = self._build_nutrition_prompt(user, preferences, calorie_target)
            
            if self.groq_client and settings.GROQ_API_KEY:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are AROMI, an expert nutritionist AI. Create detailed, personalized meal plans based on user preferences and goals. Return in JSON format."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                try:
                    plan_data = json.loads(response.choices[0].message.content)
                    plan_data["target_calories"] = calorie_target
                    return plan_data
                except:
                    return self._generate_template_nutrition(user, preferences, calorie_target)
            else:
                return self._generate_template_nutrition(user, preferences, calorie_target)
                
        except Exception as e:
            logger.error(f"Error generating nutrition plan: {e}")
            calorie_target = self._calculate_calorie_target(
                self._calculate_bmr(user), 
                user.activity_level, 
                user.fitness_goal
            )
            return self._generate_template_nutrition(user, preferences, calorie_target)
    
    def _calculate_bmr(self, user: User) -> float:
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor equation"""
        if not user.age or not user.weight or not user.height:
            return 1800  # Default
        
        if user.gender and user.gender.lower() == "female":
            # For women
            bmr = (10 * user.weight) + (6.25 * user.height) - (5 * user.age) - 161
        else:
            # For men (default)
            bmr = (10 * user.weight) + (6.25 * user.height) - (5 * user.age) + 5
        
        return bmr
    
    def _calculate_calorie_target(self, bmr: float, activity_level: str, fitness_goal: FitnessGoal) -> int:
        """Calculate daily calorie target based on activity and goals"""
        # Activity multipliers
        activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }
        
        multiplier = activity_multipliers.get(activity_level, 1.55)
        tdee = bmr * multiplier
        
        # Adjust based on goal
        if fitness_goal == FitnessGoal.WEIGHT_LOSS:
            return int(tdee - 500)  # Calorie deficit
        elif fitness_goal == FitnessGoal.WEIGHT_GAIN or fitness_goal == FitnessGoal.MUSCLE_GAIN:
            return int(tdee + 300)  # Calorie surplus
        else:
            return int(tdee)  # Maintenance
    
    def _build_workout_prompt(self, user: User, preferences: Dict[str, Any]) -> str:
        """Build prompt for workout generation"""
        prompt = f"""
        Create a personalized 7-day workout plan for a user with the following profile:
        
        User Profile:
        - Age: {user.age or 'Not specified'}
        - Gender: {user.gender or 'Not specified'}
        - Height: {user.height or 'Not specified'} cm
        - Weight: {user.weight or 'Not specified'} kg
        - Fitness Level: {user.fitness_level or 'beginner'}
        - Fitness Goal: {user.fitness_goal.value if user.fitness_goal else 'maintenance'}
        - Workout Preference: {user.workout_preference.value if user.workout_preference else 'moderate'}
        
        Additional Preferences:
        - Available Time: {preferences.get('available_time', '45')} minutes per session
        - Equipment Available: {preferences.get('equipment', 'minimal')}
        - Days per week: {preferences.get('days_per_week', 5)}
        
        Please provide a JSON response with:
        1. A 7-day workout schedule with specific exercises
        2. For each exercise include: name, sets, reps, rest time
        3. Warm-up and cool-down routines
        4. Daily fitness tips
        5. Expected calorie burn per session
        
        Format as JSON with structure:
        {{
            "title": "Plan title",
            "description": "Plan description",
            "weekly_schedule": [
                {{
                    "day": "Day 1",
                    "focus": "Full Body",
                    "exercises": [
                        {{
                            "name": "Push-ups",
                            "sets": 3,
                            "reps": 10,
                            "rest_time": 60,
                            "calories_burn": 50
                        }}
                    ]
                }}
            ],
            "tips": ["tip1", "tip2"]
        }}
        """
        return prompt
    
    def _build_nutrition_prompt(self, user: User, preferences: Dict[str, Any], calorie_target: int) -> str:
        """Build prompt for nutrition plan generation"""
        prompt = f"""
        Create a 7-day meal plan for a user with the following profile:
        
        User Profile:
        - Age: {user.age or 'Not specified'}
        - Gender: {user.gender or 'Not specified'}
        - Height: {user.height or 'Not specified'} cm
        - Weight: {user.weight or 'Not specified'} kg
        - Activity Level: {user.activity_level or 'moderate'}
        - Fitness Goal: {user.fitness_goal.value if user.fitness_goal else 'maintenance'}
        - Diet Preference: {user.diet_preference.value if user.diet_preference else 'vegetarian'}
        
        Dietary Restrictions:
        - Allergies: {user.allergies or 'None'}
        - Medical Conditions: {user.medical_conditions or 'None'}
        
        Plan Requirements:
        - Daily Calorie Target: {calorie_target} calories
        - Meals per day: {preferences.get('meals_per_day', 3)} plus snacks
        
        Please provide a JSON response with:
        1. A 7-day meal plan with breakfast, lunch, dinner, and snacks
        2. For each meal include: name, ingredients, calories, protein, carbs, fats
        3. Simple recipes or preparation steps
        4. Macro-nutrient breakdown for each day
        
        Format as JSON.
        """
        return prompt
    
    def _generate_template_workout(self, user: User, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a template workout plan as fallback"""
        return {
            "title": "Personalized Workout Plan",
            "description": f"AI-generated plan for {user.full_name or user.username}",
            "weekly_schedule": [
                {
                    "day": "Day 1",
                    "focus": "Full Body",
                    "exercises": [
                        {"name": "Push-ups", "sets": 3, "reps": 10, "rest_time": 60, "calories_burn": 50},
                        {"name": "Squats", "sets": 3, "reps": 15, "rest_time": 60, "calories_burn": 70},
                        {"name": "Plank", "sets": 3, "duration": 30, "rest_time": 30, "calories_burn": 40}
                    ]
                }
            ],
            "tips": ["Stay hydrated", "Focus on form", "Rest when needed"]
        }
    
    def _generate_template_nutrition(self, user: User, preferences: Dict[str, Any], calorie_target: int) -> Dict[str, Any]:
        """Generate a template nutrition plan as fallback"""
        return {
            "title": "Personalized Meal Plan",
            "description": f"AI-generated meal plan for {user.full_name or user.username}",
            "target_calories": calorie_target,
            "daily_plans": [
                {
                    "day": 1,
                    "meals": [
                        {"type": "breakfast", "name": "Oatmeal with Fruits", "calories": 350},
                        {"type": "lunch", "name": "Quinoa Salad", "calories": 450},
                        {"type": "dinner", "name": "Grilled Vegetables", "calories": 500},
                        {"type": "snack", "name": "Greek Yogurt", "calories": 200}
                    ]
                }
            ],
            "tips": ["Drink plenty of water", "Eat mindfully", "Plan your meals ahead"]
        }

# ⚠️ IMPORTANT: Add this singleton instance at the END of the file
arogya_mitra_agent = ArogyaMitraAgent()