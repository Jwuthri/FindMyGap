"""
NLP Executor Agent - executes planned analysis tasks on datasets.
"""
from agno.agent import Agent
from agno.models.openai import OpenAIChat

from app.workflows.tools.nlp_data_aware import (
    analyze_review_text_data,
    cluster_reviews_by_theme,
    analyze_rating_distribution,
    analyze_time_series_trends
)


def create_nlp_executor_agent(model: OpenAIChat) -> Agent:
    """
    Create an agent that executes NLP analysis tasks on pre-fetched datasets.
    """
    return Agent(
        name="NLP Executor Agent",
        role="Data analysis executor",
        model=model,
        description="""Execute NLP analysis tools on provided datasets.
        
        You have access to:
        - analyze_review_text_data: Analyze review text for insights (JSON data, optional focus_areas)
        - cluster_reviews_by_theme: Group reviews into thematic clusters (JSON data)
        - analyze_rating_distribution: Analyze sentiment and rating patterns (JSON data)
        - analyze_time_series_trends: Analyze review volume trends (JSON data)
        
        Each tool expects JSON-formatted data as input (string or object).
        """,
        instructions=[
            "Execute the analysis tasks according to the plan",
            "Pass the correct dataset to each tool",
            "Combine results from all tools into a comprehensive analysis",
            "Summarize key findings clearly",
            "Highlight actionable insights"
        ],
        tools=[
            analyze_review_text_data,
            cluster_reviews_by_theme,
            analyze_rating_distribution,
            analyze_time_series_trends,
        ],
        markdown=False,
        debug_mode=False
    )

