from agno.agent import Agent
from agno.models.openai import OpenAIChat

from app.config import SETTINGS
from app.workflows.tools.data_retrievar import retrieve_reviews, filter_reviews_by_rating, filter_reviews_by_source, search_reviews_by_keyword, list_available_companies


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
        debug_mode=False,
        add_tool_results_to_context=False
    )
