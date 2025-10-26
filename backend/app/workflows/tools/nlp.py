import json
from collections import Counter
import math

from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool

from app.workflows.mock_data import get_reviews
from app.config import SETTINGS

# ============================================================================
# ML & ANALYSIS TOOLS
# ============================================================================
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


@tool(requires_confirmation=False)
def compute_tfidf(company: str, top_n: int = 10) -> str:
    """
    Compute TF-IDF to find most important terms in reviews.
    
    Args:
        company: Company name (spotify, notion, slack)
        top_n: How many top terms to return (default 10)
    
    Returns:
        JSON with top terms and TF-IDF scores
    """
    reviews = get_reviews(company)
    
    if not reviews:
        return json.dumps({"error": f"No reviews for {company}"})
    
    # Get review texts
    documents = [r["text"].lower() for r in reviews]
    
    # Build word frequencies
    word_doc_count = {}
    word_freq_per_doc = []
    
    for doc in documents:
        words = [w for w in doc.split() if len(w) > 3 and w not in STOPWORDS]
        word_freq = Counter(words)
        word_freq_per_doc.append(word_freq)
        
        for word in set(words):
            word_doc_count[word] = word_doc_count.get(word, 0) + 1
    
    # Calculate TF-IDF
    num_docs = len(documents)
    tfidf_scores = {}
    
    for word, doc_count in word_doc_count.items():
        if doc_count < 2:  # Skip words in only 1 doc
            continue
            
        idf = math.log(num_docs / doc_count)
        total_tf = sum(freq.get(word, 0) for freq in word_freq_per_doc)
        avg_tf = total_tf / num_docs
        tfidf_scores[word] = avg_tf * idf
    
    # Get top N
    top_terms = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    return json.dumps({
        "company": company,
        "reviews_analyzed": num_docs,
        "top_terms": [
            {"term": term, "score": round(score, 3)}
            for term, score in top_terms
        ]
    })


@tool(requires_confirmation=False)
def analyze_sentiment_distribution(company: str) -> str:
    """
    Analyze rating distribution and sentiment patterns.
    
    Args:
        company: Company name
    
    Returns:
        JSON string with sentiment analysis
    """
    reviews = get_reviews(company)
    
    if not reviews:
        return json.dumps({"error": "No reviews found"})
    
    # Rating distribution
    rating_counts = Counter(r["rating"] for r in reviews)
    total = len(reviews)
    
    # Sentiment categories
    positive = sum(rating_counts.get(r, 0) for r in [4, 5])
    neutral = rating_counts.get(3, 0)
    negative = sum(rating_counts.get(r, 0) for r in [1, 2])
    
    # Source distribution
    source_counts = Counter(r["source"] for r in reviews)
    
    # Average rating
    avg_rating = sum(r["rating"] for r in reviews) / total
    
    return json.dumps({
        "company": company,
        "total_reviews": total,
        "average_rating": round(avg_rating, 2),
        "sentiment_distribution": {
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
            "positive_percent": round((positive / total) * 100, 1),
            "negative_percent": round((negative / total) * 100, 1)
        },
        "rating_breakdown": dict(rating_counts),
        "source_breakdown": dict(source_counts)
    }, indent=2)


@tool(requires_confirmation=False)
def identify_feature_requests(company: str) -> str:
    """
    Use LLM to identify feature requests, pain points, and product gaps from reviews.
    
    Args:
        company: Company name
    
    Returns:
        JSON string with analyzed feature requests and gaps
    """
    reviews = get_reviews(company)
    
    if not reviews:
        return json.dumps({"error": "No reviews found"})
    
    # Create a focused agent for feature extraction
    model = OpenAIChat(id="gpt-5-mini", api_key=SETTINGS.OPENAI_API_KEY)
    
    analysis_agent = Agent(
        name="Feature Analysis Agent",
        model=model,
        instructions=[
            "Analyze customer reviews to identify feature requests, pain points, and product gaps",
            "Group similar requests together",
            "Quantify frequency and impact"
        ],
        response_model=FeatureAnalysisResult,
        markdown=False
    )
    
    # Prepare review data
    review_texts = "\n\n".join([
        f"Review {i+1} (Rating: {r['rating']}/5, {r['date']}):\n{r['text']}"
        for i, r in enumerate(reviews[:500])  # Limit to avoid token issues
    ])
    
    prompt = f"""Analyze these {company} reviews and identify:

1. Feature requests (what users want added)
2. Pain points (what frustrates users)
3. Product gaps (missing functionality vs competitors)

Reviews:
{review_texts}"""
    
    response = analysis_agent.run(prompt)
    return response.content.model_dump_json(indent=2)


@tool(requires_confirmation=False)
def cluster_similar_reviews(company: str, num_clusters: int = 5) -> str:
    """
    Use LLM to intelligently group reviews by theme/topic.
    
    Args:
        company: Company name
        num_clusters: Number of topic clusters to identify
    
    Returns:
        JSON string with thematic clusters
    """
    reviews = get_reviews(company)
    
    if not reviews:
        return json.dumps({"error": "No reviews found"})
    
    model = OpenAIChat(id="gpt-5-mini", api_key=SETTINGS.OPENAI_API_KEY)
    
    clustering_agent = Agent(
        name="Review Clustering Agent",
        model=model,
        instructions=[
            f"Group reviews into {num_clusters} thematic clusters",
            "Identify the main topic/theme of each cluster",
            "Assign reviews to the most relevant cluster",
            "Provide clear cluster names and descriptions"
        ],
        response_model=ClusteringResult,
        markdown=False
    )
    
    # Prepare condensed review data
    review_summary = "\n".join([
        f"{i+1}. [{r['rating']}★] {r['text'][:100]}..."
        for i, r in enumerate(reviews[:50])
    ])
    
    prompt = f"""Analyze these {company} customer reviews and group them into {num_clusters} thematic clusters.

Reviews:
{review_summary}"""
    
    response = clustering_agent.run(prompt)
    result = response.content.model_dump()
    result["company"] = company
    result["total_reviews_analyzed"] = len(reviews)
    return json.dumps(result, indent=2)
