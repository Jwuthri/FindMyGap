"""
Example usage of the DSPy workflow.

Run this script to test the workflow:
    python -m app.dspy_workflow.example
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path if running directly
backend_path = Path(__file__).parent.parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.dspy_workflow.main import run_workflow


async def main():
    """Run example queries through the DSPy workflow."""
    
    print("=" * 80)
    print("DSPy Workflow Examples")
    print("=" * 80)
    print()
    
    # Example 1: Data retrieval query
    print("Example 1: Data Retrieval Query")
    print("-" * 80)
    query1 = "What are the main product gaps for Netflix based on customer reviews?"
    print(f"Query: {query1}")
    print()
    
    try:
        result1 = await run_workflow(query1, user_id=1)
        print("\nResult:")
        print(result1)
    except Exception as e:
        print(f"\nError: {e}")
    
    print("\n" + "=" * 80)
    print()
    
    # Example 2: General query (no data retrieval)
    print("Example 2: General Query")
    print("-" * 80)
    query2 = "What is sentiment analysis and how does it work?"
    print(f"Query: {query2}")
    print()
    
    try:
        result2 = await run_workflow(query2, user_id=1)
        print("\nResult:")
        print(result2)
    except Exception as e:
        print(f"\nError: {e}")
    
    print("\n" + "=" * 80)
    print()
    
    # Example 3: Specific data query
    print("Example 3: Specific Data Query")
    print("-" * 80)
    query3 = "Show me the top 5 most recent reviews for Netflix"
    print(f"Query: {query3}")
    print()
    
    try:
        result3 = await run_workflow(query3, user_id=1)
        print("\nResult:")
        print(result3)
    except Exception as e:
        print(f"\nError: {e}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
