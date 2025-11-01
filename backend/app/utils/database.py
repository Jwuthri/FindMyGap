"""
Database utility functions.

Provides common database operations used across the application.
"""

from pathlib import Path
from typing import Dict, Optional

import pandas as pd
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app import get_logger

logger = get_logger(__name__)


def sanitize_table_name(name: str, user_id: Optional[int] = None) -> str:
    """
    Create a safe, unique table name from user input.
    
    Prefixes with __user_{id}_ to ensure uniqueness across users.
    The double underscore prefix makes it easier to identify user tables.
    
    Args:
        name: Original name (from filename or user input)
        user_id: User ID to prefix
        
    Returns:
        Safe, unique table name with __user_{id}_ prefix
    """
    # Remove file extension
    name = Path(name).stem
    
    # Convert to snake_case
    name = name.lower().replace(' ', '_').replace('-', '_')
    
    # Remove special characters
    name = ''.join(c for c in name if c.isalnum() or c == '_')
    
    # Prefix with __user_{id}_ for easy identification
    return f"__user_{user_id}_{name}" if user_id else name


def check_table_exists(db: Session, table_name: str) -> bool:
    """
    Check if a table exists in the database.
    
    Args:
        db: Database session
        table_name: Name of the table to check
        
    Returns:
        True if table exists, False otherwise
    """
    inspector = inspect(db.bind)
    return table_name in inspector.get_table_names()


def get_table_schema(db: Session, table_name: str) -> Dict[str, str]:
    """
    Fetch actual schema from database using SQLAlchemy inspector.
    
    Args:
        db: Database session
        table_name: Name of the table
        
    Returns:
        Dict mapping column names to their types
    """
    inspector = inspect(db.bind)
    columns = {}
    
    try:
        for column in inspector.get_columns(table_name):
            columns[column['name']] = str(column['type'])
    except Exception as e:
        logger.error(f"Failed to get schema for {table_name}: {e}")
    
    return columns


def get_table_row_count(db: Session, table_name: str) -> int:
    """
    Get the number of rows in a table.
    
    Args:
        db: Database session
        table_name: Name of the table
        
    Returns:
        Number of rows
    """
    try:
        result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        return result.scalar()
    except Exception as e:
        logger.error(f"Failed to get row count for {table_name}: {e}")
        return 0


def insert_dataframe(
    db: Session,
    df: pd.DataFrame,
    table_name: str,
    if_exists: str = "replace"
) -> bool:
    """
    Insert a pandas DataFrame into a database table.
    
    Args:
        db: Database session
        df: Pandas DataFrame to insert
        table_name: Name of the target table
        if_exists: What to do if table exists ('fail', 'replace', 'append')
        
    Returns:
        True if successful, False otherwise
    """
    try:
        df.to_sql(table_name, db.bind, if_exists=if_exists, index=False)
        logger.info(f"Inserted {len(df)} rows into {table_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to insert data into {table_name}: {e}", exc_info=True)
        return False


def read_table_sample(
    db: Session,
    table_name: str,
    limit: int = 100
) -> Optional[pd.DataFrame]:
    """
    Read a sample of rows from a table.
    
    Args:
        db: Database session
        table_name: Name of the table
        limit: Maximum number of rows to read
        
    Returns:
        DataFrame with sample data or None if error
    """
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT {limit}", db.bind)
        return df
    except Exception as e:
        logger.error(f"Failed to read from {table_name}: {e}", exc_info=True)
        return None


def drop_table(db: Session, table_name: str) -> bool:
    """
    Drop a table from the database.
    
    Args:
        db: Database session
        table_name: Name of the table to drop
        
    Returns:
        True if successful, False otherwise
    """
    try:
        db.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
        db.commit()
        logger.info(f"Dropped table: {table_name}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to drop table {table_name}: {e}", exc_info=True)
        return False
