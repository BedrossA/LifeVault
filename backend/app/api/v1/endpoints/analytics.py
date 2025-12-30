"""Analytics endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, UTC
from pydantic import BaseModel

from app.db.base import get_db
from app.db.mongodb import get_mongo_db
from app.core.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

# Schemas
class AnalyticsEntryBase(BaseModel):
    category: str
    metric: str
    value: float
    unit: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None

class AnalyticsEntryCreate(AnalyticsEntryBase):
    pass

class AnalyticsEntry(AnalyticsEntryBase):
    id: str
    user_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class GoalBase(BaseModel):
    metric: str
    category: str
    target_value: float
    unit: Optional[str] = None
    deadline: Optional[datetime] = None

class GoalCreate(GoalBase):
    pass

class Goal(GoalBase):
    id: str
    user_id: int
    current_value: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class AnalyticsStats(BaseModel):
    total_entries: int
    categories: dict
    date_range: dict
    trends: List[dict]

# Analytics Entries
@router.post("/entries", response_model=AnalyticsEntry, status_code=status.HTTP_201_CREATED)
async def create_entry(
    entry_data: AnalyticsEntryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new analytics entry"""
    entry_dict = {
        **entry_data.model_dump(),
        "user_id": current_user.id,
        "timestamp": datetime.now(UTC),
    }
    
    # Store in MongoDB
    mongo_db = await get_mongo_db()
    result = await mongo_db.analytics_entries.insert_one(entry_dict)
    
    return {
        **entry_dict,
        "id": str(result.inserted_id),
    }

@router.get("/entries", response_model=List[AnalyticsEntry])
async def get_entries(
    category: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
):
    """Get analytics entries with optional filters"""
    query = {"user_id": current_user.id}
    
    if category:
        query["category"] = category
    
    if start_date or end_date:
        query["timestamp"] = {}
        if start_date:
            # Handle date string without time
            try:
                if 'T' not in start_date:
                    start_date = f"{start_date}T00:00:00"
                query["timestamp"]["$gte"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except:
                query["timestamp"]["$gte"] = datetime.fromisoformat(f"{start_date}T00:00:00+00:00")
        if end_date:
            try:
                if 'T' not in end_date:
                    end_date = f"{end_date}T23:59:59"
                query["timestamp"]["$lte"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except:
                query["timestamp"]["$lte"] = datetime.fromisoformat(f"{end_date}T23:59:59+00:00")
    
    mongo_db = await get_mongo_db()
    cursor = mongo_db.analytics_entries.find(query).sort("timestamp", -1)
    entries = await cursor.to_list(length=1000)
    
    return [{"id": str(e.pop("_id")), **e} for e in entries]

@router.get("/entries/{entry_id}", response_model=AnalyticsEntry)
async def get_entry(
    entry_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific analytics entry"""
    from bson import ObjectId
    
    mongo_db = await get_mongo_db()
    entry = await mongo_db.analytics_entries.find_one({
        "_id": ObjectId(entry_id),
        "user_id": current_user.id
    })
    
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    return {"id": str(entry.pop("_id")), **entry}

@router.put("/entries/{entry_id}", response_model=AnalyticsEntry)
async def update_entry(
    entry_id: str,
    entry_data: AnalyticsEntryCreate,
    current_user: User = Depends(get_current_active_user),
):
    """Update an analytics entry"""
    from bson import ObjectId
    
    mongo_db = await get_mongo_db()
    result = await mongo_db.analytics_entries.update_one(
        {"_id": ObjectId(entry_id), "user_id": current_user.id},
        {"$set": entry_data.model_dump()}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    entry = await mongo_db.analytics_entries.find_one({"_id": ObjectId(entry_id)})
    return {"id": str(entry.pop("_id")), **entry}

@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(
    entry_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Delete an analytics entry"""
    from bson import ObjectId
    
    mongo_db = await get_mongo_db()
    result = await mongo_db.analytics_entries.delete_one({
        "_id": ObjectId(entry_id),
        "user_id": current_user.id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Entry not found")

# Statistics
@router.get("/stats", response_model=AnalyticsStats)
async def get_stats(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
):
    """Get analytics statistics"""
    query = {"user_id": current_user.id}
    
    if start_date or end_date:
        query["timestamp"] = {}
        if start_date:
            # Handle date string without time
            try:
                if 'T' not in start_date:
                    start_date = f"{start_date}T00:00:00"
                query["timestamp"]["$gte"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except:
                query["timestamp"]["$gte"] = datetime.fromisoformat(f"{start_date}T00:00:00+00:00")
        if end_date:
            try:
                if 'T' not in end_date:
                    end_date = f"{end_date}T23:59:59"
                query["timestamp"]["$lte"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except:
                query["timestamp"]["$lte"] = datetime.fromisoformat(f"{end_date}T23:59:59+00:00")
    
    mongo_db = await get_mongo_db()
    entries = await mongo_db.analytics_entries.find(query).to_list(length=10000)
    
    # Calculate stats
    categories = {}
    category_values = {}  # Track values per category for trend calculation
    
    for entry in entries:
        cat = entry.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
        
        # Track values for trend calculation
        if cat not in category_values:
            category_values[cat] = []
        value = entry.get("value", 0)
        timestamp = entry.get("timestamp")
        if timestamp:
            category_values[cat].append({
                "value": value,
                "timestamp": timestamp
            })
    
    # Calculate trends
    trends = []
    if entries:
        # Split entries into two periods (first half vs second half)
        sorted_entries = sorted(entries, key=lambda x: x.get("timestamp", datetime.min.replace(tzinfo=UTC)))
        mid_point = len(sorted_entries) // 2
        
        if mid_point > 0:
            first_half = sorted_entries[:mid_point]
            second_half = sorted_entries[mid_point:]
            
            # Calculate average values per category for each period
            first_period_avg = {}
            second_period_avg = {}
            
            for entry in first_half:
                cat = entry.get("category", "unknown")
                value = entry.get("value", 0)
                if cat not in first_period_avg:
                    first_period_avg[cat] = {"sum": 0, "count": 0}
                first_period_avg[cat]["sum"] += value
                first_period_avg[cat]["count"] += 1
            
            for entry in second_half:
                cat = entry.get("category", "unknown")
                value = entry.get("value", 0)
                if cat not in second_period_avg:
                    second_period_avg[cat] = {"sum": 0, "count": 0}
                second_period_avg[cat]["sum"] += value
                second_period_avg[cat]["count"] += 1
            
            # Calculate trend direction for each category
            all_categories = set(list(first_period_avg.keys()) + list(second_period_avg.keys()))
            
            for cat in all_categories:
                first_avg = 0
                second_avg = 0
                
                if cat in first_period_avg and first_period_avg[cat]["count"] > 0:
                    first_avg = first_period_avg[cat]["sum"] / first_period_avg[cat]["count"]
                
                if cat in second_period_avg and second_period_avg[cat]["count"] > 0:
                    second_avg = second_period_avg[cat]["sum"] / second_period_avg[cat]["count"]
                
                # Calculate percentage change
                if first_avg > 0:
                    change_percent = ((second_avg - first_avg) / first_avg) * 100
                elif second_avg > 0:
                    change_percent = 100  # New category
                else:
                    change_percent = 0
                
                # Determine trend direction
                if abs(change_percent) < 5:
                    direction = "stable"
                elif change_percent > 0:
                    direction = "increasing"
                else:
                    direction = "decreasing"
                
                trends.append({
                    "category": cat,
                    "direction": direction,
                    "change_percent": round(change_percent, 2),
                    "first_period_avg": round(first_avg, 2),
                    "second_period_avg": round(second_avg, 2),
                })
    
    return {
        "total_entries": len(entries),
        "categories": categories,
        "date_range": {
            "start": start_date or "",
            "end": end_date or "",
        },
        "trends": trends,
    }

# Time Series
@router.get("/time-series")
async def get_time_series(
    metric: str = Query(...),
    category: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
):
    """Get time series data for a metric"""
    query = {"user_id": current_user.id, "metric": metric}
    
    if category:
        query["category"] = category
    
    if start_date or end_date:
        query["timestamp"] = {}
        if start_date:
            # Handle date string without time
            try:
                if 'T' not in start_date:
                    start_date = f"{start_date}T00:00:00"
                query["timestamp"]["$gte"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except:
                query["timestamp"]["$gte"] = datetime.fromisoformat(f"{start_date}T00:00:00+00:00")
        if end_date:
            try:
                if 'T' not in end_date:
                    end_date = f"{end_date}T23:59:59"
                query["timestamp"]["$lte"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except:
                query["timestamp"]["$lte"] = datetime.fromisoformat(f"{end_date}T23:59:59+00:00")
    
    mongo_db = await get_mongo_db()
    entries = await mongo_db.analytics_entries.find(query).sort("timestamp", 1).to_list(length=10000)
    
    data = [
        {
            "date": entry["timestamp"].isoformat(),
            "value": entry["value"],
        }
        for entry in entries
    ]
    
    return {
        "metric": metric,
        "category": category or "all",
        "data": data,
    }

# Goals
@router.post("/goals", response_model=Goal, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_active_user),
):
    """Create a new goal"""
    goal_dict = {
        **goal_data.model_dump(),
        "user_id": current_user.id,
        "current_value": 0.0,
        "created_at": datetime.now(UTC),
    }
    
    mongo_db = await get_mongo_db()
    result = await mongo_db.goals.insert_one(goal_dict)
    
    return {
        **goal_dict,
        "id": str(result.inserted_id),
    }

@router.get("/goals", response_model=List[Goal])
async def get_goals(
    current_user: User = Depends(get_current_active_user),
):
    """Get user goals"""
    mongo_db = await get_mongo_db()
    cursor = mongo_db.goals.find({"user_id": current_user.id})
    goals = await cursor.to_list(length=100)
    
    # Calculate current values from entries
    for goal in goals:
        entries = await mongo_db.analytics_entries.find({
            "user_id": current_user.id,
            "metric": goal["metric"],
            "category": goal["category"],
        }).to_list(length=10000)
        
        goal["current_value"] = sum(e.get("value", 0) for e in entries)
    
    return [{"id": str(g.pop("_id")), **g} for g in goals]

@router.put("/goals/{goal_id}", response_model=Goal)
async def update_goal(
    goal_id: str,
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_active_user),
):
    """Update a goal"""
    from bson import ObjectId
    
    mongo_db = await get_mongo_db()
    result = await mongo_db.goals.update_one(
        {"_id": ObjectId(goal_id), "user_id": current_user.id},
        {"$set": goal_data.model_dump()}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    goal = await mongo_db.goals.find_one({"_id": ObjectId(goal_id)})
    return {"id": str(goal.pop("_id")), **goal}

@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Delete a goal"""
    from bson import ObjectId
    
    mongo_db = await get_mongo_db()
    result = await mongo_db.goals.delete_one({
        "_id": ObjectId(goal_id),
        "user_id": current_user.id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Goal not found")

# Export
@router.get("/export")
async def export_data(
    format: str = Query("json", regex="^(json|csv)$"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
):
    """Export analytics data"""
    from fastapi.responses import Response
    import json
    import csv
    from io import StringIO
    
    query = {"user_id": current_user.id}
    
    if start_date or end_date:
        query["timestamp"] = {}
        if start_date:
            # Handle date string without time
            try:
                if 'T' not in start_date:
                    start_date = f"{start_date}T00:00:00"
                query["timestamp"]["$gte"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except:
                query["timestamp"]["$gte"] = datetime.fromisoformat(f"{start_date}T00:00:00+00:00")
        if end_date:
            try:
                if 'T' not in end_date:
                    end_date = f"{end_date}T23:59:59"
                query["timestamp"]["$lte"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except:
                query["timestamp"]["$lte"] = datetime.fromisoformat(f"{end_date}T23:59:59+00:00")
    
    mongo_db = await get_mongo_db()
    entries = await mongo_db.analytics_entries.find(query).to_list(length=100000)
    
    if format == "json":
        data = [{"id": str(e.pop("_id")), **e} for e in entries]
        return Response(
            content=json.dumps(data, default=str),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=analytics-{datetime.now(UTC).date()}.json"}
        )
    else:  # CSV
        output = StringIO()
        if entries:
            writer = csv.DictWriter(output, fieldnames=entries[0].keys())
            writer.writeheader()
            for entry in entries:
                entry["_id"] = str(entry["_id"])
                writer.writerow(entry)
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=analytics-{datetime.now(UTC).date()}.csv"}
        )
