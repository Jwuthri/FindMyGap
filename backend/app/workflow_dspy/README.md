# DSPy Workflow

This folder contains a DSPy-based implementation of the product gap detection workflow, as an alternative to the Agno-based workflow in `app/workflows/`.

## Architecture

The DSPy workflow follows a similar structure to the Agno workflow but uses DSPy's programming model:

### Key Differences from Agno Workflow

| Aspect | Agno Workflow | DSPy Workflow |
|--------|---------------|---------------|
| **Agents** | `Agent` classes with tools | `dspy.Module` with `dspy.Signature` |
| **Workflow** | `Workflow` with `Step`, `Condition`, `Parallel` | Custom `dspy.Module` with conditional logic |
| **Streaming** | Built-in event streaming | Manual logging |
| **Tools** | Agent tools with function calling | Direct Python function calls |
| **Output** | Structured via `output_schema` | Structured via `dspy.OutputField` |

## Structure

```
dspy_workflow/
├── __init__.py
├── main.py                      # Entry point, workflow execution
├── product_gap_workflow.py      # Main workflow orchestration
├── modules/                     # DSPy modules (equivalent to agents)
│   ├── __init__.py
│   ├── query_analyzer.py       # Analyze query and determine path
│   ├── retrieval_planner.py    # Plan SQL queries
│   ├── output_formatter.py     # Determine output format
│   └── answer_writer.py        # Generate final answer
└── steps/                       # Non-LLM execution steps
    ├── __init__.py
    └── data_retrieval.py       # Execute SQL queries
```

## Workflow Steps

1. **Query Analysis** - Determine if data retrieval is needed
2. **Output Format Detection** - Determine desired output format
3. **Retrieval Planning** (conditional) - Generate SQL queries
4. **Data Retrieval** (conditional) - Execute queries
5. **Answer Writing** - Generate final formatted response

## Usage

```python
from app.dspy_workflow.main import run_workflow

# Run the workflow
result = await run_workflow(
    query="What are the main product gaps for Netflix?",
    user_id=1
)
print(result)
```

## DSPy Concepts

### Signatures
DSPy signatures define the input/output interface for LLM calls:

```python
class QueryAnalysisSignature(dspy.Signature):
    query = dspy.InputField(desc="User's question")
    needs_data_retrieval = dspy.OutputField(desc="Whether data retrieval is needed")
```

### Modules
DSPy modules are composable components that use signatures:

```python
class QueryAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.analyze = dspy.ChainOfThought(QueryAnalysisSignature)
    
    def forward(self, query: str):
        return self.analyze(query=query)
```

### ChainOfThought
`dspy.ChainOfThought` adds reasoning steps before generating output, similar to Agno's reasoning.

## Configuration

DSPy is configured in `main.py`:

```python
lm = dspy.OpenAI(
    model="gpt-4o-mini",
    api_key=SETTINGS.OPENAI_API_KEY,
    max_tokens=4000
)
dspy.settings.configure(lm=lm)
```

## Benefits of DSPy

1. **Programmatic** - Workflows are Python code, not configuration
2. **Composable** - Modules can be easily reused and combined
3. **Optimizable** - DSPy can optimize prompts automatically
4. **Type-safe** - Strong typing with Pydantic models
5. **Lightweight** - Minimal abstraction over LLM calls

## Future Enhancements

- Add DSPy optimizers (e.g., `BootstrapFewShot`)
- Implement NLP analysis modules
- Add evaluation metrics
- Create compiled/optimized versions of modules
