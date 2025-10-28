# Platform Datasets Setup

This directory contains scripts for setting up and managing platform-wide datasets with AI-generated metadata.

## Overview

Platform datasets are common datasets available to all users (unlike user-uploaded datasets which are user-specific). The system uses an LLM agent to automatically generate comprehensive metadata for these datasets, including:

- Field descriptions
- Primary text fields for semantic search
- Embedding-suitable fields
- Key fields for filtering/grouping
- Estimated use cases
- Data quality notes

## Database Tables

### 1. `reviews_feedback`
Contains customer reviews from various platforms (Spotify, Notion, Slack, Netflix).

**Schema:**
- `id` (INTEGER): Unique review identifier
- `company` (TEXT): Company name (spotify, notion, slack, netflix)
- `category` (TEXT): Review category (currently "review")
- `rating` (INTEGER): Rating score (1-5)
- `text` (TEXT): Full review content
- `source` (TEXT): Platform source (app_store, reddit, trustpilot, etc.)
- `date` (TEXT): Review date (YYYY-MM-DD)
- `author` (TEXT): Review author username

**Data:** 186 reviews across 4 companies

### 2. `platform_datasets`
Stores metadata for all platform datasets.

**Schema:**
- `id` (INTEGER): Primary key
- `table_name` (TEXT): Name of the platform table
- `collection_name` (TEXT): Human-readable collection name
- `description` (TEXT): Dataset description
- `data_category` (TEXT): Category (e.g., "customer_feedback")
- `field_descriptions` (TEXT): JSON string with field descriptions
- `key_fields` (TEXT): JSON array of important fields
- `embedding_fields` (TEXT): JSON array of fields suitable for embeddings
- `primary_text_field` (TEXT): Main text field for semantic search
- `combined_text_fields` (TEXT): JSON array of fields to combine for embeddings
- `estimated_use_cases` (TEXT): JSON array of use cases
- `potential_joins` (TEXT): JSON array of joinable fields
- `data_quality_notes` (TEXT): Notes on data quality
- `row_count` (INTEGER): Number of rows in the dataset
- `created_at` (TIMESTAMP): Creation timestamp
- `updated_at` (TIMESTAMP): Last update timestamp

## Scripts

### 1. `setup_platform_datasets.py`
**Complete setup script that:**
1. Creates the `platform_datasets` metadata table
2. Ingests mock review data into `reviews_feedback` table
3. Generates metadata using LLM agent (GPT-4o-mini)
4. Stores metadata in `platform_datasets` table

**Usage:**
```bash
# From project root
python backend/scripts/setup_platform_datasets.py
```

**Requirements:**
- OpenAI API key must be set in environment variables or `.env` file
- The script uses `SETTINGS.OPENAI_API_KEY` from `app.config`

**Output:**
```
======================================================================
PLATFORM DATASETS SETUP
======================================================================

Step 1: Initializing platform_datasets metadata table...
✓ Platform metadata table created/verified

Step 2: Ingesting mock review data...
✓ Successfully ingested 186 reviews from 4 companies
  Table: reviews_feedback
  Total rows: 186
  Companies: netflix, notion, slack, spotify

Step 3: Generating metadata with LLM agent...
✓ Metadata generated successfully!

Step 4: Storing metadata in database...
✓ Metadata stored successfully in platform_datasets table

======================================================================
SETUP COMPLETE!
======================================================================
```

### 2. `view_platform_metadata.py`
**View stored metadata for platform datasets.**

**Usage:**
```bash
python backend/scripts/view_platform_metadata.py
```

**Output:**
Displays comprehensive metadata including:
- Collection name and category
- Description
- Primary text field for semantic search
- Embedding fields
- Key fields
- Field descriptions
- Estimated use cases
- Potential joins
- Data quality notes

### 3. `ingest_mock_data.py`
**Legacy script - ingests only the review data without metadata generation.**

**Usage:**
```bash
python backend/scripts/ingest_mock_data.py
```

**Note:** Use `setup_platform_datasets.py` instead for complete setup with metadata.

## Programmatic Usage

### Generate Metadata for a Platform Dataset

```python
from app.workflows.utils.data_ingestion import generate_platform_metadata
from agno.models.openai import OpenAIChat
from app.config import get_settings

SETTINGS = get_settings()

# Initialize model
model = OpenAIChat(
    id="gpt-4o-mini",
    api_key=SETTINGS.OPENAI_API_KEY
)

# Generate metadata
result = await generate_platform_metadata(
    table_name="reviews_feedback",
    db_path="backend/memory.db",
    model=model
)

if result["success"]:
    metadata = result["metadata"]
    print(f"Primary text field: {metadata['primary_text_field']}")
    print(f"Embedding fields: {metadata['embedding_fields']}")
```

### Store Platform Dataset Metadata

```python
from app.workflows.utils.schema_manager import register_platform_dataset

success = register_platform_dataset(
    db_path="backend/memory.db",
    table_name="reviews_feedback",
    metadata=metadata_dict
)
```

### Retrieve Platform Dataset Metadata

```python
from app.workflows.utils.schema_manager import get_platform_dataset_metadata

metadata = get_platform_dataset_metadata(
    db_path="backend/memory.db",
    table_name="reviews_feedback"
)

if metadata:
    print(f"Description: {metadata['description']}")
    print(f"Primary text field: {metadata['primary_text_field']}")
    print(f"Key fields: {metadata['key_fields']}")
```

### Initialize Metadata Tables

```python
from app.workflows.utils.schema_manager import (
    init_metadata_table,
    init_platform_metadata_table
)

# Initialize user datasets metadata table
init_metadata_table("backend/memory.db")

# Initialize platform datasets metadata table
init_platform_metadata_table("backend/memory.db")
```

## Adding New Platform Datasets

To add a new platform dataset:

1. **Create the table and populate it with data**
   ```python
   import pandas as pd
   import sqlite3
   
   df = pd.DataFrame(your_data)
   conn = sqlite3.connect("backend/memory.db")
   df.to_sql("your_table_name", conn, if_exists="replace", index=False)
   conn.close()
   ```

2. **Generate metadata using the LLM agent**
   ```python
   result = await generate_platform_metadata(
       table_name="your_table_name",
       db_path="backend/memory.db",
       model=model
   )
   ```

3. **Store the metadata**
   ```python
   register_platform_dataset(
       db_path="backend/memory.db",
       table_name="your_table_name",
       metadata=result["metadata"]
   )
   ```

4. **Update `PLATFORM_TABLES` in `schema_manager.py`** (optional, for hardcoded schema info)

## Verification

After running the setup, verify everything is working:

```bash
# Check tables exist
sqlite3 backend/memory.db ".tables"
# Should show: platform_datasets  reviews_feedback

# Check review data
sqlite3 backend/memory.db "SELECT COUNT(*) FROM reviews_feedback"
# Should show: 186

# Check metadata exists
sqlite3 backend/memory.db "SELECT table_name, collection_name FROM platform_datasets"
# Should show: reviews_feedback|reviews_feedback

# View full metadata
python backend/scripts/view_platform_metadata.py
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Platform Datasets Flow                    │
└─────────────────────────────────────────────────────────────┘

1. Data Ingestion
   ├── mock_data.py (source data)
   └── ingest_mock_reviews() → reviews_feedback table

2. Metadata Generation
   ├── LLM Agent (GPT-4o-mini)
   ├── Analyzes table structure & sample data
   └── Generates DatasetMetadata

3. Metadata Storage
   ├── platform_datasets table
   └── Stores all metadata fields as JSON/TEXT

4. Metadata Retrieval
   ├── get_platform_dataset_metadata()
   └── Returns parsed metadata dict

5. Usage
   ├── Query planning (knows which fields to search)
   ├── Semantic search (uses primary_text_field)
   └── Embeddings (uses embedding_fields)
```

## Key Features

- **Automatic Metadata Generation**: LLM analyzes data and generates comprehensive metadata
- **Semantic Search Support**: Identifies best fields for embeddings and vector search
- **Field Descriptions**: Human-readable descriptions for every field
- **Use Case Suggestions**: AI-generated potential use cases
- **Data Quality Notes**: Automatic quality assessment
- **Extensible**: Easy to add new platform datasets

## Troubleshooting

**Error: "OPENAI_API_KEY not set"**
- Ensure your `.env` file contains `OPENAI_API_KEY=your_key_here`
- Or set it as an environment variable: `export OPENAI_API_KEY=your_key_here`

**Error: "Table already exists"**
- The scripts use `DROP TABLE IF EXISTS` and `INSERT OR REPLACE`
- Safe to run multiple times

**Error: "No metadata found"**
- Run `setup_platform_datasets.py` first to generate metadata
- Check that the table name matches exactly

## Future Enhancements

- Support for multiple platform datasets
- Automatic metadata refresh on data updates
- Metadata versioning
- Custom metadata fields
- Integration with vector databases for semantic search
