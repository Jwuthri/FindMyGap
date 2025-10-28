from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat


class SQLQuery(BaseModel):
    """Single SQL query to execute"""
    query: str = Field(..., description="The SQL query to execute")
    purpose: str = Field(..., description="What this query retrieves")
    result_key: str = Field(..., description="Key to store results under (e.g., 'reviews', 'feedback')")


class RetrievalPlan(BaseModel):
    """Structured plan for data retrieval using SQL queries"""
    sql_queries: list[SQLQuery] = Field(..., description="List of SQL queries to execute")
    reasoning: str = Field(..., description="Why this retrieval strategy was chosen")
    expected_data_types: list[str] = Field(..., description="Types of data expected (e.g., ['reviews', 'feedback', 'ratings'])")


def create_retrieval_planner_agent(model: OpenAIChat, table_schemas: str | None = None) -> Agent:
    """
    Agent that generates SQL queries for data retrieval based on available table schemas.
    Returns a structured plan with SQL queries that will be executed by a separate step.
    
    Args:
        model: The LLM model to use
        table_schemas: String describing available tables and their schemas
    """    
    return Agent(
        name="RetrievalPlanner",
        role="SQL Query Generator for Data Retrieval",
        model=model,
        description=f"""Analyze the user query and generate SQL queries to retrieve necessary data.
        
        {table_schemas}
        """,
        instructions=[
            "Analyze the user query to understand what data is needed",
            "Generate appropriate SQL SELECT queries based on available tables",
            "Use WHERE clauses to filter data efficiently",
            "Set reasonable LIMIT clauses (default 100, max 500 for analysis)",
            "Use LIKE for text matching, = for exact matches",
            "For negative reviews, use: WHERE rating <= 2",
            "For positive reviews, use: WHERE rating >= 4",
            "You can generate multiple queries if different data types are needed",
            "Return a structured plan with SQL queries - DO NOT execute them yourself",
            "SQL syntax: Use standard SQLite syntax"
        ],
        response_model=RetrievalPlan,
        markdown=False,
        debug_mode=False,
    )

