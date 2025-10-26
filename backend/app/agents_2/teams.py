# """
# Find My Gaps - Multi-Agent Team System

# Architecture:
# - Triage Agent: Routes requests to appropriate specialized agents
# - Data Agent: Retrieves and manages review data
# - ML Agent: Performs TF-IDF, clustering, and statistical analysis
# - Visualization Agent: Determines best output format and generates visualizations
# - Verification Agent: Checks answer accuracy and quality
# """

# import json
# from typing import Optional, List, Dict, Any
# from collections import Counter
# import math
# import io
# import base64
# from pydantic import BaseModel, Field

# from agno.team import Team
# from agno.agent import Agent, RunEvent
# from agno.models.openai import OpenAIChat
# from agno.db.sqlite import SqliteDb
# from agno.memory import MemoryManager
# from agno.tools import tool
# # Note: Guardrails import commented out - may not be available in all agno versions
# # from agno.guardrails import PIIDetectionGuardrail, PromptInjectionGuardrail

# from app.agents.mock_data import (
#     get_reviews,
#     get_all_companies,
#     get_reviews_by_rating,
#     get_reviews_by_source,
#     search_reviews
# )

# from app.config import SETTINGS

# # Data science imports
# import pandas as pd
# import numpy as np


# # ============================================================================
# # PYDANTIC SCHEMAS FOR STRUCTURED OUTPUTS
# # ============================================================================
    
# # Common stopwords to exclude
# STOPWORDS = {
#     'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'as', 'are', 
#     'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does',
#     'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
#     'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
#     'it', 'we', 'they', 'them', 'their', 'what', 'which', 'who', 'when',
#     'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
#     'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
#     'same', 'so', 'than', 'too', 'very', 'just', 'but', 'for', 'with',
#     'about', 'from', 'into', 'through', 'during', 'before', 'after'
# }

# class FeatureRequest(BaseModel):
#     category: str
#     description: str
#     frequency: int
#     examples: List[str]

# class PainPoint(BaseModel):
#     category: str
#     description: str
#     severity: str = Field(..., description="high, medium, or low")
#     examples: List[str]

# class ProductGapItem(BaseModel):
#     gap: str
#     impact: str
#     mentioned_by: int

# class FeatureAnalysisResult(BaseModel):
#     feature_requests: List[FeatureRequest]
#     pain_points: List[PainPoint]
#     product_gaps: List[ProductGapItem]

# class ProductGap(BaseModel):
#     gap_name: str
#     description: str
#     impact: str = Field(..., description="high, medium, or low")
#     frequency: str
#     evidence: List[str]
#     recommended_action: str
#     priority_score: int = Field(..., ge=1, le=10)

# class ProductGapsResult(BaseModel):
#     gaps: List[ProductGap]
#     summary: str
#     competitive_mentions: List[str]

# class ReviewCluster(BaseModel):
#     theme: str
#     description: str
#     review_ids: List[int]
#     key_insights: List[str]
#     sentiment: str = Field(..., description="positive, negative, or mixed")

# class ClusteringResult(BaseModel):
#     clusters: List[ReviewCluster]

# class OutputFormatRecommendation(BaseModel):
#     question: str
#     primary_format: str = Field(..., description="bar_chart, line_chart, pie_chart, table, markdown, json, etc")
#     alternative_formats: List[str]
#     reasoning: str

# class AccuracyCheck(BaseModel):
#     has_data_reference: bool
#     has_numbers: bool
#     reasonable_length: bool
#     answers_question: bool

# class VerificationResult(BaseModel):
#     accuracy_score: float
#     checks: AccuracyCheck
#     verified: bool
#     recommendations: List[str]

# # ============================================================================
# # DATA RETRIEVAL TOOLS
# # ============================================================================

# @tool(requires_confirmation=False)
# def retrieve_reviews(company: str, limit: int = 100) -> str:
#     """
#     Retrieve customer reviews for a company.
    
#     Args:
#         company: Company name (e.g., "spotify", "notion", "slack")
#         limit: Maximum number of reviews to retrieve
    
#     Returns:
#         JSON string with reviews
#     """
#     reviews = get_reviews(company, limit)
#     return json.dumps({
#         "company": company,
#         "total_reviews": len(reviews),
#         "reviews": reviews
#     }, indent=2)


# @tool(requires_confirmation=False)
# def filter_reviews_by_rating(company: str, min_rating: int, max_rating: int) -> str:
#     """
#     Filter reviews by rating range.
    
#     Args:
#         company: Company name
#         min_rating: Minimum rating (1-5)
#         max_rating: Maximum rating (1-5)
    
#     Returns:
#         JSON string with filtered reviews
#     """
#     reviews = get_reviews_by_rating(company, min_rating, max_rating)
#     return json.dumps({
#         "company": company,
#         "rating_range": f"{min_rating}-{max_rating}",
#         "total_reviews": len(reviews),
#         "reviews": reviews
#     }, indent=2)


# @tool(requires_confirmation=False)
# def filter_reviews_by_source(company: str, source: str) -> str:
#     """
#     Filter reviews by source platform.
    
#     Args:
#         company: Company name
#         source: Source platform (app_store, reddit, trustpilot)
    
#     Returns:
#         JSON string with filtered reviews
#     """
#     reviews = get_reviews_by_source(company, source)
#     return json.dumps({
#         "company": company,
#         "source": source,
#         "total_reviews": len(reviews),
#         "reviews": reviews
#     }, indent=2)


# @tool(requires_confirmation=False)
# def search_reviews_by_keyword(company: str, keyword: str) -> str:
#     """
#     Search reviews containing specific keyword.
    
#     Args:
#         company: Company name
#         keyword: Search keyword
    
#     Returns:
#         JSON string with matching reviews
#     """
#     reviews = search_reviews(company, keyword)
#     return json.dumps({
#         "company": company,
#         "keyword": keyword,
#         "total_matches": len(reviews),
#         "reviews": reviews
#     }, indent=2)


# @tool(requires_confirmation=False)
# def list_available_companies() -> str:
#     """
#     List all companies with available review data.
    
#     Returns:
#         JSON string with company list
#     """
#     companies = get_all_companies()
#     return json.dumps({
#         "total_companies": len(companies),
#         "companies": companies
#     }, indent=2)


# # ============================================================================
# # ML & ANALYSIS TOOLS
# # ============================================================================

# @tool(requires_confirmation=False)
# def compute_tfidf(company: str, top_n: int = 10) -> str:
#     """
#     Compute TF-IDF to find most important terms in reviews.
    
#     Args:
#         company: Company name (spotify, notion, slack)
#         top_n: How many top terms to return (default 10)
    
#     Returns:
#         JSON with top terms and TF-IDF scores
#     """
#     reviews = get_reviews(company)
    
#     if not reviews:
#         return json.dumps({"error": f"No reviews for {company}"})
    
#     # Get review texts
#     documents = [r["text"].lower() for r in reviews]
    
#     # Build word frequencies
#     word_doc_count = {}
#     word_freq_per_doc = []
    
#     for doc in documents:
#         words = [w for w in doc.split() if len(w) > 3 and w not in STOPWORDS]
#         word_freq = Counter(words)
#         word_freq_per_doc.append(word_freq)
        
#         for word in set(words):
#             word_doc_count[word] = word_doc_count.get(word, 0) + 1
    
#     # Calculate TF-IDF
#     num_docs = len(documents)
#     tfidf_scores = {}
    
#     for word, doc_count in word_doc_count.items():
#         if doc_count < 2:  # Skip words in only 1 doc
#             continue
            
#         idf = math.log(num_docs / doc_count)
#         total_tf = sum(freq.get(word, 0) for freq in word_freq_per_doc)
#         avg_tf = total_tf / num_docs
#         tfidf_scores[word] = avg_tf * idf
    
#     # Get top N
#     top_terms = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
#     return json.dumps({
#         "company": company,
#         "reviews_analyzed": num_docs,
#         "top_terms": [
#             {"term": term, "score": round(score, 3)}
#             for term, score in top_terms
#         ]
#     })


# @tool(requires_confirmation=False)
# def analyze_sentiment_distribution(company: str) -> str:
#     """
#     Analyze rating distribution and sentiment patterns.
    
#     Args:
#         company: Company name
    
#     Returns:
#         JSON string with sentiment analysis
#     """
#     reviews = get_reviews(company)
    
#     if not reviews:
#         return json.dumps({"error": "No reviews found"})
    
#     # Rating distribution
#     rating_counts = Counter(r["rating"] for r in reviews)
#     total = len(reviews)
    
#     # Sentiment categories
#     positive = sum(rating_counts.get(r, 0) for r in [4, 5])
#     neutral = rating_counts.get(3, 0)
#     negative = sum(rating_counts.get(r, 0) for r in [1, 2])
    
#     # Source distribution
#     source_counts = Counter(r["source"] for r in reviews)
    
#     # Average rating
#     avg_rating = sum(r["rating"] for r in reviews) / total
    
#     return json.dumps({
#         "company": company,
#         "total_reviews": total,
#         "average_rating": round(avg_rating, 2),
#         "sentiment_distribution": {
#             "positive": positive,
#             "neutral": neutral,
#             "negative": negative,
#             "positive_percent": round((positive / total) * 100, 1),
#             "negative_percent": round((negative / total) * 100, 1)
#         },
#         "rating_breakdown": dict(rating_counts),
#         "source_breakdown": dict(source_counts)
#     }, indent=2)


# @tool(requires_confirmation=False)
# def identify_feature_requests(company: str) -> str:
#     """
#     Use LLM to identify feature requests, pain points, and product gaps from reviews.
    
#     Args:
#         company: Company name
    
#     Returns:
#         JSON string with analyzed feature requests and gaps
#     """
#     reviews = get_reviews(company)
    
#     if not reviews:
#         return json.dumps({"error": "No reviews found"})
    
#     # Create a focused agent for feature extraction
#     model = OpenAIChat(id="gpt-5-mini", api_key=SETTINGS.OPENAI_API_KEY)
    
#     analysis_agent = Agent(
#         name="Feature Analysis Agent",
#         model=model,
#         instructions=[
#             "Analyze customer reviews to identify feature requests, pain points, and product gaps",
#             "Group similar requests together",
#             "Quantify frequency and impact"
#         ],
#         response_model=FeatureAnalysisResult,
#         markdown=False
#     )
    
#     # Prepare review data
#     review_texts = "\n\n".join([
#         f"Review {i+1} (Rating: {r['rating']}/5, {r['date']}):\n{r['text']}"
#         for i, r in enumerate(reviews[:500])  # Limit to avoid token issues
#     ])
    
#     prompt = f"""Analyze these {company} reviews and identify:

# 1. Feature requests (what users want added)
# 2. Pain points (what frustrates users)
# 3. Product gaps (missing functionality vs competitors)

# Reviews:
# {review_texts}"""
    
#     response = analysis_agent.run(prompt)
#     return response.content.model_dump_json(indent=2)


# @tool(requires_confirmation=False)
# def analyze_product_gaps(company: str, focus_on_negative: bool = True) -> str:
#     """
#     Deep LLM-powered analysis to identify critical product gaps.
    
#     Args:
#         company: Company name
#         focus_on_negative: Whether to focus on negative reviews (1-3 stars)
    
#     Returns:
#         JSON with prioritized product gaps
#     """
#     if focus_on_negative:
#         reviews = get_reviews_by_rating(company, 1, 3)
#     else:
#         reviews = get_reviews(company)
    
#     if not reviews:
#         return json.dumps({"error": "No reviews found"})
    
#     model = OpenAIChat(id="gpt-5-mini", api_key=SETTINGS.OPENAI_API_KEY)
    
#     gap_analyzer = Agent(
#         name="Product Gap Analyzer",
#         model=model,
#         instructions=[
#             "Identify critical product gaps from customer feedback",
#             "Prioritize by impact and frequency",
#             "Compare with competitor mentions",
#             "Suggest actionable improvements"
#         ],
#         response_model=ProductGapsResult,
#         markdown=False
#     )
    
#     review_data = "\n\n".join([
#         f"Review {i+1} | {r['rating']}★ | {r['date']} | {r['source']}\n{r['text']}"
#         for i, r in enumerate(reviews[:40])
#     ])

#     prompt = f"""Analyze these {company} customer reviews to identify the TOP 3-5 PRODUCT GAPS.

# A product gap is:
# - Missing feature that customers want
# - Poor implementation vs competitors
# - Unmet user need or expectation

# Reviews:
# {review_data}

# Focus on gaps with highest impact + frequency."""
    
#     response = gap_analyzer.run(prompt)
#     result = response.content.model_dump()
#     result["company"] = company
#     result["reviews_analyzed"] = len(reviews)
#     return json.dumps(result, indent=2)


# @tool(requires_confirmation=False)
# def cluster_similar_reviews(company: str, num_clusters: int = 5) -> str:
#     """
#     Use LLM to intelligently group reviews by theme/topic.
    
#     Args:
#         company: Company name
#         num_clusters: Number of topic clusters to identify
    
#     Returns:
#         JSON string with thematic clusters
#     """
#     reviews = get_reviews(company)
    
#     if not reviews:
#         return json.dumps({"error": "No reviews found"})
    
#     model = OpenAIChat(id="gpt-5-mini", api_key=SETTINGS.OPENAI_API_KEY)
    
#     clustering_agent = Agent(
#         name="Review Clustering Agent",
#         model=model,
#         instructions=[
#             f"Group reviews into {num_clusters} thematic clusters",
#             "Identify the main topic/theme of each cluster",
#             "Assign reviews to the most relevant cluster",
#             "Provide clear cluster names and descriptions"
#         ],
#         response_model=ClusteringResult,
#         markdown=False
#     )
    
#     # Prepare condensed review data
#     review_summary = "\n".join([
#         f"{i+1}. [{r['rating']}★] {r['text'][:100]}..."
#         for i, r in enumerate(reviews[:50])
#     ])
    
#     prompt = f"""Analyze these {company} customer reviews and group them into {num_clusters} thematic clusters.

# Reviews:
# {review_summary}"""
    
#     response = clustering_agent.run(prompt)
#     result = response.content.model_dump()
#     result["company"] = company
#     result["total_reviews_analyzed"] = len(reviews)
#     return json.dumps(result, indent=2)


# # ============================================================================
# # DATA SCIENCE TOOLS - DYNAMIC CODE EXECUTION
# # ============================================================================

# @tool(requires_confirmation=False)
# def execute_python_analysis(company: str, python_code: str) -> str:
#     """
#     Execute arbitrary Python code for data analysis on review data.
    
#     The code has access to:
#     - df: pandas DataFrame with review data (columns: id, rating, text, date, source, metadata)
#     - pd: pandas
#     - np: numpy
#     - sklearn: scikit-learn (import as needed)
#     - scipy: scipy
#     - All standard Python libraries
    
#     The code should store results in a variable called 'result' which will be returned.
    
#     Args:
#         company: Company name
#         python_code: Python code to execute. Must set 'result' variable with output.
    
#     Returns:
#         JSON with execution results
    
#     Example:
#         python_code = '''
# # Calculate correlation between rating and text length
# df['text_length'] = df['text'].str.len()
# corr = df[['rating', 'text_length']].corr()
# result = corr.to_dict()
# '''
#     """
#     reviews = get_reviews(company)
    
#     if not reviews:
#         return json.dumps({"error": "No reviews found"})
    
#     try:
#         # Prepare DataFrame
#         df = pd.DataFrame(reviews)
        
#         # Create execution namespace with available libraries
#         namespace = {
#             'df': df,
#             'pd': pd,
#             'np': np,
#             'json': json,
#             'result': None
#         }
        
#         # Execute the code
#         exec(python_code, namespace)
        
#         # Get the result
#         result = namespace.get('result')
        
#         if result is None:
#             return json.dumps({
#                 "error": "Code did not set 'result' variable",
#                 "company": company
#             })
        
#         # Convert result to JSON-serializable format
#         if isinstance(result, pd.DataFrame):
#             result = result.to_dict(orient='records')
#         elif isinstance(result, pd.Series):
#             result = result.to_dict()
#         elif isinstance(result, np.ndarray):
#             result = result.tolist()
#         elif hasattr(result, 'tolist'):
#             result = result.tolist()
        
#         return json.dumps({
#             "company": company,
#             "total_reviews": len(df),
#             "result": result
#         }, indent=2)
    
#     except Exception as e:
#         return json.dumps({
#             "error": f"Code execution failed: {str(e)}",
#             "company": company,
#             "code": python_code
#         })


# # ============================================================================
# # OUTPUT FORMAT DETECTION & VISUALIZATION
# # ============================================================================

# @tool(requires_confirmation=False)
# def determine_best_output_format(question: str, data_type: str = "reviews") -> str:
#     """
#     Use LLM to determine the best output format for a given question.
    
#     Args:
#         question: User's question
#         data_type: Type of data being analyzed
    
#     Returns:
#         JSON string with recommended output format
#     """
#     model = OpenAIChat(id="gpt-5-mini", api_key=SETTINGS.OPENAI_API_KEY)
    
#     format_agent = Agent(
#         name="Format Analyzer",
#         model=model,
#         instructions=[
#             "Analyze the question and recommend the best output format",
#             "Consider what format would be clearest for the user",
#             "Available formats: table, bar_chart, line_chart, pie_chart, markdown, json"
#         ],
#         response_model=OutputFormatRecommendation,
#         markdown=False
#     )
    
#     prompt = f"""Determine the best output format for this question about {data_type}:

# Question: {question}

# Consider:
# - If user asks for "table" or "show as table" → recommend table
# - If asking about distribution/comparison → bar_chart or pie_chart
# - If asking about trends over time → line_chart
# - For general questions → markdown
# - For detailed lists → table"""
    
#     response = format_agent.run(prompt)
#     return response.content.model_dump_json(indent=2)


# @tool(requires_confirmation=False)
# def generate_visualization_spec(data_summary: str, format_type: str, title: str) -> str:
#     """
#     Generate visualization specification for given data.
    
#     Args:
#         data_summary: Summary of data to visualize
#         format_type: Type of visualization (bar_chart, pie_chart, etc.)
#         title: Title of the visualization

#     Returns:
#         JSON string with visualization spec
#     """
#     return json.dumps({
#         "format": format_type,
#         "spec": {
#             "title": title,
#             "description": f"Visualization as {format_type}",
#             "data_source": data_summary[:100],
#             "config": {
#                 "responsive": True,
#                 "animated": True,
#                 "theme": "modern"
#             }
#         },
#         "implementation_note": f"Frontend should render this as {format_type}"
#     }, indent=2)


# # ============================================================================
# # VERIFICATION TOOLS
# # ============================================================================

# @tool(requires_confirmation=False)
# def verify_answer_accuracy(answer: str, original_data: str, question: str) -> str:
#     """
#     Use LLM to verify the accuracy of an answer against original data.
    
#     Args:
#         answer: Generated answer
#         original_data: Source data used
#         question: Original question
    
#     Returns:
#         JSON string with verification results
#     """
#     model = OpenAIChat(id="gpt-5-mini", api_key=SETTINGS.OPENAI_API_KEY)
    
#     verification_agent = Agent(
#         name="Answer Verifier",
#         model=model,
#         instructions=[
#             "Verify the answer against the original data",
#             "Check for accuracy, data references, and completeness",
#             "Provide specific recommendations for improvement"
#         ],
#         response_model=VerificationResult,
#         markdown=False
#     )
    
#     prompt = f"""Verify this answer against the source data.

# Question: {question}

# Answer: {answer}

# Source Data: {original_data}

# Check if the answer:
# - Has data references (mentions reviews, customers, feedback)
# - Has numbers/quantitative data
# - Has reasonable length (50-2000 chars)
# - Actually answers the question

# Provide accuracy score (0-100), verification checks, and recommendations."""
    
#     response = verification_agent.run(prompt)
#     return response.content.model_dump_json(indent=2)


# # ============================================================================
# # SPECIALIZED AGENTS
# # ============================================================================

# def create_triage_agent(model: OpenAIChat, db: Optional[SqliteDb] = None) -> Agent:
#     """Triage agent routes requests to appropriate specialized agents."""
#     return Agent(
#         name="Triage Agent",
#         role="Quickly route requests and coordinate execution",
#         model=model,
#         description="""You coordinate the Find My Gaps team. Route requests fast and get results.
        
#         Available agents:
#         - Data Agent: Gets reviews (use for "show", "get", "fetch" requests)
#         - ML Agent: Analysis (use for TF-IDF, sentiment, clustering, feature requests)
#         - Visualization Agent: Output format (use when format matters)
        
#         DON'T explain or plan extensively. Just delegate and execute.""",
#         instructions=[
#             "Quickly identify what the user wants",
#             "Delegate immediately to the right agent(s)",
#             "No lengthy explanations or planning",
#             "Get results, don't theorize",
#             "Be concise and action-oriented"
#         ],
#         tools=[
#             list_available_companies
#         ],
#         # db=db,
#         markdown=False,
#         debug_mode=False
#     )


# def create_data_agent(model: OpenAIChat, db: Optional[SqliteDb] = None) -> Agent:
#     """Data agent retrieves and manages review data."""
#     return Agent(
#         name="Data Agent",
#         role="Get review data fast",
#         model=model,
#         description="""Get reviews. Use the tool and confirm. Don't echo the data back.""",
#         instructions=[
#             "Use the tool that matches the request",
#             "After getting data, just say 'Retrieved X reviews for Y' - don't output the full JSON",
#             "The coordinator will see the tool result directly",
#             "Keep your response brief - just confirmation"
#         ],
#         tools=[
#             retrieve_reviews,
#             filter_reviews_by_rating,
#             filter_reviews_by_source,
#             search_reviews_by_keyword,
#             list_available_companies,
#             determine_best_output_format
#         ],
#         # db=db,
#         markdown=False,
#         debug_mode=False
#     )


# def create_ml_agent(model: OpenAIChat, db: Optional[SqliteDb] = None) -> Agent:
#     """ML agent performs AI-powered analysis on customer feedback."""
    
#     return Agent(
#         name="ML Agent",
#         role="AI-powered customer feedback analyst",
#         model=model,
#         description="""Analyze customer feedback using AI. Tools available:
#         - compute_tfidf: Statistical term importance
#         - analyze_sentiment_distribution: Rating/sentiment breakdown
#         - identify_feature_requests: Extract feature requests and pain points
#         - cluster_similar_reviews: Group reviews by theme
#         - analyze_product_gaps: Deep analysis of product gaps (best for "what are the gaps" questions)
        
#         Choose the right tool for the question.""",
#         instructions=[
#             "Pick the most relevant analysis tool for the question",
#             "For 'product gaps' or 'what's missing', use analyze_product_gaps",
#             "For 'feature requests', use identify_feature_requests",
#             "For 'group by topic', use cluster_similar_reviews",
#             "Trust tool results - don't retry the same tool with the same arguments",
#             "Summarize key findings concisely"
#         ],
#         tools=[
#             compute_tfidf,
#             analyze_sentiment_distribution,
#             identify_feature_requests,
#             cluster_similar_reviews,
#             analyze_product_gaps,
#             determine_best_output_format
#         ],
#         # db=db,
#         markdown=False,
#         debug_mode=False
#     )


# def create_visualization_agent(model: OpenAIChat, db: Optional[SqliteDb] = None) -> Agent:
#     """Visualization agent determines best output format."""
#     return Agent(
#         name="Visualization Agent",
#         role="Pick output format",
#         model=model,
#         description="""Determine best format (chart/table/markdown) and specify it. Quick.""",
#         instructions=[
#             "Decide the best format",
#             "Create the spec if needed",
#             "Be brief"
#         ],
#         tools=[
#             determine_best_output_format,
#             generate_visualization_spec
#         ],
#         # db=db,
#         markdown=False,
#         debug_mode=False
#     )


# def create_verification_agent(model: OpenAIChat, db: Optional[SqliteDb] = None) -> Agent:
#     """Verification agent checks answer quality and accuracy."""
#     return Agent(
#         name="Verification Agent",
#         role="Verify accuracy and quality of answers",
#         model=model,
#         description="""You are the quality assurance specialist for Find My Gaps.
        
#         Your responsibilities:
#         - Verify answers against source data
#         - Check for accuracy and completeness
#         - Ensure proper citations
#         - Validate quantitative claims
        
#         Be thorough and objective in your verification.
#         """,
#         instructions=[
#             "Cross-reference answers with source data",
#             "Check all numerical claims",
#             "Verify logical consistency",
#             "Flag any unsupported statements",
#             "Provide specific feedback"
#         ],
#         tools=[
#             verify_answer_accuracy
#         ],
#         # db=db,
#         markdown=True,
#         debug_mode=False
#     )


# def create_data_science_agent(model: OpenAIChat, db: Optional[SqliteDb] = None) -> Agent:
#     """Data science agent writes and executes Python code for analysis."""
#     return Agent(
#         name="Data Science Agent",
#         role="Python data scientist - writes and executes pandas/sklearn/scipy code",
#         model=model,
#         description="""You write and execute Python code to analyze review data.
        
#         You have access to a DataFrame called 'df' with columns:
#         - id, rating, text, date, source, metadata
        
#         Available libraries:
#         - pandas (pd)
#         - numpy (np)
#         - sklearn (import as needed)
#         - scipy (import as needed)
        
#         Write Python code to:
#         - Calculate statistics, correlations
#         - Run ML clustering (KMeans, DBSCAN, etc)
#         - Perform time series analysis
#         - Detect outliers
#         - Any custom analysis
        
#         IMPORTANT: Set your result in a variable called 'result'. This will be returned to the user.""",
#         instructions=[
#             "Write complete, executable Python code",
#             "Always set 'result' variable with your output",
#             "Use df for the review DataFrame",
#             "Import sklearn/scipy as needed in your code",
#             "Handle errors gracefully",
#             "Keep code clean and commented",
#             "Convert pandas/numpy objects to dicts/lists for result"
#         ],
#         tools=[
#             execute_python_analysis
#         ],
#         # db=db,
#         markdown=False,
#         debug_mode=False
#     )


# # ============================================================================
# # FIND MY GAPS TEAM
# # ============================================================================

# def create_findmygaps_team(
#     api_key: str,
#     db_file: str = "memory.db",
#     user_id: Optional[str] = None
# ) -> Team:
#     """
#     Create the Find My Gaps analysis team with proper architecture.
    
#     Args:
#         api_key: OpenAI API key
#         db_file: SQLite database path
#         user_id: User ID for session tracking
    
#     Returns:
#         Configured Team instance
#     """
#     model = OpenAIChat(id="gpt-5-mini", api_key=api_key)
    
#     db = SqliteDb(db_file=db_file)
#     memory_manager = MemoryManager(db=db, model=model)

#     # Create specialized agents (no triage - direct delegation)
#     data = create_data_agent(model, db)
#     ml = create_ml_agent(model, db)
#     data_science = create_data_science_agent(model, db)
#     visualization = create_visualization_agent(model, db)
#     # verification = create_verification_agent(model, db)    
#     # Create team - coordinator delegates directly to specialists
#     team = Team(
#         name="Find My Gaps Analysis Team",
#         members=[data, ml, data_science, visualization],
#         model=model,
#         description="""You coordinate specialists to analyze customer feedback.
        
#         IMPORTANT: When you delegate a task, YOU receive the tool result directly.
#         Don't ask the agent to return or repeat data - you already have it.
        
#         Specialists:
#         - Data Agent: retrieves reviews
#         - ML Agent: AI-powered semantic analysis (TF-IDF, sentiment, feature extraction, clustering)
#         - Data Science Agent: writes and executes custom Python code for ANY analysis (pandas/sklearn/scipy)
#         - Visualization Agent: output formatting
        
#         Choose the right specialist:
#         - For data retrieval → Data Agent
#         - For semantic/LLM insights → ML Agent  
#         - For statistical/ML/custom analysis → Data Science Agent (most flexible, can do anything)
#         - For formatting output → Visualization Agent
        
#         Data Science Agent is your Swiss Army knife - it can write Python code on the fly for any analysis.
        
#         Workflow: Delegate → Get tool result → Use it in your answer.""",
#         instructions=[
#             "Delegate to the right specialist",
#             "When a specialist calls a tool, YOU get the result automatically",
#             "Use tool results directly in your final answer",
#             "NEVER delegate again to ask for the same data",
#             "Present the data/analysis directly to the user"
#         ],
#         # db=db,
#         memory_manager=memory_manager,
#         enable_agentic_memory=True,
#         add_history_to_context=True,
#         num_history_runs=5,
#         user_id=user_id or "default_user",
#         markdown=True,
#         debug_mode=False,
#         # Note: Guardrails commented out - may not be available in all agno versions
#         # pre_hooks=[
#         #     PIIDetectionGuardrail(mask_pii=True),
#         #     PromptInjectionGuardrail()
#         # ]
#     )
    
#     return team

