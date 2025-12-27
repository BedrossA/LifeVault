"""Enhanced Face Recognition API Endpoints"""
from fastapi import APIRouter, Depends, File, UploadFile, Request, HTTPException, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.db.base import get_db
from app.db.mongodb import get_mongo_db
from app.db.redis import get_redis
from app.schemas.face import (
    FaceEnrollResponse,
    FaceRecognitionResponse,
    FaceListResponse,
    FaceDeleteResponse,
    FaceStatsResponse,
    FaceAddEncodingResponse
)
from app.services.face_service import FaceRecognitionService
from app.services.face_service_enhanced import EnhancedFaceService
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.face import Face

router = APIRouter()

# ============================================
# ENROLLMENT ENDPOINTS
# ============================================

@router.post("/enroll", response_model=FaceEnrollResponse)
async def enroll_face(
    label: str = Form(...),
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """
    Enroll a new face for the current user
    
    - **label**: Label for this face (e.g., "primary", "with_glasses")
    - **image**: Image file containing a single face
    
    Returns face_id, encoding_id, quality metrics, and adaptive threshold
    """
    image_array = FaceRecognitionService.load_image_from_upload(image)
    
    result = await FaceRecognitionService.enroll_face(
        db=db,
        mongo_db=mongo_db,
        user=current_user,
        image=image_array,
        label=label
    )
    
    return FaceEnrollResponse(**result)


@router.post("/{face_id}/add-encoding", response_model=FaceAddEncodingResponse)
async def add_face_encoding(
    face_id: int,
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """
    ✨ NEW: Add another encoding to existing face
    
    Allows you to enroll the same person from different angles,
    lighting conditions, or with accessories (glasses, hat, etc.)
    
    - **face_id**: ID of the face to add encoding to
    - **image**: Another image of the same person
    
    Maximum 10 encodings per face. Improves recognition accuracy!
    """
    image_array = FaceRecognitionService.load_image_from_upload(image)
    
    result = await EnhancedFaceService.add_encoding_to_face(
        db=db,
        mongo_db=mongo_db,
        face_id=face_id,
        user=current_user,
        image=image_array
    )
    
    return FaceAddEncodingResponse(**result)


# ============================================
# RECOGNITION ENDPOINTS
# ============================================

@router.post("/recognize", response_model=FaceRecognitionResponse)
async def recognize_face(
    request: Request,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db),
    redis = Depends(get_redis)
):
    """
    Recognize a face in the uploaded image (single face mode)
    
    - **image**: Image file containing a face to recognize
    
    Returns user information if face is recognized.
    For backward compatibility, rejects images with multiple faces.
    """
    ip_address = request.client.host
    image_array = FaceRecognitionService.load_image_from_upload(image)
    
    result = await FaceRecognitionService.recognize_face(
        db=db,
        mongo_db=mongo_db,
        redis=redis,
        image=image_array,
        ip_address=ip_address
    )
    
    return FaceRecognitionResponse(**result)


@router.post("/recognize-multi", response_model=FaceRecognitionResponse)
async def recognize_multiple_faces(
    request: Request,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """
    ✨ NEW: Recognize MULTIPLE faces in one image
    
    - **image**: Image file that may contain multiple faces
    
    Returns array of detected faces with:
    - Known users (matched against database)
    - Unknown faces (not in database)
    - Bounding boxes for each face
    - Confidence scores
    
    Useful for family photos, group pictures, or security monitoring.
    """
    ip_address = request.client.host
    image_array = FaceRecognitionService.load_image_from_upload(image)
    
    result = await EnhancedFaceService.recognize_faces_multi(
        db=db,
        mongo_db=mongo_db,
        image=image_array,
        ip_address=ip_address
    )
    
    return FaceRecognitionResponse(**result)


# ============================================
# MANAGEMENT ENDPOINTS
# ============================================

@router.get("/my-faces", response_model=List[FaceListResponse])
def list_my_faces(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get list of all enrolled faces for current user
    
    Now includes:
    - encoding_count: Number of encodings for this face
    - average_quality: Average quality across all encodings
    - recognition_count: Times this face was recognized
    - custom_threshold: Adaptive threshold (if enabled)
    """
    faces = db.query(Face).filter(
        Face.user_id == current_user.id
    ).order_by(Face.created_at.desc()).all()
    
    return faces


@router.delete("/{face_id}", response_model=FaceDeleteResponse)
async def delete_face(
    face_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """
    Delete an enrolled face
    
    - **face_id**: ID of the face to delete
    
    Deletes face record from PostgreSQL and ALL associated
    encodings from MongoDB.
    """
    # Get face record
    face = db.query(Face).filter(
        Face.id == face_id,
        Face.user_id == current_user.id
    ).first()
    
    if not face:
        raise HTTPException(status_code=404, detail="Face not found")
    
    # Delete ALL encodings from MongoDB (including additional ones)
    result = await mongo_db.face_encodings.delete_many({
        "$or": [
            {"encoding_id": face.encoding_id},  # Primary encoding
            {"metadata.parent_face_id": face_id}  # Additional encodings
        ]
    })
    
    deleted_count = result.deleted_count
    
    # Delete from PostgreSQL
    db.delete(face)
    db.commit()
    
    return FaceDeleteResponse(
        message=f"Face '{face.label}' deleted (removed {deleted_count} encodings)",
        deleted_face_id=face_id
    )


@router.get("/stats", response_model=FaceStatsResponse)
def get_face_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get face recognition statistics for current user
    
    Enhanced with:
    - Total encodings count
    - Average quality across all faces
    - Total recognitions count
    """
    faces = db.query(Face).filter(
        Face.user_id == current_user.id
    ).all()
    
    total_faces = len(faces)
    active_faces = len([f for f in faces if f.is_active])
    total_encodings = sum(f.encoding_count for f in faces)
    
    # Calculate average quality
    if faces:
        avg_quality = sum(f.average_quality for f in faces) / len(faces)
    else:
        avg_quality = 0.0
    
    # Sum all recognitions
    total_recognitions = sum(f.recognition_count for f in faces)
    
    latest_face = db.query(Face).filter(
        Face.user_id == current_user.id
    ).order_by(Face.created_at.desc()).first()
    
    return FaceStatsResponse(
        total_faces=total_faces,
        active_faces=active_faces,
        total_encodings=total_encodings,
        max_faces=5,
        average_quality=avg_quality,
        total_recognitions=total_recognitions,
        latest_enrollment=latest_face.created_at if latest_face else None
    )


# ============================================
# UTILITY ENDPOINTS
# ============================================

@router.get("/config")
def get_face_config(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current face recognition configuration
    
    Useful for UI to show current settings
    """
    return {
        "max_faces_per_user": 5,
        "max_encodings_per_face": 10,
        "min_quality_threshold": 0.5,
        "adaptive_thresholds_enabled": True,
        "multi_face_detection_enabled": True,
        "max_faces_in_frame": 10,
        "detection_method": "hog",  # or "cnn"
        "thresholds": {
            "high_quality": 0.5,
            "default": 0.6,
            "low_quality": 0.7
        }
    }


@router.get("/{face_id}/details")
def get_face_details(
    face_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific face
    
    Includes all quality metrics and usage statistics
    """
    face = db.query(Face).filter(
        Face.id == face_id,
        Face.user_id == current_user.id
    ).first()
    
    if not face:
        raise HTTPException(status_code=404, detail="Face not found")
    
    return {
        "id": face.id,
        "label": face.label,
        "encoding_count": face.encoding_count,
        "quality_score": face.quality_score,
        "average_quality": face.average_quality,
        "custom_threshold": face.custom_threshold,
        "recognition_count": face.recognition_count,
        "is_active": face.is_active,
        "created_at": face.created_at,
        "last_recognized": face.last_recognized,
        "can_add_more_encodings": face.encoding_count < 10,
        "recommendation": (
            "Add more encodings from different angles to improve accuracy"
            if face.encoding_count < 3
            else "Good coverage!"
        )
    }
