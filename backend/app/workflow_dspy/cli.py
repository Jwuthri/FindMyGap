"""
CLI tool for running DSPy workflow queries.

Usage:
    python -m app.dspy_workflow.cli "Your query here"
    python -m app.dspy_workflow.cli --interactive
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add backend to path if running directly
backend_path = Path(__file__).parent.parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.dspy_workflow.main import run_workflow


async def run_single_query(query: str, user_id: int = 1):
    """Run a single query through the workflow."""
    print(f"\nQuery: {query}")
    print("-" * 80)
    
    try:
        result = await run_workflow(query, user_id=user_id)
        print("\nResult:")
        print("=" * 80)
        print(result)
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def interactive_mode(user_id: int = 1):
    """Run in interactive mode."""
    print("=" * 80)
    print("DSPy Workflow - Interactive Mode")
    print("=" * 80)
    print("Enter your queries (type 'exit' or 'quit' to stop)")
    print()
    
    while True:
        try:
            query = input("\n🔍 Query: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye!")
                break
            
            await run_single_query(query, user_id=user_id)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\n\nGoodbye!")
            break


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run DSPy workflow queries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a single query
  python -m app.dspy_workflow.cli "What are the gaps for Netflix?"
  
  # Interactive mode
  python -m app.dspy_workflow.cli --interactive
  
  # Specify user ID
  python -m app.dspy_workflow.cli --user-id 2 "Show me reviews"
        """
    )
    
    parser.add_argument(
        'query',
        nargs='?',
        help='Query to run (if not in interactive mode)'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '-u', '--user-id',
        type=int,
        default=1,
        help='User ID for database queries (default: 1)'
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        asyncio.run(interactive_mode(user_id=args.user_id))
    elif args.query:
        asyncio.run(run_single_query(args.query, user_id=args.user_id))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
