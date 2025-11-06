"""
Entry point for running the LlamaIndex workflow.
"""

import asyncio
from llama_index.core.workflow import StartEvent

from app import get_logger
from app.workflow.workflow import ProductGapWorkflow

logger = get_logger("llamaindex_workflow.main")


async def run_workflow(query: str, user_id: int = 1, stream: bool = False):
    """
    Execute the LlamaIndex workflow for a given query.
    
    Args:
        query: User's question
        user_id: User ID for data access
        stream: Whether to stream results (LlamaIndex workflows support this)
    """
    logger.info("=" * 80)
    logger.info(f"🚀 Starting LlamaIndex Workflow")
    logger.info(f"   └─ Query: {query[:100]}{'...' if len(query) > 100 else ''}")
    logger.info("=" * 80)
    
    # Create workflow instance
    workflow = ProductGapWorkflow(user_id=user_id, timeout=900, verbose=True)
    
    # Run workflow
    result = await workflow.run(query=query)
    
    logger.info("=" * 80)
    logger.info("🏁 Workflow Completed")
    logger.info("=" * 80)
    
    return result


async def run_workflow_streaming(query: str, user_id: int = 1):
    """
    Execute the workflow with streaming support.
    
    Note: LlamaIndex workflows don't have built-in streaming events.
    This implementation simulates streaming by yielding progress updates.
    """
    logger.info("🚀 Starting LlamaIndex Workflow (Streaming Mode)")
    
    workflow = ProductGapWorkflow(user_id=user_id, timeout=300, verbose=True)
    
    # Simulate streaming by yielding progress events
    yield {"type": "workflow_started", "message": "Workflow started"}
    
    try:
        # Run the workflow
        result = await workflow.run(query=query)
        
        # Yield completion event
        yield {"type": "workflow_completed", "result": result}
        
    except Exception as e:
        # Yield error event
        yield {"type": "workflow_error", "error": str(e)}
        raise
    
    logger.info("🏁 Workflow Completed (Streaming)")


if __name__ == "__main__":
    # Test query
    test_query = "What are the main product gaps for Netflix based on customer reviews?"
    result = asyncio.run(run_workflow(test_query))
    print("\n" + "=" * 80)
    print("FINAL RESULT:")
    print("=" * 80)
    print(result)
