import logging
from agno.agent import Agent, RunEvent
from agno.models.openrouter import OpenRouter
from app.config import SETTINGS
from app import get_logger
from agno.db.sqlite import SqliteDb
from agno.memory import MemoryManager
from agno.session import AgentSession
from pydantic import BaseModel, Field

logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

logger = get_logger("agno_streaming_simple_agent")
model = OpenRouter(id="openai/gpt-5-mini", api_key=SETTINGS.OPENROUTER_API_KEY, reasoning_effort="medium")
db = SqliteDb(db_file="memory.db")
memory_manager = MemoryManager(db=db, model=model)


class MovieScript(BaseModel):
    setting: str = Field(
        ..., description="Provide a nice setting for a blockbuster movie."
    )
    ending: str = Field(
        ...,
        description="Ending of the movie. If not available, provide a happy ending.",
    )
    genre: str = Field(
        ...,
        description="Genre of the movie. If not available, select action, thriller or romantic comedy.",
    )
    name: str = Field(..., description="Give a name to this movie")
    characters: list[str] = Field(..., description="Name of characters for this movie.")
    storyline: str = Field(
        ..., description="3 sentence storyline for the movie. Make it exciting!"
    )
    rating: dict[str, int] = Field(
        ...,
        description="Your own rating of the movie. 1-10. Return a dictionary with the keys 'story' and 'acting'.",
    )

john_doe_id = "john_doe@example.com"
session = AgentSession(session_id=john_doe_id)
agent = Agent(
    model=model,
    memory_manager=memory_manager,
    enable_agentic_memory=True,
    db=db,
    add_history_to_context=True,
    num_history_runs=3,
    markdown=True,
    user_id=john_doe_id,
    description="You write movie scripts.",
    add_datetime_to_context=True,
    add_location_to_context=True,
    add_memories_to_context=True
)
system_message = agent.get_system_message(session)
print(system_message.content)

response = agent.run(
    "My name is John Doe and I like to swim and play soccer.", 
    stream=True,
    stream_intermediate_steps=True
)

for chunk in response:
    if chunk.event in [RunEvent.tool_call_started]:
        logger.critical(f"TOOL CALL from team member {chunk.agent_id}: {chunk.tool.tool_name} with args: {chunk.tool.tool_args}")
   
    elif chunk.event in [RunEvent.reasoning_step, ]:
        logger.error(f"REASONING from {chunk.agent_id}: {chunk.reasoning_content}")
   
    elif chunk.event in [RunEvent.run_content] and chunk.content:
        logger.info(f"OUTPUT from {chunk.agent_id}: {chunk.content}")
   
    elif chunk.event in [RunEvent.custom_event]:
        logger.warning(f"✅ Custom event emitted: {chunk.event}")

memories = agent.get_user_memories(user_id=john_doe_id)
logger.info(f"John Doe's memories: {memories}")
