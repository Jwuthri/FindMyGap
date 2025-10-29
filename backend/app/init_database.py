"""
Database initialization script.

This script:
1. Creates all necessary tables (users, user_datasets, platform_datasets, reviews_feedback)
2. Creates a default user (user_123)
3. Registers platform dataset metadata for reviews_feedback
4. Ingests mock reviews data
5. Ingests sample conversation data for the default user
"""

import asyncio
import sys
import sqlite3
import pandas as pd
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.workflows.utils.schema_manager import (
    init_metadata_table,
    init_platform_metadata_table,
    init_user_table,
    register_platform_dataset,
)
from app.workflows.utils.data_ingestion import ingest_mock_reviews, ingest_data_file
from app.config import SETTINGS
from agno.models.openai import OpenAIChat
from app import get_logger

logger = get_logger("scripts.init_database")


def create_default_user(db_path: str, user_id: str):
    """Create a default user in the users table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO users (user_id, email, username)
            VALUES (?, ?, ?)
        """, (user_id, f"{user_id}@example.com", user_id))
        
        conn.commit()
        logger.info(f"✓ Created default user: {user_id}")
    except Exception as e:
        logger.error(f"Failed to create default user: {e}")
    finally:
        conn.close()


def register_reviews_feedback_metadata(db_path: str):
    """Register the reviews_feedback platform dataset with comprehensive metadata."""
    metadata = {
        "collection_name": "reviews_feedback",
        "description": "This dataset contains user reviews and feedback about the Spotify music application, collected from various sources. Each entry includes the review content, ratings, and other metadata related to the feedback, allowing for analysis of user sentiment and feature requests over time.",
        "data_category": "customer_feedback",
        "field_descriptions": {
            "id": "Unique identifier for each review entry.",
            "company": "The name of the company associated with the review, in this case, Spotify.",
            "category": "The category of the feedback, currently fixed as 'review'.",
            "rating": "User rating for the application on a scale of 1 to 5.",
            "text": "The content of the user's review or feedback, detailing their experiences and suggestions.",
            "source": "The platform from which the feedback was sourced, such as app stores or forums.",
            "date": "The date when the review was submitted.",
            "author": "The username or identifier of the person who submitted the review."
        },
        "key_fields": ["id", "company", "rating", "text", "source", "date", "author"],
        "embedding_fields": ["text"],
        "primary_text_field": "text",
        "combined_text_fields": None,
        "estimated_use_cases": [
            "Sentiment analysis on user feedback to improve product features.",
            "Understanding user preferences for targeted marketing or feature development.",
            "Trend analysis over time related to user satisfaction and feature requests.",
            "Comparative analysis of user feedback from different sources to gauge reliability of review platforms."
        ],
        "potential_joins": ["id", "company", "author"],
        "data_quality_notes": "The dataset appears to have no missing values, ensuring completeness for analysis. The consistency of entries is good, but future reviews may introduce variability in categories or text formatting."
    }
    
    success = register_platform_dataset(db_path, "reviews_feedback", metadata)
    if success:
        logger.info("✓ Registered reviews_feedback platform dataset metadata")
    else:
        logger.error("Failed to register reviews_feedback metadata")


async def create_sample_conversations(db_path: str, user_id: str = "user_123"):
    """Create and ingest sample conversations data for the default user."""
    logger.info("Creating sample conversations data...")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'conversation_id': ['conv_001', 'conv_001', 'conv_002', 'conv_002', 'conv_003'],
        'message_index': [1, 2, 1, 2, 1],
        'author': ['customer', 'agent', 'customer', 'agent', 'customer'],
        'content': [
            'My product is not working properly',
            'Sorry to hear that. Can you describe the issue?',
            'I need a refund for my order',
            'I can help you with that. What is your order number?',
            'How do I track my shipment?'
        ],
        'timestamp': [
            '2024-01-15 10:30:00',
            '2024-01-15 10:35:00',
            '2024-01-15 11:00:00',
            '2024-01-15 11:05:00',
            '2024-01-16 09:15:00'
        ],
        'subject': ['Product Issue', 'Product Issue', 'Refund Request', 'Refund Request', 'Shipping Question']
    })
    
    # Save to temporary CSV
    tmp_dir = Path("tmp")
    tmp_dir.mkdir(exist_ok=True)
    csv_path = tmp_dir / "sample_conversations.csv"
    sample_data.to_csv(csv_path, index=False)
    
    # Ingest using the data ingestion pipeline
    model = OpenAIChat(id="gpt-4o-mini", api_key=SETTINGS.OPENAI_API_KEY)
    
    result = await ingest_data_file(
        file_path=str(csv_path),
        user_id=user_id,
        db_path=db_path,
        model=model
    )
    
    if result["success"]:
        logger.info(f"✓ Ingested sample conversations: {result['table_name']}")
    else:
        logger.error(f"Failed to ingest sample conversations: {result.get('error')}")
    
    return result


async def main():
    """Initialize the database with all tables and sample data."""
    
    db_path = "memory.db"
    user_id = "julien123"
    
    logger.info("="*60)
    logger.info("DATABASE INITIALIZATION")
    logger.info("="*60)
    logger.info(f"Database: {db_path}\n")
    
    # Ensure tmp directory exists
    Path("tmp").mkdir(exist_ok=True)
    
    # Step 1: Initialize all tables
    logger.info("Step 1: Creating database tables...")
    init_user_table(db_path)
    init_metadata_table(db_path)
    init_platform_metadata_table(db_path)
    
    # Step 2: Create default user
    logger.info("\nStep 2: Creating default user...")
    create_default_user(db_path, user_id)
    
    # Step 3: Ingest mock reviews data
    logger.info("\nStep 3: Ingesting mock reviews data...")
    reviews_result = ingest_mock_reviews(db_path)
    if reviews_result["success"]:
        logger.info(f"✓ Ingested {reviews_result['total_rows']} reviews from {len(reviews_result['companies'])} companies")
    else:
        logger.error(f"Failed to ingest reviews: {reviews_result.get('error')}")
    
    # Step 4: Register platform dataset metadata
    logger.info("\nStep 4: Registering platform dataset metadata...")
    register_reviews_feedback_metadata(db_path)
    
    # Step 5: Create and ingest sample conversations
    logger.info("\nStep 5: Creating sample user dataset...")
    conversations_result = await create_sample_conversations(db_path, user_id)
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("INITIALIZATION COMPLETE")
    logger.info("="*60)
    logger.info(f"Database: {db_path}")
    logger.info(f"Default User: {user_id}")
    logger.info(f"\nTables created:")
    logger.info(f"  - users")
    logger.info(f"  - user_datasets")
    logger.info(f"  - platform_datasets")
    logger.info(f"  - reviews_feedback ({reviews_result.get('total_rows', 0)} rows)")
    if conversations_result.get("success"):
        logger.info(f"  - {conversations_result['table_name']} ({conversations_result['row_count']} rows)")
    logger.info("\n✓ Database ready for use!")


if __name__ == "__main__":
    asyncio.run(main())
