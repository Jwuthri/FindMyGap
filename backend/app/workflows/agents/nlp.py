from agno.agent import Agent
from agno.models.openai import OpenAIChat

from app.workflows.tools.nlp import compute_tfidf, analyze_sentiment_distribution, identify_feature_requests, cluster_similar_reviews


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
        """,
        instructions=[
            "Select the most relevant analysis tool for the query",
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
        ],
        markdown=False,
        debug_mode=False
    )
