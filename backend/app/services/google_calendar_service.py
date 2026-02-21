# backend/app/services/google_calendar_service.py
import os
import pickle
import datetime
from typing import List, Dict, Optional, Any
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.config import settings

logger = logging.getLogger(__name__)

class GoogleCalendarService:
    """Service to interact with Google Calendar API"""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
# In the __init__ method, make sure redirect_uri is set correctly
    def __init__(self):
        self.client_id = settings.GOOGLE_CALENDAR_CLIENT_ID
        self.client_secret = settings.GOOGLE_CALENDAR_CLIENT_SECRET
        self.redirect_uri = "http://localhost:8000/api/v1/calendar/callback"  # Hardcode to be safe
        self.token_dir = "tokens"
        
        # Create token directory if it doesn't exist
        os.makedirs(self.token_dir, exist_ok=True)
        
        print(f"📅 Google Calendar Service initialized with redirect URI: {self.redirect_uri}")
    
    def get_authorization_url(self, user_id: int) -> str:
        """Get Google OAuth authorization URL for a user"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        # Generate authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=str(user_id),
            prompt='consent'
        )
        
        return auth_url
    
    async def handle_oauth_callback(self, code: str, user_id: int) -> bool:
        """Handle OAuth callback and save token for user"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=self.SCOPES,
                redirect_uri=self.redirect_uri
            )
            
            # Exchange code for token
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            # Save credentials for user
            self._save_credentials(user_id, credentials)
            return True
            
        except Exception as e:
            logger.error(f"Error in OAuth callback: {e}")
            return False
    
    def _save_credentials(self, user_id: int, credentials):
        """Save user credentials to file"""
        token_path = os.path.join(self.token_dir, f"token_{user_id}.pickle")
        with open(token_path, 'wb') as token:
            pickle.dump(credentials, token)
    
    def _load_credentials(self, user_id: int) -> Optional[Credentials]:
        """Load user credentials from file"""
        token_path = os.path.join(self.token_dir, f"token_{user_id}.pickle")
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                return pickle.load(token)
        return None
    
    def _refresh_credentials_if_needed(self, credentials: Credentials) -> Credentials:
        """Refresh credentials if expired"""
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
            except Exception as e:
                logger.error(f"Error refreshing credentials: {e}")
        return credentials
    
    async def create_workout_event(
        self,
        user_id: int,
        workout_title: str,
        workout_description: str,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        location: str = "Home/Gym"
    ) -> Optional[Dict[str, Any]]:
        """
        Create a calendar event for a workout
        
        Args:
            user_id: User ID
            workout_title: Title of the workout
            workout_description: Description with exercises
            start_time: When the workout starts
            end_time: When the workout ends
            location: Where the workout takes place
            
        Returns:
            Created event details or None if failed
        """
        try:
            # Load credentials
            credentials = self._load_credentials(user_id)
            if not credentials:
                logger.error(f"No credentials found for user {user_id}")
                return None
            
            # Refresh if needed
            credentials = self._refresh_credentials_if_needed(credentials)
            
            # Build service
            service = build('calendar', 'v3', credentials=credentials)
            
            # Create event
            event = {
                'summary': f"🏋️ {workout_title}",
                'location': location,
                'description': workout_description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 30},
                        {'method': 'email', 'minutes': 60},
                    ],
                },
                'colorId': '4',  # Green color for workouts
                'transparency': 'opaque',
                'visibility': 'public'
            }
            
            # Insert event
            event = service.events().insert(calendarId='primary', body=event).execute()
            logger.info(f"Event created: {event.get('htmlLink')}")
            
            return {
                'event_id': event.get('id'),
                'html_link': event.get('htmlLink'),
                'summary': event.get('summary'),
                'start': event.get('start'),
                'end': event.get('end')
            }
            
        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            return None
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            return None
    
    async def create_weekly_workout_schedule(
        self,
        user_id: int,
        workout_plan: Dict[str, Any],
        start_date: datetime.date
    ) -> List[Dict[str, Any]]:
        """
        Create a full week of workout events
        
        Args:
            user_id: User ID
            workout_plan: Workout plan with daily schedules
            start_date: Start date for the week
            
        Returns:
            List of created events
        """
        created_events = []
        
        if 'weekly_schedule' not in workout_plan:
            return created_events
        
        for day_index, day_data in enumerate(workout_plan['weekly_schedule']):
            if day_data.get('is_rest_day', False):
                continue
            
            # Calculate date for this day
            workout_date = start_date + datetime.timedelta(days=day_index)
            
            # Set workout time (default to 7:00 AM if not specified)
            start_hour = day_data.get('start_hour', 7)
            start_minute = day_data.get('start_minute', 0)
            duration_minutes = day_data.get('duration', 45)
            
            start_datetime = datetime.datetime.combine(
                workout_date,
                datetime.time(start_hour, start_minute)
            )
            end_datetime = start_datetime + datetime.timedelta(minutes=duration_minutes)
            
            # Build workout description
            description = f"Workout Type: {day_data.get('workout_type', 'Mixed')}\n\n"
            description += "Exercises:\n"
            
            for exercise in day_data.get('exercises', []):
                if isinstance(exercise, dict):
                    name = exercise.get('name', 'Exercise')
                    sets = exercise.get('sets', '')
                    reps = exercise.get('reps', '')
                    duration = exercise.get('duration', '')
                    
                    if reps:
                        description += f"• {name}: {sets} sets × {reps} reps\n"
                    elif duration:
                        description += f"• {name}: {duration} seconds\n"
                    else:
                        description += f"• {name}\n"
            
            # Create event
            event = await self.create_workout_event(
                user_id=user_id,
                workout_title=f"Day {day_index + 1}: {day_data.get('workout_type', 'Workout')}",
                workout_description=description,
                start_time=start_datetime,
                end_time=end_datetime,
                location=day_data.get('location', 'Home/Gym')
            )
            
            if event:
                created_events.append(event)
        
        return created_events
    
    async def update_workout_event(
        self,
        user_id: int,
        event_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an existing workout event"""
        try:
            credentials = self._load_credentials(user_id)
            if not credentials:
                return None
            
            credentials = self._refresh_credentials_if_needed(credentials)
            service = build('calendar', 'v3', credentials=credentials)
            
            # Get existing event
            event = service.events().get(calendarId='primary', eventId=event_id).execute()
            
            # Apply updates
            for key, value in updates.items():
                if key in event:
                    event[key] = value
            
            # Update event
            updated_event = service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            return {
                'event_id': updated_event.get('id'),
                'html_link': updated_event.get('htmlLink'),
                'summary': updated_event.get('summary')
            }
            
        except Exception as e:
            logger.error(f"Error updating event: {e}")
            return None
    
    async def delete_workout_event(self, user_id: int, event_id: str) -> bool:
        """Delete a workout event"""
        try:
            credentials = self._load_credentials(user_id)
            if not credentials:
                return False
            
            credentials = self._refresh_credentials_if_needed(credentials)
            service = build('calendar', 'v3', credentials=credentials)
            
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            return False
    
    async def get_upcoming_workouts(self, user_id: int, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get upcoming workout events from calendar"""
        try:
            credentials = self._load_credentials(user_id)
            if not credentials:
                return []
            
            credentials = self._refresh_credentials_if_needed(credentials)
            service = build('calendar', 'v3', credentials=credentials)
            
            # Get current time
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            
            # Get events
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime',
                q='🏋️'  # Search for workout events
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                formatted_events.append({
                    'event_id': event.get('id'),
                    'summary': event.get('summary'),
                    'description': event.get('description'),
                    'start': event.get('start', {}).get('dateTime', event.get('start', {}).get('date')),
                    'end': event.get('end', {}).get('dateTime', event.get('end', {}).get('date')),
                    'html_link': event.get('htmlLink')
                })
            
            return formatted_events
            
        except Exception as e:
            logger.error(f"Error getting upcoming workouts: {e}")
            return []
    
    async def check_calendar_connection(self, user_id: int) -> Dict[str, Any]:
        """Check if user is connected to Google Calendar"""
        credentials = self._load_credentials(user_id)
        
        if not credentials:
            return {
                'connected': False,
                'auth_url': self.get_authorization_url(user_id)
            }
        
        # Test the connection
        try:
            credentials = self._refresh_credentials_if_needed(credentials)
            service = build('calendar', 'v3', credentials=credentials)
            
            # Try to list calendars as a test
            calendar_list = service.calendarList().list().execute()
            
            return {
                'connected': True,
                'email': credentials.valid,
                'calendar_count': len(calendar_list.get('items', []))
            }
        except Exception as e:
            logger.error(f"Calendar connection test failed: {e}")
            return {
                'connected': False,
                'error': str(e),
                'auth_url': self.get_authorization_url(user_id)
            }

# Create singleton instance
google_calendar_service = GoogleCalendarService()