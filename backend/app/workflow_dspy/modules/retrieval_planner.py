"""
Retrieval Planner module using DSPy.
"""

from typing import Any, Dict, List

import dspy
from pydantic import BaseModel, Field


class SQLQuery(BaseModel):
    """Single SQL query in the retrieval plan."""
    purpose: str = Field(..., description="What this query retrieves")
    query: str = Field(..., description="SQL query to execute")
    result_key: str = Field(..., description="Key to store results under")


class RetrievalPlan(BaseModel):
    """Plan for data retrieval."""
    reasoning: str = Field(..., description="Why these queries are needed")
    expected_data_types: List[str] = Field(..., description="Types of data expected")
    sql_queries: List[SQLQuery] = Field(..., description="SQL queries to execute")


class RetrievalPlanningSignature(dspy.Signature):
    """Plan data retrieval strategy."""
    
    query = dspy.InputField(desc="User's question")
    analysis = dspy.InputField(desc="Query analysis reasoning")
    table_schemas = dspy.InputField(desc="Available database table schemas")
    
    reasoning = dspy.OutputField(desc="Explanation of retrieval strategy")
    expected_data_types = dspy.OutputField(desc="Comma-separated list of expected data types")
    sql_queries_json = dspy.OutputField(desc="JSON array of SQL queries with purpose, query, and result_key fields")


class RetrievalPlanner(dspy.Module):
    """Plan data retrieval by generating SQL queries."""
    
    def __init__(self, table_schemas: List[Dict[str, Any]]):
        super().__init__()
        self.table_schemas = table_schemas
        self.plan = dspy.ChainOfThought(RetrievalPlanningSignature)
    
    def forward(self, query: str, analysis: str) -> RetrievalPlan:
        """
        Create a retrieval plan with SQL queries.
        
        Args:
            query: User's question
            analysis: Query analysis reasoning
            
        Returns:
            RetrievalPlan with SQL queries
        """
        import json
        
        # Format schemas for prompt
        schemas_str = "\n\n".join([
            f"Table: {schema['table_name']}\n"
            f"Columns: {', '.join([f\"{col['name']} ({col['type']})\" for col in schema['columns']])}"
            for schema in self.table_schemas
        ])
        
        result = self.plan(
            query=query,
            analysis=analysis,
            table_schemas=schemas_str
        )
        
        # Parse the output
        try:
            sql_queries_data = json.loads(result.sql_queries_json)
            sql_queries = [SQLQuery(**q) for q in sql_queries_data]
        except Exception:
            # Fallback if JSON parsing fails
            sql_queries = []
        
        expected_types = [t.strip() for t in result.expected_data_types.split(',')]
        
        return RetrievalPlan(
            reasoning=result.reasoning,
            expected_data_types=expected_types,
            sql_queries=sql_queries
        )
