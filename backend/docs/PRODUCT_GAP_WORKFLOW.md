# Product Gap Detection Workflow System

## Overview

An intelligent workflow system that analyzes product reviews to identify gaps and opportunities. The system autonomously determines optimal output formats and executes multi-step analysis with conditional step execution.

## Architecture

```
User Query
    ↓
Query Analyzer (determines what's needed)
    ↓
[Conditional: Data Retrieval] → Fetch reviews if needed
    ↓
[Conditional: Data Sufficiency Check] → Verify data adequacy
    ↓
[Conditional: Retry with more data] → If insufficient (max 1 retry)
    ↓
[Conditional: NLP Analysis] → AI-powered insights if needed
    ↓
Output Format Detection (always) → Determine best presentation format
    ↓
Answer Writer Team (always) → Format final answer
```

## Core Agents

### 1. Query Analyzer Agent
- **Purpose**: Examines incoming query and determines execution path
- **Output**: Structured analysis (`QueryAnalysis` model)
  - `needs_data_retrieval`: bool
  - `needs_nlp_analysis`: bool  
  - `company`: Optional[str]
  - `query_type`: str
  - `reasoning`: str

### 2. Database Retrieval Agent
- **Purpose**: Fetch review data from database
- **Tools**: 
  - `retrieve_reviews`
  - `filter_reviews_by_rating`
  - `filter_reviews_by_source`
  - `search_reviews_by_keyword`
- **Conditional**: Only runs if Query Analyzer sets `needs_data_retrieval=True`
- **Default**: Starts with 100 reviews

### 3. Data Sufficiency Evaluator Agent
- **Purpose**: Evaluate if retrieved data is adequate for planned NLP analysis
- **Output**: Structured evaluation (`DataSufficiencyResult` model)
  - `is_sufficient`: bool
  - `current_count`: int
  - `recommended_count`: int
  - `reasoning`: str
- **Conditional**: Only runs if both data retrieval AND NLP analysis are needed
- **Logic**: Can trigger one retry with 2x-3x data (max 500 reviews)

### 4. NLP Analysis Agent
- **Purpose**: Perform AI-powered text analytics
- **Tools**:
  - `compute_tfidf`: Statistical term importance
  - `analyze_sentiment_distribution`: Rating/sentiment breakdown
  - `identify_feature_requests`: Extract feature requests and pain points
  - `cluster_similar_reviews`: Group reviews by theme
  - `analyze_product_gaps`: Deep gap analysis (best for "what's missing")
- **Conditional**: Only runs if Query Analyzer sets `needs_nlp_analysis=True`
- **Sequential**: Runs after data retrieval (and potential retry) completes

### 5. Output Format Detection Agent
- **Purpose**: Determine optimal output format
- **Tools**: `determine_best_output_format`
- **Output**: Format recommendation with reasoning
- **Always runs**: Required to guide Answer Writer Team

### 6. Answer Writer Team
- **Purpose**: Format final answer based on detected format
- **Structure**: Team with specialized writer agents
- **Members**:
  - **Markdown Writer**: Reports and explanations
  - **Table Writer**: Structured tabular data
  - **Chart Writer**: Visualization specifications
  - **JSON Writer**: Structured API responses
- **Coordinator**: Routes to appropriate writer
- **Always runs**: Final step in workflow

## Usage

### Basic Usage

```python
import asyncio
from app.agents.product_gap_workflow import create_product_gap_workflow
from app.config import SETTINGS

async def main():
    # Create workflow
    workflow = create_product_gap_workflow(
        api_key=SETTINGS.OPENAI_API_KEY
    )
    
    # Run query
    result = await workflow.arun(
        input="What are the main product gaps for Spotify?",
        markdown=True
    )
    
    print(result)

asyncio.run(main())
```

### Streaming Execution

```python
from agno.run.workflow import WorkflowRunEvent

async def main():
    workflow = create_product_gap_workflow(api_key=SETTINGS.OPENAI_API_KEY)
    
    resp = await workflow.arun(
        input="What are the main product gaps for Spotify?",
        markdown=True,
        stream=True,
        stream_intermediate_steps=True
    )
    
    async for event in resp:
        if event.event == WorkflowRunEvent.step_started.value:
            print(f"Starting: {event.step_name}")
        elif event.event == WorkflowRunEvent.step_completed.value:
            print(f"Completed: {event.step_name}")
        elif event.event == WorkflowRunEvent.workflow_completed.value:
            print(f"\nFinal Answer:\n{event.content}")

asyncio.run(main())
```

## Example Queries

### Data Retrieval Only
```python
"Show me the latest 50 reviews for Spotify"
```
**Workflow**: Query Analysis → Data Retrieval → Format Detection → Answer Writing

### Data + NLP Analysis
```python
"What are the main product gaps for Notion based on customer feedback?"
```
**Workflow**: Query Analysis → Data Retrieval → Sufficiency Check → NLP Analysis → Format Detection → Answer Writing

### NLP Only (using existing data)
```python
"Cluster Slack reviews by theme"
```
**Workflow**: Query Analysis → NLP Analysis → Format Detection → Answer Writing

### General Question
```python
"What companies do you have data for?"
```
**Workflow**: Query Analysis → Format Detection → Answer Writing

### Complex Analysis (triggers retry)
```python
"Perform detailed clustering analysis on Spotify reviews to identify all major themes"
```
**Workflow**: Query Analysis → Data Retrieval (100) → Sufficiency Check (insufficient) → Data Retrieval Retry (300) → NLP Analysis → Format Detection → Answer Writing

## Demo Scripts

### Quick Test
```bash
cd backend
python scripts/test_workflow.py
```

### Comprehensive Demo
```bash
cd backend
python scripts/agno_example/product_gap_workflow_demo.py
```

The demo script includes 5 test scenarios:
1. Data retrieval only
2. Data + NLP analysis
3. NLP only
4. General question
5. Insufficient data with retry

## Configuration

### Database
- **Location**: `tmp/product_gap_workflow.db`
- **Table**: `product_gap_workflow_session`
- **Purpose**: Persist workflow sessions and enable resume

### Model
- **Default**: `gpt-5-mini` (fast, cost-effective)
- **Alternative**: Can be changed to `gpt-5` for more complex reasoning

## Key Features

✅ **Conditional Execution**: Steps only run when needed based on query analysis
✅ **Data Sufficiency Checking**: Automatic retry with more data if insufficient
✅ **Tool Reuse**: All tools imported from `teams.py` (no duplication)
✅ **Streaming Support**: Real-time progress tracking
✅ **Specialized Writers**: Format-specific output agents
✅ **Session Persistence**: Resume and track workflow history
✅ **Flexible Architecture**: Mix agents, teams, and custom functions

## Files

- `/backend/app/agents/product_gap_workflow.py` - Main workflow implementation
- `/backend/scripts/agno_example/product_gap_workflow_demo.py` - Comprehensive demo
- `/backend/scripts/test_workflow.py` - Quick test script
- `/backend/app/agents/teams.py` - Reusable tools and agents

## Success Criteria

✅ Workflow correctly skips unnecessary steps based on query
✅ Data retrieval → NLP runs sequentially when both needed
✅ Data sufficiency check triggers retry when needed (max 1 retry)
✅ Answer Writer Team selects correct writer agent
✅ Streaming shows intermediate step progress
✅ All agents reuse existing tools (no duplication)

## Future Enhancements

- [ ] Add workflow branching for complex decision trees
- [ ] Implement parallel data retrieval from multiple sources
- [ ] Add caching layer for frequently accessed reviews
- [ ] Support for multiple output formats in single response
- [ ] Integration with real-time data streaming
- [ ] Advanced retry strategies with exponential backoff
- [ ] Multi-language support for international reviews

## Troubleshooting

### Workflow hangs or times out
- Check API key is valid
- Verify database permissions for `tmp/` directory
- Reduce data limits if processing large datasets

### Steps not running conditionally
- Verify Query Analyzer is producing structured output
- Check step preparation functions are correctly parsing previous outputs

### Tool execution errors
- Ensure mock data generators in `teams.py` are accessible
- Verify company names match available data (spotify, notion, slack)

## Support

For issues or questions, refer to:
- `/backend/docs/AGNO_DOC.md` - Full Agno framework documentation
- `/backend/docs/FINDMYGAPS_TEAM.md` - Team-based architecture reference

