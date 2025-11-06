#!/usr/bin/env python3
"""
Test script to demonstrate the adapted retrieval planner behavior.
"""

import asyncio
from app.llamaindex_workflow.agents.base import QueryAnalysis
from app.llamaindex_workflow.agents.retrieval_planner import plan_retrieval

# Mock table schemas
MOCK_SCHEMAS = {
    "user_review_feedback": """
    CREATE TABLE user_review_feedback (
        id SERIAL PRIMARY KEY,
        company_name VARCHAR(255),
        rating INTEGER,
        text TEXT,
        source VARCHAR(100),
        date TIMESTAMP,
        author VARCHAR(255)
    );
    """
}

async def test_nlp_mode():
    """Test retrieval planning when NLP analysis is needed."""
    print("🧠 Testing NLP Analysis Mode (should generate simple queries)")
    
    query = "Find product gaps for Netflix based on user reviews"
    
    # Simulate query analysis that needs NLP
    analysis = QueryAnalysis(
        needs_data_retrieval=True,
        needs_nlp_analysis=True,  # This should trigger simple query mode
        company="Netflix",
        query_type="analysis",
        reasoning="User wants gap analysis requiring NLP processing",
        analysis_type="gap_detection"
    )
    
    plan = await plan_retrieval(query, MOCK_SCHEMAS, analysis)
    
    print(f"Generated {len(plan.sql_queries)} queries:")
    for i, sql_query in enumerate(plan.sql_queries, 1):
        print(f"\n{i}. Purpose: {sql_query.purpose}")
        print(f"   Query: {sql_query.query}")
    
    print(f"\nReasoning: {plan.reasoning}")
    return plan

async def test_direct_mode():
    """Test retrieval planning when no NLP analysis is needed."""
    print("\n" + "="*60)
    print("🎯 Testing Direct Query Mode (can use complex queries)")
    
    query = "Show me Netflix reviews with ratings below 3 that mention specific features"
    
    # Simulate query analysis that doesn't need NLP
    analysis = QueryAnalysis(
        needs_data_retrieval=True,
        needs_nlp_analysis=False,  # This should allow complex queries
        company="Netflix",
        query_type="data_only",
        reasoning="User wants specific data without analysis",
        analysis_type="none"
    )
    
    plan = await plan_retrieval(query, MOCK_SCHEMAS, analysis)
    
    print(f"Generated {len(plan.sql_queries)} queries:")
    for i, sql_query in enumerate(plan.sql_queries, 1):
        print(f"\n{i}. Purpose: {sql_query.purpose}")
        print(f"   Query: {sql_query.query}")
    
    print(f"\nReasoning: {plan.reasoning}")
    return plan

async def main():
    """Run both test scenarios."""
    print("Testing Adaptive Retrieval Planner")
    print("="*60)
    
    nlp_plan = await test_nlp_mode()
    direct_plan = await test_direct_mode()
    
    print("\n" + "="*60)
    print("📊 COMPARISON SUMMARY:")
    print(f"NLP Mode: {len(nlp_plan.sql_queries)} queries")
    print(f"Direct Mode: {len(direct_plan.sql_queries)} queries")
    
    # Check for complexity differences
    nlp_has_like = any("LIKE" in q.query or "ILIKE" in q.query for q in nlp_plan.sql_queries)
    direct_has_like = any("LIKE" in q.query or "ILIKE" in q.query for q in direct_plan.sql_queries)
    
    print(f"NLP Mode uses LIKE patterns: {nlp_has_like}")
    print(f"Direct Mode uses LIKE patterns: {direct_has_like}")
    
    # Note about data formats
    print(f"\nData Format Selection:")
    print(f"NLP Mode would use: CSV format (better for text processing)")
    print(f"Direct Mode would use: JSON format (structured data)")

if __name__ == "__main__":
    asyncio.run(main())