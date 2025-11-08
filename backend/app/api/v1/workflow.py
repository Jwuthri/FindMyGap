"""
Workflow API endpoints for FindMyGap.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app import get_logger
from app.database.base import SessionLocal
from app.database.repositories import (
    WorkflowStepRepository,
    MessageRepository,
    ConversationRepository
)
from app.models.workflow_step import WorkflowStepSchema
from app.models.message import MessageSchema
from app.workflow.main import run_workflow

logger = get_logger(__name__)

router = APIRouter()


class WorkflowQueryRequest(BaseModel):
    """Request schema for workflow query."""
    
    query: str = Field(..., description="User query/question")
    user_id: int = Field(default=1, description="User ID")
    conversation_id: Optional[int] = Field(None, description="Optional conversation ID to continue existing conversation")


class WorkflowQueryResponse(BaseModel):
    """Response schema for workflow query."""
    
    result: str = Field(..., description="Generated answer")
    conversation_id: int = Field(..., description="Conversation ID")
    message_id: Optional[int] = Field(None, description="User message ID")
    assistant_message_id: Optional[int] = Field(None, description="Assistant message ID")


def get_db():
    """Dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/query", response_model=WorkflowQueryResponse)
async def execute_workflow(request: WorkflowQueryRequest):
    """
    Execute the product gap workflow for a given query.
    
    This endpoint runs the complete workflow:
    1. Query analysis
    2. Format detection
    3. Data retrieval planning (if needed)
    4. Data retrieval (if needed)
    5. NLP analysis (if needed)
    6. Answer generation
    
    Returns the generated answer along with conversation and message IDs.
    """
    try:
        logger.info(f"Workflow query request: user_id={request.user_id}, conversation_id={request.conversation_id}")
        
        # Run the workflow
        result = await run_workflow(
            query=request.query,
            user_id=request.user_id,
            conversation_id=request.conversation_id
        )
        
        # Get the conversation_id and message IDs from the database
        db = SessionLocal()
        try:
            msg_repo = MessageRepository()
            conv_repo = ConversationRepository()
            
            # If conversation_id was provided, use it; otherwise find the latest conversation for this user
            if request.conversation_id:
                conversation_id = request.conversation_id
            else:
                # Find the latest conversation for this user
                conversations = conv_repo.get_by_user_id(db, request.user_id)
                if conversations:
                    conversation_id = conversations[0].id  # First one is most recent (desc order)
                else:
                    raise HTTPException(status_code=404, detail="Conversation not found")
            
            # Get messages for this conversation, ordered by creation time
            messages = msg_repo.get_by_conversation_id(db, conversation_id)
            
            # Find user and assistant messages (most recent first)
            user_message = None
            assistant_message = None
            
            for msg in reversed(messages):  # Start from most recent
                if msg.role == "user" and not user_message:
                    user_message = msg
                elif msg.role == "assistant" and not assistant_message:
                    assistant_message = msg
                if user_message and assistant_message:
                    break
            
            return WorkflowQueryResponse(
                result=result,
                conversation_id=conversation_id,
                message_id=user_message.id if user_message else None,
                assistant_message_id=assistant_message.id if assistant_message else None
            )
        finally:
            db.close()
            
    except Exception as e:
        logger.exception(f"Error executing workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@router.get("/steps/{message_id}", response_model=list[WorkflowStepSchema])
async def get_workflow_steps(message_id: int, db: SessionLocal = Depends(get_db)):
    """
    Get all workflow steps for a given message ID.
    
    Returns a list of workflow steps executed for the message, ordered by creation time.
    """
    try:
        repo = WorkflowStepRepository()
        steps = repo.get_by_message_id(db, message_id)
        
        return [WorkflowStepSchema.model_validate(step) for step in steps]
    except Exception as e:
        logger.exception(f"Error fetching workflow steps: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch workflow steps: {str(e)}")


@router.get("/messages/{conversation_id}", response_model=list[MessageSchema])
async def get_conversation_messages(conversation_id: int, db: SessionLocal = Depends(get_db)):
    """
    Get all messages for a conversation.
    
    Returns a list of messages ordered by creation time.
    """
    try:
        repo = MessageRepository()
        messages = repo.get_by_conversation_id(db, conversation_id)
        
        return [MessageSchema.model_validate(msg) for msg in messages]
    except Exception as e:
        logger.exception(f"Error fetching messages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {str(e)}")

