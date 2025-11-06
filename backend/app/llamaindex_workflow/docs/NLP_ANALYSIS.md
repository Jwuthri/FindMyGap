# NLP Analysis Implementation

## Overview

The NLP analysis step is integrated into the LlamaIndex workflow and executes conditionally when `needs_nlp_analysis=True` in the query analysis.

## Architecture

### Flow

```
DataRetrievedEvent → nlp_analysis step → DataRetrievedEvent (with NLP results)
```

The step:
1. Checks if `analysis.needs_nlp_analysis` is True
2. If False, passes through the event unchanged
3. If True, invokes the NLP agent with retrieved data
4. Adds NLP results to the event's `retrieved_data`

### Components

#### 1. NLP Tools (`tools/nlp_tools.py`)

Four specialized tools that return **tool call specifications** (not actual analysis):

- **`compute_tfidf_tool`**: Find most important terms
  - Required: `dataset_name`, `text_column`
  - Optional: `top_n`, `min_df`, `max_df`, `ngram_range`
  - Use for: key terms, important words, topics

- **`cluster_reviews_tool`**: Group similar text by theme
  - Required: `dataset_name`, `text_column`
  - Optional: `num_clusters`, `method`, `id_column`, `include_metadata`
  - Use for: themes, topics, patterns, grouping

- **`analyze_sentiment_tool`**: Analyze sentiment and ratings
  - Required: `dataset_name`, `text_column`
  - Optional: `rating_column`, `include_distribution`, `group_by`
  - Use for: sentiment, ratings, satisfaction

- **`identify_features_tool`**: Extract feature requests and pain points
  - Required: `dataset_name`, `text_column`
  - Optional: `min_frequency`, `rating_column`, `id_column`, `extract_pain_points`, `extract_product_gaps`
  - Use for: gaps, missing features, requests

**Key Design**: Tools return specifications, not data. Actual data retrieval happens separately.

#### 2. NLP Agent (`agents/nlp_agent.py`)

A ReAct agent that:
- Receives the query, analysis type, and retrieved data info
- Selects appropriate NLP tool(s)
- Returns tool call specifications with parameters

**Input**:
```python
{
    "query": "Find product gaps for Netflix",
    "analysis": QueryAnalysis(...),
    "retrieved_data": {
        "data": {"user_reviews": [...], ...},
        "total_rows": 1500
    }
}
```

**Output**:
```python
{
    "tool_calls": [
        {
            "tool": "identify_features",
            "dataset_name": "user_reviews",
            "parameters": {
                "text_column": "review_text",
                "min_frequency": 2,
                "rating_column": "rating",
                "id_column": "id",
                "extract_pain_points": True,
                "extract_product_gaps": True
            }
        }
    ],
    "agent_response": "...",
    "reasoning": "..."
}
```

#### 3. Workflow Step (`workflow.py`)

The `nlp_analysis` step:

```python
@step
async def nlp_analysis(self, ctx: Context, ev: DataRetrievedEvent) -> DataRetrievedEvent:
    """Step 5: Perform NLP analysis if needed."""
    if not ev.analysis.needs_nlp_analysis:
        return ev  # Pass through
    
    nlp_results = await perform_nlp_analysis(
        query=ev.query,
        analysis=ev.analysis,
        retrieved_data=ev.retrieved_data
    )
    
    # Add results to event
    ev.retrieved_data['nlp_analysis'] = nlp_results
    return ev
```

## Usage Examples

### Example 1: Product Gaps

```python
query = "Find product gaps for Netflix"
analysis = QueryAnalysis(
    needs_nlp_analysis=True,
    analysis_type="gap_detection",
    company="Netflix"
)

# Agent will select: identify_features_tool
# Output: {
#   "tool": "identify_features",
#   "dataset_name": "user_reviews",
#   "parameters": {
#     "text_column": "review_text",
#     "min_frequency": 2,
#     "rating_column": "rating",
#     "extract_pain_points": True,
#     "extract_product_gaps": True
#   }
# }
```

### Example 2: Sentiment Analysis

```python
query = "Analyze sentiment in Spotify reviews"
analysis = QueryAnalysis(
    needs_nlp_analysis=True,
    analysis_type="sentiment",
    company="Spotify"
)

# Agent will select: analyze_sentiment_tool
# Output: {
#   "tool": "analyze_sentiment",
#   "dataset_name": "feedback_data",
#   "parameters": {
#     "text_column": "comment",
#     "rating_column": "score",
#     "include_distribution": True
#   }
# }
```

### Example 3: Theme Clustering

```python
query = "What are the main themes in Notion reviews?"
analysis = QueryAnalysis(
    needs_nlp_analysis=True,
    analysis_type="clustering",
    company="Notion"
)

# Agent will select: cluster_reviews_tool
# Output: {
#   "tool": "cluster_reviews",
#   "dataset_name": "reviews",
#   "parameters": {
#     "text_column": "text",
#     "num_clusters": 5,
#     "method": "kmeans",
#     "id_column": "review_id",
#     "include_metadata": ["stars", "date"]
#   }
# }
```

## Tool Selection Logic

The agent uses this mapping:

| Query Intent | Analysis Type | Selected Tool |
|-------------|---------------|---------------|
| Product gaps, missing features | `gap_detection` | `identify_features` |
| Sentiment, ratings | `sentiment` | `analyze_sentiment` |
| Themes, topics, patterns | `clustering` | `cluster_reviews` |
| Key terms, important words | `tfidf` | `compute_tfidf` |

## Data Flow

1. **Query Analysis** → Determines `needs_nlp_analysis=True`
2. **Data Retrieval** → Fetches data (e.g., user reviews)
3. **NLP Analysis** → Agent selects tool and parameters
4. **Tool Execution** (separate) → Uses dataset_name to retrieve and analyze
5. **Answer Generation** → Incorporates NLP results

## Key Design Decisions

### Why Tool Calls Return Specifications?

- **Separation of Concerns**: Agent decides WHAT to analyze, not HOW
- **Flexibility**: Actual data retrieval can be optimized separately
- **Reusability**: Same tool specs can be used with different data sources
- **Testability**: Easy to test agent logic without data dependencies

### Why Not Pass Data Directly?

- **Token Efficiency**: Avoid sending large datasets to LLM
- **Scalability**: Works with datasets of any size
- **Performance**: Data retrieval can be parallelized
- **Clarity**: Clear separation between planning and execution

## Testing

Run the example:

```bash
cd backend
python -m app.llamaindex_workflow.nlp_example
```

This demonstrates:
- Different query types
- Tool selection logic
- Parameter configuration
- Agent reasoning

## Integration Points

The NLP analysis results are available in:
- `DataRetrievedEvent.retrieved_data['nlp_analysis']`
- Downstream steps (e.g., answer generation)
- Final workflow output

## Future Enhancements

1. **Multi-tool execution**: Agent can select multiple tools
2. **Tool chaining**: Output of one tool feeds into another
3. **Custom parameters**: User-specified analysis parameters
4. **Result caching**: Cache NLP results for similar queries
5. **Streaming results**: Stream analysis results as they complete
