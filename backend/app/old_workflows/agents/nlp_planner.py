"""
NLP Analysis Planner Agent - creates execution plan for data analysis.
"""
from typing import Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from pydantic import BaseModel, Field


class AnalysisTask(BaseModel):
    """A single analysis task to execute."""
    tool_name: str = Field(..., description="Name of the tool to use: analyze_review_text_data, cluster_reviews_by_theme, analyze_rating_distribution, or analyze_time_series_trends")
    dataset_key: str = Field(..., description="Key of the dataset to analyze (e.g., 'recent_reviews', 'dedup_reviews', 'rating_distribution')")
    parameters: Optional[dict] = Field(default=None, description="Additional parameters for the tool (optional)")
    rationale: str = Field(..., description="Why this analysis is needed")


class AnalysisPlan(BaseModel):
    """Complete analysis execution plan."""
    tasks: list[AnalysisTask] = Field(..., description="List of analysis tasks to execute in order")
    summary: str = Field(..., description="Summary of the analysis strategy")


def create_nlp_planner_agent(model: OpenAIChat) -> Agent:
    """
    Create an agent that plans NLP analysis tasks based on available datasets.
    """
    return Agent(
        name="NLP Analysis Planner",
        role="Data analysis strategist",
        model=model,
        description="""Plan which NLP analysis tools to use on which datasets.
        
        Available datasets (JSON format):
        - recent_reviews: Raw review text data (list of {rating, text, source, date, author})
        - dedup_reviews: Deduplicated review text data (list of {rating, text, source, date, author})
        - rating_distribution: Aggregated rating counts (list of {rating, count})
        - rating_by_source: Rating breakdown by source (list of {rating, source, count})
        - reviews_time_series: Review volume over time (list of {review_date, reviews_count})
        
        Available tools:
        - analyze_review_text_data: Extract insights from review text (accepts focus_areas parameter)
        - cluster_reviews_by_theme: Group reviews into thematic clusters
        - analyze_rating_distribution: Analyze sentiment and rating patterns
        - analyze_time_series_trends: Analyze review volume trends
        """,
        instructions=[
            "Analyze the user query and available datasets",
            "Create a plan that uses the most appropriate tool for each dataset",
            "For text analysis (features/themes), use dedup_reviews to avoid redundancy",
            "For sentiment/ratings, use rating_distribution and rating_by_source",
            "For trends, use reviews_time_series",
            "Order tasks logically (broad analysis first, then detailed)",
            "Don't create redundant tasks - each tool should only be called once per relevant dataset"
        ],
        output_schema=AnalysisPlan,
        markdown=False,
        debug_mode=False
    )

