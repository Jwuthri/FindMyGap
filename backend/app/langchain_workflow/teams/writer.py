"""Writer team using LangGraph multi-agent collaboration."""
from typing import Annotated, Literal

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import create_react_agent

from app.langchain_workflow.agents.writer import (
    create_markdown_writer_agent,
    create_table_writer_agent,
    create_chart_writer_agent,
    create_json_writer_agent
)


def create_answer_writer_team(model: ChatOpenAI):
    """
    Create a team of specialized writers using LangGraph.
    The team coordinator routes to the appropriate writer based on format.
    """
    # Create writer agents
    markdown_writer = create_markdown_writer_agent(model)
    table_writer = create_table_writer_agent(model)
    chart_writer = create_chart_writer_agent(model)
    json_writer = create_json_writer_agent(model)
    
    # Define the workflow state
    class WriterTeamState(MessagesState):
        """State for the writer team workflow."""
        format_type: str = "markdown"
        final_output: str = ""
    
    # Define workflow
    workflow = StateGraph(WriterTeamState)
    
    # Router function to select writer
    def route_to_writer(state: WriterTeamState) -> Literal["markdown", "table", "chart", "json"]:
        """Route to appropriate writer based on format."""
        format_type = state.get("format_type", "markdown").lower()
        
        if "table" in format_type:
            return "table"
        elif "chart" in format_type or "pie" in format_type or "bar" in format_type or "line" in format_type:
            return "chart"
        elif "json" in format_type:
            return "json"
        else:
            return "markdown"
    
    # Writer node functions
    def markdown_writer_node(state: WriterTeamState):
        """Execute markdown writer."""
        messages = state["messages"]
        last_message = messages[-1].content if messages else ""
        
        result = markdown_writer.invoke({"input": last_message})
        return {
            "messages": [AIMessage(content=result.content)],
            "final_output": result.content
        }
    
    def table_writer_node(state: WriterTeamState):
        """Execute table writer."""
        messages = state["messages"]
        last_message = messages[-1].content if messages else ""
        
        result = table_writer.invoke({"input": last_message})
        return {
            "messages": [AIMessage(content=result.content)],
            "final_output": result.content
        }
    
    def chart_writer_node(state: WriterTeamState):
        """Execute chart writer."""
        messages = state["messages"]
        last_message = messages[-1].content if messages else ""
        
        result = chart_writer.invoke({"input": last_message})
        return {
            "messages": [AIMessage(content=result.content)],
            "final_output": result.content
        }
    
    def json_writer_node(state: WriterTeamState):
        """Execute JSON writer."""
        messages = state["messages"]
        last_message = messages[-1].content if messages else ""
        
        result = json_writer.invoke({"input": last_message})
        return {
            "messages": [AIMessage(content=result.content)],
            "final_output": result.content
        }
    
    # Add nodes
    workflow.add_node("markdown", markdown_writer_node)
    workflow.add_node("table", table_writer_node)
    workflow.add_node("chart", chart_writer_node)
    workflow.add_node("json", json_writer_node)
    
    # Add conditional routing from START
    workflow.add_conditional_edges(
        START,
        route_to_writer,
        {
            "markdown": "markdown",
            "table": "table",
            "chart": "chart",
            "json": "json"
        }
    )
    
    # All writers go to END
    workflow.add_edge("markdown", END)
    workflow.add_edge("table", END)
    workflow.add_edge("chart", END)
    workflow.add_edge("json", END)
    
    return workflow.compile()

