"""
Schema utility functions.

Provides schema formatting and retrieval utilities for LLM context.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, date

from sqlalchemy.orm import Session
from sqlalchemy import inspect

from app import get_logger
from app.database.repositories.dataset import (
    PlatformDatasetRepository,
    UserDatasetRepository,
)
from app.database.repositories.user_review_feedback import UserReviewFeedbackRepository
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


def format_eda_stats(eda: Dict[str, Dict[str, Any]]) -> str:
    """Format EDA statistics into readable string."""
    if not eda:
        return ""
    
    lines = ["Data Statistics:"]
    for col_name, stats in eda.items():
        parts = [f"  {col_name}:"]
        
        for key, value in stats.items():
            if key == "sample_values":
                parts.append(f" {key}={value}")
            elif isinstance(value, (datetime, date)):
                parts.append(f" {key}={value.isoformat()}")
            else:
                parts.append(f" {key}={value}")
        
        lines.append("".join(parts))
    
    return "\n".join(lines)


def format_table_schema(
    table_name: str,
    columns: Dict[str, str],
    description: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    eda: Optional[Dict[str, Dict[str, Any]]] = None,
    relationships: Optional[List[str]] = None
) -> str:
    """
    Format a single table schema in human-readable format for LLM.
    
    Args:
        table_name: Name of the table
        columns: Dict of column_name -> type/description
        description: Table description
        metadata: Optional metadata dict with embedding fields, key fields, etc.
        relationships: Optional list of relationship descriptions for JOINs
        
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
    
    # Add EDA stats if available
    if eda:
        lines.append("")
        lines.append(format_eda_stats(eda))
    
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
            eda_stats = get_column_eda(user_reviews, actual_columns)

            schema = format_table_schema(
                dataset.table_name,
                actual_columns,
                dataset.description or f"Platform dataset ({dataset.row_count} rows)",
                metadata=metadata,
                eda=eda_stats
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
                eda_stats = get_column_eda(user_reviews, actual_columns)
                
                schema = format_table_schema(
                    dataset.table_name,
                    actual_columns,
                    dataset.description or f"User-uploaded dataset ({dataset.row_count} rows)",
                    metadata=metadata,
                    eda=eda_stats
                )
                schemas.append(schema)
                schemas.append("")
        
        if user_reviews:
            schemas.append("=" * 60)
            schemas.append(f"USER REVIEWS (User: {user_id})")
            schemas.append("=" * 60)
            
            # Get companies user has access to
            user_companies = user_review_feedback_repo.get_user_companies(db, user_id)
            company_list = ", ".join([f"{c['name']} (id={c['id']})" for c in user_companies])
            # Add companies table
            company_columns = db_utils.get_table_schema(db, "companies")
            company_schema = format_table_schema(
                "companies",
                company_columns,
                description=f"Companies table. User has access to {len(user_companies)} companies: {company_list}"
            )
            schemas.append(company_schema)
            schemas.append("")
            schemas.append("--------")
            schemas.append("")
            # Add reviews table with relationship info
            review_columns = db_utils.get_table_schema(db, "reviews_feedback")
            eda_stats = get_column_eda(user_reviews, review_columns)
            
            review_schema = format_table_schema(
                "reviews_feedback",
                review_columns,
                description=f"User's accessible reviews ({len(user_reviews)} reviews)",
                eda=eda_stats,
                relationships=[
                    "company_id -> companies.id (JOIN companies ON reviews_feedback.company_id = companies.id)",
                    "To filter by company name: JOIN companies and use WHERE companies.name = '...'"
                ]
            )
            schemas.append(review_schema)
            schemas.append("")
    
    logger.info("\n".join(schemas))
    breakpoint()
    return "\n".join(schemas)
