"""
API endpoints for Find My Gaps analysis.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, AsyncGenerator
import json

from agno.agent import RunEvent
from agno.team import TeamRunEvent

from app.agents.teams import create_findmygaps_team
from app.config import SETTINGS

router = APIRouter(prefix="/analysis", tags=["analysis"])


class AnalysisRequest(BaseModel):
    """Request model for gap analysis."""
    question: str = Field(..., description="Question about the product/company")
    company: Optional[str] = Field(None, description="Company to analyze")
    user_id: Optional[str] = Field(None, description="User ID")
    session_id: str = Field(default="default", description="Session ID")


async def stream_analysis(
    question: str,
    user_id: str = "anonymous",
    session_id: str = "default"
) -> AsyncGenerator[str, None]:
    """Stream team analysis with proper event handling."""
    try:
        team = create_findmygaps_team(
            api_key=SETTINGS.OPENAI_API_KEY,
            db_file="memory.db",
            user_id=user_id
        )
        
        yield f"data: {json.dumps({'type': 'start', 'question': question})}\n\n"
        
        async for event in team.arun(
            question,
            stream=True,
            stream_intermediate_steps=True,
            stream_member_events=True
        ):
            if hasattr(event, 'event'):
                # Team delegation
                if event.event == TeamRunEvent.tool_call_started:
                    if hasattr(event.tool, 'tool_name') and event.tool.tool_name == "delegate_task_to_member":
                        args = event.tool.tool_args or {}
                        yield f"data: {json.dumps({'type': 'delegation', 'agent': args.get('member_id', 'unknown'), 'task': args.get('task', '')[:100]})}\n\n"
                
                # Agent tool calls started
                elif event.event == RunEvent.tool_call_started:
                    agent_name = getattr(event, 'agent_name', 'Agent')
                    yield f"data: {json.dumps({'type': 'tool_call', 'agent': agent_name, 'tool': event.tool.tool_name})}\n\n"
                
                # Agent tool calls completed - SEND THE ACTUAL DATA
                elif event.event == RunEvent.tool_call_completed:
                    agent_name = getattr(event, 'agent_name', 'Agent')
                    tool_name = event.tool.tool_name
                    
                    # Send data retrieval results to frontend
                    if tool_name in ["retrieve_reviews", "filter_reviews_by_rating", "filter_reviews_by_source", "search_reviews_by_keyword"]:
                        # Parse the JSON result
                        try:
                            data = json.loads(event.tool_result) if isinstance(event.tool_result, str) else event.tool_result
                            yield f"data: {json.dumps({'type': 'data', 'tool': tool_name, 'agent': agent_name, 'data': data})}\n\n"
                        except:
                            pass
                    
                    # Send analysis results
                    elif tool_name in ["compute_tfidf", "analyze_sentiment_distribution", "identify_feature_requests", "cluster_similar_reviews", "analyze_product_gaps"]:
                        try:
                            data = json.loads(event.tool_result) if isinstance(event.tool_result, str) else event.tool_result
                            yield f"data: {json.dumps({'type': 'analysis', 'tool': tool_name, 'agent': agent_name, 'data': data})}\n\n"
                        except:
                            pass
                    
                    # Send Python code execution
                    elif tool_name == "execute_python_analysis":
                        try:
                            # Get the code from tool args
                            code = event.tool.tool_args.get('python_code', '')
                            result = json.loads(event.tool_result) if isinstance(event.tool_result, str) else event.tool_result
                            yield f"data: {json.dumps({'type': 'code_execution', 'tool': tool_name, 'agent': agent_name, 'code': code, 'result': result})}\n\n"
                        except:
                            pass
                
                # Content streaming
                elif event.event == RunEvent.run_content:
                    yield f"data: {json.dumps({'type': 'content', 'text': event.content})}\n\n"
                
                # Completion
                elif event.event == RunEvent.run_completed:
                    yield f"data: {json.dumps({'type': 'complete'})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


@router.post("/chat")
async def chat(request: AnalysisRequest):
    """
    Chat with the Find My Gaps team.
    
    The team will automatically:
    - Triage your request to the right agents
    - Retrieve relevant data
    - Perform analysis
    - Determine best output format
    - Verify answer accuracy
    """
    if not SETTINGS.OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    return StreamingResponse(
        stream_analysis(
            question=request.question,
            user_id=request.user_id or "anonymous",
            session_id=request.session_id
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "openai_configured": bool(SETTINGS.OPENAI_API_KEY)
    }
