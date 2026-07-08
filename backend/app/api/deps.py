from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.security import decode_token
from app.core.exceptions import AuthenticationException
from app.services.auth_service import AuthService
from app.models.user import User

# Use HTTPBearer to parse token from 'Authorization: Bearer <token>' header
reusable_oauth2 = HTTPBearer()

def get_current_user(
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(reusable_oauth2)
) -> User:
    """Validate JWT token and return the authenticated user."""
    payload = decode_token(token.credentials)
    if not payload or payload.get("type") != "access":
        raise AuthenticationException("Invalid token or token expired")
    
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationException("Token sub missing")
        
    user = AuthService.get_user_by_id(db, user_id)
    if not user:
        raise AuthenticationException("User does not exist")
    return user
