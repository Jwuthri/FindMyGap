<!-- a426bbb9-c873-454d-9ece-4dc02ff7abde 26ec2c5c-7a97-448e-9e16-373fefd95d4e -->
# Product Gap Detection Workflow System

## Architecture Overview

Create a conditional workflow that intelligently routes queries through specialized agents:

**Query Analyzer Agent** → **[Data Retrieval]** → **[Data Sufficiency Check]** → **[Retry Data Retrieval if needed]** → **[NLP Analysis]** → **Output Format Detection** → **Answer Writer Team**

Conditional steps (Data Retrieval, Data Sufficiency Check, NLP Analysis) only execute when needed based on query analysis. The Data Sufficiency Check can trigger one retry with increased data limit.

## Implementation Steps

### 1. Create Core Workflow File

**File**: `/backend/app/agents/product_gap_workflow.py`

Structure:

- Import existing tools from `teams.py` (all retrieve/analysis functions)
- Define 5 agent types + 1 team
- Build conditional workflow with Step objects
- Add streaming support

### 2. Agent Implementations

#### Query Analyzer Agent

- **Purpose**: Examine user query and determine execution plan
- **Output**: Structured decision on which steps to run (needs_data, needs_nlp)
- **Model**: gpt-5-mini
- **Tools**: None (pure reasoning)
- **Response Model**: Pydantic schema with `needs_data_retrieval: bool`, `needs_nlp_analysis: bool`, `company: str`, `query_type: str`

#### Database Retrieval Agent

- **Purpose**: Fetch review data
- **Reuse tools from teams.py**: `retrieve_reviews`, `filter_reviews_by_rating`, `filter_reviews_by_source`, `search_reviews_by_keyword`
- **Conditional**: Only runs if Query Analyzer sets `needs_data_retrieval=True`
- **Output**: JSON with reviews
- **Initial limit**: 100 reviews (default)

#### Data Sufficiency Evaluator Agent

- **Purpose**: Evaluate if retrieved data is sufficient for the planned NLP analysis
- **Input**: Retrieved data + original query + planned NLP approach
- **Output**: Pydantic schema with `is_sufficient: bool`, `current_count: int`, `recommended_count: int`, `reasoning: str`
- **Conditional**: Only runs after data retrieval AND if NLP analysis is needed
- **Logic**: 
- Checks data quantity vs analysis requirements
- If insufficient: signals retry with increased limit (2x or 3x original)
- Max 1 retry allowed
- **Model**: gpt-5-mini

#### NLP Analysis Agent

- **Purpose**: Perform text analytics (clustering, TF-IDF, feature extraction)
- **Reuse tools from teams.py**: `compute_tfidf`, `analyze_sentiment_distribution`, `identify_feature_requests`, `cluster_similar_reviews`, `analyze_product_gaps`
- **Conditional**: Only runs if Query Analyzer sets `needs_nlp_analysis=True`
- **Sequential dependency**: Runs after Database Retrieval (and potential retry) is complete
- **Output**: Analysis results

#### Output Format Detection Agent

- **Purpose**: Determine best output format (markdown/table/chart/json)
- **Reuse tool from teams.py**: `determine_best_output_format`
- **Always runs**: Required to guide Answer Writer Team
- **Output**: Format specification with primary format and reasoning

#### Answer Writer Team

- **Purpose**: Format final answer based on detected output format
- **Structure**: Team with specialized writer agents
- **Members**:
- **MarkdownWriter Agent**: Formats as markdown reports
- **TableWriter Agent**: Creates structured tables/dataframes
- **ChartWriter Agent**: Generates visualization specs
- **JSONWriter Agent**: Outputs structured JSON
- **Coordinator**: Routes to appropriate writer based on format detection
- **Always runs**: Final step in workflow

### 3. Workflow Configuration

Use `agno.workflow.workflow.Workflow` with:

- **Steps**: 

1. Query Analyzer (always)
2. Database Retrieval (conditional via workflow condition)
3. NLP Analysis (conditional via workflow condition)
4. Output Format Detection (always)
5. Answer Writer Team (always)

- **Persistence**: SqliteDb at `memory.db`
- **Streaming**: Enable with `stream=True`, `stream_intermediate_steps=True`
- **Conditions**: Check Query Analyzer output to skip/run conditional steps

### 4. Key Files to Modify/Create

**New file**: `/backend/app/agents/product_gap_workflow.py`

- Import tools from `app.agents.teams`
- Define all agents
- Define Answer Writer Team
- Build workflow with conditional logic
- Export `create_product_gap_workflow()` factory function

**New file**: `/backend/scripts/agno_example/product_gap_workflow_demo.py`

- Demo script showing workflow execution
- Test cases: 
- Query needing only data retrieval
- Query needing data + NLP
- Query needing only NLP
- Query needing neither (general question)
- Show streaming output

### 5. Conditional Execution Pattern

Reference: `/backend/scripts/agno_example/agno_workflow_event_streaming.py` shows async generators for step preparation.

Implement workflow conditions by checking Query Analyzer output in step input preparation functions.

### 6. Reusable Components

From `teams.py` (lines 128-224, 231-655):

- All `@tool` decorated functions for data retrieval
- All `@tool` decorated functions for NLP analysis
- Pydantic schemas (lines 60-122)
- STOPWORDS constant

Do NOT duplicate - import directly.

## Success Criteria

- Workflow correctly skips unnecessary steps based on query
- Data retrieval → NLP runs sequentially when both needed
- Answer Writer Team selects correct writer agent
- Streaming shows intermediate step progress
- All agents reuse existing tools (no duplication)
- Demo script runs successfully with various query types

### To-dos

- [ ] Create /backend/app/agents/product_gap_workflow.py with imports and structure
- [ ] Implement Query Analyzer Agent with structured output for routing decisions
- [ ] Implement Database Retrieval Agent reusing tools from teams.py
- [ ] Implement NLP Analysis Agent reusing tools from teams.py
- [ ] Implement Output Format Detection Agent reusing tool from teams.py
- [ ] Create Answer Writer Team with specialized writer agents (Markdown, Table, Chart, JSON)
- [ ] Build Workflow with conditional step execution logic and SqliteDb persistence
- [ ] Create demo script at /backend/scripts/agno_example/product_gap_workflow_demo.py with test cases