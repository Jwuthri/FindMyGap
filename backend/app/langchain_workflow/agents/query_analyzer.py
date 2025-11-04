"""Query analyzer agent using LangChain."""
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class QueryAnalysis(BaseModel):
    """Query analysis result determining workflow execution path."""
    needs_data_retrieval: bool = Field(..., description="Whether to retrieve review data")
    needs_nlp_analysis: bool = Field(..., description="Whether to perform NLP analysis")
    company: Optional[str] = Field(None, description="Company name if applicable")
    query_type: str = Field(..., description="Type of query: data_only, analysis, general, etc")
    reasoning: str = Field(..., description="Brief explanation of routing decision")


def create_query_analyzer_agent(model: ChatOpenAI):
    """
    Create query analyzer using LangChain structured output.
    Returns a runnable chain that analyzes queries.
    """
    parser = PydanticOutputParser(pydantic_object=QueryAnalysis)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Query Analyzer that determines workflow execution paths.

Analyze the user's question to determine what steps are needed:
- Does this need data retrieval? (mentions specific company, asks for reviews, needs data)
- Does this need NLP analysis? (asks for gaps, patterns, clustering, sentiment, features)
- What company are they asking about?
- What type of query is this?

{format_instructions}"""),
        ("user", "{query}")
    ])
    
    chain = prompt | model.with_structured_output(QueryAnalysis)
    return chain

