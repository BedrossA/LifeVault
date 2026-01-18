"""Improved Analytics endpoints with better error handling"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, UTC
from pydantic import BaseModel, Field
import logging

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