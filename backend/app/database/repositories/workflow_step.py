"""
Workflow step repository for FindMyGap.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app import get_logger
from app.database.models.workflow_step import WorkflowStepTable

logger = get_logger(__name__)


class WorkflowStepRepository:
    """Repository for WorkflowStep model operations."""

    def _log_prefix(self, step_id: Optional[int] = None, message_id: Optional[int] = None) -> str:
        """Generate log prefix following team standards."""
        return f"[WorkflowStepRepository] | [step_id={step_id or 'None'}] | [message_id={message_id or 'None'}]"

    def create(
        self,
        db: Session,
        message_id: int,
        step_name: str,
        step_type: str,
        input_data: Optional[dict] = None,
        output_data: Optional[dict] = None,
        status: str = "pending",
        error_message: Optional[str] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ) -> WorkflowStepTable:
        """Create a new workflow step."""
        step = WorkflowStepTable(
            message_id=message_id,
            step_name=step_name,
            step_type=step_type,
            input_data=input_data,
            output_data=output_data,
            status=status,
            error_message=error_message,
            started_at=started_at,
            completed_at=completed_at
        )
        db.add(step)
        db.commit()
        db.refresh(step)
        logger.info(f"{self._log_prefix(step.id, message_id)} | Created workflow step: {step_name}")
        return step

    def get_by_id(self, db: Session, step_id: int) -> Optional[WorkflowStepTable]:
        """Get workflow step by ID."""
        return db.query(WorkflowStepTable).filter(WorkflowStepTable.id == step_id).first()

    def get_by_message_id(
        self,
        db: Session,
        message_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[WorkflowStepTable]:
        """Get all workflow steps for a message."""
        return (
            db.query(WorkflowStepTable)
            .filter(WorkflowStepTable.message_id == message_id)
            .order_by(WorkflowStepTable.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_step_type(
        self,
        db: Session,
        message_id: int,
        step_type: str
    ) -> List[WorkflowStepTable]:
        """Get workflow steps by step type."""
        return (
            db.query(WorkflowStepTable)
            .filter(
                WorkflowStepTable.message_id == message_id,
                WorkflowStepTable.step_type == step_type
            )
            .order_by(WorkflowStepTable.created_at.asc())
            .all()
        )

    def get_by_status(
        self,
        db: Session,
        message_id: int,
        status: str
    ) -> List[WorkflowStepTable]:
        """Get workflow steps by status."""
        return (
            db.query(WorkflowStepTable)
            .filter(
                WorkflowStepTable.message_id == message_id,
                WorkflowStepTable.status == status
            )
            .order_by(WorkflowStepTable.created_at.asc())
            .all()
        )

    def update(self, db: Session, step_id: int, **kwargs) -> Optional[WorkflowStepTable]:
        """Update workflow step."""
        step = self.get_by_id(db, step_id)
        if not step:
            return None

        for key, value in kwargs.items():
            if hasattr(step, key):
                setattr(step, key, value)

        db.commit()
        db.refresh(step)
        logger.info(f"{self._log_prefix(step_id)} | Updated workflow step")
        return step

    def mark_started(self, db: Session, step_id: int) -> Optional[WorkflowStepTable]:
        """Mark workflow step as started."""
        return self.update(
            db,
            step_id,
            status="in_progress",
            started_at=datetime.utcnow()
        )

    def mark_completed(
        self,
        db: Session,
        step_id: int,
        output_data: Optional[dict] = None
    ) -> Optional[WorkflowStepTable]:
        """Mark workflow step as completed."""
        update_data = {
            "status": "completed",
            "completed_at": datetime.utcnow()
        }
        if output_data is not None:
            update_data["output_data"] = output_data
        return self.update(db, step_id, **update_data)

    def mark_failed(
        self,
        db: Session,
        step_id: int,
        error_message: str,
        output_data: Optional[dict] = None
    ) -> Optional[WorkflowStepTable]:
        """Mark workflow step as failed."""
        update_data = {
            "status": "failed",
            "error_message": error_message,
            "completed_at": datetime.utcnow()
        }
        if output_data is not None:
            update_data["output_data"] = output_data
        return self.update(db, step_id, **update_data)

    def delete(self, db: Session, step_id: int) -> bool:
        """Delete workflow step by ID."""
        step = self.get_by_id(db, step_id)
        if step:
            db.delete(step)
            db.commit()
            logger.info(f"{self._log_prefix(step_id)} | Deleted workflow step")
            return True
        return False

