# LlamaIndex Workflow - Documentation Index

Welcome to the LlamaIndex workflow implementation documentation. This index helps you navigate all available documentation.

## 📚 Documentation Overview

### Getting Started

1. **[README.md](./README.md)** - Start here!
   - Overview of the workflow
   - Quick installation guide
   - Basic usage examples
   - File structure

2. **[QUICK_START.md](./QUICK_START.md)** - Hands-on guide
   - Installation instructions
   - Basic usage patterns
   - Configuration options
   - Common issues and solutions

### Understanding the System

3. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Deep dive
   - Core concepts (Events, Steps, Context)
   - Workflow flow diagram
   - Step-by-step execution details
   - Conditional and parallel execution
   - Best practices

4. **[COMPARISON.md](./COMPARISON.md)** - Agno vs LlamaIndex
   - Architecture comparison
   - Key differences
   - Pros and cons of each approach
   - When to use which framework
   - Performance considerations

### Migration and Development

5. **[MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)** - Migrate from Agno
   - Step-by-step migration process
   - Concept mapping
   - Code examples (before/after)
   - Common patterns
   - Troubleshooting

6. **[TESTING.md](./TESTING.md)** - Testing guide
   - Unit testing steps
   - Integration testing
   - Mocking strategies
   - Test fixtures
   - Best practices

### Code Examples

7. **[example.py](./example.py)** - Working examples
   - Basic execution
   - Streaming mode
   - Direct workflow usage
   - Multiple queries
   - Error handling

## 🗂️ Code Structure

### Core Files

- **[workflow.py](./workflow.py)** - Main workflow implementation
  - `ProductGapWorkflow` class
  - All workflow steps
  - Event routing logic

- **[events.py](./events.py)** - Event definitions
  - All event types used in the workflow
  - Lightweight trigger events

- **[agents.py](./agents.py)** - LLM agent configurations
  - Query analysis
  - Format detection
  - Retrieval planning
  - Answer generation

- **[services.py](./services.py)** - Data services
  - `DataRetrievalService` class
  - SQL execution
  - Data formatting

- **[main.py](./main.py)** - Entry points
  - `run_workflow()` - Basic execution
  - `run_workflow_streaming()` - Streaming mode

### Test Files

- **[tests/conftest.py](./tests/conftest.py)** - Test fixtures
- **[tests/test_services.py](./tests/test_services.py)** - Service tests

## 🎯 Quick Navigation

### I want to...

**...get started quickly**
→ [README.md](./README.md) → [QUICK_START.md](./QUICK_START.md)

**...understand how it works**
→ [ARCHITECTURE.md](./ARCHITECTURE.md)

**...migrate from Agno**
→ [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)

**...compare with Agno**
→ [COMPARISON.md](./COMPARISON.md)

**...write tests**
→ [TESTING.md](./TESTING.md)

**...see examples**
→ [example.py](./example.py)

**...understand the code**
→ [workflow.py](./workflow.py) → [ARCHITECTURE.md](./ARCHITECTURE.md)

## 📖 Reading Order

### For New Users

1. [README.md](./README.md) - Get overview
2. [QUICK_START.md](./QUICK_START.md) - Try it out
3. [example.py](./example.py) - See examples
4. [ARCHITECTURE.md](./ARCHITECTURE.md) - Understand deeply

### For Agno Users

1. [COMPARISON.md](./COMPARISON.md) - See differences
2. [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) - Learn migration
3. [ARCHITECTURE.md](./ARCHITECTURE.md) - Understand new patterns
4. [example.py](./example.py) - See it in action

### For Developers

1. [ARCHITECTURE.md](./ARCHITECTURE.md) - Understand system
2. [workflow.py](./workflow.py) - Read implementation
3. [TESTING.md](./TESTING.md) - Learn testing
4. [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) - See patterns

## 🔑 Key Concepts

### Events
Lightweight triggers that activate workflow steps. Defined in [events.py](./events.py).

### Steps
Methods decorated with `@step` that process events. Defined in [workflow.py](./workflow.py).

### Context
Shared state store that persists across all steps. Used via `ctx.get()` and `ctx.set()`.

### Workflow
Class-based workflow that orchestrates all steps. Main class: `ProductGapWorkflow`.

## 📊 Workflow Flow

```
Start → Query Analysis + Format Detection (parallel)
     → Retrieval Planning (conditional)
     → Data Retrieval (conditional)
     → Prepare Context
     → Generate Answer
     → Stop
```

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed flow diagram.

## 🛠️ Common Tasks

### Run the workflow
```python
from app.llamaindex_workflow.main import run_workflow
result = await run_workflow("Your query here")
```

### Enable streaming
```python
from app.llamaindex_workflow.main import run_workflow_streaming
async for event in run_workflow_streaming("Your query"):
    print(event)
```

### Add a new step
1. Define event in [events.py](./events.py)
2. Add `@step` method in [workflow.py](./workflow.py)
3. Emit event from previous step
4. Update tests

### Debug issues
1. Enable verbose mode: `ProductGapWorkflow(verbose=True)`
2. Check logs
3. Use `stream_events()` to see event flow
4. Add breakpoints in step methods

## 📝 Documentation Standards

All documentation follows these principles:

- **Clear**: Easy to understand for all skill levels
- **Complete**: Covers all aspects thoroughly
- **Practical**: Includes working examples
- **Organized**: Logical structure and navigation
- **Up-to-date**: Reflects current implementation

## 🤝 Contributing

When updating documentation:

1. Keep this index updated
2. Add cross-references between docs
3. Include code examples
4. Update diagrams if needed
5. Test all code examples

## 📞 Support

- Check documentation first
- Review [example.py](./example.py) for patterns
- See [TESTING.md](./TESTING.md) for debugging
- Read [ARCHITECTURE.md](./ARCHITECTURE.md) for deep understanding

## 🔄 Version History

- **v1.0** - Initial LlamaIndex implementation
  - Event-driven architecture
  - Conditional execution
  - Parallel steps
  - Comprehensive documentation

---

**Last Updated:** 2025-11-04

**Maintained By:** Development Team

**Related:** [Agno Workflow](../workflows/), [DSPy Workflow](../dspy_workflow/)
