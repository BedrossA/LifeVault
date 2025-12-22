# backend/services/face_recognition_service.py
import face_recognition
import numpy as np
from cryptography.fernet import Fernet

class FaceRecognitionService:
    def __init__(self, encryption_key):
        self.cipher = Fernet(encryption_key)
        
    def extract_face_encoding(self, image):
        """Extract 128D face embedding"""
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        return face_encodings
    
    def encrypt_embedding(self, embedding):
        """Encrypt face embedding before storage"""
        embedding_bytes = embedding.tobytes()
        return self.cipher.encrypt(embedding_bytes)
    
    def compare_faces(self, known_embedding, new_embedding, threshold=0.6):
        """Compare face embeddings"""
        distance = face_recognition.face_distance([known_embedding], new_embedding)
        return distance[0] < threshold