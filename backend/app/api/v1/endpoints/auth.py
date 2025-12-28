"""Authentication endpoints with OAuth2PasswordRequestForm"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, UTC
from typing import List
import logging

from app.db.base import get_db
from app.db.redis import get_redis
from app.schemas.auth import (
    UserCreate, UserResponse, Token, TokenRefresh, LoginHistoryResponse, UserActivityResponse,
    PasswordResetRequest, PasswordReset
)
from app.models.user import User, LoginHistory, UserActivity
from app.core import security
from app.core.config import settings
from app.core.deps import get_current_active_user

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
):
    """
    OAuth2 compatible token login
    
    Uses standard OAuth2 password flow (RFC 6749)
    - Accepts application/x-www-form-urlencoded
    - Returns access_token and refresh_token
    - Compatible with Swagger UI "Authorize" button
    """
    # Get username and password from form_data
    username = form_data.username  # ← CHANGED
    password = form_data.password  # ← CHANGED
    
    # Authenticate user
    user = db.query(User).filter(User.username == username).first()
    
    if not user or not security.verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token = security.create_refresh_token(data={"sub": str(user.id)})
    
    # Store refresh token in Redis
    await redis.setex(
        f"refresh_token:{user.id}",
        settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        refresh_token
    )
    
    # Log login
    ip_address = request.client.host if request else None
    user_agent = request.headers.get("user-agent") if request else None
    
    login_record = LoginHistory(
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
        success=True
    )
    db.add(login_record)
    
    # Update last login
    user.last_login = datetime.now(UTC)
    db.commit()
    
    # Return token in OAuth2 format
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    - **username**: Unique username (3-50 characters)
    - **email**: Valid email address
    - **password**: Strong password (min 8 characters)
    """
    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = security.get_password_hash(user_data.password)
    
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    """
    # Verify refresh token
    try:
        payload = security.decode_token(token_data.refresh_token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if refresh token is in Redis
    stored_token = await redis.get(f"refresh_token:{user_id}")
    if not stored_token or stored_token.decode() != token_data.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revoked or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = security.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    new_refresh_token = security.create_refresh_token(data={"sub": str(user.id)})
    
    # Update refresh token in Redis
    await redis.setex(
        f"refresh_token:{user.id}",
        settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        new_refresh_token
    )
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    redis = Depends(get_redis)
):
    """
    Logout current user (revoke refresh token)
    """
    # Delete refresh token from Redis
    await redis.delete(f"refresh_token:{current_user.id}")
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information
    """
    return current_user


@router.get("/history", response_model=List[LoginHistoryResponse])
def get_login_history(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get login history for current user
    
    - **limit**: Number of records to return (default: 10, max: 100)
    """
    if limit > 100:
        limit = 100
    
    history = db.query(LoginHistory).filter(
        LoginHistory.user_id == current_user.id
    ).order_by(LoginHistory.timestamp.desc()).limit(limit).all()
    
    return history


@router.get("/activity", response_model=List[UserActivityResponse])
def get_user_activity(
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get recent activity for current user
    
    - **limit**: Number of records to return (default: 20, max: 100)
    """
    if limit > 100:
        limit = 100
    
    activity = db.query(UserActivity).filter(
        UserActivity.user_id == current_user.id
    ).order_by(UserActivity.timestamp.desc()).limit(limit).all()
    
    return activity


@router.post("/forgot-password")
async def forgot_password(
    request_data: PasswordResetRequest,
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
):
    """
    Request password reset
    
    Sends a password reset token to the user's email address.
    For security, always returns success even if email doesn't exist.
    """
    user = db.query(User).filter(User.email == request_data.email).first()
    
    if user:
        # Generate reset token (valid for 1 hour)
        reset_token = security.create_password_reset_token(user.id)
        
        # Store token in Redis (expires in 1 hour)
        await redis.setex(
            f"password_reset:{reset_token}",
            3600,  # 1 hour
            str(user.id)
        )
        
        # TODO: Send email with reset link
        # For now, we'll just log it (in production, use email service)
        logger.info(f"Password reset token for {user.email}: {reset_token}")
        # In production: send_email(user.email, reset_token)
    
    # Always return success for security (don't reveal if email exists)
    return {"message": "If an account with that email exists, a password reset link has been sent."}


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
):
    """
    Reset password using reset token
    
    - **token**: Password reset token from email
    - **new_password**: New password (min 8 characters)
    """
    # Verify token
    try:
        user_id_str = await redis.get(f"password_reset:{reset_data.token}")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        user_id = int(user_id_str.decode())
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.hashed_password = security.get_password_hash(reset_data.new_password)
    user.failed_login_attempts = 0  # Reset failed attempts
    db.commit()
    
    # Delete reset token (one-time use)
    await redis.delete(f"password_reset:{reset_data.token}")
    
    return {"message": "Password has been successfully reset"}
