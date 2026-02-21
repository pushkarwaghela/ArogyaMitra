# backend/app/services/ai_agent.py
import asyncio
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from groq import Groq
from app.config import settings  # Changed from app.core.config to app.config
from app.models.user import User, FitnessGoal, WorkoutPreference, DietPreference
from app.models.workout import WorkoutPlan, Exercise, WeeklySchedule, ExerciseInstance, DifficultyLevel, WorkoutType
from app.models.nutrition import NutritionPlan, Meal, DailyMealPlan, DailyMealInstance, MealType, CuisineType
from app.models.progress import ProgressRecord
from app.services.youtube_service import youtube_service
from app.services.spoonacular_service import spoonacular_service


import logging

logger = logging.getLogger(__name__)

class ArogyaMitraAgent:
    """
    ArogyaMitra AI Agent - Your Personal Fitness Companion
    
    This agent orchestrates all AI-powered features:
    - Workout plan generation
    - Nutrition planning
    - Motivational coaching
    - Dynamic plan modifications
    - Progress analysis
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
    
    async def enhance_workout_with_videos(self, workout_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Add YouTube video links to each exercise in the workout plan"""

        if "weekly_schedule" not in workout_plan:
            return workout_plan

        for day in workout_plan["weekly_schedule"]:
            if "exercises" in day:
                for exercise in day["exercises"]:
                    # Get exercise name
                    if isinstance(exercise, dict):
                        exercise_name = exercise.get("name", "")
                    else:
                        exercise_name = str(exercise)
                        exercise = {"name": exercise_name}

                    # Fetch videos for this exercise
                    if exercise_name:
                        videos = await youtube_service.search_exercise_videos(
                            exercise_name=exercise_name,
                            workout_type=workout_plan.get("workout_type"),
                            difficulty=workout_plan.get("difficulty"),
                            max_results=2
                        )

                        # Add videos to exercise
                        exercise["videos"] = videos

                        # Add the first video as primary
                        if videos:
                            exercise["video_url"] = videos[0].get("embed_url")
                            exercise["video_title"] = videos[0].get("title")

        return workout_plan

    # Also update the generate_workout_plan method to include videos:

    async def generate_workout_plan(self, user: User, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a personalized workout plan using AI and enhance with YouTube videos
        """
        try:
            # Construct prompt for Groq
            prompt = self._build_workout_prompt(user, preferences)

            # Call Groq API
            if self.groq_client:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are AROMI, an expert fitness and wellness AI coach. Generate detailed, personalized workout plans based on user data."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )

                # Parse response
                plan_data = self._parse_workout_response(response.choices[0].message.content)

                # Enhance with YouTube videos
                enhanced_plan = await self.enhance_workout_with_videos(plan_data)
                return enhanced_plan
            else:
                # Fallback to template-based plan
                plan_data = self._generate_template_workout(user, preferences)
                enhanced_plan = await self.enhance_workout_with_videos(plan_data)
                return enhanced_plan

        except Exception as e:
            logger.error(f"Error generating workout plan: {e}")
            plan_data = self._generate_template_workout(user, preferences)
            enhanced_plan = await self.enhance_workout_with_videos(plan_data)
            return enhanced_plan
    
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
        - Workout Preference: {user.workout_preference.value if user.workout_preference else 'hybrid'}
        
        Additional Preferences:
        - Available Time: {preferences.get('available_time', '30-45')} minutes per session
        - Equipment Available: {preferences.get('equipment', 'minimal')}
        - Preferred Workout Type: {preferences.get('workout_type', 'mixed')}
        - Days per week: {preferences.get('days_per_week', 5)}
        
        Please provide:
        1. A 7-day workout schedule with specific exercises
        2. For each exercise include: name, sets, reps, rest time
        3. YouTube video links for each exercise (searchable terms)
        4. Warm-up and cool-down routines
        5. Daily fitness tips
        6. Expected calorie burn per session
        
        Format the response as JSON.
        """
        return prompt
    
    def _parse_workout_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into structured data"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback to structured parsing
                return self._parse_workout_text(response_text)
        except Exception as e:
            logger.error(f"Error parsing workout response: {e}")
            return {}
    
    def _parse_workout_text(self, text: str) -> Dict[str, Any]:
        """Parse non-JSON text response into structured format"""
        # Simple parsing logic - can be enhanced
        lines = text.split('\n')
        workout_data = {
            "title": "Personalized Workout Plan",
            "description": "AI-generated workout plan",
            "weekly_schedule": [],
            "tips": []
        }
        
        current_day = None
        for line in lines:
            if "Day" in line or "day" in line.lower():
                current_day = line.strip()
                workout_data["weekly_schedule"].append({"day": current_day, "exercises": []})
            elif current_day and line.strip() and not line.startswith(('Tip', 'Note')):
                if workout_data["weekly_schedule"]:
                    workout_data["weekly_schedule"][-1]["exercises"].append(line.strip())
            elif "Tip" in line or "Note" in line:
                workout_data["tips"].append(line.strip())
        
        return workout_data
    
    def _generate_template_workout(self, user: User, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a template workout plan when AI is unavailable"""
        workout_type = preferences.get('workout_type', 'mixed')
        days_per_week = preferences.get('days_per_week', 5)
        
        exercises_by_type = {
            "strength": [
                {"name": "Push-ups", "sets": 3, "reps": 10, "video": "push ups exercise"},
                {"name": "Squats", "sets": 3, "reps": 15, "video": "squats exercise"},
                {"name": "Lunges", "sets": 3, "reps": 12, "video": "lunges exercise"},
                {"name": "Plank", "sets": 3, "duration": 30, "video": "plank exercise"},
            ],
            "cardio": [
                {"name": "Jumping Jacks", "sets": 3, "duration": 30, "video": "jumping jacks"},
                {"name": "High Knees", "sets": 3, "duration": 30, "video": "high knees exercise"},
                {"name": "Burpees", "sets": 3, "reps": 10, "video": "burpees exercise"},
                {"name": "Mountain Climbers", "sets": 3, "duration": 30, "video": "mountain climbers"},
            ],
            "yoga": [
                {"name": "Downward Dog", "sets": 1, "duration": 60, "video": "downward dog yoga"},
                {"name": "Warrior Pose", "sets": 1, "duration": 60, "video": "warrior pose"},
                {"name": "Tree Pose", "sets": 1, "duration": 30, "video": "tree pose yoga"},
                {"name": "Child's Pose", "sets": 1, "duration": 60, "video": "child's pose"},
            ]
        }
        
        weekly_schedule = []
        for day in range(1, days_per_week + 1):
            day_exercises = []
            if workout_type == "mixed":
                if day % 3 == 0:
                    exercises = exercises_by_type["cardio"]
                elif day % 2 == 0:
                    exercises = exercises_by_type["strength"]
                else:
                    exercises = exercises_by_type["yoga"]
            else:
                exercises = exercises_by_type.get(workout_type, exercises_by_type["strength"])
            
            day_exercises.extend(exercises)
            
            weekly_schedule.append({
                "day": f"Day {day}",
                "exercises": day_exercises,
                "warmup": ["Arm circles", "Leg swings", "Torso twists"],
                "cooldown": ["Hamstring stretch", "Quad stretch", "Deep breathing"]
            })
        
        return {
            "title": f"{workout_type.capitalize()} Workout Plan",
            "description": f"A {days_per_week}-day {workout_type} workout plan",
            "weekly_schedule": weekly_schedule,
            "tips": [
                "Stay hydrated throughout your workout",
                "Listen to your body and rest when needed",
                "Focus on form over speed",
                "Gradually increase intensity as you get stronger"
            ]
        }
    
    async def generate_nutrition_plan(self, user: User, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a personalized nutrition plan using AI and Spoonacular
        """
        try:
            # Calculate BMR and calorie needs
            bmr = self._calculate_bmr(user)
            calorie_target = self._calculate_calorie_target(bmr, user.activity_level, user.fitness_goal)

            # Get diet preference from user
            diet = user.diet_preference.value if user.diet_preference else "vegetarian"

            # Get allergies/exclusions
            exclude = user.allergies if user.allergies else None

            # Try to get meal plan from Spoonacular first
            if spoonacular_service.api_key and spoonacular_service.api_key != "your_spoonacular_api_key_here":
                spoonacular_plan = await spoonacular_service.generate_meal_plan(
                    target_calories=calorie_target,
                    diet=diet,
                    exclude=exclude,
                    time_frame="day"  # Start with one day
                )

                if spoonacular_plan and "meals" in spoonacular_plan:
                    # Convert Spoonacular plan to our format
                    return self._convert_spoonacular_plan(spoonacular_plan, calorie_target, user)

            # Fallback to AI-generated plan
            prompt = self._build_nutrition_prompt(user, preferences, calorie_target)

            if self.groq_client:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are AROMI, an expert nutritionist AI. Create detailed, personalized meal plans based on user preferences and goals."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )

                plan_data = self._parse_nutrition_response(response.choices[0].message.content)
                plan_data["target_calories"] = calorie_target

                # Enhance with Spoonacular recipes
                enhanced_plan = await self._enhance_with_recipes(plan_data, user)
                return enhanced_plan
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

    def _convert_spoonacular_plan(self, spoonacular_plan: Dict, calorie_target: int, user: User) -> Dict[str, Any]:
        """Convert Spoonacular meal plan to our format"""
        meals = spoonacular_plan.get("meals", {})
        nutrients = spoonacular_plan.get("nutrients", {})

        daily_plans = []
        day_meals = []

        # Process each meal
        meal_types = ["breakfast", "lunch", "dinner", "snack"]
        for meal_type in meal_types:
            if meal_type in meals:
                meal = meals[meal_type]
                day_meals.append({
                    "type": meal_type,
                    "name": meal.get("title", f"{meal_type.capitalize()}"),
                    "calories": meal.get("nutrition", {}).get("nutrients", [{}])[0].get("amount", 0) if meal.get("nutrition") else 0,
                    "protein": 0,  # Would need to parse from nutrition data
                    "carbs": 0,
                    "fats": 0,
                    "recipe_id": meal.get("id"),
                    "image_url": meal.get("image")
                })

        daily_plans.append({
            "day": "Day 1",
            "meals": day_meals,
            "total_calories": calorie_target,
            "total_protein": nutrients.get("protein", 0),
            "total_carbs": nutrients.get("carbohydrates", 0),
            "total_fats": nutrients.get("fat", 0)
        })

        return {
            "title": f"{user.diet_preference.value.capitalize()} Meal Plan",
            "description": f"A {calorie_target} calorie meal plan",
            "daily_plans": daily_plans,
            "tips": [
                "Drink plenty of water throughout the day",
                "Prepare meals in advance to stay on track",
                "Include a variety of colorful vegetables"
            ]
        }

    async def _enhance_with_recipes(self, plan_data: Dict, user: User) -> Dict:
        """Enhance meal plan with real recipes from Spoonacular"""
        if "daily_plans" not in plan_data:
            return plan_data

        for day in plan_data["daily_plans"]:
            if "meals" in day:
                for meal in day["meals"]:
                    # Search for recipe based on meal name
                    recipes = await spoonacular_service.search_recipes(
                        query=meal.get("name", ""),
                        diet=user.diet_preference.value if user.diet_preference else None,
                        intolerances=user.allergies,
                        max_results=1
                    )

                    if recipes:
                        recipe = recipes[0]
                        meal["recipe_id"] = recipe.get("id")
                        meal["image_url"] = recipe.get("image")
                        meal["ready_in_minutes"] = recipe.get("readyInMinutes")
                        meal["servings"] = recipe.get("servings")

                        # Add nutrition if available
                        if "nutrition" in recipe:
                            nutrients = recipe["nutrition"].get("nutrients", [])
                            for nutrient in nutrients:
                                if nutrient["name"] == "Calories":
                                    meal["calories"] = int(nutrient["amount"] / recipe.get("servings", 1))

        return plan_data
     
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
        - Cuisine Preference: {preferences.get('cuisine', 'mixed')}
        - Meals per day: {preferences.get('meals_per_day', 3)} plus snacks
        
        Please provide:
        1. A 7-day meal plan with breakfast, lunch, dinner, and snacks
        2. For each meal include: name, ingredients, calories, protein, carbs, fats
        3. Simple recipes or preparation steps
        4. Macro-nutrient breakdown for each day
        
        Format the response as JSON.
        """
        return prompt
    
# In backend/app/services/ai_agent.py, update the _parse_nutrition_response method:

    def _parse_nutrition_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI nutrition response with better error handling"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError as je:
                    logger.error(f"JSON decode error: {je}")
                    # If JSON parsing fails, try to clean the response
                    cleaned_text = self._clean_json_response(json_match.group())
                    return json.loads(cleaned_text)
            else:
                return self._parse_nutrition_text(response_text)
        except Exception as e:
            logger.error(f"Error parsing nutrition response: {e}")
            return self._parse_nutrition_text(response_text)

    def _clean_json_response(self, text: str) -> str:
        """Clean common JSON formatting issues"""
        # Remove trailing commas
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*\]', ']', text)

        # Ensure property names are in quotes
        text = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', text)

        return text
    
    def _parse_nutrition_text(self, text: str) -> Dict[str, Any]:
        """Parse non-JSON nutrition text"""
        return {
            "title": "Personalized Nutrition Plan",
            "description": "AI-generated meal plan",
            "daily_plans": [],
            "tips": ["Stay hydrated", "Eat mindfully", "Plan your meals ahead"]
        }
    
    def _generate_template_nutrition(self, user: User, preferences: Dict[str, Any], calorie_target: int) -> Dict[str, Any]:
        """Generate a template nutrition plan"""
        diet_type = user.diet_preference.value if user.diet_preference else "vegetarian"
        cuisine = preferences.get('cuisine', 'mixed')
        meals_per_day = preferences.get('meals_per_day', 3)
        
        # Sample meals by diet type
        meals_by_diet = {
            "vegetarian": {
                "breakfast": ["Oatmeal with fruits", "Greek yogurt with berries", "Smoothie bowl"],
                "lunch": ["Quinoa salad", "Lentil soup with bread", "Vegetable stir-fry with tofu"],
                "dinner": ["Chickpea curry with rice", "Vegetable pasta", "Mushroom risotto"],
                "snack": ["Apple with peanut butter", "Mixed nuts", "Fruit smoothie"]
            },
            "non_vegetarian": {
                "breakfast": ["Eggs with toast", "Protein smoothie", "Oatmeal with protein powder"],
                "lunch": ["Grilled chicken salad", "Tuna sandwich", "Turkey wrap"],
                "dinner": ["Salmon with vegetables", "Chicken stir-fry", "Lean beef with sweet potato"],
                "snack": ["Greek yogurt", "Protein bar", "Hard-boiled eggs"]
            },
            "vegan": {
                "breakfast": ["Oatmeal with plant milk", "Tofu scramble", "Smoothie bowl"],
                "lunch": ["Quinoa bowl with veggies", "Lentil soup", "Hummus wrap"],
                "dinner": ["Tofu curry", "Bean chili", "Vegan pasta"],
                "snack": ["Fruit", "Nuts", "Vegan protein shake"]
            }
        }
        
        # Get meals for diet type (default to vegetarian)
        meals = meals_by_diet.get(diet_type, meals_by_diet["vegetarian"])
        
        daily_plans = []
        for day in range(1, 8):
            day_meals = []
            
            # Add breakfast
            day_meals.append({
                "type": "breakfast",
                "name": meals["breakfast"][day % len(meals["breakfast"])],
                "calories": int(calorie_target * 0.25),
                "protein": 15,
                "carbs": 40,
                "fats": 10
            })
            
            # Add lunch
            day_meals.append({
                "type": "lunch",
                "name": meals["lunch"][day % len(meals["lunch"])],
                "calories": int(calorie_target * 0.35),
                "protein": 25,
                "carbs": 50,
                "fats": 15
            })
            
            # Add dinner
            day_meals.append({
                "type": "dinner",
                "name": meals["dinner"][day % len(meals["dinner"])],
                "calories": int(calorie_target * 0.3),
                "protein": 30,
                "carbs": 40,
                "fats": 20
            })
            
            # Add snack if meals_per_day > 3
            if meals_per_day > 3:
                day_meals.append({
                    "type": "snack",
                    "name": meals["snack"][day % len(meals["snack"])],
                    "calories": int(calorie_target * 0.1),
                    "protein": 10,
                    "carbs": 15,
                    "fats": 5
                })
            
            daily_plans.append({
                "day": f"Day {day}",
                "meals": day_meals,
                "total_calories": sum(meal["calories"] for meal in day_meals),
                "total_protein": sum(meal["protein"] for meal in day_meals),
                "total_carbs": sum(meal["carbs"] for meal in day_meals),
                "total_fats": sum(meal["fats"] for meal in day_meals)
            })
        
        return {
            "title": f"{diet_type.capitalize()} Meal Plan",
            "description": f"A 7-day {calorie_target} calorie meal plan",
            "daily_plans": daily_plans,
            "tips": [
                "Drink plenty of water throughout the day",
                "Prepare meals in advance to stay on track",
                "Listen to your hunger and fullness cues",
                "Include a variety of colorful vegetables"
            ]
        }
    
    async def get_motivational_message(self, user: User, context: Dict[str, Any]) -> str:
        """Get personalized motivational message from AI"""
        try:
            if self.groq_client:
                prompt = f"""
                Generate a short, encouraging motivational message for a fitness user.
                
                User Context:
                - Name: {user.full_name or user.username}
                - Goal: {user.fitness_goal.value if user.fitness_goal else 'fitness'}
                - Recent progress: {context.get('progress', 'making progress')}
                - Current challenge: {context.get('challenge', 'staying consistent')}
                
                Make it personal, inspiring, and action-oriented. Keep it under 100 words.
                """
                
                response = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are AROMI, a motivational fitness coach. Generate encouraging messages that inspire action and consistency."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=150
                )
                
                return response.choices[0].message.content
            else:
                return self._get_template_motivation(user, context)
                
        except Exception as e:
            logger.error(f"Error getting motivational message: {e}")
            return self._get_template_motivation(user, context)
    
    def _get_template_motivation(self, user: User, context: Dict[str, Any]) -> str:
        """Get template motivational message"""
        messages = [
            f"Keep going, {user.username}! Every workout brings you closer to your goals.",
            f"Remember why you started, {user.username}. Consistency is key!",
            f"You're doing great, {user.username}! Small steps every day lead to big results.",
            f"Stay strong, {user.username}! Your future self will thank you.",
            f"Believe in yourself, {user.username}! You have the power to achieve your fitness goals."
        ]
        import random
        return random.choice(messages)
    
    async def adjust_plan_dynamically(self, user: User, current_plan: Dict, adjustment_type: str, details: Dict) -> Dict:
        """Dynamically adjust workout/nutrition plan based on real-time factors"""
        
        if adjustment_type == "travel":
            return self._adjust_for_travel(current_plan, details)
        elif adjustment_type == "injury":
            return self._adjust_for_injury(current_plan, details)
        elif adjustment_type == "time_constraint":
            return self._adjust_for_time(current_plan, details)
        elif adjustment_type == "mood":
            return self._adjust_for_mood(current_plan, details)
        else:
            return current_plan
    
    def _adjust_for_travel(self, plan: Dict, details: Dict) -> Dict:
        """Adjust workout plan for travel"""
        adjusted_plan = plan.copy()
        adjusted_plan["title"] = f"Travel-Friendly {plan.get('title', 'Workout')}"
        adjusted_plan["description"] = "Modified for travel - no equipment needed"
        
        # Replace exercises with bodyweight alternatives
        for day in adjusted_plan.get("weekly_schedule", []):
            for exercise in day.get("exercises", []):
                if isinstance(exercise, dict):
                    exercise["equipment"] = "none"
                    exercise["notes"] = "Perfect for hotel room"
        
        adjusted_plan["tips"] = [
            "Stay hydrated during travel",
            "Pack workout clothes in your carry-on",
            "Use hotel stairs for cardio",
            "Try to maintain your sleep schedule"
        ] + plan.get("tips", [])
        
        return adjusted_plan
    
    def _adjust_for_injury(self, plan: Dict, details: Dict) -> Dict:
        """Adjust workout plan for injury"""
        injury_area = details.get("area", "unknown")
        
        adjusted_plan = plan.copy()
        adjusted_plan["title"] = f"Injury-Modified {plan.get('title', 'Workout')}"
        adjusted_plan["description"] = f"Modified to accommodate {injury_area} injury"
        
        # Add injury-specific modifications
        adjusted_plan["warnings"] = [f"⚠️ Avoid exercises that strain your {injury_area}"]
        adjusted_plan["alternatives"] = ["Consult with a physical therapist", "Focus on other muscle groups"]
        
        return adjusted_plan
    
    def _adjust_for_time(self, plan: Dict, details: Dict) -> Dict:
        """Adjust workout plan for time constraints"""
        available_time = details.get("available_minutes", 20)
        
        adjusted_plan = plan.copy()
        adjusted_plan["title"] = f"Quick {available_time}-Minute Workout"
        
        # Simplify exercises to fit time constraint
        for day in adjusted_plan.get("weekly_schedule", []):
            # Reduce number of exercises or sets
            if len(day.get("exercises", [])) > 4:
                day["exercises"] = day["exercises"][:4]
            
            # Add efficiency tips
            day["tips"] = ["Superset exercises to save time", "Minimize rest between sets"]
        
        return adjusted_plan
    
    def _adjust_for_mood(self, plan: Dict, details: Dict) -> Dict:
        """Adjust workout based on mood"""
        mood = details.get("mood", "neutral")
        
        adjusted_plan = plan.copy()
        
        if mood in ["tired", "low_energy"]:
            adjusted_plan["title"] = "Gentle Recovery Workout"
            adjusted_plan["intensity"] = "low"
            adjusted_plan["focus"] = "mobility and stretching"
        elif mood in ["stressed", "anxious"]:
            adjusted_plan["title"] = "Stress-Relief Workout"
            adjusted_plan["focus"] = "yoga and breathing exercises"
        elif mood in ["energetic", "motivated"]:
            adjusted_plan["title"] = "High-Energy Workout"
            adjusted_plan["intensity"] = "high"
        
        return adjusted_plan
    
    async def analyze_progress(self, user: User, progress_records: List[ProgressRecord]) -> Dict[str, Any]:
        """Analyze user progress and provide insights"""
        
        if not progress_records:
            return {
                "message": "Start tracking your progress to see insights!",
                "suggestions": ["Log your first workout", "Record your weight", "Track your meals"]
            }
        
        # Calculate trends
        weights = [r.weight for r in progress_records if r.weight]
        weight_trend = "stable"
        if len(weights) >= 2:
            if weights[-1] < weights[0]:
                weight_trend = "decreasing"
            elif weights[-1] > weights[0]:
                weight_trend = "increasing"
        
        workouts_completed = sum(1 for r in progress_records if r.workout_completed)
        completion_rate = (workouts_completed / len(progress_records)) * 100 if progress_records else 0
        
        # Generate insights
        insights = {
            "summary": f"You've completed {workouts_completed} workouts in this period.",
            "weight_trend": weight_trend,
            "completion_rate": f"{completion_rate:.1f}%",
            "streak": self._calculate_streak(progress_records),
            "recommendations": []
        }
        
        if completion_rate < 50:
            insights["recommendations"].append("Try shorter workouts to build consistency")
        elif completion_rate > 80:
            insights["recommendations"].append("Great consistency! Consider increasing intensity")
        
        if weight_trend == "decreasing" and user.fitness_goal == FitnessGoal.WEIGHT_LOSS:
            insights["recommendations"].append("You're on track with your weight loss goal!")
        elif weight_trend == "increasing" and user.fitness_goal == FitnessGoal.WEIGHT_GAIN:
            insights["recommendations"].append("Great progress on your weight gain journey!")
        
        return insights
    
    def _calculate_streak(self, records: List[ProgressRecord]) -> int:
        """Calculate current workout streak"""
        if not records:
            return 0
        
        # Sort by date
        sorted_records = sorted(records, key=lambda r: r.record_date, reverse=True)
        
        streak = 0
        for record in sorted_records:
            if record.workout_completed:
                streak += 1
            else:
                break
        
        return streak


# Singleton instance
arogya_mitra_agent = ArogyaMitraAgent()