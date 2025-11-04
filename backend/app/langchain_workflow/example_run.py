"""
Example script to run the LangChain Product Gap Workflow.

This demonstrates how to use the LangChain implementation and compare
it with the Agno implementation.
"""

import asyncio
from app import get_logger
from app.langchain_workflow.product_gap_workflow import run_workflow

logger = get_logger(__name__)


def example_queries():
    """Return example queries to test the workflow."""
    return [
        "What are the top product gaps for Notion based on user reviews?",
        "Show me a table of the most requested features",
        "Analyze sentiment distribution for Slack reviews",
        "What are the main pain points users mention?",
        "List all reviews mentioning 'pricing' or 'expensive'",
    ]


def run_single_query(query: str, user_id: int = 1):
    """
    Run a single query through the workflow.
    
    Args:
        query: User query to process
        user_id: User ID for user-specific data
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"Running Query: {query}")
    logger.info(f"{'='*80}\n")
    
    try:
        result = run_workflow(query=query, user_id=user_id)
        
        logger.info(f"\n{'='*80}")
        logger.info("RESULTS:")
        logger.info(f"{'='*80}")
        
        logger.info(f"\nQuery Analysis:")
        logger.info(f"  {result.get('query_analysis', {})}")
        
        logger.info(f"\nFormat Detection:")
        logger.info(f"  {result.get('format_detection', {})}")
        
        if result.get('retrieval_plan'):
            logger.info(f"\nRetrieval Plan:")
            logger.info(f"  {result['retrieval_plan'].get('reasoning', 'N/A')}")
            logger.info(f"  Queries: {len(result['retrieval_plan'].get('sql_queries', []))}")
        
        if result.get('retrieved_data'):
            logger.info(f"\nRetrieved Data:")
            logger.info(f"  Total Rows: {result['retrieved_data'].get('total_rows', 0)}")
        
        if result.get('nlp_analysis'):
            logger.info(f"\nNLP Analysis:")
            logger.info(f"  Performed: Yes")
        
        logger.info(f"\n{'='*80}")
        logger.info("FINAL ANSWER:")
        logger.info(f"{'='*80}")
        logger.info(result.get('final_answer', 'No answer generated'))
        logger.info(f"\n{'='*80}\n")
        
        return result
        
    except Exception as e:
        logger.error(f"Error running workflow: {e}", exc_info=True)
        return None


def run_comparison():
    """
    Run the same query through both Agno and LangChain workflows
    to compare results and performance.
    """
    query = "What are the top 3 product gaps for Notion?"
    
    logger.info("\n" + "="*80)
    logger.info("COMPARISON: Agno vs LangChain")
    logger.info("="*80 + "\n")
    
    # Run LangChain version
    logger.info("\n--- LangChain Implementation ---\n")
    langchain_result = run_single_query(query)
    
    # Run Agno version (if available)
    logger.info("\n--- Agno Implementation ---\n")
    try:
        from app.workflows.product_gap_workflow import create_product_gap_workflow
        
        agno_workflow = create_product_gap_workflow(user_id=1)
        agno_result = agno_workflow.run(query)
        
        logger.info(f"\nAgno Result:")
        logger.info(agno_result)
        
    except Exception as e:
        logger.warning(f"Could not run Agno workflow for comparison: {e}")
    
    # Compare
    logger.info("\n" + "="*80)
    logger.info("COMPARISON SUMMARY:")
    logger.info("="*80)
    logger.info("""
Key Differences:
1. Code Style: Agno more declarative, LangChain more explicit
2. State Management: Agno uses StepInput/Output, LangChain uses TypedDict
3. Workflow Definition: Agno uses Step/Condition, LangChain uses Graph nodes/edges
4. Team Coordination: Both support multi-agent, different implementations
    """)


def main():
    """Main execution function."""
    import sys
    
    if len(sys.argv) > 1:
        # Run specific query from command line
        query = " ".join(sys.argv[1:])
        run_single_query(query)
    else:
        # Run example queries
        logger.info("Running example queries...\n")
        
        queries = example_queries()
        
        for i, query in enumerate(queries, 1):
            logger.info(f"\n\nExample {i}/{len(queries)}")
            run_single_query(query)
            
            if i < len(queries):
                input("\nPress Enter to continue to next example...")
        
        # Optional: Run comparison
        compare = input("\n\nRun comparison with Agno implementation? (y/n): ")
        if compare.lower() == 'y':
            run_comparison()


if __name__ == "__main__":
    main()

