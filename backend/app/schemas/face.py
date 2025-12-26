"""Face recognition schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class FaceEnrollRequest(BaseModel):
    """Request to enroll a new face"""
    label: str = Field(..., description="Label for this face (e.g., 'primary', 'glasses')")

class FaceEnrollResponse(BaseModel):
    """Response after face enrollment"""
    face_id: int
    encoding_id: str
    label: str
    confidence_score: float
    quality_score: float
    message: str

class FaceRecognitionResponse(BaseModel):
    """Response from face recognition"""
    recognized: bool
    user_id: Optional[int] = None
    username: Optional[str] = None
    confidence: float
    num_faces_detected: int
    detection_time_ms: float
    message: str

class FaceListResponse(BaseModel):
    """User's enrolled faces"""
    id: int
    label: str
    confidence_score: float
    quality_score: float
    is_active: bool
    created_at: datetime
    last_recognized: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class FaceDeleteResponse(BaseModel):
    """Response after deleting a face"""
    message: str
    deleted_face_id: int
