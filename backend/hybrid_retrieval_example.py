#!/usr/bin/env python3
"""
Example implementation of hybrid retrieval approach.
This shows how to route queries to the optimal retrieval strategy.
"""

from typing import Dict, Any, Optional
from enum import Enum


class RetrievalStrategy(Enum):
    """Different retrieval strategies."""
    SIMPLE_DIRECT = "simple_direct"  # Direct SQL, no planning
    BROAD_NLP = "broad_nlp"  # Single broad query for NLP
    COMPLEX_PLANNED = "complex_planned"  # Multi-query planning
    VECTOR_SEMANTIC = "vector_semantic"  # Future: Vector search


class HybridRetrievalRouter:
    """Routes queries to optimal retrieval strategy."""
    
    def __init__(self, has_vector_support: bool = False):
        self.has_vector_support = has_vector_support
    
    def determine_strategy(self, query_analysis) -> RetrievalStrategy:
        """
        Determine the best retrieval strategy based on query analysis.
        
        Decision tree:
        1. Simple data query → SIMPLE_DIRECT
        2. NLP analysis needed → BROAD_NLP (or VECTOR_SEMANTIC if available)
        3. Complex multi-aspect → COMPLEX_PLANNED
        """
        # Check for vector search eligibility
        if (self.has_vector_support and 
            query_analysis.needs_nlp_analysis and
            query_analysis.analysis_type in ["gap_detection", "sentiment", "clustering"]):
            return RetrievalStrategy.VECTOR_SEMANTIC
        
        # Simple data queries - direct SQL
        if query_analysis.query_type == "simple_data" and not query_analysis.needs_nlp_analysis:
            return RetrievalStrategy.SIMPLE_DIRECT
        
        # NLP analysis - broad retrieval
        if query_analysis.needs_nlp_analysis:
            return RetrievalStrategy.BROAD_NLP
        
        # Complex queries - planned approach
        return RetrievalStrategy.COMPLEX_PLANNED
    
    async def retrieve(self, query: str, query_analysis, table_schemas: Dict[str, Any]):
        """Execute retrieval using the optimal strategy."""
        strategy = self.determine_strategy(query_analysis)
        
        print(f"🎯 Selected strategy: {strategy.value}")
        
        if strategy == RetrievalStrategy.SIMPLE_DIRECT:
            return await self._simple_direct_retrieval(query, query_analysis, table_schemas)
        
        elif strategy == RetrievalStrategy.BROAD_NLP:
            return await self._broad_nlp_retrieval(query, query_analysis, table_schemas)
        
        elif strategy == RetrievalStrategy.VECTOR_SEMANTIC:
            return await self._vector_semantic_retrieval(query, query_analysis, table_schemas)
        
        else:  # COMPLEX_PLANNED
            return await self._complex_planned_retrieval(query, query_analysis, table_schemas)
    
    async def _simple_direct_retrieval(self, query, analysis, schemas):
        """
        Strategy 1: Simple Direct SQL
        
        Use case: "Show me Netflix reviews with rating below 3"
        Approach: Generate single SQL query directly, no planning overhead
        """
        print("📊 Simple Direct Retrieval")
        
        # Generate SQL directly without planning step
        sql = self._generate_simple_sql(query, analysis)
        
        return {
            "strategy": "simple_direct",
            "sql_queries": [sql],
            "format": "json",
            "reasoning": "Direct SQL query for simple data retrieval"
        }
    
    async def _broad_nlp_retrieval(self, query, analysis, schemas):
        """
        Strategy 2: Broad NLP Retrieval
        
        Use case: "Find product gaps for Netflix"
        Approach: Single broad query, let NLP handle pattern detection
        """
        print("🧠 Broad NLP Retrieval")
        
        company = analysis.company or "Unknown"
        
        # Single broad query - no keyword filtering
        sql = f"""
            SELECT id, rating, text, source, date, author
            FROM user_review_feedback
            WHERE company_name = '{company}'
            ORDER BY date DESC
            LIMIT 2000
        """
        
        return {
            "strategy": "broad_nlp",
            "sql_queries": [sql],
            "format": "csv",  # CSV better for NLP processing
            "reasoning": f"Broad retrieval of {company} reviews for downstream NLP analysis"
        }
    
    async def _vector_semantic_retrieval(self, query, analysis, schemas):
        """
        Strategy 3: Vector Semantic Search (Future)
        
        Use case: "Find reviews about pricing issues"
        Approach: Semantic similarity search using embeddings
        """
        print("🔍 Vector Semantic Retrieval")
        
        company = analysis.company or "Unknown"
        
        # Vector similarity search
        # Note: Requires pre-computed embeddings in 'text_embedding' column
        sql = f"""
            SELECT id, rating, text, source, date, author,
                   text_embedding <=> '[query_embedding]' as similarity
            FROM user_review_feedback
            WHERE company_name = '{company}'
            ORDER BY similarity ASC
            LIMIT 500
        """
        
        return {
            "strategy": "vector_semantic",
            "sql_queries": [sql],
            "format": "csv",
            "reasoning": f"Semantic search for {company} reviews using vector similarity"
        }
    
    async def _complex_planned_retrieval(self, query, analysis, schemas):
        """
        Strategy 4: Complex Planned Retrieval
        
        Use case: "Compare Netflix and Spotify feature gaps"
        Approach: Multi-query planning with LLM
        """
        print("🎯 Complex Planned Retrieval")
        
        # Use existing plan_retrieval function
        from app.llamaindex_workflow.agents import plan_retrieval
        
        plan = await plan_retrieval(query, schemas, analysis)
        
        return {
            "strategy": "complex_planned",
            "sql_queries": [q.query for q in plan.sql_queries],
            "format": "json",
            "reasoning": plan.reasoning
        }
    
    def _generate_simple_sql(self, query: str, analysis) -> str:
        """Generate simple SQL for direct queries."""
        company = analysis.company or "Unknown"
        
        # Basic template - could be enhanced with simple LLM call
        sql = f"""
            SELECT *
            FROM user_review_feedback
            WHERE company_name = '{company}'
            ORDER BY date DESC
            LIMIT 1000
        """
        
        return sql


# Example usage
async def demonstrate_hybrid_routing():
    """Show how different queries route to different strategies."""
    
    router = HybridRetrievalRouter(has_vector_support=False)
    
    scenarios = [
        {
            "query": "Show me Netflix reviews",
            "analysis": type('obj', (object,), {
                'query_type': 'simple_data',
                'needs_nlp_analysis': False,
                'company': 'Netflix',
                'analysis_type': 'none'
            })(),
            "expected": RetrievalStrategy.SIMPLE_DIRECT
        },
        {
            "query": "Find product gaps for Netflix",
            "analysis": type('obj', (object,), {
                'query_type': 'analysis',
                'needs_nlp_analysis': True,
                'company': 'Netflix',
                'analysis_type': 'gap_detection'
            })(),
            "expected": RetrievalStrategy.BROAD_NLP
        },
        {
            "query": "Compare Netflix and Spotify feature requests",
            "analysis": type('obj', (object,), {
                'query_type': 'complex',
                'needs_nlp_analysis': True,
                'company': 'Netflix',
                'analysis_type': 'comparison'
            })(),
            "expected": RetrievalStrategy.COMPLEX_PLANNED
        }
    ]
    
    print("Hybrid Retrieval Routing Examples")
    print("=" * 60)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. Query: {scenario['query']}")
        strategy = router.determine_strategy(scenario['analysis'])
        print(f"   Strategy: {strategy.value}")
        print(f"   Expected: {scenario['expected'].value}")
        print(f"   Match: {'✅' if strategy == scenario['expected'] else '❌'}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demonstrate_hybrid_routing())