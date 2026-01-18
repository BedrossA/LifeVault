"""Logging configuration for the application"""
import logging
import logging.handlers
import sys
from pathlib import Path
from app.core.config import settings
import json
from datetime import datetime
from typing import Optional

class StructuredLogger:
    """Structured JSON logging for better log analysis"""
    
    @staticmethod
    def log_api_call(
        endpoint: str,
        method: str,
        user_id: Optional[int],
        status_code: int,
        duration_ms: float,
        error: Optional[str] = None
    ):
        """Log API call with structured data"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "api_call",
            "endpoint": endpoint,
            "method": method,
            "user_id": user_id,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "error": error
        }
        
        logger = logging.getLogger("api")
        if error:
            logger.error(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))

def setup_logging():
    """Configure application logging"""
    
    # Create logger
    logger = logging.getLogger("lifevault")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # File handler with rotation
    log_file = Path(settings.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.handlers.RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Log startup
    logger.info(f"Logging initialized - Level: {settings.LOG_LEVEL}")
    logger.info(f"Log file: {settings.LOG_FILE}")
    
    return logger

# Initialize logging and export logger
logger = setup_logging()
