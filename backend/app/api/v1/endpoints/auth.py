"""Authentication API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Any

from app.db.base import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.token import Token, TokenRefresh
from app.services.auth_service import AuthService
from app.core.deps import get_current_active_user, rate_limit_login
from app.models.user import User
from app.services.mongo_service import MongoService

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> Any:
    """Register a new user"""
    user = AuthService.create_user(db, user_data)
    return user

@router.post("/login", response_model=Token, dependencies=[Depends(rate_limit_login)])
async def login(request: Request, credentials: UserLogin, db: Session = Depends(get_db)) -> Any:
    """Login user and create session"""
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")
    
    user = await AuthService.authenticate_user(db, credentials.username, credentials.password, ip_address, user_agent)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    tokens = await AuthService.create_tokens(user)
    await MongoService.log_activity(user.id, "login", "auth", ip_address, metadata={"user_agent": user_agent})
    
    return tokens

@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh) -> Any:
    """Refresh access token"""
    tokens = await AuthService.refresh_access_token(token_data.refresh_token)
    return tokens

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(request: Request, token_data: TokenRefresh, current_user: User = Depends(get_current_active_user)) -> Any:
    """Logout user"""
    ip_address = request.client.host
    await AuthService.logout(token_data.refresh_token, current_user.id, ip_address)
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)) -> Any:
    """Get current user information"""
    return current_user

@router.get("/history", response_model=list)
async def get_login_history(limit: int = 10, current_user: User = Depends(get_current_active_user)) -> Any:
    """Get user's login history"""
    history = await MongoService.get_login_history(current_user.id, limit)
    return history

@router.get("/activity", response_model=list)
async def get_user_activity(limit: int = 20, current_user: User = Depends(get_current_active_user)) -> Any:
    """Get user's activity log"""
    activities = await MongoService.get_user_activities(current_user.id, limit)
    return activities
