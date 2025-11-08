# Migration to Per-User Review Tables

## Overview

Changed from a single shared `user_review_feedback` table to per-user tables with the pattern `__user_{user_id}_review_feedback`.

## Benefits

1. **Better isolation**: Each user's data is in their own table
2. **Easier data management**: Can drop/backup individual user data
3. **Clearer ownership**: Table name explicitly shows which user it belongs to
4. **Performance**: Smaller tables, no need to filter by user_id
5. **Automatic registration**: Tables are automatically registered in `user_datasets` and `table_eda`

## Changes Made

### New Files

1. **`app/services/user_table_service.py`**
   - Service for managing per-user tables
   - Methods: `create_user_table()`, `insert_review()`, `get_reviews()`, etc.

2. **`app/cli/commands/migrate_user_tables.py`**
   - Migration script to move data from old table to new tables
   - Usage: `python -m app.cli.commands.migrate_user_tables [--dry-run] [--drop-old]`

### Modified Files

1. **`app/utils/schema.py`**
   - Now uses `UserTableService` to get per-user table schemas
   - Dynamically generates table name based on user_id

2. **`app/cli/commands/grant_review_access.py`**
   - Updated to use `UserTableService` instead of `UserReviewFeedbackRepository`
   - Creates user table if it doesn't exist

## Migration Steps

### 1. Run Migration Script

```bash
# Dry run to see what will happen
python -m app.cli.commands.migrate_user_tables --dry-run

# Actually migrate
python -m app.cli.commands.migrate_user_tables

# Migrate and drop old table
python -m app.cli.commands.migrate_user_tables --drop-old
```

### 2. Update Code References

Any code that directly queries `user_review_feedback` should be updated to use `UserTableService`:

**Before:**
```python
from app.database.repositories.user_review_feedback import UserReviewFeedbackRepository

repo = UserReviewFeedbackRepository()
reviews = repo.get_user_reviews(db, user_id)
```

**After:**
```python
from app.services.user_table_service import UserTableService

reviews = UserTableService.get_reviews(db, user_id)
```

### 3. Schema Generation

The schema service now automatically uses the correct per-user table:

```python
# In workflow/agents, the schema will include:
# __user_1_review_feedback (for user_id=1)
# __user_2_review_feedback (for user_id=2)
# etc.
```

## API Reference

### UserTableService Methods

```python
# Get table name for a user
table_name = UserTableService.get_user_table_name(user_id)
# Returns: "__user_1_review_feedback"

# Create user's table (also registers in user_datasets and table_eda)
UserTableService.create_user_table(db, user_id)

# Insert a review (automatically updates row counts in metadata)
review_id = UserTableService.insert_review(
    db, user_id, company_name="Netflix", 
    text="Great service!", rating=5,
    update_counts=True  # Set to False for batch inserts
)

# Get reviews
reviews = UserTableService.get_reviews(
    db, user_id, 
    company_name="Netflix",  # optional filter
    limit=100, offset=0
)

# Count reviews
count = UserTableService.count_reviews(db, user_id)

# Get companies
companies = UserTableService.get_user_companies(db, user_id)

# Check if table exists
exists = UserTableService.table_exists(db, user_id)

# Drop user's table (careful!)
UserTableService.drop_user_table(db, user_id)
```

## Table Schema

Each per-user table has the same structure:

```sql
CREATE TABLE __user_{user_id}_review_feedback (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    category VARCHAR(255),
    rating INTEGER,
    text TEXT NOT NULL,
    source VARCHAR(255),
    date TIMESTAMP,
    author VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx___user_{user_id}_review_feedback_company ON __user_{user_id}_review_feedback(company_name);
CREATE INDEX idx___user_{user_id}_review_feedback_date ON __user_{user_id}_review_feedback(date);
CREATE INDEX idx___user_{user_id}_review_feedback_rating ON __user_{user_id}_review_feedback(rating);
```

## Backward Compatibility

The old `UserReviewFeedbackRepository` is still available but deprecated. It will continue to work with the old `user_review_feedback` table if it exists.

For new code, use `UserTableService` instead.

## Rollback

If you need to rollback:

1. The old `user_review_feedback` table is preserved unless you used `--drop-old`
2. You can drop the new per-user tables manually:
   ```sql
   DROP TABLE IF EXISTS __user_1_review_feedback CASCADE;
   DROP TABLE IF EXISTS __user_2_review_feedback CASCADE;
   -- etc.
   ```

## Automatic Metadata Registration

When a user table is created, it's automatically registered in two places:

### 1. user_datasets
- Tracks the table as a user-owned dataset
- Includes column metadata and descriptions
- Maintains row count for quick reference

### 2. table_eda
- Stores exploratory data analysis
- Includes column statistics
- Contains LLM-generated summaries and insights
- Updated as data is added

This ensures the table is immediately available in:
- Schema generation for LLM agents
- Query planning and retrieval
- Data exploration tools

## Notes

- Table names start with `__` to indicate they are system-managed
- User ID is part of the table name for easy identification
- Each user's table is independent and can be managed separately
- The service automatically creates tables when needed
- Row counts are automatically updated in metadata tables
- For batch inserts, use `update_counts=False` and call `_update_row_counts()` once at the end
