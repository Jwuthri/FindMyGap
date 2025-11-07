---
alwaysApply: true
description: Architecture patterns and project structure for the FindMyGap backend
---

# Architecture Patterns

## Project Structure

The backend follows a layered architecture with clear separation of concerns:

```
backend/app/
├── api/              # FastAPI routes and endpoints
├── cli/              # Command-line interface tools
├── core/             # Core application logic
├── database # Command-line interface tools
├── config.py         # Application configuration
├── database/         # Database layer
│   ├── models/       # SQLAlchemy table models
│   ├── repositories/ # Data access layer
│   ├── base.py       # Base model class
│   └── session.py    # Database session management
├── models/           # Pydantic schemas for API serialization
├── workflows/        # Main LLM/agent workflows
│   ├── steps/        # Individual workflow steps
│   └── utils/        # Workflow utilities
└── utils/            # Shared utilities
```

## Layer Responsibilities

### API Layer (`backend/app/api/`)
- FastAPI route definitions
- Request/response handling
- Input validation using Pydantic models
- Authentication and authorization
- HTTP-specific logic

### CLI Layer (`backend/app/cli/`)
- Command-line interface implementations
- Client command runners
- Script entry points
- Terminal-based interactions

### Database Layer (`backend/app/database/`)

#### Models (`backend/app/database/models/`)
- SQLAlchemy table definitions
- Database schema representation
- Relationships between tables
- One file per table

#### Repositories (`backend/app/database/repositories/`)
- All SQL queries and database operations
- Data access abstraction
- Transaction management
- One file per table matching the model

### Pydantic Models (`backend/app/models/`)
- API request/response schemas
- Data validation and serialization
- Type definitions for API contracts
- One file per domain entity

### Workflows Layer (`backend/app/workflows/`)
- Main LLM and agent workflows
- Business logic orchestration
- Multi-step processes
- Integration with external AI services

## Design Patterns

### Repository Pattern

All database operations MUST go through repository classes:

```python
# Good - using repository
from app.database.repositories.user import UserRepository

user = UserRepository.get_by_email(db, email="user@example.com")

# Bad - direct database access in business logic
user = db.query(UserTable).filter(UserTable.email == email).first()
```

### Separation of Concerns

Keep layers independent:
- API layer calls repositories, not database models directly
- Repositories handle database operations, not business logic
- Workflows orchestrate, repositories execute
- Models define structure, repositories define behavior

### Dependency Flow

```
API/CLI → Workflows → Repositories → Database Models
         ↓
    Pydantic Models (for serialization)
```

## File Organization

### Naming Conventions
- Database models: `{entity}_table.py` or `{entity}.py` with `{Entity}Table` class
- Repositories: `{entity}.py` with `{Entity}Repository` class
- Pydantic models: `{entity}.py` with `{Entity}Schema` class
- Workflows: `{workflow_name}_workflow.py`

### Module Structure
Each module should have:
- Clear single responsibility
- Minimal dependencies
- Proper imports (absolute from `app.`)
- Type hints on all public functions

## Configuration

### Settings Management
- All configuration in `backend/app/config.py`
- Use environment variables for secrets
- Provide sensible defaults
- Document all configuration options

### Environment Files
- `.env` for local development (not committed)
- `.env.template` as example (committed)
- Use `python-dotenv` for loading

## Error Handling

### Exception Hierarchy
- Create custom exceptions for domain-specific errors
- Inherit from appropriate base exceptions
- Include context in exception messages
- Log exceptions with appropriate severity

### Error Propagation
- Let exceptions bubble up to API layer
- Handle exceptions at appropriate level
- Don't catch and ignore exceptions
- Use try-except-finally for resource cleanup

## Async Patterns

### When to Use Async
- External API calls (LLM providers, etc.)
- I/O-bound operations
- Concurrent task execution
- Long-running workflows

### Repository Async Support
- Use `base_async.py` for async repository base
- Implement both sync and async methods when needed
- Use `asyncio` for concurrent operations
- Properly handle async context managers

## Testing Strategy

### Test Organization
- Mirror source structure in `backend/tests/`
- Unit tests for repositories and utilities
- Integration tests for workflows
- API tests for endpoints

### Test Isolation
- Use test database or mocks
- Clean up after each test
- Don't depend on test execution order
- Use fixtures for common setup
