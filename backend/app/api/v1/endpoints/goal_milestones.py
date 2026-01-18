"""Goal milestone endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.db.base import get_db
from app.db.mongodb import get_mongo_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.goal_milestone import GoalMilestone

router = APIRouter()

# Schemas
class GoalMilestoneBase(BaseModel):
    title: str
    description: Optional[str] = None
    target_value: float
    order: int = 0

class GoalMilestoneCreate(GoalMilestoneBase):
    pass

class GoalMilestoneResponse(GoalMilestoneBase):
    id: int
    goal_id: str
    current_value: float
    achieved: bool
    achieved_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Create milestone
@router.post("/goals/{goal_id}/milestones", response_model=GoalMilestoneResponse, status_code=status.HTTP_201_CREATED)
async def create_milestone(
    goal_id: str,
    milestone_data: GoalMilestoneCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """Create a milestone for a goal"""
    # Verify goal exists and belongs to user
    goal = await mongo_db.goals.find_one({
        "id": goal_id,
        "user_id": current_user.id
    })
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    milestone = GoalMilestone(
        goal_id=goal_id,
        **milestone_data.model_dump()
    )
    
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    
    return milestone

# Get milestones for a goal
@router.get("/goals/{goal_id}/milestones", response_model=List[GoalMilestoneResponse])
async def get_milestones(
    goal_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """Get all milestones for a goal"""
    # Verify goal exists and belongs to user
    goal = await mongo_db.goals.find_one({
        "id": goal_id,
        "user_id": current_user.id
    })
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    milestones = db.query(GoalMilestone).filter(
        GoalMilestone.goal_id == goal_id
    ).order_by(GoalMilestone.order).all()
    
    return milestones

# Update milestone progress
@router.patch("/milestones/{milestone_id}/progress")
async def update_milestone_progress(
    milestone_id: int,
    current_value: float,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """Update milestone progress"""
    milestone = db.query(GoalMilestone).filter(
        GoalMilestone.id == milestone_id
    ).first()
    
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    # Verify goal belongs to use
    goal = await mongo_db.goals.find_one({
        "id": milestone.goal_id,
        "user_id": current_user.id
    })
    
    if not goal:
        raise HTTPException(status_code=403, detail="Access denied")
    
    milestone.current_value = current_value
    
    # Check if milestone is achieved
    if milestone.current_value >= milestone.target_value and not milestone.achieved:
        milestone.achieved = True
        milestone.achieved_at = datetime.now()
    
    db.commit()
    db.refresh(milestone)
    
    return milestone

# Mark milestone as achieved
@router.post("/milestones/{milestone_id}/achieve", response_model=GoalMilestoneResponse)
async def achieve_milestone(
    milestone_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """Mark a milestone as achieved"""
    milestone = db.query(GoalMilestone).filter(
        GoalMilestone.id == milestone_id
    ).first()
    
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    # Verify goal belongs to user
    goal = await mongo_db.goals.find_one({
        "id": milestone.goal_id,
        "user_id": current_user.id
    })
    
    if not goal:
        raise HTTPException(status_code=403, detail="Access denied")
    
    milestone.achieved = True
    milestone.achieved_at = datetime.now()
    
    db.commit()
    db.refresh(milestone)
    
    return milestone

# Delete milestone
@router.delete("/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_milestone(
    milestone_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """Delete a milestone"""
    milestone = db.query(GoalMilestone).filter(
        GoalMilestone.id == milestone_id
    ).first()
    
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    # Verify goal belongs to user
    goal = await mongo_db.goals.find_one({
        "id": milestone.goal_id,
        "user_id": current_user.id
    })
    
    if not goal:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db.delete(milestone)
    db.commit()
    
    return None

