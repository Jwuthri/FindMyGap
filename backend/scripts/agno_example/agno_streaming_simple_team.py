from dataclasses import dataclass
import logging
from typing import Optional
from agno.agent import Agent, RunEvent
from agno.models.openrouter import OpenRouter
from app.config import get_settings
from app import get_logger
from agno.db.sqlite import SqliteDb
from agno.memory import MemoryManager
from agno.session import AgentSession
from agno.team import Team, TeamRunEvent
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

logger = get_logger("agno_streaming_simple_agent")

from agno.run.agent import CustomEvent

@dataclass
class CustomerProfileEvent(CustomEvent):
    """CustomEvent for customer profile."""

    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None


from agno.tools import tool

@tool()
def my_tool():
    """
    Get the customer profile for the customer with ID 123.
    """
    return CustomerProfileEvent(
        customer_name="John Doe",
        customer_email="john.doe@example.com",
        customer_phone="1234567890",
    )


settings = get_settings()
model = OpenRouter(id="openai/gpt-5-mini", api_key=settings.OPENROUTER_API_KEY, reasoning_effort="medium")
db = SqliteDb(
    db_file="memory.db",
)
memory_manager = MemoryManager(
    db=db,
    model=model
)

john_doe_id = "john_doe2@example.com"
session = AgentSession(session_id=john_doe_id)

news_agent = Agent(name="News Agent", role="Get the latest news", model=model)
weather_agent = Agent(name="Weather Agent", role="Get the weather for the next 7 days", model=model)
team = Team(
    name="News and Weather Team", 
    members=[news_agent, weather_agent],
    model=model,
    user_id=john_doe_id,
    # tools=[my_tool],
    id="news_and_weather_team"
)

response = team.run(" What is the weather in Tokyo?", stream=True, stream_intermediate_steps=True, stream_member_events=True)

for chunk in response:
    if chunk.event in [RunEvent.tool_call_started]:
        logger.critical(f"TOOL CALL from team member {chunk.agent_id}: {chunk.tool.tool_name} with args: {chunk.tool.tool_args}")
    elif chunk.event in [TeamRunEvent.tool_call_started]:
        if chunk.tool.tool_name == "delegate_task_to_member":
            args = chunk.tool.tool_args or {}
            member_id = args.get("member_id") or args.get("agent_id")
            task = args.get("task")
            logger.info(f"Delegating to: {member_id}, task: {task}")
        logger.critical(f"TOOL CALL from team: {chunk.tool.tool_name} with args: {chunk.tool.tool_args}")

    elif chunk.event in [RunEvent.reasoning_step, ]:
        logger.error(f"REASONING from {chunk.agent_id}: {chunk.reasoning_content}")
    elif chunk.event in [TeamRunEvent.reasoning_step]:
        logger.error(f"REASONING from team: {chunk.reasoning_content}")

    elif chunk.event in [RunEvent.run_content] and chunk.content:
        # breakpoint()
        logger.info(f"OUTPUT from {chunk.agent_id}: {chunk.content}")
    elif chunk.event in [TeamRunEvent.run_content] and chunk.content:
        logger.info(f"OUTPUT from team: {chunk.content}")
    
    elif chunk.event in [TeamRunEvent.custom_event]:
        print(f"✅ Custom team event emitted: {chunk.event}")

    elif chunk.event in [RunEvent.custom_event]:
        print(f"✅ Custom event emitted: {chunk.event}")
