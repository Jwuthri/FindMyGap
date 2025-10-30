"""
User Review Feedback repository for managing user access to reviews.
"""

from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app import get_logger
from app.database.models.user_review_feedback import UserReviewFeedbackTable
from app.database.models.review import ReviewTable

logger = get_logger(__name__)


class UserReviewFeedbackRepository:
    """Repository for UserReviewFeedback model operations."""

    def _log_prefix(self, user_id: Optional[int] = None, review_id: Optional[int] = None) -> str:
        """Generate log prefix following team standards."""
        return f"[UserReviewFeedbackRepository] | [user_id={user_id or 'None'}] | [review_id={review_id or 'None'}]"

    def create(
        self,
        db: Session,
        user_id: int,
        review_id: int,
        is_owner: bool = False,
        access_type: Optional[str] = None,
        notes: Optional[str] = None
    ) -> UserReviewFeedbackTable:
        """
        Grant a user access to a review.
        
        Args:
            db: Database session
            user_id: User ID
            review_id: Review ID
            is_owner: Whether the user owns this review
            access_type: How the user got access (e.g., "uploaded", "shared", "platform")
            notes: Optional notes about this relationship
            
        Returns:
            Created UserReviewFeedback record
        """
        user_review = UserReviewFeedbackTable(
            user_id=user_id,
            review_id=review_id,
            is_owner=is_owner,
            access_type=access_type,
            notes=notes
        )
        db.add(user_review)
        db.commit()
        db.refresh(user_review)
        logger.info(f"{self._log_prefix(user_id, review_id)} | Granted user access to review")
        return user_review

    def get_by_id(self, db: Session, user_review_id: int) -> Optional[UserReviewFeedbackTable]:
        """Get user review feedback by ID."""
        return db.query(UserReviewFeedbackTable).filter(
            UserReviewFeedbackTable.id == user_review_id
        ).first()

    def get_user_reviews(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReviewTable]:
        """
        Get all reviews a user has access to.
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Review objects the user has access to
        """
        return (
            db.query(ReviewTable)
            .join(UserReviewFeedbackTable, ReviewTable.id == UserReviewFeedbackTable.review_id)
            .filter(UserReviewFeedbackTable.user_id == user_id)
            .order_by(ReviewTable.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_user_owned_reviews(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReviewTable]:
        """
        Get all reviews owned by a user.
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Review objects owned by the user
        """
        return (
            db.query(ReviewTable)
            .join(UserReviewFeedbackTable, ReviewTable.id == UserReviewFeedbackTable.review_id)
            .filter(
                and_(
                    UserReviewFeedbackTable.user_id == user_id,
                    UserReviewFeedbackTable.is_owner == True
                )
            )
            .order_by(ReviewTable.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def check_user_access(self, db: Session, user_id: int, review_id: int) -> bool:
        """
        Check if a user has access to a specific review.
        
        Args:
            db: Database session
            user_id: User ID
            review_id: Review ID
            
        Returns:
            True if user has access, False otherwise
        """
        exists = db.query(UserReviewFeedbackTable).filter(
            and_(
                UserReviewFeedbackTable.user_id == user_id,
                UserReviewFeedbackTable.review_id == review_id
            )
        ).first()
        return exists is not None

    def grant_access(
        self,
        db: Session,
        user_id: int,
        review_id: int,
        access_type: str = "shared"
    ) -> Optional[UserReviewFeedbackTable]:
        """
        Grant a user access to a review if they don't already have it.
        
        Args:
            db: Database session
            user_id: User ID
            review_id: Review ID
            access_type: Type of access being granted
            
        Returns:
            UserReviewFeedback record or None if already exists
        """
        if self.check_user_access(db, user_id, review_id):
            logger.info(f"{self._log_prefix(user_id, review_id)} | User already has access")
            return None
        
        return self.create(db, user_id, review_id, is_owner=False, access_type=access_type)

    def revoke_access(self, db: Session, user_id: int, review_id: int) -> bool:
        """
        Revoke a user's access to a review.
        
        Args:
            db: Database session
            user_id: User ID
            review_id: Review ID
            
        Returns:
            True if access was revoked, False if no access existed
        """
        user_review = db.query(UserReviewFeedbackTable).filter(
            and_(
                UserReviewFeedbackTable.user_id == user_id,
                UserReviewFeedbackTable.review_id == review_id
            )
        ).first()
        
        if user_review:
            db.delete(user_review)
            db.commit()
            logger.info(f"{self._log_prefix(user_id, review_id)} | Revoked user access to review")
            return True
        return False

    def bulk_grant_access(
        self,
        db: Session,
        user_id: int,
        review_ids: List[int],
        is_owner: bool = False,
        access_type: Optional[str] = None
    ) -> int:
        """
        Grant a user access to multiple reviews at once.
        
        Args:
            db: Database session
            user_id: User ID
            review_ids: List of review IDs
            is_owner: Whether the user owns these reviews
            access_type: How the user got access
            
        Returns:
            Number of new access grants created
        """
        count = 0
        for review_id in review_ids:
            if not self.check_user_access(db, user_id, review_id):
                self.create(db, user_id, review_id, is_owner, access_type)
                count += 1
        
        logger.info(f"{self._log_prefix(user_id)} | Granted access to {count} reviews")
        return count

    def get_review_users(
        self,
        db: Session,
        review_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserReviewFeedbackTable]:
        """
        Get all users who have access to a specific review.
        
        Args:
            db: Database session
            review_id: Review ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of UserReviewFeedback records
        """
        return (
            db.query(UserReviewFeedbackTable)
            .filter(UserReviewFeedbackTable.review_id == review_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_user_reviews(self, db: Session, user_id: int) -> int:
        """
        Count total reviews a user has access to.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Total count of accessible reviews
        """
        return db.query(UserReviewFeedbackTable).filter(
            UserReviewFeedbackTable.user_id == user_id
        ).count()
