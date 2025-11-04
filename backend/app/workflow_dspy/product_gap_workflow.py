"""
Product Gap Detection Workflow using DSPy.

This workflow uses DSPy modules and signatures instead of Agno agents.
"""

from typing import Optional

import dspy
from app import get_logger
from app.database.base import SessionLocal
from app.dspy_workflow.modules.query_analyzer import QueryAnalyzer
from app.dspy_workflow.modules.retrieval_planner import RetrievalPlanner
from app.dspy_workflow.modules.output_formatter import OutputFormatter
from app.dspy_workflow.modules.answer_writer import AnswerWriter
from app.dspy_workflow.steps.data_retrieval import DataRetrievalStep
from app.services.schema_service import SchemaService

logger = get_logger(__name__)


class ProductGapWorkflow(dspy.Module):
    """
    DSPy-based Product Gap Detection Workflow.
    
    Architecture:
    1. Query Analysis - determine what's needed
    2. Output Format Detection - determine desired format
    3. Retrieval Planning (conditional) - plan data retrieval
    4. Data Retrieval (conditional) - execute queries
    5. Answer Writing - generate final response
    """
    
    def __init__(self, user_id: Optional[int] = 1):
        super().__init__()
        self.user_id = user_id
        
        # Initialize modules
        self.query_analyzer = QueryAnalyzer()
        self.output_formatter = OutputFormatter()
        
        # Get table schemas for retrieval planner
        db_session = SessionLocal()
        try:
            schema_service = SchemaService(db_session)
            self.table_schemas = schema_service.get_all_available_schemas(user_id)
            logger.info(f"[ProductGapWorkflow] | Loaded {len(self.table_schemas)} table schemas")
        finally:
            db_session.close()
        
        self.retrieval_planner = RetrievalPlanner(table_schemas=self.table_schemas)
        self.data_retrieval = DataRetrievalStep()
        self.answer_writer = AnswerWriter()
    
    def forward(self, query: str):
        """
        Execute the workflow.
        
        Args:
            query: User's question
            
        Returns:
            Final formatted answer
        """
        logger.info(f"[ProductGapWorkflow] | Processing query: {query}")
        
        # Step 1: Analyze query
        logger.info("▶️  STEP: Query Analysis")
        analysis = self.query_analyzer(query=query)
        logger.info(f"   └─ Needs data: {analysis.needs_data_retrieval}")
        logger.info(f"   └─ Query type: {analysis.query_type}")
        
        # Step 2: Determine output format
        logger.info("▶️  STEP: Output Format Detection")
        output_format = self.output_formatter(query=query)
        logger.info(f"   └─ Format: {output_format.format_type}")
        
        # Step 3 & 4: Conditional data retrieval
        retrieved_data = None
        if analysis.needs_data_retrieval:
            logger.info("▶️  STEP: Retrieval Planning")
            retrieval_plan = self.retrieval_planner(
                query=query,
                analysis=analysis.reasoning
            )
            logger.info(f"   └─ Plan: {retrieval_plan.reasoning}")
            
            logger.info("▶️  STEP: Data Retrieval")
            db_session = SessionLocal()
            try:
                retrieved_data = self.data_retrieval(
                    plan=retrieval_plan,
                    db_session=db_session
                )
                logger.info(f"   └─ Retrieved {retrieved_data.get('total_rows', 0)} rows")
            finally:
                db_session.close()
        
        # Step 5: Generate final answer
        logger.info("▶️  STEP: Answer Writing")
        answer = self.answer_writer(
            query=query,
            analysis=analysis,
            output_format=output_format,
            data=retrieved_data
        )
        
        logger.info("✓ Workflow completed")
        return answer.answer
