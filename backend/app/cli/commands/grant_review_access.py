"""Grant review access command."""

from app import get_logger
from app.database.base import SessionLocal
from app.database.repositories.review import ReviewRepository
from app.database.repositories.user import UserRepository
from app.services.user_table_service import UserTableService

logger = get_logger(__name__)


def grant_company_reviews_access(user_id: int, company_name: str):
    """
    Grant a user access to all reviews from a specific company by copying them.
    
    Args:
        user_id: User ID to grant access to
        company_name: Company name whose reviews to copy
    """
    logger.info("="*60)
    logger.info("GRANTING BULK REVIEW ACCESS")
    logger.info("="*60)
    
    db = SessionLocal()
    
    try:
        user_repo = UserRepository()
        review_repo = ReviewRepository()
        
        # Validate user exists
        user = user_repo.get_by_id(db, user_id)
        if not user:
            logger.error(f"❌ User with ID {user_id} not found")
            return False
        
        logger.info(f"User: {user.email} (ID: {user.id})")
        logger.info(f"Company: {company_name}")
        
        # Ensure user's table exists
        UserTableService.create_user_table(db, user_id)
        
        # Get all reviews for this company
        all_reviews = review_repo.get_by_company(db, company_name, skip=0, limit=10000)
        
        if not all_reviews:
            logger.warning(f"⚠️  No reviews found for company {company_name}")
            return True
        
        logger.info(f"Found {len(all_reviews)} reviews for {company_name}")
        logger.info("Copying reviews to user's table...")
        
        # Copy each review to user's table (batch mode - update counts at end)
        count = 0
        for review in all_reviews:
            UserTableService.insert_review(
                db=db,
                user_id=user_id,
                company_name=review.company_name,
                review_text=review.text,
                rating=review.rating,
                category=review.category,
                source=review.source,
                date=review.date,
                author=review.author,
                update_counts=False  # Don't update on each insert for performance
            )
            count += 1
        
        # Update counts once at the end
        table_name = UserTableService.get_user_table_name(user_id)
        UserTableService._update_row_counts(db, user_id, table_name)
        
        logger.info(f"\n✅ Successfully copied {count} reviews")
        logger.info(f"   User: {user.email}")
        logger.info(f"   Company: {company_name}")
        logger.info(f"   Reviews Copied: {count}")
        logger.info(f"   Table: {UserTableService.get_user_table_name(user_id)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to grant access: {e}", exc_info=True)
        return False
        
    finally:
        db.close()


def grant_all_reviews_access(user_id: int):
    """
    Grant a user access to ALL reviews in the system by copying them.
    
    Args:
        user_id: User ID to grant access to
    """
    logger.info("="*60)
    logger.info("GRANTING ACCESS TO ALL REVIEWS")
    logger.info("="*60)
    
    db = SessionLocal()
    
    try:
        user_repo = UserRepository()
        review_repo = ReviewRepository()
        user_review_repo = UserReviewFeedbackRepository()
        
        # Validate user exists
        user = user_repo.get_by_id(db, user_id)
        if not user:
            logger.error(f"❌ User with ID {user_id} not found")
            return False
        
        logger.info(f"User: {user.email} (ID: {user.id})")
        
        # Get all reviews
        all_reviews = review_repo.get_all(db, skip=0, limit=100000)
        
        if not all_reviews:
            logger.warning("⚠️  No reviews found in the system")
            return True
        
        logger.info(f"Found {len(all_reviews)} total reviews in the system")
        logger.info("Copying reviews to user's table...")
        
        # Copy each review to user's table
        count = 0
        for review in all_reviews:
            user_review_repo.create(
                db=db,
                user_id=user_id,
                company_name=review.company_name,
                text=review.text,
                rating=review.rating,
                category=review.category,
                source=review.source,
                date=review.date,
                author=review.author
            )
            count += 1
        
        logger.info(f"\n✅ Successfully copied {count} reviews")
        logger.info(f"   User: {user.email}")
        logger.info(f"   Reviews Copied: {count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to grant access: {e}", exc_info=True)
        return False
        
    finally:
        db.close()


def revoke_company_reviews_access(user_id: int, company_name: str):
    """
    Revoke a user's access to all reviews from a specific company by deleting them.
    
    Args:
        user_id: User ID to revoke access from
        company_name: Company name whose reviews to remove
    """
    logger.info("="*60)
    logger.info("REVOKING BULK REVIEW ACCESS")
    logger.info("="*60)
    
    db = SessionLocal()
    
    try:
        from sqlalchemy import and_
        from app.database.models.user_review_feedback import UserReviewFeedbackTable
        
        user_repo = UserRepository()
        
        # Validate user exists
        user = user_repo.get_by_id(db, user_id)
        if not user:
            logger.error(f"❌ User with ID {user_id} not found")
            return False
        
        logger.info(f"User: {user.email} (ID: {user.id})")
        logger.info(f"Company: {company_name}")
        
        # Delete all user reviews for this company
        result = db.query(UserReviewFeedbackTable).filter(
            and_(
                UserReviewFeedbackTable.user_id == user_id,
                UserReviewFeedbackTable.company_name == company_name
            )
        ).delete()
        
        db.commit()
        
        logger.info(f"\n✅ Successfully deleted {result} reviews")
        logger.info(f"   User: {user.email}")
        logger.info(f"   Company: {company_name}")
        logger.info(f"   Reviews Deleted: {result}")
        
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to revoke access: {e}", exc_info=True)
        return False
        
    finally:
        db.close()
