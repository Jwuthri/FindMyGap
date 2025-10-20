"""
Example demonstrating how to cancel a running agent execution.

This example shows how to:
1. Start an agent run in a separate thread
2. Cancel the run from another thread
3. Handle the cancelled response
"""

import threading
import time

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.run.agent import RunEvent
from agno.run.base import RunStatus

from app.config import SETTINGS

def long_running_task(agent: Agent, run_id_container: dict):
    """
    Simulate a long-running agent task that can be cancelled.

    Args:
        agent: The agent to run
        run_id_container: Dictionary to store the run_id for cancellation

    Returns:
        Dictionary with run results and status
    """
    try:
        print("🔵 Agent thread: Starting stream...")
        # Start the agent run - this simulates a long task
        final_response = None
        content_pieces = []

        for chunk in agent.run(
            "Write a very long story about a dragon who learns to code. "
            "Make it at least 2000 words with detailed descriptions and dialogue. "
            "Take your time and be very thorough.",
            stream=True,
        ):
            if "run_id" not in run_id_container and chunk.run_id:
                run_id_container["run_id"] = chunk.run_id
                print(f"🔵 Agent thread: Got run_id: {chunk.run_id}")

            if chunk.event == RunEvent.run_content:
                print(chunk.content, end="", flush=True)
                content_pieces.append(chunk.content)
            # When the run is cancelled, a `RunEvent.run_cancelled` event is emitted
            elif chunk.event == RunEvent.run_cancelled:
                print(f"\n🚫 Run was cancelled: {chunk.run_id}")
                run_id_container["result"] = {
                    "status": "cancelled",
                    "run_id": chunk.run_id,
                    "cancelled": True,
                    "content": "".join(content_pieces)[:200] + "..."
                    if content_pieces
                    else "No content before cancellation",
                }
                return
            elif hasattr(chunk, "status") and chunk.status == RunStatus.completed:
                final_response = chunk

        # If we get here, the run completed successfully
        if final_response:
            run_id_container["result"] = {
                "status": final_response.status.value
                if final_response.status
                else "completed",
                "run_id": final_response.run_id,
                "cancelled": final_response.status == RunStatus.cancelled,
                "content": ("".join(content_pieces)[:200] + "...")
                if content_pieces
                else "No content",
            }
        else:
            run_id_container["result"] = {
                "status": "unknown",
                "run_id": run_id_container.get("run_id"),
                "cancelled": False,
                "content": ("".join(content_pieces)[:200] + "...")
                if content_pieces
                else "No content",
            }

    except Exception as e:
        print(f"\n❌ Exception in run: {str(e)}")
        run_id_container["result"] = {
            "status": "error",
            "error": str(e),
            "run_id": run_id_container.get("run_id"),
            "cancelled": True,
            "content": "Error occurred",
        }


def cancel_after_delay(agent: Agent, run_id_container: dict, delay_seconds: int = 3):
    """
    Cancel the agent run after a specified delay.

    Args:
        agent: The agent whose run should be cancelled
        run_id_container: Dictionary containing the run_id to cancel
        delay_seconds: How long to wait before cancelling
    """
    print(f"🔴 Cancel thread: Starting, will wait for run_id...")
    
    # Wait for run_id to be available (with timeout)
    max_wait = 10  # Max seconds to wait for run_id
    waited = 0
    while "run_id" not in run_id_container and waited < max_wait:
        time.sleep(0.1)
        waited += 0.1
        if waited % 1 == 0:  # Print every second
            print(f"🔴 Cancel thread: Still waiting for run_id... ({int(waited)}s)")
    
    if "run_id" not in run_id_container:
        print("⚠️  No run_id found after waiting")
        return
    
    print(f"🔴 Cancel thread: Got run_id, waiting {delay_seconds} seconds before cancel...")
    # Now wait for the delay before cancelling
    time.sleep(delay_seconds)

    run_id = run_id_container.get("run_id")
    if run_id:
        print(f"🚫 Cancelling run: {run_id}")
        success = agent.cancel_run(run_id)
        if success:
            print(f"✅ Run {run_id} marked for cancellation")
        else:
            print(
                f"❌ Failed to cancel run {run_id} (may not exist or already completed)"
            )
    else:
        print("⚠️  No run_id found to cancel")


def main():
    """Main function demonstrating run cancellation."""

    # Initialize the agent with a model
    agent = Agent(
        name="StorytellerAgent",
        model=OpenAIChat(id="gpt-5-nano", api_key=SETTINGS.OPENAI_API_KEY),  # Use a model that can generate long responses
        description="An agent that writes detailed stories",
    )

    print("🚀 Starting agent run cancellation example...")
    print("=" * 50)

    # Container to share run_id between threads
    run_id_container = {}

    # Start the agent run in a separate thread
    agent_thread = threading.Thread(
        target=lambda: long_running_task(agent, run_id_container), name="AgentRunThread"
    )

    # Start the cancellation thread
    cancel_thread = threading.Thread(
        target=cancel_after_delay,
        args=(agent, run_id_container, 3),  # Cancel after 5 seconds
        name="CancelThread",
    )

    # Start both threads
    print("🏃 Starting agent run thread...")
    agent_thread.start()
    
    # Give agent thread a moment to actually start
    time.sleep(0.5)

    print("🏃 Starting cancellation thread...")
    cancel_thread.start()

    # Wait for both threads to complete
    print("⌛ Waiting for threads to complete...")
    agent_thread.join()
    cancel_thread.join()

    # Print the results
    print("\n" + "=" * 50)
    print("📊 RESULTS:")
    print("=" * 50)

    result = run_id_container.get("result")
    if result:
        print(f"Status: {result['status']}")
        print(f"Run ID: {result['run_id']}")
        print(f"Was Cancelled: {result['cancelled']}")

        if result.get("error"):
            print(f"Error: {result['error']}")
        else:
            print(f"Content Preview: {result['content']}")

        if result["cancelled"]:
            print("\n✅ SUCCESS: Run was successfully cancelled!")
        else:
            print("\n⚠️  WARNING: Run completed before cancellation")
    else:
        print("❌ No result obtained - check if cancellation happened during streaming")

    print("\n🏁 Example completed!")


if __name__ == "__main__":
    # Run the main example
    main()