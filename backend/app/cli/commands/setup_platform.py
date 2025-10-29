"""Setup platform datasets command."""

from agno.models.openai import OpenAIChat

from app import get_logger
from app.config import SETTINGS
from app.database.base import SessionLocal
from app.workflows.utils.data_ingestion_refactored import DataIngestionService
from app.workflows.utils.schema_manager_refactored import SchemaManagerService

logger = get_logger(__name__)


async def setup_platform_datasets():
    """Setup platform datasets with LLM-generated metadata."""
    
    logger.info("="*60)
    logger.info("SETTING UP PLATFORM DATASETS")
    logger.info("="*60)
    
    model = OpenAIChat(id="gpt-4o-mini", api_key=SETTINGS.OPENAI_API_KEY)
    db = SessionLocal()
    
    try:
        ingestion_service = DataIngestionService(db)
        schema_service = SchemaManagerService(db)
        
        platform_tables = ["reviews_feedback"]
        
        for table_name in platform_tables:
            logger.info(f"\n📊 Processing: {table_name}")
            
            if not schema_service.check_table_exists(table_name):
                logger.info(f"  ⚠️  Table doesn't exist, skipping...")
                continue
            
            result = await ingestion_service.generate_platform_metadata(table_name, model)
            
            if result["success"]:
                metadata = result["metadata"]
                logger.info(f"  ✅ Generated metadata")
                
                success = schema_service.register_platform_dataset(table_name, metadata)
                if success:
                    logger.info(f"  ✅ Registered in database")
                else:
                    logger.error(f"  ❌ Failed to register")
            else:
                logger.error(f"  ❌ Failed: {result['error']}")
        
        logger.info("\n" + "="*60)
        logger.info("SETUP COMPLETE")
        logger.info("="*60)
        
    finally:
        db.close()
