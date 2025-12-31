"""Emotion detection service using facial landmarks and OpenCV"""
import cv2
import numpy as np
import face_recognition
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class EmotionDetectionService:
    """Service for detecting emotions from facial expressions"""
    
    # Basic emotion categories
    EMOTIONS = ['happy', 'sad', 'angry', 'surprised', 'fearful', 'disgusted', 'neutral']
    
    @staticmethod
    def detect_emotion_from_landmarks(face_landmarks: Dict) -> Dict[str, float]:
        """
        Detect emotion from facial landmarks using geometric features
        
        Args:
            face_landmarks: Dictionary of facial landmarks from face_recognition
            
        Returns:
            Dictionary with emotion probabilities
        """
        try:
            # Extract key facial features
            left_eye = face_landmarks.get('left_eye', [])
            right_eye = face_landmarks.get('right_eye', [])
            nose_tip = face_landmarks.get('nose_tip', [])
            mouth = face_landmarks.get('top_lip', []) + face_landmarks.get('bottom_lip', [])
            left_eyebrow = face_landmarks.get('left_eyebrow', [])
            right_eyebrow = face_landmarks.get('right_eyebrow', [])
            
            if not all([left_eye, right_eye, nose_tip, mouth]):
                return {'neutral': 1.0}
            
            # Calculate geometric features
            features = {}
            
            # Eye opening (happy vs sad)
            left_eye_height = max(p[1] for p in left_eye) - min(p[1] for p in left_eye)
            right_eye_height = max(p[1] for p in right_eye) - min(p[1] for p in right_eye)
            avg_eye_height = (left_eye_height + right_eye_height) / 2
            features['eye_opening'] = avg_eye_height
            
            # Mouth curvature (smile detection)
            mouth_center_y = sum(p[1] for p in mouth) / len(mouth)
            mouth_corners = [p for p in mouth if abs(p[1] - mouth_center_y) < 2]
            if len(mouth_corners) >= 2:
                mouth_width = max(p[0] for p in mouth_corners) - min(p[0] for p in mouth_corners)
                mouth_height = max(p[1] for p in mouth) - min(p[1] for p in mouth)
                features['mouth_aspect_ratio'] = mouth_width / max(mouth_height, 1)
            else:
                features['mouth_aspect_ratio'] = 1.0
            
            # Eyebrow position (surprise, anger)
            if left_eyebrow and right_eyebrow:
                eyebrow_y = (sum(p[1] for p in left_eyebrow) + sum(p[1] for p in right_eyebrow)) / (len(left_eyebrow) + len(right_eyebrow))
                eye_y = (sum(p[1] for p in left_eye) + sum(p[1] for p in right_eye)) / (len(left_eye) + len(right_eye))
                features['eyebrow_eye_distance'] = abs(eyebrow_y - eye_y)
            else:
                features['eyebrow_eye_distance'] = 20.0
            
            # Calculate emotion probabilities based on features
            emotions = {}
            
            # Happy: wide mouth, raised corners, open eyes
            if features['mouth_aspect_ratio'] > 1.5:
                emotions['happy'] = min(0.8, features['mouth_aspect_ratio'] / 2.0)
            else:
                emotions['happy'] = 0.1
            
            # Sad: downturned mouth, droopy eyes
            if features['mouth_aspect_ratio'] < 0.8 and features['eye_opening'] < 10:
                emotions['sad'] = 0.7
            else:
                emotions['sad'] = 0.1
            
            # Surprised: raised eyebrows, wide eyes, open mouth
            if features['eyebrow_eye_distance'] > 25 and features['eye_opening'] > 15:
                emotions['surprised'] = 0.7
            else:
                emotions['surprised'] = 0.1
            
            # Angry: lowered eyebrows, narrowed eyes
            if features['eyebrow_eye_distance'] < 15 and features['eye_opening'] < 8:
                emotions['angry'] = 0.6
            else:
                emotions['angry'] = 0.1
            
            # Neutral: default
            emotions['neutral'] = 0.3
            emotions['fearful'] = 0.05
            emotions['disgusted'] = 0.05
            
            # Normalize probabilities
            total = sum(emotions.values())
            if total > 0:
                emotions = {k: v / total for k, v in emotions.items()}
            
            return emotions
            
        except Exception as e:
            logger.error(f"Error detecting emotion: {e}")
            return {'neutral': 1.0}
    
    @staticmethod
    def detect_emotion_from_image(image: np.ndarray, face_location: Optional[Tuple] = None) -> Dict[str, any]:
        """
        Detect emotion from image
        
        Args:
            image: Image as numpy array
            face_location: Optional face location tuple (top, right, bottom, left)
            
        Returns:
            Dictionary with emotion detection results
        """
        try:
            # Detect face if location not provided
            if face_location is None:
                face_locations = face_recognition.face_locations(image, model='hog')
                if not face_locations:
                    return {
                        'emotions': {'neutral': 1.0},
                        'dominant_emotion': 'neutral',
                        'confidence': 0.0
                    }
                face_location = face_locations[0]
            
            # Get facial landmarks
            face_landmarks_list = face_recognition.face_landmarks(image, [face_location])
            
            if not face_landmarks_list:
                return {
                    'emotions': {'neutral': 1.0},
                    'dominant_emotion': 'neutral',
                    'confidence': 0.0
                }
            
            face_landmarks = face_landmarks_list[0]
            
            # Detect emotions
            emotions = EmotionDetectionService.detect_emotion_from_landmarks(face_landmarks)
            
            # Find dominant emotion
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])
            
            return {
                'emotions': emotions,
                'dominant_emotion': dominant_emotion[0],
                'confidence': dominant_emotion[1],
                'face_location': face_location
            }
            
        except Exception as e:
            logger.error(f"Error in emotion detection: {e}")
            return {
                'emotions': {'neutral': 1.0},
                'dominant_emotion': 'neutral',
                'confidence': 0.0
            }
    
    @staticmethod
    def detect_emotions_multiple_faces(image: np.ndarray) -> List[Dict[str, any]]:
        """
        Detect emotions for multiple faces in image
        
        Args:
            image: Image as numpy array
            
        Returns:
            List of emotion detection results for each face
        """
        try:
            face_locations = face_recognition.face_locations(image, model='hog')
            results = []
            
            for face_location in face_locations:
                result = EmotionDetectionService.detect_emotion_from_image(image, face_location)
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error detecting multiple face emotions: {e}")
            return []

