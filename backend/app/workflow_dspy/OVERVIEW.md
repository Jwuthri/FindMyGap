# DSPy Workflow - Complete Overview

This document provides a complete overview of the DSPy-based workflow implementation.

## 📁 Project Structure

```
backend/app/dspy_workflow/
├── __init__.py                  # Package initialization
├── main.py                      # Entry point and workflow execution
├── product_gap_workflow.py      # Main workflow orchestration
├── cli.py                       # Command-line interface
├── example.py                   # Example usage scripts
├── utils.py                     # Utility functions
│
├── modules/                     # DSPy modules (LLM-powered components)
│   ├── __init__.py
│   ├── query_analyzer.py       # Analyze query and determine execution path
│   ├── retrieval_planner.py    # Plan SQL queries for data retrieval
│   ├── output_formatter.py     # Determine desired output format
│   └── answer_writer.py        # Generate final formatted answer
│
├── steps/                       # Non-LLM execution steps
│   ├── __init__.py
│   └── data_retrieval.py       # Execute SQL queries (no LLM)
│
└── docs/                        # Documentation
    ├── README.md               # Main documentation
    ├── GETTING_STARTED.md      # Quick start guide
    ├── COMPARISON.md           # Agno vs DSPy comparison
    └── OVERVIEW.md             # This file
```

## 🎯 What is This?

This is a **DSPy-based implementation** of the product gap detection workflow, created as an alternative to the Agno-based workflow in `backend/app/workflows/`.

### Key Features

- ✅ **Modular Design** - Composable DSPy modules
- ✅ **Type-Safe** - Pydantic models for all data structures
- ✅ **Conditional Execution** - Only retrieves data when needed
- ✅ **Reusable Components** - Shares data retrieval with Agno workflow
- ✅ **Easy to Debug** - Plain Python code, no complex abstractions
- ✅ **Optimizable** - Can use DSPy optimizers to improve prompts

## 🔄 Workflow Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        User Query                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Query Analysis                                      │
│  - Determines if data retrieval is needed                    │
│  - Identifies query type and company                         │
│  - Module: QueryAnalyzer                                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Output Format Detection                             │
│  - Determines desired output format (markdown, json, etc)    │
│  - Module: OutputFormatter                                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
              ┌───────┴────────┐
              │ Needs Data?    │
              └───────┬────────┘
                      │
        ┌─────────────┴─────────────┐
        │ Yes                       │ No
        ▼                           ▼
┌───────────────────┐         ┌─────────────┐
│ Step 3a:          │         │ Skip to     │
│ Retrieval Planning│         │ Step 5      │
│ - Generate SQL    │         └─────────────┘
│ Module:           │
│ RetrievalPlanner  │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Step 3b:          │
│ Data Retrieval    │
│ - Execute SQL     │
│ Step:             │
│ DataRetrievalStep │
└────────┬──────────┘
         │
         └─────────────┬
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 5: Answer Writing                                      │
│  - Generates final formatted answer                          │
│  - Uses query, format, and data (if retrieved)               │
│  - Module: AnswerWriter                                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      Final Answer                            │
└─────────────────────────────────────────────────────────────┘
```

## 🧩 Components

### Modules (LLM-Powered)

| Module | Purpose | Input | Output |
|--------|---------|-------|--------|
| **QueryAnalyzer** | Analyze query and determine execution path | User query | Analysis with routing decisions |
| **OutputFormatter** | Determine desired output format | User query | Format type and reasoning |
| **RetrievalPlanner** | Generate SQL queries for data retrieval | Query + analysis + schemas | SQL queries with reasoning |
| **AnswerWriter** | Generate final formatted answer | Query + analysis + format + data | Final answer |

### Steps (Non-LLM)

| Step | Purpose | Input | Output |
|------|---------|-------|--------|
| **DataRetrievalStep** | Execute SQL queries | Retrieval plan + DB session | Retrieved data |

### Utilities

| Function | Purpose |
|----------|---------|
| `decimal_default()` | JSON serialization for Decimal/date types |
| `format_data_summary()` | Create concise data summaries |
| `truncate_data_for_llm()` | Limit data size for token efficiency |
| `extract_json_from_text()` | Parse JSON from LLM responses |
| `format_schema_for_prompt()` | Format DB schemas for prompts |
| `validate_sql_query()` | Basic SQL safety validation |

## 🚀 Usage

### Command Line

```bash
# Single query
python -m app.dspy_workflow.cli "What are the gaps for Netflix?"

# Interactive mode
python -m app.dspy_workflow.cli --interactive

# Specify user ID
python -m app.dspy_workflow.cli --user-id 2 "Show me reviews"
```

### Python Code

```python
from app.dspy_workflow.main import run_workflow

# Run a query
result = await run_workflow(
    query="What are the main product gaps for Netflix?",
    user_id=1
)
print(result)
```

### Examples

```bash
# Run example queries
python -m app.dspy_workflow.example
```

## 🔧 Configuration

DSPy is configured in `main.py`:

```python
lm = dspy.OpenAI(
    model="gpt-4o-mini",
    api_key=SETTINGS.OPENAI_API_KEY,
    max_tokens=4000
)
dspy.settings.configure(lm=lm)
```

You can change:
- **Model**: `gpt-4o-mini`, `gpt-4`, `gpt-3.5-turbo`, etc.
- **Max tokens**: Adjust based on your needs
- **Temperature**: Add `temperature=0.7` for more creative responses

## 📊 Comparison with Agno Workflow

| Aspect | Agno | DSPy |
|--------|------|------|
| **Abstraction** | High (Workflow, Step, Condition) | Low (Plain Python) |
| **Streaming** | Built-in event streaming | Manual logging |
| **Debugging** | Complex (event-based) | Simple (standard Python) |
| **Flexibility** | Declarative configuration | Imperative code |
| **Optimization** | Manual | Automatic (DSPy optimizers) |
| **Learning Curve** | Steeper (framework-specific) | Gentler (Python + DSPy basics) |

See [COMPARISON.md](./COMPARISON.md) for detailed comparison.

## 🎓 Learning Resources

### DSPy Basics

1. **Signatures** - Define LLM input/output interfaces
2. **Modules** - Composable components using signatures
3. **Predictors** - Different ways to call LLMs (Predict, ChainOfThought, ReAct)
4. **Optimizers** - Automatically improve prompts

### Documentation

- [README.md](./README.md) - Main documentation
- [GETTING_STARTED.md](./GETTING_STARTED.md) - Quick start guide
- [COMPARISON.md](./COMPARISON.md) - Agno vs DSPy comparison
- [DSPy Official Docs](https://dspy-docs.vercel.app/)

## 🧪 Testing

```bash
# Run tests (when created)
pytest backend/tests/dspy_workflow/

# Test individual modules
python -c "
from app.dspy_workflow.modules.query_analyzer import QueryAnalyzer
analyzer = QueryAnalyzer()
result = analyzer(query='What are the gaps for Netflix?')
print(result)
"
```

## 🐛 Debugging

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Add Breakpoints

```python
def forward(self, query: str):
    analysis = self.query_analyzer(query=query)
    breakpoint()  # Inspect here
    # ...
```

### Print Intermediate Results

```python
result = self.query_analyzer(query=query)
print(f"Analysis: {result.model_dump_json(indent=2)}")
```

## 🔮 Future Enhancements

### Planned Features

- [ ] NLP analysis modules (sentiment, clustering, etc.)
- [ ] DSPy optimizer integration
- [ ] Evaluation metrics and benchmarks
- [ ] Caching layer for LLM calls
- [ ] Parallel execution of independent steps
- [ ] Streaming support for long-running queries
- [ ] Integration tests
- [ ] Performance benchmarks vs Agno

### Optimization Opportunities

1. **Prompt Optimization** - Use DSPy optimizers to improve prompts
2. **Caching** - Cache LLM responses for repeated queries
3. **Batching** - Process multiple queries together
4. **Model Selection** - Use smaller models for simple tasks
5. **Data Truncation** - Limit data size to reduce tokens

## 📝 Contributing

### Adding a New Module

1. Create file in `modules/`
2. Define Pydantic output model
3. Define DSPy signature
4. Create DSPy module class
5. Add to workflow in `product_gap_workflow.py`

### Adding a New Step

1. Create file in `steps/`
2. Define step class with `__call__` method
3. Add to workflow in `product_gap_workflow.py`

### Adding Tests

1. Create test file in `backend/tests/dspy_workflow/`
2. Use pytest fixtures for setup
3. Test individual modules and full workflow

## 🤝 Support

For questions or issues:

1. Check [GETTING_STARTED.md](./GETTING_STARTED.md)
2. Review [COMPARISON.md](./COMPARISON.md)
3. Check DSPy documentation
4. Ask the team

## 📄 License

Same as the main project.

---

**Happy coding with DSPy! 🎉**
