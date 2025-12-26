"""Authentication service"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, UTC
from typing import Optional
import logging
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.token import Token
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.services.cache_service import CacheService
from app.services.mongo_service import MongoService
from app.core.config import settings

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email or username already registered")
        new_user = User(email=user_data.email, username=user_data.username.lower(),
                       full_name=user_data.full_name, hashed_password=get_password_hash(user_data.password))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"User created: {new_user.username}")
        return new_user
    
    @staticmethod
    async def authenticate_user(db: Session, username: str, password: str, 
                               ip_address: str, user_agent: str) -> Optional[User]:
        user = db.query(User).filter(User.username == username.lower()).first()
        if not user:
            await MongoService.log_login_attempt(0, username, ip_address, user_agent, False, "User not found")
            return None
        if user.failed_login_attempts >= 5:
            raise HTTPException(status_code=403, detail="Account locked")
        if not verify_password(password, user.hashed_password):
            user.failed_login_attempts += 1
            db.commit()
            await MongoService.log_login_attempt(user.id, username, ip_address, user_agent, False, "Invalid password")
            return None
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account inactive")
        user.failed_login_attempts = 0
        user.last_login = datetime.now(UTC)
        user.last_login_ip = ip_address
        db.commit()
        await MongoService.log_login_attempt(user.id, username, ip_address, user_agent, True)
        return user
    
    @staticmethod
    async def create_tokens(user: User) -> Token:
        token_data = {"sub": str(user.id), "username": user.username, "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        await CacheService.cache_session(refresh_token, 
            {"user_id": user.id, "username": user.username, "email": user.email},
            ttl=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)
        return Token(access_token=access_token, refresh_token=refresh_token, 
                    token_type="bearer", expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    
    @staticmethod
    async def refresh_access_token(refresh_token: str) -> Token:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        cached_session = await CacheService.get_session(refresh_token)
        if not cached_session:
            raise HTTPException(status_code=401, detail="Session expired")
        token_data = {"sub": str(cached_session["user_id"]), 
                     "username": cached_session["username"], "email": cached_session["email"]}
        new_access_token = create_access_token(token_data)
        return Token(access_token=new_access_token, refresh_token=refresh_token, 
                    token_type="bearer", expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    
    @staticmethod
    async def logout(refresh_token: str, user_id: int, ip_address: str):
        await CacheService.invalidate_session(refresh_token)
        await MongoService.log_activity(user_id, "logout", "auth", ip_address)
        logger.info(f"User logged out: {user_id}")
