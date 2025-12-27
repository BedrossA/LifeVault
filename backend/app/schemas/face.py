"""Enhanced face recognition schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class FaceEnrollRequest(BaseModel):
    """Request to enroll a new face"""
    label: str = Field(..., description="Label for this face")

class FaceEnrollResponse(BaseModel):
    """Response after face enrollment"""
    face_id: int
    encoding_id: str
    label: str
    confidence_score: float
    quality_score: float
    encoding_count: int
    custom_threshold: Optional[float] = None
    message: str

class FaceAddEncodingResponse(BaseModel):
    """Response after adding encoding"""
    face_id: int
    encoding_id: str
    encoding_count: int
    average_quality: float
    message: str

class DetectedFace(BaseModel):
    """Individual detected face in frame"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    face_id: Optional[int] = None
    confidence: float
    bbox: Dict[str, int]  # top, right, bottom, left
    quality_score: float
    is_known: bool

class FaceRecognitionResponse(BaseModel):
    """Response from face recognition - supports multiple faces"""
    recognized: bool
    num_faces_detected: int
    detection_time_ms: float
    faces: List[DetectedFace]
    primary_user_id: Optional[int] = None
    primary_username: Optional[str] = None
    message: str

class FaceListResponse(BaseModel):
    """User's enrolled faces"""
    id: int
    label: str
    confidence_score: float
    quality_score: float
    average_quality: float
    encoding_count: int
    recognition_count: int
    custom_threshold: Optional[float] = None
    is_active: bool
    created_at: datetime
    last_recognized: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class FaceDeleteResponse(BaseModel):
    """Response after deleting a face"""
    message: str
    deleted_face_id: int

class FaceStatsResponse(BaseModel):
    """Face recognition statistics"""
    total_faces: int
    active_faces: int
    total_encodings: int
    max_faces: int
    average_quality: float
    total_recognitions: int
    latest_enrollment: Optional[datetime] = None
