# Backend Refactoring Documentation

## Overview

This document describes the major refactoring completed to align the backend with the Kiro steering rules and best practices.

## What Was Refactored

### 1. Database Layer Migration (SQLite3 → SQLAlchemy + Alembic)

**Before:**
- Raw `sqlite3` connections scattered throughout workflows
- Direct SQL queries in business logic
- No migration system
- Manual table creation

**After:**
- ✅ Full SQLAlchemy ORM with proper models
- ✅ Repository pattern for all database access
- ✅ Alembic migrations for schema management
- ✅ Proper session management

**New Models Created:**
- `UserDatasetTable` - User-uploaded datasets metadata
- `PlatformDatasetTable` - Platform-wide datasets metadata

**New Repositories Created:**
- `UserDatasetRepository` - CRUD operations for user datasets
- `PlatformDatasetRepository` - CRUD operations for platform datasets

**Migration:**
- `f87c0a5c0ce6_add_dataset_tables.py` - Creates user_datasets and platform_datasets tables

### 2. Service Layer Architecture

**New Services:**

#### `DataIngestionService` (`workflows/utils/data_ingestion_refactored.py`)
Handles all data ingestion operations:
- File upload and analysis (CSV, Excel, JSON, Parquet)
- LLM-based metadata generation
- Database table creation via SQLAlchemy
- Dataset registration via repositories

**Key Methods:**
- `ingest_data_file()` - Complete ingestion pipeline
- `ingest_mock_reviews()` - Load mock review data
- `generate_platform_metadata()` - Generate metadata for platform datasets

#### `SchemaManagerService` (`workflows/utils/schema_manager_refactored.py`)
Handles schema management:
- Schema fetching via SQLAlchemy inspector
- Schema formatting for LLM context
- Dataset registration and retrieval
- Platform dataset management

**Key Methods:**
- `get_all_available_schemas()` - Get all schemas for LLM
- `get_table_schema()` - Get schema for specific table
- `register_platform_dataset()` - Register platform dataset with metadata

### 3. CLI Scripts Organization

**Before:**
- Scripts scattered in `backend/app/` root
- Mixed concerns
- Hard to find and maintain

**After:**
All scripts moved to `backend/app/cli/`:
- ✅ `example_data_ingestion.py` - Example ingestion workflow
- ✅ `ingest_mock_data.py` - Ingest mock reviews
- ✅ `init_database.py` - Initialize database tables
- ✅ `setup_platform_datasets.py` - Setup platform datasets with metadata
- ✅ `view_platform_metadata.py` - View platform dataset metadata

### 4. Logging Standards Implementation

**Before:**
```python
logger.info(f"Created user: {user.id}")
```

**After:**
```python
logger.info(f"{self._log_prefix(user_id)} | Created user with email: {email}")
# Output: [UserRepository] | [user_id=user_123] | [company_id=None] | Created user with email: user@example.com
```

**All repositories now include:**
- `_log_prefix()` method for consistent logging
- Proper context (user_id, company_id) in all log messages
- Follows format: `[classname] | [user_id] | [company_id] | message`

### 5. Pydantic Schemas

**New Schemas Created:**
- `UserDatasetSchema` - User dataset API schema
- `UserDatasetCreateSchema` - Create user dataset schema
- `PlatformDatasetSchema` - Platform dataset API schema
- `PlatformDatasetCreateSchema` - Create platform dataset schema

## File Structure

```
backend/app/
├── cli/                          # CLI scripts (NEW)
│   ├── example_data_ingestion.py
│   ├── ingest_mock_data.py
│   ├── init_database.py
│   ├── setup_platform_datasets.py
│   └── view_platform_metadata.py
├── database/
│   ├── models/
│   │   ├── user.py
│   │   └── dataset.py           # NEW
│   └── repositories/
│       ├── user.py               # REFACTORED
│       └── dataset.py            # NEW
├── models/
│   ├── user.py
│   └── dataset.py                # NEW
└── workflows/
    └── utils/
        ├── data_ingestion.py                    # OLD (deprecated)
        ├── data_ingestion_refactored.py         # NEW
        ├── schema_manager.py                    # OLD (deprecated)
        ├── schema_manager_refactored.py         # NEW
        └── data_storage_v2.py                   # Reference only
```

## Migration Guide

### Running Migrations

```bash
# Run migrations
cd backend
alembic upgrade head

# Create new migration
alembic revision -m "description"

# Rollback
alembic downgrade -1
```

### Using the New Services

#### Data Ingestion Example

```python
from app.database.base import SessionLocal
from app.workflows.utils.data_ingestion_refactored import DataIngestionService

db = SessionLocal()
try:
    service = DataIngestionService(db)
    result = await service.ingest_data_file(
        file_path="data.csv",
        user_id="user_123",
        model=model
    )
finally:
    db.close()
```

#### Schema Management Example

```python
from app.database.base import SessionLocal
from app.workflows.utils.schema_manager_refactored import SchemaManagerService

db = SessionLocal()
try:
    service = SchemaManagerService(db)
    schemas = service.get_all_available_schemas(user_id="user_123")
    print(schemas)
finally:
    db.close()
```

#### Repository Usage Example

```python
from app.database.base import SessionLocal
from app.database.repositories.dataset import UserDatasetRepository

db = SessionLocal()
try:
    repo = UserDatasetRepository()
    
    # Create dataset
    dataset = repo.create(
        db=db,
        user_id="user_123",
        table_name="user_123_conversations",
        original_filename="conversations.csv",
        description="Customer conversations",
        column_metadata={"key_fields": ["id"]},
        row_count=1000
    )
    
    # Get user datasets
    datasets = repo.get_by_user(db, "user_123")
    
finally:
    db.close()
```

## Deprecation Notice

### Files to be Removed (After Testing)

Once the refactored code is tested and working:

1. `backend/app/workflows/utils/data_ingestion.py` → Use `data_ingestion_refactored.py`
2. `backend/app/workflows/utils/schema_manager.py` → Use `schema_manager_refactored.py`
3. `backend/app/example_data_ingestion.py` → Use `cli/example_data_ingestion.py`
4. `backend/app/ingest_mock_data.py` → Use `cli/ingest_mock_data.py`
5. `backend/app/init_database.py` → Use `cli/init_database.py`
6. `backend/app/setup_platform_datasets.py` → Use `cli/setup_platform_datasets.py`
7. `backend/app/view_platform_metadata.py` → Use `cli/view_platform_metadata.py`
8. `backend/app/regenerate_metadata.py` → Integrate into CLI if needed

## Benefits

### 1. Maintainability
- Clear separation of concerns
- Repository pattern isolates database logic
- Service layer for business logic
- Easy to test and mock

### 2. Scalability
- SQLAlchemy supports multiple databases (SQLite, PostgreSQL, MySQL)
- Alembic migrations for schema evolution
- Connection pooling and optimization
- Async support ready

### 3. Code Quality
- Consistent logging format
- Type hints throughout
- Proper error handling
- Follows team standards

### 4. Developer Experience
- Clear file organization
- Easy to find functionality
- Self-documenting code
- CLI scripts for common tasks

## Next Steps

### Phase 1: Testing (Current)
- [ ] Test all CLI scripts
- [ ] Verify migrations work
- [ ] Test data ingestion pipeline
- [ ] Test schema management

### Phase 2: Integration
- [ ] Update workflows to use new services
- [ ] Update API endpoints to use repositories
- [ ] Add async support where needed
- [ ] Update tests

### Phase 3: Cleanup
- [ ] Remove deprecated files
- [ ] Update documentation
- [ ] Add more comprehensive tests
- [ ] Performance optimization

### Phase 4: Enhancement
- [ ] Add more repository methods as needed
- [ ] Implement caching layer
- [ ] Add database query optimization
- [ ] Implement audit logging

## Configuration

### Database URL

The system now uses SQLAlchemy URLs configured in `app/config.py`:

```python
# SQLite (development)
DATABASE_URL = "sqlite:///./memory.db"

# PostgreSQL (production)
DATABASE_URL = "postgresql://user:pass@localhost:5432/findmygap"
```

### Alembic Configuration

Update `alembic.ini` to match your database:

```ini
sqlalchemy.url = sqlite:///./memory.db
# or
sqlalchemy.url = postgresql://user:pass@localhost:5432/findmygap
```

## Troubleshooting

### Migration Issues

```bash
# Check current revision
alembic current

# Show migration history
alembic history

# Stamp database to specific revision
alembic stamp head
```

### Database Connection Issues

```python
# Test database connection
from app.database.session import get_database_manager

async def test():
    db_manager = get_database_manager()
    healthy = await db_manager.health_check()
    print(f"Database healthy: {healthy}")
```

## Questions?

Refer to the steering rules in `.kiro/steering/` for:
- Architecture patterns
- Code style conventions
- Database patterns
- Logging standards
- Team standards
