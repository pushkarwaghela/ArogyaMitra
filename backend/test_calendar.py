# backend/test_calendar.py
import asyncio
import sys
import os
import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.google_calendar_service import google_calendar_service
import logging

logging.basicConfig(level=logging.INFO)

async def test_calendar():
    print("=" * 60)
    print("📅 Testing Google Calendar Integration")
    print("=" * 60)
    
    # Test 1: Check connection (will fail without token)
    print("\n📋 Test 1: Checking calendar connection...")
    user_id = 1  # Test user ID
    status = await google_calendar_service.check_calendar_connection(user_id)
    
    print(f"Connected: {status.get('connected')}")
    if not status.get('connected'):
        print(f"Auth URL: {status.get('auth_url')}")
        print("\n⚠️  Please visit the auth URL to connect your Google Calendar")
    
    # Test 2: Create a test workout event (only if connected)
    if status.get('connected'):
        print("\n📋 Test 2: Creating test workout event...")
        
        now = datetime.datetime.now()
        start_time = now + datetime.timedelta(days=1, hours=7)  # Tomorrow 7 AM
        end_time = start_time + datetime.timedelta(minutes=45)
        
        event = await google_calendar_service.create_workout_event(
            user_id=user_id,
            workout_title="Test Workout: Full Body",
            workout_description="• Push-ups: 3x10\n• Squats: 3x15\n• Planks: 3x30s",
            start_time=start_time,
            end_time=end_time,
            location="Home Gym"
        )
        
        if event:
            print(f"✅ Event created!")
            print(f"   Title: {event.get('summary')}")
            print(f"   Link: {event.get('html_link')}")
        else:
            print("❌ Failed to create event")
        
        # Test 3: Get upcoming workouts
        print("\n📋 Test 3: Getting upcoming workouts...")
        workouts = await google_calendar_service.get_upcoming_workouts(user_id=user_id)
        
        print(f"Found {len(workouts)} upcoming workouts")
        for i, workout in enumerate(workouts[:3], 1):  # Show first 3
            print(f"\n  Workout {i}:")
            print(f"    {workout.get('summary')}")
            print(f"    Start: {workout.get('start')}")
    
    print("\n" + "=" * 60)
    print("✅ Google Calendar Tests Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_calendar())