"""Enhanced face recognition models"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from app.db.base import Base

class Face(Base):
    """Face data linked to users with multiple encodings support"""
    __tablename__ = "faces"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Face metadata
    label = Column(String, nullable=False)
    encoding_id = Column(String, index=True)  # Primary encoding ID
    
    # Multiple encodings support
    encoding_count = Column(Integer, default=1)
    
    # Quality metrics
    confidence_score = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0)
    average_quality = Column(Float, default=0.0)
    
    # Adaptive threshold
    custom_threshold = Column(Float, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Usage statistics
    recognition_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_recognized = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Face user_id={self.user_id} label={self.label} encodings={self.encoding_count}>"
