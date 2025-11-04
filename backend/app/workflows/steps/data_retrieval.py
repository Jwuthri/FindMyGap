"""
Data retrieval step using SQLAlchemy.

Executes SQL queries from the retrieval plan and returns raw data.
"""

import csv
import io
from typing import Any, Dict, List, Optional

from agno.workflow.types import StepInput, StepOutput
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import get_logger

logger = get_logger(__name__)


class DataRetrievalService:
    """Service for executing data retrieval queries."""

    def __init__(self, db: Session):
        """
        Initialize data retrieval service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    @staticmethod
    def _format_as_csv(data: List[Dict[str, Any]]) -> str:
        """Convert list of dicts to CSV string (most token-efficient)."""
        if not data:
            return ""
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()

    @staticmethod
    def _format_as_markdown_table(data: List[Dict[str, Any]], max_rows: int = 100) -> str:
        """Convert list of dicts to markdown table (human-readable)."""
        if not data:
            return "No data"
        
        # Limit rows for very large datasets
        display_data = data[:max_rows]
        truncated = len(data) > max_rows
        
        keys = list(data[0].keys())
        
        # Header
        lines = [
            "| " + " | ".join(keys) + " |",
            "| " + " | ".join(["---"] * len(keys)) + " |"
        ]
        
        # Rows
        for row in display_data:
            values = [str(row.get(k, "")) for k in keys]
            lines.append("| " + " | ".join(values) + " |")
        
        if truncated:
            lines.append(f"\n*Showing {max_rows} of {len(data)} rows*")
        
        return "\n".join(lines)

    def _log_prefix(self, user_id: Optional[str] = None, company_id: Optional[str] = None) -> str:
        """Generate log prefix following team standards."""
        return f"[DataRetrievalService] | [user_id={user_id or 'None'}] | [company_id={company_id or 'None'}]"

    def execute_sql_query(self, query: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results as list of dicts.
        
        Args:
            query: SQL query to execute
            user_id: Optional user ID for logging
            
        Returns:
            List of row dictionaries
        """
        try:
            result = self.db.execute(text(query))
            
            # Convert rows to dicts
            columns = result.keys()
            results = []
            for row in result:
                results.append(dict(zip(columns, row)))
            
            logger.info(f"{self._log_prefix(user_id)} | Executed query, returned {len(results)} rows")
            return results
            
        except Exception as e:
            logger.error(f"{self._log_prefix(user_id)} | Query execution failed: {e}", exc_info=True)
            raise

    def execute_retrieval_plan(
        self,
        plan: Any,
        user_id: Optional[str] = None,
        format: str = "csv"  # Options: "csv", "markdown", "json"
    ) -> Dict[str, Any]:
        """
        Execute SQL queries from the retrieval plan and return raw data.
        
        Args:
            plan: RetrievalPlan with SQL queries
            user_id: Optional user ID for logging
            format: Output format - "csv" (most compact), "markdown" (readable), or "json" (structured)
            
        Returns:
            Dict with data organized by result_key in specified format
        """
        logger.info(f"{self._log_prefix(user_id)} | Executing retrieval plan: {plan.reasoning}")
        logger.info(f"{self._log_prefix(user_id)} | Expected data types: {plan.expected_data_types}")
        logger.info(f"{self._log_prefix(user_id)} | Output format: {format}")
        
        # Execute all SQL queries
        results = {}
        total_rows = 0
        
        for sql_query in plan.sql_queries:
            logger.info(f"{self._log_prefix(user_id)} | Executing query for '{sql_query.purpose}': {sql_query.query}")
            
            try:
                query_results = self.execute_sql_query(sql_query.query, user_id)
                
                # Format based on requested format
                if format == "csv":
                    results[sql_query.result_key] = self._format_as_csv(query_results)
                elif format == "markdown":
                    results[sql_query.result_key] = self._format_as_markdown_table(query_results)
                else:  # json (default fallback)
                    results[sql_query.result_key] = query_results
                
                total_rows += len(query_results)
                logger.info(f"{self._log_prefix(user_id)} | Retrieved {len(query_results)} rows for {sql_query.result_key}")
            except Exception as e:
                logger.error(f"{self._log_prefix(user_id)} | Query failed for {sql_query.purpose}: {e}", exc_info=True)
                results[sql_query.result_key] = ""
                results[f"{sql_query.result_key}_error"] = str(e)
        
        logger.info(f"{self._log_prefix(user_id)} | Total rows retrieved: {total_rows}")
        
        return {
            "data": results,
            "total_rows": total_rows,
            "data_types": plan.expected_data_types,
            "retrieval_reasoning": plan.reasoning,
            "format": format
        }


def execute_data_retrieval(step_input: StepInput, db: Session, format: str = "csv") -> StepOutput:
    """
    Execute SQL queries from the retrieval plan and return raw data.
    This function does NOT use an LLM - it directly executes SQL queries.
    
    Args:
        step_input: Contains the RetrievalPlan with SQL queries
        db: SQLAlchemy database session
        format: Output format - "csv" (most compact), "markdown" (readable), or "json" (structured)
        
    Returns:
        StepOutput with raw data organized by result_key
    """
    # Get the plan from previous step
    plan = step_input.previous_step_outputs.get("RetrievalPlanning")
    
    if not plan:
        logger.error("[execute_data_retrieval] | [user_id=None] | [company_id=None] | No retrieval plan found")
        return StepOutput(content={"error": "No retrieval plan", "data": {}})
    # Execute retrieval
    service = DataRetrievalService(db)
    
    try:
        result = service.execute_retrieval_plan(plan.content, format=format)
        return StepOutput(content=result)
    except Exception as e:
        logger.error(f"[execute_data_retrieval] | [user_id=None] | [company_id=None] | Retrieval failed: {e}", exc_info=True)
        return StepOutput(content={"error": f"Retrieval failed: {e}", "data": {}})
