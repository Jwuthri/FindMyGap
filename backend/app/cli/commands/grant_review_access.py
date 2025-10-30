"""Grant review access command."""

from typing import Optional

from app import get_logger
from app.database.base import SessionLocal
from app.database.repositories.company import CompanyRepository
from app.database.repositories.review import ReviewRepository
from app.database.repositories.user import UserRepository
from app.database.repositories.user_review_feedback import UserReviewFeedbackRepository

logger = get_logger(__name__)


def grant_company_reviews_access(
    user_id: int,
    company_id: int,
    access_type: str = "platform",
    is_owner: bool = False
):
    """
    Grant a user access to all reviews from a specific company.
    
    Args:
        user_id: User ID to grant access to
        company_id: Company ID whose reviews to grant access to
        access_type: Type of access (default: "platform")
        is_owner: Whether user should be marked as owner (default: False)
    """
    logger.info("="*60)
    logger.info("GRANTING BULK REVIEW ACCESS")
    logger.info("="*60)
    
    db = SessionLocal()
    
    try:
        user_repo = UserRepository()
        company_repo = CompanyRepository()
        review_repo = ReviewRepository()
        user_review_repo = UserReviewFeedbackRepository()
        
        # Validate user exists
        user = user_repo.get_by_id(db, user_id)
        if not user:
            logger.error(f"❌ User with ID {user_id} not found")
            return False
        
        logger.info(f"User: {user.email} (ID: {user.id})")
        
        # Validate company exists
        company = company_repo.get_by_id(db, company_id)
        if not company:
            logger.error(f"❌ Company with ID {company_id} not found")
            return False
        
        logger.info(f"Company: {company.name} (ID: {company.id})")
        
        # Get all reviews for this company
        all_reviews = review_repo.get_by_company(db, company_id, skip=0, limit=10000)
        
        if not all_reviews:
            logger.warning(f"⚠️  No reviews found for company {company.name}")
            return True
        
        logger.info(f"Found {len(all_reviews)} reviews for {company.name}")
        
        # Extract review IDs
        review_ids = [review.id for review in all_reviews]
        
        # Grant bulk access
        logger.info(f"Granting access with type='{access_type}', is_owner={is_owner}...")
        count = user_review_repo.bulk_grant_access(
            db=db,
            user_id=user_id,
            review_ids=review_ids,
            is_owner=is_owner,
            access_type=access_type
        )
        
        logger.info(f"\n✅ Successfully granted access to {count} reviews")
        logger.info(f"   User: {user.email}")
        logger.info(f"   Company: {company.name}")
        logger.info(f"   Total Reviews: {len(all_reviews)}")
        logger.info(f"   New Access Grants: {count}")
        logger.info(f"   Already Had Access: {len(all_reviews) - count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to grant access: {e}", exc_info=True)
        return False
        
    finally:
        db.close()


def grant_all_reviews_access(
    user_id: int,
    access_type: str = "platform",
    is_owner: bool = False
):
    """
    Grant a user access to ALL reviews in the system.
    
    Args:
        user_id: User ID to grant access to
        access_type: Type of access (default: "platform")
        is_owner: Whether user should be marked as owner (default: False)
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
        
        # Extract review IDs
        review_ids = [review.id for review in all_reviews]
        
        # Grant bulk access
        logger.info(f"Granting access with type='{access_type}', is_owner={is_owner}...")
        count = user_review_repo.bulk_grant_access(
            db=db,
            user_id=user_id,
            review_ids=review_ids,
            is_owner=is_owner,
            access_type=access_type
        )
        
        logger.info(f"\n✅ Successfully granted access to {count} reviews")
        logger.info(f"   User: {user.email}")
        logger.info(f"   Total Reviews: {len(all_reviews)}")
        logger.info(f"   New Access Grants: {count}")
        logger.info(f"   Already Had Access: {len(all_reviews) - count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to grant access: {e}", exc_info=True)
        return False
        
    finally:
        db.close()


def revoke_company_reviews_access(user_id: int, company_id: int):
    """
    Revoke a user's access to all reviews from a specific company.
    
    Args:
        user_id: User ID to revoke access from
        company_id: Company ID whose reviews to revoke access to
    """
    logger.info("="*60)
    logger.info("REVOKING BULK REVIEW ACCESS")
    logger.info("="*60)
    
    db = SessionLocal()
    
    try:
        user_repo = UserRepository()
        company_repo = CompanyRepository()
        review_repo = ReviewRepository()
        user_review_repo = UserReviewFeedbackRepository()
        
        # Validate user exists
        user = user_repo.get_by_id(db, user_id)
        if not user:
            logger.error(f"❌ User with ID {user_id} not found")
            return False
        
        logger.info(f"User: {user.email} (ID: {user.id})")
        
        # Validate company exists
        company = company_repo.get_by_id(db, company_id)
        if not company:
            logger.error(f"❌ Company with ID {company_id} not found")
            return False
        
        logger.info(f"Company: {company.name} (ID: {company.id})")
        
        # Get all reviews for this company
        all_reviews = review_repo.get_by_company(db, company_id, skip=0, limit=10000)
        
        if not all_reviews:
            logger.warning(f"⚠️  No reviews found for company {company.name}")
            return True
        
        logger.info(f"Found {len(all_reviews)} reviews for {company.name}")
        
        # Revoke access for each review
        revoked_count = 0
        for review in all_reviews:
            if user_review_repo.revoke_access(db, user_id, review.id):
                revoked_count += 1
        
        logger.info(f"\n✅ Successfully revoked access to {revoked_count} reviews")
        logger.info(f"   User: {user.email}")
        logger.info(f"   Company: {company.name}")
        logger.info(f"   Total Reviews: {len(all_reviews)}")
        logger.info(f"   Access Revoked: {revoked_count}")
        logger.info(f"   No Access Found: {len(all_reviews) - revoked_count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to revoke access: {e}", exc_info=True)
        return False
        
    finally:
        db.close()
