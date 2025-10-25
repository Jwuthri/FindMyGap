"""
Mock review data for Find My Gaps analysis.
"""

from datetime import datetime, timedelta
import random
from typing import List, Dict, Any

# Mock review database
MOCK_REVIEWS = {
    "spotify": [
        {"id": 1, "rating": 2, "text": "Missing lyrics sync feature that Apple Music has. Would pay extra for this.", "source": "app_store", "date": "2025-10-15", "author": "user123"},
        {"id": 2, "rating": 5, "text": "Best music app ever! Love the AI DJ feature.", "source": "app_store", "date": "2025-10-14", "author": "musicfan"},
        {"id": 3, "rating": 3, "text": "Good but needs better podcast discovery. I can't find niche podcasts easily.", "source": "reddit", "date": "2025-10-13", "author": "podcastlover"},
        {"id": 4, "rating": 1, "text": "Terrible shuffle algorithm. Keeps playing same songs. Need better randomization.", "source": "trustpilot", "date": "2025-10-12", "author": "frustrated_user"},
        {"id": 5, "rating": 4, "text": "Great app but missing sleep timer for podcasts. Please add this!", "source": "reddit", "date": "2025-10-11", "author": "sleepy_listener"},
        {"id": 6, "rating": 2, "text": "No way to transfer playlists to other platforms. Lock-in is frustrating.", "source": "app_store", "date": "2025-10-10", "author": "switcher"},
        {"id": 7, "rating": 5, "text": "Discover Weekly is mind-blowing. Always finds music I love.", "source": "app_store", "date": "2025-10-09", "author": "discovery_fan"},
        {"id": 8, "rating": 3, "text": "Needs better audio quality options. Competitors have lossless audio.", "source": "reddit", "date": "2025-10-08", "author": "audiophile"},
        {"id": 9, "rating": 1, "text": "Desktop app is bloated and slow. Takes forever to load.", "source": "trustpilot", "date": "2025-10-07", "author": "desktop_user"},
        {"id": 10, "rating": 4, "text": "Love it but wish there was collaborative queue for parties.", "source": "reddit", "date": "2025-10-06", "author": "party_host"},
        {"id": 11, "rating": 2, "text": "Missing karaoke mode. Would be amazing for social features.", "source": "app_store", "date": "2025-10-05", "author": "karaoke_lover"},
        {"id": 12, "rating": 5, "text": "Interface is clean and intuitive. Easy to use.", "source": "app_store", "date": "2025-10-04", "author": "ux_designer"},
        {"id": 13, "rating": 3, "text": "Need better integration with smart home devices. Alexa support is lacking.", "source": "reddit", "date": "2025-10-03", "author": "smart_home_user"},
        {"id": 14, "rating": 1, "text": "Ads are too frequent on free tier. Unbearable experience.", "source": "trustpilot", "date": "2025-10-02", "author": "free_user"},
        {"id": 15, "rating": 4, "text": "Great but needs concert recommendations based on my music taste.", "source": "reddit", "date": "2025-10-01", "author": "concert_goer"},
    ],
    "notion": [
        {"id": 16, "rating": 2, "text": "Mobile app is painfully slow. Takes 5 seconds to open a page.", "source": "app_store", "date": "2025-10-15", "author": "mobile_user"},
        {"id": 17, "rating": 5, "text": "Best note-taking app! So flexible and powerful.", "source": "app_store", "date": "2025-10-14", "author": "power_user"},
        {"id": 18, "rating": 3, "text": "Offline mode is terrible. Can't access anything without internet.", "source": "reddit", "date": "2025-10-13", "author": "traveler"},
        {"id": 19, "rating": 1, "text": "No proper Markdown export. Lock-in is real concern.", "source": "trustpilot", "date": "2025-10-12", "author": "concerned_user"},
        {"id": 20, "rating": 4, "text": "Love it but needs better table functionality. Excel-like features missing.", "source": "reddit", "date": "2025-10-11", "author": "data_person"},
        {"id": 21, "rating": 2, "text": "Collaboration is buggy. Changes don't sync in real-time.", "source": "app_store", "date": "2025-10-10", "author": "team_lead"},
        {"id": 22, "rating": 5, "text": "Templates are amazing. Saved me hours of work.", "source": "app_store", "date": "2025-10-09", "author": "template_fan"},
        {"id": 23, "rating": 3, "text": "Search is terrible. Can't find notes even when I know exact words.", "source": "reddit", "date": "2025-10-08", "author": "searcher"},
        {"id": 24, "rating": 1, "text": "No version history on free plan. Lost important work twice.", "source": "trustpilot", "date": "2025-10-07", "author": "student"},
        {"id": 25, "rating": 4, "text": "Great but needs better calendar integration. Want to see tasks in calendar view.", "source": "reddit", "date": "2025-10-06", "author": "planner"},
    ],
    "slack": [
        {"id": 26, "rating": 2, "text": "Missing AI summarization of long threads. Would save so much time.", "source": "trustpilot", "date": "2025-10-15", "author": "busy_manager"},
        {"id": 27, "rating": 5, "text": "Best team communication tool. Can't imagine work without it.", "source": "app_store", "date": "2025-10-14", "author": "remote_worker"},
        {"id": 28, "rating": 3, "text": "Needs better video call quality. Zoom is much better.", "source": "reddit", "date": "2025-10-13", "author": "video_caller"},
        {"id": 29, "rating": 1, "text": "Search is useless after 90 days on free plan. Ridiculous limitation.", "source": "trustpilot", "date": "2025-10-12", "author": "free_tier_user"},
        {"id": 30, "rating": 4, "text": "Love it but need better thread organization. Hard to follow conversations.", "source": "reddit", "date": "2025-10-11", "author": "thread_follower"},
    ]
}


def get_reviews(company: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get mock reviews for a company.
    
    Args:
        company: Company name (lowercase)
        limit: Maximum number of reviews
    
    Returns:
        List of review dictionaries
    """
    company = company.lower()
    if company not in MOCK_REVIEWS:
        return []
    
    return MOCK_REVIEWS[company][:limit]


def get_all_companies() -> List[str]:
    """Get list of companies with mock reviews."""
    return list(MOCK_REVIEWS.keys())


def get_reviews_by_rating(company: str, min_rating: int = 1, max_rating: int = 5) -> List[Dict[str, Any]]:
    """
    Get reviews filtered by rating range.
    
    Args:
        company: Company name
        min_rating: Minimum rating (1-5)
        max_rating: Maximum rating (1-5)
    
    Returns:
        Filtered reviews
    """
    reviews = get_reviews(company)
    return [r for r in reviews if min_rating <= r["rating"] <= max_rating]


def get_reviews_by_source(company: str, source: str) -> List[Dict[str, Any]]:
    """
    Get reviews from specific source.
    
    Args:
        company: Company name
        source: Source name (app_store, reddit, trustpilot)
    
    Returns:
        Filtered reviews
    """
    reviews = get_reviews(company)
    return [r for r in reviews if r["source"] == source]


def search_reviews(company: str, keyword: str) -> List[Dict[str, Any]]:
    """
    Search reviews by keyword.
    
    Args:
        company: Company name
        keyword: Search keyword
    
    Returns:
        Matching reviews
    """
    reviews = get_reviews(company)
    keyword_lower = keyword.lower()
    return [r for r in reviews if keyword_lower in r["text"].lower()]

