"""
Tool call repository for FindMyGap.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app import get_logger
from app.database.models.tool_call import ToolCallTable

logger = get_logger(__name__)


class ToolCallRepository:
    """Repository for ToolCall model operations."""

    def _log_prefix(self, tool_call_id: Optional[int] = None, workflow_step_id: Optional[int] = None) -> str:
        """Generate log prefix following team standards."""
        return f"[ToolCallRepository] | [tool_call_id={tool_call_id or 'None'}] | [workflow_step_id={workflow_step_id or 'None'}]"

    def create(
        self,
        db: Session,
        workflow_step_id: int,
        tool_name: str,
        tool_input: Optional[dict] = None,
        tool_output: Optional[dict] = None,
        status: str = "pending",
        error_message: Optional[str] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ) -> ToolCallTable:
        """Create a new tool call."""
        tool_call = ToolCallTable(
            workflow_step_id=workflow_step_id,
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=tool_output,
            status=status,
            error_message=error_message,
            started_at=started_at,
            completed_at=completed_at
        )
        db.add(tool_call)
        db.commit()
        db.refresh(tool_call)
        logger.info(f"{self._log_prefix(tool_call.id, workflow_step_id)} | Created tool call: {tool_name}")
        return tool_call

    def get_by_id(self, db: Session, tool_call_id: int) -> Optional[ToolCallTable]:
        """Get tool call by ID."""
        return db.query(ToolCallTable).filter(ToolCallTable.id == tool_call_id).first()

    def get_by_workflow_step_id(
        self,
        db: Session,
        workflow_step_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ToolCallTable]:
        """Get all tool calls for a workflow step."""
        return (
            db.query(ToolCallTable)
            .filter(ToolCallTable.workflow_step_id == workflow_step_id)
            .order_by(ToolCallTable.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_tool_name(
        self,
        db: Session,
        workflow_step_id: int,
        tool_name: str
    ) -> List[ToolCallTable]:
        """Get tool calls by tool name."""
        return (
            db.query(ToolCallTable)
            .filter(
                ToolCallTable.workflow_step_id == workflow_step_id,
                ToolCallTable.tool_name == tool_name
            )
            .order_by(ToolCallTable.created_at.asc())
            .all()
        )

    def get_by_status(
        self,
        db: Session,
        workflow_step_id: int,
        status: str
    ) -> List[ToolCallTable]:
        """Get tool calls by status."""
        return (
            db.query(ToolCallTable)
            .filter(
                ToolCallTable.workflow_step_id == workflow_step_id,
                ToolCallTable.status == status
            )
            .order_by(ToolCallTable.created_at.asc())
            .all()
        )

    def update(self, db: Session, tool_call_id: int, **kwargs) -> Optional[ToolCallTable]:
        """Update tool call."""
        tool_call = self.get_by_id(db, tool_call_id)
        if not tool_call:
            return None

        for key, value in kwargs.items():
            if hasattr(tool_call, key):
                setattr(tool_call, key, value)

        db.commit()
        db.refresh(tool_call)
        logger.info(f"{self._log_prefix(tool_call_id)} | Updated tool call")
        return tool_call

    def mark_started(self, db: Session, tool_call_id: int) -> Optional[ToolCallTable]:
        """Mark tool call as started."""
        return self.update(
            db,
            tool_call_id,
            status="in_progress",
            started_at=datetime.utcnow()
        )

    def mark_completed(
        self,
        db: Session,
        tool_call_id: int,
        tool_output: Optional[dict] = None
    ) -> Optional[ToolCallTable]:
        """Mark tool call as completed."""
        update_data = {
            "status": "completed",
            "completed_at": datetime.utcnow()
        }
        if tool_output is not None:
            update_data["tool_output"] = tool_output
        return self.update(db, tool_call_id, **update_data)

    def mark_failed(
        self,
        db: Session,
        tool_call_id: int,
        error_message: str,
        tool_output: Optional[dict] = None
    ) -> Optional[ToolCallTable]:
        """Mark tool call as failed."""
        update_data = {
            "status": "failed",
            "error_message": error_message,
            "completed_at": datetime.utcnow()
        }
        if tool_output is not None:
            update_data["tool_output"] = tool_output
        return self.update(db, tool_call_id, **update_data)

    def delete(self, db: Session, tool_call_id: int) -> bool:
        """Delete tool call by ID."""
        tool_call = self.get_by_id(db, tool_call_id)
        if tool_call:
            db.delete(tool_call)
            db.commit()
            logger.info(f"{self._log_prefix(tool_call_id)} | Deleted tool call")
            return True
        return False

