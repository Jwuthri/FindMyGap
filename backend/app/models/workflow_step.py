"""
Pydantic schemas for workflow step models.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class WorkflowStepTypeEnum(str, Enum):
    """Workflow step types."""
    QUERY_ANALYSIS = "query_analysis"
    FORMAT_DETECTION = "format_detection"
    RETRIEVAL_PLANNING = "retrieval_planning"
    DATA_RETRIEVAL = "data_retrieval"
    NLP_ANALYSIS = "nlp_analysis"
    ANSWER_GENERATION = "answer_generation"
    SKIP_RETRIEVAL = "skip_retrieval"


class StepStatusEnum(str, Enum):
    """Step execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStepSchema(BaseModel):
    """Schema for workflow step."""
    
    id: int = Field(..., description="Workflow step ID")
    message_id: int = Field(..., description="Message ID")
    step_name: str = Field(..., description="Step name")
    step_type: str = Field(..., description="Step type")
    input_data: Optional[dict] = Field(None, description="Input event data")
    output_data: Optional[dict] = Field(None, description="Output event data")
    status: str = Field(..., description="Execution status")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    started_at: Optional[datetime] = Field(None, description="Step start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Step completion timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "message_id": 1,
                "step_name": "start_workflow",
                "step_type": "query_analysis",
                "input_data": {"query": "What are the main product gaps?"},
                "output_data": {"analysis": "..."},
                "status": "completed",
                "error_message": None,
                "started_at": "2024-01-01T12:00:00Z",
                "completed_at": "2024-01-01T12:00:05Z",
                "created_at": "2024-01-01T12:00:00Z"
            }
        }


class WorkflowStepCreateSchema(BaseModel):
    """Schema for creating a workflow step."""
    
    message_id: int = Field(..., description="Message ID")
    step_name: str = Field(..., description="Step name")
    step_type: str = Field(..., description="Step type")
    input_data: Optional[dict] = Field(None, description="Input event data")
    output_data: Optional[dict] = Field(None, description="Output event data")
    status: str = Field(default="pending", description="Execution status")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    started_at: Optional[datetime] = Field(None, description="Step start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Step completion timestamp")

