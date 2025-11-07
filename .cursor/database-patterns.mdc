---
alwaysApply: true
description: Database patterns and conventions for SQLAlchemy models, Pydantic schemas, and repositories
---

# Database Patterns

## SQLAlchemy Models

### Location and Structure
- Place all database models in `backend/app/database/models/` directory
- One file per table (e.g., `user.py`, `organization.py`)
- Use descriptive table names in snake_case
- Model class names should end with `Table` suffix (e.g., `UserTable`, `OrganizationTable`)

### Standard Fields
Include these standard fields in every model:
```python
id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

### Datetime Fields
- Use `DateTime` type for all datetime fields
- Use `datetime.utcnow` for default values (not `datetime.utcnow()`)
- Always store times in UTC

### Example Pattern:
```python
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from ..base import Base

class UserTable(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

## Pydantic Schemas

### Location and Structure
- Create corresponding Pydantic schemas in `backend/app/models/` for each database model
- One file per domain entity matching the database model name (e.g., `user.py`, `organization.py`)
- Schema class names should end with `Schema` suffix (e.g., `UserSchema`, `OrganizationSchema`)

### Configuration
- Use `from_attributes = True` in Config class for SQLAlchemy compatibility
- Include proper type hints and optional fields
- Add Field descriptions for API documentation
- Include json_schema_extra with examples

### Example Pattern:
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class UserSchema(BaseModel):
    id: str = Field(..., description="User ID (UUID)")
    email: str = Field(..., description="Email address")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
```

## Repository Implementation

### Location and Structure
- Place all repositories in `backend/app/database/repositories/` directory
- One file per table matching the model name (e.g., `user.py`, `organization.py`)
- Repository class names should end with `Repository` suffix (e.g., `UserRepository`)

### Standard Methods
Implement these standard methods in every repository:
- `create()` - Create new record
- `get_by_id()` - Retrieve by primary key
- `get_all()` - List with pagination
- `update()` - Update existing record
- `delete()` - Delete record

### Domain-Specific Methods
Add domain-specific query methods as needed:
- `get_by_email()`, `get_by_username()` for users
- `get_by_org()`, `get_by_deal()` for organization/deal-scoped queries
- `search_*()` for search functionality

### Error Handling
- Use proper error handling with SQLAlchemy exceptions
- Include transaction management with commit/rollback
- Log all database operations with appropriate context

### Example Pattern:
```python
from sqlalchemy.orm import Session
from typing import Optional, List
from app import get_logger
from app.database.models.user import UserTable

logger = get_logger("user_repository")

class UserRepository:
    """Repository for User model operations."""
    
    @staticmethod
    def create(db: Session, email: str, **kwargs) -> UserTable:
        """Create a new user."""
        user = UserTable(email=email, **kwargs)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created user: {user.id}")
        return user
    
    @staticmethod
    def get_by_id(db: Session, user_id: str) -> Optional[UserTable]:
        """Get user by ID."""
        return db.query(UserTable).filter(UserTable.id == user_id).first()
```

## Database Migrations

### Alembic Usage
- Use Alembic for all database migrations
- Place migration files in `backend/alembic/versions/`
- Use descriptive migration messages
- Command: `make run_alembic_revision message="description"`

### Migration Best Practices
- Test migrations on development database first
- Include both upgrade and downgrade paths
- Document breaking changes in migration file comments

## Query Patterns

### Best Practices
- Use SQLAlchemy ORM for all database queries
- Order results by `created_at` or `updated_at` for consistency
- Implement pagination for large result sets (use `skip` and `limit`)
- Use proper indexing for frequently queried fields
- Use `.first()` for single results, `.all()` for multiple results
- Always handle `None` returns from queries
