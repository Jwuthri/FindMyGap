from typing import AsyncIterator
from textwrap import dedent

from agno.workflow.types import StepInput, StepOutput

# ============================================================================
# WORKFLOW STEP FUNCTIONS
# ============================================================================

async def query_analysis_step(step_input: StepInput) -> AsyncIterator[StepOutput]:
    """
    Step 1: Analyze query to determine execution path.
    Always runs.
    """
    user_query = step_input.input
    
    content = dedent(f"""\
        Analyze this user query and determine the workflow execution path:
        
        Query: {user_query}
        
        Determine:
        - Does this need data retrieval from the database?
        - Does this need NLP analysis?
        - What company is mentioned (if any)?
        - What type of query is this?
        
        Provide your analysis as structured output.
        """)
    
    yield StepOutput(content=content)


async def data_retrieval_prep(step_input: StepInput) -> AsyncIterator[StepOutput]:
    """
    Prepare input for data retrieval step.
    Extracts company and parameters from query analysis.
    """
    original_query = step_input.input
    # Previous step is the Query Analyzer agent's response
    analysis_result = step_input.previous_step_content
    
    content = dedent(f"""\
        Retrieve review data based on this analysis.
        
        Original query: {original_query}
        Query Analysis: {analysis_result}
        
        Instructions:
        - Extract the company name from the analysis
        - Start with 100 reviews as default limit
        - Use the most appropriate retrieval tool
        - Confirm once data is retrieved
        """)
    
    yield StepOutput(content=content)


async def data_sufficiency_prep(step_input: StepInput) -> AsyncIterator[StepOutput]:
    """
    Prepare input for data sufficiency check.
    """
    original_query = step_input.input
    retrieved_data = step_input.previous_step_content
    
    content = dedent(f"""\
        Evaluate if the retrieved data is sufficient for the planned NLP analysis.
        
        Original query: {original_query}
        Retrieved data (sample): {retrieved_data[:800]}...
        
        Consider:
        - What NLP analysis will be performed (gap analysis, clustering, sentiment, etc)?
        - Is the data quantity adequate for that analysis?
        - For clustering: need 20-30+ reviews
        - For gap analysis: need 30-50+ reviews
        - For sentiment: need 20+ reviews
        
        If insufficient, recommend 2x or 3x current count (max 500).
        Provide structured evaluation.
        """)
    
    yield StepOutput(content=content)


async def data_retrieval_retry_step(step_input: StepInput) -> AsyncIterator[StepOutput]:
    """
    Step 3b: Retry data retrieval with increased limit.
    Conditional: Only runs if sufficiency check indicates insufficient data.
    """
    content = dedent(f"""\
        Data was insufficient. Retrieve more data with increased limit.
        
        Previous evaluation: {step_input.previous_step_content}
        
        Fetch additional reviews with the recommended count.
        """)
    
    yield StepOutput(content=content)


async def nlp_analysis_prep(step_input: StepInput) -> AsyncIterator[StepOutput]:
    """
    Prepare input for NLP analysis step.
    """
    original_query = step_input.input
    data_context = step_input.previous_step_content
    
    content = dedent(f"""\
        Perform NLP analysis on the retrieved data to answer the user's query.
        
        Original query: {original_query}
        Available data context: {data_context[:800]}...
        
        Instructions:
        - Select the most appropriate NLP analysis tool
        - For "product gaps" or "what's missing": use analyze_product_gaps
        - For "feature requests": use identify_feature_requests
        - For "themes" or "clustering": use cluster_similar_reviews
        - For "sentiment" or "rating analysis": use analyze_sentiment_distribution
        - For "key terms" or "important words": use compute_tfidf
        
        Execute the analysis and summarize key findings.
        """)
    
    yield StepOutput(content=content)


async def format_detection_prep(step_input: StepInput) -> AsyncIterator[StepOutput]:
    """
    Prepare input for output format detection.
    """
    original_query = step_input.input
    analysis_results = step_input.previous_step_content
    
    content = dedent(f"""\
        Determine the best output format for presenting this answer.
        
        Query: {original_query}
        Analysis results (sample): {analysis_results[:600]}...
        
        Consider:
        - If user explicitly asked for a table/chart, honor that
        - For comparisons and structured data: table
        - For distributions and trends: chart
        - For detailed explanations and insights: markdown
        - For API/structured export: json
        
        Use the determine_best_output_format tool.
        """)
    
    yield StepOutput(content=content)


async def answer_writing_prep(step_input: StepInput) -> AsyncIterator[StepOutput]:
    """
    Prepare input for the answer writer team.
    """
    original_query = step_input.input
    all_context = step_input.previous_step_content
    
    content = dedent(f"""\
        Create a comprehensive, well-formatted final answer for the user.
        
        Original query: {original_query}
        
        All context and analysis results:
        {all_context}
        
        Instructions:
        - Review the recommended output format from the previous step
        - Delegate to the appropriate writer agent (Markdown/Table/Chart/JSON)
        - Ensure the answer is complete, accurate, and well-structured
        - Include all relevant insights, data, and recommendations
        - Be clear and actionable
        """)
    
    yield StepOutput(content=content)
