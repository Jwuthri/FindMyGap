#!/usr/bin/env python3
"""
Script to regenerate metadata for an existing platform dataset.

This is useful when:
- The data in the table has changed significantly
- You want to update the metadata with a different model
- The metadata generation logic has been improved

Run from project root: python backend/scripts/regenerate_metadata.py [table_name]
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.workflows.utils.data_ingestion import generate_platform_metadata
from app.workflows.utils.schema_manager import register_platform_dataset
from agno.models.openai import OpenAIChat
from app import get_logger
from app.config import get_settings

logger = get_logger("scripts.regenerate_metadata")
SETTINGS = get_settings()


async def regenerate_metadata(table_name: str, db_path: str = "backend/memory.db"):
    """
    Regenerate metadata for a platform dataset.
    """
    print("=" * 70)
    print(f"REGENERATING METADATA FOR: {table_name}")
    print("=" * 70)
    print()
    
    # Generate metadata using LLM agent
    print("Generating metadata with LLM agent...")
    print("This may take a moment...")
    print()
    
    try:
        # Initialize OpenAI model with API key from settings
        model = OpenAIChat(
            id="gpt-4o-mini",
            api_key=SETTINGS.OPENAI_API_KEY
        )
        
        # Generate metadata
        metadata_result = await generate_platform_metadata(
            table_name=table_name,
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
        print(f"  Description: {metadata['description'][:100]}...")
        print(f"  Category: {metadata['data_category']}")
        print(f"  Primary Text Field: {metadata.get('primary_text_field', 'N/A')}")
        print(f"  Embedding Fields: {', '.join(metadata.get('embedding_fields', []))}")
        print(f"  Key Fields: {', '.join(metadata.get('key_fields', []))}")
        print()
        
    except Exception as e:
        print(f"✗ Failed to generate metadata: {e}")
        logger.error(f"Metadata generation error: {e}", exc_info=True)
        return 1
    
    # Store metadata in database
    print("Storing updated metadata in database...")
    try:
        success = register_platform_dataset(
            db_path=db_path,
            table_name=table_name,
            metadata=metadata
        )
        
        if not success:
            print("✗ Failed to store metadata")
            return 1
        
        print("✓ Metadata updated successfully!")
        print()
        
    except Exception as e:
        print(f"✗ Failed to store metadata: {e}")
        return 1
    
    print("=" * 70)
    print("REGENERATION COMPLETE!")
    print("=" * 70)
    print()
    print(f"Metadata for '{table_name}' has been regenerated and stored.")
    print()
    
    return 0


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python regenerate_metadata.py <table_name>")
        print()
        print("Example:")
        print("  python backend/scripts/regenerate_metadata.py reviews_feedback")
        return 1
    
    table_name = sys.argv[1]
    
    try:
        return asyncio.run(regenerate_metadata(table_name))
    except KeyboardInterrupt:
        print("\n\nRegeneration interrupted by user")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        logger.error(f"Regeneration error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
