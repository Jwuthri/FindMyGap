"""Ingest mock data command."""

from app import get_logger
from app.database.base import SessionLocal
from app.workflows.utils.data_ingestion_refactored import DataIngestionService

logger = get_logger(__name__)


def ingest_mock_data():
    """Ingest mock review data."""
    
    logger.info("="*60)
    logger.info("INGESTING MOCK REVIEW DATA")
    logger.info("="*60)
    
    db = SessionLocal()
    
    try:
        ingestion_service = DataIngestionService(db)
        result = ingestion_service.ingest_mock_reviews()
        
        if result["success"]:
            logger.info(f"\n✅ {result['message']}")
            logger.info(f"Total Rows: {result['total_rows']}")
            logger.info(f"Companies: {len(result['companies'])}")
        else:
            logger.error(f"\n❌ Failed: {result['error']}")
        
    finally:
        db.close()
