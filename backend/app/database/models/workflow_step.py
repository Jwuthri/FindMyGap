"""
Workflow step model for FindMyGap.
"""

import enum
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..base import Base


class WorkflowStepTypeEnum(str, enum.Enum):
    """Workflow step types."""
    QUERY_ANALYSIS = "query_analysis"
    FORMAT_DETECTION = "format_detection"
    RETRIEVAL_PLANNING = "retrieval_planning"
    DATA_RETRIEVAL = "data_retrieval"
    NLP_ANALYSIS = "nlp_analysis"
    ANSWER_GENERATION = "answer_generation"
    SKIP_RETRIEVAL = "skip_retrieval"


class StepStatusEnum(str, enum.Enum):
    """Step execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStepTable(Base):
    """Workflow step execution tracking."""
    __tablename__ = "workflow_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False, index=True)
    
    # Step identification
    step_name = Column(String(100), nullable=False)  # e.g., "start_workflow", "detect_output_format"
    step_type = Column(String(50), nullable=False, index=True)  # WorkflowStepTypeEnum
    
    # Step execution data
    input_data = Column(JSON, nullable=True)  # Input event data
    output_data = Column(JSON, nullable=True)  # Output event data
    
    # Execution status
    status = Column(String(20), nullable=False, default="pending", index=True)  # StepStatusEnum
    error_message = Column(Text, nullable=True)
    
    # Execution timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    message = relationship("MessageTable", back_populates="workflow_steps")
    tool_calls = relationship("ToolCallTable", back_populates="workflow_step", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WorkflowStep(id={self.id}, message_id={self.message_id}, step_name={self.step_name}, status={self.status})>"

