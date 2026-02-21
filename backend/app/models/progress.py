# backend/app/models/progress.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class ProgressRecord(Base):
    __tablename__ = "progress_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Date
    record_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Body measurements
    weight = Column(Float, nullable=True)  # in kg
    body_fat_percentage = Column(Float, nullable=True)
    muscle_mass = Column(Float, nullable=True)
    waist_circumference = Column(Float, nullable=True)  # in cm
    hip_circumference = Column(Float, nullable=True)  # in cm
    chest_circumference = Column(Float, nullable=True)  # in cm
    arm_circumference = Column(Float, nullable=True)  # in cm
    thigh_circumference = Column(Float, nullable=True)  # in cm
    
    # Fitness metrics
    strength_score = Column(Integer, nullable=True)  # 1-100
    endurance_score = Column(Integer, nullable=True)  # 1-100
    flexibility_score = Column(Integer, nullable=True)  # 1-100
    
    # Daily stats
    steps_taken = Column(Integer, nullable=True)
    calories_consumed = Column(Integer, nullable=True)
    calories_burned = Column(Integer, nullable=True)
    water_intake = Column(Integer, nullable=True)  # in ml
    sleep_hours = Column(Float, nullable=True)
    
    # Wellness metrics
    mood = Column(Integer, nullable=True)  # 1-10
    energy_level = Column(Integer, nullable=True)  # 1-10
    stress_level = Column(Integer, nullable=True)  # 1-10
    
    # Workout completion
    workout_completed = Column(Boolean, default=False)
    workout_duration = Column(Integer, nullable=True)  # in minutes
    workout_intensity = Column(Integer, nullable=True)  # 1-10
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="progress_records")
    
    def __repr__(self):
        return f"<ProgressRecord {self.record_date} for User {self.user_id}>"

class Achievement(Base):
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)  # e.g., "workout", "nutrition", "milestone"
    
    # Achievement criteria
    criteria_type = Column(String, nullable=True)  # e.g., "workout_streak", "weight_loss"
    criteria_value = Column(String, nullable=True)
    
    # Achievement status
    achieved_at = Column(DateTime(timezone=True), server_default=func.now())
    is_achieved = Column(Boolean, default=True)
    
    # Badge info
    badge_icon = Column(String, nullable=True)
    badge_color = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<Achievement {self.name} for User {self.user_id}>"