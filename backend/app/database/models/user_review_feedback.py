"""
User Review Feedback model - junction table for user access to reviews.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship

from ..base import Base


class UserReviewFeedbackTable(Base):
    """Junction table linking users to reviews they have access to."""
    __tablename__ = "user_review_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    review_id = Column(Integer, ForeignKey('reviews_feedback.id'), nullable=False, index=True)
    
    # Optional: Track if user added this review or it was shared with them
    is_owner = Column(Boolean, default=False, nullable=False)
    
    # Optional: Track how the user got access (e.g., "uploaded", "shared", "platform")
    access_type = Column(String(50), nullable=True)
    
    # Optional: Additional metadata about this user-review relationship
    notes = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("UserTable", backref="user_reviews")
    review = relationship("ReviewTable", backref="user_access")

    def __repr__(self):
        return f"<UserReviewFeedback(id={self.id}, user_id={self.user_id}, review_id={self.review_id})>"
