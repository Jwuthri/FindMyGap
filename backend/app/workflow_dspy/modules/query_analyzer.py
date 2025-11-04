"""
Query Analyzer module using DSPy.
"""

from typing import Optional

import dspy
from pydantic import BaseModel, Field


class QueryAnalysisOutput(BaseModel):
    """Structured output for query analysis."""
    needs_data_retrieval: bool = Field(..., description="Whether to retrieve review data")
    needs_nlp_analysis: bool = Field(..., description="Whether to perform NLP analysis")
    company: Optional[str] = Field(None, description="Company name if applicable")
    query_type: str = Field(..., description="Type of query: data_only, analysis, general, etc")
    reasoning: str = Field(..., description="Brief explanation of routing decision")
    analysis_type: str = Field(..., description="What type of analysis is needed")


class QueryAnalysisSignature(dspy.Signature):
    """Analyze user query to determine execution path."""
    
    query = dspy.InputField(desc="User's question")
    
    needs_data_retrieval = dspy.OutputField(desc="Whether data retrieval is needed (true/false)")
    needs_nlp_analysis = dspy.OutputField(desc="Whether NLP analysis is needed (true/false)")
    company = dspy.OutputField(desc="Company name if mentioned, otherwise 'None'")
    query_type = dspy.OutputField(desc="Type of query: data_only, analysis, general, etc")
    reasoning = dspy.OutputField(desc="Brief explanation of routing decision")
    analysis_type = dspy.OutputField(desc="Type of analysis needed: TFIDF, clustering, sentiment, etc")


class QueryAnalyzer(dspy.Module):
    """Analyze queries to determine workflow execution path."""
    
    def __init__(self):
        super().__init__()
        self.analyze = dspy.ChainOfThought(QueryAnalysisSignature)
    
    def forward(self, query: str) -> QueryAnalysisOutput:
        """
        Analyze the query and return structured output.
        
        Args:
            query: User's question
            
        Returns:
            QueryAnalysisOutput with routing decisions
        """
        result = self.analyze(query=query)
        
        return QueryAnalysisOutput(
            needs_data_retrieval=result.needs_data_retrieval.lower() in ['true', 'yes', '1'],
            needs_nlp_analysis=result.needs_nlp_analysis.lower() in ['true', 'yes', '1'],
            company=result.company if result.company.lower() != 'none' else None,
            query_type=result.query_type,
            reasoning=result.reasoning,
            analysis_type=result.analysis_type
        )
