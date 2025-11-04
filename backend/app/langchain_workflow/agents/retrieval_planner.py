"""Retrieval planner agent using LangChain."""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


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


def create_retrieval_planner_agent(model: ChatOpenAI, table_schemas: str | None = None):
    """
    Create retrieval planner using LangChain structured output.
    Generates SQL queries for data retrieval based on available table schemas.
    """
    parser = PydanticOutputParser(pydantic_object=RetrievalPlan)
    
    schema_context = f"\n\nAvailable Tables:\n{table_schemas}" if table_schemas else ""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are a SQL Query Generator for Data Retrieval.

Analyze the user query and generate SQL queries to retrieve necessary data.
We are using PostgreSQL so make sure your queries are compatible.
Don't use :named_parameters (like :company) in plain SQL. Use the real names, write the full SQL queries since we gonna run them aside.

{schema_context}

Guidelines:
- Analyze the user query to understand what data is needed
- Generate appropriate SQL SELECT queries based on available tables
- Use WHERE clauses to filter data efficiently
- Set reasonable LIMIT clauses (default 200)
- Use LIKE for text matching, = for exact matches
- You can generate multiple queries if different data types are needed
- Return a structured plan with SQL queries - DO NOT execute them yourself
- Try not to retrieve the `created_at` or `updated_at` if not necessary

{{format_instructions}}"""),
        ("user", "{query}")
    ])
    
    chain = prompt | model.with_structured_output(RetrievalPlan)
    return chain

