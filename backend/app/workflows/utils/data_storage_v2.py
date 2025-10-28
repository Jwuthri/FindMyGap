"""
Alternative data storage approach: Single table with user partitioning.

This is more scalable than creating separate tables per dataset.
Good for medium-scale deployments.
"""

import sqlite3
import json
from typing import Any
from app import get_logger

logger = get_logger("workflows.utils.data_storage_v2")


# ============================================================================
# UNIFIED DATA TABLE APPROACH
# ============================================================================

def init_unified_storage(db_path: str):
    """
    Initialize unified storage tables.
    All user data goes into a single table with user_id + dataset_id partitioning.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Metadata table (same as before)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datasets_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            dataset_id TEXT NOT NULL UNIQUE,
            dataset_name TEXT NOT NULL,
            description TEXT,
            schema_json TEXT,
            row_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user_datasets (user_id, dataset_id)
        )
    """)
    
    # Unified data table - all user data goes here
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            dataset_id TEXT NOT NULL,
            row_data JSON NOT NULL,  -- Flexible schema
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user_dataset (user_id, dataset_id),
            INDEX idx_dataset (dataset_id)
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info(f"Unified storage initialized in {db_path}")


def insert_user_data_batch(
    db_path: str,
    user_id: str,
    dataset_id: str,
    rows: list[dict[str, Any]]
):
    """
    Insert a batch of rows into unified storage.
    
    Args:
        db_path: Database path
        user_id: User who owns the data
        dataset_id: Unique dataset identifier
        rows: List of row dictionaries
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Insert all rows
    for row in rows:
        cursor.execute("""
            INSERT INTO user_data (user_id, dataset_id, row_data)
            VALUES (?, ?, ?)
        """, (user_id, dataset_id, json.dumps(row)))
    
    conn.commit()
    conn.close()
    
    logger.info(f"Inserted {len(rows)} rows for {user_id}/{dataset_id}")


def query_user_data(
    db_path: str,
    user_id: str,
    dataset_id: str,
    filters: dict[str, Any] | None = None,
    limit: int = 100
) -> list[dict[str, Any]]:
    """
    Query user data with optional JSON filters.
    
    Args:
        db_path: Database path
        user_id: User ID
        dataset_id: Dataset ID
        filters: Optional filters on JSON fields
        limit: Max rows to return
        
    Returns:
        List of row dictionaries
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = """
        SELECT row_data 
        FROM user_data 
        WHERE user_id = ? AND dataset_id = ?
    """
    params = [user_id, dataset_id]
    
    # Add JSON filters if provided
    if filters:
        for key, value in filters.items():
            query += f" AND json_extract(row_data, '$.{key}') = ?"
            params.append(value)
    
    query += f" LIMIT {limit}"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    # Parse JSON
    return [json.loads(row[0]) for row in rows]


# ============================================================================
# COMPARISON: Which approach to use?
# ============================================================================

"""
APPROACH 1: Separate tables (current)
- user_123_conversations
- user_123_feedback
- user_456_conversations

Pros: Natural SQL, simple queries
Cons: Many tables, harder to manage at scale

APPROACH 2: Unified table (this file)
- Single user_data table with user_id + dataset_id
- Flexible JSON schema

Pros: Scales better, fewer tables
Cons: JSON querying slower, less type safety

RECOMMENDATION:
- Use Approach 1 (current) for < 100 users
- Use Approach 2 (this) for > 100 users
- Use PostgreSQL with proper JSONB for > 1000 users
"""

