"""NLP analysis agent using LangChain."""
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent

from app.langchain_workflow.tools.nlp import (
    compute_tfidf,
    analyze_sentiment_distribution,
    identify_feature_requests,
    cluster_similar_reviews
)


def create_nlp_analysis_agent(model: ChatOpenAI) -> AgentExecutor:
    """
    Create NLP analysis agent with tools using LangChain.
    """
    tools = [
        compute_tfidf,
        analyze_sentiment_distribution,
        identify_feature_requests,
        cluster_similar_reviews,
    ]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an NLP Analysis Agent that performs advanced text analytics and insight extraction.

Available analyses:
- compute_tfidf: Statistical term importance
- analyze_sentiment_distribution: Rating/sentiment breakdown
- identify_feature_requests: Extract feature requests and pain points
- cluster_similar_reviews: Group reviews by theme

Guidelines:
- Select the most relevant analysis tool for the query
- For 'feature requests', use identify_feature_requests
- For 'themes' or 'topics', use cluster_similar_reviews
- For 'sentiment', use analyze_sentiment_distribution
- Summarize key findings clearly"""),
        ("placeholder", "{chat_history}"),
        ("user", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(model, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    return agent_executor

