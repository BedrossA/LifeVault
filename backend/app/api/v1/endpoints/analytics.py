"""Analytics API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta

from app.db.base import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.analytics import SleepLog, MoodLog, ExerciseLog, NutritionLog, WeightLog, FinanceLog, WaterLog
from app.schemas.analytics import (
    SleepLogCreate, SleepLogUpdate, SleepLogResponse,
    MoodLogCreate, MoodLogUpdate, MoodLogResponse,
    ExerciseLogCreate, ExerciseLogResponse,
    NutritionLogCreate, NutritionLogResponse,
    WeightLogCreate, WeightLogResponse,
    FinanceLogCreate, FinanceLogResponse,
    WaterLogCreate, WaterLogResponse,
    DailySummary
)
from app.services.analytics_service import AnalyticsService

router = APIRouter()

# ============================================
# SLEEP ENDPOINTS
# ============================================

@router.post("/sleep", response_model=SleepLogResponse)
def create_sleep_log(
    data: SleepLogCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new sleep log entry
    
    - **date**: Date of sleep
    - **hours**: Total sleep hours (0-24)
    - **quality**: Sleep quality rating (1-10)
    - **bedtime**: Time went to bed (e.g., "23:00")
    - **waketime**: Time woke up (e.g., "07:00")
    """
    # Check for duplicate
    if AnalyticsService.check_duplicate_entry(
        db, SleepLog, current_user.id, data.date
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Sleep log already exists for {data.date}"
        )
    
    # Create entry
    sleep_log = SleepLog(
        user_id=current_user.id,
        **data.model_dump()
    )
    
    db.add(sleep_log)
    db.commit()
    db.refresh(sleep_log)
    
    return sleep_log

@router.get("/sleep", response_model=List[SleepLogResponse])
def list_sleep_logs(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(30, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List sleep logs with optional date range filtering
    
    - **start_date**: Start date (defaults to 30 days ago)
    - **end_date**: End date (defaults to today)
    - **limit**: Max number of results (max 100)
    """
    start, end = AnalyticsService.get_date_range(start_date, end_date)
    
    logs = db.query(SleepLog).filter(
        SleepLog.user_id == current_user.id,
        SleepLog.date >= start,
        SleepLog.date <= end
    ).order_by(SleepLog.date.desc()).limit(limit).all()
    
    return logs

@router.get("/sleep/{log_id}", response_model=SleepLogResponse)
def get_sleep_log(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific sleep log by ID"""
    log = db.query(SleepLog).filter(
        SleepLog.id == log_id,
        SleepLog.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    
    return log

@router.put("/sleep/{log_id}", response_model=SleepLogResponse)
def update_sleep_log(
    log_id: int,
    data: SleepLogUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a sleep log"""
    log = db.query(SleepLog).filter(
        SleepLog.id == log_id,
        SleepLog.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(log, field, value)
    
    db.commit()
    db.refresh(log)
    
    return log

@router.delete("/sleep/{log_id}")
def delete_sleep_log(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a sleep log"""
    log = db.query(SleepLog).filter(
        SleepLog.id == log_id,
        SleepLog.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    
    db.delete(log)
    db.commit()
    
    return {"message": "Sleep log deleted successfully"}

@router.get("/sleep/stats/summary")
def get_sleep_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get sleep statistics
    
    - **days**: Number of days to analyze (1-365, default 30)
    """
    start_date = date.today() - timedelta(days=days)
    
    logs = db.query(SleepLog).filter(
        SleepLog.user_id == current_user.id,
        SleepLog.date >= start_date
    ).all()
    
    if not logs:
        return {
            "total_entries": 0,
            "avg_hours": None,
            "avg_quality": None,
            "total_sleep_hours": None,
            "best_quality_date": None,
            "worst_quality_date": None
        }
    
    hours_list = [log.hours for log in logs]
    quality_list = [log.quality for log in logs if log.quality]
    
    # Find best and worst quality days
    quality_logs = [log for log in logs if log.quality]
    best_log = max(quality_logs, key=lambda x: x.quality) if quality_logs else None
    worst_log = min(quality_logs, key=lambda x: x.quality) if quality_logs else None
    
    return {
        "total_entries": len(logs),
        "avg_hours": round(sum(hours_list) / len(hours_list), 2),
        "avg_quality": round(sum(quality_list) / len(quality_list), 2) if quality_list else None,
        "total_sleep_hours": round(sum(hours_list), 1),
        "best_quality_date": best_log.date if best_log else None,
        "worst_quality_date": worst_log.date if worst_log else None,
        "date_range": {
            "start": start_date,
            "end": date.today()
        }
    }

# ============================================
# DAILY SUMMARY
# ============================================

@router.get("/summary/daily", response_model=DailySummary)
def get_daily_summary(
    target_date: date = Query(default_factory=date.today),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get daily summary of all analytics
    
    - **target_date**: Date to summarize (defaults to today)
    """
    summary = AnalyticsService.get_daily_summary(
        db, 
        current_user.id, 
        target_date
    )
    
    return summary

# ============================================
# MOOD ENDPOINTS (with Face Detection Support)
# ============================================

@router.post("/mood", response_model=MoodLogResponse)
def create_mood_log(
    data: MoodLogCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new mood log entry
    
    - **mood_score**: Overall mood (1-10)
    - **energy_level**: Energy level (1-10)
    - **stress_level**: Stress level (1-10)
    - **tags**: Optional tags (e.g., ["productive", "happy"])
    
    Note: For face-detected mood, use /mood/detect-from-face endpoint
    """
    mood_log = MoodLog(
        user_id=current_user.id,
        detected_from_face=False,
        **data.model_dump()
    )
    
    db.add(mood_log)
    db.commit()
    db.refresh(mood_log)
    
    return mood_log

@router.get("/mood", response_model=List[MoodLogResponse])
def list_mood_logs(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(50, le=200),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List mood logs with date range filtering"""
    start, end = AnalyticsService.get_date_range(start_date, end_date)
    
    logs = db.query(MoodLog).filter(
        MoodLog.user_id == current_user.id,
        MoodLog.date >= start,
        MoodLog.date <= end
    ).order_by(MoodLog.timestamp.desc()).limit(limit).all()
    
    return logs

@router.get("/mood/{log_id}", response_model=MoodLogResponse)
def get_mood_log(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific mood log"""
    log = db.query(MoodLog).filter(
        MoodLog.id == log_id,
        MoodLog.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Mood log not found")
    
    return log

@router.put("/mood/{log_id}", response_model=MoodLogResponse)
def update_mood_log(
    log_id: int,
    data: MoodLogUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update mood log"""
    log = db.query(MoodLog).filter(
        MoodLog.id == log_id,
        MoodLog.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Mood log not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(log, field, value)
    
    db.commit()
    db.refresh(log)
    
    return log

@router.delete("/mood/{log_id}")
def delete_mood_log(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete mood log"""
    log = db.query(MoodLog).filter(
        MoodLog.id == log_id,
        MoodLog.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Mood log not found")
    
    db.delete(log)
    db.commit()
    
    return {"message": "Mood log deleted successfully"}

# ============================================
# EXERCISE ENDPOINTS
# ============================================

from app.schemas.analytics import ExerciseLogCreate, ExerciseLogResponse
from app.models.analytics import ExerciseLog

@router.post("/exercise", response_model=ExerciseLogResponse)
def create_exercise_log(
    data: ExerciseLogCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create exercise log"""
    exercise_log = ExerciseLog(
        user_id=current_user.id,
        **data.model_dump()
    )
    
    db.add(exercise_log)
    db.commit()
    db.refresh(exercise_log)
    
    return exercise_log

@router.get("/exercise", response_model=List[ExerciseLogResponse])
def list_exercise_logs(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    activity_type: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List exercise logs with filtering"""
    start, end = AnalyticsService.get_date_range(start_date, end_date)
    
    query = db.query(ExerciseLog).filter(
        ExerciseLog.user_id == current_user.id,
        ExerciseLog.date >= start,
        ExerciseLog.date <= end
    )
    
    if activity_type:
        query = query.filter(ExerciseLog.activity_type == activity_type)
    
    logs = query.order_by(ExerciseLog.date.desc()).limit(limit).all()
    
    return logs

@router.get("/exercise/{log_id}", response_model=ExerciseLogResponse)
def get_exercise_log(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific exercise log"""
    log = db.query(ExerciseLog).filter(
        ExerciseLog.id == log_id,
        ExerciseLog.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Exercise log not found")
    
    return log

@router.delete("/exercise/{log_id}")
def delete_exercise_log(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete exercise log"""
    log = db.query(ExerciseLog).filter(
        ExerciseLog.id == log_id,
        ExerciseLog.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Exercise log not found")
    
    db.delete(log)
    db.commit()
    
    return {"message": "Exercise log deleted"}

# ============================================
# NUTRITION ENDPOINTS
# ============================================

from app.schemas.analytics import NutritionLogCreate, NutritionLogResponse
from app.models.analytics import NutritionLog

@router.post("/nutrition", response_model=NutritionLogResponse)
def create_nutrition_log(
    data: NutritionLogCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create nutrition log"""
    nutrition_log = NutritionLog(
        user_id=current_user.id,
        **data.model_dump()
    )
    
    db.add(nutrition_log)
    db.commit()
    db.refresh(nutrition_log)
    
    return nutrition_log

@router.get("/nutrition", response_model=List[NutritionLogResponse])
def list_nutrition_logs(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    meal_type: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List nutrition logs"""
    start, end = AnalyticsService.get_date_range(start_date, end_date)
    
    query = db.query(NutritionLog).filter(
        NutritionLog.user_id == current_user.id,
        NutritionLog.date >= start,
        NutritionLog.date <= end
    )
    
    if meal_type:
        query = query.filter(NutritionLog.meal_type == meal_type)
    
    logs = query.order_by(NutritionLog.timestamp.desc()).limit(limit).all()
    
    return logs

@router.delete("/nutrition/{log_id}")
def delete_nutrition_log(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete nutrition log"""
    log = db.query(NutritionLog).filter(
        NutritionLog.id == log_id,
        NutritionLog.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Nutrition log not found")
    
    db.delete(log)
    db.commit()
    
    return {"message": "Nutrition log deleted"}

# ============================================
# WEIGHT ENDPOINTS
# ============================================

from app.schemas.analytics import WeightLogCreate, WeightLogResponse
from app.models.analytics import WeightLog

@router.post("/weight", response_model=WeightLogResponse)
def create_weight_log(
    data: WeightLogCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create weight log"""
    # Check duplicate
    if AnalyticsService.check_duplicate_entry(
        db, WeightLog, current_user.id, data.date
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Weight log already exists for {data.date}"
        )
    
    weight_log = WeightLog(
        user_id=current_user.id,
        **data.model_dump()
    )
    
    db.add(weight_log)
    db.commit()
    db.refresh(weight_log)
    
    return weight_log

@router.get("/weight", response_model=List[WeightLogResponse])
def list_weight_logs(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(50, le=200),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List weight logs"""
    start, end = AnalyticsService.get_date_range(start_date, end_date)
    
    logs = db.query(WeightLog).filter(
        WeightLog.user_id == current_user.id,
        WeightLog.date >= start,
        WeightLog.date <= end
    ).order_by(WeightLog.date.desc()).limit(limit).all()
    
    return logs

@router.delete("/weight/{log_id}")
def delete_weight_log(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete weight log"""
    log = db.query(WeightLog).filter(
        WeightLog.id == log_id,
        WeightLog.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Weight log not found")
    
    db.delete(log)
    db.commit()
    
    return {"message": "Weight log deleted"}

# ============================================
# FINANCE ENDPOINTS
# ============================================

from app.schemas.analytics import FinanceLogCreate, FinanceLogResponse
from app.models.analytics import FinanceLog

@router.post("/finance", response_model=FinanceLogResponse)
def create_finance_log(
    data: FinanceLogCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create finance log
    
    - **transaction_type**: "income" or "expense"
    - **amount**: Amount in specified currency
    - **category**: Category (e.g., "food", "salary", "transport")
    """
    finance_log = FinanceLog(
        user_id=current_user.id,
        **data.model_dump()
    )
    
    db.add(finance_log)
    db.commit()
    db.refresh(finance_log)
    
    return finance_log

@router.get("/finance", response_model=List[FinanceLogResponse])
def list_finance_logs(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    transaction_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List finance logs with filtering"""
    start, end = AnalyticsService.get_date_range(start_date, end_date, days_back=90)
    
    query = db.query(FinanceLog).filter(
        FinanceLog.user_id == current_user.id,
        FinanceLog.date >= start,
        FinanceLog.date <= end
    )
    
    if transaction_type:
        query = query.filter(FinanceLog.transaction_type == transaction_type)
    
    if category:
        query = query.filter(FinanceLog.category == category)
    
    logs = query.order_by(FinanceLog.date.desc()).limit(limit).all()
    
    return logs

@router.delete("/finance/{log_id}")
def delete_finance_log(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete finance log"""
    log = db.query(FinanceLog).filter(
        FinanceLog.id == log_id,
        FinanceLog.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Finance log not found")
    
    db.delete(log)
    db.commit()
    
    return {"message": "Finance log deleted"}

@router.get("/finance/stats/summary")
def get_finance_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get finance statistics"""
    start_date = date.today() - timedelta(days=days)
    
    logs = db.query(FinanceLog).filter(
        FinanceLog.user_id == current_user.id,
        FinanceLog.date >= start_date
    ).all()
    
    income_logs = [l for l in logs if l.transaction_type == "income"]
    expense_logs = [l for l in logs if l.transaction_type == "expense"]
    
    total_income = sum(l.amount for l in income_logs)
    total_expenses = sum(l.amount for l in expense_logs)
    
    # Category breakdown
    expense_by_category = {}
    for log in expense_logs:
        if log.category not in expense_by_category:
            expense_by_category[log.category] = 0
        expense_by_category[log.category] += log.amount
    
    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_savings": round(total_income - total_expenses, 2),
        "avg_daily_expense": round(total_expenses / days, 2) if days > 0 else 0,
        "expense_by_category": expense_by_category,
        "transaction_count": {
            "income": len(income_logs),
            "expense": len(expense_logs),
            "total": len(logs)
        },
        "date_range": {
            "start": start_date,
            "end": date.today(),
            "days": days
        }
    }

# ============================================
# WATER ENDPOINTS
# ============================================

from app.schemas.analytics import WaterLogCreate, WaterLogResponse
from app.models.analytics import WaterLog

@router.post("/water", response_model=WaterLogResponse)
def create_water_log(
    data: WaterLogCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create water intake log"""
    # Check if entry exists, if so, add to it
    existing = db.query(WaterLog).filter(
        WaterLog.user_id == current_user.id,
        WaterLog.date == data.date
    ).first()
    
    if existing:
        existing.amount_ml += data.amount_ml
        db.commit()
        db.refresh(existing)
        return existing
    
    water_log = WaterLog(
        user_id=current_user.id,
        **data.model_dump()
    )
    
    db.add(water_log)
    db.commit()
    db.refresh(water_log)
    
    return water_log

@router.get("/water", response_model=List[WaterLogResponse])
def list_water_logs(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(30, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List water logs"""
    start, end = AnalyticsService.get_date_range(start_date, end_date)
    
    logs = db.query(WaterLog).filter(
        WaterLog.user_id == current_user.id,
        WaterLog.date >= start,
        WaterLog.date <= end
    ).order_by(WaterLog.date.desc()).limit(limit).all()
    
    return logs

@router.delete("/water/{log_id}")
def delete_water_log(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete water log"""
    log = db.query(WaterLog).filter(
        WaterLog.id == log_id,
        WaterLog.user_id == current_user.id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Water log not found")
    
    db.delete(log)
    db.commit()
    
    return {"message": "Water log deleted"}
