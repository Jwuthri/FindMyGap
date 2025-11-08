"""
Pydantic schemas for message models.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MessageRoleEnum(str, Enum):
    """Message role types."""
    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"


class MessageSchema(BaseModel):
    """Schema for message."""
    
    id: int = Field(..., description="Message ID")
    conversation_id: int = Field(..., description="Conversation ID")
    role: str = Field(..., description="Message role (user, system, assistant)")
    content: str = Field(..., description="Message content")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "conversation_id": 1,
                "role": "user",
                "content": "What are the main product gaps for Netflix?",
                "created_at": "2024-01-01T12:00:00Z"
            }
        }


class MessageCreateSchema(BaseModel):
    """Schema for creating a message."""
    
    conversation_id: int = Field(..., description="Conversation ID")
    role: str = Field(..., description="Message role (user, system, assistant)")
    content: str = Field(..., description="Message content")

