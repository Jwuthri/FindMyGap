"""
Utility functions for DSPy workflow.
"""

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List


def decimal_default(obj):
    """JSON serializer for Decimal, date, and datetime objects."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def format_data_summary(data: Dict[str, Any]) -> str:
    """
    Create a concise summary of retrieved data.
    
    Args:
        data: Dictionary of retrieved data
        
    Returns:
        Formatted string summary
    """
    if not data or 'data' not in data:
        return "No data available"
    
    datasets = data['data']
    total_rows = data.get('total_rows', 0)
    
    summary_parts = [f"Total rows: {total_rows}"]
    
    for key, value in datasets.items():
        if isinstance(value, list):
            summary_parts.append(f"- {key}: {len(value)} rows")
        elif isinstance(value, dict):
            summary_parts.append(f"- {key}: {len(value)} keys")
        else:
            summary_parts.append(f"- {key}: {type(value).__name__}")
    
    return "\n".join(summary_parts)


def truncate_data_for_llm(data: List[Dict[str, Any]], max_rows: int = 100) -> List[Dict[str, Any]]:
    """
    Truncate data to avoid token limits.
    
    Args:
        data: List of data rows
        max_rows: Maximum number of rows to keep
        
    Returns:
        Truncated data
    """
    if len(data) <= max_rows:
        return data
    
    # Keep first and last rows for context
    half = max_rows // 2
    return data[:half] + data[-half:]


def extract_json_from_text(text: str) -> Any:
    """
    Extract JSON from text that might contain markdown code blocks.
    
    Args:
        text: Text potentially containing JSON
        
    Returns:
        Parsed JSON object or None
    """
    # Try direct parsing first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try extracting from code blocks
    import re
    
    # Look for ```json ... ``` blocks
    json_block = re.search(r'```json\s*\n(.*?)\n```', text, re.DOTALL)
    if json_block:
        try:
            return json.loads(json_block.group(1))
        except json.JSONDecodeError:
            pass
    
    # Look for any ``` ... ``` blocks
    code_block = re.search(r'```\s*\n(.*?)\n```', text, re.DOTALL)
    if code_block:
        try:
            return json.loads(code_block.group(1))
        except json.JSONDecodeError:
            pass
    
    return None


def format_schema_for_prompt(schemas: List[Dict[str, Any]]) -> str:
    """
    Format database schemas for inclusion in prompts.
    
    Args:
        schemas: List of table schema dictionaries
        
    Returns:
        Formatted string
    """
    formatted = []
    
    for schema in schemas:
        table_name = schema.get('table_name', 'unknown')
        columns = schema.get('columns', [])
        
        col_strs = []
        for col in columns:
            col_name = col.get('name', 'unknown')
            col_type = col.get('type', 'unknown')
            col_strs.append(f"  - {col_name}: {col_type}")
        
        formatted.append(f"Table: {table_name}\n" + "\n".join(col_strs))
    
    return "\n\n".join(formatted)


def validate_sql_query(query: str) -> bool:
    """
    Basic validation of SQL query for safety.
    
    Args:
        query: SQL query string
        
    Returns:
        True if query appears safe, False otherwise
    """
    query_lower = query.lower().strip()
    
    # Block dangerous operations
    dangerous_keywords = ['drop', 'delete', 'truncate', 'alter', 'create', 'insert', 'update']
    
    for keyword in dangerous_keywords:
        if keyword in query_lower:
            return False
    
    # Must be a SELECT query
    if not query_lower.startswith('select'):
        return False
    
    return True
