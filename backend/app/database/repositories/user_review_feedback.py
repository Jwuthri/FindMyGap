"""
User Review Feedback repository for managing user's review copies.
"""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import distinct

from app import get_logger
from app.database.models.user_review_feedback import UserReviewFeedbackTable

logger = get_logger(__name__)


class UserReviewFeedbackRepository:
    """Repository for UserReviewFeedback model operations."""

    def _log_prefix(self, user_id: Optional[int] = None) -> str:
        """Generate log prefix following team standards."""
        return f"[UserReviewFeedbackRepository] | [user_id={user_id or 'None'}]"

    def create(
        self,
        db: Session,
        user_id: int,
        company_name: str,
        text: str,
        rating: Optional[int] = None,
        category: Optional[str] = None,
        source: Optional[str] = None,
        date: Optional[str] = None,
        author: Optional[str] = None
    ) -> UserReviewFeedbackTable:
        """
        Create a review copy for a user.
        
        Args:
            db: Database session
            user_id: User ID
            company_name: Company name
            text: Review text
            rating: Rating
            category: Category
            source: Source
            date: Date
            author: Author
            
        Returns:
            Created UserReviewFeedback record
        """
        user_review = UserReviewFeedbackTable(
            user_id=user_id,
            company_name=company_name,
            text=text,
            rating=rating,
            category=category,
            source=source,
            date=date,
            author=author
        )
        db.add(user_review)
        db.commit()
        db.refresh(user_review)
        logger.info(f"{self._log_prefix(user_id)} | Created review for {company_name}")
        return user_review

    def get_by_id(self, db: Session, review_id: int) -> Optional[UserReviewFeedbackTable]:
        """Get user review by ID."""
        return db.query(UserReviewFeedbackTable).filter(
            UserReviewFeedbackTable.id == review_id
        ).first()

    def get_user_reviews(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserReviewFeedbackTable]:
        """
        Get all reviews a user has access to.
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of UserReviewFeedback objects
        """
        return (
            db.query(UserReviewFeedbackTable)
            .filter(UserReviewFeedbackTable.user_id == user_id)
            .order_by(UserReviewFeedbackTable.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_company(
        self,
        db: Session,
        user_id: int,
        company_name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserReviewFeedbackTable]:
        """
        Get user's reviews for a specific company.
        
        Args:
            db: Database session
            user_id: User ID
            company_name: Company name
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of UserReviewFeedback objects
        """
        return (
            db.query(UserReviewFeedbackTable)
            .filter(
                UserReviewFeedbackTable.user_id == user_id,
                UserReviewFeedbackTable.company_name == company_name
            )
            .order_by(UserReviewFeedbackTable.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete(self, db: Session, review_id: int) -> bool:
        """
        Delete a user review.
        
        Args:
            db: Database session
            review_id: Review ID
            
        Returns:
            True if deleted, False otherwise
        """
        review = self.get_by_id(db, review_id)
        if review:
            db.delete(review)
            db.commit()
            logger.info(f"{self._log_prefix(review.user_id)} | Deleted review {review_id}")
            return True
        return False

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

    def get_user_companies(self, db: Session, user_id: int) -> List[str]:
        """
        Get all companies that a user has reviews for.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of company names
        """
        results = (
            db.query(distinct(UserReviewFeedbackTable.company_name))
            .filter(UserReviewFeedbackTable.user_id == user_id)
            .order_by(UserReviewFeedbackTable.company_name)
            .all()
        )
        
        return [name[0] for name in results]
