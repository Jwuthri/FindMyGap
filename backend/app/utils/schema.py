"""
Schema utility functions.

Provides schema formatting and retrieval utilities for LLM context.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, date

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import inspect

from app import get_logger
from app.database.models.table_eda import TableEDATable
from app.database.repositories.dataset import (
    PlatformDatasetRepository,
    UserDatasetRepository,
)
from app.database.repositories.user_review_feedback import UserReviewFeedbackRepository
from app.database.repositories.table_eda import TableEDARepository
from app.utils import database as db_utils

logger = get_logger(__name__)


def get_column_eda(rows: List[Any], schema: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
    """
    Perform fast EDA on SQLAlchemy query results.
    
    Args:
        rows: List of SQLAlchemy model instances
        schema: Dict mapping column names to their SQL types (from get_table_schema)
        
    Returns:
        Dict mapping column_name -> EDA stats dict
    """
    if not rows:
        return {}
    
    eda = {}
    
    for col_name, col_type in schema.items():
        values = [getattr(row, col_name, None) for row in rows if getattr(row, col_name, None) is not None]
        
        stats = {
            "non_null_count": len(values),
            "null_count": len(rows) - len(values),
            "col_type": col_type
        }
        
        if not values:
            eda[col_name] = stats
            continue
        
        col_type_upper = col_type.upper()
        
        # Numeric types (INTEGER, BIGINT, FLOAT, DECIMAL, NUMERIC, REAL, etc.)
        if any(t in col_type_upper for t in ['INT', 'FLOAT', 'DECIMAL', 'NUMERIC', 'REAL', 'DOUBLE']):
            # Skip if it's actually a boolean
            if col_type_upper != 'BOOLEAN' and not all(isinstance(v, bool) for v in values[:10]):
                try:
                    stats["min"] = min(values)
                    stats["max"] = max(values)
                    stats["distinct_count"] = len(set(values))
                except (TypeError, ValueError):
                    pass
        
        # String types (VARCHAR, TEXT, CHAR, etc.)
        elif any(t in col_type_upper for t in ['CHAR', 'TEXT', 'STRING', 'CLOB']):
            stats["distinct_count"] = len(set(values))
            if len(set(values)) < 50:
                stats["sample_values"] = list(set(values))[:10]
        
        # Boolean
        elif 'BOOL' in col_type_upper:
            stats["true_count"] = sum(1 for v in values if v)
            stats["false_count"] = sum(1 for v in values if not v)
        
        # Date/DateTime types
        elif any(t in col_type_upper for t in ['DATE', 'TIME', 'TIMESTAMP']):
            try:
                stats["min"] = min(values)
                stats["max"] = max(values)
            except (TypeError, ValueError):
                pass
        
        eda[col_name] = stats
    
    return eda


def format_sample_rows(sample_df, max_rows: int = 5) -> str:
    """
    Format sample rows from a DataFrame for display.
    
    Args:
        sample_df: DataFrame with sample data
        max_rows: Maximum number of rows to display
        
    Returns:
        Formatted string with sample rows
    """
    if sample_df is None or sample_df.empty:
        return "  No sample data available"
    
    lines = []
    df_subset = sample_df.head(max_rows)
    
    for idx, row in df_subset.iterrows():
        lines.append(f"  Row {idx + 1}:")
        for col in df_subset.columns:
            value = row[col]
            # Truncate long strings
            if isinstance(value, str) and len(value) > 100:
                value = value[:97] + "..."
            lines.append(f"    {col}: {value}")
    
    return "\n".join(lines)


def format_table_schema(
    table_name: str,
    columns: Dict[str, str],
    description: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    eda: Optional[TableEDATable] = None,
    relationships: Optional[List[str]] = None,
    sample_rows: Optional[Any] = None
) -> str:
    """
    Format a single table schema in human-readable format for LLM.
    
    Args:
        table_name: Name of the table
        columns: Dict of column_name -> type/description
        description: Table description
        metadata: Optional metadata dict with embedding fields, key fields, etc.
        eda: Optional TableEDATable object with EDA data
        relationships: Optional list of relationship descriptions for JOINs
        sample_rows: Optional DataFrame with sample rows from the table
        
    Returns:
        Formatted schema string
    """
    lines = [f"Table: {table_name}"]
    if description:
        lines.append(f"Description: {description}")
    lines.append("Columns:")
    
    for col_name, col_info in columns.items():
        lines.append(f"  - {col_name}: {col_info}")
    
    # Add relationships for JOIN queries
    if relationships:
        lines.append("Relationships:")
        for rel in relationships:
            lines.append(f"  - {rel}")
    
    # Add semantic search info if available
    if metadata:
        if metadata.get("primary_text_field"):
            lines.append(f"Primary Text Field (for semantic search): {metadata['primary_text_field']}")
        if metadata.get("embedding_fields"):
            lines.append(f"Embedding Fields: {', '.join(metadata['embedding_fields'])}")
        if metadata.get("key_fields"):
            lines.append(f"Key Fields: {', '.join(metadata['key_fields'])}")
    
    # Add EDA if available
    if eda:
        lines.append("")
        lines.append(f"Table Summary: {eda.summary}")
        lines.append("")
        lines.append(f"Field Metadata ({len(eda.insights)} fields):")
        for field in eda.insights:  # insights column stores field metadata
            lines.append(f"  {field['field_name']} ({field['data_type']})")
            lines.append(f"    {field['description']}")
            if field.get('unique_value_count'):
                lines.append(f"    Unique Values: {field['unique_value_count']}")
            if field.get('top_values'):
                top_vals = ', '.join(field['top_values'][:5])
                lines.append(f"    Top Values: {top_vals}")
    
    # Add sample rows
    if sample_rows is not None:
        lines.append("")
        lines.append("Sample Rows (5 examples):")
        lines.append(format_sample_rows(sample_rows, max_rows=5))
    
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
    user_review_feedback_repo = UserReviewFeedbackRepository()
    eda_repo = TableEDARepository()

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
            eda_record = eda_repo.get_by_table_name(db, dataset.table_name)
            
            # Get sample rows
            sample_rows = db_utils.read_table_sample(db, dataset.table_name, limit=5)

            schema = format_table_schema(
                dataset.table_name,
                actual_columns,
                dataset.description or f"Platform dataset ({dataset.row_count} rows)",
                metadata=metadata,
                eda=eda_record,
                sample_rows=sample_rows
            )
            schemas.append(schema)
            schemas.append("")
    
    # 2. Add user-uploaded datasets if user_id provided
    if user_id:
        user_datasets = user_dataset_repo.get_by_user(db, user_id)
        user_reviews = user_review_feedback_repo.get_user_reviews(db, user_id)
        
        if user_datasets:
            schemas.append("=" * 60)
            schemas.append(f"USER DATASETS (User: {user_id})")
            schemas.append("=" * 60)
            
            for dataset in user_datasets:
                # Get actual schema from database
                actual_columns = db_utils.get_table_schema(db, dataset.table_name)
                
                # SQLAlchemy automatically deserializes JSON columns
                metadata = dataset.column_metadata
                eda_record = eda_repo.get_by_table_name(db, dataset.table_name)
                
                # Get sample rows
                sample_rows = db_utils.read_table_sample(db, dataset.table_name, limit=5)

                schema = format_table_schema(
                    dataset.table_name,
                    actual_columns,
                    dataset.description or f"User-uploaded dataset ({dataset.row_count} rows)",
                    metadata=metadata,
                    eda=eda_record,
                    sample_rows=sample_rows
                )
                schemas.append(schema)
                schemas.append("")
        
        if user_reviews:
            schemas.append("=" * 60)
            schemas.append(f"USER REVIEWS (User: {user_id})")
            schemas.append("=" * 60)

            # Add per-user review feedback table
            from app.services.user_table_service import UserTableService

            user_table_name = UserTableService.get_user_table_name(user_id)

            # Check if user's table exists
            if UserTableService.table_exists(db, user_id):
                # Get companies user has access to
                user_companies = UserTableService.get_user_companies(db, user_id)
                company_list = ", ".join(user_companies[:10])
                if len(user_companies) > 10:
                    company_list += f" ... and {len(user_companies) - 10} more"

                # Get review count
                review_count = UserTableService.count_reviews(db, user_id)

                # Get table schema
                review_columns = db_utils.get_table_schema(db, user_table_name)

                # Get EDA from database if available
                eda_record = eda_repo.get_by_table_name(db, user_table_name)
                
                # Get sample rows
                sample_rows = db_utils.read_table_sample(db, user_table_name, limit=5)
                
                review_schema = format_table_schema(
                    user_table_name,
                    review_columns,
                    description=f"User's reviews ({review_count} reviews). Companies: {company_list}",
                    eda=eda_record,
                    sample_rows=sample_rows
                )
                schemas.append(review_schema)
                schemas.append("")
    
    data = "\n".join(schemas)
    logger.info(f"Available schemas:\n{data}")

    return data
