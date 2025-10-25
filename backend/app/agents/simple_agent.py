"""
Simplified single-agent version for Find My Gaps.

This works better than the multi-agent team for straightforward queries.
"""

from typing import Optional
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb
from agno.memory import MemoryManager
from agno.guardrails import PIIDetectionGuardrail, PromptInjectionGuardrail

from app.agents.teams import (
    # Data tools
    retrieve_reviews,
    filter_reviews_by_rating,
    filter_reviews_by_source,
    search_reviews_by_keyword,
    list_available_companies,
    # ML tools
    compute_tfidf,
    analyze_sentiment_distribution,
    identify_feature_requests,
    cluster_similar_reviews,
)


def create_simple_agent(
    api_key: str,
    db_file: str = "memory.db",
    user_id: Optional[str] = None
) -> Agent:
    """
    Create a single agent with all tools - simpler and faster than team.
    
    Args:
        api_key: OpenAI API key
        db_file: SQLite database path
        user_id: User ID
    
    Returns:
        Configured Agent
    """
    model = OpenAIChat(id="gpt-5-mini", api_key=api_key)
    
    db = SqliteDb(db_file=db_file)
    memory_manager = MemoryManager(db=db, model=model)
    
    agent = Agent(
        name="Find My Gaps Analyst",
        role="Analyze customer feedback to find product gaps",
        model=model,
        description="""You analyze customer reviews to identify product gaps.

        You have tools to:
        - Get reviews for companies (Spotify, Notion, Slack)
        - Run TF-IDF analysis to find important terms
        - Analyze sentiment distribution
        - Identify feature requests
        - Cluster reviews by topic
        
        When asked a question:
        1. Use the appropriate tool(s)
        2. Present results clearly and concisely
        3. Include key numbers and insights
        4. Keep responses brief""",
        instructions=[
            "Use tools to get data and perform analysis",
            "Present results clearly with key numbers",
            "Be concise - no lengthy explanations",
            "Focus on actionable insights"
        ],
        tools=[
            # Data retrieval
            retrieve_reviews,
            filter_reviews_by_rating,
            filter_reviews_by_source,
            search_reviews_by_keyword,
            list_available_companies,
            # ML analysis
            compute_tfidf,
            analyze_sentiment_distribution,
            identify_feature_requests,
            cluster_similar_reviews,
        ],
        db=db,
        memory_manager=memory_manager,
        enable_agentic_memory=True,
        add_history_to_context=True,
        num_history_runs=5,
        user_id=user_id or "default_user",
        markdown=True,
        debug_mode=False,
        pre_hooks=[
            PIIDetectionGuardrail(mask_pii=True),
            PromptInjectionGuardrail()
        ]
    )
    
    return agent

