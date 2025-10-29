"""
Pydantic schemas for review models.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReviewSchema(BaseModel):
    """Schema for customer review."""
    
    id: int = Field(..., description="Review ID")
    company_id: int = Field(..., description="Company ID")
    category: Optional[str] = Field(None, description="Review category")
    rating: Optional[int] = Field(None, description="Rating (1-5)")
    text: str = Field(..., description="Review text content")
    source: Optional[str] = Field(None, description="Review source platform")
    date: Optional[datetime] = Field(None, description="Review date")
    author: Optional[str] = Field(None, description="Review author")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "company": "Spotify",
                "category": "review",
                "rating": 5,
                "text": "Great app, love the features!",
                "source": "app_store",
                "date": "2024-01-15",
                "author": "john_doe",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class ReviewCreateSchema(BaseModel):
    """Schema for creating a review."""
    
    company_id: int = Field(..., description="Company ID")
    text: str = Field(..., description="Review text content")
    rating: Optional[int] = Field(None, description="Rating (1-5)")
    category: Optional[str] = Field(None, description="Review category")
    source: Optional[str] = Field(None, description="Review source platform")
    date: Optional[str] = Field(None, description="Review date")
    author: Optional[str] = Field(None, description="Review author")
