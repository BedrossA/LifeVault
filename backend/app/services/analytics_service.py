"""Analytics service for data validation and processing"""
from typing import Optional, List, Dict
from datetime import date, datetime, timedelta, UTC
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.analytics import (
    SleepLog, MoodLog, ExerciseLog, NutritionLog,
    WeightLog, FinanceLog, WaterLog
)
from app.models.user import User

class AnalyticsService:
    """Service for analytics operations"""
    
    @staticmethod
    def calculate_bmi(weight_kg: float, height_cm: float) -> float:
        """Calculate BMI from weight and height"""
        height_m = height_cm / 100
        return round(weight_kg / (height_m ** 2), 2)
    
    @staticmethod
    def get_date_range(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        days_back: int = 30
    ) -> tuple[date, date]:
        """Get date range with defaults"""
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=days_back)
        return start_date, end_date
    
    @staticmethod
    def check_duplicate_entry(
        db: Session,
        model,
        user_id: int,
        entry_date: date,
        exclude_id: Optional[int] = None
    ) -> bool:
        """Check if entry already exists for date"""
        query = db.query(model).filter(
            and_(
                model.user_id == user_id,
                model.date == entry_date
            )
        )
        
        if exclude_id:
            query = query.filter(model.id != exclude_id)
        
        return query.first() is not None
    
    @staticmethod
    def get_daily_summary(
        db: Session,
        user_id: int,
        target_date: date
    ) -> Dict:
        """Get summary of all analytics for a specific day"""
        
        # Sleep
        sleep = db.query(SleepLog).filter(
            and_(
                SleepLog.user_id == user_id,
                SleepLog.date == target_date
            )
        ).first()
        
        # Mood (average if multiple entries)
        mood_avg = db.query(func.avg(MoodLog.mood_score)).filter(
            and_(
                MoodLog.user_id == user_id,
                MoodLog.date == target_date
            )
        ).scalar()
        
        # Exercise (total minutes)
        exercise_total = db.query(func.sum(ExerciseLog.duration_minutes)).filter(
            and_(
                ExerciseLog.user_id == user_id,
                ExerciseLog.date == target_date
            )
        ).scalar()
        
        # Nutrition (total calories)
        calories_total = db.query(func.sum(NutritionLog.calories)).filter(
            and_(
                NutritionLog.user_id == user_id,
                NutritionLog.date == target_date
            )
        ).scalar()
        
        # Water (total)
        water_total = db.query(func.sum(WaterLog.amount_ml)).filter(
            and_(
                WaterLog.user_id == user_id,
                WaterLog.date == target_date
            )
        ).scalar()
        
        # Finance
        income_total = db.query(func.sum(FinanceLog.amount)).filter(
            and_(
                FinanceLog.user_id == user_id,
                FinanceLog.date == target_date,
                FinanceLog.transaction_type == "income"
            )
        ).scalar()
        
        expenses_total = db.query(func.sum(FinanceLog.amount)).filter(
            and_(
                FinanceLog.user_id == user_id,
                FinanceLog.date == target_date,
                FinanceLog.transaction_type == "expense"
            )
        ).scalar()
        
        return {
            "date": target_date,
            "sleep_hours": sleep.hours if sleep else None,
            "avg_mood": float(mood_avg) if mood_avg else None,
            "exercise_minutes": int(exercise_total) if exercise_total else None,
            "calories_consumed": int(calories_total) if calories_total else None,
            "water_ml": int(water_total) if water_total else None,
            "income": float(income_total) if income_total else None,
            "expenses": float(expenses_total) if expenses_total else None,
        }
