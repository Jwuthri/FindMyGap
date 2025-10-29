"""View schemas command."""

from app import get_logger
from app.database.base import SessionLocal
from app.workflows.utils.schema_manager_refactored import SchemaManagerService

logger = get_logger(__name__)


def view_platform_metadata(user_id=None):
    """View all platform dataset metadata."""
    
    logger.info("="*60)
    logger.info("AVAILABLE SCHEMAS")
    logger.info("="*60)
    
    db = SessionLocal()
    
    try:
        schema_service = SchemaManagerService(db)
        schemas = schema_service.get_all_available_schemas(user_id)
        print(schemas)
        
    finally:
        db.close()
