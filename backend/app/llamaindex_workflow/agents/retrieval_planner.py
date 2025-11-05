"""
Retrieval planner agent for creating data retrieval strategies.
"""

from typing import Dict, Any
from llama_index.core.llms import ChatMessage
from app import get_logger

from .base import get_llm, RetrievalPlan

logger = get_logger(__name__)


async def plan_retrieval(query: str, table_schemas: Dict[str, Any]) -> RetrievalPlan:
    """
    Plan data retrieval strategy.
    """
    llm = get_llm()
    sllm = llm.as_structured_llm(output_cls=RetrievalPlan)
    
    # Handle case where table_schemas is a string (from schema service)
    if isinstance(table_schemas, str):
        schema_info = table_schemas
    else:
        schema_info = "\n".join([
            f"Table: {name}\nSchema: {schema}"
            for name, schema in table_schemas.items()
        ])
    
    prompt = f"""Create a data retrieval plan for this query:

Query: {query}

Available Tables:
{schema_info}

Generate SQL queries to retrieve the necessary data."""

    messages = [
        ChatMessage(role="system", content="You are a data retrieval planner that creates SQL queries."),
        ChatMessage(role="user", content=prompt)
    ]
    
    response = await sllm.achat(messages)
    result = response.raw
    
    logger.info(f"Retrieval plan: {result}")
    return result