import asyncio

from agno.agent import RunEvent
from agno.agent.agent import Agent
from app.config import SETTINGS
import httpx, json
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool


@tool(requires_confirmation=False)
def get_top_hackernews_stories(num_stories: int) -> str:
    """Fetch top stories from Hacker News.

    Args:
        num_stories (int): Number of stories to retrieve

    Returns:
        str: JSON string containing story details
    """
    # Fetch top story IDs
    response = httpx.get("https://hacker-news.firebaseio.com/v0/topstories.json")
    story_ids = response.json()

    # Yield story details
    all_stories = []
    for story_id in story_ids[:num_stories]:
        story_response = httpx.get(
            f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        )
        story = story_response.json()
        if "text" in story:
            story.pop("text", None)
        all_stories.append(story)
    return json.dumps(all_stories)

finance_agent = Agent(
    id="finance-agent",
    name="Finance Agent",
    model=OpenAIChat(id="gpt-5-mini", api_key=SETTINGS.OPENAI_API_KEY),
    tools=[get_top_hackernews_stories],
)


async def run_agent_with_events(prompt: str):
    content_started = False
    async for run_output_event in finance_agent.arun(
        prompt,
        stream=True,
        stream_intermediate_steps=True,
    ):
        if run_output_event.event in [RunEvent.run_started, RunEvent.run_completed]:
            print(f"\nEVENT: {run_output_event.event}")

        if run_output_event.event in [RunEvent.tool_call_started]:
            print(f"\nEVENT: {run_output_event.event}")
            print(f"TOOL CALL: {run_output_event.tool.tool_name}")  # type: ignore
            print(f"TOOL CALL ARGS: {run_output_event.tool.tool_args}")  # type: ignore

        if run_output_event.event in [RunEvent.tool_call_completed]:
            print(f"\nEVENT: {run_output_event.event}")
            print(f"TOOL CALL: {run_output_event.tool.tool_name}")  # type: ignore
            print(f"TOOL CALL RESULT: {run_output_event.tool.result}")  # type: ignore

        if run_output_event.event in [RunEvent.run_content]:
            if not content_started:
                print("\nCONTENT:")
                content_started = True
            else:
                print(run_output_event.content, end="")


if __name__ == "__main__":
    asyncio.run(
        run_agent_with_events(
            "fetch a story from hacker new",
        )
    )