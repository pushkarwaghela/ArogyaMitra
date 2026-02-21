# backend/app/models/health.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class HealthAssessment(Base):
    __tablename__ = "health_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Vital stats
    bmi = Column(Float, nullable=True)
    body_fat_percentage = Column(Float, nullable=True)
    muscle_mass = Column(Float, nullable=True)
    resting_heart_rate = Column(Integer, nullable=True)
    blood_pressure_systolic = Column(Integer, nullable=True)
    blood_pressure_diastolic = Column(Integer, nullable=True)
    
    # Lifestyle factors
    sleep_hours = Column(Float, nullable=True)
    stress_level = Column(Integer, nullable=True)  # 1-10
    energy_level = Column(Integer, nullable=True)  # 1-10
    water_intake = Column(Integer, nullable=True)  # in ml
    
    # Health conditions (updated)
    current_conditions = Column(Text, nullable=True)  # JSON string
    medications = Column(Text, nullable=True)  # JSON string
    allergies = Column(Text, nullable=True)  # JSON string
    
    # Assessment metadata
    assessment_date = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="health_assessments")
    
    def __repr__(self):
        return f"<HealthAssessment {self.id} for User {self.user_id}>"