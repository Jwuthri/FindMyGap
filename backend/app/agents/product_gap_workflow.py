"""
Product Gap Detection Workflow System

Intelligent workflow that conditionally executes specialized agents based on query analysis.
Includes data sufficiency checking with automatic retry mechanism.

Architecture:
Query Analyzer → [Data Retrieval] → [Data Sufficiency Check] → [Retry if needed] → 
[NLP Analysis] → Output Format Detection → Answer Writer Team
"""

import asyncio
import json
from typing import Optional, AsyncIterator
from textwrap import dedent
from pydantic import BaseModel, Field

from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb
from agno.workflow.types import StepInput, StepOutput
from agno.workflow.workflow import Workflow
from agno.workflow.step import Step
from agno.workflow.condition import Condition
from agno.workflow.parallel import Parallel

# Import existing tools from teams.py
from app.agents.teams import (
    retrieve_reviews,
    filter_reviews_by_rating,
    filter_reviews_by_source,
    search_reviews_by_keyword,
    list_available_companies,
    compute_tfidf,
    analyze_sentiment_distribution,
    identify_feature_requests,
    cluster_similar_reviews,
    analyze_product_gaps,
    determine_best_output_format,
)

from app.config import SETTINGS


# ============================================================================
# PYDANTIC SCHEMAS FOR STRUCTURED OUTPUTS
# ============================================================================

class QueryAnalysis(BaseModel):
    """Query analysis result determining workflow execution path."""
    needs_data_retrieval: bool = Field(..., description="Whether to retrieve review data")
    needs_nlp_analysis: bool = Field(..., description="Whether to perform NLP analysis")
    company: Optional[str] = Field(None, description="Company name if applicable")
    query_type: str = Field(..., description="Type of query: data_only, analysis, general, etc")
    reasoning: str = Field(..., description="Brief explanation of routing decision")


class DataSufficiencyResult(BaseModel):
    """Evaluation of whether retrieved data is sufficient for analysis."""
    is_sufficient: bool = Field(..., description="Whether data is sufficient")
    current_count: int = Field(..., description="Current number of data points")
    recommended_count: int = Field(..., description="Recommended number of data points")
    reasoning: str = Field(..., description="Explanation of sufficiency determination")


# ============================================================================
# QUERY ANALYZER AGENT
# ============================================================================

def create_query_analyzer_agent(model: OpenAIChat) -> Agent:
    """
    Analyze user query to determine execution path.
    Pure reasoning agent with no tools.
    """
    return Agent(
        name="Query Analyzer",
        role="Analyze queries and route to appropriate workflow steps",
        model=model,
        description="""Analyze the user's question to determine what steps are needed.
        
        Determine:
        - Does this need data retrieval? (mentions specific company, asks for reviews, needs data)
        - Does this need NLP analysis? (asks for gaps, patterns, clustering, sentiment, features)
        - What company are they asking about?
        - What type of query is this?
        """,
        instructions=[
            "Read the user's question carefully",
            "Determine if data retrieval is needed (specific company queries, show reviews, etc)",
            "Determine if NLP analysis is needed (find gaps, analyze sentiment, cluster, etc)",
            "Extract company name if mentioned",
            "Classify query type",
            "Provide clear reasoning"
        ],
        output_schema=QueryAnalysis,
        markdown=False,
        debug_mode=False
    )


# ============================================================================
# DATABASE RETRIEVAL AGENT
# ============================================================================

def create_database_retrieval_agent(model: OpenAIChat) -> Agent:
    """
    Retrieve review data from database.
    """
    return Agent(
        name="Database Retrieval Agent",
        role="Fetch review data efficiently",
        model=model,
        description="""Retrieve review data based on query requirements.
        
        Available tools:
        - retrieve_reviews: Get reviews for a company
        - filter_reviews_by_rating: Filter by rating range
        - filter_reviews_by_source: Filter by platform
        - search_reviews_by_keyword: Search by keyword
        """,
        instructions=[
            "Use the most appropriate tool for the query",
            "Start with reasonable data limits (100 reviews default)",
            "Confirm retrieval with count",
            "Keep responses brief"
        ],
        tools=[
            retrieve_reviews,
            filter_reviews_by_rating,
            filter_reviews_by_source,
            search_reviews_by_keyword,
            list_available_companies
        ],
        markdown=False,
        debug_mode=False
    )


# ============================================================================
# DATA SUFFICIENCY EVALUATOR AGENT
# ============================================================================

def create_data_sufficiency_agent(model: OpenAIChat) -> Agent:
    """
    Evaluate if retrieved data is sufficient for planned analysis.
    """
    return Agent(
        name="Data Sufficiency Evaluator",
        role="Assess if data quantity is adequate for analysis",
        model=model,
        description="""Evaluate whether the retrieved data is sufficient for the planned NLP analysis.
        
        Consider:
        - Current data count vs analysis requirements
        - For clustering: need at least 20-30 reviews
        - For TF-IDF: need at least 10-15 reviews
        - For gap analysis: need at least 30-50 reviews
        - For sentiment distribution: 20+ reviews
        
        If insufficient, recommend 2x or 3x the current count (max 500).
        """,
        instructions=[
            "Analyze the current data count",
            "Consider what NLP analysis is planned",
            "Determine if count is sufficient",
            "If insufficient, recommend increased count",
            "Be conservative - prefer more data for better insights"
        ],
        output_schema=DataSufficiencyResult,
        markdown=False,
        debug_mode=False
    )


# ============================================================================
# NLP ANALYSIS AGENT
# ============================================================================

def create_nlp_analysis_agent(model: OpenAIChat) -> Agent:
    """
    Perform NLP and ML analysis on review data.
    """
    return Agent(
        name="NLP Analysis Agent",
        role="AI-powered text analytics and insight extraction",
        model=model,
        description="""Perform advanced NLP analysis on customer reviews.
        
        Available analyses:
        - compute_tfidf: Statistical term importance
        - analyze_sentiment_distribution: Rating/sentiment breakdown
        - identify_feature_requests: Extract feature requests and pain points
        - cluster_similar_reviews: Group reviews by theme
        - analyze_product_gaps: Deep gap analysis (best for "what's missing")
        """,
        instructions=[
            "Select the most relevant analysis tool for the query",
            "For 'product gaps' or 'what's missing', use analyze_product_gaps",
            "For 'feature requests', use identify_feature_requests",
            "For 'themes' or 'topics', use cluster_similar_reviews",
            "For 'sentiment', use analyze_sentiment_distribution",
            "Summarize key findings clearly"
        ],
        tools=[
            compute_tfidf,
            analyze_sentiment_distribution,
            identify_feature_requests,
            cluster_similar_reviews,
            analyze_product_gaps
        ],
        markdown=False,
        debug_mode=False
    )


# ============================================================================
# OUTPUT FORMAT DETECTION AGENT
# ============================================================================

def create_output_format_agent(model: OpenAIChat) -> Agent:
    """
    Determine best output format for the answer.
    """
    return Agent(
        name="Output Format Detection Agent",
        role="Determine optimal output format",
        model=model,
        description="""Analyze the query and data to determine the best output format.
        
        Formats:
        - markdown: General answers, explanations, reports
        - table: Structured data, lists, comparisons
        - chart: Distributions, trends, visualizations
        - json: API responses, structured exports
        """,
        instructions=[
            "Consider what format would be clearest",
            "If user asks for table/chart explicitly, honor that",
            "Default to markdown for general questions",
            "Use table for structured data",
            "Be concise"
        ],
        tools=[determine_best_output_format],
        markdown=False,
        debug_mode=False
    )


# ============================================================================
# ANSWER WRITER TEAM
# ============================================================================

def create_markdown_writer_agent(model: OpenAIChat) -> Agent:
    """Writer specialized in markdown reports."""
    return Agent(
        name="Markdown Writer",
        role="Create well-formatted markdown reports",
        model=model,
        instructions=[
            "Format output as clean, readable markdown",
            "Use headers, lists, and emphasis appropriately",
            "Include data references and numbers",
            "Be comprehensive but concise"
        ],
        markdown=True,
        debug_mode=False
    )


def create_table_writer_agent(model: OpenAIChat) -> Agent:
    """Writer specialized in tables and structured data."""
    return Agent(
        name="Table Writer",
        role="Create structured tables and dataframes",
        model=model,
        instructions=[
            "Format output as markdown tables",
            "Include clear column headers",
            "Align data properly",
            "Add totals/summaries if relevant"
        ],
        markdown=True,
        debug_mode=False
    )


def create_chart_writer_agent(model: OpenAIChat) -> Agent:
    """Writer specialized in visualization specifications."""
    return Agent(
        name="Chart Writer",
        role="Generate visualization specifications",
        model=model,
        instructions=[
            "Provide clear chart specifications",
            "Include chart type, data, labels",
            "Suggest appropriate visualization",
            "Explain what the chart shows"
        ],
        markdown=True,
        debug_mode=False
    )


def create_json_writer_agent(model: OpenAIChat) -> Agent:
    """Writer specialized in JSON output."""
    return Agent(
        name="JSON Writer",
        role="Create structured JSON responses",
        model=model,
        instructions=[
            "Format output as valid JSON",
            "Include all relevant data",
            "Use clear key names",
            "Add metadata if helpful"
        ],
        markdown=False,
        debug_mode=False
    )


def create_answer_writer_team(model: OpenAIChat) -> Team:
    """
    Team of specialized writers for different output formats.
    """
    markdown_writer = create_markdown_writer_agent(model)
    table_writer = create_table_writer_agent(model)
    chart_writer = create_chart_writer_agent(model)
    json_writer = create_json_writer_agent(model)
    
    return Team(
        name="Answer Writer Team",
        members=[markdown_writer, table_writer, chart_writer, json_writer],
        model=model,
        description="""Coordinate writers to format the final answer based on detected output format.
        
        Writers:
        - Markdown Writer: For reports and explanations
        - Table Writer: For structured tabular data
        - Chart Writer: For visualizations
        - JSON Writer: For API/structured responses
        
        Select the writer that matches the recommended format.
        """,
        instructions=[
            "Check the recommended output format from previous step",
            "Delegate to the appropriate writer agent",
            "Ensure the answer is well-formatted and complete",
            "Include all relevant data and insights"
        ],
        markdown=True,
        debug_mode=False
    )


# ============================================================================
# CONDITION EVALUATORS
# ============================================================================

def needs_data_retrieval(step_input: StepInput) -> bool:
    """
    Evaluate if data retrieval is needed based on query analysis.
    Query Analyzer returns structured QueryAnalysis model.
    """
    try:
        # Parse the structured output from Query Analyzer
        analysis = QueryAnalysis.model_validate_json(step_input.previous_step_content)
        return analysis.needs_data_retrieval
    except Exception:
        # Fallback: if parsing fails, default to False
        return False


def needs_nlp_analysis(step_input: StepInput) -> bool:
    """
    Evaluate if NLP analysis is needed based on query analysis.
    Query Analyzer returns structured QueryAnalysis model.
    """
    try:
        # Parse the structured output from Query Analyzer
        analysis = QueryAnalysis.model_validate_json(step_input.previous_step_content)
        return analysis.needs_nlp_analysis
    except Exception:
        # Fallback: if parsing fails, default to False
        return False


# ============================================================================
# WORKFLOW STEP FUNCTIONS
# ============================================================================

async def query_analysis_step(step_input: StepInput) -> AsyncIterator[StepOutput]:
    """
    Step 1: Analyze query to determine execution path.
    Always runs.
    """
    user_query = step_input.input
    
    content = dedent(f"""\
        Analyze this user query and determine the workflow execution path:
        
        Query: {user_query}
        
        Determine:
        - Does this need data retrieval from the database?
        - Does this need NLP analysis?
        - What company is mentioned (if any)?
        - What type of query is this?
        
        Provide your analysis as structured output.
        """)
    
    yield StepOutput(content=content)


async def data_retrieval_prep(step_input: StepInput) -> AsyncIterator[StepOutput]:
    """
    Prepare input for data retrieval step.
    Extracts company and parameters from query analysis.
    """
    original_query = step_input.input
    # Previous step is the Query Analyzer agent's response
    analysis_result = step_input.previous_step_content
    
    content = dedent(f"""\
        Retrieve review data based on this analysis.
        
        Original query: {original_query}
        Query Analysis: {analysis_result}
        
        Instructions:
        - Extract the company name from the analysis
        - Start with 100 reviews as default limit
        - Use the most appropriate retrieval tool
        - Confirm once data is retrieved
        """)
    
    yield StepOutput(content=content)


async def data_sufficiency_prep(step_input: StepInput) -> AsyncIterator[StepOutput]:
    """
    Prepare input for data sufficiency check.
    """
    original_query = step_input.input
    retrieved_data = step_input.previous_step_content
    
    content = dedent(f"""\
        Evaluate if the retrieved data is sufficient for the planned NLP analysis.
        
        Original query: {original_query}
        Retrieved data (sample): {retrieved_data[:800]}...
        
        Consider:
        - What NLP analysis will be performed (gap analysis, clustering, sentiment, etc)?
        - Is the data quantity adequate for that analysis?
        - For clustering: need 20-30+ reviews
        - For gap analysis: need 30-50+ reviews
        - For sentiment: need 20+ reviews
        
        If insufficient, recommend 2x or 3x current count (max 500).
        Provide structured evaluation.
        """)
    
    yield StepOutput(content=content)


async def data_retrieval_retry_step(step_input: StepInput) -> AsyncIterator[StepOutput]:
    """
    Step 3b: Retry data retrieval with increased limit.
    Conditional: Only runs if sufficiency check indicates insufficient data.
    """
    content = dedent(f"""\
        Data was insufficient. Retrieve more data with increased limit.
        
        Previous evaluation: {step_input.previous_step_content}
        
        Fetch additional reviews with the recommended count.
        """)
    
    yield StepOutput(content=content)


async def nlp_analysis_prep(step_input: StepInput) -> AsyncIterator[StepOutput]:
    """
    Prepare input for NLP analysis step.
    """
    original_query = step_input.input
    data_context = step_input.previous_step_content
    
    content = dedent(f"""\
        Perform NLP analysis on the retrieved data to answer the user's query.
        
        Original query: {original_query}
        Available data context: {data_context[:800]}...
        
        Instructions:
        - Select the most appropriate NLP analysis tool
        - For "product gaps" or "what's missing": use analyze_product_gaps
        - For "feature requests": use identify_feature_requests
        - For "themes" or "clustering": use cluster_similar_reviews
        - For "sentiment" or "rating analysis": use analyze_sentiment_distribution
        - For "key terms" or "important words": use compute_tfidf
        
        Execute the analysis and summarize key findings.
        """)
    
    yield StepOutput(content=content)


async def format_detection_prep(step_input: StepInput) -> AsyncIterator[StepOutput]:
    """
    Prepare input for output format detection.
    """
    original_query = step_input.input
    analysis_results = step_input.previous_step_content
    
    content = dedent(f"""\
        Determine the best output format for presenting this answer.
        
        Query: {original_query}
        Analysis results (sample): {analysis_results[:600]}...
        
        Consider:
        - If user explicitly asked for a table/chart, honor that
        - For comparisons and structured data: table
        - For distributions and trends: chart
        - For detailed explanations and insights: markdown
        - For API/structured export: json
        
        Use the determine_best_output_format tool.
        """)
    
    yield StepOutput(content=content)


async def answer_writing_prep(step_input: StepInput) -> AsyncIterator[StepOutput]:
    """
    Prepare input for the answer writer team.
    """
    original_query = step_input.input
    all_context = step_input.previous_step_content
    
    content = dedent(f"""\
        Create a comprehensive, well-formatted final answer for the user.
        
        Original query: {original_query}
        
        All context and analysis results:
        {all_context}
        
        Instructions:
        - Review the recommended output format from the previous step
        - Delegate to the appropriate writer agent (Markdown/Table/Chart/JSON)
        - Ensure the answer is complete, accurate, and well-structured
        - Include all relevant insights, data, and recommendations
        - Be clear and actionable
        """)
    
    yield StepOutput(content=content)


# ============================================================================
# WORKFLOW CREATION
# ============================================================================

def create_product_gap_workflow(
    api_key: str,
    db_file: str = "tmp/product_gap_workflow.db",
) -> Workflow:
    """
    Create the Product Gap Detection Workflow with conditional execution.
    
    Architecture:
    1. Query Analysis (always) - determines what's needed
    2. Conditional Parallel Steps:
       - Data Retrieval (if needed)
       - Data Sufficiency Check + NLP Analysis (if needed)
    3. Format Detection (always) - determines output format
    4. Answer Writer Team (always) - creates final answer
    
    Args:
        api_key: OpenAI API key
        db_file: SQLite database path for workflow persistence
    
    Returns:
        Configured Workflow instance
    """
    model = OpenAIChat(id="gpt-5-mini", api_key=api_key)
    db = SqliteDb(session_table="product_gap_workflow_session", db_file=db_file)
    
    # Create all agents
    query_analyzer = create_query_analyzer_agent(model)
    data_retrieval = create_database_retrieval_agent(model)
    data_sufficiency = create_data_sufficiency_agent(model)
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
    
    data_sufficiency_step = Step(
        name="DataSufficiency",
        description="Check if retrieved data is sufficient",
        agent=data_sufficiency,
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
            # Step 1: Query Analysis (always runs)
            query_analysis_step,
            
            # Step 2: Conditional parallel execution
            Parallel(
                # Condition 1: Data Retrieval if needed
                Condition(
                    name="DataRetrievalCondition",
                    description="Retrieve data if query analysis indicates it's needed",
                    evaluator=needs_data_retrieval,
                    steps=[data_retrieval_step],
                ),
                # Condition 2: Data Sufficiency Check + NLP Analysis if needed
                Condition(
                    name="NLPAnalysisCondition",
                    description="Perform NLP analysis with data sufficiency check if needed",
                    evaluator=needs_nlp_analysis,
                    steps=[
                        # data_sufficiency_step,  # Check if data is sufficient
                        nlp_analysis_step,       # Perform NLP analysis
                    ],
                ),
                name="ConditionalDataAndAnalysis",
                description="Run data retrieval and/or NLP analysis as needed",
            ),
            
            # Step 3: Format Detection (always runs)
            format_detection_step,
            
            # Step 4: Answer Writing (always runs)
            answer_writing_step,
        ],
        db=db,
    )
    
    return workflow


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def run_workflow(query: str, stream: bool = True):
    """
    Execute the workflow for a given query.
    
    Args:
        query: User's question
        stream: Whether to stream intermediate results
    """
    workflow = create_product_gap_workflow(api_key=SETTINGS.OPENAI_API_KEY)
    
    if stream:
        resp = await workflow.arun(
            input=query,
            markdown=True,
            stream=True,
            stream_intermediate_steps=True,
        )
        async for event in resp:
            print(event)
            print()
    else:
        resp = await workflow.arun(input=query, markdown=True)
        print(resp)


if __name__ == "__main__":
    # Test query
    test_query = "What are the main product gaps for Spotify based on customer reviews?"
    asyncio.run(run_workflow(test_query))

