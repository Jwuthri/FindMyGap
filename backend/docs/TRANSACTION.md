# Database Transaction Management

Complete guide to managing database transactions in this FastAPI application.

## Table of Contents

- [Overview](#overview)
- [Basic Patterns](#basic-patterns)
- [FastAPI Integration](#fastapi-integration)
- [Advanced Features](#advanced-features)
- [Performance Optimization](#performance-optimization)
- [Best Practices](#best-practices)
- [Common Pitfalls](#common-pitfalls)

---

## Overview

This application provides multiple transaction management patterns:

1. **Context Managers** - Explicit transaction control (recommended for FastAPI)
2. **Decorators** - Automatic transaction wrapping (for service layer)
3. **Transaction Managers** - Complex operations with savepoints
4. **Bulk Operations** - N+1 query prevention

---

## Basic Patterns

### 1. Async Transaction Scope (FastAPI Routes)

**Best for:** Most FastAPI endpoints with multiple database operations

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_async_session
from app.database.transaction import async_transaction_scope
from app.database.repositories.user import UserRepository

router = APIRouter()

@router.post("/users")
async def create_user_with_profile(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """Create user and profile in a single transaction."""
    user_repo = UserRepository()
    
    async with async_transaction_scope(db) as session:
        # All operations succeed or all rollback
        user = await user_repo.async_create(session, **user_data.dict())
        profile = await profile_repo.async_create(session, user_id=user.id)
        
        return {"user": user, "profile": profile}
```

**Why this pattern:**
- ✅ Works seamlessly with FastAPI dependency injection
- ✅ Explicit transaction boundaries
- ✅ Auto-commit on success, auto-rollback on error
- ✅ Clear code flow

### 2. Read-Only Operations

**Best for:** Query-only endpoints (no writes)

```python
from app.database.transaction import read_only_scope

@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_async_session),
    skip: int = 0,
    limit: int = 100
):
    """List users (read-only, no commit)."""
    async with read_only_scope(db) as session:
        users = await user_repo.async_get_multi(session, skip=skip, limit=limit)
        return users
```

**Why use read-only:**
- 🚀 Slightly more performant (skips commit)
- 🔒 Makes intent clear (no writes expected)
- 🐛 Easier debugging

### 3. Service Layer with Decorators

**Best for:** Reusable business logic in service classes

```python
from app.database.transaction import async_transactional

class UserService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.notification_repo = NotificationRepository()
    
    @async_transactional
    async def register_user(self, db: AsyncSession, email: str, name: str):
        """Register user and send welcome notification."""
        # Transaction automatically managed
        user = await self.user_repo.async_create(
            db, 
            email=email, 
            name=name
        )
        
        notification = await self.notification_repo.async_create(
            db,
            user_id=user.id,
            message=f"Welcome {name}!"
        )
        
        return user

# Usage in FastAPI route
@router.post("/register")
async def register(
    data: UserRegister,
    db: AsyncSession = Depends(get_async_session)
):
    service = UserService()
    return await service.register_user(db, data.email, data.name)
```

**When to use decorators:**
- ✅ Service/business logic layer
- ✅ Reusable transaction patterns
- ❌ Avoid in FastAPI route handlers (use context managers instead)

---

## FastAPI Integration

### Pattern 1: Simple CRUD Operation

```python
@router.post("/items")
async def create_item(
    item: ItemCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """Simple create - transaction handled by repository."""
    # For single operations, repository handles transaction
    return await item_repo.async_create(db, **item.dict())
```

### Pattern 2: Multi-Step Operation

```python
@router.post("/orders")
async def create_order(
    order: OrderCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """Multi-step operation - explicit transaction."""
    async with async_transaction_scope(db) as session:
        # Create order
        new_order = await order_repo.async_create(session, **order.dict())
        
        # Create order items
        for item in order.items:
            await order_item_repo.async_create(
                session,
                order_id=new_order.id,
                **item.dict()
            )
        
        # Update inventory
        for item in order.items:
            await inventory_repo.async_decrement(
                session,
                product_id=item.product_id,
                quantity=item.quantity
            )
        
        return new_order
```

### Pattern 3: Background Tasks with Transactions

```python
from fastapi import BackgroundTasks

async def send_welcome_email_task(user_id: int):
    """Background task with its own transaction."""
    async with async_session_maker() as db:
        async with async_transaction_scope(db) as session:
            user = await user_repo.async_get(session, user_id)
            # Send email...
            await user_repo.async_update(
                session, 
                user_id, 
                welcome_email_sent=True
            )

@router.post("/users")
async def create_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session)
):
    async with async_transaction_scope(db) as session:
        new_user = await user_repo.async_create(session, **user.dict())
    
    # Separate transaction for background task
    background_tasks.add_task(send_welcome_email_task, new_user.id)
    return new_user
```

---

## Advanced Features

### 1. Savepoints (Nested Transactions)

**Use case:** Try operation, rollback if fails, continue transaction

```python
from app.database.transaction import AsyncTransactionManager

@router.post("/batch-import")
async def batch_import(
    items: list[ItemCreate],
    db: AsyncSession = Depends(get_async_session)
):
    """Import items, skip invalid ones without failing entire batch."""
    manager = AsyncTransactionManager(db)
    results = {"success": [], "failed": []}
    
    try:
        for item in items:
            # Create savepoint before each item
            savepoint = await manager.savepoint()
            
            try:
                new_item = await item_repo.async_create(db, **item.dict())
                results["success"].append(new_item.id)
            except Exception as e:
                # Rollback this item only
                await manager.rollback_to_savepoint(savepoint)
                results["failed"].append({"item": item.name, "error": str(e)})
        
        # Commit all successful items
        await manager.commit()
        return results
        
    except Exception as e:
        await manager.rollback()
        raise
```

### 2. Complex Multi-Entity Transaction

```python
@router.post("/projects/{project_id}/deploy")
async def deploy_project(
    project_id: int,
    config: DeployConfig,
    db: AsyncSession = Depends(get_async_session)
):
    """Complex deployment with multiple entities."""
    manager = AsyncTransactionManager(db)
    
    try:
        # Step 1: Validate project
        project = await project_repo.async_get(db, project_id)
        if not project:
            raise HTTPException(404, "Project not found")
        
        # Step 2: Create deployment record
        sp1 = await manager.savepoint()
        deployment = await deployment_repo.async_create(
            db,
            project_id=project_id,
            status="pending",
            config=config.dict()
        )
        
        # Step 3: Allocate resources
        sp2 = await manager.savepoint()
        try:
            resources = await resource_repo.async_allocate(
                db,
                deployment_id=deployment.id,
                requirements=config.resources
            )
        except InsufficientResourcesError:
            # Rollback resource allocation, but keep deployment record
            await manager.rollback_to_savepoint(sp2)
            await deployment_repo.async_update(
                db,
                deployment.id,
                status="failed",
                error="Insufficient resources"
            )
            await manager.commit()
            raise HTTPException(503, "Insufficient resources")
        
        # Step 4: Update project status
        await project_repo.async_update(
            db,
            project_id,
            last_deployment_id=deployment.id,
            status="deploying"
        )
        
        await manager.commit()
        return deployment
        
    except Exception as e:
        await manager.rollback()
        raise
```

---

## Performance Optimization

### 1. Prevent N+1 Queries with Eager Loading

```python
from app.database.transaction import optimize_query_for_eager_loading
from sqlalchemy import select

@router.get("/users")
async def list_users_with_posts(db: AsyncSession = Depends(get_async_session)):
    """Load users with their posts (no N+1)."""
    async with read_only_scope(db) as session:
        # Build base query
        query = select(User)
        
        # Add eager loading
        query = optimize_query_for_eager_loading(
            query, 
            relationships=['posts', 'profile']
        )
        
        result = await session.execute(query)
        users = result.scalars().unique().all()
        return users
```

### 2. Bulk Load Related Objects

```python
from app.database.transaction import bulk_load_related

@router.get("/posts/feed")
async def get_feed(db: AsyncSession = Depends(get_async_session)):
    """Get posts with authors efficiently."""
    async with read_only_scope(db) as session:
        # Get posts
        posts = await post_repo.async_get_multi(session, limit=100)
        
        # Bulk load authors (1 query instead of N)
        def load_authors(db, user_ids):
            return user_repo.async_get_by_ids(db, user_ids)
        
        authors_by_id = bulk_load_related(session, posts, load_authors)
        
        # Attach authors to posts
        for post in posts:
            post.author = authors_by_id.get(post.user_id)
        
        return posts
```

### 3. Batch Operations

```python
@router.post("/users/bulk")
async def create_users_bulk(
    users: list[UserCreate],
    db: AsyncSession = Depends(get_async_session)
):
    """Bulk create users efficiently."""
    async with async_transaction_scope(db) as session:
        # Use bulk insert for better performance
        user_dicts = [user.dict() for user in users]
        await session.execute(
            insert(User),
            user_dicts
        )
        return {"created": len(users)}
```

---

## Best Practices

### ✅ DO

1. **Use context managers in FastAPI routes**
   ```python
   async with async_transaction_scope(db) as session:
       # operations
   ```

2. **Keep transactions short**
   ```python
   # Good - quick transaction
   async with async_transaction_scope(db) as session:
       await repo.create(session, data)
   
   # Bad - long-running transaction
   async with async_transaction_scope(db) as session:
       await slow_external_api_call()  # ❌ Don't do this
       await repo.create(session, data)
   ```

3. **Use read-only scopes for queries**
   ```python
   async with read_only_scope(db) as session:
       return await repo.get_all(session)
   ```

4. **Handle specific exceptions**
   ```python
   try:
       async with async_transaction_scope(db) as session:
           await repo.create(session, data)
   except IntegrityError:
       raise HTTPException(409, "Already exists")
   ```

### ❌ DON'T

1. **Don't nest transactions unnecessarily**
   ```python
   # Bad
   async with async_transaction_scope(db) as session:
       async with async_transaction_scope(session) as nested:  # ❌
           await repo.create(nested, data)
   ```

2. **Don't perform I/O inside transactions**
   ```python
   # Bad
   async with async_transaction_scope(db) as session:
       user = await repo.create(session, data)
       await send_email(user.email)  # ❌ Do this after commit
   ```

3. **Don't forget error handling**
   ```python
   # Bad - errors not handled
   async with async_transaction_scope(db) as session:
       await repo.create(session, data)  # What if this fails?
   ```

4. **Don't use decorators in route handlers**
   ```python
   # Bad
   @router.post("/users")
   @async_transactional  # ❌ Use context manager instead
   async def create_user(db: AsyncSession = Depends(get_async_session)):
       pass
   ```

---

## Common Pitfalls

### Issue 1: Accessing Objects After Commit

```python
# Problem
async with async_transaction_scope(db) as session:
    user = await user_repo.async_create(session, name="John")

# ❌ Object may be detached from session
print(user.posts)  # Might fail!

# Solution 1: Access within transaction
async with async_transaction_scope(db) as session:
    user = await user_repo.async_create(session, name="John")
    posts = user.posts  # ✅ Access before commit

# Solution 2: Eager load
async with async_transaction_scope(db) as session:
    user = await user_repo.async_create(session, name="John")
    await session.refresh(user, ['posts'])  # Load relationship
```

### Issue 2: Transaction Timeout

```python
# Problem
async with async_transaction_scope(db) as session:
    # Long operation holds transaction lock
    for i in range(10000):
        await external_api_call()  # ❌
        await repo.create(session, data)

# Solution: Do I/O outside transaction
data_list = []
for i in range(10000):
    result = await external_api_call()  # ✅ Outside transaction
    data_list.append(result)

async with async_transaction_scope(db) as session:
    for data in data_list:
        await repo.create(session, data)  # ✅ Quick DB operations
```

### Issue 3: Forgotten Await

```python
# Problem
async with async_transaction_scope(db) as session:
    user_repo.async_create(session, name="John")  # ❌ Forgot await

# Solution
async with async_transaction_scope(db) as session:
    await user_repo.async_create(session, name="John")  # ✅
```

---

## Quick Reference

| Use Case | Pattern | Example |
|----------|---------|---------|
| Single DB operation | Direct repo call | `await repo.create(db, data)` |
| Multiple operations | `async_transaction_scope` | `async with async_transaction_scope(db)` |
| Read-only queries | `read_only_scope` | `async with read_only_scope(db)` |
| Service layer | `@async_transactional` | Decorator on service methods |
| Complex with rollback | `AsyncTransactionManager` | Savepoint support |
| N+1 prevention | `optimize_query_for_eager_loading` | Eager load relationships |

---

## Testing Transactions

```python
import pytest
from app.database.transaction import async_transaction_scope

@pytest.mark.asyncio
async def test_transaction_rollback(async_session):
    """Test transaction rollback on error."""
    try:
        async with async_transaction_scope(async_session) as session:
            user = await user_repo.async_create(session, email="test@test.com")
            raise ValueError("Simulated error")
    except ValueError:
        pass
    
    # Verify rollback
    result = await user_repo.async_get_by_email(async_session, "test@test.com")
    assert result is None  # User was rolled back
```

---

**Need help?** Check the implementation in `app/database/transaction.py`

