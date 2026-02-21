# backend/app/services/aromi_coach.py
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from groq import Groq

from app.config import settings
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage, MessageType
from app.services.ai_agent import arogya_mitra_agent
from app.services.workout_service import WorkoutService
from app.services.nutrition_service import NutritionService

logger = logging.getLogger(__name__)

class AROMICoach:
    """
    AROMI AI Coach - Real-time adaptive fitness companion
    
    Features:
    - Natural language understanding of user needs
    - Context-aware plan adjustments
    - Motivational support
    - Conversation history tracking
    - Dynamic recommendations based on mood, travel, injuries, etc.
    """
    
    def __init__(self):
        self.groq_client = None
        self._init_groq()
        
        # Intent patterns for understanding user messages
        self.intent_patterns = {
            "travel": [
                r"travel", r"trip", r"vacation", r"holiday", r"business trip",
                r"going to", r"visiting", r"away", r"hotel", r"out of town"
            ],
            "injury": [
                r"injur", r"hurt", r"pain", r"ache", r"sore", r"pulled",
                r"strained", r"sprain", r"broken", r"fracture"
            ],
            "fatigue": [
                r"tired", r"exhausted", r"no energy", r"fatigue", r"sleepy",
                r"worn out", r"burned out", r"can't workout"
            ],
            "mood": [
                r"mood", r"feeling", r"depressed", r"anxious", r"stressed",
                r"sad", r"down", r"low", r"unmotivated"
            ],
            "time_constraint": [
                r"busy", r"no time", r"short on time", r"hectic", r"schedule",
                r"deadline", r"work load", r"can't find time"
            ],
            "motivation": [
                r"motivat", r"inspire", r"encourage", r"give up", r"quitting",
                r"losing hope", r"discouraged"
            ],
            "nutrition": [
                r"eat", r"meal", r"food", r"diet", r"hungry", r"recipe",
                r"cook", r"snack", r"calories", r"protein"
            ],
            "workout": [
                r"exercise", r"workout", r"train", r"gym", r"routine",
                r"fitness", r"strength", r"cardio"
            ],
            "progress": [
                r"progress", r"result", r"improve", r"getting better",
                r"weight loss", r"muscle gain", r"see change"
            ]
        }
    
    def _init_groq(self):
        """Initialize Groq client"""
        try:
            if settings.GROQ_API_KEY:
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
                logger.info("✅ AROMI AI Coach initialized with Groq")
            else:
                logger.warning("⚠️ No Groq API key found for AROMI")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Groq for AROMI: {e}")
    
    async def process_message(
        self,
        user: User,
        message: str,
        session_id: Optional[int] = None,
        db_session = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate appropriate response
        
        Args:
            user: User object
            message: User's message text
            session_id: Optional chat session ID
            db_session: Database session for storing chat history
            
        Returns:
            Response with message, suggestions, and any actions taken
        """
        
        # Detect intent
        intent = self._detect_intent(message)
        logger.info(f"Detected intent: {intent}")
        
        # Extract entities and context
        entities = self._extract_entities(message)
        
        # Generate response based on intent
        if self.groq_client:
            response_text, actions = await self._generate_ai_response(user, message, intent, entities)
        else:
            response_text, actions = self._generate_rule_based_response(user, message, intent, entities)
        
        # Store in database if session provided
        if db_session and session_id:
            await self._store_message(db_session, session_id, message, response_text, intent, actions)
        
        # Prepare suggestions
        suggestions = self._get_suggestions(intent, actions)
        
        return {
            "response": response_text,
            "intent": intent,
            "actions": actions,
            "suggestions": suggestions,
            "session_id": session_id
        }
    
    def _detect_intent(self, message: str) -> str:
        """Detect the primary intent of the user message"""
        message_lower = message.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return intent
        
        return "general"
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """Extract relevant entities from message"""
        entities = {}
        
        # Extract numbers (duration, sets, reps, etc.)
        numbers = re.findall(r'\d+', message)
        if numbers:
            entities["numbers"] = [int(n) for n in numbers]
        
        # Extract body parts for injuries
        body_parts = ["back", "knee", "shoulder", "wrist", "ankle", "hip", "elbow", "neck"]
        for part in body_parts:
            if part in message.lower():
                entities["body_part"] = part
                break
        
        # Extract time references
        if "day" in message.lower() or "days" in message.lower():
            entities["timeframe"] = "days"
        elif "week" in message.lower() or "weeks" in message.lower():
            entities["timeframe"] = "weeks"
        elif "month" in message.lower():
            entities["timeframe"] = "months"
        
        return entities
    
    async def _generate_ai_response(
        self,
        user: User,
        message: str,
        intent: str,
        entities: Dict[str, Any]
    ) -> tuple:
        """Generate response using Groq AI"""
        
        # Build context from user profile
        user_context = self._build_user_context(user)
        
        # Build prompt
        prompt = f"""
        You are AROMI, an empathetic and knowledgeable AI fitness coach. Respond to the user's message in a helpful, encouraging way.
        
        User Context:
        - Name: {user.full_name or user.username}
        - Age: {user.age or 'Not specified'}
        - Fitness Goal: {user.fitness_goal.value if user.fitness_goal else 'Not specified'}
        - Workout Preference: {user.workout_preference.value if user.workout_preference else 'Not specified'}
        - Diet Preference: {user.diet_preference.value if user.diet_preference else 'Not specified'}
        
        User Message: "{message}"
        Detected Intent: {intent}
        
        Provide a response that:
        1. Acknowledges their message empathetically
        2. Offers specific advice related to their intent
        3. Suggests concrete actions they can take
        4. Keeps the tone warm and motivating
        
        Keep the response concise (under 150 words) and actionable.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are AROMI, a friendly and motivational AI fitness coach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            response_text = response.choices[0].message.content
            
            # Determine if any actions should be taken
            actions = await self._determine_actions(user, intent, entities, message)
            
            return response_text, actions
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self._generate_rule_based_response(user, message, intent, entities)
    
    def _generate_rule_based_response(
        self,
        user: User,
        message: str,
        intent: str,
        entities: Dict[str, Any]
    ) -> tuple:
        """Generate rule-based response when AI is unavailable"""
        
        responses = {
            "travel": {
                "response": "Traveling is a great opportunity to explore new ways to stay active! Here are some travel-friendly workout tips:\n\n• Bodyweight exercises (push-ups, squats, lunges)\n• Use hotel stairs for cardio\n• Stretching routines for recovery\n• Quick 15-minute HIIT workouts\n\nWould you like me to adjust your current workout plan for travel?",
                "actions": [{"type": "adjust_plan", "reason": "travel"}]
            },
            "injury": {
                "response": "I'm sorry to hear about your injury. Your health comes first! Here's what I recommend:\n\n• Rest the injured area\n• Focus on other muscle groups\n• Gentle stretching if approved\n• Consult with a healthcare professional\n\nI can modify your workouts to avoid the injured area.",
                "actions": [{"type": "adjust_plan", "reason": "injury", "body_part": entities.get("body_part")}]
            },
            "fatigue": {
                "response": "It's normal to feel tired sometimes. Listen to your body! Here are some suggestions:\n\n• Take a rest day (recovery is important!)\n• Try gentle activities like walking or yoga\n• Ensure you're getting enough sleep\n• Stay hydrated and eat well\n\nRemember, consistency over intensity!",
                "actions": [{"type": "adjust_plan", "reason": "fatigue"}]
            },
            "mood": {
                "response": "I hear you. Exercise can be a powerful mood booster! Here's what might help:\n\n• A gentle workout to release endorphins\n• Outdoor activities for fresh air\n• Meditation or deep breathing\n• Talk to someone you trust\n\nYou've got this! 💪",
                "actions": [{"type": "motivate"}]
            },
            "time_constraint": {
                "response": "Short on time? No problem! Here are some efficient options:\n\n• 15-minute HIIT workouts\n• Superset exercises to save time\n• Focus on compound movements\n• Schedule workouts like appointments\n\nI can create quick workout plans for busy days.",
                "actions": [{"type": "adjust_plan", "reason": "time"}]
            },
            "motivation": {
                "response": "You're doing amazing! Remember why you started. Here's a boost:\n\n• Every workout counts, no matter how small\n• Progress takes time - be patient with yourself\n• Celebrate small victories\n• You're stronger than you think!\n\nWhat's one small win you can celebrate today?",
                "actions": [{"type": "motivate"}]
            },
            "nutrition": {
                "response": "Great question about nutrition! Here are some tips:\n\n• Eat protein with every meal\n• Stay hydrated throughout the day\n• Plan meals ahead to stay on track\n• Listen to your hunger cues\n\nI can suggest meal ideas based on your preferences!",
                "actions": [{"type": "nutrition_advice"}]
            },
            "workout": {
                "response": "Ready to work out? That's awesome! Here are some suggestions:\n\n• Check your workout plan for today\n• Warm up properly before starting\n• Focus on form over speed\n• Stay hydrated\n\nWhat type of workout are you in the mood for?",
                "actions": [{"type": "show_workout"}]
            },
            "progress": {
                "response": "Progress is about consistency, not perfection! Here's how you're doing:\n\n• Every workout builds momentum\n• Small improvements add up\n• Take progress photos and measurements\n• Celebrate non-scale victories\n\nKeep up the great work! 🌟",
                "actions": [{"type": "show_progress"}]
            }
        }
        
        # Default response
        default_response = {
            "response": "I'm here to help with your fitness journey! You can ask me about workouts, nutrition, motivation, or adjusting your plan based on travel, injuries, or time constraints.",
            "actions": []
        }
        
        response_data = responses.get(intent, default_response)
        return response_data["response"], response_data.get("actions", [])
    
    async def _determine_actions(
        self,
        user: User,
        intent: str,
        entities: Dict[str, Any],
        message: str
    ) -> List[Dict[str, Any]]:
        """Determine what actions to take based on the conversation"""
        actions = []
        
        # Travel-related actions
        if intent == "travel":
            # Check if they want plan adjustment
            if any(word in message.lower() for word in ["adjust", "change", "modify", "update", "new"]):
                actions.append({
                    "type": "adjust_plan",
                    "reason": "travel",
                    "duration": entities.get("numbers", [4])[0] if entities.get("numbers") else 4
                })
        
        # Injury-related actions
        elif intent == "injury":
            body_part = entities.get("body_part", "unknown")
            actions.append({
                "type": "adjust_plan",
                "reason": "injury",
                "body_part": body_part,
                "severity": "mild"  # Could be determined by keywords
            })
        
        # Time constraint actions
        elif intent == "time_constraint":
            if entities.get("numbers"):
                available_minutes = entities["numbers"][0]
                actions.append({
                    "type": "quick_workout",
                    "duration": min(available_minutes, 30)  # Cap at 30 min
                })
        
        return actions
    
    def _build_user_context(self, user: User) -> str:
        """Build context string from user profile"""
        context = []
        context.append(f"Name: {user.full_name or user.username}")
        if user.age:
            context.append(f"Age: {user.age}")
        if user.fitness_goal:
            context.append(f"Goal: {user.fitness_goal.value}")
        if user.workout_preference:
            context.append(f"Workout Preference: {user.workout_preference.value}")
        if user.diet_preference:
            context.append(f"Diet: {user.diet_preference.value}")
        return "\n".join(context)
    
    def _get_suggestions(self, intent: str, actions: List[Dict]) -> List[str]:
        """Get contextual suggestions based on intent and actions"""
        
        suggestions = {
            "travel": [
                "Adjust my plan for travel",
                "Travel-friendly workouts",
                "Healthy eating on vacation"
            ],
            "injury": [
                "Modify workouts for injury",
                "Alternative exercises",
                "Recovery tips"
            ],
            "fatigue": [
                "Rest day activities",
                "Energy-boosting tips",
                "Light workout options"
            ],
            "mood": [
                "Mood-boosting workouts",
                "Meditation exercises",
                "Talk to someone"
            ],
            "time_constraint": [
                "15-minute workouts",
                "Quick meal prep",
                "Schedule planning"
            ],
            "motivation": [
                "Success stories",
                "Daily motivation",
                "Progress tracking"
            ],
            "nutrition": [
                "Meal ideas",
                "Snack suggestions",
                "Hydration tips"
            ],
            "workout": [
                "Today's workout",
                "Exercise library",
                "Workout history"
            ],
            "progress": [
                "View my progress",
                "Update measurements",
                "Set new goals"
            ]
        }
        
        # Add action-specific suggestions
        if actions:
            for action in actions:
                if action.get("type") == "adjust_plan":
                    suggestions["general"] = ["Confirm adjustment", "See modified plan", "Keep original plan"]
        
        return suggestions.get(intent, [
            "Tell me more",
            "Give me advice",
            "Motivate me",
            "Adjust my plan"
        ])
    
    async def _store_message(
        self,
        db_session,
        session_id: int,
        user_message: str,
        ai_response: str,
        intent: str,
        actions: List[Dict]
    ):
        """Store conversation in database"""
        try:
            from app.models.chat import ChatMessage
            
            # Store user message
            user_msg = ChatMessage(
                session_id=session_id,
                message_type=MessageType.USER,
                content=user_message,
                intent=intent
            )
            db_session.add(user_msg)
            
            # Store AI response
            ai_msg = ChatMessage(
                session_id=session_id,
                message_type=MessageType.AI,
                content=ai_response,
                intent=intent,
                metadata=json.dumps({"actions": actions})
            )
            db_session.add(ai_msg)
            
            db_session.commit()
        except Exception as e:
            logger.error(f"Error storing chat message: {e}")
            db_session.rollback()
    
    async def create_chat_session(self, db_session, user_id: int) -> int:
        """Create a new chat session"""
        from app.models.chat import ChatSession
        
        session = ChatSession(
            user_id=user_id,
            title=f"Chat with AROMI - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        
        return session.id
    
    async def get_chat_history(self, db_session, session_id: int, limit: int = 50) -> List[Dict]:
        """Get chat history for a session"""
        from app.models.chat import ChatMessage
        
        messages = db_session.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.asc()).limit(limit).all()
        
        return [
            {
                "id": msg.id,
                "type": msg.message_type.value,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat(),
                "intent": msg.intent
            }
            for msg in messages
        ]


# Singleton instance
aromi_coach = AROMICoach()