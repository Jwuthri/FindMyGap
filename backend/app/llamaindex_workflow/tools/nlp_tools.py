"""
NLP analysis tools for LlamaIndex workflow.

These tools are designed to work with dataset names rather than actual data.
The data retrieval happens separately based on the dataset_name parameter.
"""

from typing import Any, Dict
from pydantic import BaseModel, Field
from llama_index.core.tools import FunctionTool

from app import get_logger

logger = get_logger(__name__)


class NLPToolCall(BaseModel):
    """Base model for NLP tool call parameters."""
    dataset_name: str = Field(..., description="Name of the dataset to analyze (e.g., 'user_reviews', 'feedback_data')")


class TFIDFParams(NLPToolCall):
    """Parameters for TF-IDF analysis."""
    text_column: str = Field(..., description="Column containing text data (e.g., 'review_text', 'feedback')")
    top_n: int = Field(default=10, description="Number of top terms to return")
    min_df: int = Field(default=2, description="Minimum document frequency")
    max_df: float = Field(default=0.8, description="Maximum document frequency (0.0-1.0)")
    ngram_range: tuple[int, int] = Field(default=(1, 2), description="N-gram range (min, max)")


class ClusteringParams(NLPToolCall):
    """Parameters for clustering analysis."""
    text_column: str = Field(..., description="Column containing text data")
    num_clusters: int = Field(default=5, description="Number of clusters to create")
    method: str = Field(default="kmeans", description="Clustering method: kmeans, hierarchical, dbscan")
    id_column: str = Field(default="id", description="Column containing unique identifiers")
    include_metadata: list[str] = Field(default_factory=list, description="Additional columns to include (e.g., ['rating', 'date'])")


class SentimentParams(NLPToolCall):
    """Parameters for sentiment analysis."""
    text_column: str = Field(..., description="Column containing text data")
    rating_column: str = Field(default="rating", description="Column containing rating/score")
    include_distribution: bool = Field(default=True, description="Include rating distribution")
    group_by: str | None = Field(default=None, description="Column to group by (e.g., 'product', 'category')")


class FeatureParams(NLPToolCall):
    """Parameters for feature extraction."""
    text_column: str = Field(..., description="Column containing text data")
    min_frequency: int = Field(default=2, description="Minimum frequency for feature requests")
    rating_column: str = Field(default="rating", description="Column containing rating/score")
    id_column: str = Field(default="id", description="Column containing unique identifiers")
    extract_pain_points: bool = Field(default=True, description="Extract pain points in addition to features")
    extract_product_gaps: bool = Field(default=True, description="Extract product gaps")


def compute_tfidf_analysis(
    dataset_name: str,
    text_column: str,
    top_n: int = 10,
    min_df: int = 2,
    max_df: float = 0.8,
    ngram_range: tuple[int, int] = (1, 2)
) -> Dict[str, Any]:
    """
    Compute TF-IDF to find most important terms in text data.
    
    This tool identifies the most statistically significant terms in the dataset.
    Use this when you need to understand key topics or important words.
    
    Args:
        dataset_name: Name of the dataset to analyze (e.g., 'user_reviews', 'feedback_data')
        text_column: Column containing text data (e.g., 'review_text', 'feedback', 'comment')
        top_n: Number of top terms to return (default: 10)
        min_df: Minimum document frequency - ignore terms appearing in fewer docs (default: 2)
        max_df: Maximum document frequency - ignore terms appearing in more than this % (default: 0.8)
        ngram_range: N-gram range as (min, max) - e.g., (1,2) for unigrams and bigrams (default: (1,2))
    
    Returns:
        Dictionary with tool call parameters for execution
    """
    logger.info(f"TF-IDF tool called: dataset={dataset_name}, text_column={text_column}, top_n={top_n}")
    
    return {
        "tool": "compute_tfidf",
        "dataset_name": dataset_name,
        "parameters": {
            "text_column": text_column,
            "top_n": top_n,
            "min_df": min_df,
            "max_df": max_df,
            "ngram_range": ngram_range,
        }
    }


def cluster_reviews_analysis(
    dataset_name: str,
    text_column: str,
    num_clusters: int = 5,
    method: str = "kmeans",
    id_column: str = "id",
    include_metadata: list[str] | None = None
) -> Dict[str, Any]:
    """
    Cluster similar text entries by theme or topic.
    
    This tool groups similar reviews/feedback into thematic clusters.
    Use this when you need to identify common themes or group similar feedback.
    
    Args:
        dataset_name: Name of the dataset to analyze
        text_column: Column containing text data to cluster
        num_clusters: Number of clusters to create (default: 5)
        method: Clustering method - 'kmeans', 'hierarchical', or 'dbscan' (default: 'kmeans')
        id_column: Column containing unique identifiers (default: 'id')
        include_metadata: Additional columns to include in results (e.g., ['rating', 'date', 'user_id'])
    
    Returns:
        Dictionary with tool call parameters for execution
    """
    if include_metadata is None:
        include_metadata = []
    
    logger.info(f"Clustering tool called: dataset={dataset_name}, text_column={text_column}, num_clusters={num_clusters}")
    
    return {
        "tool": "cluster_reviews",
        "dataset_name": dataset_name,
        "parameters": {
            "text_column": text_column,
            "num_clusters": num_clusters,
            "method": method,
            "id_column": id_column,
            "include_metadata": include_metadata,
        }
    }


def analyze_sentiment_analysis(
    dataset_name: str,
    text_column: str,
    rating_column: str = "rating",
    include_distribution: bool = True,
    group_by: str | None = None
) -> Dict[str, Any]:
    """
    Analyze sentiment and rating distribution in the data.
    
    This tool analyzes sentiment patterns and rating distributions.
    Use this when you need to understand overall sentiment or rating trends.
    
    Args:
        dataset_name: Name of the dataset to analyze
        text_column: Column containing text data for sentiment analysis
        rating_column: Column containing rating/score (default: 'rating')
        include_distribution: Include detailed rating distribution (default: True)
        group_by: Optional column to group results by (e.g., 'product', 'category', 'date')
    
    Returns:
        Dictionary with tool call parameters for execution
    """
    logger.info(f"Sentiment tool called: dataset={dataset_name}, text_column={text_column}, rating_column={rating_column}")
    
    return {
        "tool": "analyze_sentiment",
        "dataset_name": dataset_name,
        "parameters": {
            "text_column": text_column,
            "rating_column": rating_column,
            "include_distribution": include_distribution,
            "group_by": group_by,
        }
    }


def identify_features_analysis(
    dataset_name: str,
    text_column: str,
    min_frequency: int = 2,
    rating_column: str = "rating",
    id_column: str = "id",
    extract_pain_points: bool = True,
    extract_product_gaps: bool = True
) -> Dict[str, Any]:
    """
    Identify feature requests, pain points, and product gaps from text data.
    
    This tool extracts and categorizes feature requests and pain points.
    Use this when you need to find what users are asking for or complaining about.
    
    Args:
        dataset_name: Name of the dataset to analyze
        text_column: Column containing text data to analyze
        min_frequency: Minimum frequency for feature requests (default: 2)
        rating_column: Column containing rating/score for context (default: 'rating')
        id_column: Column containing unique identifiers (default: 'id')
        extract_pain_points: Extract pain points in addition to features (default: True)
        extract_product_gaps: Extract product gaps (default: True)
    
    Returns:
        Dictionary with tool call parameters for execution
    """
    logger.info(f"Feature identification tool called: dataset={dataset_name}, text_column={text_column}, min_frequency={min_frequency}")
    
    return {
        "tool": "identify_features",
        "dataset_name": dataset_name,
        "parameters": {
            "text_column": text_column,
            "min_frequency": min_frequency,
            "rating_column": rating_column,
            "id_column": id_column,
            "extract_pain_points": extract_pain_points,
            "extract_product_gaps": extract_product_gaps,
        }
    }


# Create LlamaIndex FunctionTool instances
compute_tfidf_tool = FunctionTool.from_defaults(
    fn=compute_tfidf_analysis,
    name="compute_tfidf",
    description=(
        "Compute TF-IDF to find most important terms in text data. "
        "REQUIRED: dataset_name, text_column. "
        "OPTIONAL: top_n (default 10), min_df (default 2), max_df (default 0.8), ngram_range (default (1,2)). "
        "Use for: understanding key topics, important words, term frequency analysis."
    )
)

cluster_reviews_tool = FunctionTool.from_defaults(
    fn=cluster_reviews_analysis,
    name="cluster_reviews",
    description=(
        "Cluster similar text entries by theme or topic. "
        "REQUIRED: dataset_name, text_column. "
        "OPTIONAL: num_clusters (default 5), method (kmeans/hierarchical/dbscan), id_column (default 'id'), include_metadata (list of columns). "
        "Use for: identifying common themes, grouping similar feedback, topic discovery."
    )
)

analyze_sentiment_tool = FunctionTool.from_defaults(
    fn=analyze_sentiment_analysis,
    name="analyze_sentiment",
    description=(
        "Analyze sentiment and rating distribution in the data. "
        "REQUIRED: dataset_name, text_column. "
        "OPTIONAL: rating_column (default 'rating'), include_distribution (default True), group_by (column name). "
        "Use for: understanding sentiment trends, rating analysis, satisfaction metrics."
    )
)

identify_features_tool = FunctionTool.from_defaults(
    fn=identify_features_analysis,
    name="identify_features",
    description=(
        "Identify feature requests, pain points, and product gaps from text data. "
        "REQUIRED: dataset_name, text_column. "
        "OPTIONAL: min_frequency (default 2), rating_column (default 'rating'), id_column (default 'id'), "
        "extract_pain_points (default True), extract_product_gaps (default True). "
        "Use for: finding user needs, missing features, pain points, product gaps."
    )
)
