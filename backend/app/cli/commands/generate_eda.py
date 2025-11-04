"""Generate EDA command."""

from typing import Optional, List

from agno.models.openai import OpenAIChat

from app import get_logger
from app.config import SETTINGS
from app.database.base import SessionLocal
from app.services.eda_service import EDAService

logger = get_logger(__name__)


async def generate_eda_for_table(table_name: str):
    """Generate EDA for a specific table."""
    logger.info("="*60)
    logger.info(f"GENERATING EDA FOR TABLE: {table_name}")
    logger.info("="*60)
    
    model = OpenAIChat(id="gpt-5-mini", api_key=SETTINGS.OPENAI_API_KEY)
    db = SessionLocal()
    
    try:
        eda_service = EDAService(db)
        result = await eda_service.generate_eda_for_table(table_name, model)
        
        if result["success"]:
            logger.info(f"\n✅ EDA Generated Successfully")
            logger.info(f"Table: {result['table_name']}")
            logger.info(f"Rows: {result['row_count']}")
            logger.info(f"Columns: {result['column_count']}")
            logger.info(f"\nSummary:\n{result['summary']}")
            logger.info(f"\nField Metadata ({len(result['field_metadata'])} fields):")
            for field in result['field_metadata']:
                logger.info(f"\n  {field['field_name']} ({field['data_type']})")
                logger.info(f"    {field['description']}")
                if field.get('unique_value_count'):
                    logger.info(f"    Unique Values: {field['unique_value_count']}")
                if field.get('top_values'):
                    logger.info(f"    Top Values: {', '.join(field['top_values'][:5])}")
        else:
            logger.error(f"\n❌ Failed: {result['error']}")
        
    finally:
        db.close()


async def refresh_all_eda(table_names: Optional[List[str]] = None):
    """Refresh EDA for all tables or specific tables."""
    logger.info("="*60)
    logger.info("REFRESHING TABLE EDA")
    logger.info("="*60)
    
    model = OpenAIChat(id="gpt-5-mini", api_key=SETTINGS.OPENAI_API_KEY)
    db = SessionLocal()
    
    try:
        eda_service = EDAService(db)
        result = await eda_service.refresh_eda_for_all_tables(model, table_names)
        
        logger.info(f"\n✅ EDA Refresh Complete")
        logger.info(f"Total Tables: {result['total_tables']}")
        logger.info(f"Success: {result['success_count']}")
        logger.info(f"Failed: {result['failed_count']}")
        
        # Show details
        logger.info(f"\nDetails:")
        for r in result['results']:
            if r['success']:
                logger.info(f"  ✓ {r['table_name']} - {r['row_count']} rows")
            else:
                logger.info(f"  ✗ {r.get('table_name', 'unknown')} - {r.get('error', 'unknown error')}")
        
    finally:
        db.close()


def view_eda(table_name: str):
    """View EDA for a table."""
    logger.info("="*60)
    logger.info(f"TABLE EDA: {table_name}")
    logger.info("="*60)
    
    db = SessionLocal()
    
    try:
        eda_service = EDAService(db)
        eda = eda_service.get_eda(table_name)
        
        if not eda:
            logger.warning(f"\n⚠️  No EDA found for table: {table_name}")
            logger.info("Run: python -m app.cli generate-eda --table {table_name}")
            return
        
        logger.info(f"\nTable: {eda['table_name']}")
        logger.info(f"Rows: {eda['row_count']}")
        logger.info(f"Last Updated: {eda['updated_at']}")
        
        logger.info(f"\nSummary:\n{eda['summary']}")
        
        logger.info(f"\nField Metadata ({len(eda['insights'])} fields):")
        for field in eda['insights']:  # insights column stores field metadata
            logger.info(f"\n  {field['field_name']} ({field['data_type']})")
            logger.info(f"    {field['description']}")
            if field.get('unique_value_count'):
                logger.info(f"    Unique Values: {field['unique_value_count']}")
            if field.get('top_values'):
                logger.info(f"    Top Values: {', '.join(field['top_values'][:5])}")
        
    finally:
        db.close()
