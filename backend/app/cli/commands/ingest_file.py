"""Ingest file command."""

from agno.models.openai import OpenAIChat

from app import get_logger
from app.config import SETTINGS
from app.database.base import SessionLocal
from app.workflows.utils.data_ingestion_refactored import DataIngestionService

logger = get_logger(__name__)


async def ingest_data_file(file_path: str, user_id: int):
    """Ingest a data file."""
    
    logger.info(f"Ingesting file: {file_path} for user: {user_id}")
    
    model = OpenAIChat(id="gpt-4o-mini", api_key=SETTINGS.OPENAI_API_KEY)
    db = SessionLocal()
    
    try:
        service = DataIngestionService(db)
        result = await service.ingest_data_file(file_path, user_id, model)
        
        if result["success"]:
            logger.info(f"✅ {result['message']}")
            logger.info(f"Table: {result['table_name']}")
            logger.info(f"Rows: {result['row_count']}")
        else:
            logger.error(f"❌ Failed: {result['error']}")
        
    finally:
        db.close()
