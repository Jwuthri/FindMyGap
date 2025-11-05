"""
Main workflow definition using LlamaIndex.

This workflow implements the product gap detection logic with multi-step execution.
"""

from typing import Any, Dict, Optional
from llama_index.core.workflow import (
    Workflow,
    StartEvent,
    StopEvent,
    Event,
    step,
    Context
)

from app import get_logger
from app.database.base import SessionLocal
from app.services.schema_service import SchemaService
from .agents import (
    analyze_query,
    detect_format,
    plan_retrieval,
    generate_answer,
    RetrievalPlan
)
from .services import DataRetrievalService

logger = get_logger(__name__)


# Define custom events for workflow steps
class QueryAnalyzedEvent(Event):
    """Event triggered after query analysis is complete."""
    query: str
    analysis: Any


class FormatDetectedEvent(Event):
    """Event triggered after format detection is complete."""
    query: str
    analysis: Any
    format_info: Any


class RetrievalPlanEvent(Event):
    """Event triggered when retrieval planning is needed."""
    query: str
    analysis: Any
    format_info: Any
    plan: RetrievalPlan


class DataRetrievedEvent(Event):
    """Event triggered after data retrieval is complete."""
    query: str
    analysis: Any
    format_info: Any
    retrieved_data: Optional[Dict[str, Any]]


class SkipRetrievalEvent(Event):
    """Event triggered when data retrieval is not needed."""
    query: str
    analysis: Any
    format_info: Any


class ProductGapWorkflow(Workflow):
    """
    Product Gap Detection Workflow using LlamaIndex.
    
    Flow:
    1. Start -> Query Analysis -> Format Detection -> (Conditional) Data Retrieval -> Generate Answer
    """

    def __init__(self, user_id: int = 1, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        
        # Load table schemas
        db_session = SessionLocal()
        try:
            schema_service = SchemaService(db_session)
            self.table_schemas = schema_service.get_all_available_schemas(user_id)
            logger.info(f"Loaded {len(self.table_schemas)} table schemas")
        finally:
            db_session.close()

    @step
    async def start(self, ctx: Context, ev: StartEvent) -> StopEvent:
        """
        Execute the entire workflow sequentially.
        """
        query = ev.query
        logger.info(f"🚀 Workflow started with query: {query}")
        
        # Step 1: Query Analysis
        logger.info("▶️  Step: Query Analysis")
        analysis = await analyze_query(query)
        logger.info(f"✓ Query Analysis complete: needs_data={analysis.needs_data_retrieval}")
        
        # Step 2: Format Detection
        logger.info("▶️  Step: Format Detection")
        format_info = await detect_format(query)
        logger.info(f"✓ Format Detection complete: {format_info.format_type}")
        
        # Step 3: Conditional Data Retrieval
        retrieved_data = None
        if analysis.needs_data_retrieval:
            logger.info("▶️  Step: Retrieval Planning")
            plan = await plan_retrieval(query, self.table_schemas)
            logger.info(f"✓ Retrieval Planning complete: {len(plan.sql_queries)} queries")
            
            logger.info("▶️  Step: Data Retrieval")
            db_session = SessionLocal()
            try:
                service = DataRetrievalService(db_session)
                retrieved_data = service.execute_retrieval_plan(plan, format="json")
                logger.info(f"✓ Data Retrieval complete: {retrieved_data['total_rows']} rows")
            finally:
                db_session.close()
        
        # Step 4: Generate Answer
        logger.info("▶️  Step: Generate Answer")
        
        # Build context string
        context_parts = [f"Query: {query}"]
        
        if format_info:
            context_parts.append(f"\nDesired Format: {format_info.format_type}")
            context_parts.append(f"Format Details: {format_info.format_details}")
        
        if analysis:
            context_parts.append(f"\nQuery Type: {analysis.query_type}")
            context_parts.append(f"Analysis Type: {analysis.analysis_type}")
        
        if retrieved_data:
            context_parts.append(f"\nRetrieved Data ({retrieved_data['total_rows']} rows):")
            context_parts.append(f"\nData are: <data>{retrieved_data['data']}</data>")
            context_parts.append(f"\nReasoning: {retrieved_data['reasoning']}")
            
            # Add data summary
            for key, value in retrieved_data['data'].items():
                if not key.endswith('_error'):
                    context_parts.append(f"\n{key}: {str(value)[:500]}...")  # Truncate for context
        
        context = "\n".join(context_parts)
        
        # Generate final answer using the writer team
        answer = await generate_answer(context, format_info.format_type if format_info else "markdown")
        
        logger.info("✓ Answer generation complete")
        logger.info("🏁 Workflow completed")
        
        return StopEvent(result=answer)
