"""Face recognition API endpoints"""
from fastapi import APIRouter, Depends, File, UploadFile, Request, HTTPException, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.db.base import get_db
from app.db.mongodb import get_mongo_db
from app.db.redis import get_redis
from app.schemas.face import (
    FaceEnrollRequest,
    FaceEnrollResponse,
    FaceRecognitionResponse,
    FaceListResponse,
    FaceDeleteResponse
)
from app.services.face_service import FaceRecognitionService
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.face import Face

router = APIRouter()

@router.post("/enroll", response_model=FaceEnrollResponse)
async def enroll_face(
    label: str = Form(...),  # Changed from query param to Form field
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """
    Enroll a new face for the current user
    
    - **label**: Label for this face (e.g., "primary", "with_glasses")
    - **image**: Image file containing a single face
    """
    # Load image
    image_array = FaceRecognitionService.load_image_from_upload(image)
    
    # Enroll face
    result = await FaceRecognitionService.enroll_face(
        db=db,
        mongo_db=mongo_db,
        user=current_user,
        image=image_array,
        label=label
    )
    
    return FaceEnrollResponse(**result)

@router.post("/recognize", response_model=FaceRecognitionResponse)
async def recognize_face(
    request: Request,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db),
    redis = Depends(get_redis)
):
    """
    Recognize a face in the uploaded image
    
    - **image**: Image file containing a face to recognize
    
    Returns user information if face is recognized
    """
    ip_address = request.client.host
    
    # Load image
    image_array = FaceRecognitionService.load_image_from_upload(image)
    
    # Recognize face
    result = await FaceRecognitionService.recognize_face(
        db=db,
        mongo_db=mongo_db,
        redis=redis,
        image=image_array,
        ip_address=ip_address
    )
    
    return FaceRecognitionResponse(**result)

@router.get("/my-faces", response_model=List[FaceListResponse])
def list_my_faces(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get list of all enrolled faces for current user
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
    """
    # Get face record
    face = db.query(Face).filter(
        Face.id == face_id,
        Face.user_id == current_user.id
    ).first()
    
    if not face:
        raise HTTPException(status_code=404, detail="Face not found")
    
    # Delete from MongoDB
    await mongo_db.face_encodings.delete_one({"encoding_id": face.encoding_id})
    
    # Delete from PostgreSQL
    db.delete(face)
    db.commit()
    
    return FaceDeleteResponse(
        message=f"Face '{face.label}' deleted successfully",
        deleted_face_id=face_id
    )

@router.get("/stats")
def get_face_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get face recognition statistics for current user"""
    
    total_faces = db.query(func.count(Face.id)).filter(
        Face.user_id == current_user.id
    ).scalar()
    
    active_faces = db.query(func.count(Face.id)).filter(
        Face.user_id == current_user.id,
        Face.is_active == True
    ).scalar()
    
    latest_face = db.query(Face).filter(
        Face.user_id == current_user.id
    ).order_by(Face.created_at.desc()).first()
    
    return {
        "total_faces": total_faces,
        "active_faces": active_faces,
        "max_faces": 5,
        "latest_enrollment": latest_face.created_at if latest_face else None
    }
