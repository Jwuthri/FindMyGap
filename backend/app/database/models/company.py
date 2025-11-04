"""
Company model.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from ..base import Base


class CompanyTable(Base):
    """Company model."""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    industry = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name})>"
