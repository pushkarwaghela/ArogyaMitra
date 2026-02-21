# backend/app/api/v1/endpoints/youtube.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.services.youtube_service import youtube_service
from app.api.v1.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/youtube", tags=["YouTube"])

@router.get("/search")
async def search_exercise_videos(
    exercise: str = Query(..., description="Name of the exercise"),
    workout_type: Optional[str] = Query(None, description="Type of workout"),
    difficulty: Optional[str] = Query(None, description="Difficulty level"),
    max_results: int = Query(5, description="Maximum number of videos"),
    current_user: User = Depends(get_current_user)
):
    """Search for exercise demonstration videos"""
    videos = await youtube_service.search_exercise_videos(
        exercise_name=exercise,
        workout_type=workout_type,
        difficulty=difficulty,
        max_results=max_results
    )
    
    return {
        "exercise": exercise,
        "total_results": len(videos),
        "videos": videos
    }

@router.get("/playlist/{workout_type}")
async def get_workout_playlist(
    workout_type: str,
    difficulty: str = Query("beginner", description="Difficulty level"),
    current_user: User = Depends(get_current_user)
):
    """Get a playlist of videos for a complete workout"""
    videos = await youtube_service.get_workout_playlist(workout_type, difficulty)
    
    return {
        "workout_type": workout_type,
        "difficulty": difficulty,
        "total_videos": len(videos),
        "videos": videos
    }

@router.get("/video/{video_id}")
async def get_video_details(
    video_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific video"""
    details = await youtube_service._get_video_details(video_id)
    return {
        "video_id": video_id,
        "details": details
    }