"""
Product Gap Detection Workflow using LangChain and LangGraph.

This workflow intelligently analyzes product gaps with conditional execution.
"""

from typing import Literal, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from sqlalchemy.orm import Session

from app import get_logger
from app.config import SETTINGS
from app.database.base import SessionLocal
from app.services.schema_service import SchemaService
from app.langchain_workflow.agents.query_analyzer import create_query_analyzer_agent
from app.langchain_workflow.agents.retrieval_planner import create_retrieval_planner_agent
from app.langchain_workflow.agents.nlp import create_nlp_analysis_agent
from app.langchain_workflow.agents.output_format import create_output_format_agent
from app.langchain_workflow.teams.writer import create_answer_writer_team
from app.langchain_workflow.steps.data_retrieval import DataRetrievalService

logger = get_logger(__name__)


# ============================================================================
# STATE DEFINITION
# ============================================================================

class WorkflowState(TypedDict):
    """State for the product gap workflow."""
    query: str
    query_analysis: dict
    format_detection: dict
    retrieval_plan: dict
    retrieved_data: dict
    nlp_analysis: dict
    writer_context: str
    final_answer: str
    user_id: int


# ============================================================================
# NODE FUNCTIONS
# ============================================================================

def analyze_query_node(state: WorkflowState) -> WorkflowState:
    """Analyze the user query to determine workflow path."""
    logger.info(f"[analyze_query_node] | [user_id={state.get('user_id')}] | Analyzing query")
    
    model = ChatOpenAI(model="gpt-4o-mini", api_key=SETTINGS.OPENAI_API_KEY)
    analyzer = create_query_analyzer_agent(model)
    
    result = analyzer.invoke({"query": state["query"]})
    
    logger.info(f"[analyze_query_node] | [user_id={state.get('user_id')}] | Analysis: {result}")
    
    return {
        **state,
        "query_analysis": result.model_dump() if hasattr(result, "model_dump") else result
    }


def detect_format_node(state: WorkflowState) -> WorkflowState:
    """Detect the best output format for the answer."""
    logger.info(f"[detect_format_node] | [user_id={state.get('user_id')}] | Detecting format")
    
    model = ChatOpenAI(model="gpt-4o-mini", api_key=SETTINGS.OPENAI_API_KEY)
    format_detector = create_output_format_agent(model)
    
    result = format_detector.invoke({"query": state["query"]})
    
    logger.info(f"[detect_format_node] | [user_id={state.get('user_id')}] | Format: {result}")
    
    return {
        **state,
        "format_detection": result.model_dump() if hasattr(result, "model_dump") else result
    }


def plan_retrieval_node(state: WorkflowState) -> WorkflowState:
    """Plan data retrieval strategy."""
    logger.info(f"[plan_retrieval_node] | [user_id={state.get('user_id')}] | Planning retrieval")
    
    # Get table schemas
    db_session = SessionLocal()
    try:
        schema_service = SchemaService(db_session)
        table_schemas = schema_service.get_all_available_schemas(state.get("user_id", 1))
    finally:
        db_session.close()
    
    model = ChatOpenAI(model="gpt-4o-mini", api_key=SETTINGS.OPENAI_API_KEY)
    planner = create_retrieval_planner_agent(model, table_schemas=table_schemas)
    
    result = planner.invoke({"query": state["query"]})
    
    logger.info(f"[plan_retrieval_node] | [user_id={state.get('user_id')}] | Plan: {result}")
    
    return {
        **state,
        "retrieval_plan": result.model_dump() if hasattr(result, "model_dump") else result
    }


def retrieve_data_node(state: WorkflowState) -> WorkflowState:
    """Execute data retrieval."""
    logger.info(f"[retrieve_data_node] | [user_id={state.get('user_id')}] | Retrieving data")
    
    db_session = SessionLocal()
    try:
        service = DataRetrievalService(db_session)
        
        # Convert dict back to object for compatibility
        class PlanObj:
            def __init__(self, d):
                self.__dict__ = d
        
        plan = PlanObj(state["retrieval_plan"])
        result = service.execute_retrieval_plan(plan, user_id=str(state.get("user_id", 1)))
        
        logger.info(f"[retrieve_data_node] | [user_id={state.get('user_id')}] | Retrieved {result.get('total_rows', 0)} rows")
        
        return {
            **state,
            "retrieved_data": result
        }
    finally:
        db_session.close()


def nlp_analysis_node(state: WorkflowState) -> WorkflowState:
    """Perform NLP analysis on retrieved data."""
    logger.info(f"[nlp_analysis_node] | [user_id={state.get('user_id')}] | Performing NLP analysis")
    
    model = ChatOpenAI(model="gpt-4o-mini", api_key=SETTINGS.OPENAI_API_KEY)
    nlp_agent = create_nlp_analysis_agent(model)
    
    # Prepare input with retrieved data
    retrieved_data = state.get("retrieved_data", {})
    enhanced_input = f"""Original Query: {state['query']}

Retrieved Data:
{retrieved_data}

Please perform NLP analysis on the retrieved data above."""
    
    result = nlp_agent.invoke({"input": enhanced_input})
    
    logger.info(f"[nlp_analysis_node] | [user_id={state.get('user_id')}] | Analysis complete")
    
    return {
        **state,
        "nlp_analysis": {"output": result.get("output", "")}
    }


def prepare_writer_context_node(state: WorkflowState) -> WorkflowState:
    """Prepare context for the writer team."""
    logger.info(f"[prepare_writer_context_node] | [user_id={state.get('user_id')}] | Preparing context")
    
    format_detection = state.get("format_detection", {})
    retrieved_data = state.get("retrieved_data", {})
    nlp_analysis = state.get("nlp_analysis", {})
    
    context = f"""Writer Team Context:

Original Query: {state['query']}

Expected Output Format: {format_detection.get('primary_format', 'markdown')}
Format Reasoning: {format_detection.get('reasoning', 'N/A')}

Retrieved Data:
{retrieved_data}

NLP Analysis:
{nlp_analysis}

Please create a comprehensive answer in the specified format."""
    
    return {
        **state,
        "writer_context": context
    }


def write_answer_node(state: WorkflowState) -> WorkflowState:
    """Write the final answer using the writer team."""
    logger.info(f"[write_answer_node] | [user_id={state.get('user_id')}] | Writing answer")
    
    model = ChatOpenAI(model="gpt-4o-mini", api_key=SETTINGS.OPENAI_API_KEY)
    writer_team = create_answer_writer_team(model)
    
    format_detection = state.get("format_detection", {})
    primary_format = format_detection.get("primary_format", "markdown")
    
    result = writer_team.invoke({
        "messages": [HumanMessage(content=state["writer_context"])],
        "format_type": primary_format
    })
    
    final_output = result.get("final_output", "")
    
    logger.info(f"[write_answer_node] | [user_id={state.get('user_id')}] | Answer complete")
    
    return {
        **state,
        "final_answer": final_output
    }


# ============================================================================
# CONDITIONAL ROUTING
# ============================================================================

def should_retrieve_data(state: WorkflowState) -> Literal["retrieve", "skip_retrieve"]:
    """Determine if data retrieval is needed."""
    query_analysis = state.get("query_analysis", {})
    needs_retrieval = query_analysis.get("needs_data_retrieval", False)
    
    logger.info(f"[should_retrieve_data] | Needs retrieval: {needs_retrieval}")
    
    return "retrieve" if needs_retrieval else "skip_retrieve"


def should_perform_nlp(state: WorkflowState) -> Literal["nlp", "skip_nlp"]:
    """Determine if NLP analysis is needed."""
    query_analysis = state.get("query_analysis", {})
    needs_nlp = query_analysis.get("needs_nlp_analysis", False)
    
    logger.info(f"[should_perform_nlp] | Needs NLP: {needs_nlp}")
    
    return "nlp" if needs_nlp else "skip_nlp"


# ============================================================================
# WORKFLOW CREATION
# ============================================================================

def create_product_gap_workflow(user_id: int = 1):
    """
    Create the Product Gap Detection Workflow using LangGraph.
    
    Architecture:
    1. Query Analysis + Format Detection (parallel conceptually, sequential in implementation)
    2. Data Retrieval (conditional):
       2a. Retrieval Planning - LLM decides what data to fetch
       2b. Data Retrieval - Executor fetches raw data
    3. NLP Analysis (conditional) - analyze raw data if needed
    4. Prepare Writer Context - combine all data
    5. Answer Writing - creates final answer
    
    Args:
        user_id: Optional user ID for user-specific datasets
    
    Returns:
        Compiled LangGraph workflow
    """
    logger.info(f"[create_product_gap_workflow] | [user_id={user_id}] | Creating workflow")
    
    # Create workflow graph
    workflow = StateGraph(WorkflowState)
    
    # Add all nodes
    workflow.add_node("analyze_query", analyze_query_node)
    workflow.add_node("detect_format", detect_format_node)
    workflow.add_node("plan_retrieval", plan_retrieval_node)
    workflow.add_node("retrieve_data", retrieve_data_node)
    workflow.add_node("nlp_analysis", nlp_analysis_node)
    workflow.add_node("prepare_context", prepare_writer_context_node)
    workflow.add_node("write_answer", write_answer_node)
    
    # Build workflow with conditional execution
    workflow.add_edge(START, "analyze_query")
    workflow.add_edge("analyze_query", "detect_format")
    
    # Conditional: Data retrieval
    workflow.add_conditional_edges(
        "detect_format",
        should_retrieve_data,
        {
            "retrieve": "plan_retrieval",
            "skip_retrieve": "prepare_context"
        }
    )
    
    workflow.add_edge("plan_retrieval", "retrieve_data")
    
    # Conditional: NLP analysis
    workflow.add_conditional_edges(
        "retrieve_data",
        should_perform_nlp,
        {
            "nlp": "nlp_analysis",
            "skip_nlp": "prepare_context"
        }
    )
    
    workflow.add_edge("nlp_analysis", "prepare_context")
    workflow.add_edge("prepare_context", "write_answer")
    workflow.add_edge("write_answer", END)
    
    # Compile and return
    compiled_workflow = workflow.compile()
    
    logger.info(f"[create_product_gap_workflow] | [user_id={user_id}] | Workflow created successfully")
    
    return compiled_workflow


# ============================================================================
# EXECUTION HELPER
# ============================================================================

def run_workflow(query: str, user_id: int = 1) -> dict:
    """
    Execute the workflow with a query.
    
    Args:
        query: User query to process
        user_id: User ID for user-specific data
    
    Returns:
        Final workflow state with answer
    """
    workflow = create_product_gap_workflow(user_id)
    
    initial_state = {
        "query": query,
        "user_id": user_id,
        "query_analysis": {},
        "format_detection": {},
        "retrieval_plan": {},
        "retrieved_data": {},
        "nlp_analysis": {},
        "writer_context": "",
        "final_answer": ""
    }
    
    result = workflow.invoke(initial_state)
    return result

