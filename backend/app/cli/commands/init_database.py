"""
Database initialization command.

This command:
1. Creates all necessary tables (users, user_datasets, platform_datasets, reviews_feedback)
2. Creates a default user (user_123)
3. Registers platform dataset metadata for reviews_feedback
4. Ingests mock reviews data
5. Ingests sample conversation data for the default user
"""

import pandas as pd
from pathlib import Path

from agno.models.openai import OpenAIChat

from app import get_logger
from app.config import SETTINGS
from app.database.base import SessionLocal
from app.database.repositories.user import UserRepository
from app.workflows.utils.data_ingestion_refactored import DataIngestionService
from app.workflows.utils.schema_manager_refactored import SchemaManagerService

logger = get_logger(__name__)


def create_default_user(db: SessionLocal, user_id: str):
    """Create a default user in the users table."""
    repo = UserRepository()
    
    try:
        # Check if user exists
        existing = repo.get_by_id(db, user_id)
        if existing:
            logger.info(f"✓ User already exists: {user_id}")
            return
        
        # Create new user
        repo.create(
            db=db,
            email=f"{user_id}@example.com",
            username=user_id
        )
        logger.info(f"✓ Created default user: {user_id}")
    except Exception as e:
        logger.error(f"Failed to create default user: {e}", exc_info=True)


def register_reviews_feedback_metadata(db: SessionLocal):
    """Register the reviews_feedback platform dataset with comprehensive metadata."""
    metadata = {
        "collection_name": "reviews_feedback",
        "description": "This dataset contains user reviews and feedback about the Spotify music application, collected from various sources.",
        "data_category": "customer_feedback",
        "field_descriptions": {
            "id": "Unique identifier for each review entry.",
            "company": "The name of the company associated with the review.",
            "category": "The category of the feedback.",
            "rating": "User rating for the application on a scale of 1 to 5.",
            "text": "The content of the user's review or feedback.",
            "source": "The platform from which the feedback was sourced.",
            "date": "The date when the review was submitted.",
            "author": "The username or identifier of the person who submitted the review."
        },
        "key_fields": ["id", "company", "rating", "text", "source", "date", "author"],
        "embedding_fields": ["text"],
        "primary_text_field": "text",
        "combined_text_fields": [],
        "estimated_use_cases": [
            "Sentiment analysis on user feedback",
            "Understanding user preferences",
            "Trend analysis over time",
            "Comparative analysis of feedback sources"
        ],
        "potential_joins": ["id", "company", "author"],
        "data_quality_notes": "Complete dataset with no missing values."
    }
    
    schema_service = SchemaManagerService(db)
    success = schema_service.register_platform_dataset("reviews_feedback", metadata)
    if success:
        logger.info("✓ Registered reviews_feedback platform dataset metadata")
    else:
        logger.error("Failed to register reviews_feedback metadata")


async def create_sample_conversations(db: SessionLocal, user_id: str = "user_123"):
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
    
    # Ingest using the data ingestion service
    model = OpenAIChat(id="gpt-4o-mini", api_key=SETTINGS.OPENAI_API_KEY)
    ingestion_service = DataIngestionService(db)
    
    result = await ingestion_service.ingest_data_file(
        file_path=str(csv_path),
        user_id=user_id,
        model=model
    )
    
    if result["success"]:
        logger.info(f"✓ Ingested sample conversations: {result['table_name']}")
    else:
        logger.error(f"Failed to ingest sample conversations: {result.get('error')}")
    
    return result


async def init_database():
    """Initialize the database with all tables and sample data."""
    
    user_id = "julien123"
    
    logger.info("="*60)
    logger.info("DATABASE INITIALIZATION")
    logger.info("="*60)
    
    # Ensure tmp directory exists
    Path("tmp").mkdir(exist_ok=True)
    
    db = SessionLocal()
    
    try:
        # Step 1: Tables are created by Alembic migrations
        logger.info("Step 1: Database tables (use 'alembic upgrade head' to create)")
        
        # Step 2: Create default user
        logger.info("\nStep 2: Creating default user...")
        create_default_user(db, user_id)
        
        # Step 3: Ingest mock reviews data
        logger.info("\nStep 3: Ingesting mock reviews data...")
        ingestion_service = DataIngestionService(db)
        reviews_result = ingestion_service.ingest_mock_reviews()
        if reviews_result["success"]:
            logger.info(f"✓ Ingested {reviews_result['total_rows']} reviews from {len(reviews_result['companies'])} companies")
        else:
            logger.error(f"Failed to ingest reviews: {reviews_result.get('error')}")
        
        # Step 4: Register platform dataset metadata
        logger.info("\nStep 4: Registering platform dataset metadata...")
        register_reviews_feedback_metadata(db)
        
        # Step 5: Create and ingest sample conversations
        logger.info("\nStep 5: Creating sample user dataset...")
        conversations_result = await create_sample_conversations(db, user_id)
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("INITIALIZATION COMPLETE")
        logger.info("="*60)
        logger.info(f"Default User: {user_id}")
        logger.info(f"\nData ingested:")
        logger.info(f"  - reviews_feedback ({reviews_result.get('total_rows', 0)} rows)")
        if conversations_result.get("success"):
            logger.info(f"  - {conversations_result['table_name']} ({conversations_result['row_count']} rows)")
        logger.info("\n✓ Database ready for use!")
        
    finally:
        db.close()
