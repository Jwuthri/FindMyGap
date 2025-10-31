---
alwaysApply: true
description: Team standards for code quality, testing, and workflow
---

# Team Standards

## Logging Standards

### Required Log Format

Every log message MUST be prefixed with the following format:

```
[classname] | [user_id] | [company_id] | message
```

### Format Rules

1. **[classname]**: Always include the name of the class where the log is generated
2. **[user_id]**: Include user ID when available in context
3. **[company_id]**: Include company ID when available in context
4. Use `None` or `N/A` for unavailable context values
5. Separate each field with ` | ` (space-pipe-space)

### Examples

```python
# In a class method with all context available
logger.info("[UserRepository] | [user_id=user_123] | [company_id=comp_456] | User authenticated successfully")

# With some missing context
logger.error("[ProductGapWorkflow] | [user_id=user_123] | [company_id=None] | Failed to process message")

# Minimal context
logger.debug("[DatabaseSession] | [user_id=None] | [company_id=None] | Connection established")
```

### Implementation Guidelines

1. **Create a logging helper method** in each class:

```python
def _log_prefix(self, user_id=None, company_id=None):
    # Try to get from instance attributes if not provided
    user_id = user_id or getattr(self, 'user_id', None)
    company_id = company_id or getattr(self, 'company_id', None)
    return f"[{self.__class__.__name__}] | [user_id={user_id or 'None'}] | [company_id={company_id or 'None'}]"
```

2. **Use the helper in log statements**:

```python
logger.info(f"{self._log_prefix(user_id, company_id)} | Your message here")
```

3. **For static/module-level functions**, use the module name as classname:

```python
logger.info("[workflows.utils.schema_manager] | [user_id=user_123] | [company_id=None] | Schema validated")
```

### Context Extraction

- Extract IDs from request context, database objects, or method parameters
- Pass context down through method calls when possible
- Store frequently used context (like user_id, company_id) in class instance variables

This standard ensures consistent, traceable logging across the entire backend application.

## Code Quality

### General Principles

- Always write unit tests for new functions
- Use meaningful variable names that describe their purpose
- Add docstrings to all public functions and classes
- Keep functions focused on a single responsibility
- Avoid deep nesting (max 3-4 levels)

### Documentation

- Use Google-style docstrings for Python functions
- Document parameters, return values, and exceptions
- Include usage examples for complex functions
- Keep comments up-to-date with code changes

### README Files Policy

**CRITICAL: Do not create excessive documentation files**

- Maximum of ONE README.md per directory
- Update existing README.md files instead of creating new ones
- Use the main README.md at project root for global documentation
- When documentation is needed:
  - First check if a README.md already exists in that directory
  - If it exists, UPDATE it with new information
  - If it doesn't exist, only create one if absolutely necessary
  - Never create multiple documentation files in the same directory (e.g., CLI_README.md, API_README.md, etc.)
- Consolidate related documentation into a single README.md per directory
- Use sections and headers within README.md to organize different topics
- Don't create document randomly in the codebase, follow these rules

## Python Specific

### Style Guidelines

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Prefer f-strings for string formatting over `.format()` or `%`
- Use list/dict comprehensions for simple transformations
- Avoid mutable default arguments

### Type Hints Example

```python
from typing import Optional, List

def get_user_by_email(email: str, include_deleted: bool = False) -> Optional[UserTable]:
    """Get user by email address."""
    pass

def get_all_users(skip: int = 0, limit: int = 100) -> List[UserTable]:
    """Get all users with pagination."""
    pass
```

### String Formatting

```python
# Good - use f-strings
logger.info(f"User {user_id} logged in at {timestamp}")

# Avoid - old style formatting
logger.info("User %s logged in at %s" % (user_id, timestamp))
logger.info("User {} logged in at {}".format(user_id, timestamp))
```

## Git Workflow

### Commit Messages

- Write clear, descriptive commit messages
- Use present tense ("Add feature" not "Added feature")
- First line should be 50 characters or less
- Include context in the body if needed

### Branch Strategy

- Create feature branches for new work
- Use descriptive branch names (e.g., `feature/user-authentication`, `fix/login-bug`)
- Keep branches focused on a single feature or fix
- Delete branches after merging

### Before Merging

- Ensure all tests pass
- Run linters and formatters
- Review your own changes first
- Get code review when possible

## Permission and Safety

### Command Execution

- **Never run a command without asking permission first**
- Explain what the command will do before running it
- Confirm destructive operations (delete, drop, truncate)
- Use dry-run options when available

### Database Operations

- Always backup before schema changes
- Test migrations on development environment first
- Never run DELETE or UPDATE without WHERE clause in production
- Use transactions for multi-step operations

## Testing

### Test Coverage

- Write unit tests for all business logic
- Test edge cases and error conditions
- Use meaningful test names that describe what is being tested
- Keep tests independent and isolated

### Test Organization

- Place tests in `backend/tests/` directory
- Mirror the source code structure
- Use fixtures for common test data
- Mock external dependencies
