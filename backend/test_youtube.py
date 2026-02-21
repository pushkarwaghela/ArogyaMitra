# backend/test_youtube.py
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.youtube_service import youtube_service
import logging

logging.basicConfig(level=logging.INFO)

async def test_youtube():
    print("=" * 60)
    print("🎥 Testing YouTube API Integration")
    print("=" * 60)
    
    # Test 1: Search for push-up videos
    print("\n📹 Test 1: Searching for 'push ups' videos...")
    videos = await youtube_service.search_exercise_videos(
        exercise_name="push ups",
        difficulty="beginner",
        max_results=3
    )
    
    print(f"Found {len(videos)} videos")
    for i, video in enumerate(videos, 1):
        print(f"\n  Video {i}:")
        print(f"    Title: {video.get('title', 'N/A')}")
        print(f"    Channel: {video.get('channel_title', 'N/A')}")
        print(f"    Embed URL: {video.get('embed_url', 'N/A')}")
    
    # Test 2: Search for squat videos
    print("\n\n📹 Test 2: Searching for 'squats' videos...")
    videos = await youtube_service.search_exercise_videos(
        exercise_name="squats",
        workout_type="strength",
        max_results=2
    )
    
    print(f"Found {len(videos)} videos")
    for i, video in enumerate(videos, 1):
        print(f"\n  Video {i}:")
        print(f"    Title: {video.get('title', 'N/A')}")
        print(f"    Channel: {video.get('channel_title', 'N/A')}")
    
    # Test 3: Get workout playlist
    print("\n\n📹 Test 3: Getting beginner yoga playlist...")
    videos = await youtube_service.get_workout_playlist(
        workout_type="yoga",
        difficulty="beginner"
    )
    
    print(f"Found {len(videos)} videos in playlist")
    
    print("\n" + "=" * 60)
    print("✅ YouTube API Tests Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_youtube())