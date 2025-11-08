"""
Test workflow database tracking.

Run this to verify that conversations, messages, workflow steps, and tool calls
are properly tracked in the database.
"""

import asyncio
from app.workflow.main import run_workflow
from app.database.base import SessionLocal
from app.database.repositories import (
    ConversationRepository,
    MessageRepository,
    WorkflowStepRepository,
    ToolCallRepository
)
from app import get_logger

logger = get_logger(__name__)


async def test_workflow_tracking():
    """Test that workflow execution properly tracks everything in the database."""
    
    print("\n" + "=" * 80)
    print("Testing Workflow Database Tracking")
    print("=" * 80 + "\n")
    
    # Run a simple workflow
    query = "What are the main product gaps for Netflix?"
    print(f"Running workflow with query: {query}\n")
    
    result = await run_workflow(query, user_id=1)
    
    print("\n" + "=" * 80)
    print("Workflow completed! Checking database...")
    print("=" * 80 + "\n")
    
    # Check what was created in the database
    db_session = SessionLocal()
    try:
        conv_repo = ConversationRepository()
        msg_repo = MessageRepository()
        step_repo = WorkflowStepRepository()
        tool_repo = ToolCallRepository()
        
        # Get the latest conversation
        conversations = conv_repo.get_by_user_id(db_session, user_id=1, limit=1)
        if not conversations:
            print("❌ No conversation found!")
            return
        
        conversation = conversations[0]
        print(f"✅ Conversation: ID={conversation.id}, Title={conversation.title}")
        
        # Get messages
        messages = msg_repo.get_by_conversation_id(db_session, conversation.id)
        print(f"\n✅ Messages ({len(messages)}):")
        for msg in messages:
            content_preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            print(f"   - {msg.role}: {content_preview}")
        
        # Get workflow steps for the user message
        if messages:
            user_message = [m for m in messages if m.role == "user"][0]
            steps = step_repo.get_by_message_id(db_session, user_message.id)
            print(f"\n✅ Workflow Steps ({len(steps)}):")
            for step in steps:
                print(f"   - {step.step_name} ({step.step_type}): {step.status}")
                
                # Get tool calls for NLP analysis step
                if step.step_type == "nlp_analysis":
                    tool_calls = tool_repo.get_by_workflow_step_id(db_session, step.id)
                    if tool_calls:
                        print(f"      Tool Calls ({len(tool_calls)}):")
                        for tool_call in tool_calls:
                            print(f"      - {tool_call.tool_name}: {tool_call.status}")
        
        print("\n" + "=" * 80)
        print("Database tracking verification complete!")
        print("=" * 80 + "\n")
        
    finally:
        db_session.close()


if __name__ == "__main__":
    asyncio.run(test_workflow_tracking())

