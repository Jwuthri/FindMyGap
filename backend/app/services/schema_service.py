"""
Schema management workflow service.

Orchestrates schema-related operations:
1. Schema retrieval and formatting for LLM context
2. Platform dataset registration
"""

from typing import Any, Dict

from sqlalchemy.orm import Session

from app import get_logger
from app.database.repositories.dataset import PlatformDatasetRepository
from app.utils import database as db_utils
from app.utils import schema as schema_utils

logger = get_logger(__name__)


class SchemaService:
    """Workflow service for schema management operations."""

    def __init__(self, db: Session):
        """
        Initialize schema service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.platform_dataset_repo = PlatformDatasetRepository()

    def _log_prefix(self, user_id: str = None, company_id: str = None) -> str:
        """Generate log prefix following team standards."""
        return f"[SchemaService] | [user_id={user_id or 'None'}] | [company_id={company_id or 'None'}]"

    def get_all_available_schemas(self, user_id: str = None) -> str:
        """
        Get formatted schema string for all available tables.
        
        Includes both platform tables and user-uploaded datasets.
        
        Args:
            user_id: Optional user ID to filter user datasets
            
        Returns:
            Formatted string describing all available tables
        """
        return schema_utils.get_all_available_schemas(self.db, user_id)

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
            row_count = db_utils.get_table_row_count(self.db, table_name)
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
