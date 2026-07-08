from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import UserRegister, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import BadRequestException, NotFoundException

class AuthService:
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> User:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def register_user(db: Session, user_in: UserRegister) -> User:
        existing_user = AuthService.get_user_by_email(db, user_in.email)
        if existing_user:
            raise BadRequestException("A user with this email already exists.")
        
        user = User(
            email=user_in.email,
            password_hash=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            company=user_in.company,
            role=user_in.role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        user = AuthService.get_user_by_email(db, email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def update_user(db: Session, db_user: User, user_in: UserUpdate) -> User:
        if user_in.email and user_in.email != db_user.email:
            existing = AuthService.get_user_by_email(db, user_in.email)
            if existing:
                raise BadRequestException("A user with this email already exists.")
            db_user.email = user_in.email
        
        if user_in.password:
            db_user.password_hash = get_password_hash(user_in.password)
        if user_in.full_name is not None:
            db_user.full_name = user_in.full_name
        if user_in.company is not None:
            db_user.company = user_in.company
        if user_in.role is not None:
            db_user.role = user_in.role
            
        db.commit()
        db.refresh(db_user)
        return db_user
