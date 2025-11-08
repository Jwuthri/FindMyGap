"""
Message repository for FindMyGap.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app import get_logger
from app.database.models.message import MessageTable

logger = get_logger(__name__)


class MessageRepository:
    """Repository for Message model operations."""

    def _log_prefix(self, message_id: Optional[int] = None, conversation_id: Optional[int] = None) -> str:
        """Generate log prefix following team standards."""
        return f"[MessageRepository] | [message_id={message_id or 'None'}] | [conversation_id={conversation_id or 'None'}]"

    def create(
        self,
        db: Session,
        conversation_id: int,
        role: str,
        content: str
    ) -> MessageTable:
        """Create a new message."""
        message = MessageTable(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        logger.info(f"{self._log_prefix(message.id, conversation_id)} | Created message with role: {role}")
        return message

    def get_by_id(self, db: Session, message_id: int) -> Optional[MessageTable]:
        """Get message by ID."""
        return db.query(MessageTable).filter(MessageTable.id == message_id).first()

    def get_by_conversation_id(
        self,
        db: Session,
        conversation_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[MessageTable]:
        """Get all messages for a conversation."""
        return (
            db.query(MessageTable)
            .filter(MessageTable.conversation_id == conversation_id)
            .order_by(MessageTable.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_role(
        self,
        db: Session,
        conversation_id: int,
        role: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[MessageTable]:
        """Get messages by role in a conversation."""
        return (
            db.query(MessageTable)
            .filter(
                MessageTable.conversation_id == conversation_id,
                MessageTable.role == role
            )
            .order_by(MessageTable.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[MessageTable]:
        """Get all messages with pagination."""
        return (
            db.query(MessageTable)
            .order_by(MessageTable.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, db: Session, message_id: int, **kwargs) -> Optional[MessageTable]:
        """Update message."""
        message = self.get_by_id(db, message_id)
        if not message:
            return None

        for key, value in kwargs.items():
            if hasattr(message, key):
                setattr(message, key, value)

        db.commit()
        db.refresh(message)
        logger.info(f"{self._log_prefix(message_id)} | Updated message")
        return message

    def delete(self, db: Session, message_id: int) -> bool:
        """Delete message by ID."""
        message = self.get_by_id(db, message_id)
        if message:
            db.delete(message)
            db.commit()
            logger.info(f"{self._log_prefix(message_id)} | Deleted message")
            return True
        return False

