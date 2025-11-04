"""
Output Formatter module using DSPy.
"""

import dspy
from pydantic import BaseModel, Field


class OutputFormat(BaseModel):
    """Desired output format."""
    format_type: str = Field(..., description="Type of format: markdown, json, table, bullet_points, etc")
    reasoning: str = Field(..., description="Why this format is appropriate")


class OutputFormatSignature(dspy.Signature):
    """Determine the best output format for the query."""
    
    query = dspy.InputField(desc="User's question")
    
    format_type = dspy.OutputField(desc="Best format type: markdown, json, table, bullet_points, etc")
    reasoning = dspy.OutputField(desc="Why this format is appropriate")


class OutputFormatter(dspy.Module):
    """Determine the best output format for the response."""
    
    def __init__(self):
        super().__init__()
        self.format = dspy.ChainOfThought(OutputFormatSignature)
    
    def forward(self, query: str) -> OutputFormat:
        """
        Determine output format.
        
        Args:
            query: User's question
            
        Returns:
            OutputFormat with format type and reasoning
        """
        result = self.format(query=query)
        
        return OutputFormat(
            format_type=result.format_type,
            reasoning=result.reasoning
        )
