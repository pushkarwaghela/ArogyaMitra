# backend/app/api/v1/endpoints/ai_test.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.ai_agent import arogya_mitra_agent
from app.api.v1.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/ai-test", tags=["AI Test"])

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = {}

class ChatResponse(BaseModel):
    response: str
    suggestions: Optional[list] = []

@router.post("/chat", response_model=ChatResponse)
async def test_ai_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Test the AI agent with a simple chat"""
    
    # Simple prompt for testing
    prompt = f"""
    User: {request.message}
    
    As AROMI, the AI fitness coach, provide a helpful, encouraging response.
    Keep it concise and friendly.
    """
    
    try:
        if arogya_mitra_agent.groq_client:
            response = arogya_mitra_agent.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are AROMI, a friendly and motivational AI fitness coach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            reply = response.choices[0].message.content
            
            return ChatResponse(
                response=reply,
                suggestions=[
                    "Tell me about workout plans",
                    "Give me nutrition advice",
                    "Motivate me",
                    "Adjust my plan for travel"
                ]
            )
        else:
            return ChatResponse(
                response="I'm here to help! How can I assist with your fitness journey today?",
                suggestions=["Generate workout", "Meal planning", "Progress tracking"]
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def check_ai_status(current_user: User = Depends(get_current_user)):
    """Check if AI agent is properly configured"""
    return {
        "groq_configured": arogya_mitra_agent.groq_client is not None,
        "api_key_present": bool(arogya_mitra_agent.groq_client) if arogya_mitra_agent.groq_client else False,
        "status": "ready" if arogya_mitra_agent.groq_client else "ai_service_unavailable"
    }