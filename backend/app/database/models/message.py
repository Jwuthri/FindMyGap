"""
Message model for FindMyGap.
"""

import enum
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..base import Base


class MessageRoleEnum(str, enum.Enum):
    """Message role types."""
    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"


class MessageTable(Base):
    """Message model for user queries and system responses."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False, index=True)  # user, system, assistant
    
    # Message content
    content = Column(Text, nullable=False)  # User query or system response
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    conversation = relationship("ConversationTable", back_populates="messages")
    workflow_steps = relationship("WorkflowStepTable", back_populates="message", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, role={self.role})>"

