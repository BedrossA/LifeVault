"""Analytics schemas for API validation"""
from pydantic import BaseModel, Field, ConfigDict, field_validator, ValidationInfo
from typing import Optional, List
from datetime import date, datetime
import math

class AnalyticsEntryCreate(BaseModel):
    category: str = Field(..., min_length=1, max_length=50)
    metric: str = Field(..., min_length=1, max_length=50)
    value: float
    unit: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator('value')
    @classmethod
    def validate_value(cls, v: float) -> float:
        # Pydantic V2 has built-in finite checks, but for custom logic:
        if not math.isfinite(v):
            raise ValueError('Value must be a finite number')
        return v

    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed = {'health', 'fitness', 'productivity', 'mood', 'finance', 'other'}
        if v not in allowed:
            raise ValueError(f'Category must be one of {sorted(allowed)}')
        return v
# Sleep Schemas
class SleepLogCreate(BaseModel):
    date: date
    hours: float = Field(..., ge=0, le=24)
    quality: Optional[int] = Field(None, ge=1, le=10)
    bedtime: Optional[str] = None
    waketime: Optional[str] = None
    deep_sleep_hours: Optional[float] = None
    rem_sleep_hours: Optional[float] = None
    interruptions: Optional[int] = None
    notes: Optional[str] = None

class SleepLogUpdate(BaseModel):
    hours: Optional[float] = Field(None, ge=0, le=24)
    quality: Optional[int] = Field(None, ge=1, le=10)
    bedtime: Optional[str] = None
    waketime: Optional[str] = None
    deep_sleep_hours: Optional[float] = None
    rem_sleep_hours: Optional[float] = None
    interruptions: Optional[int] = None
    notes: Optional[str] = None

class SleepLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    date: date
    hours: float
    quality: Optional[int]
    bedtime: Optional[str]
    waketime: Optional[str]
    deep_sleep_hours: Optional[float]
    rem_sleep_hours: Optional[float]
    interruptions: Optional[int]
    notes: Optional[str]
    created_at: datetime

# Mood Schemas
class MoodLogCreate(BaseModel):
    date: date
    mood_score: int = Field(..., ge=1, le=10)
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

class MoodLogUpdate(BaseModel):
    mood_score: Optional[int] = Field(None, ge=1, le=10)
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

class MoodLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    date: date
    timestamp: datetime
    mood_score: int
    energy_level: Optional[int]
    stress_level: Optional[int]
    detected_from_face: bool
    face_confidence: Optional[float]
    detected_emotion: Optional[str]
    tags: Optional[List[str]]
    notes: Optional[str]
    created_at: datetime

# Exercise Schemas
class ExerciseLogCreate(BaseModel):
    date: date
    activity_type: str
    duration_minutes: int = Field(..., gt=0)
    calories: Optional[int] = None
    distance_km: Optional[float] = None
    repetitions: Optional[int] = None
    sets: Optional[int] = None
    weight_kg: Optional[float] = None
    intensity: Optional[str] = None
    heart_rate_avg: Optional[int] = None
    heart_rate_max: Optional[int] = None
    notes: Optional[str] = None

class ExerciseLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    date: date
    activity_type: str
    duration_minutes: int
    calories: Optional[int]
    distance_km: Optional[float]
    intensity: Optional[str]
    notes: Optional[str]
    created_at: datetime

# Nutrition Schemas
class NutritionLogCreate(BaseModel):
    date: date
    meal_type: str
    description: str
    calories: Optional[int] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    water_ml: Optional[int] = None
    notes: Optional[str] = None

class NutritionLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    date: date
    timestamp: datetime
    meal_type: str
    description: str
    calories: Optional[int]
    protein_g: Optional[float]
    carbs_g: Optional[float]
    fat_g: Optional[float]
    notes: Optional[str]
    created_at: datetime

# Weight Schemas
class WeightLogCreate(BaseModel):
    date: date
    weight_kg: float = Field(..., gt=0)
    body_fat_percent: Optional[float] = None
    muscle_mass_kg: Optional[float] = None
    bmi: Optional[float] = None
    waist_cm: Optional[float] = None
    chest_cm: Optional[float] = None
    notes: Optional[str] = None

class WeightLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    date: date
    weight_kg: float
    body_fat_percent: Optional[float]
    muscle_mass_kg: Optional[float]
    bmi: Optional[float]
    notes: Optional[str]
    created_at: datetime

# Finance Schemas
class FinanceLogCreate(BaseModel):
    date: date
    transaction_type: str  # income or expense
    amount: float = Field(..., gt=0)
    currency: str = "USD"
    category: str
    subcategory: Optional[str] = None
    payment_method: Optional[str] = None
    description: str
    merchant: Optional[str] = None
    is_recurring: bool = False
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

class FinanceLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    date: date
    transaction_type: str
    amount: float
    currency: str
    category: str
    subcategory: Optional[str]
    description: str
    merchant: Optional[str]
    is_recurring: bool
    tags: Optional[List[str]]
    created_at: datetime

# Water Schemas
class WaterLogCreate(BaseModel):
    date: date
    amount_ml: int = Field(..., gt=0)
    goal_ml: int = 2000
    notes: Optional[str] = None

class WaterLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    date: date
    amount_ml: int
    goal_ml: int
    notes: Optional[str]
    created_at: datetime

# Statistics Schemas
class DailySummary(BaseModel):
    date: date
    sleep_hours: Optional[float] = None
    avg_mood: Optional[float] = None
    exercise_minutes: Optional[int] = None
    calories_consumed: Optional[int] = None
    water_ml: Optional[int] = None
    expenses: Optional[float] = None
    income: Optional[float] = None

class WeeklyStats(BaseModel):
    start_date: date
    end_date: date
    avg_sleep: Optional[float] = None
    avg_mood: Optional[float] = None
    total_exercise_minutes: Optional[int] = None
    total_expenses: Optional[float] = None
    total_income: Optional[float] = None
    net_savings: Optional[float] = None
