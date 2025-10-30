# User Review Feedback Table

## Overview

The `user_review_feedback` table is a junction table that manages which users have access to which reviews. This enables:

- **User-specific review collections**: Each user can have their own set of reviews
- **Review ownership tracking**: Know which reviews a user uploaded vs. shared with them
- **Access control**: Easily check if a user can view/analyze a specific review
- **Sharing capabilities**: Enable users to share reviews with each other

## Table Structure

```sql
CREATE TABLE user_review_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    review_id INTEGER NOT NULL,
    is_owner BOOLEAN DEFAULT FALSE,
    access_type VARCHAR(50),
    notes VARCHAR,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (review_id) REFERENCES reviews_feedback(id) ON DELETE CASCADE,
    UNIQUE (user_id, review_id)
);
```

## Key Fields

- **user_id**: References the user who has access
- **review_id**: References the review in the main `reviews_feedback` table
- **is_owner**: Boolean flag indicating if the user uploaded/owns this review
- **access_type**: How the user got access (e.g., "uploaded", "shared", "platform")
- **notes**: Optional metadata about this relationship

## Architecture

```
┌─────────────┐         ┌──────────────────────┐         ┌──────────────────┐
│   users     │         │ user_review_feedback │         │ reviews_feedback │
├─────────────┤         ├──────────────────────┤         ├──────────────────┤
│ id          │◄────────│ user_id              │         │ id               │
│ email       │         │ review_id            │────────►│ company_id       │
│ username    │         │ is_owner             │         │ text             │
│ ...         │         │ access_type          │         │ rating           │
└─────────────┘         │ notes                │         │ ...              │
                        │ created_at           │         └──────────────────┘
                        │ updated_at           │
                        └──────────────────────┘
```

## Use Cases

### 1. User Uploads Reviews
When a user uploads a CSV of reviews:
```python
# Create reviews in main table
review_ids = []
for review_data in uploaded_reviews:
    review = review_repo.create(db, company_id=company_id, text=review_data['text'])
    review_ids.append(review.id)

# Grant user access with ownership
user_review_repo.bulk_grant_access(
    db=db,
    user_id=user_id,
    review_ids=review_ids,
    is_owner=True,
    access_type="uploaded"
)
```

### 2. Platform-Wide Reviews
For reviews available to all users (like mock data):
```python
# Create review in main table
review = review_repo.create(db, company_id=company_id, text="Great product!")

# Grant access to all users or specific users
for user_id in all_user_ids:
    user_review_repo.create(
        db=db,
        user_id=user_id,
        review_id=review.id,
        is_owner=False,
        access_type="platform"
    )
```

### 3. Sharing Reviews
Allow users to share reviews with each other:
```python
# User A shares a review with User B
user_review_repo.grant_access(
    db=db,
    user_id=user_b_id,
    review_id=review_id,
    access_type="shared"
)
```

### 4. Access Control
Check if a user can access a review before showing it:
```python
if user_review_repo.check_user_access(db, user_id, review_id):
    # Show the review
    review = review_repo.get_by_id(db, review_id)
else:
    # Return 403 Forbidden
    raise HTTPException(status_code=403, detail="Access denied")
```

### 5. User Dashboard
Get all reviews accessible to a user:
```python
# Get all reviews (owned + shared)
all_reviews = user_review_repo.get_user_reviews(db, user_id)

# Get only owned reviews
owned_reviews = user_review_repo.get_user_owned_reviews(db, user_id)

# Get count
total_count = user_review_repo.count_user_reviews(db, user_id)
```

## Repository Methods

### UserReviewFeedbackRepository

- `create()` - Grant a user access to a review
- `get_user_reviews()` - Get all reviews a user has access to
- `get_user_owned_reviews()` - Get only reviews owned by a user
- `check_user_access()` - Check if user has access to a review
- `grant_access()` - Grant access if not already granted
- `revoke_access()` - Remove user's access to a review
- `bulk_grant_access()` - Grant access to multiple reviews at once
- `get_review_users()` - Get all users who have access to a review
- `count_user_reviews()` - Count total reviews accessible to a user

## Migration

Run the migration to create the table:
```bash
cd backend
alembic upgrade head
```

## Example Workflow

```python
from sqlalchemy.orm import Session
from app.database.repositories.review import ReviewRepository
from app.database.repositories.user_review_feedback import UserReviewFeedbackRepository

def ingest_user_reviews(db: Session, user_id: int, csv_data: list[dict]):
    """Complete workflow for user review ingestion."""
    
    review_repo = ReviewRepository()
    user_review_repo = UserReviewFeedbackRepository()
    
    # Step 1: Create reviews in main table
    review_ids = []
    for row in csv_data:
        review = review_repo.create(
            db=db,
            company_id=row['company_id'],
            text=row['text'],
            rating=row.get('rating')
        )
        review_ids.append(review.id)
    
    # Step 2: Grant user access
    count = user_review_repo.bulk_grant_access(
        db=db,
        user_id=user_id,
        review_ids=review_ids,
        is_owner=True,
        access_type="uploaded"
    )
    
    return {
        "reviews_created": len(review_ids),
        "access_granted": count
    }
```

## Benefits

1. **Separation of Concerns**: Main review data is separate from access control
2. **Scalability**: Easy to add/remove user access without touching review data
3. **Flexibility**: Support multiple access patterns (owned, shared, platform-wide)
4. **Audit Trail**: Track when and how users got access to reviews
5. **Performance**: Indexed lookups for fast access checks
6. **Data Integrity**: Foreign key constraints ensure referential integrity
