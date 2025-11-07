---
alwaysApply: true
description: Code style conventions, formatting, and naming standards for the backend
---

# Code Style Conventions

## Formatting and Linting

### Tools and Configuration
- Use Black with line length 120 characters for code formatting
- Use isort with Black profile for import sorting
- Follow PEP 8 guidelines with Ruff linting
- Use pre-commit hooks for automated code quality checks

### Running Formatters
```bash
# Format code with Black
black backend/app --line-length 120

# Sort imports with isort
isort backend/app --profile black

# Run linter
ruff check backend/app
```

## Import Organization

### Import Order
Group imports in this order with blank lines between groups:
1. Standard library imports
2. Third-party library imports
3. Local application imports

### Import Style
- Use absolute imports from `app.` root
- Import specific classes/functions rather than entire modules when possible
- Avoid wildcard imports (`from module import *`)
- Keep imports alphabetically sorted within each group

### Example:
```python
# Standard library
import uuid
from datetime import datetime
from typing import List, Optional

# Third-party
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import Session

# Local
from app import get_logger
from app.database.models.user import UserTable
from app.models.user import UserSchema
```

## Naming Conventions

### Classes
- Use PascalCase for class names
- Database models: end with `Table` (e.g., `UserTable`, `OrganizationTable`)
- Pydantic schemas: end with `Schema` (e.g., `UserSchema`, `OrganizationSchema`)
- Repositories: end with `Repository` (e.g., `UserRepository`)
- Workflows: end with `Workflow` (e.g., `ProductGapWorkflow`)

### Functions and Methods
- Use snake_case for function and method names
- Use descriptive names that indicate action (e.g., `get_user_by_email`, `create_organization`)
- Prefix private methods with underscore (e.g., `_validate_input`, `_log_prefix`)
- Prefix async functions with async context when helpful (e.g., `async_fetch_data`)

### Variables
- Use snake_case for variable names
- Use descriptive names (e.g., `user_email` not `ue`)
- Boolean variables should be prefixed with `is_`, `has_`, `can_`, etc.
- Avoid single-letter names except for iterators

### Constants
- Use UPPER_SNAKE_CASE for constants
- Define module-level constants at the top of the file
- Group related constants together

### Example:
```python
# Constants
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30
API_BASE_URL = "https://api.example.com"

# Class
class UserRepository:
    """Repository for user operations."""
    
    # Public method
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[UserTable]:
        """Get user by email address."""
        return db.query(UserTable).filter(UserTable.email == email).first()
    
    # Private method
    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        return "@" in email
```

## File Naming

### Python Files
- Use snake_case for file names
- Match file name to primary class/function when possible
- Provider-specific files: prefix with underscore (e.g., `_openai.py`, `_anthropic.py`)

### Examples:
- `user.py` - contains `UserTable`, `UserRepository`, or `UserSchema`
- `product_gap_workflow.py` - contains `ProductGapWorkflow`
- `schema_manager.py` - contains schema management utilities

## Enums and Constants

### Enum Definitions
- Use Enum classes for related constants
- Inherit from `str` and `enum.Enum` for string enums
- Use UPPER_CASE for enum values
- Define enums with string values for database compatibility

### Example:
```python
import enum

class UserStatusEnum(str, enum.Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class Providers(str, enum.Enum):
    """LLM provider options."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
```

## Error Handling

### Exception Classes
- Create custom exception classes for specific domains
- Inherit from appropriate base exception
- Use descriptive exception names ending in `Error`
- Include helpful error messages

### Exception Handling
- Use try-catch blocks with specific exception types
- Log errors with appropriate log levels and context
- Include `exc_info=True` for detailed error logging in debug mode
- Don't catch exceptions you can't handle

### Example:
```python
from app import get_logger

logger = get_logger(__name__)

class RepositoryError(Exception):
    """Base exception for repository operations."""
    pass

class UserNotFoundError(RepositoryError):
    """Raised when user is not found."""
    pass

def get_user(db: Session, user_id: str) -> UserTable:
    """Get user by ID."""
    try:
        user = db.query(UserTable).filter(UserTable.id == user_id).first()
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error getting user {user_id}", exc_info=True)
        raise RepositoryError(f"Failed to get user: {str(e)}")
```

## Code Comments

### When to Comment
- Complex algorithms or business logic
- Non-obvious workarounds or hacks
- Important context or decisions
- TODO items with owner and date

### When Not to Comment
- Don't comment obvious code
- Don't leave commented-out code (use git history)
- Don't write redundant comments

### Example:
```python
# Good - explains why
# Using UTC timestamp to avoid timezone issues across regions
created_at = datetime.utcnow()

# Bad - states the obvious
# Set created_at to current time
created_at = datetime.utcnow()

# Good - TODO with context
# TODO(john, 2024-01-15): Refactor to use async repository after migration
user = UserRepository.get_by_id(db, user_id)
```

## Function Documentation

### Docstring Format
Use Google-style docstrings for all public functions:

```python
def create_user(db: Session, email: str, username: str = None) -> UserTable:
    """Create a new user in the database.
    
    Args:
        db: Database session
        email: User email address
        username: Optional username (defaults to None)
    
    Returns:
        Created user object
    
    Raises:
        ValueError: If email is invalid
        RepositoryError: If database operation fails
    """
    pass
```
