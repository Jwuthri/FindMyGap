import sqlite3
from typing import Any
from agno.workflow.types import StepInput, StepOutput
from app import get_logger

logger = get_logger("workflows.steps.data_retrieval")


def execute_sql_query(db_connection: sqlite3.Connection, query: str) -> list[dict[str, Any]]:
    """
    Execute a SQL query and return results as list of dicts.
    
    Args:
        db_connection: SQLite database connection
        query: SQL query to execute
        
    Returns:
        List of row dictionaries
    """
    cursor = db_connection.cursor()
    cursor.execute(query)
    
    # Get column names
    columns = [description[0] for description in cursor.description]
    
    # Convert rows to dicts
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    
    return results


def execute_data_retrieval(step_input: StepInput, db_path: str = "memory.db") -> StepOutput:
    """
    Execute SQL queries from the retrieval plan and return raw data.
    This function does NOT use an LLM - it directly executes SQL queries.
    
    Args:
        step_input: Contains the RetrievalPlan with SQL queries
        db_path: Path to SQLite database
        
    Returns:
        StepOutput with raw data organized by result_key
    """
    # Get the plan from previous step
    plan = step_input.previous_step_outputs.get("RetrievalPlanning")
    
    if not plan:
        logger.error("No retrieval plan found")
        return StepOutput(content={"error": "No retrieval plan", "data": {}})
    
    logger.info(f"Executing retrieval plan: {plan.reasoning}")
    logger.info(f"Expected data types: {plan.expected_data_types}")
    
    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        logger.info(f"Connected to database: {db_path}")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return StepOutput(content={"error": f"Database connection failed: {e}", "data": {}})
    
    # Execute all SQL queries
    results = {}
    total_rows = 0
    
    try:
        for sql_query in plan.sql_queries:
            logger.info(f"Executing query for '{sql_query.purpose}': {sql_query.query}")
            
            try:
                query_results = execute_sql_query(conn, sql_query.query)
                results[sql_query.result_key] = query_results
                total_rows += len(query_results)
                logger.info(f"Retrieved {len(query_results)} rows for {sql_query.result_key}")
                
            except Exception as e:
                logger.error(f"Query failed for {sql_query.purpose}: {e}")
                results[sql_query.result_key] = []
                results[f"{sql_query.result_key}_error"] = str(e)
    
    finally:
        conn.close()
        logger.info(f"Database connection closed. Total rows retrieved: {total_rows}")
    
    # Return raw structured data
    return StepOutput(content={
        "data": results,
        "total_rows": total_rows,
        "data_types": plan.expected_data_types,
        "retrieval_reasoning": plan.reasoning
    })

