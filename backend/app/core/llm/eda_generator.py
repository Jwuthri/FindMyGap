"""
LLM-based EDA generation for database tables.

This module uses LLM agents to analyze table statistics and generate comprehensive
field metadata including descriptions, data types, and value distributions.
"""

from typing import Any, Dict, List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from pydantic import BaseModel, Field

from app import get_logger

logger = get_logger(__name__)


class FieldMetadata(BaseModel):
    """Metadata for a single field."""
    field_name: str = Field(description="Name of the field")
    data_type: str = Field(description="Data type (int, text, timestamp, float, boolean)")
    description: str = Field(description="Detailed description of what this field represents and its purpose")
    unique_value_count: int | None = Field(default=None, description="Number of unique values")
    top_values: List[str] | None = Field(default=None, description="Top 5-10 most common values with counts")


class TableEDAResponse(BaseModel):
    """LLM response for table EDA."""
    summary: str = Field(description="A concise summary of the table data (2-3 sentences)")
    field_metadata: List[FieldMetadata] = Field(description="Detailed metadata for each field including description and purpose")


class EDAGenerator:
    """Service for generating table EDA using LLM."""

    def _log_prefix(self, table_name: str = None) -> str:
        """Generate log prefix following team standards."""
        return f"[EDAGenerator] | [table={table_name or 'None'}]"

    async def generate_table_eda(
        self,
        table_name: str,
        column_stats: Dict[str, Dict[str, Any]],
        row_count: int,
        model: OpenAIChat
    ) -> TableEDAResponse:
        """
        Use LLM to generate summary and field metadata from column statistics.
        
        Args:
            table_name: Name of the table
            column_stats: Column statistics
            row_count: Total row count
            model: LLM model
            
        Returns:
            TableEDAResponse with summary and field metadata
        """
        logger.info(f"{self._log_prefix(table_name)} | Generating LLM insights")
        
        # Format stats for LLM
        stats_summary = f"Table: {table_name}\nTotal Rows: {row_count}\n\nColumn Statistics:\n"
        for col_name, stats in column_stats.items():
            stats_summary += f"\n{col_name} ({stats.get('dtype', 'unknown')}):\n"
            for key, value in stats.items():
                if key == 'top_values':
                    # Format top values nicely
                    top_str = ", ".join([f"{k}({v})" for k, v in list(value.items())[:5]])
                    stats_summary += f"  - {key}: {top_str}\n"
                elif key == 'sample_values':
                    stats_summary += f"  - {key}: {', '.join(map(str, value))}\n"
                elif key != 'dtype':
                    stats_summary += f"  - {key}: {value}\n"
        
        prompt = f"""Analyze this database table and provide:

1. A concise summary (2-3 sentences) describing what this table contains and its purpose

2. For EACH field, provide:
   - field_name: The exact column name
   - data_type: Simplified type (int, text, timestamp, float, boolean)
   - description: A detailed description (1-2 sentences) explaining what this field represents, its purpose, and any important patterns or characteristics
   - unique_value_count: Number of unique values (if available)
   - top_values: List of top 5-10 most common values formatted as "value(count)" (if applicable)

Table: {table_name}
Total Rows: {row_count}

{stats_summary}

Be specific and actionable. Focus on helping someone understand what each field means and how to use it in queries.
For example, if a field is "conversation_id", explain that it's a UUID that groups messages in the same conversation thread."""

        # Create agent with structured output
        agent = Agent(
            name="EDA Generator",
            model=model,
            description="Generate table EDA with field metadata",
            output_schema=TableEDAResponse,
            markdown=False
        )
        
        response = await agent.arun(prompt)
        eda_response: TableEDAResponse = response.content
        
        logger.info(f"{self._log_prefix(table_name)} | Generated metadata for {len(eda_response.field_metadata)} fields")
        return eda_response
