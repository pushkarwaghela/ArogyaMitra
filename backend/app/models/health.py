# backend/app/models/health.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class HealthAssessment(Base):
    __tablename__ = "health_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # Personal Info
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)

    # Medical History
    medical_conditions = Column(Text, nullable=True)  # JSON string
    injuries = Column(Text, nullable=True)  # JSON string
    medications = Column(Text, nullable=True)  # JSON string
    allergies = Column(Text, nullable=True)  # JSON string

    # Lifestyle
    sleep_hours = Column(Float, nullable=True)
    stress_level = Column(String, nullable=True)
    water_intake = Column(String, nullable=True)
    smoking = Column(Boolean, default=False)
    alcohol = Column(Boolean, default=False)

    # Fitness
    fitness_level = Column(String, nullable=True)
    workout_frequency = Column(String, nullable=True)
    preferred_workout_time = Column(String, nullable=True)
    fitness_goal = Column(String, nullable=True)

    # Dietary
    diet_type = Column(String, nullable=True)
    meal_prep_time = Column(String, nullable=True)
    cooking_skill = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="health_assessments")

    def __repr__(self):
        return f"<HealthAssessment for User {self.user_id}>"