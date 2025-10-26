import asyncio

from agno.run.workflow import WorkflowRunEvent
from agno.agent import RunEvent
from agno.team.team import TeamRunEvent
from app import get_logger
from app.workflows.product_gap_workflow import create_product_gap_workflow

logger = get_logger("workflows.main")


async def run_workflow(query: str, stream: bool = True):
    """
    Execute the workflow for a given query.
    
    Args:
        query: User's question
        stream: Whether to stream intermediate results
    """
    workflow = create_product_gap_workflow()
    if stream:
        resp = await workflow.arun(
            input=query,
            markdown=True,
            stream=True,
            stream_intermediate_steps=True,
        )
        async for event in resp:
            # Workflow-level events
            if event.event == WorkflowRunEvent.workflow_started.value:
                logger.info("=" * 80)
                logger.info(f"🚀 WORKFLOW STARTED: {getattr(event, 'workflow_name', 'ProductGapWorkflow')}")
                logger.info(f"   └─ Input: {query[:100]}{'...' if len(query) > 100 else ''}")
                logger.info("=" * 80)
                
            elif event.event == WorkflowRunEvent.workflow_completed.value:
                duration = getattr(event, 'duration', None)
                logger.info("=" * 80)
                logger.info(f"🏁 WORKFLOW COMPLETED")
                if duration:
                    logger.info(f"   └─ Total duration: {duration:.2f}s")
                logger.info("=" * 80)
                logger.info(f"   └─ Event details: {event}")
            
            # Step-level events
            elif event.event == WorkflowRunEvent.step_started.value:
                step_name = getattr(event, 'step_name', 'Unknown')
                logger.info(f"\n▶️  STEP STARTED: {step_name}")
                logger.info(f"   └─ Event details: {event}")
                
            elif event.event == WorkflowRunEvent.step_completed.value:
                step_name = getattr(event, 'step_name', 'Unknown')
                duration = getattr(event, 'duration', None)
                output = getattr(event, 'output', None)
                
                logger.info(f"✓ STEP COMPLETED: {step_name}")
                if duration:
                    logger.info(f"   ├─ Duration: {duration:.2f}s")
                if output:
                    output_str = str(output)[:200]
                    logger.info(f"   └─ Output preview: {output_str}{'...' if len(str(output)) > 200 else ''}")
                logger.info(f"   └─ Full event: {event}")
            
            # Condition events
            elif event.event == WorkflowRunEvent.condition_execution_started.value:
                logger.info(f"🔀 CONDITION STARTED: {getattr(event, 'condition_name', 'N/A')}")
                logger.info(f"   └─ Event details: {event}")
                
            elif event.event == WorkflowRunEvent.condition_execution_completed.value:
                result = getattr(event, 'result', None)
                logger.info(f"✅ CONDITION COMPLETED: {getattr(event, 'condition_name', 'N/A')} → Result: {result}")
                logger.info(f"   └─ Event details: {event}")
            
            # Agent tool calls
            elif event.event == RunEvent.tool_call_started.value:
                agent_id = getattr(event, 'agent_id', 'Unknown')
                tool_name = getattr(event.tool, 'tool_name', 'Unknown') if hasattr(event, 'tool') else 'Unknown'
                tool_args = getattr(event.tool, 'tool_args', {}) if hasattr(event, 'tool') else {}
                logger.critical(f"🔧 TOOL CALL from agent {agent_id}: {tool_name} with args: {tool_args}")
            
            # Team tool calls
            elif event.event == TeamRunEvent.tool_call_started.value:
                tool_name = getattr(event.tool, 'tool_name', 'Unknown') if hasattr(event, 'tool') else 'Unknown'
                tool_args = getattr(event.tool, 'tool_args', {}) if hasattr(event, 'tool') else {}
                
                if tool_name == "delegate_task_to_member":
                    member_id = tool_args.get("member_id") or tool_args.get("agent_id")
                    task = tool_args.get("task")
                    logger.info(f"   └─ Delegating to: {member_id}, task: {task}")
                
                logger.critical(f"🔧 TOOL CALL from team: {tool_name} with args: {tool_args}")
            
            # Agent reasoning
            elif event.event == RunEvent.reasoning_step.value:
                agent_id = getattr(event, 'agent_id', 'Unknown')
                reasoning = getattr(event, 'reasoning_content', '')
                logger.error(f"🧠 REASONING from {agent_id}: {reasoning}")
            
            # Team reasoning
            elif event.event == TeamRunEvent.reasoning_step.value:
                reasoning = getattr(event, 'reasoning_content', '')
                logger.error(f"🧠 REASONING from team: {reasoning}")
            
            # Agent content
            elif event.event == RunEvent.run_content.value and getattr(event, 'content', None):
                agent_id = getattr(event, 'agent_id', 'Unknown')
                content = event.content
                logger.info(f"📝 OUTPUT from {agent_id}: {content}")
            
            # Team content
            elif event.event == TeamRunEvent.run_content.value and getattr(event, 'content', None):
                content = event.content
                logger.info(f"📝 OUTPUT from team: {content}")
            
            # Custom events
            elif event.event == RunEvent.custom_event.value:
                logger.warning(f"✨ Custom agent event: {event}")
            
            elif event.event == TeamRunEvent.custom_event.value:
                logger.warning(f"✨ Custom team event: {event}")
            
            # Unknown events
            else:
                # print(f"⚠️  Unhandled event")
                pass
    else:
        resp = await workflow.arun(input=query, markdown=True)
        print(resp)


if __name__ == "__main__":
    # Test query
    test_query = "What are the main product gaps for Spotify based on customer reviews?"
    asyncio.run(run_workflow(test_query))
