"""NLP tools using LangChain."""
import json
from collections import Counter
import math

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.config import SETTINGS

# Common stopwords to exclude
STOPWORDS = {
    'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'as', 'are', 
    'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does',
    'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
    'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
    'it', 'we', 'they', 'them', 'their', 'what', 'which', 'who', 'when',
    'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
    'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
    'same', 'so', 'than', 'too', 'very', 'just', 'but', 'for', 'with',
    'about', 'from', 'into', 'through', 'during', 'before', 'after'
}


class ReviewCluster(BaseModel):
    theme: str = Field(..., description="The theme of the cluster")
    description: str = Field(..., description="The description of the cluster")
    review_ids: list[int] = Field(..., description="The review ids of the cluster")
    key_insights: list[str] = Field(..., description="The key insights of the cluster")
    sentiment: str = Field(..., description="positive, negative, or mixed")


class ClusteringResult(BaseModel):
    clusters: list[ReviewCluster]


class FeatureRequest(BaseModel):
    category: str = Field(..., description="The category of the feature request")
    description: str = Field(..., description="The description of the feature request")
    frequency: int = Field(..., description="The frequency of the feature request")
    examples: list[str] = Field(..., description="Examples of the feature request")


class PainPoint(BaseModel):
    category: str = Field(..., description="The category of the pain point")
    description: str = Field(..., description="The description of the pain point")
    severity: str = Field(..., description="high, medium, or low")
    examples: list[str] = Field(..., description="Examples of the pain point")


class ProductGapItem(BaseModel):
    gap: str = Field(..., description="The gap in the product")
    impact: str = Field(..., description="The impact of the gap on the user")
    mentioned_by: int = Field(..., description="The number of times the gap has been mentioned in the reviews")


class FeatureAnalysisResult(BaseModel):
    feature_requests: list[FeatureRequest]
    pain_points: list[PainPoint]
    product_gaps: list[ProductGapItem]


@tool
def compute_tfidf(company: str, top_n: int = 10) -> str:
    """
    Compute TF-IDF to find most important terms in reviews.
    
    Args:
        company: Company name (spotify, notion, slack)
        top_n: How many top terms to return (default 10)
    
    Returns:
        JSON with top terms and TF-IDF scores
    """
    # Note: This would need to be connected to actual data source
    # For now, returning mock structure
    return json.dumps({
        "company": company,
        "reviews_analyzed": 0,
        "top_terms": [],
        "note": "This tool needs to be connected to actual review data"
    })


@tool
def analyze_sentiment_distribution(company: str) -> str:
    """
    Analyze rating distribution and sentiment patterns.
    
    Args:
        company: Company name
    
    Returns:
        JSON string with sentiment analysis
    """
    # Note: This would need to be connected to actual data source
    return json.dumps({
        "company": company,
        "total_reviews": 0,
        "average_rating": 0,
        "sentiment_distribution": {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        },
        "note": "This tool needs to be connected to actual review data"
    }, indent=2)


@tool
def identify_feature_requests(company: str) -> str:
    """
    Use LLM to identify feature requests, pain points, and product gaps from reviews.
    
    Args:
        company: Company name
    
    Returns:
        JSON string with analyzed feature requests and gaps
    """
    # Note: This would need to be connected to actual data source
    return json.dumps({
        "feature_requests": [],
        "pain_points": [],
        "product_gaps": [],
        "note": "This tool needs to be connected to actual review data and LLM"
    }, indent=2)


@tool
def cluster_similar_reviews(company: str, num_clusters: int = 5) -> str:
    """
    Use LLM to intelligently group reviews by theme/topic.
    
    Args:
        company: Company name
        num_clusters: Number of topic clusters to identify
    
    Returns:
        JSON string with thematic clusters
    """
    # Note: This would need to be connected to actual data source
    return json.dumps({
        "company": company,
        "total_reviews_analyzed": 0,
        "clusters": [],
        "note": "This tool needs to be connected to actual review data and LLM"
    }, indent=2)

