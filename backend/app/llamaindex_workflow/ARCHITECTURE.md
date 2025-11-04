# LlamaIndex Workflow Architecture

## Overview

This implementation uses LlamaIndex's event-driven workflow system to replicate the product gap detection workflow originally built with Agno.

## Core Concepts

### 1. Events

Events are the primary mechanism for communication between workflow steps. Each event triggers specific steps that are registered to handle it.

```python
class QueryAnalysisEvent(Event):
    """Trigger event for query analysis step."""
    pass
```

Events are lightweight triggers. Data is passed via the `Context` object, not the events themselves.

### 2. Steps

Steps are methods decorated with `@step` that process events and optionally emit new events.

```python
@step
async def analyze_query_step(self, ctx: Context, ev: QueryAnalysisEvent):
    query = await ctx.get("query")
    analysis = await analyze_query(query)
    await ctx.set("query_analysis", analysis)
    
    if analysis.needs_data_retrieval:
        ctx.send_event(RetrievalPlanEvent())
```

### 3. Context

The `Context` object is a shared state store that persists across all steps in a workflow run.

```python
# Store data
await ctx.set("key", value)

# Retrieve data
value = await ctx.get("key")

# With default
value = await ctx.get("key", default=None)
```

### 4. Event Routing

Steps can emit events to trigger other steps:

```python
# Send a single event
ctx.send_event(NextStepEvent())

# Send multiple events (parallel execution)
ctx.send_event(Event1())
ctx.send_event(Event2())
```

## Workflow Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        StartEvent                            │
│                     (query: string)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ├──────────────────┬─────────────────┐
                         │                  │                 │
                         ▼                  ▼                 │
              ┌──────────────────┐ ┌──────────────────┐      │
              │ Query Analysis   │ │ Format Detection │      │
              │                  │ │                  │      │
              └────────┬─────────┘ └────────┬─────────┘      │
                       │                    │                │
                       │ (if needs data)    │                │
                       ▼                    │                │
              ┌──────────────────┐          │                │
              │ Retrieval Plan   │          │                │
              │                  │          │                │
              └────────┬─────────┘          │                │
                       │                    │                │
                       ▼                    │                │
              ┌──────────────────┐          │                │
              │ Data Retrieval   │          │                │
              │                  │          │                │
              └────────┬─────────┘          │                │
                       │                    │                │
                       └────────┬───────────┘                │
                                │                            │
                                ▼                            │
                       ┌──────────────────┐                  │
                       │ Prepare Context  │◄─────────────────┘
                       │                  │
                       └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Generate Answer  │
                       │                  │
                       └────────┬─────────┘
                                │
                                ▼
                         ┌─────────────┐
                         │  StopEvent  │
                         │  (result)   │
                         └─────────────┘
```

## Step Details

### 1. Start Step

**Trigger:** `StartEvent(query=str)`

**Actions:**
- Stores query in context
- Emits `QueryAnalysisEvent` and `FormatDetectionEvent` in parallel

**Context Updates:**
- `query`: User's input query

### 2. Query Analysis Step

**Trigger:** `QueryAnalysisEvent`

**Actions:**
- Analyzes query using LLM
- Determines if data retrieval is needed
- Determines if NLP analysis is needed
- Conditionally emits `RetrievalPlanEvent`

**Context Updates:**
- `query_analysis`: QueryAnalysis object

### 3. Format Detection Step

**Trigger:** `FormatDetectionEvent`

**Actions:**
- Detects desired output format using LLM
- Stores format information

**Context Updates:**
- `format_info`: FormatDetection object

### 4. Retrieval Planning Step

**Trigger:** `RetrievalPlanEvent`

**Actions:**
- Creates SQL queries based on query and available schemas
- Emits `DataRetrievalEvent`

**Context Updates:**
- `retrieval_plan`: Dict with SQL queries and reasoning

### 5. Data Retrieval Step

**Trigger:** `DataRetrievalEvent`

**Actions:**
- Executes SQL queries
- Formats results
- Emits `WriterContextEvent`

**Context Updates:**
- `retrieved_data`: Dict with data, total_rows, format, etc.

### 6. Prepare Context & Generate Answer Step

**Trigger:** `WriterContextEvent`

**Actions:**
- Gathers all context (query, format, data, analysis)
- Generates final answer using LLM
- Returns `StopEvent` with result

**Context Reads:**
- `query`
- `format_info`
- `retrieved_data`
- `query_analysis`

## Conditional Execution

Conditional logic is implemented via event emission:

```python
@step
async def analyze_query_step(self, ctx: Context, ev: QueryAnalysisEvent):
    analysis = await analyze_query(query)
    
    # Only emit next event if condition is met
    if analysis.needs_data_retrieval:
        ctx.send_event(RetrievalPlanEvent())
    # If not emitted, that branch doesn't execute
```

## Parallel Execution

Parallel execution happens when multiple events are emitted:

```python
@step
async def start(self, ctx: Context, ev: StartEvent):
    # These run in parallel
    ctx.send_event(QueryAnalysisEvent())
    ctx.send_event(FormatDetectionEvent())
```

## Error Handling

Errors can be caught at the step level:

```python
@step
async def retrieve_data_step(self, ctx: Context, ev: DataRetrievalEvent):
    try:
        result = service.execute_retrieval_plan(plan)
        await ctx.set("retrieved_data", result)
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        await ctx.set("retrieval_error", str(e))
    
    ctx.send_event(WriterContextEvent())
```

## Observability

LlamaIndex workflows have built-in observability:

```python
# Enable verbose logging
workflow = ProductGapWorkflow(verbose=True)

# Stream events
async for event in workflow.stream_events(query="..."):
    print(f"Event: {event}")
```

## Extending the Workflow

### Adding a New Step

1. Define an event:
```python
class MyNewEvent(Event):
    pass
```

2. Create a step:
```python
@step
async def my_new_step(self, ctx: Context, ev: MyNewEvent):
    # Your logic here
    result = do_something()
    await ctx.set("my_result", result)
    ctx.send_event(NextEvent())
```

3. Emit the event from another step:
```python
@step
async def previous_step(self, ctx: Context, ev: PreviousEvent):
    # ...
    ctx.send_event(MyNewEvent())
```

### Adding Conditional Logic

```python
@step
async def conditional_step(self, ctx: Context, ev: TriggerEvent):
    condition = check_condition()
    
    if condition:
        ctx.send_event(PathAEvent())
    else:
        ctx.send_event(PathBEvent())
```

### Adding Parallel Branches

```python
@step
async def parallel_step(self, ctx: Context, ev: TriggerEvent):
    # All these run in parallel
    ctx.send_event(Task1Event())
    ctx.send_event(Task2Event())
    ctx.send_event(Task3Event())
```

## Best Practices

1. **Keep Events Simple**: Events should be lightweight triggers, not data carriers
2. **Use Context for Data**: Store all data in context, not in events
3. **Handle Errors Gracefully**: Catch exceptions and store error info in context
4. **Log Extensively**: Use logger to track workflow progress
5. **Type Hints**: Use type hints for better IDE support
6. **Async All the Way**: Keep all steps async for better performance
7. **Test Steps Independently**: Each step should be testable in isolation

## Performance Considerations

- **Parallel Execution**: Use `ctx.send_event()` multiple times for parallel tasks
- **Context Size**: Keep context data reasonable in size
- **Database Sessions**: Always close sessions in finally blocks
- **Timeouts**: Set appropriate timeouts for long-running workflows
- **Caching**: Consider caching expensive operations in context

## Debugging Tips

1. **Enable Verbose Mode**: `workflow = ProductGapWorkflow(verbose=True)`
2. **Check Context**: Log context state at each step
3. **Event Tracing**: Use `stream_events()` to see event flow
4. **Step Isolation**: Test individual steps with mock context
5. **Breakpoints**: Use debugger to inspect context and events
