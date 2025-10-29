"""
Data ingestion utilities using SQLAlchemy and repository pattern.

This module handles:
1. File upload and analysis (CSV, Excel, JSON, Parquet)
2. LLM-based metadata generation
3. Database table creation and data insertion
4. Dataset registration via repositories
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from agno.models.openai import OpenAIChat
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import get_logger
from app.database.repositories.dataset import (
    PlatformDatasetRepository,
    UserDatasetRepository,
)
from app.workflows.agents.data_ingestion import (
    DataPreview,
    DatasetMetadata,
    create_data_ingestion_agent,
)
from app.workflows.mock_data import MOCK_REVIEWS, get_all_companies

logger = get_logger(__name__)


class DataIngestionService:
    """Service for data ingestion operations."""

    def __init__(self, db: Session):
        """
        Initialize data ingestion service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.user_dataset_repo = UserDatasetRepository()
        self.platform_dataset_repo = PlatformDatasetRepository()

    def _log_prefix(self, user_id: Optional[str] = None, company_id: Optional[str] = None) -> str:
        """Generate log prefix following team standards."""
        return f"[DataIngestionService] | [user_id={user_id or 'None'}] | [company_id={company_id or 'None'}]"

    def sanitize_table_name(self, name: str, user_id: str) -> str:
        """
        Create a safe, unique table name from user input.
        
        Prefixes with user_id to ensure uniqueness across users.
        
        Args:
            name: Original name (from filename or user input)
            user_id: User ID to prefix
            
        Returns:
            Safe, unique table name
        """
        # Remove file extension
        name = Path(name).stem
        
        # Convert to snake_case
        name = name.lower().replace(' ', '_').replace('-', '_')
        
        # Remove special characters
        name = ''.join(c for c in name if c.isalnum() or c == '_')
        
        # Prefix with user_id
        return f"user_{user_id}_{name}"

    def analyze_dataframe(self, df: pd.DataFrame, filename: str) -> DataPreview:
        """
        Analyze a DataFrame and create a preview for the ingestion agent.
        
        Args:
            df: Pandas DataFrame
            filename: Original filename
            
        Returns:
            DataPreview object with analysis
        """
        # Infer column types
        columns = {}
        for col in df.columns:
            dtype = str(df[col].dtype)
            if 'int' in dtype:
                columns[col] = 'INTEGER'
            elif 'float' in dtype:
                columns[col] = 'REAL'
            elif 'datetime' in dtype or 'date' in dtype:
                columns[col] = 'TIMESTAMP'
            else:
                columns[col] = 'TEXT'
        
        # Get sample rows (first 10)
        sample_rows = df.head(10).to_dict('records')
        
        # Get null counts
        null_counts = df.isnull().sum().to_dict()
        
        # Get unique counts for categorical columns
        unique_counts = {}
        for col in df.columns:
            if df[col].dtype == 'object' or df[col].nunique() < 50:
                unique_counts[col] = int(df[col].nunique())
        
        return DataPreview(
            filename=filename,
            row_count=len(df),
            columns=columns,
            sample_rows=sample_rows,
            null_counts=null_counts,
            unique_counts=unique_counts
        )

    def generate_unique_table_name(self, base_name: str, user_id: str) -> str:
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
        user_id: str,
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
        preview = self.analyze_dataframe(df, filename)
        
        # 3. Get existing user datasets to avoid duplicates
        existing_datasets = self.user_dataset_repo.get_user_dataset_names(self.db, user_id)
        logger.info(f"{self._log_prefix(user_id)} | User has {len(existing_datasets)} existing datasets")
        
        # 4. Use LLM agent to generate metadata
        logger.info(f"{self._log_prefix(user_id)} | Generating metadata with LLM agent")
        ingestion_agent = create_data_ingestion_agent(model)
        
        existing_info = ""
        if existing_datasets:
            existing_info = f"""

IMPORTANT: This user already has the following datasets:
{', '.join(existing_datasets)}

Please ensure the collection_name you suggest is different from these existing datasets."""
        
        prompt = f"""Analyze this uploaded dataset and generate comprehensive metadata.

Filename: {preview.filename}
Rows: {preview.row_count}

Columns and Types:
{json.dumps(preview.columns, indent=2)}

Sample Data (first few rows):
{json.dumps(preview.sample_rows[:5], indent=2)}

Statistics:
- Null counts: {json.dumps(preview.null_counts, indent=2) if preview.null_counts else 'N/A'}
- Unique values: {json.dumps(preview.unique_counts, indent=2) if preview.unique_counts else 'N/A'}
{existing_info}

Generate metadata for this dataset."""

        try:
            response = await ingestion_agent.arun(prompt)
            metadata: DatasetMetadata = response.content
            logger.info(f"{self._log_prefix(user_id)} | Generated metadata: {metadata.collection_name}")
        except Exception as e:
            logger.error(f"{self._log_prefix(user_id)} | Metadata generation failed: {e}", exc_info=True)
            return {"success": False, "error": f"Metadata generation failed: {e}"}
        
        # 5. Create table name
        if table_name:
            base_table_name = self.sanitize_table_name(table_name, user_id)
        elif file_ext == '.csv':
            base_table_name = self.sanitize_table_name(filename, user_id)
        else:
            base_table_name = self.sanitize_table_name(metadata.collection_name, user_id)
        
        final_table_name = self.generate_unique_table_name(base_table_name, user_id)
        
        # 6. Insert data into database using pandas to_sql
        try:
            # Use SQLAlchemy connection from session
            df.to_sql(final_table_name, self.db.bind, if_exists="replace", index=False)
            logger.info(f"{self._log_prefix(user_id)} | Data inserted into table: {final_table_name}")
        except Exception as e:
            logger.error(f"{self._log_prefix(user_id)} | Database insertion failed: {e}", exc_info=True)
            return {"success": False, "error": f"Database insertion failed: {e}"}
        
        # 7. Register in metadata system using repository
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
            # Collect all reviews from all companies
            all_reviews = []
            companies = get_all_companies()
            
            for company in companies:
                company_reviews = MOCK_REVIEWS[company]
                for review in company_reviews:
                    review_with_company = review.copy()
                    review_with_company['company'] = company
                    all_reviews.append(review_with_company)
            
            logger.info(f"{self._log_prefix()} | Collected {len(all_reviews)} reviews from {len(companies)} companies")
            
            # Convert to DataFrame
            df = pd.DataFrame(all_reviews)
            df = df[['id', 'company', "category", 'rating', 'text', 'source', 'date', 'author']]
            
            # Insert using SQLAlchemy
            df.to_sql('reviews_feedback', self.db.bind, if_exists='replace', index=False)
            
            # Verify insertion
            result = self.db.execute(text("SELECT COUNT(*) FROM reviews_feedback"))
            row_count = result.scalar()
            
            result = self.db.execute(text("SELECT company, COUNT(*) FROM reviews_feedback GROUP BY company"))
            company_counts = dict(result.fetchall())
            
            logger.info(f"{self._log_prefix()} | Successfully ingested {row_count} reviews into 'reviews_feedback' table")
            
            return {
                "success": True,
                "table_name": "reviews_feedback",
                "total_rows": row_count,
                "companies": list(company_counts.keys()),
                "company_counts": company_counts,
                "message": f"Successfully ingested {row_count} reviews from {len(companies)} companies"
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
        Generate metadata for a platform dataset using LLM agent.
        
        Args:
            table_name: Name of the platform table
            model: LLM model for analysis
            
        Returns:
            Dict with metadata or error
        """
        logger.info(f"{self._log_prefix()} | Generating metadata for platform table: {table_name}")
        
        try:
            # Read table data using SQLAlchemy
            df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 100", self.db.bind)
            
            if df.empty:
                return {"success": False, "error": f"Table {table_name} is empty"}
            
            logger.info(f"{self._log_prefix()} | Loaded {len(df)} sample rows from {table_name}")
            
            # Analyze the data
            preview = self.analyze_dataframe(df, table_name)
            
            # Use LLM agent to generate metadata
            logger.info(f"{self._log_prefix()} | Generating metadata with LLM agent")
            ingestion_agent = create_data_ingestion_agent(model)
            
            prompt = f"""Analyze this platform dataset and generate comprehensive metadata.

This is a PLATFORM dataset that will be available to all users for analysis.

Table Name: {table_name}
Rows: {preview.row_count} (sample from larger dataset)

Columns and Types:
{json.dumps(preview.columns, indent=2)}

Sample Data (first few rows):
{json.dumps(preview.sample_rows[:5], indent=2)}

Statistics:
- Null counts: {json.dumps(preview.null_counts, indent=2) if preview.null_counts else 'N/A'}
- Unique values: {json.dumps(preview.unique_counts, indent=2) if preview.unique_counts else 'N/A'}

Generate comprehensive metadata for this dataset."""

            response = await ingestion_agent.arun(prompt)
            metadata: DatasetMetadata = response.content
            
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
