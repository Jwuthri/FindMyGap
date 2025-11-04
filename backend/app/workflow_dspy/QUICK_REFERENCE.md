# DSPy Workflow - Quick Reference

## 🚀 Quick Start

```bash
# Install DSPy
pip install dspy-ai

# Run example
python -m app.dspy_workflow.example

# Run CLI
python -m app.dspy_workflow.cli "Your query here"

# Interactive mode
python -m app.dspy_workflow.cli --interactive
```

## 📂 File Structure

```
dspy_workflow/
├── main.py                    # Entry point
├── product_gap_workflow.py    # Main workflow
├── cli.py                     # CLI tool
├── example.py                 # Examples
├── utils.py                   # Utilities
├── modules/                   # LLM modules
│   ├── query_analyzer.py
│   ├── retrieval_planner.py
│   ├── output_formatter.py
│   └── answer_writer.py
└── steps/                     # Non-LLM steps
    └── data_retrieval.py
```

## 🧩 Core Components

### Modules (LLM-Powered)

```python
# Query Analyzer
from app.dspy_workflow.modules.query_analyzer import QueryAnalyzer
analyzer = QueryAnalyzer()
result = analyzer(query="Your query")

# Retrieval Planner
from app.dspy_workflow.modules.retrieval_planner import RetrievalPlanner
planner = RetrievalPlanner(table_schemas=schemas)
plan = planner(query="Your query", analysis="Analysis text")

# Output Formatter
from app.dspy_workflow.modules.output_formatter import OutputFormatter
formatter = OutputFormatter()
format_info = formatter(query="Your query")

# Answer Writer
from app.dspy_workflow.modules.answer_writer import AnswerWriter
writer = AnswerWriter()
answer = writer(query="Your query", analysis=analysis, output_format=format_info, data=data)
```

### Steps (Non-LLM)

```python
# Data Retrieval
from app.dspy_workflow.steps.data_retrieval import DataRetrievalStep
retrieval = DataRetrievalStep()
data = retrieval(plan=plan, db_session=session)
```

## 🔧 DSPy Patterns

### Define a Signature

```python
import dspy

class MySignature(dspy.Signature):
    """What the LLM should do"""
    input_field = dspy.InputField(desc="Input description")
    output_field = dspy.OutputField(desc="Output description")
```

### Create a Module

```python
class MyModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(MySignature)
    
    def forward(self, input_value):
        result = self.predictor(input_field=input_value)
        return result.output_field
```

### Use Different Predictors

```python
# Basic prediction
self.predict = dspy.Predict(MySignature)

# With reasoning
self.cot = dspy.ChainOfThought(MySignature)

# ReAct pattern
self.react = dspy.ReAct(MySignature)

# Program of Thought
self.pot = dspy.ProgramOfThought(MySignature)
```

## 🎯 Common Tasks

### Run a Query

```python
from app.dspy_workflow.main import run_workflow

result = await run_workflow(
    query="What are the gaps for Netflix?",
    user_id=1
)
```

### Configure DSPy

```python
import dspy
from app.config import SETTINGS

lm = dspy.OpenAI(
    model="gpt-4o-mini",
    api_key=SETTINGS.OPENAI_API_KEY,
    max_tokens=4000,
    temperature=0.7  # Optional
)
dspy.settings.configure(lm=lm)
```

### Add Logging

```python
from app import get_logger

logger = get_logger(__name__)
logger.info("Your message")
logger.error("Error message", exc_info=True)
```

## 🔍 Debugging

```python
# Add breakpoint
breakpoint()

# Print intermediate results
print(f"Result: {result.model_dump_json(indent=2)}")

# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Utilities

```python
from app.dspy_workflow.utils import (
    decimal_default,           # JSON serialization
    format_data_summary,       # Data summaries
    truncate_data_for_llm,     # Limit data size
    extract_json_from_text,    # Parse JSON from text
    format_schema_for_prompt,  # Format DB schemas
    validate_sql_query         # SQL validation
)

# Example usage
summary = format_data_summary(data)
truncated = truncate_data_for_llm(data, max_rows=100)
json_obj = extract_json_from_text(llm_response)
```

## 🧪 Testing

```python
# Test a module
from app.dspy_workflow.modules.query_analyzer import QueryAnalyzer

def test_query_analyzer():
    analyzer = QueryAnalyzer()
    result = analyzer(query="What are the gaps for Netflix?")
    assert result.needs_data_retrieval == True
    assert result.company == "Netflix"
```

## 📝 Environment Variables

```bash
# Required
export OPENAI_API_KEY="your-api-key"
export DATABASE_URL="postgresql://user:pass@host:port/db"

# Optional
export LOG_LEVEL="INFO"
```

## 🆚 Agno vs DSPy

| Feature | Agno | DSPy |
|---------|------|------|
| Workflow | Declarative | Imperative |
| Streaming | ✅ Built-in | ❌ Manual |
| Debugging | Complex | Simple |
| Optimization | Manual | Automatic |
| Learning Curve | Steep | Gentle |

## 📚 Documentation

- [README.md](./README.md) - Main docs
- [GETTING_STARTED.md](./GETTING_STARTED.md) - Quick start
- [COMPARISON.md](./COMPARISON.md) - Agno vs DSPy
- [OVERVIEW.md](./OVERVIEW.md) - Complete overview

## 🔗 External Resources

- [DSPy Docs](https://dspy-docs.vercel.app/)
- [DSPy GitHub](https://github.com/stanfordnlp/dspy)
- [DSPy Examples](https://github.com/stanfordnlp/dspy/tree/main/examples)

## 💡 Tips

1. **Start Simple** - Begin with basic modules, add complexity later
2. **Use ChainOfThought** - Better results than basic Predict
3. **Validate Outputs** - Always check LLM responses
4. **Cache Calls** - Avoid redundant LLM calls
5. **Truncate Data** - Keep token usage reasonable
6. **Test Modules** - Test each module independently
7. **Log Everything** - Helps with debugging
8. **Use Type Hints** - Makes code more maintainable

## ⚠️ Common Pitfalls

1. **Forgetting to configure DSPy** - Call `dspy.settings.configure(lm=lm)` first
2. **Not handling JSON parsing errors** - LLMs don't always return valid JSON
3. **Token limits** - Truncate large datasets
4. **SQL injection** - Always validate SQL queries
5. **Missing error handling** - Wrap LLM calls in try/except

## 🎯 Next Steps

1. Read [GETTING_STARTED.md](./GETTING_STARTED.md)
2. Run [example.py](./example.py)
3. Try the [CLI](./cli.py)
4. Customize modules for your use case
5. Add tests
6. Optimize with DSPy optimizers

---

**Need help?** Check the full documentation or ask the team!
