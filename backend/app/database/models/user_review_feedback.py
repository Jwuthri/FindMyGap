"""
User Review Feedback model - user's copy of reviews they have access to.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from ..base import Base


class UserReviewFeedbackTable(Base):
    """User's copy of reviews they have access to."""
    __tablename__ = "user_review_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    category = Column(String, nullable=True)
    rating = Column(Integer, nullable=True)
    text = Column(Text, nullable=False)
    source = Column(String, nullable=True)
    date = Column(DateTime, nullable=True)
    author = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<UserReviewFeedback(id={self.id}, user_id={self.user_id}, company_name={self.company_name})>"
