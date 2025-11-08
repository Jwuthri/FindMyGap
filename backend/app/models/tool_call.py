"""
Pydantic schemas for tool call models.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ToolCallStatusEnum(str, Enum):
    """Tool call execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ToolCallSchema(BaseModel):
    """Schema for tool call."""
    
    id: int = Field(..., description="Tool call ID")
    workflow_step_id: int = Field(..., description="Workflow step ID")
    tool_name: str = Field(..., description="Tool name")
    tool_input: Optional[dict] = Field(None, description="Tool input parameters")
    tool_output: Optional[dict] = Field(None, description="Tool output result")
    status: str = Field(..., description="Execution status")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    started_at: Optional[datetime] = Field(None, description="Tool call start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Tool call completion timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "workflow_step_id": 1,
                "tool_name": "compute_tfidf",
                "tool_input": {"dataset_name": "reviews", "text_column": "text"},
                "tool_output": {"top_terms": ["feature", "bug", "improvement"]},
                "status": "completed",
                "error_message": None,
                "started_at": "2024-01-01T12:00:00Z",
                "completed_at": "2024-01-01T12:00:02Z",
                "created_at": "2024-01-01T12:00:00Z"
            }
        }


class ToolCallCreateSchema(BaseModel):
    """Schema for creating a tool call."""
    
    workflow_step_id: int = Field(..., description="Workflow step ID")
    tool_name: str = Field(..., description="Tool name")
    tool_input: Optional[dict] = Field(None, description="Tool input parameters")
    tool_output: Optional[dict] = Field(None, description="Tool output result")
    status: str = Field(default="pending", description="Execution status")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    started_at: Optional[datetime] = Field(None, description="Tool call start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Tool call completion timestamp")

