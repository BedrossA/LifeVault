"""Face recognition models"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Face(Base):
    """Face data linked to users"""
    __tablename__ = "faces"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Face metadata
    label = Column(String, nullable=False)  # "primary", "alternate_1", etc.
    encoding_id = Column(String, unique=True, index=True)  # MongoDB reference
    
    # Quality metrics
    confidence_score = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_recognized = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Face user_id={self.user_id} label={self.label}>"