"""List entities command - helper for finding IDs."""

from app import get_logger
from app.database.base import SessionLocal
from app.database.repositories.company import CompanyRepository
from app.database.repositories.review import ReviewRepository
from app.database.repositories.user import UserRepository
from app.services.user_table_service import UserTableService

logger = get_logger(__name__)


def list_users():
    """List all users with their IDs."""
    logger.info("="*60)
    logger.info("USERS")
    logger.info("="*60)
    
    db = SessionLocal()
    
    try:
        user_repo = UserRepository()
        users = user_repo.get_all(db, skip=0, limit=1000)
        
        if not users:
            logger.info("No users found")
            return
        
        logger.info(f"\nFound {len(users)} users:\n")
        for user in users:
            logger.info(f"  ID: {user.id:3d} | Email: {user.email:30s} | Username: {user.username or 'N/A'}")
        
    finally:
        db.close()


def list_companies():
    """List all companies with their IDs and review counts."""
    logger.info("="*60)
    logger.info("COMPANIES")
    logger.info("="*60)
    
    db = SessionLocal()
    
    try:
        company_repo = CompanyRepository()
        review_repo = ReviewRepository()
        
        companies = company_repo.get_all(db, skip=0, limit=1000)
        
        if not companies:
            logger.info("No companies found")
            logger.info("\nRun: python -m app.cli.main seed-companies")
            return
        
        logger.info(f"\nFound {len(companies)} companies:\n")
        for company in companies:
            reviews = review_repo.get_by_company(db, company.name, skip=0, limit=10000)
            review_count = len(reviews)
            logger.info(f"  ID: {company.id:3d} | Name: {company.name:20s} | Reviews: {review_count:4d}")
        
    finally:
        db.close()


def list_user_access(user_id: int):
    """
    List all reviews a user has access to, grouped by company.
    
    Args:
        user_id: User ID to check
    """
    logger.info("="*60)
    logger.info(f"USER ACCESS REPORT - User ID: {user_id}")
    logger.info("="*60)
    
    db = SessionLocal()
    
    try:
        user_repo = UserRepository()
        company_repo = CompanyRepository()
        
        # Get user
        user = user_repo.get_by_id(db, user_id)
        if not user:
            logger.error(f"❌ User with ID {user_id} not found")
            return
        
        logger.info(f"\nUser: {user.email} (ID: {user.id})")
        
        # Get all reviews user has access to
        reviews = UserTableService.get_reviews(db, user_id, limit=10000, offset=0)
        
        if not reviews:
            logger.info("\n⚠️  User has no review access")
            return
        
        logger.info(f"\nTotal Reviews: {len(reviews)}")
        
        # Group by company
        company_groups = {}
        for review in reviews:
            company_name = review.company_name
            if company_name not in company_groups:
                company_groups[company_name] = []
            company_groups[company_name].append(review)
        
        logger.info(f"Companies: {len(company_groups)}\n")
        
        # Show breakdown by company
        for company_name, company_reviews in sorted(company_groups.items()):
            logger.info(f"  {company_name:20s} - {len(company_reviews):4d} reviews")
        
        logger.info(f"\nTotal: {len(reviews)} reviews from {len(company_groups)} companies")
        
    finally:
        db.close()


def list_all():
    """List all users and companies."""
    list_users()
    logger.info("\n")
    list_companies()
