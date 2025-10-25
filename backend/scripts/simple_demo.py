"""
Simple single-agent demo - faster and less verbose than team version.
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.config import SETTINGS
from agno.agent import RunEvent
from app.agents.simple_agent import create_simple_agent


async def run_demo(agent, question: str):
    """Run a demo query."""
    print(f"\n{'='*80}")
    print(f"Q: {question}")
    print(f"{'='*80}\n")
    
    async for event in agent.arun(
        question,
        stream=True,
        stream_intermediate_steps=True
    ):
        if hasattr(event, 'event'):
            if event.event == RunEvent.tool_call_started:
                print(f"\n🔧 Using: {event.tool.tool_name}")
            elif event.event == RunEvent.run_content:
                print(event.content, end="", flush=True)
    
    print("\n")


async def main():
    """Run demos."""
    agent = create_simple_agent(
        api_key=SETTINGS.OPENAI_API_KEY,
        db_file="simple_demo.db",
        user_id="demo_user"
    )
    
    demos = [
        "Show me all reviews for Spotify",
        "What are the top 10 most important terms in Spotify reviews using TF-IDF?",
        "Analyze sentiment distribution for Notion",
        "What features are Slack customers requesting?",
        "Group Spotify reviews by topic",
        "Show me negative reviews for Notion",
        "What are the main complaints about Spotify?",
        "Compare Spotify vs Notion - which has better ratings?",
    ]
    
    print("\n🚀 Find My Gaps - Simple Agent Demo\n")
    print("Available demos:")
    for i, demo in enumerate(demos, 1):
        print(f"  {i}. {demo}")
    print(f"  {len(demos) + 1}. Run all")
    print(f"  0. Custom question")
    
    try:
        choice = input("\nSelect (0-9): ").strip()
        
        if choice == "0":
            question = input("Your question: ").strip()
            await run_demo(agent, question)
        
        elif choice == str(len(demos) + 1):
            for question in demos:
                await run_demo(agent, question)
                await asyncio.sleep(0.5)
        
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            question = demos[int(choice) - 1]
            await run_demo(agent, question)
        
        else:
            print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted")


if __name__ == "__main__":
    asyncio.run(main())

