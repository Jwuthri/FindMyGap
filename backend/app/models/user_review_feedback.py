"""
Pydantic schemas for user review feedback models.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserReviewFeedbackSchema(BaseModel):
    """Schema for user review feedback relationship."""
    
    id: int = Field(..., description="User review feedback ID")
    user_id: int = Field(..., description="User ID")
    review_id: int = Field(..., description="Review ID")
    is_owner: bool = Field(False, description="Whether user owns this review")
    access_type: Optional[str] = Field(None, description="How user got access (uploaded, shared, platform)")
    notes: Optional[str] = Field(None, description="Additional notes about this relationship")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 123,
                "review_id": 456,
                "is_owner": True,
                "access_type": "uploaded",
                "notes": "User uploaded this review",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class UserReviewFeedbackCreateSchema(BaseModel):
    """Schema for creating user review feedback relationship."""
    
    user_id: int = Field(..., description="User ID")
    review_id: int = Field(..., description="Review ID")
    is_owner: bool = Field(False, description="Whether user owns this review")
    access_type: Optional[str] = Field(None, description="How user got access")
    notes: Optional[str] = Field(None, description="Additional notes")


class UserReviewAccessGrantSchema(BaseModel):
    """Schema for granting user access to reviews."""
    
    user_id: int = Field(..., description="User ID to grant access to")
    review_ids: list[int] = Field(..., description="List of review IDs to grant access to")
    access_type: Optional[str] = Field("shared", description="Type of access being granted")
    is_owner: bool = Field(False, description="Whether user should be marked as owner")


class UserReviewAccessCheckSchema(BaseModel):
    """Schema for checking user access to a review."""
    
    user_id: int = Field(..., description="User ID")
    review_id: int = Field(..., description="Review ID")
    has_access: bool = Field(..., description="Whether user has access")
