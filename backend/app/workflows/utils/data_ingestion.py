import pandas as pd
import sqlite3
import json
from pathlib import Path
from typing import Any
from agno.models.openai import OpenAIChat

from app.workflows.agents.data_ingestion import (
    create_data_ingestion_agent,
    DataPreview,
    DatasetMetadata
)
from app.workflows.utils.schema_manager import register_user_dataset
from app.workflows.mock_data import MOCK_REVIEWS, get_all_companies
from app import get_logger

logger = get_logger("workflows.utils.data_ingestion")


def sanitize_table_name(name: str, user_id: str) -> str:
    """
    Create a safe, unique table name from user input.
    
    Prefixes with user_id to ensure uniqueness across users.
    Example: "customer_support_conversations" 
         -> "user_123_customer_support_conversations"
    
    Args:
        name: Original name (from filename or user input)
        user_id: User ID to prefix (ensures uniqueness)
        
    Returns:
        Safe, unique table name
    """
    # Remove file extension
    name = Path(name).stem
    
    # Convert to snake_case
    name = name.lower().replace(' ', '_').replace('-', '_')
    
    # Remove special characters
    name = ''.join(c for c in name if c.isalnum() or c == '_')
    
    # Prefix with user_id to ensure uniqueness
    # user_123_conversations vs user_456_conversations
    return f"user_{user_id}_{name}"


def analyze_dataframe(df: pd.DataFrame, filename: str) -> DataPreview:
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


async def ingest_data_file(
    file_path: str,
    user_id: str,
    db_path: str,
    model: OpenAIChat,
    table_name: str | None = None
) -> dict[str, Any]:
    """
    Complete data ingestion pipeline:
    1. Load and analyze the file
    2. Use LLM agent to generate metadata
    3. Create table and insert data
    4. Register in metadata system
    
    Args:
        file_path: Path to uploaded file (CSV, Excel, JSON, Parquet)
        user_id: User ID who owns this data
        db_path: Path to SQLite database
        model: LLM model for analysis
        table_name: Optional custom table name
        
    Returns:
        Dict with ingestion results and metadata
    """
    logger.info(f"Starting ingestion for {file_path}")
    
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
        
        logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        
    except Exception as e:
        logger.error(f"Failed to load file: {e}")
        return {"success": False, "error": f"File loading failed: {e}"}
    
    # 2. Analyze the data
    preview = analyze_dataframe(df, filename)
    
    # 3. Use LLM agent to generate metadata
    logger.info("Generating metadata with LLM agent...")
    ingestion_agent = create_data_ingestion_agent(model)
    
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

Generate metadata for this dataset."""

    try:
        response = await ingestion_agent.arun(prompt)
        # Extract structured output from response
        metadata: DatasetMetadata = response.content
        logger.info(f"Generated metadata: {metadata.collection_name}")
    except Exception as e:
        logger.error(f"Metadata generation failed: {e}")
        return {"success": False, "error": f"Metadata generation failed: {e}"}
    
    # 4. Create table name
    final_table_name = table_name or sanitize_table_name(metadata.collection_name, user_id)
    
    # 5. Insert data into SQLite
    try:
        conn = sqlite3.connect(db_path)
        df.to_sql(final_table_name, conn, if_exists="replace", index=False)
        conn.close()
        logger.info(f"Data inserted into table: {final_table_name}")
    except Exception as e:
        logger.error(f"Database insertion failed: {e}")
        return {"success": False, "error": f"Database insertion failed: {e}"}
    
    # 6. Register in metadata system
    column_metadata = json.dumps({
        "field_descriptions": metadata.field_descriptions,
        "key_fields": metadata.key_fields,
        "data_category": metadata.data_category,
        "estimated_use_cases": metadata.estimated_use_cases,
        "potential_joins": metadata.potential_joins,
        "embedding_fields": metadata.embedding_fields,
        "primary_text_field": metadata.primary_text_field,
        "combined_text_fields": metadata.combined_text_fields,
    })
    
    success = register_user_dataset(
        db_path=db_path,
        user_id=user_id,
        table_name=final_table_name,
        original_filename=filename,
        description=metadata.description,
        column_metadata=column_metadata
    )
    
    if not success:
        return {"success": False, "error": "Failed to register dataset"}
    
    # 7. Return results
    return {
        "success": True,
        "table_name": final_table_name,
        "row_count": len(df),
        "column_count": len(df.columns),
        "metadata": metadata.model_dump(),
        "message": f"Successfully ingested {filename} as {final_table_name}"
    }



def ingest_mock_reviews(db_path: str = "backend/memory.db") -> dict[str, Any]:
    """
    Ingest mock review data from mock_data.py into the reviews table.
    
    Creates a reviews table with columns: id, company, rating, text, source, date, author
    and populates it with all mock reviews from all companies.
    
    Args:
        db_path: Path to SQLite database (default: backend/memory.db)
        
    Returns:
        Dict with ingestion results including success status and row counts
    """
    logger.info(f"Starting mock review ingestion to {db_path}")
    
    try:
        # Collect all reviews from all companies
        all_reviews = []
        companies = get_all_companies()
        
        for company in companies:
            company_reviews = MOCK_REVIEWS[company]
            for review in company_reviews:
                # Add company field to each review
                review_with_company = review.copy()
                review_with_company['company'] = company
                all_reviews.append(review_with_company)
        
        logger.info(f"Collected {len(all_reviews)} reviews from {len(companies)} companies")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_reviews)
        
        # Reorder columns for better organization
        df = df[['id', 'company', "category", 'rating', 'text', 'source', 'date', 'author']]
        
        # Connect to database and insert
        conn = sqlite3.connect(db_path)
        
        # Drop existing table if it exists (to avoid duplicates)
        conn.execute("DROP TABLE IF EXISTS reviews_feedback")
        
        # Insert data
        df.to_sql('reviews_feedback', conn, if_exists='replace', index=False)
        
        # Verify insertion
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM reviews_feedback")
        row_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT company, COUNT(*) FROM reviews_feedback GROUP BY company")
        company_counts = dict(cursor.fetchall())
        
        conn.close()
        
        logger.info(f"Successfully ingested {row_count} reviews into 'reviews_feedback' table")
        
        return {
            "success": True,
            "table_name": "reviews_feedback",
            "total_rows": row_count,
            "companies": list(company_counts.keys()),
            "company_counts": company_counts,
            "message": f"Successfully ingested {row_count} reviews from {len(companies)} companies"
        }
        
    except Exception as e:
        logger.error(f"Mock review ingestion failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to ingest mock reviews: {e}"
        }



async def generate_platform_metadata(
    table_name: str,
    db_path: str,
    model: OpenAIChat
) -> dict[str, Any]:
    """
    Generate metadata for a platform dataset using LLM agent.
    
    This function:
    1. Reads the table structure and sample data
    2. Uses LLM agent to generate comprehensive metadata
    3. Returns the metadata dict (does not store it)
    
    Args:
        table_name: Name of the platform table
        db_path: Path to SQLite database
        model: LLM model for analysis
        
    Returns:
        Dict with metadata or error
    """
    logger.info(f"Generating metadata for platform table: {table_name}")
    
    try:
        # 1. Read table data
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 100", conn)
        conn.close()
        
        if df.empty:
            return {"success": False, "error": f"Table {table_name} is empty"}
        
        logger.info(f"Loaded {len(df)} sample rows from {table_name}")
        
        # 2. Analyze the data
        preview = analyze_dataframe(df, table_name)
        
        # 3. Use LLM agent to generate metadata
        logger.info("Generating metadata with LLM agent...")
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

Generate comprehensive metadata for this dataset. Pay special attention to:
1. Identifying the primary text field for semantic search (the main content field)
2. Listing all fields suitable for embeddings (rich text content)
3. Key fields that users will want to filter/group by
4. Potential use cases for this data"""

        response = await ingestion_agent.arun(prompt)
        metadata: DatasetMetadata = response.content
        
        logger.info(f"Generated metadata for {table_name}: {metadata.collection_name}")
        
        return {
            "success": True,
            "table_name": table_name,
            "metadata": metadata.model_dump()
        }
        
    except Exception as e:
        logger.error(f"Metadata generation failed for {table_name}: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to generate metadata: {e}"
        }
