"""Analytics data models for personal tracking"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Date, Text, Boolean
from datetime import datetime, UTC
from app.db.base import Base

class SleepLog(Base):
    """Sleep tracking"""
    __tablename__ = "sleep_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    # Sleep metrics
    hours = Column(Float, nullable=False)
    quality = Column(Integer, nullable=True)  # 1-10 scale
    bedtime = Column(String, nullable=True)  # "23:00"
    waketime = Column(String, nullable=True)  # "07:00"
    
    # Additional tracking
    deep_sleep_hours = Column(Float, nullable=True)
    rem_sleep_hours = Column(Float, nullable=True)
    interruptions = Column(Integer, nullable=True)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

class MoodLog(Base):
    """Mood tracking - manual or face detection"""
    __tablename__ = "mood_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))
    
    # Mood metrics
    mood_score = Column(Integer, nullable=False)  # 1-10
    energy_level = Column(Integer, nullable=True)  # 1-10
    stress_level = Column(Integer, nullable=True)  # 1-10
    
    # Face detection (AI-powered)
    detected_from_face = Column(Boolean, default=False)
    face_confidence = Column(Float, nullable=True)
    detected_emotion = Column(String, nullable=True)  # happy, sad, neutral, angry, surprised, fear
    face_image_id = Column(String, nullable=True)  # MongoDB reference
    
    # Manual tracking
    tags = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

class ExerciseLog(Base):
    """Exercise and activity tracking"""
    __tablename__ = "exercise_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    activity_type = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    calories = Column(Integer, nullable=True)
    
    # Activity-specific
    distance_km = Column(Float, nullable=True)
    repetitions = Column(Integer, nullable=True)
    sets = Column(Integer, nullable=True)
    weight_kg = Column(Float, nullable=True)
    
    # Intensity
    intensity = Column(String, nullable=True)  # low, moderate, high
    heart_rate_avg = Column(Integer, nullable=True)
    heart_rate_max = Column(Integer, nullable=True)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

class NutritionLog(Base):
    """Nutrition and meal tracking"""
    __tablename__ = "nutrition_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))
    
    meal_type = Column(String, nullable=False)  # breakfast, lunch, dinner, snack
    description = Column(Text, nullable=False)
    
    # Macros
    calories = Column(Integer, nullable=True)
    protein_g = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    fiber_g = Column(Float, nullable=True)
    water_ml = Column(Integer, nullable=True)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

class WeightLog(Base):
    """Body weight and composition tracking"""
    __tablename__ = "weight_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    weight_kg = Column(Float, nullable=False)
    body_fat_percent = Column(Float, nullable=True)
    muscle_mass_kg = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)
    
    # Measurements
    waist_cm = Column(Float, nullable=True)
    chest_cm = Column(Float, nullable=True)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

class FinanceLog(Base):
    """💰 Financial tracking"""
    __tablename__ = "finance_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    # Transaction
    transaction_type = Column(String, nullable=False)  # income, expense
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    
    # Categorization
    category = Column(String, nullable=False)  # food, transport, salary, etc.
    subcategory = Column(String, nullable=True)
    
    # Payment
    payment_method = Column(String, nullable=True)
    
    # Details
    description = Column(Text, nullable=False)
    merchant = Column(String, nullable=True)
    
    # Metadata
    is_recurring = Column(Boolean, default=False)
    tags = Column(JSON, nullable=True)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

class WaterLog(Base):
    """Water intake tracking"""
    __tablename__ = "water_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    amount_ml = Column(Integer, nullable=False)
    goal_ml = Column(Integer, default=2000)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
