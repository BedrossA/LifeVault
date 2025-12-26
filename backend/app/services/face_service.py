"""Face recognition service using face_recognition library"""
import face_recognition
import numpy as np
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from PIL import Image
import io
import time
import uuid
import logging

from app.models.user import User
from app.models.face import Face
from app.models.face_mongo_models import FaceEncoding, RecognitionEvent
from app.core.config import settings

logger = logging.getLogger(__name__)

class FaceRecognitionService:
    """Service for face detection, encoding, and recognition"""
    
    @staticmethod
    def load_image_from_upload(file: UploadFile) -> np.ndarray:
        """Load image from uploaded file"""
        try:
            image_data = file.file.read()
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return np.array(image)
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            raise HTTPException(status_code=400, detail="Invalid image file")
    
    @staticmethod
    def detect_faces(image: np.ndarray, method: str = "hog") -> List[Tuple]:
        """
        Detect faces in image
        
        Args:
            image: Image as numpy array
            method: Detection method ('hog' or 'cnn')
        
        Returns:
            List of face locations (top, right, bottom, left)
        """
        try:
            face_locations = face_recognition.face_locations(
                image, 
                model=method
            )
            return face_locations
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []
    
    @staticmethod
    def encode_face(image: np.ndarray, face_location: Tuple) -> Optional[np.ndarray]:
        """
        Generate face encoding from image
        
        Args:
            image: Image as numpy array
            face_location: Face location tuple
        
        Returns:
            128-dimensional face encoding or None
        """
        try:
            encodings = face_recognition.face_encodings(
                image,
                known_face_locations=[face_location],
                model=settings.FACE_ENCODING_MODEL
            )
            
            if encodings:
                return encodings[0]
            return None
        except Exception as e:
            logger.error(f"Error encoding face: {e}")
            return None
    
    @staticmethod
    def calculate_quality_score(image: np.ndarray, face_location: Tuple) -> float:
        """
        Calculate face quality score based on size and clarity
        
        Args:
            image: Image as numpy array
            face_location: Face location tuple (top, right, bottom, left)
        
        Returns:
            Quality score between 0 and 1
        """
        top, right, bottom, left = face_location
        
        # Face size
        face_width = right - left
        face_height = bottom - top
        face_area = face_width * face_height
        
        image_height, image_width = image.shape[:2]
        image_area = image_height * image_width
        
        # Size score (larger faces are better, up to 30% of image)
        size_ratio = face_area / image_area
        size_score = min(size_ratio / 0.3, 1.0)
        
        # Simple sharpness check (variance of Laplacian)
        face_crop = image[top:bottom, left:right]
        if len(face_crop.shape) == 3:
            face_gray = np.mean(face_crop, axis=2).astype(np.uint8)
        else:
            face_gray = face_crop
        
        # Calculate variance
        variance = np.var(face_gray)
        sharpness_score = min(variance / 1000.0, 1.0)
        
        # Combined score
        quality_score = (size_score * 0.6 + sharpness_score * 0.4)
        
        return float(quality_score)
    
    @staticmethod
    async def enroll_face(
        db: Session,
        mongo_db,
        user: User,
        image: np.ndarray,
        label: str
    ) -> dict:
        """
        Enroll a new face for a user
        
        Args:
            db: PostgreSQL session
            mongo_db: MongoDB database
            user: User object
            image: Image as numpy array
            label: Label for this face
        
        Returns:
            Dictionary with enrollment result
        """
        start_time = time.time()
        
        # Check if user already has max faces
        existing_faces = db.query(Face).filter(
            Face.user_id == user.id,
            Face.is_active == True
        ).count()
        
        if existing_faces >= settings.MAX_FACES_PER_USER:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {settings.MAX_FACES_PER_USER} faces per user"
            )
        
        # Detect faces
        face_locations = FaceRecognitionService.detect_faces(
            image,
            method=settings.FACE_DETECTION_METHOD
        )
        
        if not face_locations:
            raise HTTPException(
                status_code=400,
                detail="No face detected in image"
            )
        
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
        
        # Generate unique encoding ID
        encoding_id = str(uuid.uuid4())
        
        # Store encoding in MongoDB
        top, right, bottom, left = face_location
        face_encoding_doc = FaceEncoding(
            encoding_id=encoding_id,
            user_id=user.id,
            label=label,
            encoding=encoding.tolist(),
            image_width=image.shape[1],
            image_height=image.shape[0],
            face_location={
                "top": int(top),
                "right": int(right),
                "bottom": int(bottom),
                "left": int(left)
            },
            confidence_score=1.0,  # High confidence for enrollment
            quality_score=quality_score,
            detection_method=settings.FACE_DETECTION_METHOD
        )
        
        await mongo_db.face_encodings.insert_one(face_encoding_doc.dict())
        
        # Store metadata in PostgreSQL
        face_record = Face(
            user_id=user.id,
            label=label,
            encoding_id=encoding_id,
            confidence_score=1.0,
            quality_score=quality_score,
            is_active=True,
            is_verified=True
        )
        
        db.add(face_record)
        db.commit()
        db.refresh(face_record)
        
        elapsed_time = (time.time() - start_time) * 1000
        
        logger.info(f"Face enrolled for user {user.username}: {label} (quality: {quality_score:.2f})")
        
        return {
            "face_id": face_record.id,
            "encoding_id": encoding_id,
            "label": label,
            "confidence_score": 1.0,
            "quality_score": quality_score,
            "detection_time_ms": elapsed_time,
            "message": f"Face '{label}' enrolled successfully"
        }
    
    @staticmethod
    async def recognize_face(
        db: Session,
        mongo_db,
        redis,
        image: np.ndarray,
        ip_address: str
    ) -> dict:
        """
        Recognize a face in the image
        
        Args:
            db: PostgreSQL session
            mongo_db: MongoDB database
            redis: Redis client
            image: Image as numpy array
            ip_address: Client IP address
        
        Returns:
            Dictionary with recognition result
        """
        start_time = time.time()
        
        # Detect faces
        face_locations = FaceRecognitionService.detect_faces(
            image,
            method=settings.FACE_DETECTION_METHOD
        )
        
        num_faces = len(face_locations)
        
        if num_faces == 0:
            elapsed_time = (time.time() - start_time) * 1000
            
            # Log event
            event = RecognitionEvent(
                event_id=str(uuid.uuid4()),
                recognized=False,
                confidence=0.0,
                num_faces_detected=0,
                detection_time_ms=elapsed_time,
                ip_address=ip_address
            )
            await mongo_db.recognition_events.insert_one(event.dict())
            
            return {
                "recognized": False,
                "user_id": None,
                "username": None,
                "confidence": 0.0,
                "num_faces_detected": 0,
                "detection_time_ms": elapsed_time,
                "message": "No face detected"
            }
        
        if num_faces > 1:
            elapsed_time = (time.time() - start_time) * 1000
            return {
                "recognized": False,
                "user_id": None,
                "username": None,
                "confidence": 0.0,
                "num_faces_detected": num_faces,
                "detection_time_ms": elapsed_time,
                "message": f"Multiple faces detected ({num_faces}). Please ensure only one person."
            }
        
        face_location = face_locations[0]
        
        # Generate encoding for detected face
        unknown_encoding = FaceRecognitionService.encode_face(image, face_location)
        if unknown_encoding is None:
            elapsed_time = (time.time() - start_time) * 1000
            return {
                "recognized": False,
                "user_id": None,
                "username": None,
                "confidence": 0.0,
                "num_faces_detected": 1,
                "detection_time_ms": elapsed_time,
                "message": "Failed to encode detected face"
            }
        
        # Get all active face encodings from MongoDB
        cursor = mongo_db.face_encodings.find({})
        known_encodings = await cursor.to_list(length=1000)
        
        if not known_encodings:
            elapsed_time = (time.time() - start_time) * 1000
            return {
                "recognized": False,
                "user_id": None,
                "username": None,
                "confidence": 0.0,
                "num_faces_detected": 1,
                "detection_time_ms": elapsed_time,
                "message": "No enrolled faces in system"
            }
        
        # Compare with known faces
        best_match_user_id = None
        best_match_distance = float('inf')
        
        for known_face in known_encodings:
            known_encoding = np.array(known_face["encoding"])
            
            # Calculate face distance (lower is better)
            distance = face_recognition.face_distance(
                [known_encoding],
                unknown_encoding
            )[0]
            
            if distance < best_match_distance:
                best_match_distance = distance
                best_match_user_id = known_face["user_id"]
        
        elapsed_time = (time.time() - start_time) * 1000
        
        # Check if match is good enough
        tolerance = settings.FACE_RECOGNITION_TOLERANCE
        recognized = best_match_distance <= tolerance
        
        if recognized:
            # Get user details
            user = db.query(User).filter(User.id == best_match_user_id).first()
            
            if user and user.is_active:
                # Update last_recognized timestamp
                db.query(Face).filter(
                    Face.user_id == user.id,
                    Face.is_active == True
                ).update({"last_recognized": func.now()})
                db.commit()
                
                confidence = float(1.0 - best_match_distance)
                
                # Log recognition event
                event = RecognitionEvent(
                    event_id=str(uuid.uuid4()),
                    user_id=user.id,
                    recognized=True,
                    confidence=confidence,
                    num_faces_detected=1,
                    detection_time_ms=elapsed_time,
                    ip_address=ip_address
                )
                await mongo_db.recognition_events.insert_one(event.dict())
                
                logger.info(f"Face recognized: {user.username} (confidence: {confidence:.2f})")
                
                return {
                    "recognized": True,
                    "user_id": user.id,
                    "username": user.username,
                    "confidence": confidence,
                    "num_faces_detected": 1,
                    "detection_time_ms": elapsed_time,
                    "message": f"Welcome back, {user.username}!"
                }
        
        # Not recognized
        event = RecognitionEvent(
            event_id=str(uuid.uuid4()),
            recognized=False,
            confidence=float(1.0 - best_match_distance) if best_match_distance != float('inf') else 0.0,
            num_faces_detected=1,
            detection_time_ms=elapsed_time,
            ip_address=ip_address
        )
        await mongo_db.recognition_events.insert_one(event.dict())
        
        return {
            "recognized": False,
            "user_id": None,
            "username": None,
            "confidence": 0.0,
            "num_faces_detected": 1,
            "detection_time_ms": elapsed_time,
            "message": "Face not recognized"
        }