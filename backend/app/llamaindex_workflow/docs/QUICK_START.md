# Quick Start Guide

## Installation

First, install LlamaIndex:

```bash
pip install llama-index llama-index-llms-openai
```

Or add to your `pyproject.toml`:

```toml
[tool.poetry.dependencies]
llama-index = "^0.10.0"
llama-index-llms-openai = "^0.1.0"
```

## Basic Usage

### 1. Run the Workflow

```python
from app.llamaindex_workflow.main import run_workflow

# Simple execution
result = await run_workflow(
    query="What are the main product gaps for Netflix?",
    user_id=1
)
print(result)
```

### 2. Streaming Mode

```python
from app.llamaindex_workflow.main import run_workflow_streaming

# Stream events as they happen
async for event in run_workflow_streaming(
    query="Analyze customer sentiment",
    user_id=1
):
    print(f"Event: {event}")
```

### 3. Direct Workflow Usage

```python
from app.llamaindex_workflow.workflow import ProductGapWorkflow

# Create workflow instance
workflow = ProductGapWorkflow(user_id=1, verbose=True)

# Run with custom timeout
result = await workflow.run(
    query="Your question here",
    timeout=300
)
```

## Understanding the Flow

The workflow follows this pattern:

```
Start
  ├─> Query Analysis ──┐
  └─> Format Detection ┘
           │
           ├─> [If needs data] Retrieval Planning
           │         │
           │         └─> Data Retrieval
           │
           └─> Prepare Context
                    │
                    └─> Generate Answer
```

## Configuration

### Environment Variables

Make sure these are set in your `.env`:

```bash
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@localhost/db
```

### Custom LLM

To use a different model:

```python
# In agents.py
def get_llm() -> OpenAI:
    return OpenAI(
        model="gpt-4",  # Change model here
        api_key=SETTINGS.OPENAI_API_KEY,
        temperature=0.1
    )
```

## Debugging

Enable verbose logging:

```python
workflow = ProductGapWorkflow(user_id=1, verbose=True)
```

Check logs:

```python
from app import get_logger

logger = get_logger("llamaindex_workflow")
logger.setLevel("DEBUG")
```

## Common Issues

### Issue: "No table schemas found"

**Solution:** Make sure your database has tables and the user has access:

```python
from app.services.schema_service import SchemaService
from app.database.base import SessionLocal

db = SessionLocal()
service = SchemaService(db)
schemas = service.get_all_available_schemas(user_id=1)
print(f"Found {len(schemas)} schemas")
```

### Issue: "Event not handled"

**Solution:** Make sure all events have corresponding `@step` methods that accept them.

### Issue: "Workflow timeout"

**Solution:** Increase timeout:

```python
workflow = ProductGapWorkflow(user_id=1, timeout=600)  # 10 minutes
```

## Next Steps

- Read [COMPARISON.md](./COMPARISON.md) to understand differences from Agno
- Check [workflow.py](./workflow.py) for implementation details
- Explore [events.py](./events.py) to see all event types
- Review [agents.py](./agents.py) for LLM configurations
