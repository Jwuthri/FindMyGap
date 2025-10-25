"""
Find My Gaps - Demo Script

Demonstrates the multi-agent team with proper coordination.
"""

import asyncio
import os
import sys
from app.config import SETTINGS

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from agno.agent import RunEvent
from agno.team import TeamRunEvent
from app.agents.teams import create_findmygaps_team


async def demo_with_events(team, question: str):
    """Demo with detailed event logging."""
    print(f"\n{'='*80}")
    print(f"Question: {question}")
    print(f"{'='*80}\n")
    
    async for event in team.arun(
        question,
        stream=True,
        stream_intermediate_steps=True,
        stream_member_events=True
    ):
        if hasattr(event, 'event'):
            # Team-level delegation
            if event.event == TeamRunEvent.tool_call_started:
                if hasattr(event.tool, 'tool_name') and event.tool.tool_name == "delegate_task_to_member":
                    args = event.tool.tool_args or {}
                    print(f"\n👥 Delegating to: {args.get('member_id', 'unknown')}")
                    print(f"   Task: {args.get('task', args.get('task_description', ''))[:80]}...")
            
            # Agent tool execution started
            elif event.event == RunEvent.tool_call_started:
                agent_name = getattr(event, 'agent_name', 'Agent')
                print(f"\n🔧 {agent_name} → {event.tool.tool_name} | args: {event.tool.tool_args}")

            # Agent tool execution completed - HERE'S THE DATA
            elif event.event == RunEvent.tool_call_completed:
                agent_name = getattr(event, 'agent_name', 'Agent')
                tool_name = event.tool.tool_name
                
                # Capture data retrieval results
                if tool_name == "retrieve_reviews":
                    print(f"\n📦 Data retrieved from {tool_name}")
                    print(f"   Result preview: {str(event.tool.result)[:200]}...")
                    # This is where you'd send to frontend:
                    # await websocket.send_json({"type": "data", "tool": tool_name, "result": event.tool_result})
            
            # Content output
            elif event.event == RunEvent.run_content:
                print(event.content, end="", flush=True)
            
            # Completion
            elif event.event == RunEvent.run_completed:
                print(f"\n\n✅ Complete\n")
    print("Done")


async def main():
    """Run demo scenarios."""
    team = create_findmygaps_team(
        api_key=SETTINGS.OPENAI_API_KEY,
        db_file="findmygaps_demo.db",
        user_id="demo_user"
    )
    
    demos = [
        # Basic data retrieval
        "Show me all reviews for Spotify",
        
        # ML analysis
        "What are the top 10 most important terms in Spotify reviews using TF-IDF?",
        
        # Sentiment analysis
        "Analyze the sentiment distribution for Notion",
        
        # Feature requests
        "What features are Slack customers requesting?",
        
        # Clustering
        "Group Spotify reviews by topic",
        
        # Comparison
        "Compare sentiment between Spotify and Notion",
        
        # Output format
        "Show me a chart of rating distribution for Spotify",
        
        # Complex query
        "What are the top 3 product gaps for Notion based on negative reviews? Show as a table.",
    ]
    
    print("\n🚀 Find My Gaps - Demo\n")
    print("Available demos:")
    for i, demo in enumerate(demos, 1):
        print(f"  {i}. {demo}")
    print(f"  {len(demos) + 1}. Run all")
    print(f"  0. Custom question")
    
    try:
        choice = input("\nSelect (0-9): ").strip()
        
        if choice == "0":
            question = input("Your question: ").strip()
            await demo_with_events(team, question)
        
        elif choice == str(len(demos) + 1):
            for question in demos:
                await demo_with_events(team, question)
                await asyncio.sleep(1)
        
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            question = demos[int(choice) - 1]
            await demo_with_events(team, question)
        
        else:
            print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted")


if __name__ == "__main__":
    asyncio.run(main())
