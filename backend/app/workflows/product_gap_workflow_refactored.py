"""
Product Gap Detection Workflow using refactored services.

This workflow intelligently analyzes product gaps with conditional execution.
"""

from typing import Optional

from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.workflow.condition import Condition
from agno.workflow.parallel import Parallel
from agno.workflow.step import Step
from agno.workflow.types import StepInput, StepOutput
from agno.workflow.workflow import Workflow

from app import get_logger
from app.config import SETTINGS
from app.database.base import SessionLocal
from app.workflows.agents.nlp import create_nlp_analysis_agent
from app.workflows.agents.output_format import create_output_format_agent
from app.workflows.agents.query_analyzer import create_query_analyzer_agent
from app.workflows.agents.retrieval_planner import create_retrieval_planner_agent
from app.workflows.steps.data_retrieval_refactored import execute_data_retrieval
from app.workflows.teams.writer import create_answer_writer_team
from app.services.schema_service import SchemaService

logger = get_logger(__name__)


# ============================================================================
# CONDITION EVALUATORS
# ============================================================================

def needs_data_retrieval(step_input: StepInput) -> bool:
    """
    Evaluate if data retrieval is needed based on query analysis.
    Query Analyzer returns structured QueryAnalysis model.
    """
    try:
        return step_input.previous_step_outputs.get("QueryAnalysis").needs_data_retrieval
    except Exception as e:
        logger.error(f"[needs_data_retrieval] | [user_id=None] | [company_id=None] | Error: {e}")
        return False


def needs_nlp_analysis(step_input: StepInput) -> bool:
    """
    Evaluate if NLP analysis is needed based on query analysis.
    Query Analyzer returns structured QueryAnalysis model.
    """
    try:
        return step_input.previous_step_outputs.get("QueryAnalysis").needs_nlp_analysis
    except Exception as e:
        logger.error(f"[needs_nlp_analysis] | [user_id=None] | [company_id=None] | Error: {e}")
        return False


# ============================================================================
# STEP EXECUTORS
# ============================================================================

def send_to_writer_team(step_input: StepInput) -> StepOutput:
    """
    Prepare data and format information for the writer team.
    Gets data from retrieval/NLP steps and format from format detection.
    """
    prev_steps = step_input.previous_step_outputs.get("AnalysisAndFormatDetection")
    
    # Get format detection output
    format_detection = prev_steps.get("FormatDetection")
    
    # Get data from various steps (if they ran)
    data_retrieval = None
    nlp_analysis = None
    
    try:
        data_retrieval = step_input.previous_step_outputs.get("DataRetrieval")
    except Exception:
        pass
    
    try:
        nlp_analysis = step_input.previous_step_outputs.get("NLPAnalysis")
    except Exception:
        pass
    
    report = f"""Writer Team Context:
Expected output Format: {format_detection}
Data: {data_retrieval}
Analysis: {nlp_analysis}"""
    
    logger.info(f"[send_to_writer_team] | [user_id=None] | [company_id=None] | Prepared context for writer team")
    
    return StepOutput(content=report)


def send_debugging(step_input: StepInput) -> StepOutput:
    """Debug step to inspect previous outputs."""
    logger.debug(f"[send_debugging] | [user_id=None] | [company_id=None] | Previous outputs: {step_input.previous_step_outputs}")
    return StepOutput(content=step_input.previous_step_outputs)


# ============================================================================
# WORKFLOW CREATION
# ============================================================================

def create_product_gap_workflow(
    db_file: str = "memory.db",
    user_id: Optional[str] = None
) -> Workflow:
    """
    Create the Product Gap Detection Workflow with conditional execution.
    
    Architecture:
    1. Parallel: Query Analysis + Format Detection (both always run)
    2. Data Retrieval (conditional):
       2a. Retrieval Planning - LLM decides what data to fetch
       2b. Data Retrieval - Executor fetches raw data (no LLM)
    3. NLP Analysis (conditional) - analyze raw data if needed
    4. Send to Writer Team (always) - prepare data with format info
    5. Answer Writer Team (always) - creates final answer
    
    Args:
        db_file: SQLite database path for workflow persistence
        user_id: Optional user ID for user-specific datasets
    
    Returns:
        Configured Workflow instance
    """
    logger.info(f"[create_product_gap_workflow] | [user_id={user_id or 'None'}] | [company_id=None] | Creating workflow")
    
    model = OpenAIChat(id="gpt-4o-mini", api_key=SETTINGS.OPENAI_API_KEY)
    db = SqliteDb(session_table="product_gap_workflow_session", db_file=db_file)
    
    # Create all agents
    query_analyzer = create_query_analyzer_agent(model)
    
    # Fetch all available table schemas using refactored service
    db_session = SessionLocal()
    try:
        schema_service = SchemaService(db_session)
        table_schemas = schema_service.get_all_available_schemas(user_id)
        logger.info(f"[create_product_gap_workflow] | [user_id={user_id or 'None'}] | [company_id=None] | Loaded schemas")
    finally:
        db_session.close()
    
    retrieval_planner = create_retrieval_planner_agent(model, table_schemas=table_schemas)
    nlp_analysis = create_nlp_analysis_agent(model)
    format_detection = create_output_format_agent(model)
    answer_writers = create_answer_writer_team(model)
    
    # Define workflow steps
    query_analysis_step = Step(
        name="QueryAnalysis",
        description="Analyze query to determine execution path",
        agent=query_analyzer,
    )
    
    retrieval_planning_step = Step(
        name="RetrievalPlanning",
        description="Plan data retrieval strategy",
        agent=retrieval_planner,
    )
    
    # Data retrieval step now uses refactored service
    def execute_data_retrieval_with_session(step_input: StepInput) -> StepOutput:
        """Wrapper to provide database session to data retrieval."""
        db_session = SessionLocal()
        try:
            return execute_data_retrieval(step_input, db_session)
        finally:
            db_session.close()
    
    data_retrieval_step = Step(
        name="DataRetrieval",
        description="Execute data retrieval and return raw data",
        executor=execute_data_retrieval_with_session,
    )
    
    nlp_analysis_step = Step(
        name="NLPAnalysis",
        description="Perform NLP analysis on reviews",
        agent=nlp_analysis,
    )
    
    format_detection_step = Step(
        name="FormatDetection",
        description="Determine best output format",
        agent=format_detection,
    )

    send_to_writer_team_step = Step(
        name="SendToWriterTeam",
        description="Send data to writer team",
        executor=send_to_writer_team,
    )

    debugging_step = Step(
        name="Debugging",
        description="Debugging step",
        executor=send_debugging,
    )

    answer_writing_step = Step(
        name="AnswerWriting",
        description="Write final formatted answer",
        team=answer_writers,
    )
    
    # Build workflow with conditional execution
    workflow = Workflow(
        name="Product Gap Detection Workflow",
        description="Intelligent workflow for analyzing product gaps with conditional step execution",
        steps=[
            # Step 1: Run Query Analysis and Format Detection in parallel
            Parallel(
                query_analysis_step,
                format_detection_step,
                name="AnalysisAndFormatDetection",
                description="Analyze query and detect format in parallel",
            ),
            
            # Step 2: Data Retrieval if needed (split into planning + execution)
            Condition(
                name="DataRetrievalCondition",
                description="Retrieve data if query analysis indicates it's needed",
                evaluator=needs_data_retrieval,
                steps=[
                    retrieval_planning_step,  # LLM plans what to retrieve
                    data_retrieval_step,      # Executor fetches raw data
                ],
            ),
            
            # Step 3: NLP Analysis if needed (runs after data retrieval)
            Condition(
                name="NLPAnalysisCondition",
                description="Perform NLP analysis on retrieved data if needed",
                evaluator=needs_nlp_analysis,
                steps=[nlp_analysis_step],
            ),
            
            # Step 4: Send to writer team (uses format detection output)
            send_to_writer_team_step,
            
            # Step 5: Answer Writing
            answer_writing_step,
        ],
        db=db,
    )
    
    logger.info(f"[create_product_gap_workflow] | [user_id={user_id or 'None'}] | [company_id=None] | Workflow created successfully")
    
    return workflow
