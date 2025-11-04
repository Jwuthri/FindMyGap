import asyncio
from typing import Dict, List

from agno.agent import Agent
from pydantic import BaseModel, Field
from agno.models.openrouter import OpenRouter
from app.config import SETTINGS


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
    characters: List[str] = Field(..., description="Name of characters for this movie.")
    storyline: str = Field(
        ..., description="3 sentence storyline for the movie. Make it exciting!"
    )
    rating: Dict[str, int] = Field(
        ...,
        description="Your own rating of the movie. 1-10. Return a dictionary with the keys 'story' and 'acting'.",
    )

model = OpenRouter(id="openai/gpt-5-mini", api_key=SETTINGS.OPENROUTER_API_KEY, reasoning_effort="low")


# Agent that uses structured outputs with streaming
structured_output_agent = Agent(
    model=model,
    description="You write movie scripts.",
    output_schema=MovieScript,
)

# structured_output_agent.print_response(
#     "New York", stream=True, stream_intermediate_steps=True
# )
res = structured_output_agent.run("New York")
