"""
Pydantic schemas for dataset models.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class UserDatasetSchema(BaseModel):
    """Schema for user-uploaded dataset."""
    
    id: int = Field(..., description="Dataset ID")
    user_id: int = Field(..., description="User ID who owns this dataset")
    table_name: str = Field(..., description="Database table name")
    original_filename: Optional[str] = Field(None, description="Original uploaded filename")
    description: Optional[str] = Field(None, description="Dataset description")
    column_metadata: Optional[Dict[str, Any]] = Field(None, description="Column metadata dict")
    row_count: int = Field(0, description="Number of rows in dataset")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user_123",
                "table_name": "user_123_conversations",
                "original_filename": "conversations.csv",
                "description": "Customer support conversations",
                "column_metadata": {"key_fields": ["conversation_id"]},
                "row_count": 1500,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class UserDatasetCreateSchema(BaseModel):
    """Schema for creating a user dataset."""
    
    user_id: int = Field(..., description="User ID who owns this dataset")
    table_name: str = Field(..., description="Database table name")
    original_filename: Optional[str] = Field(None, description="Original uploaded filename")
    description: Optional[str] = Field(None, description="Dataset description")
    column_metadata: Optional[Dict[str, Any]] = Field(None, description="Column metadata dict")
    row_count: int = Field(0, description="Number of rows in dataset")


class PlatformDatasetSchema(BaseModel):
    """Schema for platform-wide dataset."""
    
    id: int = Field(..., description="Dataset ID")
    table_name: str = Field(..., description="Database table name")
    collection_name: str = Field(..., description="Collection name")
    description: Optional[str] = Field(None, description="Dataset description")
    data_category: Optional[str] = Field(None, description="Data category")
    field_descriptions: Optional[Dict[str, str]] = Field(None, description="Field descriptions dict")
    key_fields: Optional[List[str]] = Field(None, description="List of key fields")
    embedding_fields: Optional[List[str]] = Field(None, description="List of embedding fields")
    primary_text_field: Optional[str] = Field(None, description="Primary text field for semantic search")
    combined_text_fields: Optional[List[str]] = Field(None, description="List of combined text fields")
    estimated_use_cases: Optional[List[str]] = Field(None, description="List of use cases")
    potential_joins: Optional[List[str]] = Field(None, description="List of potential joins")
    data_quality_notes: Optional[str] = Field(None, description="Data quality notes")
    row_count: int = Field(0, description="Number of rows in dataset")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "table_name": "reviews_feedback",
                "collection_name": "Customer Reviews",
                "description": "Customer reviews from various platforms",
                "data_category": "feedback",
                "field_descriptions": {"rating": "Rating score 1-5"},
                "key_fields": ["id", "company"],
                "embedding_fields": ["text"],
                "primary_text_field": "text",
                "combined_text_fields": ["text", "author"],
                "estimated_use_cases": ["sentiment analysis", "product feedback"],
                "potential_joins": [],
                "data_quality_notes": "High quality, verified reviews",
                "row_count": 5000,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class PlatformDatasetCreateSchema(BaseModel):
    """Schema for creating a platform dataset."""
    
    table_name: str = Field(..., description="Database table name")
    collection_name: str = Field(..., description="Collection name")
    metadata: Dict[str, Any] = Field(..., description="Dataset metadata from LLM agent")
