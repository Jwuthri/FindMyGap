"""
Answer Writer module using DSPy.
"""

from typing import Any, Dict, Optional

import dspy
from pydantic import BaseModel, Field


class Answer(BaseModel):
    """Final answer output."""
    answer: str = Field(..., description="The formatted answer")


class AnswerWritingSignature(dspy.Signature):
    """Write a comprehensive answer based on query and data."""
    
    query = dspy.InputField(desc="User's question")
    query_analysis = dspy.InputField(desc="Analysis of the query")
    output_format = dspy.InputField(desc="Desired output format")
    data = dspy.InputField(desc="Retrieved data (if any)")
    
    answer = dspy.OutputField(desc="Comprehensive formatted answer")


class AnswerWriter(dspy.Module):
    """Generate final formatted answer."""
    
    def __init__(self):
        super().__init__()
        self.write = dspy.ChainOfThought(AnswerWritingSignature)
    
    def forward(
        self,
        query: str,
        analysis: Any,
        output_format: Any,
        data: Optional[Dict[str, Any]] = None
    ) -> Answer:
        """
        Write the final answer.
        
        Args:
            query: User's question
            analysis: Query analysis output
            output_format: Desired output format
            data: Retrieved data (if any)
            
        Returns:
            Answer with formatted response
        """
        # Format inputs for the signature
        query_analysis_str = f"Type: {analysis.query_type}, Reasoning: {analysis.reasoning}"
        output_format_str = f"Format: {output_format.format_type}, Reasoning: {output_format.reasoning}"
        data_str = str(data) if data else "No data retrieved"
        
        result = self.write(
            query=query,
            query_analysis=query_analysis_str,
            output_format=output_format_str,
            data=data_str
        )
        
        return Answer(answer=result.answer)
