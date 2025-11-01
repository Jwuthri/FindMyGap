"""
Data ingestion workflow service.

Orchestrates the complete data ingestion pipeline:
1. File loading and analysis
2. LLM-based metadata generation
3. Database table creation and data insertion
4. Dataset registration
"""

from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from agno.models.openai import OpenAIChat
from sqlalchemy.orm import Session

from app import get_logger
from app.core.llm.metadata_generator import MetadataGenerator
from app.database.repositories.company import CompanyRepository
from app.database.repositories.dataset import (
    PlatformDatasetRepository,
    UserDatasetRepository,
)
from app.database.repositories.review import ReviewRepository
from app.utils import database as db_utils
from app.workflows.mock_data import MOCK_REVIEWS, get_all_companies

logger = get_logger(__name__)


class DataIngestionService:
    """Workflow service for data ingestion operations."""

    def __init__(self, db: Session):
        """
        Initialize data ingestion service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.user_dataset_repo = UserDatasetRepository()
        self.platform_dataset_repo = PlatformDatasetRepository()
        self.metadata_generator = MetadataGenerator()

    def _log_prefix(self, user_id: Optional[int] = None, company_id: Optional[int] = None) -> str:
        """Generate log prefix following team standards."""
        return f"[DataIngestionService] | [user_id={user_id or 'None'}] | [company_id={company_id or 'None'}]"

    def generate_unique_table_name(self, base_name: str, user_id: int) -> str:
        """
        Generate a unique table name by appending a number if needed.
        
        Args:
            base_name: Base table name
            user_id: User ID (for logging)
            
        Returns:
            Unique table name
        """
        if not self.user_dataset_repo.table_exists(self.db, base_name):
            return base_name
        
        # Table exists, find next available number
        counter = 2
        while True:
            new_name = f"{base_name}_{counter}"
            if not self.user_dataset_repo.table_exists(self.db, new_name):
                logger.info(f"{self._log_prefix(user_id)} | Table {base_name} exists, using {new_name}")
                return new_name
            counter += 1
            
            if counter > 100:
                raise ValueError(f"Too many tables with base name {base_name}")

    async def ingest_data_file(
        self,
        file_path: str,
        user_id: int,
        model: OpenAIChat,
        table_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete data ingestion pipeline.
        
        Args:
            file_path: Path to uploaded file
            user_id: User ID who owns this data
            model: LLM model for analysis
            table_name: Optional custom table name
            
        Returns:
            Dict with ingestion results and metadata
        """
        logger.info(f"{self._log_prefix(user_id)} | Starting ingestion for {file_path}")
        
        # 1. Load the file
        file_ext = Path(file_path).suffix.lower()
        filename = Path(file_path).name
        
        try:
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif file_ext == '.json':
                df = pd.read_json(file_path)
            elif file_ext == '.parquet':
                df = pd.read_parquet(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            logger.info(f"{self._log_prefix(user_id)} | Loaded {len(df)} rows, {len(df.columns)} columns")
            
        except Exception as e:
            logger.error(f"{self._log_prefix(user_id)} | Failed to load file: {e}", exc_info=True)
            return {"success": False, "error": f"File loading failed: {e}"}
        
        # 2. Analyze the data
        preview = self.metadata_generator.analyze_dataframe(df, filename)
        
        # 3. Get existing user datasets to avoid duplicates
        existing_datasets = self.user_dataset_repo.get_user_dataset_names(self.db, user_id)
        logger.info(f"{self._log_prefix(user_id)} | User has {len(existing_datasets)} existing datasets")
        
        # 4. Use LLM to generate metadata
        logger.info(f"{self._log_prefix(user_id)} | Generating metadata with LLM")
        try:
            metadata = await self.metadata_generator.generate_user_dataset_metadata(
                preview=preview,
                model=model,
                existing_dataset_names=existing_datasets
            )
            logger.info(f"{self._log_prefix(user_id)} | Generated metadata: {metadata.collection_name}")
        except Exception as e:
            logger.error(f"{self._log_prefix(user_id)} | Metadata generation failed: {e}", exc_info=True)
            return {"success": False, "error": f"Metadata generation failed: {e}"}
        
        # 5. Create table name
        if table_name:
            base_table_name = db_utils.sanitize_table_name(table_name, user_id)
        elif file_ext == '.csv':
            base_table_name = db_utils.sanitize_table_name(filename, user_id)
        else:
            base_table_name = db_utils.sanitize_table_name(metadata.collection_name, user_id)
        
        final_table_name = self.generate_unique_table_name(base_table_name, user_id)
        
        # 6. Insert data into database
        try:
            success = db_utils.insert_dataframe(self.db, df, final_table_name)
            if not success:
                return {"success": False, "error": "Database insertion failed"}
            logger.info(f"{self._log_prefix(user_id)} | Data inserted into table: {final_table_name}")
        except Exception as e:
            logger.error(f"{self._log_prefix(user_id)} | Database insertion failed: {e}", exc_info=True)
            return {"success": False, "error": f"Database insertion failed: {e}"}
        
        # 7. Register in metadata system
        column_metadata = {
            "field_descriptions": metadata.field_descriptions,
            "key_fields": metadata.key_fields,
            "data_category": metadata.data_category,
            "estimated_use_cases": metadata.estimated_use_cases,
            "potential_joins": metadata.potential_joins,
            "embedding_fields": metadata.embedding_fields,
            "primary_text_field": metadata.primary_text_field,
            "combined_text_fields": metadata.combined_text_fields,
        }
        
        try:
            self.user_dataset_repo.create(
                db=self.db,
                user_id=user_id,
                table_name=final_table_name,
                original_filename=filename,
                description=metadata.description,
                column_metadata=column_metadata,
                row_count=len(df)
            )
        except Exception as e:
            logger.error(f"{self._log_prefix(user_id)} | Failed to register dataset: {e}", exc_info=True)
            return {"success": False, "error": "Failed to register dataset"}
        
        # 8. Return results
        return {
            "success": True,
            "table_name": final_table_name,
            "row_count": len(df),
            "column_count": len(df.columns),
            "metadata": metadata.model_dump(),
            "message": f"Successfully ingested {filename} as {final_table_name}"
        }

    def ingest_mock_reviews(self) -> Dict[str, Any]:
        """
        Ingest mock review data from mock_data.py into the reviews table.
        
        Returns:
            Dict with ingestion results including success status and row counts
        """
        logger.info(f"{self._log_prefix()} | Starting mock review ingestion")
        
        try:
            company_repo = CompanyRepository()
            review_repo = ReviewRepository()
            
            companies = get_all_companies()
            total_reviews = 0
            company_counts = {}
            
            for company_name in companies:
                # Get or create company
                company = company_repo.get_or_create(self.db, name=company_name)
                company_counts[company_name] = 0
                
                # Get reviews for this company
                company_reviews = MOCK_REVIEWS[company_name]
                
                for review_data in company_reviews:
                    # Create review with company_id
                    review_repo.create(
                        db=self.db,
                        company_id=company.id,
                        text=review_data['text'],
                        rating=review_data.get('rating'),
                        category=review_data.get('category'),
                        source=review_data.get('source'),
                        date=review_data.get('date'),
                        author=review_data.get('author')
                    )
                    total_reviews += 1
                    company_counts[company_name] += 1
            
            logger.info(f"{self._log_prefix()} | Successfully ingested {total_reviews} reviews")
            
            return {
                "success": True,
                "table_name": "reviews_feedback",
                "total_rows": total_reviews,
                "companies": list(company_counts.keys()),
                "company_counts": company_counts,
                "message": f"Successfully ingested {total_reviews} reviews from {len(companies)} companies"
            }
            
        except Exception as e:
            logger.error(f"{self._log_prefix()} | Mock review ingestion failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to ingest mock reviews: {e}"
            }

    async def generate_platform_metadata(
        self,
        table_name: str,
        model: OpenAIChat
    ) -> Dict[str, Any]:
        """
        Generate metadata for a platform dataset using LLM.
        
        Args:
            table_name: Name of the platform table
            model: LLM model for analysis
            
        Returns:
            Dict with metadata or error
        """
        logger.info(f"{self._log_prefix()} | Generating metadata for platform table: {table_name}")
        
        try:
            # Read table sample
            df = db_utils.read_table_sample(self.db, table_name, limit=100)
            
            if df is None or df.empty:
                return {"success": False, "error": f"Table {table_name} is empty or doesn't exist"}
            
            logger.info(f"{self._log_prefix()} | Loaded {len(df)} sample rows from {table_name}")
            
            # Analyze the data
            preview = self.metadata_generator.analyze_dataframe(df, table_name)
            
            # Use LLM to generate metadata
            logger.info(f"{self._log_prefix()} | Generating metadata with LLM")
            metadata = await self.metadata_generator.generate_platform_dataset_metadata(
                table_name=table_name,
                preview=preview,
                model=model
            )
            
            logger.info(f"{self._log_prefix()} | Generated metadata for {table_name}: {metadata.collection_name}")
            
            return {
                "success": True,
                "table_name": table_name,
                "metadata": metadata.model_dump()
            }
            
        except Exception as e:
            logger.error(f"{self._log_prefix()} | Metadata generation failed for {table_name}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to generate metadata: {e}"
            }
