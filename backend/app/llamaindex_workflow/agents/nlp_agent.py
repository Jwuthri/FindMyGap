"""
NLP analysis agent for performing text analytics on retrieved data.

This agent has access to NLP tools and decides which analysis to perform
based on the query and analysis type.
"""

from typing import Dict, Any, List
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.llms import ChatMessage

from app import get_logger
from .base import get_llm, QueryAnalysis
from ..tools import (
    compute_tfidf_tool,
    cluster_reviews_tool,
    analyze_sentiment_tool,
    identify_features_tool,
)

logger = get_logger(__name__)


async def perform_nlp_analysis(
    query: str,
    analysis: QueryAnalysis,
    retrieved_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Perform NLP analysis using an agent with access to NLP tools.
    
    The agent will:
    1. Understand the query and analysis type
    2. Select appropriate NLP tool(s)
    3. Return tool call specifications (dataset_name + parameters)
    
    Args:
        query: Original user query
        analysis: Query analysis result
        retrieved_data: Retrieved data from previous step
        
    Returns:
        Dictionary containing tool calls and their parameters
    """
    logger.info(f"Starting NLP analysis for query: {query}")
    logger.info(f"Analysis type: {analysis.analysis_type}")
    
    # Create the NLP agent with tools
    llm = get_llm()
    
    tools = [
        compute_tfidf_tool,
        cluster_reviews_tool,
        analyze_sentiment_tool,
        identify_features_tool,
    ]
    
    # Use FunctionAgent (new workflow-based API)
    agent = FunctionAgent(
        tools=tools,
        llm=llm,
        verbose=True,
    )
    
    # Build context for the agent
    context_parts = [
        f"Original Query: {query}",
        f"Analysis Type: {analysis.analysis_type}",
        f"Company: {analysis.company or 'Not specified'}",
        f"\nAvailable datasets from retrieval:",
    ]
    
    # Add information about available datasets with column hints
    if retrieved_data and 'data' in retrieved_data:
        for key, value in retrieved_data['data'].items():
            if not key.endswith('_error'):
                context_parts.append(f"  - Dataset: '{key}' ({retrieved_data.get('total_rows', 0)} rows)")
                # Try to infer common columns
                if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                    columns = list(value[0].keys())
                    context_parts.append(f"    Columns: {', '.join(columns)}")
    
    context_parts.extend([
        "\nYour task:",
        "1. Analyze the query and determine which NLP analysis tool(s) to use",
        "2. For each tool, specify:",
        "   - dataset_name: exact name from available datasets above",
        "   - text_column: column containing text data (e.g., 'review_text', 'feedback', 'comment', 'text')",
        "   - other parameters as needed (rating_column, id_column, etc.)",
        "\nTool Selection Guidelines:",
        "- For 'product gaps' or 'what's missing': use identify_features",
        "  → Requires: text_column, optional: rating_column, min_frequency",
        "- For 'themes' or 'topics': use cluster_reviews",
        "  → Requires: text_column, optional: num_clusters, include_metadata",
        "- For 'sentiment' or 'ratings': use analyze_sentiment",
        "  → Requires: text_column, optional: rating_column, group_by",
        "- For 'key terms' or 'important words': use compute_tfidf",
        "  → Requires: text_column, optional: top_n, ngram_range",
        "\nIMPORTANT:",
        "- Use exact dataset names from the available datasets list",
        "- Specify the correct text_column based on available columns",
        "- Common text columns: 'review_text', 'text', 'feedback', 'comment', 'description'",
        "- Common rating columns: 'rating', 'score', 'stars'",
        "- Common id columns: 'id', 'review_id', 'feedback_id'",
    ])
    
    prompt = "\n".join(context_parts)
    
    logger.info(f"Agent prompt: {prompt}")
    
    # Run the agent
    try:
        response = await agent.achat(prompt)
        logger.info(f"Agent response: {response}")
        
        # Extract tool calls from agent's execution
        # FunctionCallingAgent stores tool calls in sources
        tool_calls = []
        
        if hasattr(response, 'sources') and response.sources:
            for source in response.sources:
                # Each source represents a tool call
                if hasattr(source, 'raw_output'):
                    tool_calls.append(source.raw_output)
                elif hasattr(source, 'content'):
                    # Try to parse content as tool result
                    try:
                        import json
                        tool_result = json.loads(source.content) if isinstance(source.content, str) else source.content
                        if isinstance(tool_result, dict) and 'tool' in tool_result:
                            tool_calls.append(tool_result)
                    except:
                        pass
        
        # If no tool calls found in sources, check chat history
        if not tool_calls and hasattr(agent, 'chat_history'):
            for msg in agent.chat_history:
                if hasattr(msg, 'additional_kwargs') and 'tool_calls' in msg.additional_kwargs:
                    for tc in msg.additional_kwargs['tool_calls']:
                        if hasattr(tc, 'function'):
                            tool_calls.append({
                                "tool": tc.function.name,
                                "arguments": tc.function.arguments
                            })
        
        logger.info(f"Extracted {len(tool_calls)} tool calls")
        
        return {
            "tool_calls": tool_calls,
            "agent_response": str(response),
            "reasoning": analysis.reasoning,
        }
        
    except Exception as e:
        logger.error(f"Error in NLP agent: {e}", exc_info=True)
        return {
            "error": str(e),
            "tool_calls": [],
            "agent_response": "",
        }


def create_nlp_agent_prompt(query: str, analysis: QueryAnalysis, dataset_info: List[str]) -> str:
    """
    Create a structured prompt for the NLP agent.
    
    Args:
        query: Original user query
        analysis: Query analysis result
        dataset_info: List of available dataset names
        
    Returns:
        Formatted prompt string
    """
    return f"""You are an NLP analysis expert. Analyze the query and select appropriate NLP tools.

Query: {query}
Analysis Type: {analysis.analysis_type}
Company: {analysis.company or 'Not specified'}

Available Datasets:
{chr(10).join(f'  - {ds}' for ds in dataset_info)}

Available Tools:
1. compute_tfidf: Find most important terms (use for: key terms, important words, topics)
2. cluster_reviews: Group similar text by theme (use for: themes, topics, patterns, grouping)
3. analyze_sentiment: Analyze sentiment and ratings (use for: sentiment, ratings, satisfaction)
4. identify_features: Extract feature requests and pain points (use for: gaps, missing features, requests)

Task:
Select the most appropriate tool(s) for this query. For each tool:
- Specify the dataset_name from the available datasets
- Set appropriate parameters

Think step by step and explain your reasoning."""
