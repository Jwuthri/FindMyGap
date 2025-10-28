#!/usr/bin/env python3
"""
Script to view platform dataset metadata.

Run from project root: python backend/scripts/view_platform_metadata.py
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.workflows.utils.schema_manager import get_platform_dataset_metadata


def main():
    db_path = "backend/memory.db"
    table_name = "reviews_feedback"
    
    print("=" * 70)
    print(f"PLATFORM DATASET METADATA: {table_name}")
    print("=" * 70)
    print()
    
    metadata = get_platform_dataset_metadata(db_path, table_name)
    
    if not metadata:
        print(f"✗ No metadata found for table '{table_name}'")
        print()
        print("Run setup_platform_datasets.py first to generate metadata.")
        return 1
    
    print(f"Collection Name: {metadata['collection_name']}")
    print(f"Category: {metadata['data_category']}")
    print(f"Row Count: {metadata['row_count']}")
    print()
    
    print("Description:")
    print(f"  {metadata['description']}")
    print()
    
    print("Primary Text Field (for semantic search):")
    print(f"  {metadata.get('primary_text_field', 'N/A')}")
    print()
    
    print("Embedding Fields:")
    for field in metadata.get('embedding_fields', []):
        print(f"  - {field}")
    print()
    
    print("Key Fields:")
    for field in metadata.get('key_fields', []):
        print(f"  - {field}")
    print()
    
    print("Field Descriptions:")
    for field, desc in metadata.get('field_descriptions', {}).items():
        print(f"  - {field}: {desc}")
    print()
    
    print("Estimated Use Cases:")
    for i, use_case in enumerate(metadata.get('estimated_use_cases', []), 1):
        print(f"  {i}. {use_case}")
    print()
    
    if metadata.get('potential_joins'):
        print("Potential Joins:")
        for join in metadata['potential_joins']:
            print(f"  - {join}")
        print()
    
    if metadata.get('data_quality_notes'):
        print("Data Quality Notes:")
        print(f"  {metadata['data_quality_notes']}")
        print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
