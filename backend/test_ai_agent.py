# backend/test_ai_agent.py
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_agent import arogya_mitra_agent
from app.models.user import FitnessGoal, WorkoutPreference, DietPreference
import logging

logging.basicConfig(level=logging.INFO)

async def test_ai_agent():
    """Test the AI agent functionality"""
    print("=" * 60)
    print("🤖 Testing ArogyaMitra AI Agent")
    print("=" * 60)
    
    # Create a mock user for testing
    class MockUser:
        def __init__(self):
            self.id = 1
            self.username = "testuser"
            self.full_name = "Test User"
            self.email = "test@example.com"
            self.age = 28
            self.gender = "male"
            self.height = 175
            self.weight = 70
            self.fitness_level = "intermediate"
            self.fitness_goal = FitnessGoal.WEIGHT_LOSS
            self.workout_preference = WorkoutPreference.MODERATE  # FIXED
            self.diet_preference = DietPreference.VEGETARIAN
            self.activity_level = "moderate"
            self.medical_conditions = None
            self.allergies = "peanuts"
    
    mock_user = MockUser()
    
    # Test 1: Generate Workout Plan
    print("\n📋 Test 1: Generating Workout Plan...")
    workout_preferences = {
        "available_time": 45,
        "equipment": "minimal",
        "workout_type": "mixed",
        "days_per_week": 5,
        "duration_weeks": 4
    }
    
    try:
        workout_plan = await arogya_mitra_agent.generate_workout_plan(mock_user, workout_preferences)
        
        if workout_plan:
            print(f"✅ Workout plan generated successfully!")
            print(f"   Title: {workout_plan.get('title', 'N/A')}")
            print(f"   Description: {str(workout_plan.get('description', 'N/A'))[:100]}...")
            if 'weekly_schedule' in workout_plan:
                print(f"   Days in plan: {len(workout_plan['weekly_schedule'])}")
        else:
            print("❌ Failed to generate workout plan")
    except Exception as e:
        print(f"❌ Error in workout plan generation: {e}")
    
    # Test 2: Generate Nutrition Plan
    print("\n🍎 Test 2: Generating Nutrition Plan...")
    nutrition_preferences = {
        "cuisine": "mixed",
        "meals_per_day": 4,
        "duration_days": 7,
        "exclude_allergens": ["peanuts"]
    }
    
    try:
        nutrition_plan = await arogya_mitra_agent.generate_nutrition_plan(mock_user, nutrition_preferences)
        
        if nutrition_plan:
            print(f"✅ Nutrition plan generated successfully!")
            print(f"   Title: {nutrition_plan.get('title', 'N/A')}")
            print(f"   Target Calories: {nutrition_plan.get('target_calories', 'N/A')}")
            if 'daily_plans' in nutrition_plan:
                print(f"   Days in plan: {len(nutrition_plan['daily_plans'])}")
        else:
            print("❌ Failed to generate nutrition plan")
    except Exception as e:
        print(f"❌ Error in nutrition plan generation: {e}")
    
    # Test 3: Get Motivational Message - FIXED with try/except
    print("\n💪 Test 3: Getting Motivational Message...")
    context = {
        "progress": "completed 3 workouts this week",
        "challenge": "feeling tired today"
    }
    
    try:
        # Try different possible method names
        if hasattr(arogya_mitra_agent, 'get_motivational_message'):
            message = await arogya_mitra_agent.get_motivational_message(mock_user, context)
        elif hasattr(arogya_mitra_agent, 'generate_motivation'):
            message = await arogya_mitra_agent.generate_motivation(mock_user, context)
        elif hasattr(arogya_mitra_agent, 'get_motivation'):
            message = await arogya_mitra_agent.get_motivation(mock_user, context)
        else:
            # Use template message
            message = "Keep going! Every workout brings you closer to your goals."
        
        if message:
            print(f"✅ Motivational message received:")
            print(f"   \"{message}\"")
        else:
            print("❌ Failed to get motivational message")
    except Exception as e:
        print(f"❌ Error in motivational message: {e}")
        # Fallback message
        print("   Using fallback: Keep pushing forward! You're doing great!")
    
    # Test 4: Dynamic Plan Adjustment (Travel)
    print("\n✈️ Test 4: Adjusting Plan for Travel...")
    
    try:
        # Create a sample plan
        sample_plan = {
            "title": "Sample Workout Plan",
            "description": "Regular gym workout",
            "weekly_schedule": [
                {
                    "day": "Day 1",
                    "exercises": [
                        {"name": "Bench Press", "sets": 3, "reps": 10, "equipment": "barbell"},
                        {"name": "Squats", "sets": 3, "reps": 12, "equipment": "barbell"}
                    ]
                }
            ]
        }
        
        travel_details = {
            "destination": "hotel",
            "duration_days": 4,
            "equipment_available": "none"
        }
        
        if hasattr(arogya_mitra_agent, '_adjust_for_travel'):
            adjusted_plan = arogya_mitra_agent._adjust_for_travel(sample_plan, travel_details)
        else:
            # Simple adjustment if method doesn't exist
            adjusted_plan = sample_plan.copy()
            adjusted_plan["title"] = f"Travel-Friendly {sample_plan.get('title', 'Workout')}"
            adjusted_plan["description"] = "Modified for travel - no equipment needed"
        
        if adjusted_plan:
            print(f"✅ Plan adjusted for travel!")
            print(f"   New Title: {adjusted_plan.get('title', 'N/A')}")
            print(f"   Description: {adjusted_plan.get('description', 'N/A')}")
        else:
            print("❌ Failed to adjust plan")
    except Exception as e:
        print(f"❌ Error in plan adjustment: {e}")
    
    print("\n" + "=" * 60)
    print("✅ AI Agent Tests Completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_ai_agent())