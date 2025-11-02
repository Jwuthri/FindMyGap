"""
Data retrieval step using SQLAlchemy.

Executes SQL queries from the retrieval plan and returns raw data.
"""

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
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute SQL queries from the retrieval plan and return raw data.
        
        Args:
            plan: RetrievalPlan with SQL queries
            user_id: Optional user ID for logging
            
        Returns:
            Dict with data organized by result_key
        """
        logger.info(f"{self._log_prefix(user_id)} | Executing retrieval plan: {plan.reasoning}")
        logger.info(f"{self._log_prefix(user_id)} | Expected data types: {plan.expected_data_types}")
        
        # Execute all SQL queries
        results = {}
        total_rows = 0
        
        for sql_query in plan.sql_queries:
            logger.info(f"{self._log_prefix(user_id)} | Executing query for '{sql_query.purpose}': {sql_query.query}")
            
            try:
                query_results = self.execute_sql_query(sql_query.query, user_id)
                results[sql_query.result_key] = query_results
                total_rows += len(query_results)
                logger.info(f"{self._log_prefix(user_id)} | Retrieved {len(query_results)} rows for {sql_query.result_key}")
                
            except Exception as e:
                logger.error(f"{self._log_prefix(user_id)} | Query failed for {sql_query.purpose}: {e}", exc_info=True)
                results[sql_query.result_key] = []
                results[f"{sql_query.result_key}_error"] = str(e)
        
        logger.info(f"{self._log_prefix(user_id)} | Total rows retrieved: {total_rows}")
        
        return {
            "data": results,
            "total_rows": total_rows,
            "data_types": plan.expected_data_types,
            "retrieval_reasoning": plan.reasoning
        }


def execute_data_retrieval(step_input: StepInput, db: Session) -> StepOutput:
    """
    Execute SQL queries from the retrieval plan and return raw data.
    This function does NOT use an LLM - it directly executes SQL queries.
    
    Args:
        step_input: Contains the RetrievalPlan with SQL queries
        db: SQLAlchemy database session
        
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
        result = service.execute_retrieval_plan(plan.content)
        return StepOutput(content=result)
    except Exception as e:
        logger.error(f"[execute_data_retrieval] | [user_id=None] | [company_id=None] | Retrieval failed: {e}", exc_info=True)
        return StepOutput(content={"error": f"Retrieval failed: {e}", "data": {}})
