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
    db_path = "/Users/julienwuthrich/GitHub/findmygap/backend/memory.db"
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
            'feature_id': ['FEAT-001', 'FEAT-002', 'FEAT-003', 'FEAT-004', 'FEAT-005', 'FEAT-006', 'FEAT-007', 'FEAT-008', 'FEAT-009', 'FEAT-010',
                          'FEAT-011', 'FEAT-012', 'FEAT-013', 'FEAT-014', 'FEAT-015', 'FEAT-016', 'FEAT-017', 'FEAT-018', 'FEAT-019', 'FEAT-020',
                          'FEAT-021', 'FEAT-022', 'FEAT-023', 'FEAT-024', 'FEAT-025', 'FEAT-026', 'FEAT-027', 'FEAT-028', 'FEAT-029', 'FEAT-030',
                          'FEAT-031', 'FEAT-032', 'FEAT-033', 'FEAT-034', 'FEAT-035', 'FEAT-036', 'FEAT-037', 'FEAT-038', 'FEAT-039', 'FEAT-040'],
            'feature_name': [
                'AI-Powered Auto-Complete', 'Advanced Table Filtering', 'Custom API Rate Limits', 'Dark Mode Improvements', 'Database Relations V2',
                'Email Integration', 'Formula Builder UI', 'Google Calendar Sync', 'Inline Comments', 'Kanban Board Templates',
                'Live Collaboration Cursors', 'Mobile Offline Mode', 'Notion Charts', 'Page Analytics', 'PDF Export Enhancement',
                'Real-time Notifications', 'Slack Integration V2', 'Table Grouping', 'Timeline View', 'Version History Search',
                'Web Clipper Extension', 'Workspace Permissions', 'Zapier Integration', 'Advanced Search Filters', 'Block Templates',
                'Calendar View Filters', 'Database Rollups', 'Export to Markdown', 'Formula Autocomplete', 'Gallery View Customization',
                'Import from Confluence', 'Keyboard Shortcuts Panel', 'Link Preview Cards', 'Multi-Select Properties', 'Nested Databases',
                'Page Cover Videos', 'Quick Capture Widget', 'Recurring Tasks', 'Sidebar Customization', 'Table of Contents Auto-Update'
            ],
            'category': [
                'AI/ML', 'Database', 'API', 'UI/UX', 'Database',
                'Integration', 'Database', 'Integration', 'Collaboration', 'Templates',
                'Collaboration', 'Mobile', 'Visualization', 'Analytics', 'Export',
                'Notifications', 'Integration', 'Database', 'Visualization', 'Core',
                'Integration', 'Security', 'Integration', 'Search', 'Templates',
                'Visualization', 'Database', 'Export', 'Database', 'Visualization',
                'Import', 'UI/UX', 'Core', 'Database', 'Database',
                'UI/UX', 'Mobile', 'Tasks', 'UI/UX', 'Core'
            ],
            'status': [
                'In Development', 'Shipped', 'Planning', 'Shipped', 'In Development',
                'Planning', 'In Development', 'Shipped', 'Shipped', 'Shipped',
                'Shipped', 'In Development', 'Beta', 'Planning', 'Shipped',
                'Shipped', 'In Development', 'Beta', 'Shipped', 'Shipped',
                'Shipped', 'In Development', 'Shipped', 'Planning', 'Shipped',
                'Beta', 'Shipped', 'Shipped', 'In Development', 'Beta',
                'Planning', 'Shipped', 'Shipped', 'Shipped', 'Planning',
                'Beta', 'Planning', 'In Development', 'Shipped', 'In Development'
            ],
            'priority': [
                'High', 'Medium', 'Low', 'Medium', 'High',
                'Medium', 'High', 'Medium', 'High', 'Low',
                'High', 'High', 'Medium', 'Low', 'Medium',
                'High', 'Medium', 'High', 'Medium', 'Medium',
                'Medium', 'High', 'Low', 'Medium', 'Low',
                'Medium', 'Medium', 'Low', 'High', 'Low',
                'Medium', 'Low', 'Medium', 'Medium', 'High',
                'Low', 'Medium', 'High', 'Medium', 'Medium'
            ],
            'team': [
                'AI Team', 'Database Team', 'Platform Team', 'Design Team', 'Database Team',
                'Integrations Team', 'Database Team', 'Integrations Team', 'Collaboration Team', 'Templates Team',
                'Collaboration Team', 'Mobile Team', 'Visualization Team', 'Analytics Team', 'Export Team',
                'Platform Team', 'Integrations Team', 'Database Team', 'Visualization Team', 'Core Team',
                'Integrations Team', 'Security Team', 'Integrations Team', 'Search Team', 'Templates Team',
                'Visualization Team', 'Database Team', 'Export Team', 'Database Team', 'Visualization Team',
                'Import Team', 'Design Team', 'Core Team', 'Database Team', 'Database Team',
                'Design Team', 'Mobile Team', 'Tasks Team', 'Design Team', 'Core Team'
            ],
            'user_requests': [
                1247, 892, 156, 2341, 1089,
                734, 945, 1523, 2876, 445,
                3421, 2156, 1678, 289, 1834,
                2945, 1234, 1567, 1923, 1456,
                1789, 1345, 678, 823, 567,
                934, 1245, 456, 1123, 389,
                512, 789, 1678, 1456, 923,
                234, 645, 2134, 1567, 1089
            ],
            'estimated_effort': [
                'Large', 'Medium', 'Small', 'Small', 'Large',
                'Medium', 'Medium', 'Medium', 'Small', 'Small',
                'Medium', 'Large', 'Large', 'Medium', 'Small',
                'Medium', 'Medium', 'Large', 'Medium', 'Medium',
                'Small', 'Large', 'Small', 'Medium', 'Small',
                'Medium', 'Medium', 'Small', 'Medium', 'Small',
                'Medium', 'Small', 'Small', 'Small', 'Large',
                'Small', 'Medium', 'Medium', 'Medium', 'Small'
            ],
            'target_quarter': [
                'Q1 2025', 'Q4 2024', 'Q2 2025', 'Q4 2024', 'Q1 2025',
                'Q2 2025', 'Q1 2025', 'Q4 2024', 'Q3 2024', 'Q3 2024',
                'Q3 2024', 'Q1 2025', 'Q4 2024', 'Q2 2025', 'Q3 2024',
                'Q3 2024', 'Q1 2025', 'Q4 2024', 'Q3 2024', 'Q3 2024',
                'Q2 2024', 'Q1 2025', 'Q2 2024', 'Q2 2025', 'Q2 2024',
                'Q4 2024', 'Q2 2024', 'Q2 2024', 'Q1 2025', 'Q4 2024',
                'Q2 2025', 'Q1 2024', 'Q2 2024', 'Q2 2024', 'Q2 2025',
                'Q4 2024', 'Q2 2025', 'Q1 2025', 'Q3 2024', 'Q1 2025'
            ],
            'description': [
                'Implement AI-powered suggestions for completing sentences and blocks based on context and user patterns',
                'Add advanced filtering capabilities to database tables including multiple conditions and saved filter sets',
                'Allow enterprise customers to configure custom rate limits for API usage based on their needs',
                'Enhance dark mode with better contrast ratios and support for custom color schemes',
                'Redesign database relations system to support many-to-many relationships and circular references',
                'Native email integration allowing users to send and receive emails directly within Notion pages',
                'Visual formula builder with drag-and-drop interface for creating complex database formulas',
                'Two-way sync with Google Calendar for seamless event management and scheduling',
                'Enable inline commenting on specific text selections for better collaboration and feedback',
                'Pre-built Kanban board templates for common workflows like sprint planning and content calendars',
                'Show real-time cursor positions of collaborators editing the same page',
                'Full offline functionality for mobile apps with automatic sync when connection is restored',
                'Native charting capabilities for visualizing database data with various chart types',
                'Analytics dashboard showing page views, edit history, and collaboration metrics',
                'Improved PDF export with better formatting, custom page sizes, and embedded media support',
                'Real-time push notifications for mentions, comments, and page updates across all devices',
                'Enhanced Slack integration with better formatting, thread support, and bidirectional sync',
                'Group table rows by property values with collapsible sections and aggregate functions',
                'Timeline view for databases to visualize date-based data in a Gantt-chart style layout',
                'Search through page version history to find and restore specific past versions',
                'Browser extension for clipping web content directly into Notion with formatting preserved',
                'Granular workspace permissions with role-based access control and custom permission sets',
                'Native Zapier integration for connecting Notion with thousands of other apps and services',
                'Advanced search with filters for date ranges, authors, page types, and custom properties',
                'Reusable block templates that can be inserted quickly with predefined content and structure',
                'Filter calendar views by database properties to show only relevant events',
                'Database rollup properties that aggregate data from related databases',
                'Export pages and databases to Markdown format with proper formatting and links',
                'Autocomplete suggestions for formula functions with inline documentation',
                'Customize gallery view card layouts with custom property display and sizing options',
                'Import tool for migrating content from Confluence with preserved formatting and structure',
                'Searchable keyboard shortcuts panel with customization options',
                'Rich link preview cards showing metadata, images, and descriptions for external URLs',
                'Multi-select property type for databases allowing multiple values per field',
                'Support for creating databases within database items for hierarchical data structures',
                'Support for video files as page cover images with autoplay and loop options',
                'Quick capture widget for mobile devices to rapidly add notes and tasks',
                'Recurring task functionality with flexible scheduling options and automatic creation',
                'Customize sidebar layout with collapsible sections, custom ordering, and favorites',
                'Automatically update table of contents blocks when page structure changes'
            ]
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

