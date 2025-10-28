import sqlite3
import json
from typing import Any
from app import get_logger

logger = get_logger("workflows.utils.schema_manager")


# ============================================================================
# HARDCODED PLATFORM TABLES
# ============================================================================

PLATFORM_TABLES = {
    "reviews_feedback": {
        "description": "Customer reviews from various platforms",
        "columns": {
            "id": "INTEGER PRIMARY KEY",
            "company": "TEXT - Company/product name",
            "rating": "INTEGER - Rating score (1-5)",
            "category": "TEXT - category (review, feedback, etc.)",
            "source": "TEXT - Platform (app_store, reddit, trustpilot, etc.)",
            "review_text": "TEXT - Full review content",
            "author": "TEXT - Review author",
            "created_at": "TIMESTAMP - Review creation date"
        }
    }
}


# ============================================================================
# METADATA TABLE SCHEMA
# ============================================================================

def init_metadata_table(db_path: str):
    """
    Initialize the user_datasets metadata table.
    This tracks all user-uploaded datasets.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            table_name TEXT NOT NULL UNIQUE,
            original_filename TEXT,
            description TEXT,
            column_metadata TEXT, -- JSON string with column info
            row_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info(f"Metadata table initialized in {db_path}")


def init_platform_metadata_table(db_path: str):
    """
    Initialize the platform_datasets metadata table.
    This tracks platform-wide datasets that are common for all users (like reviews_feedback).
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS platform_datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT NOT NULL UNIQUE,
            collection_name TEXT NOT NULL,
            description TEXT,
            data_category TEXT,
            field_descriptions TEXT, -- JSON string
            key_fields TEXT, -- JSON array
            embedding_fields TEXT, -- JSON array
            primary_text_field TEXT,
            combined_text_fields TEXT, -- JSON array
            estimated_use_cases TEXT, -- JSON array
            potential_joins TEXT, -- JSON array
            data_quality_notes TEXT,
            row_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info(f"Platform metadata table initialized in {db_path}")


# ============================================================================
# SCHEMA FETCHING
# ============================================================================

def get_table_schema_from_db(db_path: str, table_name: str) -> dict[str, str]:
    """
    Fetch actual schema from SQLite database using PRAGMA.
    
    Returns:
        Dict mapping column names to their types
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = {}
    
    for row in cursor.fetchall():
        col_name = row[1]
        col_type = row[2]
        columns[col_name] = col_type
    
    conn.close()
    return columns


def get_user_datasets(db_path: str, user_id: str) -> list[dict[str, Any]]:
    """
    Fetch all datasets uploaded by a specific user.
    
    Returns:
        List of dataset metadata dicts
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT table_name, description, column_metadata, row_count, original_filename
        FROM user_datasets
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))
    
    datasets = []
    for row in cursor.fetchall():
        datasets.append({
            "table_name": row[0],
            "description": row[1],
            "column_metadata": row[2],
            "row_count": row[3],
            "original_filename": row[4],
        })
    
    conn.close()
    return datasets


# ============================================================================
# SCHEMA FORMATTING FOR LLM
# ============================================================================

def format_table_schema_for_llm(
    table_name: str, 
    columns: dict[str, str], 
    description: str = "",
    metadata: dict | None = None
) -> str:
    """
    Format a single table schema in human-readable format for LLM.
    
    Args:
        table_name: Name of the table
        columns: Dict of column_name -> type/description
        description: Table description
        metadata: Optional metadata dict with embedding fields, key fields, etc.
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


def get_all_available_schemas(db_path: str, user_id: str | None = None) -> str:
    """
    Get formatted schema string for all available tables.
    Includes both platform tables and user-uploaded datasets.
    
    Args:
        db_path: Path to SQLite database
        user_id: Optional user ID to filter user datasets
        
    Returns:
        Formatted string describing all available tables
    """
    schemas = []
    
    # 1. Add hardcoded platform tables
    schemas.append("=" * 60)
    schemas.append("PLATFORM TABLES (Always Available)")
    schemas.append("=" * 60)
    
    for table_name, table_info in PLATFORM_TABLES.items():
        schema = format_table_schema_for_llm(
            table_name,
            table_info["columns"],
            table_info["description"]
        )
        schemas.append(schema)
        schemas.append("")
    
    # 2. Add user-uploaded datasets if user_id provided
    if user_id:
        user_datasets = get_user_datasets(db_path, user_id)
        
        if user_datasets:
            schemas.append("=" * 60)
            schemas.append(f"USER DATASETS (User: {user_id})")
            schemas.append("=" * 60)
            
            for dataset in user_datasets:
                # Get actual schema from database
                actual_columns = get_table_schema_from_db(db_path, dataset["table_name"])
                
                # Parse metadata if available
                import json
                metadata = None
                if dataset.get("column_metadata"):
                    try:
                        metadata = json.loads(dataset["column_metadata"])
                    except:
                        pass
                
                schema = format_table_schema_for_llm(
                    dataset["table_name"],
                    actual_columns,
                    dataset.get("description", f"User-uploaded dataset ({dataset.get('row_count', 0)} rows)"),
                    metadata=metadata
                )
                schemas.append(schema)
                schemas.append("")
    
    return "\n".join(schemas)


# ============================================================================
# DATASET REGISTRATION
# ============================================================================

def register_user_dataset(
    db_path: str,
    user_id: str,
    table_name: str,
    original_filename: str,
    description: str = "",
    column_metadata: str = ""
) -> bool:
    """
    Register a new user dataset in the metadata table.
    Call this after ingesting a user's CSV/Excel/etc.
    
    Args:
        db_path: Path to SQLite database
        user_id: User ID who owns this dataset
        table_name: Name of the table created for this dataset
        original_filename: Original filename of uploaded file
        description: Optional description of the dataset
        column_metadata: Optional JSON string with column descriptions
        
    Returns:
        True if successful
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO user_datasets (user_id, table_name, original_filename, description, column_metadata, row_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, table_name, original_filename, description, column_metadata, row_count))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Registered dataset: {table_name} for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to register dataset: {e}")
        return False




def register_platform_dataset(
    db_path: str,
    table_name: str,
    metadata: dict[str, Any]
) -> bool:
    """
    Register a platform dataset with its metadata.
    
    Args:
        db_path: Path to SQLite database
        table_name: Name of the platform table
        metadata: DatasetMetadata dict from LLM agent
        
    Returns:
        True if successful
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get row count
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
        except:
            row_count = 0
        
        # Convert lists/dicts to JSON strings
        field_descriptions = json.dumps(metadata.get("field_descriptions", {}))
        key_fields = json.dumps(metadata.get("key_fields", []))
        embedding_fields = json.dumps(metadata.get("embedding_fields", []))
        combined_text_fields = json.dumps(metadata.get("combined_text_fields", []))
        estimated_use_cases = json.dumps(metadata.get("estimated_use_cases", []))
        potential_joins = json.dumps(metadata.get("potential_joins", []))
        
        # Insert or replace
        cursor.execute("""
            INSERT OR REPLACE INTO platform_datasets (
                table_name, collection_name, description, data_category,
                field_descriptions, key_fields, embedding_fields,
                primary_text_field, combined_text_fields,
                estimated_use_cases, potential_joins,
                data_quality_notes, row_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            table_name,
            metadata.get("collection_name", table_name),
            metadata.get("description", ""),
            metadata.get("data_category", ""),
            field_descriptions,
            key_fields,
            embedding_fields,
            metadata.get("primary_text_field"),
            combined_text_fields,
            estimated_use_cases,
            potential_joins,
            metadata.get("data_quality_notes", ""),
            row_count
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Registered platform dataset: {table_name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to register platform dataset: {e}")
        return False


def get_platform_dataset_metadata(db_path: str, table_name: str) -> dict[str, Any] | None:
    """
    Get metadata for a platform dataset.
    
    Args:
        db_path: Path to SQLite database
        table_name: Name of the platform table
        
    Returns:
        Metadata dict or None if not found
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT collection_name, description, data_category,
                   field_descriptions, key_fields, embedding_fields,
                   primary_text_field, combined_text_fields,
                   estimated_use_cases, potential_joins,
                   data_quality_notes, row_count
            FROM platform_datasets
            WHERE table_name = ?
        """, (table_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        import json
        return {
            "collection_name": row[0],
            "description": row[1],
            "data_category": row[2],
            "field_descriptions": json.loads(row[3]) if row[3] else {},
            "key_fields": json.loads(row[4]) if row[4] else [],
            "embedding_fields": json.loads(row[5]) if row[5] else [],
            "primary_text_field": row[6],
            "combined_text_fields": json.loads(row[7]) if row[7] else [],
            "estimated_use_cases": json.loads(row[8]) if row[8] else [],
            "potential_joins": json.loads(row[9]) if row[9] else [],
            "data_quality_notes": row[10],
            "row_count": row[11]
        }
        
    except Exception as e:
        logger.error(f"Failed to get platform dataset metadata: {e}")
        return None
