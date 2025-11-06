"""
LLM-based metadata generation for datasets.

This module uses LLM agents to analyze datasets and generate comprehensive metadata
including descriptions, field information, and semantic search configurations.
"""

import json
from typing import Any, Dict, List, Optional

import pandas as pd
from agno.models.openai import OpenAIChat

from app import get_logger
from app.old_workflows.agents.data_ingestion import (
    DataPreview,
    DatasetMetadata,
    create_data_ingestion_agent,
)

logger = get_logger(__name__)


class MetadataGenerator:
    """Service for generating dataset metadata using LLM."""

    def _log_prefix(self, user_id: Optional[str] = None, company_id: Optional[str] = None) -> str:
        """Generate log prefix following team standards."""
        return f"[MetadataGenerator] | [user_id={user_id or 'None'}] | [company_id={company_id or 'None'}]"

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

    async def generate_user_dataset_metadata(
        self,
        preview: DataPreview,
        model: OpenAIChat,
        existing_dataset_names: Optional[List[str]] = None
    ) -> DatasetMetadata:
        """
        Generate metadata for a user-uploaded dataset.
        
        Args:
            preview: DataPreview object with dataset analysis
            model: LLM model for metadata generation
            existing_dataset_names: List of existing dataset names to avoid duplicates
            
        Returns:
            DatasetMetadata object
        """
        logger.info(f"{self._log_prefix()} | Generating metadata for {preview.filename}")
        
        ingestion_agent = create_data_ingestion_agent(model)
        
        existing_info = ""
        if existing_dataset_names:
            existing_info = f"""

IMPORTANT: This user already has the following datasets:
{', '.join(existing_dataset_names)}

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

        response = await ingestion_agent.arun(prompt)
        metadata: DatasetMetadata = response.content
        
        logger.info(f"{self._log_prefix()} | Generated metadata: {metadata.collection_name}")
        return metadata

    async def generate_platform_dataset_metadata(
        self,
        table_name: str,
        preview: DataPreview,
        model: OpenAIChat
    ) -> DatasetMetadata:
        """
        Generate metadata for a platform dataset.
        
        Args:
            table_name: Name of the platform table
            preview: DataPreview object with dataset analysis
            model: LLM model for metadata generation
            
        Returns:
            DatasetMetadata object
        """
        logger.info(f"{self._log_prefix()} | Generating metadata for platform table: {table_name}")
        
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
        return metadata
