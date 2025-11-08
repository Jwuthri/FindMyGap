"""
Example script demonstrating the grant_review_access functionality.

This can be run directly or used as a reference for integration.
"""

from app import get_logger
from app.database.base import SessionLocal
from app.database.repositories.company import CompanyRepository
from app.database.repositories.user import UserRepository
from app.services.user_table_service import UserTableService

logger = get_logger(__name__)


def example_workflow():
    """
    Complete example workflow showing how to:
    1. Create/get a user
    2. Get company information
    3. Grant access to company reviews
    4. Verify access
    """
    db = SessionLocal()
    
    try:
        user_repo = UserRepository()
        company_repo = CompanyRepository()
        
        # Step 1: Get or create a test user
        logger.info("Step 1: Getting user...")
        user = user_repo.get_by_email(db, "john@example.com")
        if not user:
            user = user_repo.create(
                db=db,
                email="john@example.com",
                username="john"
            )
            logger.info(f"Created user: {user.id} - {user.email}")
        else:
            logger.info(f"Found user: {user.id} - {user.email}")
        
        # Step 2: Get company (assuming Spotify with ID 1)
        logger.info("\nStep 2: Getting company...")
        company = company_repo.get_by_id(db, 1)
        if not company:
            logger.error("Company not found. Run 'seed-companies' first.")
            return
        logger.info(f"Found company: {company.id} - {company.name}")
        
        # Step 3: Check current access
        logger.info("\nStep 3: Checking current access...")
        current_reviews = UserTableService.get_reviews(db, user.id)
        logger.info(f"User currently has access to {len(current_reviews)} reviews")
        
        # Step 4: Grant access using the CLI function
        logger.info("\nStep 4: Granting access to company reviews...")
        from app.cli.commands.grant_review_access import grant_company_reviews_access
        
        success = grant_company_reviews_access(
            user_id=user.id,
            company_id=company.id,
            access_type="platform",
            is_owner=False
        )
        
        if success:
            logger.info("✅ Access granted successfully")
        else:
            logger.error("❌ Failed to grant access")
            return
        
        # Step 5: Verify access
        logger.info("\nStep 5: Verifying access...")
        updated_reviews = UserTableService.get_reviews(db, user.id)
        logger.info(f"User now has access to {len(updated_reviews)} reviews")
        
        # Step 6: Show some sample reviews
        logger.info("\nStep 6: Sample accessible reviews:")
        for i, review in enumerate(updated_reviews[:3], 1):
            review_text = review.get('text', '')[:60] if isinstance(review, dict) else str(review)[:60]
            logger.info(f"  {i}. Review {review.get('id', 'N/A')}: {review_text}...")
        
        logger.info("\n" + "="*60)
        logger.info("WORKFLOW COMPLETE")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"Error in workflow: {e}", exc_info=True)
        
    finally:
        db.close()


if __name__ == "__main__":
    example_workflow()
