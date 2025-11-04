# LlamaIndex Workflow Implementation

This directory contains a reimplementation of the product gap detection workflow using [LlamaIndex Workflows](https://developers.llamaindex.ai/python/llamaagents/workflows/).

## Overview

The workflow analyzes product gaps using a multi-step process with conditional execution:

1. **Query Analysis** - Determines what steps are needed
2. **Format Detection** - Identifies desired output format
3. **Data Retrieval** (conditional) - Fetches relevant data from database
4. **NLP Analysis** (conditional) - Performs text analysis on reviews
5. **Answer Generation** - Creates final formatted response

## Quick Start

```python
from app.llamaindex_workflow.main import run_workflow

# Run the workflow
result = await run_workflow("What are the main product gaps for Netflix?")
print(result)
```

See [QUICK_START.md](./QUICK_START.md) for detailed usage examples.

## Key Differences from Agno Implementation

- Uses LlamaIndex's `Workflow` and `@step` decorators
- Events are used for step communication instead of `StepInput`/`StepOutput`
- Conditional logic handled via event routing
- Built-in support for streaming and observability
- Context-based state management

See [COMPARISON.md](./COMPARISON.md) for a detailed comparison.

## Documentation

- **[QUICK_START.md](./QUICK_START.md)** - Get started quickly with examples
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Deep dive into workflow architecture
- **[COMPARISON.md](./COMPARISON.md)** - Compare with Agno implementation
- **[TESTING.md](./TESTING.md)** - Testing guide and best practices

## File Structure

```
llamaindex_workflow/
├── __init__.py              # Package initialization
├── workflow.py              # Main workflow definition with all steps
├── events.py                # Event definitions for inter-step communication
├── agents.py                # LLM agent configurations
├── services.py              # Data retrieval and processing services
├── main.py                  # Entry point and execution logic
├── example.py               # Usage examples
├── README.md                # This file
├── QUICK_START.md           # Quick start guide
├── ARCHITECTURE.md          # Architecture documentation
├── COMPARISON.md            # Comparison with Agno
└── TESTING.md               # Testing guide
```

## Installation

Install LlamaIndex dependencies:

```bash
pip install llama-index llama-index-llms-openai
```

Or add to `pyproject.toml`:

```toml
[tool.poetry.dependencies]
llama-index = "^0.10.0"
llama-index-llms-openai = "^0.1.0"
```

## Features

✅ Event-driven architecture  
✅ Conditional step execution  
✅ Parallel step execution  
✅ Context-based state management  
✅ Built-in streaming support  
✅ Comprehensive logging  
✅ Type-safe events  
✅ Easy to extend  

## Examples

### Basic Usage

```python
from app.llamaindex_workflow.main import run_workflow

result = await run_workflow(
    query="What are the main product gaps for Netflix?",
    user_id=1
)
```

### Streaming Mode

```python
from app.llamaindex_workflow.main import run_workflow_streaming

async for event in run_workflow_streaming(query="...", user_id=1):
    print(f"Event: {event}")
```

### Direct Workflow Control

```python
from app.llamaindex_workflow.workflow import ProductGapWorkflow

workflow = ProductGapWorkflow(user_id=1, verbose=True, timeout=600)
result = await workflow.run(query="...")
```

See [example.py](./example.py) for more examples.

## Configuration

Set these environment variables:

```bash
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@localhost/db
```

## Contributing

When adding new features:

1. Define new events in `events.py`
2. Add step methods in `workflow.py`
3. Update documentation
4. Add tests
5. Update examples

## License

Same as parent project.
