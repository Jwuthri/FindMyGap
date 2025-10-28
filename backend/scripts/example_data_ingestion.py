"""
Example script showing how to use the data ingestion system.

This demonstrates the complete pipeline:
1. User uploads a file (CSV, Excel, JSON, etc.)
2. System analyzes it with an LLM agent
3. Generates metadata automatically
4. Ingests into database
5. Makes it available for queries
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agno.models.openai import OpenAIChat
from app.config import SETTINGS
from app.workflows.utils.data_ingestion import ingest_data_file
from app.workflows.utils.schema_manager import get_all_available_schemas, init_metadata_table
from app import get_logger

logger = get_logger("scripts.example_data_ingestion")


async def main():
    """Example data ingestion flow"""
    
    # Setup
    db_path = "/Users/julienwuthrich/GitHub/findmygap/tmp/product_gap_workflow.db"
    user_id = "user_123"
    model = OpenAIChat(id="gpt-5-nano", api_key=SETTINGS.OPENAI_API_KEY)
    
    # Initialize metadata table (first time only)
    init_metadata_table(db_path)
    
    # Example 1: Ingest a customer communications dataset
    print("\n" + "="*60)
    print("EXAMPLE: Ingesting customer service conversations")
    print("="*60)
    
    # In real usage, this would be an uploaded file
    # For demo, you could create a sample CSV:
    """
    import pandas as pd
    
    sample_data = pd.DataFrame({
        'conversation_id': ['conv_001', 'conv_001', 'conv_002'],
        'message_index': [1, 2, 1],
        'author': ['customer', 'agent', 'customer'],
        'content': [
            'My product is not working',
            'Sorry to hear that. Can you describe the issue?',
            'I need a refund'
        ],
        'timestamp': ['2024-01-15 10:30', '2024-01-15 10:35', '2024-01-15 11:00'],
        'subject': ['Product Issue', 'Product Issue', 'Refund Request']
    })
    
    sample_data.to_csv('tmp/sample_conversations.csv', index=False)
    """
    
    # Simulate file upload
    file_path = "tmp/sample_conversations.csv"
    
    # Check if file exists
    if not Path(file_path).exists():
        print(f"⚠️  Sample file not found: {file_path}")
        print("Creating sample file...")
        
        import pandas as pd
        sample_data = pd.DataFrame({
            'conversation_id': ['conv_001', 'conv_001', 'conv_002', 'conv_002', 'conv_003'],
            'message_index': [1, 2, 1, 2, 1],
            'author': ['customer', 'agent', 'customer', 'agent', 'customer'],
            'content': [
                'My product is not working properly',
                'Sorry to hear that. Can you describe the issue?',
                'I need a refund for my order',
                'I can help you with that. What is your order number?',
                'How do I track my shipment?'
            ],
            'timestamp': [
                '2024-01-15 10:30:00',
                '2024-01-15 10:35:00',
                '2024-01-15 11:00:00',
                '2024-01-15 11:05:00',
                '2024-01-16 09:15:00'
            ],
            'subject': ['Product Issue', 'Product Issue', 'Refund Request', 'Refund Request', 'Shipping Question']
        })
        
        Path("tmp").mkdir(exist_ok=True)
        sample_data.to_csv(file_path, index=False)
        print(f"✓ Created sample file: {file_path}\n")
    
    # Ingest the file
    result = await ingest_data_file(
        file_path=file_path,
        user_id=user_id,
        db_path=db_path,
        model=model
    )
    
    if result["success"]:
        print(f"✅ {result['message']}")
        print(f"\nGenerated Metadata:")
        print(f"  Table: {result['table_name']}")
        print(f"  Rows: {result['row_count']}")
        print(f"  Columns: {result['column_count']}")
        print(f"\n  Description:")
        print(f"    {result['metadata']['description']}")
        print(f"\n  Category: {result['metadata']['data_category']}")
        print(f"\n  Key Fields: {', '.join(result['metadata']['key_fields'])}")
        
        # Semantic search info
        if result['metadata'].get('primary_text_field'):
            print(f"\n  🔍 Semantic Search Configuration:")
            print(f"    Primary Text Field: {result['metadata']['primary_text_field']}")
            if result['metadata'].get('embedding_fields'):
                print(f"    All Embedding Fields: {', '.join(result['metadata']['embedding_fields'])}")
            if result['metadata'].get('combined_text_fields'):
                print(f"    Combined Fields: {' + '.join(result['metadata']['combined_text_fields'])}")
        
        print(f"\n  Suggested Use Cases:")
        for use_case in result['metadata']['estimated_use_cases']:
            print(f"    - {use_case}")
    else:
        print(f"❌ Ingestion failed: {result['error']}")
    
    # Show all available schemas
    print("\n" + "="*60)
    print("ALL AVAILABLE SCHEMAS")
    print("="*60)
    schemas = get_all_available_schemas(db_path, user_id)
    print(schemas)


if __name__ == "__main__":
    asyncio.run(main())

