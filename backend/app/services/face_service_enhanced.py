"""
Enhanced Face Recognition Service
Multiple encodings per user, adaptive thresholds, multi-person detection
"""
import face_recognition
import numpy as np
from typing import Optional, List, Tuple, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, UploadFile
from PIL import Image
import io
import time
import uuid
import logging

from app.models.user import User
from app.models.face import Face
from app.models.face_mongo_models import FaceEncoding
from app.core.config import settings

logger = logging.getLogger(__name__)


class EnhancedFaceService:
    """Enhanced face recognition with advanced features"""
    
    @staticmethod
    def get_adaptive_threshold(face: Face) -> float:
        """
        Get adaptive recognition threshold based on face quality
        
        Higher quality → stricter threshold (lower = 0.5)
        Lower quality → lenient threshold (higher = 0.7)
        """
        if face.custom_threshold is not None:
            return face.custom_threshold
        
        if not settings.FACE_ADAPTIVE_THRESHOLD_ENABLED:
            return settings.FACE_RECOGNITION_TOLERANCE
        
        quality = face.average_quality if face.average_quality > 0 else face.quality_score
        
        if quality >= 0.7:
            return settings.FACE_HIGH_QUALITY_THRESHOLD  # 0.5
        elif quality <= 0.4:
            return settings.FACE_LOW_QUALITY_THRESHOLD  # 0.7
        else:
            return settings.FACE_RECOGNITION_TOLERANCE  # 0.6
    
    @staticmethod
    async def add_encoding_to_face(
        db: Session,
        mongo_db,
        face_id: int,
        user: User,
        image: np.ndarray
    ) -> dict:
        """
        Add additional encoding to existing face
        Allows user to have 5-10 different photos (angles/lighting)
        """
        from app.services.face_service import FaceRecognitionService
        
        start_time = time.time()
        
        # Get face record
        face = db.query(Face).filter(
            Face.id == face_id,
            Face.user_id == user.id,
            Face.is_active == True
        ).first()
        
        if not face:
            raise HTTPException(status_code=404, detail="Face not found")
        
        # Check max encodings
        if face.encoding_count >= 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 encodings per face"
            )
        
        # Detect face
        face_locations = FaceRecognitionService.detect_faces(image)
        if not face_locations:
            raise HTTPException(status_code=400, detail="No face detected in image")
        if len(face_locations) > 1:
            raise HTTPException(
                status_code=400, 
                detail="Multiple faces detected. Please upload image with single face"
            )
        
        face_location = face_locations[0]
        
        # Generate encoding
        encoding = FaceRecognitionService.encode_face(image, face_location)
        if encoding is None:
            raise HTTPException(
                status_code=400, 
                detail="Failed to generate face encoding"
            )
        
        # Calculate quality
        quality_score = FaceRecognitionService.calculate_quality_score(
            image, 
            face_location
        )
        
        if quality_score < settings.FACE_MIN_QUALITY_THRESHOLD:
            raise HTTPException(
                status_code=400,
                detail=f"Image quality too low ({quality_score:.2f}). Please use better lighting."
            )
        
        # Generate new encoding ID
        encoding_id = str(uuid.uuid4())
        
        # Store in MongoDB with reference to parent face
        top, right, bottom, left = face_location
        face_encoding_doc = FaceEncoding(
            encoding_id=encoding_id,
            user_id=user.id,
            label=f"{face.label}_encoding_{face.encoding_count + 1}",
            encoding=encoding.tolist(),
            image_width=image.shape[1],
            image_height=image.shape[0],
            face_location={
                "top": int(top),
                "right": int(right),
                "bottom": int(bottom),
                "left": int(left)
            },
            confidence_score=1.0,
            quality_score=quality_score,
            detection_method=settings.FACE_DETECTION_METHOD,
            metadata={"parent_face_id": face_id}
        )
        
        await mongo_db.face_encodings.insert_one(face_encoding_doc.dict())
        
        # Update face record statistics
        new_count = face.encoding_count + 1
        new_avg_quality = (
            (face.average_quality * face.encoding_count + quality_score) / new_count
        )
        
        face.encoding_count = new_count
        face.average_quality = new_avg_quality
        face.updated_at = func.now()
        
        # Update adaptive threshold based on new average
        if settings.FACE_ADAPTIVE_THRESHOLD_ENABLED:
            if new_avg_quality >= 0.7:
                face.custom_threshold = settings.FACE_HIGH_QUALITY_THRESHOLD
            elif new_avg_quality <= 0.4:
                face.custom_threshold = settings.FACE_LOW_QUALITY_THRESHOLD
            else:
                face.custom_threshold = None  # Use default
        
        db.commit()
        db.refresh(face)
        
        elapsed_time = (time.time() - start_time) * 1000
        
        logger.info(
            f"Added encoding to face {face_id} "
            f"(count: {new_count}, avg quality: {new_avg_quality:.2f})"
        )
        
        return {
            "face_id": face.id,
            "encoding_id": encoding_id,
            "encoding_count": new_count,
            "average_quality": new_avg_quality,
            "detection_time_ms": elapsed_time,
            "message": f"Encoding added successfully (total: {new_count})"
        }
    
    @staticmethod
    async def recognize_faces_multi(
        db: Session,
        mongo_db,
        image: np.ndarray,
        ip_address: str
    ) -> dict:
        """
        Recognize MULTIPLE faces in image
        
        Returns information about ALL detected faces:
        - Known users (matched against database)
        - Unknown faces (not in database)
        """
        from app.services.face_service import FaceRecognitionService
        
        start_time = time.time()
        event_id = str(uuid.uuid4())
        
        # Detect all faces in frame
        max_faces = (
            settings.FACE_MAX_FACES_IN_FRAME 
            if settings.FACE_ENABLE_MULTI_DETECTION 
            else 1
        )
        
        face_locations = FaceRecognitionService.detect_faces(
            image,
            method=settings.FACE_DETECTION_METHOD,
            max_faces=max_faces
        )
        
        num_faces = len(face_locations)
        
        if num_faces == 0:
            elapsed_time = (time.time() - start_time) * 1000
            return {
                "recognized": False,
                "num_faces_detected": 0,
                "detection_time_ms": elapsed_time,
                "faces": [],
                "primary_user_id": None,
                "primary_username": None,
                "message": "No face detected"
            }
        
        # Load all known face encodings from MongoDB
        cursor = mongo_db.face_encodings.find({})
        known_encodings_data = await cursor.to_list(length=10000)
        
        # Organize by user (multiple encodings per user)
        user_encodings: Dict[int, List[np.ndarray]] = {}
        user_faces: Dict[int, Face] = {}
        
        for enc_data in known_encodings_data:
            user_id = enc_data["user_id"]
            
            if user_id not in user_encodings:
                user_encodings[user_id] = []
                
                # Get face record for adaptive threshold
                face = db.query(Face).filter(
                    Face.user_id == user_id,
                    Face.is_active == True
                ).first()
                user_faces[user_id] = face
            
            user_encodings[user_id].append(np.array(enc_data["encoding"]))
        
        # Process EACH detected face
        detected_faces = []
        recognized_user_ids = []
        
        for face_location in face_locations:
            top, right, bottom, left = face_location
            
            # Encode this detected face
            unknown_encoding = FaceRecognitionService.encode_face(image, face_location)
            if unknown_encoding is None:
                # Could not encode - skip
                continue
            
            # Calculate quality of detection
            quality_score = FaceRecognitionService.calculate_quality_score(
                image, 
                face_location
            )
            
            # Compare with ALL known users
            best_match_user_id = None
            best_match_distance = float('inf')
            best_match_face = None
            
            for user_id, encodings_list in user_encodings.items():
                # Compare with ALL encodings for this user
                distances = face_recognition.face_distance(
                    encodings_list, 
                    unknown_encoding
                )
                min_distance = float(np.min(distances))
                
                if min_distance < best_match_distance:
                    best_match_distance = min_distance
                    best_match_user_id = user_id
                    best_match_face = user_faces[user_id]
            
            # Determine if recognized using adaptive threshold
            if best_match_face and best_match_user_id:
                threshold = EnhancedFaceService.get_adaptive_threshold(best_match_face)
                is_recognized = best_match_distance <= threshold
            else:
                is_recognized = False
            
            # Build face info
            if is_recognized:
                user = db.query(User).filter(User.id == best_match_user_id).first()
                
                if user and user.is_active:
                    confidence = float(1.0 - best_match_distance)
                    
                    detected_faces.append({
                        "user_id": user.id,
                        "username": user.username,
                        "face_id": best_match_face.id,
                        "confidence": confidence,
                        "bbox": {
                            "top": int(top), 
                            "right": int(right), 
                            "bottom": int(bottom), 
                            "left": int(left)
                        },
                        "quality_score": quality_score,
                        "is_known": True
                    })
                    
                    recognized_user_ids.append(user.id)
                    
                    # Update recognition stats
                    best_match_face.recognition_count += 1
                    best_match_face.last_recognized = func.now()
            else:
                # Unknown face
                confidence = (
                    float(1.0 - best_match_distance) 
                    if best_match_distance != float('inf') 
                    else 0.0
                )
                
                detected_faces.append({
                    "user_id": None,
                    "username": None,
                    "face_id": None,
                    "confidence": confidence,
                    "bbox": {
                        "top": int(top), 
                        "right": int(right), 
                        "bottom": int(bottom), 
                        "left": int(left)
                    },
                    "quality_score": quality_score,
                    "is_known": False
                })
        
        db.commit()
        elapsed_time = (time.time() - start_time) * 1000
        
        # Determine primary user (first recognized)
        primary_user_id = None
        primary_username = None
        if recognized_user_ids:
            primary_user_id = recognized_user_ids[0]
            user = db.query(User).filter(User.id == primary_user_id).first()
            if user:
                primary_username = user.username
        
        # Build message
        if not detected_faces:
            message = f"Detected {num_faces} face(s) but could not process"
        elif len(recognized_user_ids) == 0:
            message = f"Detected {num_faces} unknown face(s)"
        elif len(recognized_user_ids) == 1:
            message = f"Welcome back, {primary_username}!"
        else:
            users = ", ".join([
                db.query(User).filter(User.id == uid).first().username 
                for uid in recognized_user_ids[:3]
            ])
            if len(recognized_user_ids) > 3:
                users += f" and {len(recognized_user_ids) - 3} more"
            message = f"Recognized: {users}"
        
        logger.info(
            f"Multi-face recognition: {num_faces} detected, "
            f"{len(recognized_user_ids)} recognized, "
            f"{elapsed_time:.0f}ms"
        )
        
        return {
            "recognized": len(recognized_user_ids) > 0,
            "num_faces_detected": num_faces,
            "detection_time_ms": elapsed_time,
            "faces": detected_faces,
            "primary_user_id": primary_user_id,
            "primary_username": primary_username,
            "message": message
        }
