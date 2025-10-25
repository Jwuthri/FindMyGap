"""
Quick test script - using simple single agent (faster).
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.config import SETTINGS
from app.agents.simple_agent import create_simple_agent
from agno.agent import RunEvent


async def quick_test():
    """Quick test."""
    
    print("\n🚀 Find My Gaps - Quick Test\n")
    
    agent = create_simple_agent(
        api_key=SETTINGS.OPENAI_API_KEY,
        db_file="/tmp/test.db",
        user_id="test_user"
    )
    
    question = "What are the top 10 terms in Spotify reviews using TF-IDF?"
    
    print(f"Question: {question}\n")
    print("="*80 + "\n")
    
    async for event in agent.arun(
        question,
        stream=True,
        stream_intermediate_steps=True
    ):
        if hasattr(event, 'event'):
            if event.event == RunEvent.tool_call_started:
                print(f"🔧 {event.tool.tool_name}\n")
            elif event.event == RunEvent.run_content:
                print(event.content, end="", flush=True)
    
    print("\n\n" + "="*80)
    print("✅ Test complete!")


if __name__ == "__main__":
    asyncio.run(quick_test())

