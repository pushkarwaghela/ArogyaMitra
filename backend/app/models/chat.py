# backend/app/models/chat.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum, Float  # Add Float here
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class MessageType(str, enum.Enum):
    USER = "user"
    AI = "ai"
    SYSTEM = "system"

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session metadata
    title = Column(String, default="New Chat")
    context = Column(Text, nullable=True)  # JSON string for conversation context
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatSession {self.id} for User {self.user_id}>"

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    
    # Message content
    message_type = Column(Enum(MessageType), nullable=False)
    content = Column(Text, nullable=False)
    
    # AI-specific fields
    intent = Column(String, nullable=True)  # Detected intent
    sentiment = Column(String, nullable=True)  # Sentiment analysis
    
    # Metadata
    tokens_used = Column(Integer, nullable=True)
    processing_time = Column(Float, nullable=True)  # in seconds
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage {self.message_type} in Session {self.session_id}>"