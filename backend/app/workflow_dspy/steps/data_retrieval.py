"""
Data retrieval step for DSPy workflow.

Executes SQL queries from the retrieval plan and returns raw data.
"""

from typing import Any, Dict

from sqlalchemy.orm import Session

from app import get_logger
from app.workflows.steps.data_retrieval import DataRetrievalService

logger = get_logger(__name__)


class DataRetrievalStep:
    """Execute data retrieval queries (no LLM involved)."""
    
    def __call__(self, plan: Any, db_session: Session) -> Dict[str, Any]:
        """
        Execute SQL queries from the retrieval plan.
        
        Args:
            plan: RetrievalPlan with SQL queries
            db_session: SQLAlchemy database session
            
        Returns:
            Dict with retrieved data
        """
        logger.info(f"[DataRetrievalStep] | Executing retrieval plan")
        
        service = DataRetrievalService(db_session)
        
        try:
            result = service.execute_retrieval_plan(plan, format="json")
            return result
        except Exception as e:
            logger.error(f"[DataRetrievalStep] | Retrieval failed: {e}", exc_info=True)
            return {"error": f"Retrieval failed: {e}", "data": {}}
