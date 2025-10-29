"""
Pydantic schemas for company models.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CompanySchema(BaseModel):
    """Schema for company."""
    
    id: int = Field(..., description="Company ID")
    name: str = Field(..., description="Company name")
    description: Optional[str] = Field(None, description="Company description")
    industry: Optional[str] = Field(None, description="Industry")
    website: Optional[str] = Field(None, description="Website URL")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Spotify",
                "description": "Music streaming service",
                "industry": "Technology",
                "website": "https://spotify.com",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class CompanyCreateSchema(BaseModel):
    """Schema for creating a company."""
    
    name: str = Field(..., description="Company name")
    description: Optional[str] = Field(None, description="Company description")
    industry: Optional[str] = Field(None, description="Industry")
    website: Optional[str] = Field(None, description="Website URL")
