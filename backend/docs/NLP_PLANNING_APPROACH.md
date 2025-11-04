# NLP Analysis Planning Approach

## Overview

The NLP analysis now uses a **Plan-Execute** pattern where:
1. A **Planner Agent** decides which tools to use on which datasets
2. An **Executor Agent** runs the tools with the pre-fetched data
3. No data fetching happens during analysis (fast + cheap)

## Architecture

### Data Flow

```
Retrieved Data (from DataRetrieval step)
    ↓
    ├── recent_reviews (JSON list)
    ├── dedup_reviews (JSON list)
    ├── rating_distribution (JSON list)
    ├── rating_by_source (JSON list)
    └── reviews_time_series (JSON list)
    ↓
NLP Planner Agent
    ↓
Analysis Plan
    ├── Task 1: analyze_review_text_data on dedup_reviews
    ├── Task 2: cluster_reviews_by_theme on dedup_reviews
    ├── Task 3: analyze_rating_distribution on rating_distribution
    └── Task 4: analyze_time_series_trends on reviews_time_series
    ↓
NLP Executor Agent
    ↓
Comprehensive Analysis Results
```

## Components

### 1. Data-Aware Tools (`nlp_data_aware.py`)

Tools that operate on pre-fetched JSON data:

- **analyze_review_text_data**: Extract insights from review text (accepts optional focus_areas parameter)
- **cluster_reviews_by_theme**: Group reviews into thematic clusters
- **analyze_rating_distribution**: Sentiment and rating analysis
- **analyze_time_series_trends**: Review volume trends over time

Each tool:
- Accepts JSON data as a string or object parameter
- Parses the data internally (handles string, dict, or list)
- Returns JSON results
- Never fetches data from external sources
- Generic and flexible - not limited to product gaps

### 2. NLP Planner Agent (`nlp_planner.py`)

Creates an execution plan based on:
- User query intent
- Available datasets
- Tool capabilities

**Output Schema:**
```python
class AnalysisPlan(BaseModel):
    tasks: list[AnalysisTask]  # Ordered list of analysis tasks
    summary: str  # Strategy summary
```

**Example Plan:**
```json
{
  "tasks": [
    {
      "tool_name": "analyze_review_text_data",
      "dataset_key": "dedup_reviews",
      "parameters": {},
      "rationale": "Extract feature requests from deduplicated reviews"
    },
    {
      "tool_name": "analyze_rating_distribution",
      "dataset_key": "rating_distribution",
      "parameters": {},
      "rationale": "Understand overall sentiment patterns"
    }
  ],
  "summary": "Two-phase analysis: extract qualitative insights, then quantify sentiment"
}
```

### 3. NLP Executor Agent (`nlp_executor.py`)

Executes the plan by:
- Receiving the plan + datasets
- Calling each tool with the appropriate dataset
- Combining results into comprehensive analysis
- Summarizing key findings

## Workflow Integration

In `product_gap_workflow.py`, the `execute_nlp_analysis_with_data` function:

1. **Extracts retrieved data** from previous steps
2. **Creates dataset summary** for the planner
3. **Runs planner** to get execution plan
4. **Runs executor** with plan + actual datasets
5. **Returns comprehensive analysis**

## Benefits

### ✅ No Redundant Data Fetching
- Data is fetched once in DataRetrieval step
- All tools operate on pre-fetched data
- Fast execution, low cost

### ✅ Intelligent Planning
- Planner selects appropriate tools for each dataset
- Avoids redundant analysis
- Adapts to query requirements

### ✅ Flexible Tool Parameters
- Each tool can have different schemas
- Parameters can be customized per task
- Easy to add new tools

### ✅ Clear Separation of Concerns
- Planner: What to do
- Executor: How to do it
- Tools: Domain logic

## Example Usage

**Query:** "What are users complaining about Netflix and how has sentiment changed over time?"

**Retrieved Datasets:**
- recent_reviews (45 reviews)
- dedup_reviews (45 deduplicated)
- rating_distribution (5 rating levels)
- rating_by_source (ratings per source)
- reviews_time_series (30 days)

**Generated Plan:**
1. `analyze_review_text_data` on `dedup_reviews` → Extract pain points
2. `cluster_reviews_by_theme` on `dedup_reviews` → Group by complaint type
3. `analyze_rating_distribution` on `rating_distribution` + `rating_by_source` → Sentiment overview
4. `analyze_time_series_trends` on `reviews_time_series` → Trend analysis

**Execution:**
- Each tool runs with its specific dataset
- Results are combined
- Final answer addresses all aspects of the query

## Adding New Tools

To add a new analysis tool:

1. **Create the tool** in `nlp_data_aware.py`:
```python
@tool(requires_confirmation=False)
def my_new_analysis(data_json: str, param: int = 5) -> str:
    """Analyze data in a new way."""
    data = parse_data(data_json)  # Handles JSON string, dict, or list
    # ... analysis logic ...
    return json.dumps(result)
```

2. **Add to executor** in `nlp_executor.py`:
```python
from app.workflows.tools.nlp_data_aware import my_new_analysis

def create_nlp_executor_agent(model: OpenAIChat) -> Agent:
    return Agent(
        tools=[..., my_new_analysis],
        ...
    )
```

3. **Update planner description** in `nlp_planner.py`:
```python
description="""...
Available tools:
- my_new_analysis: Description of what it does
"""
```

Done! The planner will automatically consider your new tool when creating plans.

