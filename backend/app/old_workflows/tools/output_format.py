from pydantic import BaseModel, Field

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool

from app.config import SETTINGS

# ============================================================================
# OUTPUT FORMAT DETECTION & VISUALIZATION
# ============================================================================

class OutputFormatRecommendation(BaseModel):
    primary_format: str = Field(..., description="bar_chart, line_chart, pie_chart, table, markdown, json, etc")
    alternative_format: str = Field(..., description="bar_chart, line_chart, pie_chart, table, markdown, json, etc")
    reasoning: str = Field(..., description="Reasoning for the recommendation, less than 20 words")


@tool(requires_confirmation=False, stop_after_tool_call=True)
def determine_best_output_format(question: str, data_type: str = "reviews") -> str:
    """
    Use LLM to determine the best output format for a given question.
    
    Args:
        question: User's question
        data_type: Type of data being analyzed
    
    Returns:
        JSON string with recommended output format
    """
    model = OpenAIChat(id="gpt-5-mini", api_key=SETTINGS.OPENAI_API_KEY)
    
    format_agent = Agent(
        name="Format Analyzer",
        model=model,
        instructions=[
            "Analyze the question and recommend the best output format",
            "Consider what format would be clearest for the user",
            "Available formats: table, bar_chart, line_chart, pie_chart, markdown, json"
        ],
        output_schema=OutputFormatRecommendation,
        markdown=False
    )
    
    prompt = f"""Determine the best output format for this question about {data_type}:

Question: {question}

Consider:
- If user asks for "table" or "show as table" → recommend table
- If asking about distribution/comparison → bar_chart or pie_chart
- If asking about trends over time → line_chart
- For general questions → markdown
- For detailed lists → table"""
    
    response = format_agent.run(prompt)
    
    return response.content
