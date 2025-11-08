"""
Tool call model for FindMyGap.
"""

import enum
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..base import Base


class ToolCallStatusEnum(str, enum.Enum):
    """Tool call execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ToolCallTable(Base):
    """Tool call execution tracking."""
    __tablename__ = "tool_calls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_step_id = Column(Integer, ForeignKey("workflow_steps.id"), nullable=False, index=True)
    
    # Tool identification
    tool_name = Column(String(100), nullable=False, index=True)  # e.g., "compute_tfidf", "cluster_reviews"
    
    # Tool execution data
    tool_input = Column(JSON, nullable=True)  # Tool parameters/input
    tool_output = Column(JSON, nullable=True)  # Tool result/output
    
    # Execution status
    status = Column(String(20), nullable=False, default="pending", index=True)  # ToolCallStatusEnum
    error_message = Column(Text, nullable=True)
    
    # Execution timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    workflow_step = relationship("WorkflowStepTable", back_populates="tool_calls")

    def __repr__(self):
        return f"<ToolCall(id={self.id}, workflow_step_id={self.workflow_step_id}, tool_name={self.tool_name}, status={self.status})>"

