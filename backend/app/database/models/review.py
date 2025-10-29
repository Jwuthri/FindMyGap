"""
Review model for customer feedback.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from ..base import Base


class ReviewTable(Base):
    """Customer review/feedback model."""
    __tablename__ = "reviews_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    category = Column(String, nullable=True)
    rating = Column(Integer, nullable=True)
    text = Column(Text, nullable=False)
    source = Column(String, nullable=True)
    date = Column(DateTime, nullable=True)
    author = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    company = relationship("CompanyTable", back_populates="reviews")

    def __repr__(self):
        return f"<Review(id={self.id}, company_id={self.company_id}, rating={self.rating})>"
