"""Create company command."""

from app import get_logger
from app.database.base import SessionLocal
from app.database.repositories.company import CompanyRepository

logger = get_logger(__name__)


def create_company(
    name: str,
    description: str = None,
    industry: str = None,
    website: str = None
):
    """Create a new company."""
    
    logger.info(f"Creating company: {name}")
    
    db = SessionLocal()
    
    try:
        repo = CompanyRepository()
        
        # Check if company exists
        existing = repo.get_by_name(db, name)
        if existing:
            logger.info(f"Company {name} already exists with ID: {existing.id}")
            return existing
        
        # Create company
        company = repo.create(
            db=db,
            name=name,
            description=description,
            industry=industry,
            website=website
        )
        
        logger.info(f"✅ Created company: {company.id} - {company.name}")
        return company
        
    finally:
        db.close()
