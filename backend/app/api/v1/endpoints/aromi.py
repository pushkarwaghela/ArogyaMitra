# backend/app/api/v1/endpoints/aromi.py
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
import json
import asyncio

from app.database import get_db
from app.api.v1.dependencies import get_current_user
from app.models.user import User
from app.services.aromi_coach import aromi_coach

router = APIRouter(prefix="/aromi", tags=["AROMI AI Coach"])

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    suggestions: List[str]
    session_id: Optional[int] = None
    actions: List[dict] = []

class SessionResponse(BaseModel):
    id: int
    title: str
    created_at: str
    message_count: int

class MessageResponse(BaseModel):
    id: int
    type: str
    content: str
    timestamp: str
    intent: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_with_aromi(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with AROMI AI Coach for real-time fitness advice
    """
    # Create new session if not provided
    session_id = request.session_id
    if not session_id:
        session_id = await aromi_coach.create_chat_session(db, current_user.id)
    
    # Process message
    result = await aromi_coach.process_message(
        user=current_user,
        message=request.message,
        session_id=session_id,
        db_session=db
    )
    
    return ChatResponse(
        response=result["response"],
        intent=result["intent"],
        suggestions=result["suggestions"],
        session_id=session_id,
        actions=result.get("actions", [])
    )

@router.get("/sessions", response_model=List[SessionResponse])
async def get_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all chat sessions for the user"""
    from app.models.chat import ChatSession, ChatMessage
    
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.created_at.desc()).all()
    
    result = []
    for session in sessions:
        message_count = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).count()
        
        result.append(SessionResponse(
            id=session.id,
            title=session.title,
            created_at=session.created_at.isoformat(),
            message_count=message_count
        ))
    
    return result

@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages for a specific chat session"""
    from app.models.chat import ChatSession
    
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    history = await aromi_coach.get_chat_history(db, session_id)
    return history

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session"""
    from app.models.chat import ChatSession
    
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(session)
    db.commit()
    
    return {"message": "Session deleted successfully"}

@router.post("/adjust-plan")
async def adjust_workout_plan(
    adjustment_type: str,
    details: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Adjust workout plan based on real-time factors"""
    from app.services.workout_service import WorkoutService
    
    # Get active workout plan
    active_plan = await WorkoutService.get_active_workout_plan(db, current_user.id)
    if not active_plan:
        raise HTTPException(status_code=404, detail="No active workout plan found")
    
    # Adjust plan using AI agent
    from app.services.ai_agent import arogya_mitra_agent
    
    # Convert plan to dict
    plan_dict = {
        "id": active_plan.id,
        "title": active_plan.title,
        "description": active_plan.description,
        "weekly_schedule": []  # Would need to fetch exercises
    }
    
    adjusted = await arogya_mitra_agent.adjust_plan_dynamically(
        current_user, plan_dict, adjustment_type, details
    )
    
    return {
        "message": f"Plan adjusted for {adjustment_type}",
        "adjustments": adjusted
    }

@router.get("/quick-tip")
async def get_quick_tip(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get a quick fitness tip"""
    tips = {
        "nutrition": [
            "Drink water before meals to help control portions",
            "Include protein in every meal to stay full longer",
            "Eat colorful vegetables for a variety of nutrients",
            "Plan your meals ahead to avoid unhealthy choices"
        ],
        "workout": [
            "Warm up for 5-10 minutes before exercising",
            "Focus on form, not just weight",
            "Rest 48 hours between strength training same muscle groups",
            "Listen to your body - rest when needed"
        ],
        "motivation": [
            "Remember why you started",
            "Celebrate small victories",
            "Find a workout buddy for accountability",
            "Track your progress to stay motivated"
        ],
        "recovery": [
            "Get 7-9 hours of sleep for optimal recovery",
            "Stretch after workouts when muscles are warm",
            "Stay hydrated throughout the day",
            "Consider foam rolling for muscle recovery"
        ]
    }
    
    if category and category in tips:
        import random
        return {"tip": random.choice(tips[category])}
    else:
        all_tips = []
        for cat_tips in tips.values():
            all_tips.extend(cat_tips)
        import random
        return {"tip": random.choice(all_tips)}

# WebSocket for real-time chat
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket connection for real-time AROMI coaching"""
    await websocket.accept()
    try:
        # Get user from token (would need authentication)
        # For now, assume first user
        from app.database import SessionLocal
        db = SessionLocal()
        user = db.query(User).first()
        
        # Create chat session
        session_id = await aromi_coach.create_chat_session(db, user.id)
        
        await websocket.send_text(json.dumps({
            "type": "welcome",
            "message": f"Hello {user.full_name}! I'm AROMI, your AI fitness coach. How can I help you today?",
            "session_id": session_id
        }))
        
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message
            result = await aromi_coach.process_message(
                user=user,
                message=message_data.get("message", ""),
                session_id=session_id,
                db_session=db
            )
            
            # Send response
            await websocket.send_text(json.dumps({
                "type": "response",
                "data": result
            }))
            
    except WebSocketDisconnect:
        logger.info("Client disconnected from WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        db.close()