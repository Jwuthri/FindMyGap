# Getting Started with DSPy Workflow

This guide will help you get started with the DSPy-based workflow implementation.

## Prerequisites

1. Install DSPy:
```bash
pip install dspy-ai
# or with uv
uv pip install dspy-ai
```

2. Ensure you have the required environment variables:
```bash
export OPENAI_API_KEY="your-api-key"
export DATABASE_URL="postgresql://..."
```

## Quick Start

### 1. Run the Example Script

```bash
cd backend
python -m app.dspy_workflow.example
```

This will run several example queries through the workflow.

### 2. Use in Your Code

```python
from app.dspy_workflow.main import run_workflow

# Run a query
result = await run_workflow(
    query="What are the main product gaps for Netflix?",
    user_id=1
)
print(result)
```

### 3. Customize the Workflow

The workflow is defined in `product_gap_workflow.py`. You can:

- Add new modules in `modules/`
- Add new steps in `steps/`
- Modify the workflow logic in `ProductGapWorkflow.forward()`

## Understanding DSPy Concepts

### Signatures

Signatures define the input/output interface for LLM calls:

```python
class MySignature(dspy.Signature):
    """What the LLM should do"""
    
    input_field = dspy.InputField(desc="Description of input")
    output_field = dspy.OutputField(desc="Description of output")
```

### Modules

Modules are composable components that use signatures:

```python
class MyModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(MySignature)
    
    def forward(self, input_value):
        result = self.predictor(input_field=input_value)
        return result.output_field
```

### Predictors

DSPy provides several predictors:

- `dspy.Predict` - Basic LLM call
- `dspy.ChainOfThought` - Adds reasoning steps
- `dspy.ReAct` - Reasoning + Acting pattern
- `dspy.ProgramOfThought` - Generates and executes code

## Workflow Architecture

```
User Query
    ↓
Query Analyzer (determines if data is needed)
    ↓
Output Formatter (determines desired format)
    ↓
[Conditional] Retrieval Planner (generates SQL)
    ↓
[Conditional] Data Retrieval (executes SQL)
    ↓
Answer Writer (generates final response)
    ↓
Final Answer
```

## Adding a New Module

1. Create a new file in `modules/`:

```python
# modules/my_module.py
import dspy
from pydantic import BaseModel, Field

class MyOutput(BaseModel):
    result: str = Field(..., description="The result")

class MySignature(dspy.Signature):
    input_data = dspy.InputField(desc="Input description")
    result = dspy.OutputField(desc="Output description")

class MyModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.process = dspy.ChainOfThought(MySignature)
    
    def forward(self, input_data: str) -> MyOutput:
        result = self.process(input_data=input_data)
        return MyOutput(result=result.result)
```

2. Use it in the workflow:

```python
# product_gap_workflow.py
from app.dspy_workflow.modules.my_module import MyModule

class ProductGapWorkflow(dspy.Module):
    def __init__(self, user_id: Optional[int] = 1):
        super().__init__()
        # ... existing modules
        self.my_module = MyModule()
    
    def forward(self, query: str):
        # ... existing logic
        my_result = self.my_module(input_data=some_data)
        # ... use my_result
```

## Debugging

### Enable DSPy Logging

```python
import dspy
dspy.settings.configure(lm=lm, trace=[])
```

### Add Breakpoints

Since DSPy workflows are just Python code, you can use standard debugging:

```python
def forward(self, query: str):
    analysis = self.query_analyzer(query=query)
    breakpoint()  # Debug here
    # ... rest of workflow
```

### Check Module Outputs

```python
result = self.query_analyzer(query=query)
print(f"Analysis: {result.model_dump()}")
```

## Optimization

DSPy can automatically optimize prompts:

```python
from dspy.teleprompt import BootstrapFewShot

# Define a metric
def validate_answer(example, pred, trace=None):
    return pred.answer and len(pred.answer) > 10

# Create optimizer
optimizer = BootstrapFewShot(metric=validate_answer)

# Optimize the workflow
optimized_workflow = optimizer.compile(
    workflow,
    trainset=training_examples
)
```

## Testing

Create tests in `tests/`:

```python
# tests/test_query_analyzer.py
import pytest
from app.dspy_workflow.modules.query_analyzer import QueryAnalyzer

def test_query_analyzer():
    analyzer = QueryAnalyzer()
    result = analyzer(query="What are the gaps for Netflix?")
    
    assert result.needs_data_retrieval == True
    assert result.company == "Netflix"
```

## Performance Tips

1. **Cache LLM calls** - DSPy supports caching
2. **Truncate data** - Use `utils.truncate_data_for_llm()`
3. **Batch queries** - Process multiple queries together
4. **Use smaller models** - For simple tasks, use gpt-3.5-turbo
5. **Optimize prompts** - Use DSPy optimizers

## Common Issues

### Issue: "No module named 'dspy'"
**Solution**: Install DSPy: `pip install dspy-ai`

### Issue: "OpenAI API key not found"
**Solution**: Set `OPENAI_API_KEY` environment variable

### Issue: "Database connection failed"
**Solution**: Check `DATABASE_URL` in your `.env` file

### Issue: "JSON parsing failed in retrieval planner"
**Solution**: The LLM might not be returning valid JSON. Check the prompt or use a more capable model.

## Next Steps

1. Read the [COMPARISON.md](./COMPARISON.md) to understand differences from Agno
2. Check out [DSPy documentation](https://dspy-docs.vercel.app/)
3. Experiment with different predictors and optimizers
4. Add your own modules and customize the workflow

## Resources

- [DSPy GitHub](https://github.com/stanfordnlp/dspy)
- [DSPy Documentation](https://dspy-docs.vercel.app/)
- [DSPy Examples](https://github.com/stanfordnlp/dspy/tree/main/examples)
