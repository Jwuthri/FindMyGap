"""
Data-aware NLP tools that operate on pre-fetched datasets.
These tools don't fetch data - they analyze what's passed to them.
"""
import json
from collections import Counter
from typing import Any

from app import get_logger
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool

from app.config import SETTINGS

logger = get_logger("workflows.tools.nlp_data_aware")

# ============================================================================
# SCHEMAS
# ============================================================================

class ReviewCluster(BaseModel):
    theme: str = Field(..., description="The theme of the cluster")
    description: str = Field(..., description="The description of the cluster")
    review_count: int = Field(..., description="Number of reviews in this cluster")
    key_insights: list[str] = Field(..., description="The key insights of the cluster")
    sentiment: str = Field(..., description="positive, negative, or mixed")

class ClusteringResult(BaseModel):
    clusters: list[ReviewCluster]

class TextInsight(BaseModel):
    category: str = Field(..., description="Category of the insight")
    description: str = Field(..., description="Detailed description")
    frequency: int = Field(..., description="How often this appears in the data")
    severity: str = Field(..., description="high, medium, or low impact")
    examples: list[str] = Field(..., description="Examples from the reviews")

class TextAnalysisResult(BaseModel):
    insights: list[TextInsight] = Field(..., description="Key insights extracted from text")
    summary: str = Field(..., description="Overall summary of findings")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_data(data_input: str | dict | list) -> list[dict]:
    """Parse data input into list of dictionaries."""
    logger.debug(f"parse_data: input type={type(data_input).__name__}")
    
    if isinstance(data_input, str):
        try:
            data_input = json.loads(data_input)
            logger.debug(f"parse_data: parsed JSON string, result type={type(data_input).__name__}")
        except json.JSONDecodeError as e:
            logger.error(f"parse_data: JSON decode error - {e}")
            return []
    
    if isinstance(data_input, dict):
        # If it's a single dict, wrap it in a list
        logger.debug("parse_data: wrapping single dict in list")
        return [data_input]
    
    if isinstance(data_input, list):
        logger.debug(f"parse_data: returning list with {len(data_input)} items")
        return data_input
    
    logger.warning(f"parse_data: unexpected data type, returning empty list")
    return []

# ============================================================================
# DATA-AWARE TOOLS
# ============================================================================

@tool(requires_confirmation=False)
def analyze_review_text_data(reviews_data: str, focus_areas: str = "all insights") -> str:
    """
    Analyze review text data using LLM to extract key insights.
    
    Args:
        reviews_data: JSON string or object containing reviews with fields like: rating, text, source, date, author
        focus_areas: What to focus on (e.g., "feature requests", "pain points", "all insights")
    
    Returns:
        JSON string with extracted insights
    """
    logger.info(f"analyze_review_text_data: starting analysis with focus_areas='{focus_areas}'")
    
    reviews = parse_data(reviews_data)
    logger.info(f"analyze_review_text_data: parsed {len(reviews)} reviews")
    
    if not reviews:
        logger.warning("analyze_review_text_data: no reviews found in dataset")
        return json.dumps({"error": "No reviews in dataset"})
    
    logger.debug("analyze_review_text_data: initializing OpenAI model and agent")
    model = OpenAIChat(id="gpt-5-nano", api_key=SETTINGS.OPENAI_API_KEY)
    
    analysis_agent = Agent(
        name="Text Analysis Agent",
        model=model,
        instructions=[
            "Analyze customer feedback to extract key insights",
            "Identify patterns and common themes",
            "Group similar feedback together",
            "Quantify frequency and impact based on how many reviews mention each issue",
            "Categorize insights clearly"
        ],
        output_schema=TextAnalysisResult,
        markdown=False
    )
    
    # Prepare review texts (limit to avoid token issues)
    review_subset = reviews[:50]
    logger.info(f"analyze_review_text_data: processing {len(review_subset)} reviews (max 50)")
    
    review_texts = "\n\n".join([
        f"Review {i+1} (Rating: {r.get('rating', 'N/A')}/5, {r.get('date', 'N/A')}):\n{r.get('text', '')}"
        for i, r in enumerate(review_subset)
    ])
    
    prompt = f"""Analyze these customer reviews focusing on: {focus_areas}

Extract key insights including:
- Common themes and patterns
- What users like or dislike
- What users are requesting
- Issues and frustrations
- Any gaps or missing functionality

Reviews ({len(reviews)} total, showing first 50):
{review_texts}"""
    
    logger.debug(f"analyze_review_text_data: sending prompt to agent (prompt length: {len(prompt)} chars)")
    response = analysis_agent.run(prompt)
    
    logger.info("analyze_review_text_data: received response from agent, extracting insights")
    result = response.content.model_dump_json(indent=2)
    logger.debug(f"analyze_review_text_data: result length: {len(result)} chars")
    
    return result


@tool(requires_confirmation=False)
def cluster_reviews_by_theme(reviews_data: str, num_clusters: int = 5) -> str:
    """
    Use LLM to group reviews by theme/topic.
    
    Args:
        reviews_data: JSON string or object containing reviews with fields like: rating, text, source, date, author
        num_clusters: Number of topic clusters to identify (default 5)
    
    Returns:
        JSON string with thematic clusters
    """
    logger.info(f"cluster_reviews_by_theme: starting clustering with num_clusters={num_clusters}")
    
    reviews = parse_data(reviews_data)
    logger.info(f"cluster_reviews_by_theme: parsed {len(reviews)} reviews")
    
    if not reviews:
        logger.warning("cluster_reviews_by_theme: no reviews found in dataset")
        return json.dumps({"error": "No reviews in dataset"})
    
    logger.debug("cluster_reviews_by_theme: initializing OpenAI model and clustering agent")
    model = OpenAIChat(id="gpt-5-nano", api_key=SETTINGS.OPENAI_API_KEY)
    
    clustering_agent = Agent(
        name="Review Clustering Agent",
        model=model,
        instructions=[
            f"Group reviews into {num_clusters} thematic clusters",
            "Identify the main topic/theme of each cluster",
            "Provide clear cluster names and descriptions",
            "Count how many reviews belong to each theme"
        ],
        output_schema=ClusteringResult,
        markdown=False
    )
    
    # Prepare condensed review data (limit for token efficiency)
    review_subset = reviews[:80]
    logger.info(f"cluster_reviews_by_theme: processing {len(review_subset)} reviews (max 80)")
    
    review_summary = "\n".join([
        f"{i+1}. [{r.get('rating', '?')}★] {r.get('text', '')[:150]}..."
        for i, r in enumerate(review_subset)
    ])
    
    prompt = f"""Analyze these customer reviews and group them into {num_clusters} thematic clusters.

Reviews ({len(reviews)} total, showing first 80):
{review_summary}"""
    
    logger.debug(f"cluster_reviews_by_theme: sending prompt to agent (prompt length: {len(prompt)} chars)")
    response = clustering_agent.run(prompt)
    
    logger.info("cluster_reviews_by_theme: received response from agent, building result")
    result = response.content.model_dump()
    result["total_reviews_analyzed"] = len(reviews)
    
    logger.debug(f"cluster_reviews_by_theme: found {len(result.get('clusters', []))} clusters")
    
    return json.dumps(result, indent=2)


@tool(requires_confirmation=False)
def analyze_rating_distribution(rating_data: str, rating_by_source_data: str = "") -> str:
    """
    Analyze rating distribution and sentiment patterns from aggregated data.
    
    Args:
        rating_data: JSON string with rating distribution (list of {rating, count})
        rating_by_source_data: Optional JSON string with rating breakdown by source (list of {rating, source, count})
    
    Returns:
        JSON string with sentiment analysis
    """
    logger.info("analyze_rating_distribution: starting rating analysis")
    
    ratings = parse_data(rating_data)
    logger.info(f"analyze_rating_distribution: parsed {len(ratings)} rating records")
    
    if not ratings:
        logger.warning("analyze_rating_distribution: no rating data provided")
        return json.dumps({"error": "No rating data provided"})
    
    # Parse rating counts
    logger.debug("analyze_rating_distribution: calculating rating distribution")
    rating_counts = {}
    total = 0
    for row in ratings:
        rating = int(row.get('rating', 0))
        count = int(row.get('count', 0))
        rating_counts[rating] = count
        total += count
    
    logger.info(f"analyze_rating_distribution: total reviews={total}, rating distribution={rating_counts}")
    
    # Calculate sentiment
    positive = sum(rating_counts.get(r, 0) for r in [4, 5])
    neutral = rating_counts.get(3, 0)
    negative = sum(rating_counts.get(r, 0) for r in [1, 2])
    
    logger.debug(f"analyze_rating_distribution: sentiment - positive={positive}, neutral={neutral}, negative={negative}")
    
    # Calculate average
    avg_rating = sum(rating * count for rating, count in rating_counts.items()) / total if total > 0 else 0
    logger.info(f"analyze_rating_distribution: average_rating={avg_rating:.2f}")
    
    result = {
        "total_reviews": total,
        "average_rating": round(avg_rating, 2),
        "sentiment_distribution": {
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
            "positive_percent": round((positive / total) * 100, 1) if total > 0 else 0,
            "negative_percent": round((negative / total) * 100, 1) if total > 0 else 0
        },
        "rating_breakdown": rating_counts
    }
    
    # Add source breakdown if provided
    if rating_by_source_data:
        logger.debug("analyze_rating_distribution: processing source breakdown data")
        source_ratings = parse_data(rating_by_source_data)
        source_breakdown = {}
        for row in source_ratings:
            source = row.get('source', 'unknown')
            count = int(row.get('count', 0))
            if source not in source_breakdown:
                source_breakdown[source] = 0
            source_breakdown[source] += count
        result["source_breakdown"] = source_breakdown
        logger.info(f"analyze_rating_distribution: source breakdown={source_breakdown}")
    
    logger.info("analyze_rating_distribution: analysis complete")
    return json.dumps(result, indent=2)


@tool(requires_confirmation=False)
def analyze_time_series_trends(time_series_data: str) -> str:
    """
    Analyze review volume trends over time.
    
    Args:
        time_series_data: JSON string with time series data (list of {review_date, reviews_count})
    
    Returns:
        JSON string with trend analysis
    """
    logger.info("analyze_time_series_trends: starting time series analysis")
    
    time_data = parse_data(time_series_data)
    logger.info(f"analyze_time_series_trends: parsed {len(time_data)} time series records")
    
    if not time_data:
        logger.warning("analyze_time_series_trends: no time series data provided")
        return json.dumps({"error": "No time series data provided"})
    
    # Parse dates and counts
    logger.debug("analyze_time_series_trends: parsing dates and counts")
    dates = []
    counts = []
    for row in time_data:
        dates.append(row.get('review_date', ''))
        counts.append(int(row.get('reviews_count', 0)))
    
    logger.debug(f"analyze_time_series_trends: date range: {dates[0] if dates else 'N/A'} to {dates[-1] if dates else 'N/A'}")
    
    # Calculate basic stats
    total_reviews = sum(counts)
    avg_per_day = total_reviews / len(counts) if counts else 0
    max_day = max(counts) if counts else 0
    min_day = min(counts) if counts else 0
    
    logger.info(f"analyze_time_series_trends: total_reviews={total_reviews}, avg_per_day={avg_per_day:.1f}, max={max_day}, min={min_day}")
    
    # Find peak day
    peak_idx = counts.index(max_day) if counts else 0
    peak_date = dates[peak_idx] if dates else ""
    
    logger.debug(f"analyze_time_series_trends: peak activity on {peak_date} with {max_day} reviews")
    
    # Determine trend
    trend = "stable"
    if counts:
        if counts[-1] > counts[0]:
            trend = "increasing"
        elif counts[-1] < counts[0]:
            trend = "decreasing"
    
    logger.info(f"analyze_time_series_trends: overall trend={trend}")
    
    result = {
        "total_reviews": total_reviews,
        "date_range": {
            "start": dates[0] if dates else "",
            "end": dates[-1] if dates else ""
        },
        "daily_stats": {
            "average": round(avg_per_day, 1),
            "max": max_day,
            "min": min_day
        },
        "peak_activity": {
            "date": peak_date,
            "reviews": max_day
        },
        "trend": trend
    }
    
    logger.info("analyze_time_series_trends: analysis complete")
    return json.dumps(result, indent=2)

