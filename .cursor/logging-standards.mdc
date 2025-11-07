---
alwaysApply: true
description: Logging format standards for consistent log prefixing across the backend codebase
---

# Logging Standards

## Required Log Format

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
