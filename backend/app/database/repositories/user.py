"""
User repository for FindMyGap.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app import get_logger
from app.database.models.user import UserTable

logger = get_logger(__name__)


class UserRepository:
    """Repository for User model operations."""

    def _log_prefix(self, user_id: Optional[str] = None, company_id: Optional[str] = None) -> str:
        """Generate log prefix following team standards."""
        return f"[UserRepository] | [user_id={user_id or 'None'}] | [company_id={company_id or 'None'}]"

    def create(self, db: Session, email: str, username: str = None, full_name: str = None, **kwargs) -> UserTable:
        """Create a new user."""
        user = UserTable(
            email=email,
            username=username,
            full_name=full_name,
            **kwargs
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"{self._log_prefix(user.id)} | Created user with email: {email}")
        return user

    def get_by_id(self, db: Session, user_id: int) -> Optional[UserTable]:
        """Get user by ID."""
        return db.query(UserTable).filter(UserTable.id == user_id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[UserTable]:
        """Get user by email."""
        return db.query(UserTable).filter(UserTable.email == email).first()

    def get_by_username(self, db: Session, username: str) -> Optional[UserTable]:
        """Get user by username."""
        return db.query(UserTable).filter(UserTable.username == username).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[UserTable]:
        """Get all users with pagination."""
        return db.query(UserTable).offset(skip).limit(limit).all()

    def update(self, db: Session, user_id: int, **kwargs) -> Optional[UserTable]:
        """Update user."""
        user = self.get_by_id(db, user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        logger.info(f"{self._log_prefix(user_id)} | Updated user")
        return user

    def delete(self, db: Session, user_id: int) -> bool:
        """Delete user by ID."""
        user = self.get_by_id(db, user_id)
        if user:
            db.delete(user)
            db.commit()
            logger.info(f"{self._log_prefix(user_id)} | Deleted user")
            return True
        return False

    def increment_usage(self, db: Session, user_id: int, requests: int = 1, tokens: int = 0):
        """Increment user usage counters."""
        user = self.get_by_id(db, user_id)
        if user:
            user.total_requests += requests
            user.total_tokens_used += tokens
            user.updated_at = datetime.utcnow()
            db.commit()

    def update_last_login(self, db: Session, user_id: int) -> Optional[UserTable]:
        """Update user's last login timestamp."""
        user = self.get_by_id(db, user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
            logger.info(f"{self._log_prefix(user_id)} | Updated last login")
        return user

    def search_users(self, db: Session, search_term: str, skip: int = 0, limit: int = 50) -> List[UserTable]:
        """Search users by email, username or full name."""
        return (
            db.query(UserTable)
            .filter(
                UserTable.email.ilike(f"%{search_term}%") |
                UserTable.username.ilike(f"%{search_term}%") |
                UserTable.full_name.ilike(f"%{search_term}%")
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
