from app.db.base import Base, engine
from app.models.user import User
from app.models.session import Session
import logging

logger = logging.getLogger(__name__)

def init_db():
    """Initialize database - create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise
