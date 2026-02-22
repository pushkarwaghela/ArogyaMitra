# backend/app/services/youtube_service.py
import httpx
import asyncio
from typing import List, Dict, Optional, Any
import logging
from app.config import settings  # Changed from app.core.config to app.config

logger = logging.getLogger(__name__)

class YouTubeService:
    """Service to interact with YouTube Data API v3"""
    
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.max_results = 5  # Default number of videos to fetch
        
    async def search_exercise_videos(
        self, 
        exercise_name: str, 
        workout_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for exercise demonstration videos on YouTube
        
        Args:
            exercise_name: Name of the exercise (e.g., "push ups")
            workout_type: Type of workout (e.g., "strength", "cardio")
            difficulty: Difficulty level (e.g., "beginner", "intermediate")
            max_results: Maximum number of videos to return
            
        Returns:
            List of video information dictionaries
        """
        try:
            # Build search query
            query = self._build_search_query(exercise_name, workout_type, difficulty)
            
            # Make API request
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search",
                    params={
                        "part": "snippet",
                        "q": query,
                        "type": "video",
                        "maxResults": max_results,
                        "key": self.api_key,
                        "videoEmbeddable": "true",
                        "safeSearch": "moderate"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    videos = await self._enrich_video_data(data.get("items", []))
                    return videos
                else:
                    logger.error(f"YouTube API error: {response.status_code} - {response.text}")
                    return self._get_fallback_videos(exercise_name)
                    
        except Exception as e:
            logger.error(f"Error fetching YouTube videos: {e}")
            return self._get_fallback_videos(exercise_name)
    
    def _build_search_query(self, exercise: str, workout_type: Optional[str], difficulty: Optional[str]) -> str:
        """Build a search query string"""
        query_parts = [exercise, "exercise", "how to", "proper form", "tutorial"]
        
        if difficulty:
            query_parts.append(difficulty)
        
        if workout_type:
            if workout_type.lower() == "strength":
                query_parts.append("strength training")
            elif workout_type.lower() == "cardio":
                query_parts.append("cardio")
            elif workout_type.lower() == "yoga":
                query_parts.append("yoga")
        
        return " ".join(query_parts)
    
    async def _enrich_video_data(self, video_items: List[Dict]) -> List[Dict[str, Any]]:
        """Enrich video data with additional details"""
        enriched_videos = []
        
        for item in video_items:
            video_id = item["id"]["videoId"]
            
            # Get video details (duration, statistics)
            video_details = await self._get_video_details(video_id)
            
            video_info = {
                "video_id": video_id,
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                "channel_title": item["snippet"]["channelTitle"],
                "published_at": item["snippet"]["publishedAt"],
                "embed_url": f"https://www.youtube.com/embed/{video_id}",
                "watch_url": f"https://www.youtube.com/watch?v={video_id}",
                "duration": video_details.get("duration", "PT0M"),
                "view_count": video_details.get("view_count", 0),
                "like_count": video_details.get("like_count", 0)
            }
            
            enriched_videos.append(video_info)
        
        return enriched_videos

    async def _get_video_details(self, video_id: str) -> Dict[str, Any]:
        """Get additional details for a specific video"""
        try:
            if not self.api_key or self.api_key == 'your-youtube-api-key':
                return {}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/videos",
                    params={
                        "part": "contentDetails,statistics",
                        "id": video_id,
                        "key": self.api_key
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    if items:
                        item = items[0]
                        return {
                            "duration": item["contentDetails"]["duration"],
                            "view_count": int(item["statistics"].get("viewCount", 0)),
                            "like_count": int(item["statistics"].get("likeCount", 0))
                        }
                else:
                    logger.warning(f"YouTube API returned {response.status_code}")
        except Exception as e:
            logger.debug(f"Error fetching video details (non-critical): {e}")

        return {}
    
    def _get_fallback_videos(self, exercise_name: str) -> List[Dict[str, Any]]:
        """Provide fallback video data when API fails"""
        # Common exercises with known good tutorials
        fallback_exercises = {
            "push ups": [
                {
                    "video_id": "IODxDxX7oi4",
                    "title": "How to Do a Push-Up | Perfect Form",
                    "channel_title": "Howcast",
                    "embed_url": "https://www.youtube.com/embed/IODxDxX7oi4"
                }
            ],
            "squats": [
                {
                    "video_id": "aclHkVaku9U",
                    "title": "How to Squat: Proper Form",
                    "channel_title": "Men's Health",
                    "embed_url": "https://www.youtube.com/embed/aclHkVaku9U"
                }
            ],
            "lunges": [
                {
                    "video_id": "QOVaHwm-Q6c",
                    "title": "How to Do Lunges | Perfect Form",
                    "channel_title": "Howcast",
                    "embed_url": "https://www.youtube.com/embed/QOVaHwm-Q6c"
                }
            ]
        }
        
        # Try to find fallback for the exercise
        for key, videos in fallback_exercises.items():
            if key in exercise_name.lower():
                return videos
        
        # Generic fallback
        return [{
            "video_id": "placeholder",
            "title": f"Exercise tutorial for {exercise_name}",
            "channel_title": "ArogyaMitra",
            "embed_url": "",
            "message": "Video tutorial coming soon"
        }]
    
    async def get_workout_playlist(self, workout_type: str, difficulty: str) -> List[Dict[str, Any]]:
        """Get a playlist of videos for a full workout"""
        search_terms = {
            "strength": f"{difficulty} strength training full body workout",
            "cardio": f"{difficulty} cardio workout at home",
            "yoga": f"{difficulty} yoga flow for beginners",
            "hiit": f"{difficulty} HIIT workout no equipment"
        }
        
        query = search_terms.get(workout_type.lower(), f"{difficulty} {workout_type} workout")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/search",
                params={
                    "part": "snippet",
                    "q": query,
                    "type": "video",
                    "maxResults": 10,
                    "key": self.api_key,
                    "videoEmbeddable": "true"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return await self._enrich_video_data(data.get("items", []))
            
            return []

# Create singleton instance
youtube_service = YouTubeService()