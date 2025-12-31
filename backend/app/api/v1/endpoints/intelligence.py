"""Intelligence and analytics endpoints"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.base import get_db
from app.db.mongodb import get_mongo_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.services.analytics_intelligence_service import (
    CorrelationDetectionService,
    AnomalyDetectionService,
    PatternRecognitionService,
    PredictiveAnalyticsService,
    RecommendationService
)
from app.services.emotion_detection_service import EmotionDetectionService
from app.services.activity_logging_service import ActivityLoggingService
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Schemas
class CorrelationResponse(BaseModel):
    metric1: str
    metric2: str
    correlation: float
    p_value: float
    strength: str
    significance: bool

class AnomalyResponse(BaseModel):
    index: int
    value: float
    z_score: Optional[float] = None
    severity: str
    timestamp: Optional[str] = None

class ForecastResponse(BaseModel):
    forecast: List[float]
    confidence_upper: List[float]
    confidence_lower: List[float]
    method: str

class RecommendationResponse(BaseModel):
    type: str
    priority: str
    title: str
    message: str
    action: str
    metric: Optional[str] = None

# Correlation Detection
@router.get("/correlations", response_model=List[CorrelationResponse])
async def get_correlations(
    metrics: str = Query(..., description="Comma-separated list of metrics"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Get correlations between metrics"""
    try:
        metric_list = [m.strip() for m in metrics.split(',')]
        
        query = {"user_id": current_user.id}
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            if end_date:
                query["timestamp"]["$lte"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        entries = await mongo_db.analytics_entries.find(query).to_list(length=10000)
        
        correlations = CorrelationDetectionService.find_correlations(entries, metric_list)
        
        return correlations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Anomaly Detection
@router.get("/anomalies/{metric}", response_model=List[AnomalyResponse])
async def get_anomalies(
    metric: str,
    method: str = Query("zscore", regex="^(zscore|iqr)$"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Detect anomalies in a metric"""
    try:
        query = {"user_id": current_user.id}
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            if end_date:
                query["timestamp"]["$lte"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        entries = await mongo_db.analytics_entries.find(query).to_list(length=10000)
        
        anomalies = AnomalyDetectionService.detect_anomalies_in_entries(entries, metric, method)
        
        return anomalies
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Pattern Recognition
@router.get("/patterns/{metric}")
async def get_patterns(
    metric: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Detect patterns in a metric"""
    try:
        query = {"user_id": current_user.id, "metric": metric}
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            if end_date:
                query["timestamp"]["$lte"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        entries = await mongo_db.analytics_entries.find(query).to_list(length=10000)
        
        # Extract values and timestamps
        values = []
        timestamps = []
        for entry in entries:
            try:
                values.append(float(entry.get('value', 0)))
                ts = entry.get('timestamp')
                if isinstance(ts, str):
                    timestamps.append(datetime.fromisoformat(ts.replace('Z', '+00:00')))
                elif ts:
                    timestamps.append(ts)
            except (ValueError, TypeError):
                continue
        
        # Detect patterns
        seasonality = PatternRecognitionService.detect_seasonality(values, timestamps)
        trend = PatternRecognitionService.detect_trend(values, timestamps)
        
        return {
            'seasonality': seasonality,
            'trend': trend
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Predictive Analytics
@router.get("/forecast/{metric}", response_model=ForecastResponse)
async def get_forecast(
    metric: str,
    periods: int = Query(7, ge=1, le=30),
    method: str = Query("linear", regex="^(linear|moving_average)$"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Get forecast for a metric"""
    try:
        query = {"user_id": current_user.id, "metric": metric}
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            if end_date:
                query["timestamp"]["$lte"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        entries = await mongo_db.analytics_entries.find(query).to_list(length=1000)
        
        # Extract values
        values = []
        for entry in entries:
            try:
                values.append(float(entry.get('value', 0)))
            except (ValueError, TypeError):
                continue
        
        # Get forecast
        forecast_result = PredictiveAnalyticsService.forecast_with_confidence(
            values, periods, method
        )
        
        return forecast_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Recommendations
@router.get("/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """Get smart recommendations"""
    try:
        # Get recent entries
        entries = await mongo_db.analytics_entries.find(
            {"user_id": current_user.id}
        ).to_list(length=1000)
        
        # Get goals (from analytics endpoint)
        from app.api.v1.endpoints.analytics import router as analytics_router
        # This would need to be refactored to use a service
        goals = []  # Placeholder - would fetch from goals endpoint
        
        # Get trends
        trends = []  # Placeholder - would calculate trends
        
        recommendations = RecommendationService.generate_recommendations(
            entries, goals, trends
        )
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Activity Logging
@router.get("/activities")
async def get_activities(
    limit: int = Query(50, ge=1, le=500),
    activity_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user activity logs"""
    activities = ActivityLoggingService.get_user_activities(
        db, current_user.id, limit, activity_type
    )
    
    return [
        {
            'id': a.id,
            'action': a.action,
            'details': a.details,
            'ip_address': a.ip_address,
            'timestamp': a.timestamp.isoformat()
        }
        for a in activities
    ]

@router.get("/activities/stats")
async def get_activity_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get activity statistics"""
    stats = ActivityLoggingService.get_activity_stats(db, current_user.id, days)
    return stats

