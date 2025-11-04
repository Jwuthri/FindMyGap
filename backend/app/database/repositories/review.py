"""
Review repository for customer feedback operations.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app import get_logger
from app.database.models.review import ReviewTable

logger = get_logger(__name__)


class ReviewRepository:
    """Repository for Review model operations."""

    def _log_prefix(self, user_id: Optional[str] = None, company_id: Optional[str] = None) -> str:
        """Generate log prefix following team standards."""
        return f"[ReviewRepository] | [user_id={user_id or 'None'}] | [company_id={company_id or 'None'}]"

    def create(
        self,
        db: Session,
        company_name: str,
        text: str,
        rating: Optional[int] = None,
        category: Optional[str] = None,
        source: Optional[str] = None,
        date: Optional[str] = None,
        author: Optional[str] = None
    ) -> ReviewTable:
        """Create a new review."""
        review = ReviewTable(
            company_name=company_name,
            text=text,
            rating=rating,
            category=category,
            source=source,
            date=date,
            author=author
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        logger.info(f"{self._log_prefix()} | Created review for {company_name}")
        return review

    def get_by_id(self, db: Session, review_id: int) -> Optional[ReviewTable]:
        """Get review by ID."""
        return db.query(ReviewTable).filter(ReviewTable.id == review_id).first()

    def get_by_company(
        self,
        db: Session,
        company_name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReviewTable]:
        """Get all reviews for a company."""
        return (
            db.query(ReviewTable)
            .filter(ReviewTable.company_name == company_name)
            .order_by(ReviewTable.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ReviewTable]:
        """Get all reviews with pagination."""
        return (
            db.query(ReviewTable)
            .order_by(ReviewTable.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete(self, db: Session, review_id: int) -> bool:
        """Delete review by ID."""
        review = self.get_by_id(db, review_id)
        if review:
            db.delete(review)
            db.commit()
            logger.info(f"{self._log_prefix()} | Deleted review: {review_id}")
            return True
        return False
