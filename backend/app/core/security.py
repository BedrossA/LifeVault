"""Security utilities using native bcrypt directly"""
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.logging import logger
import secrets
import hashlib

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        # Check if hash is valid bcrypt format (should start with $2a$, $2b$, or $2y$)
        if not hashed_password or not hashed_password.startswith(('$2a$', '$2b$', '$2y$')):
            logger.error(f"Invalid password hash format: prefix={hashed_password[:10] if hashed_password else 'None'}")
            return False
        
        # Convert password to bytes for bcrypt
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        logger.error(f"Password verification error: {e}, hash_prefix={hashed_password[:20] if hashed_password else 'None'}")
        return False

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt"""
    try:
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)  # Increase rounds for better security
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"Password hashing error: {e}")
        raise

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access", "iat": datetime.now(UTC)})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh", "iat": datetime.now(UTC), "jti": secrets.token_urlsafe(32)})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        # Adding leeway handles the tiny microsecond differences
        return jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM],
            options={"leeway": 60} 
        )
    except Exception as e:
        # This will print to your RPi console so you can see the EXACT error
        print(f"JWT Decode Error: {str(e)}")
        return None

def create_password_reset_token(user_id: int) -> str:
    """Create a secure password reset token"""
    # Use a URL-safe random token instead of JWT for password reset
    # This is simpler and doesn't require decoding
    return secrets.token_urlsafe(32)