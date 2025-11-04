"""
Agent configurations for LlamaIndex workflow.

These agents use LlamaIndex's LLM interface.
"""

from typing import Dict, Any
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from pydantic import BaseModel, Field

from llama_index.core.agent.workflow import FunctionAgent, AgentWorkflow
from llama_index.core.tools import FunctionTool
from llama_index.core.workflow import Context

from app.config import SETTINGS
from app import get_logger

logger = get_logger(__name__)


class QueryAnalysis(BaseModel):
    """Query analysis result determining workflow execution path."""
    needs_data_retrieval: bool = Field(..., description="Whether to retrieve review data")
    needs_nlp_analysis: bool = Field(..., description="Whether to perform NLP analysis")
    company: str | None = Field(None, description="Company name if applicable")
    query_type: str = Field(..., description="Type of query: data_only, analysis, general, etc")
    reasoning: str = Field(..., description="Brief explanation of routing decision")
    analysis_type: str = Field(..., description="What type of analysis is needed")


class FormatDetection(BaseModel):
    """Output format detection result."""
    format_type: str = Field(..., description="Type of format: markdown, json, table, etc")
    format_details: str = Field(..., description="Specific formatting requirements")


class SQLQuery(BaseModel):
    """SQL query definition."""
    query: str = Field(..., description="The SQL query string")
    purpose: str = Field(..., description="Purpose of this query")
    result_key: str = Field(..., description="Key to store results under")


class RetrievalPlan(BaseModel):
    """Data retrieval plan."""
    sql_queries: list[SQLQuery] = Field(..., description="List of SQL queries to execute")
    reasoning: str = Field(..., description="Explanation of the retrieval strategy")
    expected_data_types: list[str] = Field(..., description="List of expected data types")


def get_llm() -> OpenAI:
    """Get configured LLM instance."""
    return OpenAI(
        model="gpt-4o-mini",
        api_key=SETTINGS.OPENAI_API_KEY,
        temperature=0.1
    )


async def analyze_query(query: str) -> QueryAnalysis:
    """
    Analyze user query to determine execution path.
    """
    llm = get_llm()
    sllm = llm.as_structured_llm(output_cls=QueryAnalysis)
    
    prompt = f"""Analyze this user query and determine what workflow steps are needed:

Query: {query}

Determine:
- Does this need data retrieval? (mentions specific company, asks for reviews, needs data)
- Does this need NLP analysis? (asks for gaps, patterns, clustering, sentiment, features)
- What company are they asking about?
- What type of query is this?
- What type of analysis is needed (TFIDF, clustering, sentiment, etc)?"""

    messages = [
        ChatMessage(role="system", content="You are a query analyzer that determines workflow execution paths."),
        ChatMessage(role="user", content=prompt)
    ]
    
    response = await sllm.achat(messages)
    result = response.raw
    
    logger.info(f"Query analysis: {result}")
    return result


async def detect_format(query: str) -> FormatDetection:
    """
    Detect desired output format from query.
    """
    llm = get_llm()
    sllm = llm.as_structured_llm(output_cls=FormatDetection)
    
    prompt = f"""Analyze this query and determine the best output format:

Query: {query}

Determine:
- What format would be best? (markdown report, JSON, table, bullet points, etc)
- Any specific formatting requirements mentioned?"""

    messages = [
        ChatMessage(role="system", content="You are a format detection specialist."),
        ChatMessage(role="user", content=prompt)
    ]
    
    response = await sllm.achat(messages)
    result = response.raw
    
    logger.info(f"Format detection: {result}")
    return result


async def plan_retrieval(query: str, table_schemas: Dict[str, Any]) -> RetrievalPlan:
    """
    Plan data retrieval strategy.
    """
    llm = get_llm()
    sllm = llm.as_structured_llm(output_cls=RetrievalPlan)
    
    # Handle case where table_schemas is a string (from schema service)
    if isinstance(table_schemas, str):
        schema_info = table_schemas
    else:
        schema_info = "\n".join([
            f"Table: {name}\nSchema: {schema}"
            for name, schema in table_schemas.items()
        ])
    
    prompt = f"""Create a data retrieval plan for this query:

Query: {query}

Available Tables:
{schema_info}

Generate SQL queries to retrieve the necessary data."""

    messages = [
        ChatMessage(role="system", content="You are a data retrieval planner that creates SQL queries."),
        ChatMessage(role="user", content=prompt)
    ]
    
    response = await sllm.achat(messages)
    result = response.raw
    
    logger.info(f"Retrieval plan: {result}")
    return result


def write_markdown_report(context: str) -> str:
    """Tool for writing markdown reports."""
    return f"MARKDOWN_REPORT:{context}"


def write_table_report(context: str) -> str:
    """Tool for writing table reports.""" 
    return f"TABLE_REPORT:{context}"


def write_chart_report(context: str) -> str:
    """Tool for writing chart reports."""
    return f"CHART_REPORT:{context}"


def write_json_report(context: str) -> str:
    """Tool for writing JSON reports."""
    return f"JSON_REPORT:{context}"


def create_answer_writer_workflow(format_type: str = "markdown") -> AgentWorkflow:
    """
    Create a LlamaIndex AgentWorkflow with specialized writer agents.
    """
    llm = get_llm()
    
    # Create specialized writer agents
    markdown_writer = FunctionAgent(
        name="MarkdownWriter",
        description="Writes comprehensive markdown reports with proper structure and formatting.",
        system_prompt="""You are the MarkdownWriter. You specialize in creating well-structured markdown reports.
        
        Your responsibilities:
        - Create reports with clear headings and sections
        - Use bullet points, numbered lists, and emphasis effectively
        - Include Introduction, Analysis, Findings, and Recommendations sections
        - Format data insights in readable tables when appropriate
        - Use proper markdown syntax (*italic*, **bold**, `code`)
        
        When you receive context, write a comprehensive markdown report and then hand off to the coordinator.""",
        llm=llm,
        can_handoff_to=["ReportCoordinator"],
    )
    
    table_writer = FunctionAgent(
        name="TableWriter", 
        description="Writes structured tabular data reports.",
        system_prompt="""You are the TableWriter. You specialize in presenting data in clear, well-formatted tables.
        
        Your responsibilities:
        - Present data in clear, well-formatted tables
        - Use markdown table syntax with proper alignment
        - Include headers and organize data logically
        - Add summary rows when appropriate
        - Ensure tables are readable and informative
        
        When you receive context, create a table-focused report and then hand off to the coordinator.""",
        llm=llm,
        can_handoff_to=["ReportCoordinator"],
    )
    
    chart_writer = FunctionAgent(
        name="ChartWriter",
        description="Writes data visualization and chart reports.",
        system_prompt="""You are the ChartWriter. You specialize in data visualizations and chart descriptions.
        
        Your responsibilities:
        - Describe data visualizations in text format
        - Suggest appropriate chart types (bar, line, pie, etc.)
        - Provide data summaries that work well in charts
        - Include insights that visual representations would highlight
        - Format data ready for visualization tools
        
        When you receive context, create a chart-focused report and then hand off to the coordinator.""",
        llm=llm,
        can_handoff_to=["ReportCoordinator"],
    )
    
    json_writer = FunctionAgent(
        name="JsonWriter",
        description="Writes structured JSON responses.",
        system_prompt="""You are the JsonWriter. You specialize in creating structured JSON responses.
        
        Your responsibilities:
        - Structure responses as valid JSON objects
        - Organize data hierarchically with clear keys
        - Include metadata like timestamps, counts, and summaries
        - Ensure all strings are properly escaped
        - Provide structured data that's API-ready
        
        When you receive context, create a JSON-formatted report and then hand off to the coordinator.""",
        llm=llm,
        can_handoff_to=["ReportCoordinator"],
    )
    
    # Create coordinator agent
    coordinator = FunctionAgent(
        name="ReportCoordinator",
        description="Coordinates the writing team and finalizes reports.",
        system_prompt=f"""You are the ReportCoordinator. You manage the writing team and finalize reports.
        
        The requested format is: {format_type}
        
        Your responsibilities:
        - Receive completed reports from writer agents
        - Ensure the report matches the requested format
        - Make final adjustments if needed
        - Provide the final polished report
        
        You are the final step in the writing process.""",
        llm=llm,
        tools=[],
        can_handoff_to=[],  # Final agent, no handoffs
    )
    
    # Determine root agent based on format
    if format_type.lower() in ['markdown', 'report', 'bullet points']:
        root_agent = "MarkdownWriter"
    elif format_type.lower() in ['table', 'tabular', 'csv']:
        root_agent = "TableWriter"
    elif format_type.lower() in ['chart', 'visualization', 'graph']:
        root_agent = "ChartWriter"
    elif format_type.lower() in ['json', 'api', 'structured']:
        root_agent = "JsonWriter"
    else:
        root_agent = "MarkdownWriter"  # Default
    
    # Create the workflow
    workflow = AgentWorkflow(
        agents=[markdown_writer, table_writer, chart_writer, json_writer, coordinator],
        root_agent=root_agent,
        initial_state={
            "format_type": format_type,
            "report_content": "",
            "status": "initialized"
        },
    )
    
    return workflow


async def generate_answer(context: str, format_type: str = "markdown") -> str:
    """
    Generate final answer using the LlamaIndex AgentWorkflow.
    """
    workflow = create_answer_writer_workflow(format_type)
    
    # Create a proper Context object
    ctx = Context(workflow)

    # Store initial data in context
    await ctx.store.set("context", context)
    await ctx.store.set("format_type", format_type)
    
    # Run the workflow with the user message and context
    result = await workflow.run(
        user_msg=f"Please create a {format_type} report based on this context: {context}",
        ctx=ctx
    )
    
    return str(result)
