"""
Dataset repository for FindMyGap.

Handles CRUD operations for user datasets and platform datasets.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app import get_logger
from app.database.models.dataset import PlatformDatasetTable, UserDatasetTable

logger = get_logger(__name__)


class UserDatasetRepository:
    """Repository for UserDataset model operations."""

    def _log_prefix(self, user_id: Optional[str] = None, company_id: Optional[str] = None) -> str:
        """Generate log prefix following team standards."""
        return f"[UserDatasetRepository] | [user_id={user_id or 'None'}] | [company_id={company_id or 'None'}]"

    def create(
        self,
        db: Session,
        user_id: int,
        table_name: str,
        original_filename: str = None,
        description: str = None,
        column_metadata: Dict[str, Any] = None,
        row_count: int = 0
    ) -> UserDatasetTable:
        """
        Create a new user dataset.
        
        Args:
            db: Database session
            user_id: User ID who owns this dataset
            table_name: Name of the table created for this dataset
            original_filename: Original filename of uploaded file
            description: Optional description of the dataset
            column_metadata: Optional dict with column descriptions
            row_count: Number of rows in the dataset
            
        Returns:
            Created UserDatasetTable object
        """
        dataset = UserDatasetTable(
            user_id=user_id,
            table_name=table_name,
            original_filename=original_filename,
            description=description,
            column_metadata=column_metadata,  # SQLAlchemy handles JSON serialization
            row_count=row_count
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        
        logger.info(f"{self._log_prefix(user_id)} | Created dataset: {table_name}")
        return dataset

    def get_by_id(self, db: Session, dataset_id: int) -> Optional[UserDatasetTable]:
        """Get user dataset by ID."""
        return db.query(UserDatasetTable).filter(UserDatasetTable.id == dataset_id).first()

    def get_by_table_name(self, db: Session, table_name: str) -> Optional[UserDatasetTable]:
        """Get user dataset by table name."""
        return db.query(UserDatasetTable).filter(UserDatasetTable.table_name == table_name).first()

    def get_by_user(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserDatasetTable]:
        """
        Get all datasets for a specific user.
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of UserDatasetTable objects
        """
        return (
            db.query(UserDatasetTable)
            .filter(UserDatasetTable.user_id == user_id)
            .order_by(UserDatasetTable.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_user_dataset_names(self, db: Session, user_id: int) -> List[str]:
        """
        Get list of dataset names for a user (without user_id prefix).
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of dataset names without prefix
        """
        datasets = self.get_by_user(db, user_id)
        prefix = f"user_{user_id}_"
        
        dataset_names = []
        for dataset in datasets:
            table_name = dataset.table_name
            if table_name.startswith(prefix):
                clean_name = table_name[len(prefix):]
                dataset_names.append(clean_name)
            else:
                dataset_names.append(table_name)
        
        return dataset_names

    def update(
        self,
        db: Session,
        dataset_id: int,
        **kwargs
    ) -> Optional[UserDatasetTable]:
        """Update user dataset."""
        dataset = self.get_by_id(db, dataset_id)
        if not dataset:
            return None

        for key, value in kwargs.items():
            if hasattr(dataset, key):
                setattr(dataset, key, value)  # SQLAlchemy handles JSON serialization

        dataset.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(dataset)
        return dataset

    def delete(self, db: Session, dataset_id: int) -> bool:
        """Delete user dataset by ID."""
        dataset = self.get_by_id(db, dataset_id)
        if dataset:
            user_id = dataset.user_id
            table_name = dataset.table_name
            db.delete(dataset)
            db.commit()
            logger.info(f"{self._log_prefix(user_id)} | Deleted dataset: {table_name}")
            return True
        return False

    def table_exists(self, db: Session, table_name: str) -> bool:
        """Check if a table name is already registered."""
        return db.query(UserDatasetTable).filter(UserDatasetTable.table_name == table_name).first() is not None


class PlatformDatasetRepository:
    """Repository for PlatformDataset model operations."""

    def _log_prefix(self, user_id: Optional[str] = None, company_id: Optional[str] = None) -> str:
        """Generate log prefix following team standards."""
        return f"[PlatformDatasetRepository] | [user_id={user_id or 'None'}] | [company_id={company_id or 'None'}]"

    def create(
        self,
        db: Session,
        table_name: str,
        collection_name: str,
        metadata: Dict[str, Any]
    ) -> PlatformDatasetTable:
        """
        Create or update a platform dataset.
        
        Args:
            db: Database session
            table_name: Name of the platform table
            collection_name: Collection name for the dataset
            metadata: DatasetMetadata dict from LLM agent
            
        Returns:
            Created or updated PlatformDatasetTable object
        """
        # Check if exists
        existing = self.get_by_table_name(db, table_name)
        
        if existing:
            # Update existing - SQLAlchemy handles JSON serialization
            existing.collection_name = collection_name
            existing.description = metadata.get("description", "")
            existing.data_category = metadata.get("data_category", "")
            existing.field_descriptions = metadata.get("field_descriptions", {})
            existing.key_fields = metadata.get("key_fields", [])
            existing.embedding_fields = metadata.get("embedding_fields", [])
            existing.primary_text_field = metadata.get("primary_text_field")
            existing.combined_text_fields = metadata.get("combined_text_fields", [])
            existing.estimated_use_cases = metadata.get("estimated_use_cases", [])
            existing.potential_joins = metadata.get("potential_joins", [])
            existing.data_quality_notes = metadata.get("data_quality_notes", "")
            existing.row_count = metadata.get("row_count", 0)
            existing.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(existing)
            logger.info(f"{self._log_prefix()} | Updated platform dataset: {table_name}")
            return existing
        else:
            # Create new - SQLAlchemy handles JSON serialization
            dataset = PlatformDatasetTable(
                table_name=table_name,
                collection_name=collection_name,
                description=metadata.get("description", ""),
                data_category=metadata.get("data_category", ""),
                field_descriptions=metadata.get("field_descriptions", {}),
                key_fields=metadata.get("key_fields", []),
                embedding_fields=metadata.get("embedding_fields", []),
                primary_text_field=metadata.get("primary_text_field"),
                combined_text_fields=metadata.get("combined_text_fields", []),
                estimated_use_cases=metadata.get("estimated_use_cases", []),
                potential_joins=metadata.get("potential_joins", []),
                data_quality_notes=metadata.get("data_quality_notes", ""),
                row_count=metadata.get("row_count", 0)
            )
            db.add(dataset)
            db.commit()
            db.refresh(dataset)
            logger.info(f"{self._log_prefix()} | Created platform dataset: {table_name}")
            return dataset

    def get_by_id(self, db: Session, dataset_id: int) -> Optional[PlatformDatasetTable]:
        """Get platform dataset by ID."""
        return db.query(PlatformDatasetTable).filter(PlatformDatasetTable.id == dataset_id).first()

    def get_by_table_name(self, db: Session, table_name: str) -> Optional[PlatformDatasetTable]:
        """Get platform dataset by table name."""
        return db.query(PlatformDatasetTable).filter(PlatformDatasetTable.table_name == table_name).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[PlatformDatasetTable]:
        """Get all platform datasets."""
        return (
            db.query(PlatformDatasetTable)
            .order_by(PlatformDatasetTable.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_metadata(self, db: Session, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a platform dataset as a dict.
        
        Args:
            db: Database session
            table_name: Name of the platform table
            
        Returns:
            Metadata dict or None if not found
        """
        dataset = self.get_by_table_name(db, table_name)
        if not dataset:
            return None
        
        # SQLAlchemy automatically deserializes JSON columns
        return {
            "collection_name": dataset.collection_name,
            "description": dataset.description,
            "data_category": dataset.data_category,
            "field_descriptions": dataset.field_descriptions or {},
            "key_fields": dataset.key_fields or [],
            "embedding_fields": dataset.embedding_fields or [],
            "primary_text_field": dataset.primary_text_field,
            "combined_text_fields": dataset.combined_text_fields or [],
            "estimated_use_cases": dataset.estimated_use_cases or [],
            "potential_joins": dataset.potential_joins or [],
            "data_quality_notes": dataset.data_quality_notes,
            "row_count": dataset.row_count
        }

    def delete(self, db: Session, dataset_id: int) -> bool:
        """Delete platform dataset by ID."""
        dataset = self.get_by_id(db, dataset_id)
        if dataset:
            table_name = dataset.table_name
            db.delete(dataset)
            db.commit()
            logger.info(f"{self._log_prefix()} | Deleted platform dataset: {table_name}")
            return True
        return False
