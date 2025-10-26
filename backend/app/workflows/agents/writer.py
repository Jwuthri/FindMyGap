from agno.agent import Agent
from agno.models.openai import OpenAIChat


def create_markdown_writer_agent(model: OpenAIChat) -> Agent:
    """Writer specialized in markdown reports."""
    return Agent(
        name="Markdown Writer",
        role="Create well-formatted markdown reports",
        model=model,
        instructions=[
            "Format output as clean, readable markdown",
            "Use headers, lists, and emphasis appropriately",
            "Include data references and numbers",
            "Be comprehensive but concise"
        ],
        markdown=True,
        debug_mode=False
    )


def create_table_writer_agent(model: OpenAIChat) -> Agent:
    """Writer specialized in tables and structured data."""
    return Agent(
        name="Table Writer",
        role="Create structured tables and dataframes",
        model=model,
        instructions=[
            "Format output as markdown tables",
            "Include clear column headers",
            "Align data properly",
            "Add totals/summaries if relevant"
        ],
        markdown=True,
        debug_mode=False
    )


def create_chart_writer_agent(model: OpenAIChat) -> Agent:
    """Writer specialized in visualization specifications."""
    return Agent(
        name="Chart Writer",
        role="Generate visualization specifications",
        model=model,
        instructions=[
            "Provide clear chart specifications",
            "Include chart type, data, labels",
            "Suggest appropriate visualization",
            "Explain what the chart shows"
        ],
        markdown=True,
        debug_mode=False
    )


def create_json_writer_agent(model: OpenAIChat) -> Agent:
    """Writer specialized in JSON output."""
    return Agent(
        name="JSON Writer",
        role="Create structured JSON responses",
        model=model,
        instructions=[
            "Format output as valid JSON",
            "Include all relevant data",
            "Use clear key names",
            "Add metadata if helpful"
        ],
        markdown=False,
        debug_mode=False
    )
