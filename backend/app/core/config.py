"""Application configuration using Pydantic settings"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "LifeVault"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str
    API_V1_PREFIX: str = "/api/v1"
    
    # PostgreSQL
    DATABASE_URL: str
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "lifevault"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: str = ""
    REDIS_MAX_CONNECTIONS: int = 50
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    PASSWORD_MIN_LENGTH: int = 8
    
    # Rate Limiting
    RATE_LIMIT_LOGIN: int = 5
    RATE_LIMIT_WINDOW: int = 60
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Face Recognition
    FACE_DETECTION_METHOD: str = "hog"
    FACE_RECOGNITION_TOLERANCE: float = 0.6
    MAX_FACES_PER_USER: int = 5
    FACE_ENCODING_MODEL: str = "large"
    
    # File Storage
    UPLOAD_DIR: str = "./data/uploads"
    FACE_DATA_DIR: str = "./data/face_data"
    MAX_UPLOAD_SIZE: int = 10485760
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Camera Settings
    CAMERA_RESOLUTION_WIDTH: int = 2592
    CAMERA_RESOLUTION_HEIGHT: int = 1944
    CAMERA_FRAMERATE: int = 15
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/lifevault.log"
    LOG_MAX_BYTES: int = 10485760
    LOG_BACKUP_COUNT: int = 5
    
    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # This allows extra fields from .env
    )
    # Face Recognition Advanced Settings
    FACE_MIN_QUALITY_THRESHOLD: float = 0.5  # Minimum quality to accept enrollment
    FACE_ADAPTIVE_THRESHOLD_ENABLED: bool = True  # Enable per-user thresholds
    FACE_HIGH_QUALITY_THRESHOLD: float = 0.5  # Threshold for high-quality encodings
    FACE_LOW_QUALITY_THRESHOLD: float = 0.7  # Threshold for low-quality encodings
    
    # Multi-face detection
    FACE_MAX_FACES_IN_FRAME: int = 10  # Maximum faces to detect in one image
    FACE_ENABLE_MULTI_DETECTION: bool = True  # Allow multiple face detection
    
    # WebSocket settings
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    WS_MAX_FRAME_SIZE: int = 1024 * 1024  # 1MB
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    def ensure_directories(self):
        Path(self.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.FACE_DATA_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_directories()
