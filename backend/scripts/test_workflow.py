"""
Quick test script for the Product Gap Detection Workflow.
Run this to verify the basic functionality works.
"""

import asyncio
from app.agents.product_gap_workflow import create_product_gap_workflow
from app.config import SETTINGS


async def test_basic_workflow():
    """Quick test of the workflow."""
    print("Creating Product Gap Detection Workflow...")
    workflow = create_product_gap_workflow(api_key=SETTINGS.OPENAI_API_KEY)
    
    print("\nWorkflow created successfully!")
    print(f"Name: {workflow.name}")
    print(f"Description: {workflow.description}")
    print(f"Number of steps: {len(workflow.steps)}")
    
    print("\nWorkflow steps:")
    for i, step in enumerate(workflow.steps, 1):
        step_name = getattr(step, 'name', step.__name__ if callable(step) else str(step))
        print(f"  {i}. {step_name}")
    
    print("\n" + "=" * 80)
    print("Testing with a simple query...")
    print("=" * 80)
    
    query = "What are the top 3 product gaps for Spotify?"
    print(f"\nQuery: {query}\n")
    
    try:
        resp = await workflow.arun(
            input=query,
            markdown=True,
            stream=False,  # Non-streaming for quick test
        )
        print("\n" + "=" * 80)
        print("RESULT:")
        print("=" * 80)
        print(resp)
    except Exception as e:
        print(f"\nError during execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_basic_workflow())

