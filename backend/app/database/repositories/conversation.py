"""
Conversation repository for FindMyGap.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app import get_logger
from app.database.models.conversation import ConversationTable

logger = get_logger(__name__)


class ConversationRepository:
    """Repository for Conversation model operations."""

    def _log_prefix(self, conversation_id: Optional[int] = None, user_id: Optional[int] = None) -> str:
        """Generate log prefix following team standards."""
        return f"[ConversationRepository] | [conversation_id={conversation_id or 'None'}] | [user_id={user_id or 'None'}]"

    def create(
        self,
        db: Session,
        user_id: int,
        title: Optional[str] = None,
        extra_metadata: Optional[dict] = None
    ) -> ConversationTable:
        """Create a new conversation."""
        conversation = ConversationTable(
            user_id=user_id,
            title=title,
            extra_metadata=extra_metadata or {}
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        logger.info(f"{self._log_prefix(conversation.id, user_id)} | Created conversation")
        return conversation

    def get_by_id(self, db: Session, conversation_id: int) -> Optional[ConversationTable]:
        """Get conversation by ID."""
        return db.query(ConversationTable).filter(ConversationTable.id == conversation_id).first()

    def get_by_user_id(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ConversationTable]:
        """Get all conversations for a user."""
        return (
            db.query(ConversationTable)
            .filter(ConversationTable.user_id == user_id)
            .order_by(ConversationTable.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ConversationTable]:
        """Get all conversations with pagination."""
        return (
            db.query(ConversationTable)
            .order_by(ConversationTable.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, db: Session, conversation_id: int, **kwargs) -> Optional[ConversationTable]:
        """Update conversation."""
        conversation = self.get_by_id(db, conversation_id)
        if not conversation:
            return None

        for key, value in kwargs.items():
            if hasattr(conversation, key):
                setattr(conversation, key, value)

        conversation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(conversation)
        logger.info(f"{self._log_prefix(conversation_id)} | Updated conversation")
        return conversation

    def delete(self, db: Session, conversation_id: int) -> bool:
        """Delete conversation by ID."""
        conversation = self.get_by_id(db, conversation_id)
        if conversation:
            db.delete(conversation)
            db.commit()
            logger.info(f"{self._log_prefix(conversation_id)} | Deleted conversation")
            return True
        return False

