"""Initialize database command."""

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


async def init_database():
    """Initialize database with tables and sample data."""
    
    user_id = "julien123"
    
    logger.info("="*60)
    logger.info("DATABASE INITIALIZATION")
    logger.info("="*60)
    
    Path("tmp").mkdir(exist_ok=True)
    
    db = SessionLocal()
    
    try:
        logger.info("Step 1: Creating default user...")
        repo = UserRepository()
        existing = repo.get_by_id(db, user_id)
        if not existing:
            repo.create(db=db, email=f"{user_id}@example.com", username=user_id)
            logger.info(f"✓ Created user: {user_id}")
        else:
            logger.info(f"✓ User exists: {user_id}")
        
        logger.info("\nStep 2: Ingesting mock reviews...")
        ingestion_service = DataIngestionService(db)
        reviews_result = ingestion_service.ingest_mock_reviews()
        if reviews_result["success"]:
            logger.info(f"✓ Ingested {reviews_result['total_rows']} reviews")
        
        logger.info("\nStep 3: Registering platform metadata...")
        schema_service = SchemaManagerService(db)
        metadata = {
            "collection_name": "reviews_feedback",
            "description": "Customer reviews and feedback",
            "data_category": "customer_feedback",
            "field_descriptions": {
                "id": "Unique identifier",
                "company": "Company name",
                "rating": "Rating 1-5",
                "text": "Review content",
            },
            "key_fields": ["id", "company"],
            "embedding_fields": ["text"],
            "primary_text_field": "text",
            "combined_text_fields": [],
            "estimated_use_cases": ["Sentiment analysis", "Feature requests"],
            "potential_joins": ["company"],
            "data_quality_notes": "Complete dataset"
        }
        schema_service.register_platform_dataset("reviews_feedback", metadata)
        logger.info("✓ Registered platform metadata")
        
        logger.info("\n" + "="*60)
        logger.info("✓ Database initialized successfully!")
        logger.info("="*60)
        
    finally:
        db.close()
