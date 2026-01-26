"""Improved Analytics endpoints with better error handling"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC, timedelta
from pydantic import BaseModel, Field
import logging
import json
import csv
from io import StringIO

from app.db.base import get_db
from app.db.mongodb import get_mongo_db
from app.core.deps import get_current_active_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

# Schemas
class AnalyticsEntryBase(BaseModel):
    category: str = Field(..., min_length=1, max_length=50)
    metric: str = Field(..., min_length=1, max_length=50)
    value: float
    unit: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = Field(None, max_length=500)
    metadata: Optional[dict] = None

class AnalyticsEntryCreate(AnalyticsEntryBase):
    pass

class AnalyticsEntry(AnalyticsEntryBase):
    id: str
    user_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class AnalyticsStats(BaseModel):
    total_entries: int
    categories: Dict[str, int]
    date_range: Dict[str, str]
    trends: List[Dict[str, Any]]

class GoalBase(BaseModel):
    metric: str = Field(..., min_length=1, max_length=50)
    category: str = Field(..., min_length=1, max_length=50)
    target_value: float
    unit: Optional[str] = Field(None, max_length=20)
    deadline: Optional[datetime] = None

class GoalCreate(GoalBase):
    pass

class Goal(GoalBase):
    id: str
    user_id: int
    current_value: float = 0.0
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True

class TimeSeriesPoint(BaseModel):
    date: str
    value: float

class TimeSeriesData(BaseModel):
    metric: str
    data: List[TimeSeriesPoint]

# Helper function for date parsing
def parse_date_string(date_str: str) -> datetime:
    """Parse date string with error handling"""
    try:
        if 'T' not in date_str:
            date_str = f"{date_str}T00:00:00"
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError as e:
        logger.error(f"Date parsing error: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format: {date_str}. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
        )

# Analytics Entries
@router.post("/entries", response_model=AnalyticsEntry, status_code=status.HTTP_201_CREATED)
async def create_entry(
    entry_data: AnalyticsEntryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """
    Create a new analytics entry
    
    - **category**: Category of the entry (e.g., 'health', 'fitness', 'productivity')
    - **metric**: Specific metric being tracked (e.g., 'steps', 'calories', 'hours')
    - **value**: Numeric value of the metric
    - **unit**: Optional unit of measurement (e.g., 'steps', 'kcal', 'hours')
    - **notes**: Optional notes about this entry
    - **metadata**: Optional additional metadata as JSON
    """
    try:
        entry_dict = {
            **entry_data.model_dump(),
            "user_id": current_user.id,
            "timestamp": datetime.now(UTC),
        }
        
        # Validate value is finite
        if not isinstance(entry_dict['value'], (int, float)) or not float('-inf') < entry_dict['value'] < float('inf'):
            raise HTTPException(
                status_code=400,
                detail="Value must be a finite number"
            )
        
        # Store in MongoDB
        result = await mongo_db.analytics_entries.insert_one(entry_dict)
        
        logger.info(f"Created analytics entry: {entry_data.category}/{entry_data.metric} for user {current_user.id}")
        
        return {
            **entry_dict,
            "id": str(result.inserted_id),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating analytics entry: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to create analytics entry"
        )

@router.get("/entries", response_model=List[AnalyticsEntry])
async def get_entries(
    category: Optional[str] = Query(None, max_length=50),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """
    Get analytics entries with optional filters
    
    - **category**: Filter by category
    - **start_date**: Start date (ISO format)
    - **end_date**: End date (ISO format)
    - **limit**: Maximum number of entries to return (default: 1000, max: 10000)
    """
    try:
        query = {"user_id": current_user.id}
        
        if category:
            query["category"] = category
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = parse_date_string(start_date)
            if end_date:
                end_dt = parse_date_string(end_date)
                # If no time specified, include the entire end date
                if 'T00:00:00' in end_date or 'T' not in end_date:
                    from datetime import timedelta
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                query["timestamp"]["$lte"] = end_dt
        
        cursor = mongo_db.analytics_entries.find(query).sort("timestamp", -1).limit(limit)
        entries = await cursor.to_list(length=limit)
        
        return [{"id": str(e.pop("_id")), **e} for e in entries]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analytics entries: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve analytics entries"
        )

@router.get("/entries/{entry_id}", response_model=AnalyticsEntry)
async def get_entry(
    entry_id: str,
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Get a specific analytics entry by ID"""
    try:
        from bson import ObjectId
        from bson.errors import InvalidId
        
        try:
            object_id = ObjectId(entry_id)
        except InvalidId:
            raise HTTPException(
                status_code=400,
                detail="Invalid entry ID format"
            )
        
        entry = await mongo_db.analytics_entries.find_one({
            "_id": object_id,
            "user_id": current_user.id
        })
        
        if not entry:
            raise HTTPException(
                status_code=404,
                detail="Entry not found"
            )
        
        return {"id": str(entry.pop("_id")), **entry}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analytics entry: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve analytics entry"
        )

@router.put("/entries/{entry_id}", response_model=AnalyticsEntry)
async def update_entry(
    entry_id: str,
    entry_data: AnalyticsEntryCreate,
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Update an analytics entry"""
    try:
        from bson import ObjectId
        from bson.errors import InvalidId
        
        try:
            object_id = ObjectId(entry_id)
        except InvalidId:
            raise HTTPException(
                status_code=400,
                detail="Invalid entry ID format"
            )
        
        # Validate value
        if not isinstance(entry_data.value, (int, float)) or not float('-inf') < entry_data.value < float('inf'):
            raise HTTPException(
                status_code=400,
                detail="Value must be a finite number"
            )
        
        result = await mongo_db.analytics_entries.update_one(
            {"_id": object_id, "user_id": current_user.id},
            {"$set": entry_data.model_dump()}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Entry not found"
            )
        
        entry = await mongo_db.analytics_entries.find_one({"_id": object_id})
        
        logger.info(f"Updated analytics entry {entry_id} for user {current_user.id}")
        
        return {"id": str(entry.pop("_id")), **entry}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating analytics entry: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to update analytics entry"
        )

@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(
    entry_id: str,
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Delete an analytics entry"""
    try:
        from bson import ObjectId
        from bson.errors import InvalidId
        
        try:
            object_id = ObjectId(entry_id)
        except InvalidId:
            raise HTTPException(
                status_code=400,
                detail="Invalid entry ID format"
            )
        
        result = await mongo_db.analytics_entries.delete_one({
            "_id": object_id,
            "user_id": current_user.id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Entry not found"
            )
        
        logger.info(f"Deleted analytics entry {entry_id} for user {current_user.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting analytics entry: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to delete analytics entry"
        )

# Statistics
@router.get("/stats", response_model=AnalyticsStats)
async def get_stats(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """
    Get analytics statistics
    
    - **start_date**: Start date (ISO format)
    - **end_date**: End date (ISO format)
    """
    try:
        query = {"user_id": current_user.id}
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = parse_date_string(start_date)
            if end_date:
                end_dt = parse_date_string(end_date)
                if 'T00:00:00' in end_date or 'T' not in end_date:
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                query["timestamp"]["$lte"] = end_dt
        
        cursor = mongo_db.analytics_entries.find(query)
        entries = await cursor.to_list(length=None)
        
        # Calculate statistics
        total_entries = len(entries)
        categories = {}
        for entry in entries:
            cat = entry.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        # Determine date range
        if entries:
            timestamps = [e.get("timestamp") for e in entries if e.get("timestamp")]
            if timestamps:
                min_date = min(timestamps)
                max_date = max(timestamps)
                date_range = {
                    "start": min_date.isoformat() if isinstance(min_date, datetime) else str(min_date),
                    "end": max_date.isoformat() if isinstance(max_date, datetime) else str(max_date)
                }
            else:
                date_range = {"start": "", "end": ""}
        else:
            date_range = {"start": "", "end": ""}
        
        # Calculate trends (simplified - average values per category)
        trends = []
        category_values = {}
        for entry in entries:
            cat = entry.get("category", "unknown")
            if cat not in category_values:
                category_values[cat] = []
            category_values[cat].append(entry.get("value", 0))
        
        for cat, values in category_values.items():
            if values:
                avg_value = sum(values) / len(values)
                trends.append({
                    "category": cat,
                    "average_value": avg_value,
                    "entry_count": len(values)
                })
        
        return {
            "total_entries": total_entries,
            "categories": categories,
            "date_range": date_range,
            "trends": trends
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analytics statistics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve analytics statistics"
        )

# Time Series
@router.get("/time-series", response_model=TimeSeriesData)
async def get_time_series(
    metric: str = Query(..., min_length=1),
    category: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """
    Get time series data for a specific metric
    
    - **metric**: Metric name (required)
    - **category**: Filter by category (optional)
    - **start_date**: Start date (ISO format)
    - **end_date**: End date (ISO format)
    """
    try:
        query = {
            "user_id": current_user.id,
            "metric": metric
        }
        
        if category:
            query["category"] = category
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = parse_date_string(start_date)
            if end_date:
                end_dt = parse_date_string(end_date)
                if 'T00:00:00' in end_date or 'T' not in end_date:
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                query["timestamp"]["$lte"] = end_dt
        
        cursor = mongo_db.analytics_entries.find(query).sort("timestamp", 1)
        entries = await cursor.to_list(length=None)
        
        # Group by date and calculate daily averages
        daily_data = {}
        for entry in entries:
            ts = entry.get("timestamp")
            if ts:
                if isinstance(ts, datetime):
                    date_key = ts.date().isoformat()
                else:
                    date_key = str(ts).split('T')[0]
                
                if date_key not in daily_data:
                    daily_data[date_key] = []
                daily_data[date_key].append(entry.get("value", 0))
        
        # Calculate averages and create time series points
        time_series_points = []
        for date_key in sorted(daily_data.keys()):
            values = daily_data[date_key]
            avg_value = sum(values) / len(values) if values else 0
            time_series_points.append({
                "date": date_key,
                "value": avg_value
            })
        
        return {
            "metric": metric,
            "data": time_series_points
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving time series data: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve time series data"
        )

# Goals
@router.post("/goals", response_model=Goal, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """
    Create a new goal
    
    - **metric**: Metric name (e.g., 'steps', 'calories')
    - **category**: Category (e.g., 'health', 'fitness')
    - **target_value**: Target value to achieve
    - **unit**: Unit of measurement (optional)
    - **deadline**: Optional deadline date
    """
    try:
        goal_dict = {
            **goal_data.model_dump(),
            "user_id": current_user.id,
            "current_value": 0.0,
            "is_active": True,
            "created_at": datetime.now(UTC)
        }
        
        # Store in MongoDB
        result = await mongo_db.goals.insert_one(goal_dict)
        
        logger.info(f"Created goal: {goal_data.metric} for user {current_user.id}")
        
        return {
            **goal_dict,
            "id": str(result.inserted_id),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating goal: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to create goal"
        )

@router.get("/goals", response_model=List[Goal])
async def get_goals(
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Get all goals for the current user with calculated current_value"""
    try:
        query = {"user_id": current_user.id}
        cursor = mongo_db.goals.find(query).sort("created_at", -1)
        goals = await cursor.to_list(length=None)
        
        # Calculate current_value for each goal from entries
        result_goals = []
        for goal in goals:
            goal_id = str(goal.pop("_id"))
            goal_metric = goal.get("metric")
            goal_category = goal.get("category")
            
            # Query entries matching this goal's metric and category
            entries_query = {
                "user_id": current_user.id,
                "metric": goal_metric,
                "category": goal_category
            }
            
            # If goal has a deadline, only count entries before deadline
            deadline = goal.get("deadline")
            if deadline:
                if isinstance(deadline, str):
                    try:
                        deadline = parse_date_string(deadline)
                    except:
                        deadline = None  # Skip deadline filter if parsing fails
                if deadline and isinstance(deadline, datetime):
                    entries_query["timestamp"] = {"$lte": deadline}
            
            entries_cursor = mongo_db.analytics_entries.find(entries_query)
            entries = await entries_cursor.to_list(length=None)
            
            # Calculate current_value (sum of all matching entries)
            current_value = sum(float(e.get("value", 0)) for e in entries)
            
            result_goals.append({
                "id": goal_id,
                **goal,
                "current_value": current_value
            })
        
        return result_goals
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving goals: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve goals"
        )

@router.put("/goals/{goal_id}", response_model=Goal)
async def update_goal(
    goal_id: str,
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Update a goal"""
    try:
        from bson import ObjectId
        from bson.errors import InvalidId
        
        try:
            object_id = ObjectId(goal_id)
        except InvalidId:
            raise HTTPException(
                status_code=400,
                detail="Invalid goal ID format"
            )
        
        result = await mongo_db.goals.update_one(
            {"_id": object_id, "user_id": current_user.id},
            {"$set": goal_data.model_dump()}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Goal not found"
            )
        
        goal = await mongo_db.goals.find_one({"_id": object_id})
        
        logger.info(f"Updated goal {goal_id} for user {current_user.id}")
        
        return {"id": str(goal.pop("_id")), **goal}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating goal: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to update goal"
        )

@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: str,
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """Delete a goal"""
    try:
        from bson import ObjectId
        from bson.errors import InvalidId
        
        try:
            object_id = ObjectId(goal_id)
        except InvalidId:
            raise HTTPException(
                status_code=400,
                detail="Invalid goal ID format"
            )
        
        result = await mongo_db.goals.delete_one({
            "_id": object_id,
            "user_id": current_user.id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Goal not found"
            )
        
        logger.info(f"Deleted goal {goal_id} for user {current_user.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting goal: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to delete goal"
        )

# Export
@router.get("/export")
async def export_data(
    format: str = Query("json", regex="^(json|csv)$"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    mongo_db = Depends(get_mongo_db)
):
    """
    Export analytics data
    
    - **format**: Export format ('json' or 'csv')
    - **start_date**: Start date (ISO format)
    - **end_date**: End date (ISO format)
    """
    try:
        query = {"user_id": current_user.id}
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = parse_date_string(start_date)
            if end_date:
                end_dt = parse_date_string(end_date)
                if 'T00:00:00' in end_date or 'T' not in end_date:
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                query["timestamp"]["$lte"] = end_dt
        
        cursor = mongo_db.analytics_entries.find(query).sort("timestamp", -1)
        entries = await cursor.to_list(length=None)
        
        # Convert entries to list of dicts
        export_data = []
        for entry in entries:
            entry_dict = dict(entry)  # Create a copy
            entry_dict["id"] = str(entry_dict.pop("_id"))
            # Convert datetime to string
            if "timestamp" in entry_dict and isinstance(entry_dict["timestamp"], datetime):
                entry_dict["timestamp"] = entry_dict["timestamp"].isoformat()
            export_data.append(entry_dict)
        
        if format == "json":
            return Response(
                content=json.dumps(export_data, indent=2, default=str),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=analytics_export_{datetime.now(UTC).date()}.json"}
            )
        else:  # CSV
            if not export_data:
                return Response(
                    content="No data to export",
                    media_type="text/csv"
                )
            
            output = StringIO()
            fieldnames = ["id", "user_id", "category", "metric", "value", "unit", "notes", "timestamp"]
            writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for entry in export_data:
                row = {k: str(v) if v is not None else "" for k, v in entry.items() if k in fieldnames}
                writer.writerow(row)
            
            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=analytics_export_{datetime.now(UTC).date()}.csv"}
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting data: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to export data"
        )