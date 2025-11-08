"""
Main workflow definition using LlamaIndex.

This workflow implements the product gap detection logic with multi-step execution.
"""

import json
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
from app.workflow.agents import (
    analyze_query,
    detect_format,
    plan_retrieval,
    generate_answer,
    RetrievalPlan,
    QueryAnalysis
)
from app.workflow.services import DataRetrievalService
from app.workflow.services.nlp_service import NLPService

logger = get_logger(__name__)


def _summarize_nlp_results(nlp_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Summarize NLP results to reduce token consumption.
    Keeps key insights but removes verbose details.
    """
    if not nlp_results or "tool_results" not in nlp_results:
        return nlp_results
    
    summarized = {
        "tool_results": {},
        "total_tools_requested": nlp_results.get("total_tools_requested", 0),
        "total_tools_executed": nlp_results.get("total_tools_executed", 0),
        "deduplicated": nlp_results.get("deduplicated", 0),
        "successful": nlp_results.get("successful", 0)
    }
    
    for tool_key, tool_result in nlp_results["tool_results"].items():
        if "error" in tool_result:
            summarized["tool_results"][tool_key] = tool_result
            continue
        
        # Summarize based on tool type
        if "identify_features" in tool_key:
            summarized["tool_results"][tool_key] = {
                "feature_requests": {
                    "count": tool_result.get("feature_requests", {}).get("count", 0),
                    "total_unique": tool_result.get("feature_requests", {}).get("total_unique", 0)
                },
                "pain_points": {
                    "count": tool_result.get("pain_points", {}).get("count", 0)
                },
                "product_gaps": {
                    "count": tool_result.get("product_gaps", {}).get("count", 0)
                },
                "total_analyzed": tool_result.get("total_analyzed", 0)
            }
        
        elif "cluster_reviews" in tool_key:
            clusters = tool_result.get("clusters", [])
            # Keep only top 3 clusters with limited samples
            summarized_clusters = []
            for cluster in clusters[:3]:
                rating_dist = cluster.get("rating_distribution", {})
                # Calculate weighted average rating
                if rating_dist:
                    total_ratings = sum(rating_dist.values())
                    weighted_sum = sum(rating * count for rating, count in rating_dist.items())
                    avg_rating = weighted_sum / total_ratings if total_ratings > 0 else None
                else:
                    avg_rating = None
                
                summarized_clusters.append({
                    "cluster_id": cluster.get("cluster_id"),
                    "size": cluster.get("size"),
                    "sample_texts": cluster.get("sample_texts", [])[:3],  # Only 3 samples
                    "avg_rating": round(avg_rating, 2) if avg_rating else None
                })
            
            summarized["tool_results"][tool_key] = {
                "clusters": summarized_clusters,
                "num_clusters": tool_result.get("num_clusters", 0),
                "total_documents": tool_result.get("total_documents", 0)
            }
        
        elif "compute_tfidf" in tool_key:
            top_terms = tool_result.get("top_terms", [])
            # Keep only top 10 terms
            summarized["tool_results"][tool_key] = {
                "top_terms": top_terms[:10],
                "total_documents": tool_result.get("total_documents", 0),
                "vocabulary_size": tool_result.get("vocabulary_size", 0)
            }
        
        elif "analyze_sentiment" in tool_key:
            summarized["tool_results"][tool_key] = {
                "total_reviews": tool_result.get("total_reviews", 0),
                "rating_stats": tool_result.get("rating_stats", {}),
                "sentiment_distribution": tool_result.get("sentiment_distribution", {})
            }
        
        else:
            # Keep as-is for unknown tools
            summarized["tool_results"][tool_key] = tool_result
    
    return summarized


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


class NLPAnalysisCompleteEvent(Event):
    """Event triggered after NLP analysis is complete."""
    query: str
    analysis: Any
    format_info: Any
    retrieved_data: Optional[Dict[str, Any]]
    nlp_results: Optional[Dict[str, Any]]


class ProductGapWorkflow(Workflow):
    """
    Product Gap Detection Workflow using LlamaIndex.
    
    Multi-step Flow:
    1. Start -> Query Analysis
    2. Query Analysis -> Format Detection  
    3. Format Detection -> Retrieval Planning (if needed) OR Skip Retrieval
    4. Retrieval Planning -> Data Retrieval
    5. Data Retrieval -> NLP Analysis
    6. NLP Analysis OR Skip Retrieval -> Generate Answer
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
    async def nlp_analysis(self, ctx: Context, ev: DataRetrievedEvent) -> NLPAnalysisCompleteEvent:
        """Step 5: Perform NLP analysis if needed."""
        logger.info("▶️  Step 5: NLP Analysis")
        
        # Check if NLP analysis is needed
        if not ev.analysis.needs_nlp_analysis:
            logger.info("Skipping NLP analysis (not needed)")
            return NLPAnalysisCompleteEvent(
                query=ev.query,
                analysis=ev.analysis,
                format_info=ev.format_info,
                retrieved_data=ev.retrieved_data,
                nlp_results=None
            )
        
        # Import here to avoid circular dependency
        from app.workflow.agents.nlp_agent import perform_nlp_analysis
        
        # Step 5a: Agent selects which NLP tools to use
        nlp_plan = await perform_nlp_analysis(
            query=ev.query,
            analysis=ev.analysis,
            retrieved_data=ev.retrieved_data
        )
        
        logger.info(f"✓ NLP Planning complete: {len(nlp_plan.get('tool_calls', []))} tool calls planned")
        
        # Step 5b: Execute the NLP tools on the data
        nlp_service = NLPService()
        nlp_results = nlp_service.execute_tool_calls(
            tool_calls=nlp_plan.get('tool_calls', []),
            retrieved_data=ev.retrieved_data
        )
        
        # Combine plan and results
        nlp_results['plan'] = nlp_plan
        
        logger.info(f"✓ NLP Execution complete: {nlp_results.get('successful', 0)} tools succeeded")
        
        return NLPAnalysisCompleteEvent(
            query=ev.query,
            analysis=ev.analysis,
            format_info=ev.format_info,
            retrieved_data=ev.retrieved_data,
            nlp_results=nlp_results
        )

    @step
    async def generate_final_answer(self, ctx: Context, ev: NLPAnalysisCompleteEvent | SkipRetrievalEvent) -> StopEvent:
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
        if isinstance(ev, NLPAnalysisCompleteEvent) and ev.retrieved_data:
            retrieved_data = ev.retrieved_data
            
            # Convert JSON data to CSV format for token efficiency (especially after NLP processing)
            formatted_data = {}
            for key, value in retrieved_data['data'].items():
                if key.endswith('_error'):
                    formatted_data[key] = value
                elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                    # Convert list of dicts to CSV format
                    formatted_data[key] = DataRetrievalService._format_as_csv(value)
                else:
                    # Already CSV string or other format
                    formatted_data[key] = value
            
            context_parts.append(f"\nRetrieved Data contains ({retrieved_data['total_rows']} rows): <data>{formatted_data}</data>")
            context_parts.append(f"\nReasoning: {retrieved_data['reasoning']}")
            context_parts.append(f"\nNlp analysis results: <nlp>{json.dumps(ev.nlp_results, indent=2)}</nlp>")
            
            # Summarize NLP results to reduce token consumption
            # summarized_nlp = _summarize_nlp_results(ev.nlp_results) if ev.nlp_results else None
            # context_parts.append(f"\nNlp analysis results: <nlp>{summarized_nlp}</nlp>")

            # # Add data summary
            # for key, value in formatted_data.items():
            #     if not key.endswith('_error'):
            #         # Show first 500 chars of CSV
            #         context_parts.append(f"\n{key}: {str(value)[:500]}...")  # Truncate for context
        
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
