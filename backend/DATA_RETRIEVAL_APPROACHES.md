# Data Retrieval Approaches: Analysis & Alternatives

## Current Approach: Plan-Then-Execute

### How It Works
1. **Query Analysis** → Determine needs
2. **Retrieval Planning** → LLM generates SQL queries
3. **Execution** → Run all queries
4. **Answer Generation** → Process results

### Pros ✅
- **Explainable**: You can see the plan before execution
- **Debuggable**: Easy to log and inspect SQL queries
- **Flexible**: Can generate multiple queries for different aspects
- **Safe**: Can validate queries before execution
- **Auditable**: Full trace of what data was retrieved and why

### Cons ❌
- **Two LLM calls**: Query analysis + retrieval planning (slower, more expensive)
- **Over-fetching**: Might retrieve data that's not ultimately needed
- **No feedback loop**: Can't adjust queries based on initial results
- **Rigid**: All queries planned upfront without seeing data

---

## Alternative 1: Iterative Retrieval (Agentic Approach) ⭐ RECOMMENDED

### How It Works
```
1. Query Analysis → Determine needs
2. Initial Retrieval → Fetch broad dataset
3. LLM Analysis → "Do I have enough data? What's missing?"
4. Refinement Retrieval → Fetch additional specific data (if needed)
5. Answer Generation → Process all results
```

### Implementation Strategy
```python
class IterativeRetrievalAgent:
    async def retrieve_with_feedback(self, query, analysis):
        # Step 1: Initial broad retrieval
        initial_data = await self.broad_retrieval(query, analysis)
        
        # Step 2: LLM evaluates if more data is needed
        evaluation = await self.evaluate_data_sufficiency(query, initial_data)
        
        # Step 3: Refinement queries (if needed)
        if evaluation.needs_more_data:
            additional_data = await self.targeted_retrieval(
                query, 
                initial_data, 
                evaluation.missing_aspects
            )
            return self.merge_data(initial_data, additional_data)
        
        return initial_data
```

### Pros ✅
- **Adaptive**: Adjusts based on what's actually found
- **Efficient**: Only fetches what's needed
- **Smart**: Can handle "no results" scenarios gracefully
- **Better for exploration**: Good when you don't know what data exists
- **Reduces over-fetching**: Especially with NLP analysis

### Cons ❌
- **More LLM calls**: Could be 2-4 calls depending on iterations
- **Slower**: Sequential retrieval takes longer
- **Complex**: Harder to implement and debug
- **Unpredictable**: Number of queries varies

### When to Use
- ✅ Exploratory queries ("find gaps", "analyze patterns")
- ✅ When data availability is uncertain
- ✅ Complex multi-faceted analysis
- ❌ Simple direct queries ("show me reviews for Netflix")

---

## Alternative 2: Hybrid Approach (Smart Routing) ⭐⭐ BEST BALANCE

### How It Works
```
Query Analysis determines:
├─ Simple Query → Direct SQL (no planning)
├─ NLP Analysis → Single broad retrieval + NLP processing
└─ Complex Query → Plan-then-execute (current approach)
```

### Implementation Strategy
```python
async def smart_retrieval_router(query, analysis):
    if analysis.query_type == "simple_data":
        # Direct SQL - no planning needed
        return await direct_sql_retrieval(query, analysis)
    
    elif analysis.needs_nlp_analysis:
        # Single broad retrieval for NLP
        return await broad_retrieval_for_nlp(query, analysis)
    
    else:
        # Complex multi-query planning
        return await plan_and_execute(query, analysis)
```

### Pros ✅
- **Optimal for each case**: Uses best approach per query type
- **Faster for simple queries**: Skips unnecessary planning
- **Efficient for NLP**: Single retrieval + downstream processing
- **Flexible**: Can handle all query types
- **Cost-effective**: Fewer LLM calls for simple cases

### Cons ❌
- **More code paths**: Three different retrieval strategies
- **Routing logic**: Need good classification in query analysis

### When to Use
- ✅ Production systems with varied query types
- ✅ When you want to optimize for both speed and capability
- ✅ When cost optimization matters

---

## Alternative 3: Vector Search + Semantic Retrieval (Future)

### How It Works (with pgvector)
```
1. Query Analysis → Extract semantic intent
2. Vector Search → Find semantically similar reviews
3. Keyword Fallback → Traditional SQL for specific filters
4. Hybrid Ranking → Combine vector + keyword results
```

### Implementation Strategy
```python
async def semantic_retrieval(query, analysis):
    # Generate query embedding
    query_embedding = await embed_query(query)
    
    # Vector similarity search
    vector_results = await db.execute(f"""
        SELECT *, 
               text <=> '{query_embedding}' as similarity
        FROM user_review_feedback
        WHERE company_name = '{analysis.company}'
        ORDER BY similarity
        LIMIT 100
    """)
    
    # Optional: Combine with keyword filters
    if analysis.has_specific_filters:
        keyword_results = await keyword_search(query, analysis)
        return merge_and_rerank(vector_results, keyword_results)
    
    return vector_results
```

### Pros ✅
- **Semantic understanding**: Finds conceptually similar content
- **No keyword engineering**: No need for ILIKE patterns
- **Better for NLP**: Natural fit for gap detection
- **Handles synonyms**: "expensive" finds "costly", "pricey"
- **Single query**: Often just one vector search needed

### Cons ❌
- **Requires embeddings**: Need to pre-compute and store
- **Infrastructure**: pgvector extension required
- **Embedding costs**: OpenAI embedding API calls
- **Index maintenance**: Need to update embeddings for new data

### When to Use
- ✅ Semantic search ("find reviews about pricing issues")
- ✅ Gap detection (conceptual similarity)
- ✅ Large datasets where keyword matching fails
- ✅ When you have embedding infrastructure

---

## Alternative 4: Query Decomposition + Parallel Execution

### How It Works
```
1. Query Analysis → Break into sub-questions
2. Parallel Planning → Generate SQL for each sub-question
3. Parallel Execution → Run all queries simultaneously
4. Synthesis → Combine results
```

### Implementation Strategy
```python
async def parallel_retrieval(query, analysis):
    # Decompose into sub-questions
    sub_questions = await decompose_query(query)
    # e.g., ["What are low-rated reviews?", 
    #        "What features are mentioned?",
    #        "What's the sentiment trend?"]
    
    # Generate SQL for each in parallel
    sql_tasks = [
        generate_sql(sub_q, schema) 
        for sub_q in sub_questions
    ]
    sql_queries = await asyncio.gather(*sql_tasks)
    
    # Execute all in parallel
    data_tasks = [
        execute_query(sql) 
        for sql in sql_queries
    ]
    results = await asyncio.gather(*data_tasks)
    
    return combine_results(results, sub_questions)
```

### Pros ✅
- **Fast**: Parallel execution reduces latency
- **Modular**: Each sub-question handled independently
- **Scalable**: Easy to add more sub-questions
- **Clear**: Each query has specific purpose

### Cons ❌
- **Complexity**: More moving parts
- **Over-fetching**: Might retrieve overlapping data
- **Coordination**: Need to merge results intelligently

---

## Recommendation Matrix

| Query Type | Current | Iterative | Hybrid | Vector | Parallel |
|------------|---------|-----------|--------|--------|----------|
| Simple data query | ⚠️ Overkill | ❌ Too slow | ✅ Best | ❌ Overkill | ❌ Overkill |
| NLP gap analysis | ⚠️ Over-fetches | ✅ Good | ✅ Best | ⭐ Future best | ✅ Good |
| Complex multi-aspect | ✅ Good | ✅ Good | ✅ Best | ⚠️ Needs hybrid | ✅ Best |
| Exploratory | ⚠️ Rigid | ✅ Best | ✅ Good | ⭐ Excellent | ⚠️ Rigid |
| Performance | ⚠️ Medium | ❌ Slow | ✅ Fast | ✅ Fast | ⭐ Fastest |

---

## My Recommendation: Hybrid Approach + Vector (Phased)

### Phase 1: Implement Hybrid Routing (Now)
```python
# Immediate improvement - minimal code change
async def retrieve_data(query, analysis):
    if analysis.query_type == "simple_data":
        # Direct: "Show me Netflix reviews"
        return await simple_direct_query(query, analysis)
    
    elif analysis.needs_nlp_analysis:
        # Broad: "Find gaps in Netflix"
        return await broad_nlp_retrieval(query, analysis)
    
    else:
        # Complex: "Compare Netflix and Spotify gaps"
        return await plan_and_execute(query, analysis)
```

**Benefits**: 
- 40-60% faster for simple queries
- Better data efficiency for NLP queries
- Keeps current approach for complex cases

### Phase 2: Add Vector Search (When Ready)
```python
async def broad_nlp_retrieval(query, analysis):
    if has_vector_column(table):
        # Semantic search
        return await vector_search(query, analysis)
    else:
        # Fallback to broad SQL
        return await simple_broad_query(query, analysis)
```

**Benefits**:
- Seamless upgrade path
- Better semantic matching
- Eliminates keyword pattern issues

### Phase 3: Add Iterative Refinement (Optional)
For truly complex exploratory queries, add feedback loop:
```python
async def iterative_retrieval(query, analysis):
    data = await initial_retrieval(query, analysis)
    
    for iteration in range(max_iterations):
        evaluation = await evaluate_sufficiency(query, data)
        if evaluation.is_sufficient:
            break
        
        additional = await refine_retrieval(query, data, evaluation)
        data = merge(data, additional)
    
    return data
```

---

## Implementation Priority

### 🔥 High Priority (Do Now)
1. **Hybrid routing** - Easy win, big impact
2. **Simplify NLP retrieval** - Single broad query instead of multiple ILIKE patterns
3. **Add query validation** - Prevent bad SQL before execution

### 🎯 Medium Priority (Next Sprint)
1. **Parallel execution** - Speed up multi-query plans
2. **Query result caching** - Avoid re-fetching same data
3. **Adaptive limits** - Adjust LIMIT based on data availability

### 🚀 Future (When Vector Ready)
1. **Vector search integration** - Semantic retrieval
2. **Hybrid vector + keyword** - Best of both worlds
3. **Iterative refinement** - For complex exploratory queries

---

## Code Example: Hybrid Implementation

```python
# In workflow.py
@step
async def retrieve_data(self, ctx: Context, ev: RetrievalPlanEvent) -> DataRetrievedEvent:
    """Step 4: Execute data retrieval with smart routing."""
    logger.info("▶️  Step 4: Data Retrieval")
    
    # Smart routing based on query type
    if ev.analysis.query_type == "simple_data":
        retrieved_data = await self._simple_retrieval(ev)
    elif ev.analysis.needs_nlp_analysis:
        retrieved_data = await self._nlp_retrieval(ev)
    else:
        retrieved_data = await self._complex_retrieval(ev)
    
    return DataRetrievedEvent(...)

async def _simple_retrieval(self, ev):
    """Direct SQL for simple queries - no planning overhead."""
    # Generate single SQL query directly
    sql = await generate_simple_sql(ev.query, ev.analysis)
    return execute_single_query(sql)

async def _nlp_retrieval(self, ev):
    """Broad retrieval for NLP analysis."""
    # Single broad query - let NLP handle the rest
    sql = f"""
        SELECT * FROM user_review_feedback
        WHERE company_name = '{ev.analysis.company}'
        ORDER BY date DESC
        LIMIT 2000
    """
    return execute_single_query(sql, format="csv")

async def _complex_retrieval(self, ev):
    """Plan-then-execute for complex queries."""
    # Current approach - works well for complex cases
    return execute_retrieval_plan(ev.plan)
```

---

## Bottom Line

Your current approach is **solid but can be optimized**. The biggest wins:

1. **Add hybrid routing** → 40-60% faster for simple queries
2. **Simplify NLP retrieval** → Single broad query instead of multiple patterns
3. **Prepare for vector search** → Will be game-changer for semantic queries

The plan-then-execute approach is good for complex queries, but you're using it for everything. Smart routing gives you the best of all worlds.