# Testing Guide

## Unit Testing Steps

### Testing Individual Steps

Each step can be tested independently by mocking the context and events:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from llama_index.core.workflow import Context

from app.llamaindex_workflow.workflow import ProductGapWorkflow
from app.llamaindex_workflow.events import QueryAnalysisEvent


@pytest.mark.asyncio
async def test_analyze_query_step():
    """Test query analysis step."""
    # Create workflow instance
    workflow = ProductGapWorkflow(user_id=1)
    
    # Mock context
    ctx = MagicMock(spec=Context)
    ctx.get = AsyncMock(return_value="What are the product gaps?")
    ctx.set = AsyncMock()
    ctx.send_event = MagicMock()
    
    # Create event
    event = QueryAnalysisEvent()
    
    # Execute step
    await workflow.analyze_query_step(ctx, event)
    
    # Verify context was updated
    ctx.set.assert_called_once()
    call_args = ctx.set.call_args[0]
    assert call_args[0] == "query_analysis"
    
    # Verify event was sent if needed
    # ctx.send_event.assert_called()
```

### Testing Agents

```python
import pytest
from app.llamaindex_workflow.agents import analyze_query


@pytest.mark.asyncio
async def test_analyze_query():
    """Test query analysis agent."""
    query = "What are the main product gaps for Netflix?"
    
    result = await analyze_query(query)
    
    assert result.needs_data_retrieval is True
    assert result.company == "Netflix"
    assert result.query_type in ["data_only", "analysis", "general"]
```

### Testing Services

```python
import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from app.llamaindex_workflow.services import DataRetrievalService


def test_execute_sql_query():
    """Test SQL query execution."""
    # Mock database session
    db = MagicMock(spec=Session)
    
    # Mock query result
    mock_result = MagicMock()
    mock_result.keys.return_value = ["id", "name"]
    mock_result.__iter__.return_value = [
        (1, "Test 1"),
        (2, "Test 2")
    ]
    db.execute.return_value = mock_result
    
    # Create service
    service = DataRetrievalService(db)
    
    # Execute query
    results = service.execute_sql_query("SELECT * FROM test")
    
    # Verify results
    assert len(results) == 2
    assert results[0] == {"id": 1, "name": "Test 1"}
```

## Integration Testing

### Testing Full Workflow

```python
import pytest
from app.llamaindex_workflow.main import run_workflow


@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_workflow():
    """Test complete workflow execution."""
    query = "What are the main product gaps for Netflix?"
    
    result = await run_workflow(query, user_id=1)
    
    assert result is not None
    assert len(result) > 0
    assert "Netflix" in result or "product" in result.lower()
```

### Testing Conditional Paths

```python
@pytest.mark.asyncio
async def test_workflow_with_data_retrieval():
    """Test workflow when data retrieval is needed."""
    query = "Show me Netflix reviews"
    result = await run_workflow(query, user_id=1)
    assert result is not None


@pytest.mark.asyncio
async def test_workflow_without_data_retrieval():
    """Test workflow when data retrieval is not needed."""
    query = "What is a product gap?"
    result = await run_workflow(query, user_id=1)
    assert result is not None
```

## Mocking External Dependencies

### Mocking LLM Calls

```python
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
@patch('app.llamaindex_workflow.agents.get_llm')
async def test_with_mocked_llm(mock_get_llm):
    """Test with mocked LLM."""
    # Mock LLM response
    mock_llm = AsyncMock()
    mock_llm.astructured_predict.return_value = QueryAnalysis(
        needs_data_retrieval=True,
        needs_nlp_analysis=False,
        company="Netflix",
        query_type="data_only",
        reasoning="Test reasoning",
        analysis_type="none"
    )
    mock_get_llm.return_value = mock_llm
    
    # Run test
    from app.llamaindex_workflow.agents import analyze_query
    result = await analyze_query("test query")
    
    assert result.company == "Netflix"
```

### Mocking Database

```python
@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = MagicMock(spec=Session)
    
    # Mock execute to return test data
    mock_result = MagicMock()
    mock_result.keys.return_value = ["id", "review"]
    mock_result.__iter__.return_value = [
        (1, "Great product"),
        (2, "Needs improvement")
    ]
    session.execute.return_value = mock_result
    
    return session


def test_with_mock_db(mock_db_session):
    """Test using mocked database."""
    service = DataRetrievalService(mock_db_session)
    results = service.execute_sql_query("SELECT * FROM reviews")
    
    assert len(results) == 2
```

## Test Fixtures

### Common Fixtures

```python
import pytest
from app.database.base import SessionLocal


@pytest.fixture
def db_session():
    """Provide a database session for tests."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_query():
    """Provide a sample query."""
    return "What are the main product gaps for Netflix?"


@pytest.fixture
def sample_table_schemas():
    """Provide sample table schemas."""
    return {
        "reviews": {
            "columns": ["id", "company", "review_text", "rating"],
            "description": "Customer reviews"
        }
    }
```

## Running Tests

### Run All Tests

```bash
pytest backend/app/llamaindex_workflow/tests/
```

### Run Specific Test

```bash
pytest backend/app/llamaindex_workflow/tests/test_workflow.py::test_analyze_query_step
```

### Run with Coverage

```bash
pytest --cov=app.llamaindex_workflow backend/app/llamaindex_workflow/tests/
```

### Run Integration Tests Only

```bash
pytest -m integration backend/app/llamaindex_workflow/tests/
```

### Run with Verbose Output

```bash
pytest -v -s backend/app/llamaindex_workflow/tests/
```

## Test Structure

```
backend/app/llamaindex_workflow/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── test_workflow.py         # Workflow tests
│   ├── test_agents.py           # Agent tests
│   ├── test_services.py         # Service tests
│   └── test_integration.py      # Integration tests
```

## Best Practices

1. **Isolate Tests**: Each test should be independent
2. **Mock External Calls**: Mock LLM and database calls for unit tests
3. **Use Fixtures**: Share common setup via fixtures
4. **Test Edge Cases**: Test error conditions and edge cases
5. **Integration Tests**: Have separate integration tests that use real dependencies
6. **Fast Unit Tests**: Keep unit tests fast by mocking everything
7. **Clear Assertions**: Make assertions clear and specific
8. **Test Coverage**: Aim for >80% coverage

## Debugging Tests

### Print Context State

```python
@pytest.mark.asyncio
async def test_with_debug():
    workflow = ProductGapWorkflow(user_id=1, verbose=True)
    
    # Add debug logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    result = await workflow.run(query="test")
    print(f"Result: {result}")
```

### Use Breakpoints

```python
@pytest.mark.asyncio
async def test_with_breakpoint():
    workflow = ProductGapWorkflow(user_id=1)
    
    # Set breakpoint
    import pdb; pdb.set_trace()
    
    result = await workflow.run(query="test")
```

### Capture Logs

```python
def test_with_logs(caplog):
    """Test with log capture."""
    with caplog.at_level(logging.INFO):
        # Run test
        pass
    
    # Check logs
    assert "Expected log message" in caplog.text
```
