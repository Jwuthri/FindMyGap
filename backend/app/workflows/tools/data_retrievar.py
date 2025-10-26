import json

from agno.tools import tool

from app.workflows.mock_data import (
    get_reviews,
    get_all_companies,
    get_reviews_by_rating,
    get_reviews_by_source,
    search_reviews
)

# ============================================================================
# DATA RETRIEVAL TOOLS
# ============================================================================

@tool(requires_confirmation=False)
def retrieve_reviews(company: str, limit: int = 100) -> str:
    """
    Retrieve customer reviews for a company.
    
    Args:
        company: Company name (e.g., "spotify", "notion", "slack")
        limit: Maximum number of reviews to retrieve
    
    Returns:
        JSON string with reviews
    """
    reviews = get_reviews(company, limit)
    return json.dumps({
        "company": company,
        "total_reviews": len(reviews),
        "reviews": reviews
    }, indent=2)


@tool(requires_confirmation=False)
def filter_reviews_by_rating(company: str, min_rating: int, max_rating: int) -> str:
    """
    Filter reviews by rating range.
    
    Args:
        company: Company name
        min_rating: Minimum rating (1-5)
        max_rating: Maximum rating (1-5)
    
    Returns:
        JSON string with filtered reviews
    """
    reviews = get_reviews_by_rating(company, min_rating, max_rating)
    return json.dumps({
        "company": company,
        "rating_range": f"{min_rating}-{max_rating}",
        "total_reviews": len(reviews),
        "reviews": reviews
    }, indent=2)


@tool(requires_confirmation=False)
def filter_reviews_by_source(company: str, source: str) -> str:
    """
    Filter reviews by source platform.
    
    Args:
        company: Company name
        source: Source platform (app_store, reddit, trustpilot)
    
    Returns:
        JSON string with filtered reviews
    """
    reviews = get_reviews_by_source(company, source)
    return json.dumps({
        "company": company,
        "source": source,
        "total_reviews": len(reviews),
        "reviews": reviews
    }, indent=2)


@tool(requires_confirmation=False)
def search_reviews_by_keyword(company: str, keyword: str) -> str:
    """
    Search reviews containing specific keyword.
    
    Args:
        company: Company name
        keyword: Search keyword
    
    Returns:
        JSON string with matching reviews
    """
    reviews = search_reviews(company, keyword)
    return json.dumps({
        "company": company,
        "keyword": keyword,
        "total_matches": len(reviews),
        "reviews": reviews
    }, indent=2)


@tool(requires_confirmation=False)
def list_available_companies() -> str:
    """
    List all companies with available review data.
    
    Returns:
        JSON string with company list
    """
    companies = get_all_companies()
    return json.dumps({
        "total_companies": len(companies),
        "companies": companies
    }, indent=2)
