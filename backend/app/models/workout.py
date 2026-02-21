# backend/app/models/workout.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base

# Association table for workout-exercise many-to-many relationship
workout_exercises = Table(
    'workout_exercises',
    Base.metadata,
    Column('workout_plan_id', Integer, ForeignKey('workout_plans.id')),
    Column('exercise_id', Integer, ForeignKey('exercises.id'))
)

class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class WorkoutType(str, enum.Enum):
    STRENGTH = "strength"
    CARDIO = "cardio"
    HIIT = "hiit"
    YOGA = "yoga"
    PILATES = "pilates"
    CALISTHENICS = "calisthenics"
    CROSSFIT = "crossfit"
    RECOVERY = "recovery"

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Plan details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    workout_type = Column(Enum(WorkoutType), nullable=False)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.BEGINNER)
    
    # Schedule
    duration_weeks = Column(Integer, default=4)
    sessions_per_week = Column(Integer, default=3)
    session_duration = Column(Integer, default=45)  # in minutes
    
    # Goals
    target_calories_burn = Column(Integer, nullable=True)
    target_weight = Column(Float, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="workout_plans")
    exercises = relationship("Exercise", secondary=workout_exercises, back_populates="workout_plans")
    weekly_schedules = relationship("WeeklySchedule", back_populates="workout_plan", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WorkoutPlan {self.title}>"

class Exercise(Base):
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Exercise details
    muscle_group = Column(String, nullable=True)
    equipment_needed = Column(String, nullable=True)  # JSON string
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.BEGINNER)
    workout_type = Column(Enum(WorkoutType), nullable=True)
    
    # Media
    video_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    instructions = Column(Text, nullable=True)
    
    # Metrics
    calories_per_minute = Column(Float, nullable=True)
    
    # Relationships
    workout_plans = relationship("WorkoutPlan", secondary=workout_exercises, back_populates="exercises")
    exercise_instances = relationship("ExerciseInstance", back_populates="exercise")
    
    def __repr__(self):
        return f"<Exercise {self.name}>"

class WeeklySchedule(Base):
    __tablename__ = "weekly_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id"), nullable=False)
    
    week_number = Column(Integer, nullable=False)  # 1, 2, 3, 4
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    is_rest_day = Column(Boolean, default=False)
    
    # Relationships
    workout_plan = relationship("WorkoutPlan", back_populates="weekly_schedules")
    exercise_instances = relationship("ExerciseInstance", back_populates="weekly_schedule", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WeeklySchedule Week {self.week_number} Day {self.day_of_week}>"

class ExerciseInstance(Base):
    __tablename__ = "exercise_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    weekly_schedule_id = Column(Integer, ForeignKey("weekly_schedules.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    
    # Exercise specifics for this instance
    sets = Column(Integer, default=3)
    reps = Column(Integer, default=10)
    duration = Column(Integer, nullable=True)  # in seconds (for timed exercises)
    rest_time = Column(Integer, default=60)  # in seconds
    weight = Column(Float, nullable=True)  # in kg
    notes = Column(Text, nullable=True)
    
    # Completion tracking
    is_completed = Column(Boolean, default=False)
    actual_sets = Column(Integer, nullable=True)
    actual_reps = Column(Integer, nullable=True)
    actual_duration = Column(Integer, nullable=True)
    actual_weight = Column(Float, nullable=True)
    completion_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    weekly_schedule = relationship("WeeklySchedule", back_populates="exercise_instances")
    exercise = relationship("Exercise", back_populates="exercise_instances")
    
    def __repr__(self):
        return f"<ExerciseInstance {self.exercise_id} on Schedule {self.weekly_schedule_id}>"