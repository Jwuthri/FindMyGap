"""
Pydantic schemas for conversation models.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ConversationSchema(BaseModel):
    """Schema for conversation."""
    
    id: int = Field(..., description="Conversation ID")
    user_id: int = Field(..., description="User ID")
    title: Optional[str] = Field(None, description="Conversation title")
    extra_metadata: Optional[dict] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "title": "Product Gap Analysis",
                "extra_metadata": {},
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class ConversationCreateSchema(BaseModel):
    """Schema for creating a conversation."""
    
    user_id: int = Field(..., description="User ID")
    title: Optional[str] = Field(None, description="Conversation title")
    extra_metadata: Optional[dict] = Field(default_factory=dict, description="Additional metadata")

