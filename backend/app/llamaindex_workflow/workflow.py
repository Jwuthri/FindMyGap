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
from llama_index.utils.workflow import draw_all_possible_flows

from app import get_logger
from app.database.base import SessionLocal
from app.services.schema_service import SchemaService
from app.llamaindex_workflow.agents import (
    analyze_query,
    detect_format,
    plan_retrieval,
    generate_answer,
    RetrievalPlan,
    QueryAnalysis
)
from app.llamaindex_workflow.services import DataRetrievalService

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
    
    Multi-step Flow:
    1. Start -> Query Analysis
    2. Query Analysis -> Format Detection  
    3. Format Detection -> Retrieval Planning (if needed) OR Skip Retrieval
    4. Retrieval Planning -> Data Retrieval
    5. Data Retrieval OR Skip Retrieval -> Generate Answer
    """

    def __init__(self, user_id: int = 1, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        
        # Load table schemas
        db_session = SessionLocal()
        try:
            schema_service = SchemaService(db_session)
            self.table_schemas = schema_service.get_all_available_schemas(user_id)
            logger.info(f"Loaded table schemas")
        finally:
            db_session.close()

    def draw_steps(self, filename: str = "workflow.html"):
        """Draw the workflow steps."""
        draw_all_possible_flows(self, filename=filename)

    @step
    async def start_workflow(self, ctx: Context, ev: StartEvent) -> QueryAnalyzedEvent:
        """Step 1: Analyze the incoming query."""
        query = ev.query
        logger.info(f"🚀 Workflow started with query: {query}")
        
        logger.info("▶️  Step 1: Query Analysis")
        analysis = await analyze_query(query)
        logger.info(f"✓ Query Analysis complete: needs_data={analysis.needs_data_retrieval}")
        
        return QueryAnalyzedEvent(query=query, analysis=analysis)

    @step
    async def detect_output_format(self, ctx: Context, ev: QueryAnalyzedEvent) -> FormatDetectedEvent:
        """Step 2: Detect the desired output format."""
        logger.info("▶️  Step 2: Format Detection")
        format_info = await detect_format(ev.query)
        logger.info(f"✓ Format Detection complete: {format_info.format_type}")
        
        return FormatDetectedEvent(
            query=ev.query,
            analysis=ev.analysis,
            format_info=format_info
        )

    @step
    async def plan_data_retrieval(self, ctx: Context, ev: FormatDetectedEvent) -> RetrievalPlanEvent | SkipRetrievalEvent:
        """Step 3: Plan data retrieval if needed, otherwise skip."""
        if not ev.analysis.needs_data_retrieval:
            logger.info("▶️  Step 3: Skipping data retrieval (not needed)")
            return SkipRetrievalEvent(
                query=ev.query,
                analysis=ev.analysis,
                format_info=ev.format_info
            )
        
        logger.info("▶️  Step 3: Retrieval Planning")
        plan = await plan_retrieval(ev.query, self.table_schemas, ev.analysis)
        logger.info(f"✓ Retrieval Planning complete: {len(plan.sql_queries)} queries")
        
        return RetrievalPlanEvent(
            query=ev.query,
            analysis=ev.analysis,
            format_info=ev.format_info,
            plan=plan
        )

    @step
    async def retrieve_data(self, ctx: Context, ev: RetrievalPlanEvent) -> DataRetrievedEvent:
        """Step 4: Execute data retrieval based on the plan."""
        logger.info("▶️  Step 4: Data Retrieval")
        
        # Choose format based on whether NLP analysis is needed
        data_format = "json" if ev.analysis.needs_nlp_analysis else "csv"
        logger.info(f"Using {data_format} format for data retrieval (NLP analysis: {ev.analysis.needs_nlp_analysis})")
        
        db_session = SessionLocal()
        try:
            service = DataRetrievalService(db_session)
            retrieved_data = service.execute_retrieval_plan(ev.plan, format=data_format)
            # retrieved_data2 = service.execute_retrieval_plan(ev.plan, format="csv")
            logger.info(f"✓ Data Retrieval complete: {retrieved_data['total_rows']} rows")
        finally:
            db_session.close()
        
        return DataRetrievedEvent(
            query=ev.query,
            analysis=ev.analysis,
            format_info=ev.format_info,
            retrieved_data=retrieved_data
        )

    @step
    async def nlp_analysis(self, ctx: Context, ev: DataRetrievedEvent) -> DataRetrievedEvent:
        """Step 5: Perform NLP analysis if needed."""
        # Check if NLP analysis is needed
        if not ev.analysis.needs_nlp_analysis:
            logger.info("▶️  Step 5: Skipping NLP analysis (not needed)")
            return ev
        
        logger.info("▶️  Step 5: NLP Analysis")
        
        # Import here to avoid circular dependency
        from app.llamaindex_workflow.agents import perform_nlp_analysis
        
        # Perform NLP analysis using the agent
        nlp_results = await perform_nlp_analysis(
            query=ev.query,
            analysis=ev.analysis,
            retrieved_data=ev.retrieved_data
        )
        
        logger.info(f"✓ NLP Analysis complete: {len(nlp_results.get('tool_calls', []))} tool calls")
        
        # Store NLP results in the retrieved_data for downstream use
        if ev.retrieved_data:
            ev.retrieved_data['nlp_analysis'] = nlp_results
        
        return ev

    @step
    async def generate_final_answer(self, ctx: Context, ev: DataRetrievedEvent | SkipRetrievalEvent) -> StopEvent:
        """Step 6: Generate the final answer using all collected information."""
        logger.info("▶️  Step 6: Generate Answer")
        
        # Build context string
        context_parts = [f"Query: {ev.query}"]
        
        if ev.format_info:
            context_parts.append(f"\nDesired Format: {ev.format_info.format_type}")
            context_parts.append(f"Format Details: {ev.format_info.format_details}")
        
        if ev.analysis:
            context_parts.append(f"\nQuery Type: {ev.analysis.query_type}")
            # context_parts.append(f"Analysis Type: {ev.analysis.analysis_type}")
        
        # Handle retrieved data if available
        if isinstance(ev, DataRetrievedEvent) and ev.retrieved_data:
            retrieved_data = ev.retrieved_data
            context_parts.append(f"\nRetrieved Data ({retrieved_data['total_rows']} rows):")
            context_parts.append(f"\nData are: <data>{retrieved_data['data']}</data>")
            context_parts.append(f"\nReasoning: {retrieved_data['reasoning']}")
            
            # Add data summary
            for key, value in retrieved_data['data'].items():
                if not key.endswith('_error'):
                    context_parts.append(f"\n{key}: {str(value)[:500]}...")  # Truncate for context
        
        context = "\n".join(context_parts)
        breakpoint()
        # Generate final answer using the writer team
        answer = await generate_answer(
            context, 
            ev.format_info.format_type if ev.format_info else "markdown"
        )
        
        logger.info("✓ Answer generation complete")
        logger.info("🏁 Workflow completed")
        
        return StopEvent(result=answer)

if __name__ == "__main__":
    workflow = ProductGapWorkflow()
    workflow.draw_steps("workflow.html")
