from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserUpdate,
    UserResponse,
    Token,
    TokenRefreshRequest,
    TokenRefreshResponse
)
from app.services.auth_service import AuthService
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.core.exceptions import AuthenticationException, BadRequestException
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account."""
    return AuthService.register_user(db, user_in)

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate credentials and return access & refresh tokens."""
    user = AuthService.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise AuthenticationException("Incorrect email or password")
    
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/refresh-token", response_model=TokenRefreshResponse)
def refresh_token(payload: TokenRefreshRequest, db: Session = Depends(get_db)):
    """Refresh the access token using a valid refresh token."""
    decoded = decode_token(payload.refresh_token)
    if not decoded or decoded.get("type") != "refresh":
        raise AuthenticationException("Invalid or expired refresh token")
        
    user_id = decoded.get("sub")
    if not user_id:
        raise AuthenticationException("Invalid refresh token payload")
        
    user = AuthService.get_user_by_id(db, user_id)
    if not user:
        raise AuthenticationException("User not found")
        
    access_token = create_access_token(user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve logged-in user profile information."""
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_profile(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update profile details of the currently authenticated user."""
    return AuthService.update_user(db, current_user, user_in)
