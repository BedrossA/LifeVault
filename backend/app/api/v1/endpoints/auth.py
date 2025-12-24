from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Any

from app.db.base import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.token import Token, TokenRefresh
from app.services.auth_service import AuthService
from app.core.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user
    """
    user = AuthService.create_user(db, user_data)
    return user

@router.post("/login", response_model=Token)
def login(
    request: Request,
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    Login user and create session
    """
    # Get client info
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Authenticate user
    user = AuthService.authenticate_user(
        db,
        user_credentials.username,
        user_credentials.password,
        ip_address
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create session and tokens
    tokens = AuthService.create_session(
        db, user, ip_address, user_agent
    )
    
    return tokens

@router.post("/refresh", response_model=Token)
def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token
    """
    tokens = AuthService.refresh_access_token(db, token_data.refresh_token)
    return tokens

@router.post("/logout")
def logout(
    token_data: TokenRefresh,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Logout user
    """
    AuthService.logout(db, token_data.refresh_token)
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user information
    """
    return current_user
