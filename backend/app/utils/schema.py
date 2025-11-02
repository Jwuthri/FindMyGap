"""
Schema utility functions.

Provides schema formatting and retrieval utilities for LLM context.
"""

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app import get_logger
from app.database.repositories.dataset import (
    PlatformDatasetRepository,
    UserDatasetRepository,
)
from app.utils import database as db_utils

logger = get_logger(__name__)


def format_table_schema(
    table_name: str,
    columns: Dict[str, str],
    description: str = "",
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Format a single table schema in human-readable format for LLM.
    
    Args:
        table_name: Name of the table
        columns: Dict of column_name -> type/description
        description: Table description
        metadata: Optional metadata dict with embedding fields, key fields, etc.
        
    Returns:
        Formatted schema string
    """
    lines = [f"Table: {table_name}"]
    if description:
        lines.append(f"Description: {description}")
    lines.append("Columns:")
    
    for col_name, col_info in columns.items():
        lines.append(f"  - {col_name}: {col_info}")
    
    # Add semantic search info if available
    if metadata:
        if metadata.get("primary_text_field"):
            lines.append(f"Primary Text Field (for semantic search): {metadata['primary_text_field']}")
        if metadata.get("embedding_fields"):
            lines.append(f"Embedding Fields: {', '.join(metadata['embedding_fields'])}")
        if metadata.get("key_fields"):
            lines.append(f"Key Fields: {', '.join(metadata['key_fields'])}")
    
    return "\n".join(lines)


def get_all_available_schemas(db: Session, user_id: Optional[str] = None) -> str:
    """
    Get formatted schema string for all available tables.
    
    Includes both platform tables and user-uploaded datasets.
    
    Args:
        db: Database session
        user_id: Optional user ID to filter user datasets
        
    Returns:
        Formatted string describing all available tables
    """
    user_dataset_repo = UserDatasetRepository()
    platform_dataset_repo = PlatformDatasetRepository()
    
    schemas = []
    # 1. Add platform datasets
    platform_datasets = platform_dataset_repo.get_all(db)
    
    if platform_datasets:
        schemas.append("=" * 60)
        schemas.append("PLATFORM TABLES (Always Available)")
        schemas.append("=" * 60)
        
        for dataset in platform_datasets:
            # Get actual schema from database
            actual_columns = db_utils.get_table_schema(db, dataset.table_name)
            
            # Get metadata
            metadata = platform_dataset_repo.get_metadata(db, dataset.table_name)
            
            schema = format_table_schema(
                dataset.table_name,
                actual_columns,
                dataset.description or f"Platform dataset ({dataset.row_count} rows)",
                metadata=metadata
            )
            schemas.append(schema)
            schemas.append("")
    
    # 2. Add user-uploaded datasets if user_id provided
    if user_id:
        user_datasets = user_dataset_repo.get_by_user(db, user_id)
        
        if user_datasets:
            schemas.append("=" * 60)
            schemas.append(f"USER DATASETS (User: {user_id})")
            schemas.append("=" * 60)
            
            for dataset in user_datasets:
                # Get actual schema from database
                actual_columns = db_utils.get_table_schema(db, dataset.table_name)
                
                # SQLAlchemy automatically deserializes JSON columns
                metadata = dataset.column_metadata
                
                schema = format_table_schema(
                    dataset.table_name,
                    actual_columns,
                    dataset.description or f"User-uploaded dataset ({dataset.row_count} rows)",
                    metadata=metadata
                )
                schemas.append(schema)
                schemas.append("")
    
    return "\n".join(schemas)
