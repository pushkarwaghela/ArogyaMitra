# backend/test_aromi.py
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.aromi_coach import aromi_coach
from app.models.user import User, FitnessGoal, WorkoutPreference, DietPreference
import logging

logging.basicConfig(level=logging.INFO)

async def test_aromi():
    print("=" * 60)
    print("🤖 Testing AROMI AI Coach")
    print("=" * 60)
    
    # Create a mock user
    class MockUser:
        def __init__(self):
            self.id = 1
            self.username = "testuser"
            self.full_name = "Test User"
            self.age = 28
            self.fitness_goal = FitnessGoal.WEIGHT_LOSS
            self.workout_preference = WorkoutPreference.MODERATE
            self.diet_preference = DietPreference.VEGETARIAN
    
    mock_user = MockUser()
    
    # Test messages for different intents
    test_messages = [
        "I'm going on a business trip for 4 days, how should I adjust my workouts?",
        "My knee is hurting from yesterday's workout",
        "I'm feeling really tired today and have no energy",
        "I'm feeling stressed and unmotivated",
        "I only have 15 minutes to workout today",
        "What should I eat for more protein?",
        "I'm not seeing any progress, feeling discouraged",
        "Can you motivate me?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📋 Test {i}: '{message}'")
        print("-" * 40)
        
        result = await aromi_coach.process_message(mock_user, message)
        
        print(f"Intent: {result['intent']}")
        print(f"\nResponse: {result['response']}")
        print(f"\nSuggestions: {result['suggestions']}")
        if result.get('actions'):
            print(f"Actions: {result['actions']}")
        print("-" * 40)
    
    print("\n" + "=" * 60)
    print("✅ AROMI Coach Tests Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_aromi())