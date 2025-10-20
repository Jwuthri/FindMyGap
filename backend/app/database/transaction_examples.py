"""
Real-world transaction examples for FastAPI routes.

These examples demonstrate common transaction patterns you'll use in your application.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database.session import get_async_session
from app.database.transaction import (
    async_transaction_scope,
    read_only_scope,
    AsyncTransactionManager,
    optimize_query_for_eager_loading
)
from app.database.repositories.user import UserRepository

# Initialize router and repository
router = APIRouter(prefix="/examples", tags=["transaction-examples"])
user_repo = UserRepository()


# Pydantic models
class UserCreate(BaseModel):
    email: str
    clerk_user_id: str
    first_name: str | None = None
    last_name: str | None = None


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None


# ============================================================================
# EXAMPLE 1: Simple Read-Only Query
# ============================================================================

@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Simple read operation - no transaction needed.
    Use read_only_scope to make intent clear.
    """
    async with read_only_scope(db) as session:
        user = await user_repo.async_get(session, user_id)
        if not user:
            raise HTTPException(404, "User not found")
        return user


# ============================================================================
# EXAMPLE 2: Simple Create (Single Operation)
# ============================================================================

@router.post("/users/simple")
async def create_user_simple(
    user: UserCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Single operation - repository handles transaction internally.
    No explicit transaction scope needed.
    """
    return await user_repo.async_create(db, **user.dict())


# ============================================================================
# EXAMPLE 3: Multi-Step Transaction
# ============================================================================

@router.post("/users/with-profile")
async def create_user_with_profile(
    user: UserCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Multiple operations that must succeed together.
    Use async_transaction_scope for explicit transaction control.
    """
    async with async_transaction_scope(db) as session:
        # Create user
        new_user = await user_repo.async_create(session, **user.dict())
        
        # Create related records (pseudo-code, adapt to your models)
        # profile = await profile_repo.async_create(
        #     session,
        #     user_id=new_user.id,
        #     bio="",
        #     avatar_url=None
        # )
        
        # settings = await settings_repo.async_create(
        #     session,
        #     user_id=new_user.id,
        #     email_notifications=True
        # )
        
        return {
            "user": new_user,
            # "profile": profile,
            # "settings": settings
        }


# ============================================================================
# EXAMPLE 4: Update with Validation
# ============================================================================

@router.patch("/users/{user_id}")
async def update_user(
    user_id: int,
    updates: UserUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Update with validation - transaction ensures atomicity.
    """
    async with async_transaction_scope(db) as session:
        # Get user
        user = await user_repo.async_get(session, user_id)
        if not user:
            raise HTTPException(404, "User not found")
        
        # Validate updates (example)
        if updates.first_name and len(updates.first_name) < 2:
            raise HTTPException(400, "First name too short")
        
        # Apply updates
        updated_user = await user_repo.async_update(
            session,
            user_id,
            **updates.dict(exclude_unset=True)
        )
        
        # Log audit trail (pseudo-code)
        # await audit_repo.async_create(
        #     session,
        #     user_id=user_id,
        #     action="update",
        #     changes=updates.dict(exclude_unset=True)
        # )
        
        return updated_user


# ============================================================================
# EXAMPLE 5: Complex Operation with Savepoints
# ============================================================================

@router.post("/users/batch-import")
async def batch_import_users(
    users: list[UserCreate],
    db: AsyncSession = Depends(get_async_session)
):
    """
    Import multiple users, skip invalid ones without failing entire batch.
    Uses savepoints to rollback individual failures.
    """
    manager = AsyncTransactionManager(db)
    results = {
        "success": [],
        "failed": [],
        "total": len(users)
    }
    
    try:
        for user_data in users:
            # Create savepoint before each user
            savepoint = await manager.savepoint()
            
            try:
                # Try to create user
                user = await user_repo.async_create(db, **user_data.dict())
                results["success"].append({
                    "email": user.email,
                    "id": user.id
                })
                
            except Exception as e:
                # Rollback this user only, continue with others
                await manager.rollback_to_savepoint(savepoint)
                results["failed"].append({
                    "email": user_data.email,
                    "error": str(e)
                })
        
        # Commit all successful operations
        await manager.commit()
        return results
        
    except Exception as e:
        # Critical error - rollback everything
        await manager.rollback()
        raise HTTPException(500, f"Batch import failed: {str(e)}")


# ============================================================================
# EXAMPLE 6: Transaction with Background Task
# ============================================================================

async def send_welcome_email_task(user_id: int):
    """
    Background task with its own database session and transaction.
    """
    from app.database.session import async_session_maker
    
    async with async_session_maker() as db:
        async with async_transaction_scope(db) as session:
            user = await user_repo.async_get(session, user_id)
            if not user:
                return
            
            # Send email (pseudo-code)
            # await email_service.send_welcome(user.email)
            
            # Mark as sent
            await user_repo.async_update(
                session,
                user_id,
                # welcome_email_sent=True
            )


@router.post("/users/with-email")
async def create_user_with_email(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Create user and send welcome email in background.
    Separate transactions to avoid holding DB lock during email send.
    """
    # Create user in main transaction
    async with async_transaction_scope(db) as session:
        new_user = await user_repo.async_create(session, **user.dict())
    
    # Schedule email in separate transaction
    background_tasks.add_task(send_welcome_email_task, new_user.id)
    
    return new_user


# ============================================================================
# EXAMPLE 7: Conditional Transaction Logic
# ============================================================================

@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Deactivate user with conditional logic.
    """
    async with async_transaction_scope(db) as session:
        user = await user_repo.async_get(session, user_id)
        if not user:
            raise HTTPException(404, "User not found")
        
        # Check if user can be deactivated
        # has_active_subscriptions = await subscription_repo.has_active(
        #     session, user_id
        # )
        # if has_active_subscriptions:
        #     raise HTTPException(400, "Cancel subscriptions first")
        
        # Deactivate user
        await user_repo.async_update(
            session,
            user_id,
            # is_active=False,
            # deactivated_at=datetime.utcnow()
        )
        
        # Cleanup related data
        # await session_repo.async_delete_all_for_user(session, user_id)
        # await token_repo.async_revoke_all(session, user_id)
        
        return {"message": "User deactivated", "user_id": user_id}


# ============================================================================
# EXAMPLE 8: Query Optimization (Eager Loading)
# ============================================================================

@router.get("/users/with-relations")
async def list_users_optimized(
    db: AsyncSession = Depends(get_async_session),
    skip: int = 0,
    limit: int = 100
):
    """
    Fetch users with related data efficiently (no N+1 queries).
    """
    from sqlalchemy import select
    from app.database.models.user import UserTable
    
    async with read_only_scope(db) as session:
        # Build query with eager loading
        query = select(UserTable).offset(skip).limit(limit)
        
        # Add relationships to eager load (prevents N+1)
        # query = optimize_query_for_eager_loading(
        #     query,
        #     relationships=['profile', 'settings']
        # )
        
        result = await session.execute(query)
        users = result.scalars().unique().all()
        
        return users


# ============================================================================
# USAGE NOTE
# ============================================================================

"""
To use these examples:

1. Import into your main app:
   ```python
   from app.database.transaction_examples import router as examples_router
   app.include_router(examples_router)
   ```

2. Access at: http://localhost:8000/examples/users

3. Adapt patterns to your specific models and repositories

4. Remove this file in production (it's for learning/reference)
"""

