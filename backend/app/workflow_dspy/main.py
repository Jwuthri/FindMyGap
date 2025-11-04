"""
Main entry point for DSPy-based workflow execution.
"""

import asyncio
from typing import Optional

import dspy
from app import get_logger
from app.config import SETTINGS
from app.dspy_workflow.product_gap_workflow import ProductGapWorkflow

logger = get_logger("dspy_workflow.main")


def setup_dspy_lm():
    """Configure DSPy language model."""
    lm = dspy.OpenAI(
        model="gpt-4o-mini",
        api_key=SETTINGS.OPENAI_API_KEY,
        max_tokens=4000
    )
    dspy.settings.configure(lm=lm)
    return lm


async def run_workflow(query: str, user_id: Optional[int] = 1):
    """
    Execute the DSPy workflow for a given query.
    
    Args:
        query: User's question
        user_id: Optional user ID for user-specific datasets
    """
    logger.info("=" * 80)
    logger.info(f"🚀 DSPY WORKFLOW STARTED")
    logger.info(f"   └─ Input: {query[:100]}{'...' if len(query) > 100 else ''}")
    logger.info("=" * 80)
    
    # Setup DSPy
    lm = setup_dspy_lm()
    
    # Create and run workflow
    workflow = ProductGapWorkflow(user_id=user_id)
    
    try:
        result = workflow.forward(query=query)
        
        logger.info("=" * 80)
        logger.info(f"🏁 DSPY WORKFLOW COMPLETED")
        logger.info("=" * 80)
        
        return result
    except Exception as e:
        logger.error(f"❌ Workflow failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    test_query = "What are the main product gaps for Netflix based on customer reviews?"
    result = asyncio.run(run_workflow(test_query))
    print("\n" + "=" * 80)
    print("FINAL RESULT:")
    print("=" * 80)
    print(result)
