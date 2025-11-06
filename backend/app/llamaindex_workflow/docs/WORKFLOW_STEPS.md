# LlamaIndex Workflow Steps

## Complete Workflow Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         Start Event                              │
│                      (User Query Input)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Query Analysis                                          │
│  - Analyze query intent                                          │
│  - Determine needs_data_retrieval                                │
│  - Determine needs_nlp_analysis                                  │
│  - Extract company, query_type, analysis_type                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: Format Detection                                        │
│  - Detect desired output format (markdown, json, table, etc)    │
│  - Extract format details                                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────┴────────┐
                    │                 │
         needs_data_retrieval?        │
                    │                 │
              ┌─────┴─────┐           │
              │ Yes       │ No        │
              ▼           ▼           │
┌──────────────────┐  ┌──────────────────────┐
│  Step 3:         │  │  Skip Retrieval      │
│  Retrieval       │  │  Event               │
│  Planning        │  └──────────┬───────────┘
│  - Generate SQL  │             │
│  - Plan queries  │             │
└────────┬─────────┘             │
         │                       │
         ▼                       │
┌──────────────────┐             │
│  Step 4:         │             │
│  Data Retrieval  │             │
│  - Execute SQL   │             │
│  - Format data   │             │
└────────┬─────────┘             │
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │ needs_nlp_analysis?   │
         └───────────┬───────────┘
                     │
              ┌──────┴──────┐
              │ Yes         │ No
              ▼             ▼
┌──────────────────────┐   │
│  Step 5:             │   │
│  NLP Analysis        │   │
│  - Agent selects     │   │
│    NLP tool(s)       │   │
│  - Returns tool      │   │
│    call specs        │   │
│  - Adds to event     │   │
└──────────┬───────────┘   │
           │               │
           └───────┬───────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 6: Generate Final Answer                                   │
│  - Combine all context (query, format, data, NLP results)       │
│  - Generate formatted response                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Stop Event                               │
│                      (Final Answer)                              │
└─────────────────────────────────────────────────────────────────┘
```

## Step Details

### Step 1: Query Analysis
**Input**: User query string  
**Output**: `QueryAnalyzedEvent`  
**Agent**: `analyze_query()`  
**Purpose**: Understand query intent and determine workflow path

### Step 2: Format Detection
**Input**: `QueryAnalyzedEvent`  
**Output**: `FormatDetectedEvent`  
**Agent**: `detect_format()`  
**Purpose**: Determine desired output format

### Step 3: Retrieval Planning
**Input**: `FormatDetectedEvent`  
**Output**: `RetrievalPlanEvent` or `SkipRetrievalEvent`  
**Agent**: `plan_retrieval()`  
**Purpose**: Generate SQL queries for data retrieval  
**Conditional**: Only if `needs_data_retrieval=True`

### Step 4: Data Retrieval
**Input**: `RetrievalPlanEvent`  
**Output**: `DataRetrievedEvent`  
**Service**: `DataRetrievalService`  
**Purpose**: Execute SQL and retrieve data

### Step 5: NLP Analysis ⭐ NEW
**Input**: `DataRetrievedEvent`  
**Output**: `DataRetrievedEvent` (with NLP results)  
**Agent**: `perform_nlp_analysis()`  
**Purpose**: Select and configure NLP tools  
**Conditional**: Only if `needs_nlp_analysis=True`

**Available Tools**:
- `compute_tfidf`: Find important terms
- `cluster_reviews`: Group by theme
- `analyze_sentiment`: Sentiment analysis
- `identify_features`: Extract feature requests

### Step 6: Generate Final Answer
**Input**: `DataRetrievedEvent` or `SkipRetrievalEvent`  
**Output**: `StopEvent`  
**Agent**: `generate_answer()`  
**Purpose**: Create final formatted response

## Event Types

```python
class QueryAnalyzedEvent(Event):
    query: str
    analysis: QueryAnalysis

class FormatDetectedEvent(Event):
    query: str
    analysis: QueryAnalysis
    format_info: FormatDetection

class RetrievalPlanEvent(Event):
    query: str
    analysis: QueryAnalysis
    format_info: FormatDetection
    plan: RetrievalPlan

class DataRetrievedEvent(Event):
    query: str
    analysis: QueryAnalysis
    format_info: FormatDetection
    retrieved_data: Optional[Dict[str, Any]]
    # After Step 5, includes: retrieved_data['nlp_analysis']

class SkipRetrievalEvent(Event):
    query: str
    analysis: QueryAnalysis
    format_info: FormatDetection
```

## Conditional Execution

### Data Retrieval Branch
```python
if analysis.needs_data_retrieval:
    # Execute Steps 3 & 4
    plan_retrieval() → retrieve_data()
else:
    # Skip to answer generation
    SkipRetrievalEvent → generate_final_answer()
```

### NLP Analysis Branch
```python
if analysis.needs_nlp_analysis:
    # Execute Step 5
    perform_nlp_analysis()
    # Adds nlp_analysis to retrieved_data
else:
    # Pass through unchanged
    return ev
```

## Example Flows

### Flow 1: Simple Data Query (No NLP)
```
Query: "Show me Netflix reviews with rating below 3"
→ needs_data_retrieval=True, needs_nlp_analysis=False
→ Steps: 1 → 2 → 3 → 4 → (skip 5) → 6
```

### Flow 2: NLP Analysis Query
```
Query: "Find product gaps for Netflix"
→ needs_data_retrieval=True, needs_nlp_analysis=True
→ Steps: 1 → 2 → 3 → 4 → 5 → 6
→ Step 5 selects: identify_features_tool
```

### Flow 3: General Query (No Data)
```
Query: "What is product gap analysis?"
→ needs_data_retrieval=False, needs_nlp_analysis=False
→ Steps: 1 → 2 → (skip 3,4,5) → 6
```

## NLP Tool Selection Matrix

| Query Type | Analysis Type | Selected Tool | Parameters |
|-----------|---------------|---------------|------------|
| "Find gaps" | gap_detection | identify_features | min_frequency |
| "Sentiment analysis" | sentiment | analyze_sentiment | include_distribution |
| "Main themes" | clustering | cluster_reviews | num_clusters, method |
| "Key terms" | tfidf | compute_tfidf | top_n, min_df |
