from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "LifeVault"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str
    
    # Database
    DATABASE_URL: str
    
    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # Face Recognition
    FACE_DETECTION_METHOD: str = "hog"
    FACE_RECOGNITION_TOLERANCE: float = 0.6
    MAX_FACES_PER_USER: int = 5
    
    # File Storage
    UPLOAD_DIR: str = "./data/uploads"
    FACE_DATA_DIR: str = "./data/face_data"
    MAX_UPLOAD_SIZE: int = 10485760
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"

settings = Settings()
