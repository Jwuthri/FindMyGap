"""
Schema management utilities using SQLAlchemy and repository pattern.

This module handles:
1. Schema fetching and formatting for LLM context
2. Dataset registration and retrieval
3. Platform dataset management
"""

from typing import Any, Dict, List, Optional

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app import get_logger
from app.database.repositories.dataset import (
    PlatformDatasetRepository,
    UserDatasetRepository,
)

logger = get_logger(__name__)


class SchemaManagerService:
    """Service for schema management operations."""

    def __init__(self, db: Session):
        """
        Initialize schema manager service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.user_dataset_repo = UserDatasetRepository()
        self.platform_dataset_repo = PlatformDatasetRepository()

    def _log_prefix(self, user_id: Optional[str] = None, company_id: Optional[str] = None) -> str:
        """Generate log prefix following team standards."""
        return f"[SchemaManagerService] | [user_id={user_id or 'None'}] | [company_id={company_id or 'None'}]"

    def get_table_schema(self, table_name: str) -> Dict[str, str]:
        """
        Fetch actual schema from database using SQLAlchemy inspector.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dict mapping column names to their types
        """
        inspector = inspect(self.db.bind)
        columns = {}
        
        try:
            for column in inspector.get_columns(table_name):
                columns[column['name']] = str(column['type'])
        except Exception as e:
            logger.error(f"{self._log_prefix()} | Failed to get schema for {table_name}: {e}")
        
        return columns

    def check_table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table exists, False otherwise
        """
        inspector = inspect(self.db.bind)
        return table_name in inspector.get_table_names()

    def format_table_schema_for_llm(
        self,
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

    def get_all_available_schemas(self, user_id: Optional[str] = None) -> str:
        """
        Get formatted schema string for all available tables.
        
        Includes both platform tables and user-uploaded datasets.
        
        Args:
            user_id: Optional user ID to filter user datasets
            
        Returns:
            Formatted string describing all available tables
        """
        schemas = []
        
        # 1. Add platform datasets
        platform_datasets = self.platform_dataset_repo.get_all(self.db)
        
        if platform_datasets:
            schemas.append("=" * 60)
            schemas.append("PLATFORM TABLES (Always Available)")
            schemas.append("=" * 60)
            
            for dataset in platform_datasets:
                # Get actual schema from database
                actual_columns = self.get_table_schema(dataset.table_name)
                
                # Get metadata
                metadata = self.platform_dataset_repo.get_metadata(self.db, dataset.table_name)
                
                schema = self.format_table_schema_for_llm(
                    dataset.table_name,
                    actual_columns,
                    dataset.description or f"Platform dataset ({dataset.row_count} rows)",
                    metadata=metadata
                )
                schemas.append(schema)
                schemas.append("")
        
        # 2. Add user-uploaded datasets if user_id provided
        if user_id:
            user_datasets = self.user_dataset_repo.get_by_user(self.db, user_id)
            
            if user_datasets:
                schemas.append("=" * 60)
                schemas.append(f"USER DATASETS (User: {user_id})")
                schemas.append("=" * 60)
                
                for dataset in user_datasets:
                    # Get actual schema from database
                    actual_columns = self.get_table_schema(dataset.table_name)
                    
                    # SQLAlchemy automatically deserializes JSON columns
                    metadata = dataset.column_metadata
                    
                    schema = self.format_table_schema_for_llm(
                        dataset.table_name,
                        actual_columns,
                        dataset.description or f"User-uploaded dataset ({dataset.row_count} rows)",
                        metadata=metadata
                    )
                    schemas.append(schema)
                    schemas.append("")
        
        return "\n".join(schemas)

    def register_platform_dataset(
        self,
        table_name: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Register a platform dataset with its metadata.
        
        Args:
            table_name: Name of the platform table
            metadata: DatasetMetadata dict from LLM agent
            
        Returns:
            True if successful
        """
        try:
            # Get row count from actual table
            result = self.db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            row_count = result.scalar()
            metadata["row_count"] = row_count
            
            self.platform_dataset_repo.create(
                db=self.db,
                table_name=table_name,
                collection_name=metadata.get("collection_name", table_name),
                metadata=metadata
            )
            
            logger.info(f"{self._log_prefix()} | Registered platform dataset: {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"{self._log_prefix()} | Failed to register platform dataset: {e}", exc_info=True)
            return False


# Hardcoded platform tables for reference
PLATFORM_TABLES = {
    "reviews_feedback": {
        "description": "Customer reviews from various platforms",
        "columns": {
            "id": "INTEGER PRIMARY KEY",
            "company": "TEXT - Company/product name",
            "rating": "INTEGER - Rating score (1-5)",
            "category": "TEXT - category (review, feedback, etc.)",
            "source": "TEXT - Platform (app_store, reddit, trustpilot, etc.)",
            "text": "TEXT - Full review content",
            "author": "TEXT - Review author",
            "date": "TIMESTAMP - Review creation date"
        }
    }
}
