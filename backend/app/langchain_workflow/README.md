# LangChain Workflow Implementation

This is a **LangChain/LangGraph** implementation of the Product Gap Detection Workflow, parallel to the Agno implementation in `/backend/app/workflows/`.

## Purpose

This implementation allows for direct comparison between:
- **Agno Framework** (original implementation)
- **LangChain/LangGraph** (this implementation)

Both implementations provide the same functionality but use different frameworks.

## Architecture

### Workflow Structure

```
1. Query Analysis + Format Detection (sequential)
   ↓
2. Data Retrieval (conditional)
   - Retrieval Planning (LLM generates SQL)
   - Data Retrieval (executor fetches data)
   ↓
3. NLP Analysis (conditional)
   - Performs text analysis on retrieved data
   ↓
4. Prepare Writer Context
   - Combines all data and format info
   ↓
5. Answer Writing (multi-agent team)
   - Routes to appropriate writer based on format
```

## Key Differences: Agno vs LangChain

### 1. **Agent Definition**

**Agno:**
```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat

agent = Agent(
    name="Query Analyzer",
    role="Analyze queries",
    model=model,
    instructions=[...],
    output_schema=QueryAnalysis,
)
```

**LangChain:**
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([...])
chain = prompt | model.with_structured_output(QueryAnalysis)
```

### 2. **Workflow Orchestration**

**Agno:**
```python
from agno.workflow.workflow import Workflow
from agno.workflow.step import Step
from agno.workflow.condition import Condition

workflow = Workflow(
    name="Product Gap Detection",
    steps=[
        Step(...),
        Condition(
            evaluator=needs_data_retrieval,
            steps=[...]
        )
    ]
)
```

**LangChain (LangGraph):**
```python
from langgraph.graph import StateGraph, START, END

workflow = StateGraph(WorkflowState)
workflow.add_node("analyze_query", analyze_query_node)
workflow.add_conditional_edges(
    "detect_format",
    should_retrieve_data,
    {"retrieve": "plan_retrieval", "skip": "prepare_context"}
)
compiled = workflow.compile()
```

### 3. **Tools**

**Agno:**
```python
from agno.tools import tool

@tool(requires_confirmation=False)
def compute_tfidf(company: str, top_n: int = 10) -> str:
    """Compute TF-IDF scores."""
    ...
```

**LangChain:**
```python
from langchain_core.tools import tool

@tool
def compute_tfidf(company: str, top_n: int = 10) -> str:
    """Compute TF-IDF scores."""
    ...
```

### 4. **Multi-Agent Teams**

**Agno:**
```python
from agno.team import Team

team = Team(
    name="Answer Writer Team",
    members=[markdown_writer, table_writer, ...],
    model=model,
    instructions=[...]
)
```

**LangChain (LangGraph):**
```python
from langgraph.graph import StateGraph

workflow = StateGraph(TeamState)
workflow.add_node("markdown", markdown_writer_node)
workflow.add_conditional_edges(START, route_to_writer, {...})
compiled = workflow.compile()
```

### 5. **State Management**

**Agno:**
```python
from agno.workflow.types import StepInput, StepOutput

def my_step(step_input: StepInput) -> StepOutput:
    prev_output = step_input.previous_step_outputs.get("StepName")
    return StepOutput(content=result)
```

**LangChain:**
```python
from typing import TypedDict

class WorkflowState(TypedDict):
    query: str
    query_analysis: dict
    final_answer: str

def my_node(state: WorkflowState) -> WorkflowState:
    return {**state, "final_answer": result}
```

## Pros and Cons

### Agno Framework

**Pros:**
- Clean, declarative syntax
- Built-in workflow primitives (Parallel, Condition)
- Integrated agent/team abstractions
- Simpler for straightforward workflows
- Less boilerplate

**Cons:**
- Newer framework, smaller community
- Less ecosystem/integrations
- Fewer examples and resources
- More opinionated structure

### LangChain/LangGraph

**Pros:**
- Massive ecosystem and community
- Extensive integrations (1000+ tools)
- Battle-tested in production
- Great documentation and examples
- Flexible and composable
- Active development

**Cons:**
- More verbose for complex workflows
- Steeper learning curve for LangGraph
- More boilerplate code
- Need to wire up more manually

## File Structure

```
langchain_workflow/
├── __init__.py
├── README.md (this file)
├── product_gap_workflow.py          # Main workflow using LangGraph
├── example_run.py                   # Example execution script
├── agents/
│   ├── __init__.py
│   ├── query_analyzer.py           # Query analysis with structured output
│   ├── retrieval_planner.py        # SQL query generation
│   ├── nlp.py                      # NLP agent with tools
│   ├── output_format.py            # Format detection
│   └── writer.py                   # Writer agents (markdown, table, chart, json)
├── tools/
│   ├── __init__.py
│   └── nlp.py                      # NLP analysis tools
├── steps/
│   ├── __init__.py
│   └── data_retrieval.py           # Data retrieval service
└── teams/
    ├── __init__.py
    └── writer.py                   # Multi-agent writer team using LangGraph
```

## Usage

```python
from app.langchain_workflow.product_gap_workflow import run_workflow

# Run the workflow
result = run_workflow(
    query="What are the top product gaps for Notion?",
    user_id=1
)

print(result["final_answer"])
```

## Installation Requirements

Add to your `requirements.txt` or `pyproject.toml`:

```toml
langchain = "^0.3.0"
langchain-openai = "^0.2.0"
langchain-core = "^0.3.0"
langgraph = "^0.2.0"
```

## Testing

```bash
# Run example
cd backend
python -m app.langchain_workflow.example_run
```

## Which One Should You Use?

**Use Agno if:**
- You want cleaner, more declarative code
- You're building a new project
- You don't need extensive third-party integrations
- You prefer simplicity over flexibility

**Use LangChain if:**
- You need extensive ecosystem integrations
- You want maximum flexibility
- You need battle-tested production stability
- You want more community support and examples
- You're working with existing LangChain code

## Performance Comparison

Both frameworks use the same LLM calls under the hood, so performance is similar. Key differences:
- **Agno**: Slightly less overhead, more streamlined
- **LangChain**: More flexible but requires more setup

## Next Steps

1. Run both implementations with the same queries
2. Compare code readability and maintainability
3. Evaluate which fits your team's needs better
4. Consider hybrid approach: use what works best for each part

