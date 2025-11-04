# LangChain Workflow - Quick Start

## Installation

Add these to your `pyproject.toml`:

```toml
langchain = "^0.3.0"
langchain-openai = "^0.2.0"
langchain-core = "^0.3.0"
langgraph = "^0.2.0"
```

Or install via pip:

```bash
pip install langchain langchain-openai langchain-core langgraph
```

## Quick Example

```python
from app.langchain_workflow.product_gap_workflow import run_workflow

# Run a simple query
result = run_workflow(
    query="What are the top product gaps for Notion?",
    user_id=1
)

print(result["final_answer"])
```

## Using the Example Script

```bash
# Run with default examples
python -m app.langchain_workflow.example_run

# Run with custom query
python -m app.langchain_workflow.example_run "Show me sentiment distribution for Slack"
```

## Key Components

### 1. Main Workflow
```python
from app.langchain_workflow.product_gap_workflow import create_product_gap_workflow

workflow = create_product_gap_workflow(user_id=1)
result = workflow.invoke({
    "query": "Your query here",
    "user_id": 1,
    # ... other state fields
})
```

### 2. Individual Agents
```python
from langchain_openai import ChatOpenAI
from app.langchain_workflow.agents.query_analyzer import create_query_analyzer_agent

model = ChatOpenAI(model="gpt-4o-mini")
analyzer = create_query_analyzer_agent(model)

result = analyzer.invoke({"query": "What are product gaps?"})
print(result)  # QueryAnalysis object
```

### 3. Writer Team
```python
from app.langchain_workflow.teams.writer import create_answer_writer_team

writer_team = create_answer_writer_team(model)
result = writer_team.invoke({
    "messages": [HumanMessage(content="Write an answer...")],
    "format_type": "markdown"
})
```

## Environment Variables

Make sure you have:

```bash
export OPENAI_API_KEY="your-key-here"
export DATABASE_URL="postgresql://..."
```

## File Structure

```
langchain_workflow/
├── product_gap_workflow.py     # Main workflow (START HERE)
├── example_run.py               # Example usage
├── README.md                    # Documentation
├── COMPARISON.md                # Agno vs LangChain comparison
├── QUICKSTART.md                # This file
├── agents/
│   ├── query_analyzer.py
│   ├── retrieval_planner.py
│   ├── nlp.py
│   ├── output_format.py
│   └── writer.py
├── tools/
│   └── nlp.py
├── steps/
│   └── data_retrieval.py
└── teams/
    └── writer.py
```

## Common Patterns

### Adding a New Node

```python
def my_custom_node(state: WorkflowState) -> WorkflowState:
    """Process the state and return updated state."""
    # Your logic here
    result = do_something(state["query"])
    
    return {
        **state,
        "my_field": result
    }

# Add to workflow
workflow.add_node("my_node", my_custom_node)
workflow.add_edge("previous_node", "my_node")
```

### Conditional Routing

```python
def should_do_something(state: WorkflowState) -> Literal["yes", "no"]:
    """Decide which path to take."""
    if state["some_condition"]:
        return "yes"
    return "no"

workflow.add_conditional_edges(
    "decision_point",
    should_do_something,
    {"yes": "do_it", "no": "skip_it"}
)
```

### Creating a New Agent

```python
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class MyOutput(BaseModel):
    result: str = Field(..., description="The result")

def create_my_agent(model):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful agent..."),
        ("user", "{query}")
    ])
    
    return prompt | model.with_structured_output(MyOutput)
```

## Testing

```python
# Test individual components
from app.langchain_workflow.agents.query_analyzer import create_query_analyzer_agent
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini")
analyzer = create_query_analyzer_agent(model)

result = analyzer.invoke({"query": "Test query"})
assert result.needs_data_retrieval in [True, False]
```

## Debugging

Enable verbose logging:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.langchain_workflow")
logger.setLevel(logging.DEBUG)
```

## Next Steps

1. Read `README.md` for architecture overview
2. Check `COMPARISON.md` to compare with Agno
3. Run `example_run.py` to see it in action
4. Modify `product_gap_workflow.py` for your needs
5. Add custom agents/tools as needed

## Support

- LangChain Docs: https://python.langchain.com/
- LangGraph Tutorial: https://langchain-ai.github.io/langgraph/
- Agno Docs: https://agno.dev

