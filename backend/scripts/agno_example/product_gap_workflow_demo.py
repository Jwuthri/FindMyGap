"""
Product Gap Detection Workflow - Demo Script

Demonstrates the workflow with various query types:
1. Query needing only data retrieval
2. Query needing data + NLP
3. Query needing only NLP (using existing data)
4. General question (no data/NLP needed)
"""

import asyncio
from app.agents.product_gap_workflow import create_product_gap_workflow
from app.config import SETTINGS
from agno.run.workflow import WorkflowRunEvent
from app import get_logger

logger = get_logger("product_gap_workflow_demo")


async def demo_data_only_query():
    """Demo: Query needing only data retrieval."""
    print("\n" + "=" * 80)
    print("DEMO 1: Data Retrieval Only")
    print("=" * 80)
    
    workflow = create_product_gap_workflow(api_key=SETTINGS.OPENAI_API_KEY)
    
    query = "Show me the latest 50 reviews for Spotify"
    print(f"Query: {query}\n")
    
    resp = await workflow.arun(
        input=query,
        markdown=True,
        stream=True,
        stream_intermediate_steps=True,
    )
    
    async for event in resp:
        if event.event == WorkflowRunEvent.workflow_started.value:
            logger.info("Workflow started")
        elif event.event == WorkflowRunEvent.step_started.value:
            logger.info(f"Step started: {event.step_name}")
        elif event.event == WorkflowRunEvent.step_completed.value:
            logger.info(f"Step completed: {event.step_name}")
            if hasattr(event, 'content') and event.content:
                print(f"\n[{event.step_name}] Output:\n{event.content[:200]}...")
        elif event.event == WorkflowRunEvent.workflow_completed.value:
            logger.info("Workflow completed")
            print(f"\n\nFinal Answer:\n{event.content}")


async def demo_data_plus_nlp_query():
    """Demo: Query needing data retrieval + NLP analysis."""
    print("\n" + "=" * 80)
    print("DEMO 2: Data Retrieval + NLP Analysis")
    print("=" * 80)
    
    workflow = create_product_gap_workflow(api_key=SETTINGS.OPENAI_API_KEY)
    
    query = "What are the main product gaps for Notion based on customer feedback?"
    print(f"Query: {query}\n")
    
    resp = await workflow.arun(
        input=query,
        markdown=True,
        stream=True,
        stream_intermediate_steps=True,
    )
    
    async for event in resp:
        if event.event == WorkflowRunEvent.workflow_started.value:
            logger.info("Workflow started")
        elif event.event == WorkflowRunEvent.step_started.value:
            logger.info(f"Step started: {event.step_name}")
        elif event.event == WorkflowRunEvent.step_completed.value:
            logger.info(f"Step completed: {event.step_name}")
            if hasattr(event, 'content') and event.content:
                print(f"\n[{event.step_name}] Output:\n{event.content[:200]}...")
        elif event.event == WorkflowRunEvent.workflow_completed.value:
            logger.info("Workflow completed")
            print(f"\n\nFinal Answer:\n{event.content}")


async def demo_nlp_only_query():
    """Demo: Query needing only NLP analysis (assumes data available)."""
    print("\n" + "=" * 80)
    print("DEMO 3: NLP Analysis Only")
    print("=" * 80)
    
    workflow = create_product_gap_workflow(api_key=SETTINGS.OPENAI_API_KEY)
    
    query = "Cluster Slack reviews by theme"
    print(f"Query: {query}\n")
    
    resp = await workflow.arun(
        input=query,
        markdown=True,
        stream=True,
        stream_intermediate_steps=True,
    )
    
    async for event in resp:
        if event.event == WorkflowRunEvent.workflow_started.value:
            logger.info("Workflow started")
        elif event.event == WorkflowRunEvent.step_started.value:
            logger.info(f"Step started: {event.step_name}")
        elif event.event == WorkflowRunEvent.step_completed.value:
            logger.info(f"Step completed: {event.step_name}")
            if hasattr(event, 'content') and event.content:
                print(f"\n[{event.step_name}] Output:\n{event.content[:200]}...")
        elif event.event == WorkflowRunEvent.workflow_completed.value:
            logger.info("Workflow completed")
            print(f"\n\nFinal Answer:\n{event.content}")


async def demo_general_query():
    """Demo: General question not needing data or NLP."""
    print("\n" + "=" * 80)
    print("DEMO 4: General Question")
    print("=" * 80)
    
    workflow = create_product_gap_workflow(api_key=SETTINGS.OPENAI_API_KEY)
    
    query = "What companies do you have data for?"
    print(f"Query: {query}\n")
    
    resp = await workflow.arun(
        input=query,
        markdown=True,
        stream=True,
        stream_intermediate_steps=True,
    )
    
    async for event in resp:
        if event.event == WorkflowRunEvent.workflow_started.value:
            logger.info("Workflow started")
        elif event.event == WorkflowRunEvent.step_started.value:
            logger.info(f"Step started: {event.step_name}")
        elif event.event == WorkflowRunEvent.step_completed.value:
            logger.info(f"Step completed: {event.step_name}")
            if hasattr(event, 'content') and event.content:
                print(f"\n[{event.step_name}] Output:\n{event.content[:200]}...")
        elif event.event == WorkflowRunEvent.workflow_completed.value:
            logger.info("Workflow completed")
            print(f"\n\nFinal Answer:\n{event.content}")


async def demo_insufficient_data_retry():
    """Demo: Query that triggers data sufficiency check and retry."""
    print("\n" + "=" * 80)
    print("DEMO 5: Data Sufficiency Check with Retry")
    print("=" * 80)
    
    workflow = create_product_gap_workflow(api_key=SETTINGS.OPENAI_API_KEY)
    
    query = "Perform detailed clustering analysis on Spotify reviews to identify all major themes"
    print(f"Query: {query}\n")
    print("This should trigger sufficiency check and potentially retry with more data...\n")
    
    resp = await workflow.arun(
        input=query,
        markdown=True,
        stream=True,
        stream_intermediate_steps=True,
    )
    
    async for event in resp:
        if event.event == WorkflowRunEvent.workflow_started.value:
            logger.info("Workflow started")
        elif event.event == WorkflowRunEvent.step_started.value:
            logger.info(f"Step started: {event.step_name}")
        elif event.event == WorkflowRunEvent.step_completed.value:
            logger.info(f"Step completed: {event.step_name}")
            if hasattr(event, 'content') and event.content:
                print(f"\n[{event.step_name}] Output:\n{event.content[:200]}...")
        elif event.event == WorkflowRunEvent.workflow_completed.value:
            logger.info("Workflow completed")
            print(f"\n\nFinal Answer:\n{event.content}")


async def main():
    """Run all demos."""
    demos = [
        ("Data Only", demo_data_only_query),
        ("Data + NLP", demo_data_plus_nlp_query),
        ("NLP Only", demo_nlp_only_query),
        ("General", demo_general_query),
        ("Insufficient Data Retry", demo_insufficient_data_retry),
    ]
    
    print("\n" + "=" * 80)
    print("PRODUCT GAP DETECTION WORKFLOW - DEMO")
    print("=" * 80)
    print("\nThis demo showcases the workflow with different query types.")
    print("The workflow conditionally executes steps based on query analysis.")
    print("\nAvailable demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    
    print("\nRunning Demo 2 (Data + NLP) as default...\n")
    
    # Run the most comprehensive demo by default
    await demo_data_plus_nlp_query()
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print("\nTo run other demos, modify the main() function or run them individually.")


if __name__ == "__main__":
    asyncio.run(main())

