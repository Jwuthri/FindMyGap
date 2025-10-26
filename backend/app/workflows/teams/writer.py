from agno.team import Team
from agno.models.openai import OpenAIChat

from app.workflows.agents.writer import create_markdown_writer_agent, create_table_writer_agent, create_chart_writer_agent, create_json_writer_agent


def create_answer_writer_team(model: OpenAIChat) -> Team:
    """
    Team of specialized writers for different output formats.
    """
    markdown_writer = create_markdown_writer_agent(model)
    table_writer = create_table_writer_agent(model)
    chart_writer = create_chart_writer_agent(model)
    json_writer = create_json_writer_agent(model)
    
    return Team(
        name="Answer Writer Team",
        members=[markdown_writer, table_writer, chart_writer, json_writer],
        model=model,
        description="""Coordinate writers to format the final answer based on detected output format.
        
        Writers:
        - Markdown Writer: For reports and explanations
        - Table Writer: For structured tabular data
        - Chart Writer: For visualizations
        - JSON Writer: For API/structured responses
        
        Select the writer that matches the recommended format.
        """,
        instructions=[
            "Check the recommended output format from previous step",
            "Delegate to the appropriate writer agent",
            "Ensure the answer is well-formatted and complete",
            "Include all relevant data and insights"
        ],
        markdown=True,
        debug_mode=False
    )
