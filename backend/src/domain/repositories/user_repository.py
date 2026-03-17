"""
User Repository - Data access layer for User model
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import uuid

from src.domain.models.user import User, UserRole


class UserRepository:
    """User repository for database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def create(self, user: User) -> User:
        """Create new user"""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update(self, user: User) -> User:
        """Update existing user"""
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user: User) -> None:
        """Soft delete user"""
        user.deleted_at = datetime.utcnow()
        self.db.commit()
    
    def increment_failed_login(self, user: User) -> User:
        """Increment failed login attempts"""
        user.failed_login_attempts += 1
        return self.update(user)
    
    def reset_failed_login(self, user: User) -> User:
        """Reset failed login attempts"""
        user.failed_login_attempts = 0
        user.is_locked = False
        user.locked_until = None
        return self.update(user)
    
    def lock_account(self, user: User, locked_until: datetime) -> User:
        """Lock user account"""
        user.is_locked = True
        user.locked_until = locked_until
        return self.update(user)
    
    def update_last_login(self, user: User) -> User:
        """Update last login timestamp"""
        user.last_login_at = datetime.utcnow()
        return self.update(user)
    
    def get_by_refresh_token(self, token_hash: str) -> Optional[User]:
        """Get user by refresh token hash"""
        return self.db.query(User).filter(User.refresh_token == token_hash).first()
    
    def get_by_password_reset_token(self, token_hash: str) -> Optional[User]:
        """Get user by password reset token hash"""
        return self.db.query(User).filter(User.password_reset_token == token_hash).first()
