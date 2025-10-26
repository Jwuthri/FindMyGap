from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb
from agno.workflow.types import StepInput, StepOutput
from agno.workflow.workflow import Workflow
from agno.workflow.step import Step
from agno.workflow.condition import Condition
from agno.workflow.parallel import Parallel

from app.workflows.agents.query_analyzer import create_query_analyzer_agent
from app.workflows.agents.retriever_data import create_database_retrieval_agent
from app.workflows.agents.nlp import create_nlp_analysis_agent
from app.workflows.agents.output_format import create_output_format_agent
from app.workflows.teams.writer import create_answer_writer_team
from app.config import SETTINGS
from app import get_logger

logger = get_logger("workflows.product_gap_workflow")

# ============================================================================
# CONDITION EVALUATORS
# ============================================================================

def needs_data_retrieval(step_input: StepInput) -> bool:
    """
    Evaluate if data retrieval is needed based on query analysis.
    Query Analyzer returns structured QueryAnalysis model.
    """
    breakpoint()
    try:
        return step_input.previous_step_outputs.get("QueryAnalysis").needs_data_retrieval
    except Exception:
        return False


def needs_nlp_analysis(step_input: StepInput) -> bool:
    """
    Evaluate if NLP analysis is needed based on query analysis.
    Query Analyzer returns structured QueryAnalysis model.
    """
    try:
        return step_input.previous_step_outputs.get("QueryAnalysis").needs_nlp_analysis
    except Exception:
        return False

# ============================================================================
# SEND TO TEAM
# ============================================================================

def send_to_writer_team(step_input: StepInput) -> StepOutput:
    """
    Prepare data and format information for the writer team.
    Gets data from retrieval/NLP steps and format from format detection.
    """
    breakpoint()
    prev_steps = step_input.previous_step_outputs.get("AnalysisAndFormatDetection")
    # Get format detection output
    format_detection = prev_steps.get("FormatDetection")
    
    # Get data from various steps (if they ran)
    try:
        data_retrieval = step_input.previous_step_outputs("DataRetrieval")
    except Exception:
        data_retrieval = None
    
    try:
        nlp_analysis =  step_input.previous_step_outputs("NLPAnalysis")
    except Exception:
        nlp_analysis = None
    
    report = f"Writer Team Context:\nExpected output Format: {format_detection}\nData: {data_retrieval}\nAnalysis: {nlp_analysis}"
    
    return StepOutput(content=report)


def send_debugging(step_input: StepInput) -> StepOutput:
    breakpoint()
    
    return StepOutput(content=step_input.previous_step_outputs)


def send_to_data_nlp(step_input: StepInput) -> StepOutput:
    prev_steps = step_input.previous_step_outputs.get("AnalysisAndFormatDetection")
    query_analysis = prev_steps.get("QueryAnalysis")
    # format_detection = prev_steps.get("FormatDetection")
    
    return StepOutput(content=query_analysis)


def send_to_data_nlp(step_input: StepInput) -> StepOutput:
    prev_steps = step_input.previous_step_outputs.get("AnalysisAndFormatDetection")
    query_analysis = prev_steps.get("QueryAnalysis")
    # format_detection = prev_steps.get("FormatDetection")
    
    return StepOutput(content=query_analysis)

# ============================================================================
# WORKFLOW CREATION
# ============================================================================

def create_product_gap_workflow(db_file: str = "tmp/product_gap_workflow.db") -> Workflow:
    """
    Create the Product Gap Detection Workflow with conditional execution.
    
    Architecture:
    1. Parallel: Query Analysis + Format Detection (both always run)
    2. Data Retrieval (conditional) - fetch data if needed
    3. NLP Analysis (conditional) - analyze data if needed
    4. Send to Writer Team (always) - prepare data with format info
    5. Answer Writer Team (always) - creates final answer
    
    Args:
        api_key: OpenAI API key
        db_file: SQLite database path for workflow persistence
    
    Returns:
        Configured Workflow instance
    """
    model = OpenAIChat(id="gpt-5-mini", api_key=SETTINGS.OPENAI_API_KEY)
    db = SqliteDb(session_table="product_gap_workflow_session", db_file=db_file)
    
    # Create all agents
    query_analyzer = create_query_analyzer_agent(model)
    data_retrieval = create_database_retrieval_agent(model)
    nlp_analysis = create_nlp_analysis_agent(model)
    format_detection = create_output_format_agent(model)
    answer_writers = create_answer_writer_team(model)
    
    # Define workflow steps
    query_analysis_step = Step(
        name="QueryAnalysis",
        description="Analyze query to determine execution path",
        agent=query_analyzer,
    )
    
    data_retrieval_step = Step(
        name="DataRetrieval",
        description="Retrieve review data from database",
        agent=data_retrieval,
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
    
    # Build workflow with conditional execution using Condition and Parallel
    workflow = Workflow(
        name="Product Gap Detection Workflow",
        description="Intelligent workflow for analyzing product gaps with conditional step execution and data sufficiency checking",
        steps=[
            # Step 1: Run Query Analysis and Format Detection in parallel
            Parallel(
                query_analysis_step,
                format_detection_step,
                name="AnalysisAndFormatDetection",
                description="Analyze query and detect format in parallel",
            ),
            
            # debugging_step,
            # Step 2: Data Retrieval if needed
            Condition(
                name="DataRetrievalCondition",
                description="Retrieve data if query analysis indicates it's needed",
                evaluator=needs_data_retrieval,
                steps=[data_retrieval_step],
            ),
            debugging_step,

            # Step 3: NLP Analysis if needed (runs after data retrieval)
            Condition(
                name="NLPAnalysisCondition",
                description="Perform NLP analysis on retrieved data if needed",
                evaluator=needs_nlp_analysis,
                steps=[nlp_analysis_step],
            ),
            debugging_step,
            # Step 4: Send to writer team (uses format detection output)
            send_to_writer_team_step,
            
            # Step 5: Answer Writing
            answer_writing_step,
        ],
        db=db,
    )
    
    return workflow
