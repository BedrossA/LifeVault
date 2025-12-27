"""MongoDB schemas for face recognition data"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class FaceEncoding(BaseModel):
    """Face encoding stored in MongoDB"""
    encoding_id: str
    user_id: int
    label: str
    encoding: List[float]  # 128-dimensional face encoding
    
    # Image metadata
    image_width: int
    image_height: int
    face_location: Dict[str, int]  # top, right, bottom, left
    
    # Quality metrics
    confidence_score: float = 0.0
    quality_score: float = 0.0
    
    # Detection details
    detection_method: str = "hog"  # hog or cnn
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

class RecognitionEvent(BaseModel):
    """Face recognition event log"""
    event_id: str
    user_id: Optional[int] = None
    recognized: bool
    confidence: float
    
    # Detection details
    num_faces_detected: int
    detection_time_ms: float
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: str
    metadata: Optional[Dict[str, Any]] = None
