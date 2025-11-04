# Migration Guide: Agno to LlamaIndex Workflows

This guide helps you migrate from the Agno workflow implementation to LlamaIndex workflows.

## Overview of Changes

### Architecture Shift

**Agno:** Declarative workflow with explicit step ordering
**LlamaIndex:** Event-driven workflow with implicit ordering via events

### Key Concept Mapping

| Agno Concept | LlamaIndex Equivalent |
|--------------|----------------------|
| `Workflow` | `Workflow` (class-based) |
| `Step` | `@step` decorated method |
| `StepInput` | `Event` + `Context` |
| `StepOutput` | `Event` (emitted) |
| `Condition` | Conditional event emission |
| `Parallel` | Multiple `ctx.send_event()` calls |
| `previous_step_outputs` | `Context.get()` |

## Step-by-Step Migration

### 1. Convert Workflow Class

**Before (Agno):**
```python
from agno.workflow.workflow import Workflow
from agno.workflow.step import Step

workflow = Workflow(
    name="My Workflow",
    steps=[step1, step2, step3]
)
```

**After (LlamaIndex):**
```python
from llama_index.core.workflow import Workflow, step

class MyWorkflow(Workflow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize any workflow-level state
```

### 2. Convert Steps

**Before (Agno):**
```python
def my_executor(step_input: StepInput) -> StepOutput:
    data = step_input.previous_step_outputs.get("previous_step")
    result = process(data)
    return StepOutput(content=result)

my_step = Step(
    name="MyStep",
    executor=my_executor
)
```

**After (LlamaIndex):**
```python
@step
async def my_step(self, ctx: Context, ev: MyStepEvent):
    data = await ctx.get("previous_data")
    result = process(data)
    await ctx.set("my_result", result)
    ctx.send_event(NextStepEvent())
```

### 3. Convert Agent Steps

**Before (Agno):**
```python
from agno.agent import Agent

agent = Agent(
    name="Query Analyzer",
    model=model,
    output_schema=QueryAnalysis
)

step = Step(
    name="QueryAnalysis",
    agent=agent
)
```

**After (LlamaIndex):**
```python
from llama_index.llms.openai import OpenAI

@step
async def analyze_query(self, ctx: Context, ev: QueryEvent):
    llm = OpenAI(model="gpt-4o-mini")
    query = await ctx.get("query")
    
    result = await llm.astructured_predict(
        QueryAnalysis,
        messages=[...]
    )
    
    await ctx.set("analysis", result)
    ctx.send_event(NextEvent())
```

### 4. Convert Conditional Execution

**Before (Agno):**
```python
def needs_data(step_input: StepInput) -> bool:
    analysis = step_input.previous_step_outputs.get("analysis")
    return analysis.needs_data

Condition(
    evaluator=needs_data,
    steps=[data_retrieval_step]
)
```

**After (LlamaIndex):**
```python
@step
async def check_needs_data(self, ctx: Context, ev: CheckEvent):
    analysis = await ctx.get("analysis")
    
    if analysis.needs_data:
        ctx.send_event(DataRetrievalEvent())
    else:
        ctx.send_event(SkipDataEvent())
```

### 5. Convert Parallel Execution

**Before (Agno):**
```python
Parallel(
    query_analysis_step,
    format_detection_step
)
```

**After (LlamaIndex):**
```python
@step
async def start_parallel(self, ctx: Context, ev: StartEvent):
    # These execute in parallel
    ctx.send_event(QueryAnalysisEvent())
    ctx.send_event(FormatDetectionEvent())
```

### 6. Convert Context Access

**Before (Agno):**
```python
def my_executor(step_input: StepInput) -> StepOutput:
    prev_data = step_input.previous_step_outputs.get("StepName")
    result = process(prev_data.content)
    return StepOutput(content=result)
```

**After (LlamaIndex):**
```python
@step
async def my_step(self, ctx: Context, ev: MyEvent):
    prev_data = await ctx.get("step_data")
    result = process(prev_data)
    await ctx.set("result", result)
    ctx.send_event(NextEvent())
```

## Complete Example

### Agno Version

```python
from agno.workflow.workflow import Workflow
from agno.workflow.step import Step
from agno.workflow.condition import Condition

def analyze(step_input: StepInput) -> StepOutput:
    return StepOutput(content={"needs_data": True})

def retrieve(step_input: StepInput) -> StepOutput:
    return StepOutput(content={"data": [1, 2, 3]})

def needs_data(step_input: StepInput) -> bool:
    return step_input.previous_step_outputs.get("Analyze").content["needs_data"]

workflow = Workflow(
    steps=[
        Step(name="Analyze", executor=analyze),
        Condition(
            evaluator=needs_data,
            steps=[Step(name="Retrieve", executor=retrieve)]
        )
    ]
)
```

### LlamaIndex Version

```python
from llama_index.core.workflow import Workflow, step, Context, StartEvent, StopEvent

class AnalyzeEvent(Event):
    pass

class RetrieveEvent(Event):
    pass

class MyWorkflow(Workflow):
    @step
    async def analyze(self, ctx: Context, ev: StartEvent | AnalyzeEvent):
        result = {"needs_data": True}
        await ctx.set("analysis", result)
        
        if result["needs_data"]:
            ctx.send_event(RetrieveEvent())
        else:
            return StopEvent(result="Done")
    
    @step
    async def retrieve(self, ctx: Context, ev: RetrieveEvent):
        data = {"data": [1, 2, 3]}
        await ctx.set("retrieved_data", data)
        return StopEvent(result=data)
```

## Common Patterns

### Pattern 1: Sequential Steps

**Agno:**
```python
Workflow(steps=[step1, step2, step3])
```

**LlamaIndex:**
```python
@step
async def step1(self, ctx, ev: StartEvent):
    # ...
    ctx.send_event(Step2Event())

@step
async def step2(self, ctx, ev: Step2Event):
    # ...
    ctx.send_event(Step3Event())

@step
async def step3(self, ctx, ev: Step3Event):
    # ...
    return StopEvent(result=...)
```

### Pattern 2: Conditional Branch

**Agno:**
```python
Condition(evaluator=check, steps=[branch_step])
```

**LlamaIndex:**
```python
@step
async def check_and_branch(self, ctx, ev):
    if condition:
        ctx.send_event(BranchEvent())
    else:
        ctx.send_event(SkipEvent())
```

### Pattern 3: Parallel + Join

**Agno:**
```python
Parallel(step1, step2)  # Automatically joins
```

**LlamaIndex:**
```python
@step
async def start_parallel(self, ctx, ev):
    ctx.send_event(Task1Event())
    ctx.send_event(Task2Event())

@step
async def task1(self, ctx, ev: Task1Event):
    # ...
    await ctx.set("task1_done", True)
    self._check_all_done(ctx)

@step
async def task2(self, ctx, ev: Task2Event):
    # ...
    await ctx.set("task2_done", True)
    self._check_all_done(ctx)

async def _check_all_done(self, ctx):
    task1 = await ctx.get("task1_done", default=False)
    task2 = await ctx.get("task2_done", default=False)
    if task1 and task2:
        ctx.send_event(JoinEvent())
```

## Testing Changes

### Agno Tests

```python
def test_step():
    step_input = StepInput(input="test", previous_step_outputs={})
    result = my_executor(step_input)
    assert result.content == expected
```

### LlamaIndex Tests

```python
@pytest.mark.asyncio
async def test_step():
    workflow = MyWorkflow()
    ctx = MagicMock(spec=Context)
    ctx.get = AsyncMock(return_value="test")
    ctx.set = AsyncMock()
    
    await workflow.my_step(ctx, MyEvent())
    
    ctx.set.assert_called_once()
```

## Checklist

- [ ] Convert `Workflow` to class-based `Workflow`
- [ ] Convert `Step` objects to `@step` methods
- [ ] Define `Event` classes for each step trigger
- [ ] Replace `StepInput`/`StepOutput` with `Context` operations
- [ ] Convert `Condition` to conditional event emission
- [ ] Convert `Parallel` to multiple `send_event()` calls
- [ ] Update agent calls to use LlamaIndex LLM interface
- [ ] Update tests to use async and mock Context
- [ ] Add type hints to all steps
- [ ] Update documentation

## Troubleshooting

### Issue: Steps not executing

**Cause:** No event emitted to trigger the step

**Solution:** Make sure previous step emits the correct event:
```python
ctx.send_event(NextStepEvent())
```

### Issue: Context data not available

**Cause:** Data not stored in context or wrong key

**Solution:** Verify data is stored and key matches:
```python
await ctx.set("my_key", data)
# Later...
data = await ctx.get("my_key")
```

### Issue: Workflow hangs

**Cause:** No `StopEvent` returned

**Solution:** Make sure final step returns `StopEvent`:
```python
return StopEvent(result=final_result)
```

## Benefits of Migration

1. **More Flexible**: Event-driven architecture allows complex routing
2. **Better Type Safety**: Events are typed, reducing errors
3. **Easier Testing**: Steps can be tested independently
4. **Built-in Streaming**: Native support for streaming events
5. **Better Observability**: Built-in event tracking and logging
6. **Ecosystem**: Access to LlamaIndex tools and integrations

## Need Help?

- Check [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed architecture
- See [example.py](./example.py) for working examples
- Review [TESTING.md](./TESTING.md) for testing patterns
