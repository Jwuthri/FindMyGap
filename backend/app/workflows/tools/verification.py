from pydantic import BaseModel, Field

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool

from app.config import SETTINGS

# ============================================================================
# VERIFICATION TOOLS
# ============================================================================

class AccuracyCheck(BaseModel):
    has_data_reference: bool = Field(..., description="Whether the answer has data references")
    has_numbers: bool = Field(..., description="Whether the answer has numbers/quantitative data")
    reasonable_length: bool = Field(..., description="Whether the answer has a reasonable length")
    answers_question: bool = Field(..., description="Whether the answer answers the question")

class VerificationResult(BaseModel):
    accuracy_score: float = Field(..., description="The accuracy score of the answer")
    checks: AccuracyCheck = Field(..., description="The checks for the answer")
    verified: bool = Field(..., description="Whether the answer is verified")
    recommendations: list[str] = Field(..., description="The recommendations for the answer")


@tool(requires_confirmation=False)
def verify_answer_accuracy(answer: str, original_data: str, question: str) -> str:
    """
    Use LLM to verify the accuracy of an answer against original data.
    
    Args:
        answer: Generated answer
        original_data: Source data used
        question: Original question
    
    Returns:
        JSON string with verification results
    """
    model = OpenAIChat(id="gpt-5-mini", api_key=SETTINGS.OPENAI_API_KEY)
    
    verification_agent = Agent(
        name="Answer Verifier",
        model=model,
        instructions=[
            "Verify the answer against the original data",
            "Check for accuracy, data references, and completeness",
            "Provide specific recommendations for improvement"
        ],
        response_model=VerificationResult,
        markdown=False
    )
    
    prompt = f"""Verify this answer against the source data.

Question: {question}

Answer: {answer}

Source Data: {original_data}

Check if the answer:
- Has data references (mentions reviews, customers, feedback)
- Has numbers/quantitative data
- Has reasonable length (50-2000 chars)
- Actually answers the question

Provide accuracy score (0-100), verification checks, and recommendations."""
    
    response = verification_agent.run(prompt)
    return response.content.model_dump_json(indent=2)
