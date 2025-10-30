"""Create user command."""

from app import get_logger
from app.database.base import SessionLocal
from app.database.repositories.user import UserRepository

logger = get_logger(__name__)


def create_user(email: str, username: str = None, full_name: str = None):
    """Create a new user."""
    
    logger.info(f"Creating user: {email}")
    
    db = SessionLocal()
    
    try:
        repo = UserRepository()
        
        # Check if user exists
        existing = repo.get_by_email(db, email)
        if existing:
            logger.error(f"User with email {email} already exists")
            return None
        
        # Create user
        user = repo.create(
            db=db,
            email=email,
            username=username or email.split('@')[0],
            full_name=full_name
        )
        
        logger.info(f"✅ Created user: {user.id} - {user.email}")
        return user
        
    finally:
        db.close()
