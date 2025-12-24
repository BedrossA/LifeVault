from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.models.user import User
from app.models.session import Session as SessionModel
from app.schemas.user import UserCreate, UserLogin
from app.core.security import (
    verify_password, 
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)

logger = logging.getLogger(__name__)

class AuthService:
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        
        # Check if user exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            if existing_user.email == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New user created: {new_user.username}")
        return new_user
    
    @staticmethod
    def authenticate_user(
        db: Session, 
        username: str, 
        password: str,
        ip_address: Optional[str] = None
    ) -> Optional[User]:
        """Authenticate user with username and password"""
        
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            logger.warning(f"Login attempt with non-existent username: {username}")
            return None
        
        # Check if account is locked
        if user.failed_login_attempts >= 5:
            logger.warning(f"Account locked due to failed attempts: {username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account locked due to too many failed login attempts. Please contact support."
            )
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            user.failed_login_attempts += 1
            db.commit()
            logger.warning(f"Failed login attempt for user: {username}")
            return None
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        user.last_login_ip = ip_address
        db.commit()
        
        logger.info(f"Successful login: {username}")
        return user
    
    @staticmethod
    def create_session(
        db: Session,
        user: User,
        ip_address: str,
        user_agent: str,
        device_name: Optional[str] = None
    ) -> dict:
        """Create authentication session with tokens"""
        
        # Create tokens
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Create session record
        expires_at = datetime.utcnow() + timedelta(days=7)
        session = SessionModel(
            user_id=user.id,
            refresh_token=refresh_token,
            access_token=access_token,
            ip_address=ip_address,
            user_agent=user_agent,
            device_name=device_name,
            expires_at=expires_at
        )
        
        db.add(session)
        db.commit()
        
        logger.info(f"Session created for user: {user.username}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800  # 30 minutes in seconds
        }
    
    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        
        # Verify refresh token
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Check if session exists and is active
        session = db.query(SessionModel).filter(
            SessionModel.refresh_token == refresh_token,
            SessionModel.is_active == True
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session not found or expired"
            )
        
        # Check if session expired
        if session.expires_at < datetime.utcnow():
            session.is_active = False
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired"
            )
        
        # Get user
        user = db.query(User).filter(User.id == session.user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email
        }
        new_access_token = create_access_token(token_data)
        
        # Update session
        session.access_token = new_access_token
        session.last_activity = datetime.utcnow()
        db.commit()
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 1800
        }
    
    @staticmethod
    def logout(db: Session, refresh_token: str) -> bool:
        """Logout user by invalidating session"""
        
        session = db.query(SessionModel).filter(
            SessionModel.refresh_token == refresh_token
        ).first()
        
        if session:
            session.is_active = False
            db.commit()
            logger.info(f"User logged out: session_id={session.session_id}")
            return True
        
        return False
