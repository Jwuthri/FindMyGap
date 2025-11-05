# LlamaIndex Workflow - Quick Reference

## 🚀 Quick Start

```python
# Basic usage
from app.llamaindex_workflow.main import run_workflow

result = await run_workflow("Your query here", user_id=1)
```

## 📋 Common Commands

### Run Workflow
```python
# Basic
result = await run_workflow(query, user_id=1)

# Streaming
async for event in run_workflow_streaming(query, user_id=1):
    print(event)

# Direct control
workflow = ProductGapWorkflow(user_id=1, verbose=True, timeout=600)
result = await workflow.run(query=query)
```

### Run Examples
```bash
# Run basic example
python -m backend.app.llamaindex_workflow.example

# Run tests
pytest backend/app/llamaindex_workflow/tests/

# Run with coverage
pytest --cov=app.llamaindex_workflow backend/app/llamaindex_workflow/tests/
```

## 🏗️ Architecture Patterns

### Define Event
```python
from llama_index.core.workflow import Event

class MyEvent(Event):
    pass
```

### Define Step
```python
from llama_index.core.workflow import step, Context

@step
async def my_step(self, ctx: Context, ev: MyEvent):
    # Get data from context
    data = await ctx.get("key")
    
    # Process
    result = process(data)
    
    # Store result
    await ctx.set("result", result)
    
    # Trigger next step
    ctx.send_event(NextEvent())
```

### Conditional Execution
```python
@step
async def conditional_step(self, ctx: Context, ev: TriggerEvent):
    if condition:
        ctx.send_event(PathAEvent())
    else:
        ctx.send_event(PathBEvent())
```

### Parallel Execution
```python
@step
async def parallel_step(self, ctx: Context, ev: TriggerEvent):
    ctx.send_event(Task1Event())
    ctx.send_event(Task2Event())
    ctx.send_event(Task3Event())
```

### Final Step
```python
@step
async def final_step(self, ctx: Context, ev: FinalEvent):
    result = await ctx.get("final_result")
    return StopEvent(result=result)
```

## 🔧 Context Operations

```python
# Store data
await ctx.set("key", value)

# Retrieve data
value = await ctx.get("key")

# With default
value = await ctx.get("key", default=None)

# Check existence
if await ctx.get("key", default=None) is not None:
    # Key exists
```

## 🤖 LLM Operations

### Structured Prediction
```python
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage

llm = OpenAI(model="gpt-4o-mini", api_key=SETTINGS.OPENAI_API_KEY)

result = await llm.astructured_predict(
    MyModel,
    messages=[
        ChatMessage(role="system", content="System prompt"),
        ChatMessage(role="user", content="User prompt")
    ]
)
```

### Text Completion
```python
response = await llm.acomplete("Your prompt here")
result = str(response)
```

## 🗃️ Database Operations

```python
from app.database.base import SessionLocal

db_session = SessionLocal()
try:
    # Use session
    result = db_session.execute(text("SELECT * FROM table"))
finally:
    db_session.close()
```

## 🧪 Testing Patterns

### Test Step
```python
@pytest.mark.asyncio
async def test_my_step():
    workflow = MyWorkflow()
    ctx = MagicMock(spec=Context)
    ctx.get = AsyncMock(return_value="test")
    ctx.set = AsyncMock()
    
    await workflow.my_step(ctx, MyEvent())
    
    ctx.set.assert_called_once()
```

### Mock LLM
```python
@patch('app.llamaindex_workflow.agents.get_llm')
async def test_with_mock_llm(mock_get_llm):
    mock_llm = AsyncMock()
    mock_llm.astructured_predict.return_value = MyModel(...)
    mock_get_llm.return_value = mock_llm
    
    result = await my_function()
```

### Mock Database
```python
@pytest.fixture
def mock_db():
    session = MagicMock(spec=Session)
    mock_result = MagicMock()
    mock_result.keys.return_value = ["col1", "col2"]
    mock_result.__iter__.return_value = [(1, "a"), (2, "b")]
    session.execute.return_value = mock_result
    return session
```

## 📊 Logging

```python
from app import get_logger

logger = get_logger(__name__)

logger.info("Info message")
logger.error("Error message", exc_info=True)
logger.debug("Debug message")
```

## 🐛 Debugging

### Enable Verbose Mode
```python
workflow = ProductGapWorkflow(verbose=True)
```

### Stream Events
```python
async for event in workflow.stream_events(query="..."):
    print(f"Event: {type(event).__name__}")
```

### Add Breakpoints
```python
@step
async def my_step(self, ctx: Context, ev: MyEvent):
    import pdb; pdb.set_trace()
    # Debug here
```

### Check Context
```python
@step
async def debug_step(self, ctx: Context, ev: DebugEvent):
    # Log all context
    logger.info(f"Context: {ctx._data}")
```

## 🔍 Common Issues

### Step Not Executing
**Problem:** Step never runs  
**Solution:** Check if event is emitted
```python
ctx.send_event(MyStepEvent())  # Don't forget this!
```

### Context Data Missing
**Problem:** `ctx.get()` returns None  
**Solution:** Verify key and that data was stored
```python
await ctx.set("my_key", data)  # Store first
data = await ctx.get("my_key")  # Then retrieve
```

### Workflow Hangs
**Problem:** Workflow never completes  
**Solution:** Ensure final step returns StopEvent
```python
return StopEvent(result=final_result)
```

### Import Errors
**Problem:** Can't import modules  
**Solution:** Check installation
```bash
pip install llama-index llama-index-llms-openai
```

## 📁 File Locations

```
Core Files:
  workflow.py    - Main workflow
  events.py      - Event definitions
  agents.py      - LLM agents
  services.py    - Data services
  main.py        - Entry points

Documentation:
  README.md           - Overview
  QUICK_START.md      - Getting started
  ARCHITECTURE.md     - Deep dive
  COMPARISON.md       - vs Agno
  MIGRATION_GUIDE.md  - Migration help
  TESTING.md          - Testing guide
  INDEX.md            - Doc navigation
  CHEATSHEET.md       - This file

Examples & Tests:
  example.py              - Usage examples
  tests/conftest.py       - Test fixtures
  tests/test_services.py  - Service tests
```

## 🎯 Workflow Steps

```
1. start                    - Entry point
2. analyze_query_step       - Analyze query
3. detect_format_step       - Detect format
4. plan_retrieval_step      - Plan retrieval (conditional)
5. retrieve_data_step       - Retrieve data (conditional)
6. prepare_context_step     - Generate answer
```

## 🔗 Event Flow

```
StartEvent
  ├─> QueryAnalysisEvent
  └─> FormatDetectionEvent
        └─> RetrievalPlanEvent (conditional)
              └─> DataRetrievalEvent
                    └─> WriterContextEvent
                          └─> StopEvent
```

## 💡 Best Practices

1. **Keep events simple** - Just triggers, no data
2. **Use context for data** - Store everything in context
3. **Handle errors** - Try/except in steps
4. **Log extensively** - Track workflow progress
5. **Type hints** - Use them everywhere
6. **Async all the way** - Keep steps async
7. **Test independently** - Test each step alone

## 🔑 Key Concepts

- **Event**: Trigger for a step
- **Step**: Method that processes events
- **Context**: Shared state store
- **Workflow**: Orchestrates all steps
- **StopEvent**: Ends workflow with result

## 📚 Quick Links

- [Full Documentation](./INDEX.md)
- [Architecture Details](./ARCHITECTURE.md)
- [Working Examples](./example.py)
- [Testing Guide](./TESTING.md)
- [Migration Guide](./MIGRATION_GUIDE.md)

## 🆘 Getting Help

1. Check [INDEX.md](./INDEX.md) for navigation
2. Read [ARCHITECTURE.md](./ARCHITECTURE.md) for understanding
3. See [example.py](./example.py) for patterns
4. Review [TESTING.md](./TESTING.md) for debugging

---

**Quick Tip:** Start with [README.md](./README.md) if you're new!
