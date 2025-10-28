#!/usr/bin/env python3
"""
Script to setup platform datasets with metadata generation.

This script:
1. Creates the platform_datasets metadata table
2. Ingests mock review data into reviews_feedback table
3. Generates metadata using LLM agent
4. Stores metadata in platform_datasets table

Run from project root: python backend/scripts/setup_platform_datasets.py
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.workflows.utils.data_ingestion import ingest_mock_reviews, generate_platform_metadata
from app.workflows.utils.schema_manager import init_platform_metadata_table, register_platform_dataset
from agno.models.openai import OpenAIChat
from app import get_logger
from app.config import get_settings

logger = get_logger("scripts.setup_platform_datasets")
SETTINGS = get_settings()


async def setup_platform_datasets(db_path: str = "backend/memory.db"):
    """
    Complete setup for platform datasets.
    """
    print("=" * 70)
    print("PLATFORM DATASETS SETUP")
    print("=" * 70)
    print()
    
    # Step 1: Initialize platform_datasets metadata table
    print("Step 1: Initializing platform_datasets metadata table...")
    print("-" * 70)
    try:
        init_platform_metadata_table(db_path)
        print("✓ Platform metadata table created/verified")
    except Exception as e:
        print(f"✗ Failed to create metadata table: {e}")
        return 1
    print()
    
    # Step 2: Ingest mock review data
    print("Step 2: Ingesting mock review data...")
    print("-" * 70)
    result = ingest_mock_reviews(db_path)
    
    if not result["success"]:
        print(f"✗ Failed to ingest reviews: {result.get('error')}")
        return 1
    
    print(f"✓ {result['message']}")
    print(f"  Table: {result['table_name']}")
    print(f"  Total rows: {result['total_rows']}")
    print(f"  Companies: {', '.join(result['companies'])}")
    print()
    
    # Step 3: Generate metadata using LLM agent
    print("Step 3: Generating metadata with LLM agent...")
    print("-" * 70)
    print("This will analyze the reviews_feedback table and generate comprehensive metadata.")
    print("Please wait, this may take a moment...")
    print()
    
    try:
        # Initialize OpenAI model with API key from settings
        model = OpenAIChat(
            id="gpt-5-mini",
            api_key=SETTINGS.OPENAI_API_KEY
        )
        
        # Generate metadata
        metadata_result = await generate_platform_metadata(
            table_name="reviews_feedback",
            db_path=db_path,
            model=model
        )
        
        if not metadata_result["success"]:
            print(f"✗ Failed to generate metadata: {metadata_result.get('error')}")
            return 1
        
        metadata = metadata_result["metadata"]
        print("✓ Metadata generated successfully!")
        print()
        print("Generated Metadata:")
        print(f"  Collection Name: {metadata['collection_name']}")
        print(f"  Description: {metadata['description']}")
        print(f"  Category: {metadata['data_category']}")
        print(f"  Primary Text Field: {metadata.get('primary_text_field', 'N/A')}")
        print(f"  Embedding Fields: {', '.join(metadata.get('embedding_fields', []))}")
        print(f"  Key Fields: {', '.join(metadata.get('key_fields', []))}")
        print()
        
    except Exception as e:
        print(f"✗ Failed to generate metadata: {e}")
        logger.error(f"Metadata generation error: {e}", exc_info=True)
        return 1
    
    # Step 4: Store metadata in database
    print("Step 4: Storing metadata in database...")
    print("-" * 70)
    try:
        success = register_platform_dataset(
            db_path=db_path,
            table_name="reviews_feedback",
            metadata=metadata
        )
        
        if not success:
            print("✗ Failed to store metadata")
            return 1
        
        print("✓ Metadata stored successfully in platform_datasets table")
        print()
        
    except Exception as e:
        print(f"✗ Failed to store metadata: {e}")
        return 1
    
    # Summary
    print("=" * 70)
    print("SETUP COMPLETE!")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  ✓ Platform metadata table created")
    print(f"  ✓ {result['total_rows']} reviews ingested into reviews_feedback")
    print(f"  ✓ Metadata generated and stored")
    print()
    print("You can now query the reviews_feedback table with full metadata support!")
    print()
    
    return 0


def main():
    """Main entry point."""
    try:
        return asyncio.run(setup_platform_datasets())
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        logger.error(f"Setup error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
