# Agno vs LlamaIndex Workflow Comparison

## Architecture Comparison

### Agno Workflow
```python
from agno.workflow.workflow import Workflow
from agno.workflow.step import Step
from agno.workflow.condition import Condition
from agno.workflow.parallel import Parallel

workflow = Workflow(
    steps=[
        Parallel(step1, step2),
        Condition(evaluator=func, steps=[step3]),
        step4
    ]
)
```

### LlamaIndex Workflow
```python
from llama_index.core.workflow import Workflow, step, Context

class MyWorkflow(Workflow):
    @step
    async def step1(self, ctx: Context, ev: Event1) -> Event2:
        # Logic here
        return Event2(data=result)
```

## Key Differences

### 1. Step Definition

**Agno:**
- Steps defined as `Step` objects with agents or executors
- Explicit step ordering in workflow definition
- Uses `StepInput` and `StepOutput` for data passing

**LlamaIndex:**
- Steps defined as methods with `@step` decorator
- Implicit ordering via event routing
- Uses typed `Event` objects for data passing

### 2. Conditional Execution

**Agno:**
```python
Condition(
    evaluator=needs_data_retrieval,
    steps=[retrieval_step]
)
```

**LlamaIndex:**
```python
@step
async def analyze(self, ctx: Context, ev: AnalysisEvent) -> RetrievalEvent | None:
    if needs_retrieval:
        return RetrievalEvent()
    return None
```

### 3. Parallel Execution

**Agno:**
```python
Parallel(
    query_analysis_step,
    format_detection_step
)
```

**LlamaIndex:**
```python
@step
async def start(self, ctx: Context, ev: StartEvent):
    ctx.send_event(QueryEvent())
    ctx.send_event(FormatEvent())
```

### 4. Context Management

**Agno:**
- Uses `previous_step_outputs` dictionary
- Accessed via step names

**LlamaIndex:**
- Uses `Context` object with `get`/`set` methods
- Type-safe context storage

### 5. Agent Integration

**Agno:**
```python
Step(
    name="QueryAnalysis",
    agent=query_analyzer,
    output_schema=QueryAnalysis
)
```

**LlamaIndex:**
```python
@step
async def analyze_query(self, ctx: Context, ev: QueryEvent):
    llm = OpenAI()
    result = await llm.astructured_predict(QueryAnalysis, messages)
    return AnalysisEvent(result=result)
```

## Pros and Cons

### Agno Workflow

**Pros:**
- Declarative workflow definition
- Clear step ordering
- Built-in parallel and conditional constructs
- Integrated with Agno agents

**Cons:**
- More boilerplate for simple workflows
- Less flexible event routing
- Tighter coupling to Agno ecosystem

### LlamaIndex Workflow

**Pros:**
- More flexible event-driven architecture
- Cleaner code for complex routing logic
- Better type safety with events
- Part of larger LlamaIndex ecosystem
- Built-in observability and streaming

**Cons:**
- Less explicit workflow structure
- Requires understanding event routing
- More manual context management

## When to Use Each

### Use Agno When:
- You need tight integration with Agno agents and teams
- You prefer declarative workflow definitions
- You want built-in parallel/conditional constructs
- Your workflow has a clear linear structure

### Use LlamaIndex When:
- You need complex event routing logic
- You want better integration with LlamaIndex tools
- You prefer event-driven architecture
- You need advanced observability features
- Your workflow has dynamic branching

## Migration Path

To migrate from Agno to LlamaIndex:

1. Convert `Step` objects to `@step` methods
2. Replace `StepInput`/`StepOutput` with custom `Event` classes
3. Convert `Condition` evaluators to conditional returns
4. Replace `Parallel` with `ctx.send_event()` calls
5. Update agent calls to use LlamaIndex LLM interface
6. Migrate context access from `previous_step_outputs` to `Context`

## Performance Considerations

- **Agno**: Optimized for agent-based workflows with built-in caching
- **LlamaIndex**: More flexible but may require manual optimization
- Both support async execution
- LlamaIndex has better streaming support out of the box
