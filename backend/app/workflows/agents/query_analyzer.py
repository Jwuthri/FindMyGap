from typing import Optional

from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat

from app.config import SETTINGS


class QueryAnalysis(BaseModel):
    """Query analysis result determining workflow execution path."""
    needs_data_retrieval: bool = Field(..., description="Whether to retrieve review data")
    needs_nlp_analysis: bool = Field(..., description="Whether to perform NLP analysis")
    company: Optional[str] = Field(None, description="Company name if applicable")
    query_type: str = Field(..., description="Type of query: data_only, analysis, general, etc")
    reasoning: str = Field(..., description="Brief explanation of routing decision")
    analysis_type: str = Field(..., description="What type of analysis is needed, TFIDF, clustering ...")


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
