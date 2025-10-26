from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat


class OutputFormatRecommendation(BaseModel):
    primary_format: str = Field(..., description="bar_chart, line_chart, pie_chart, table, markdown, json, etc")
    alternative_format: str = Field(..., description="bar_chart, line_chart, pie_chart, table, markdown, json, etc")
    reasoning: str = Field(..., description="Reasoning for the recommendation, less than 20 words")


def create_output_format_agent(model: OpenAIChat) -> Agent:
    """
    Determine best output format for the answer using output schema.
    """
    return Agent(
        name="Output Format Detection Agent",
        role="Determine optimal output format",
        model=model,
        description="""Analyze the query to determine the best output format.
        
        Formats:
        - markdown: General answers, explanations, reports
        - table: Structured data, lists, comparisons
        - chart: Distributions, trends, visualizations
        - json: API responses, structured exports
        """,
        instructions=[
            "Analyze the question and recommend the best output format",
            "Consider what format would be clearest for the user",
            "If user asks for table/chart explicitly, honor that",
            "If asking about distribution/comparison → bar_chart or pie_chart",
            "If asking about trends over time → line_chart",
            "For detailed lists → table",
            "Default to markdown for general questions",
            "Be concise in reasoning (under 20 words)",
            "",
            "Examples for product gap analysis from reviews:",
            "- 'What product gaps exist?' → markdown (explanatory report)",
            "- 'Show top 5 missing features' → table (structured list)",
            "- 'Compare sentiment across products' → bar_chart (comparison)",
            "- 'Review volume over time' → line_chart (trend)",
            "- 'Distribution of complaint types' → pie_chart (breakdown)",
            "- 'List all negative reviews about pricing' → table (structured data)",
            "- 'Sentiment distribution' → pie_chart or bar_chart (category breakdown)"
        ],
        output_schema=OutputFormatRecommendation,
        markdown=False,
        debug_mode=False
    )
