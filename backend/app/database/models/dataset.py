"""
Dataset models for FindMyGap.

Handles both user-uploaded datasets and platform-wide datasets.
"""

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from ..base import Base


class DatasetTypeEnum(str, enum.Enum):
    """Dataset type classification."""
    USER_UPLOADED = "user_uploaded"
    PLATFORM = "platform"
    EXTERNAL = "external"


class UserDatasetTable(Base):
    """User-uploaded dataset metadata."""
    __tablename__ = "user_datasets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    table_name = Column(String, unique=True, nullable=False, index=True)
    original_filename = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    column_metadata = Column(JSON, nullable=True)  # JSON dict with column info
    row_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<UserDataset(id={self.id}, table_name={self.table_name}, user_id={self.user_id})>"


class PlatformDatasetTable(Base):
    """Platform-wide dataset metadata available to all users."""
    __tablename__ = "platform_datasets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String, unique=True, nullable=False, index=True)
    collection_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    data_category = Column(String, nullable=True)
    
    # Metadata fields (stored as JSON)
    field_descriptions = Column(JSON, nullable=True)  # JSON dict
    key_fields = Column(JSON, nullable=True)  # JSON array
    embedding_fields = Column(JSON, nullable=True)  # JSON array
    primary_text_field = Column(String, nullable=True)
    combined_text_fields = Column(JSON, nullable=True)  # JSON array
    estimated_use_cases = Column(JSON, nullable=True)  # JSON array
    potential_joins = Column(JSON, nullable=True)  # JSON array
    data_quality_notes = Column(Text, nullable=True)
    
    row_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<PlatformDataset(id={self.id}, table_name={self.table_name}, collection_name={self.collection_name})>"
