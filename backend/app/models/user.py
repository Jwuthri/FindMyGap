"""
User-related Pydantic models for API serialization.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class UserStatusEnum(str, Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class UserSchema(BaseModel):
    """User profile response model."""
    id: int = Field(..., description="User ID")
    email: Optional[str] = Field(None, description="Email address")
    username: Optional[str] = Field(None, description="Username")
    full_name: Optional[str] = Field(None, description="Full name")
    hashed_password: Optional[str] = Field(None, description="Hashed password")
    status: UserStatusEnum = Field(..., description="User status")

    preferences: Optional[dict] = Field(default_factory=dict, description="User preferences")
    extra_metadata: Optional[dict] = Field(default_factory=dict, description="Extra metadata")

    total_requests: int = Field(0, description="Total API requests made")
    total_tokens_used: int = Field(0, description="Total tokens used")

    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True  # For SQLAlchemy model conversion
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "john.doe@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "status": "active",

                "extra_metadata": {},
                "preferences": {},

                "total_requests": 0,
                "total_tokens_used": 0,
                
                "last_login_at": "2024-01-15T09:00:00Z",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
            }
        }
