#!/usr/bin/env python3
"""
Script to ingest mock review data into the database.
Run from backend directory: python scripts/ingest_mock_data.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.workflows.utils.data_ingestion import ingest_mock_reviews


def main():
    print("Starting mock review data ingestion...")
    print("-" * 50)
    
    result = ingest_mock_reviews()
    
    if result["success"]:
        print(f"✓ {result['message']}")
        print(f"\nTable: {result['table_name']}")
        print(f"Total rows: {result['total_rows']}")
        print(f"\nBreakdown by company:")
        for company, count in result['company_counts'].items():
            print(f"  - {company}: {count} reviews")
    else:
        print(f"✗ Error: {result['message']}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
