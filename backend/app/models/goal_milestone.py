"""Goal milestone models"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from app.db.base import Base

class GoalMilestone(Base):
    """Goal milestone model"""
    __tablename__ = "goal_milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(String, ForeignKey("goals.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0.0)
    achieved = Column(Boolean, default=False)
    achieved_at = Column(DateTime, nullable=True)
    order = Column(Integer, default=0)  # Order of milestone
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    def __repr__(self):
        return f"<GoalMilestone {self.id} goal_id={self.goal_id} title={self.title}>"

