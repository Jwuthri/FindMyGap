"""Seed default companies command."""

from app import get_logger
from app.database.base import SessionLocal
from app.database.repositories.company import CompanyRepository

logger = get_logger(__name__)


COMPANIES = [
    {
        "name": "Spotify",
        "description": "Music streaming service and media services provider",
        "industry": "Technology",
        "website": "https://spotify.com"
    },
    {
        "name": "Slack",
        "description": "Business communication platform and collaboration hub",
        "industry": "Technology",
        "website": "https://slack.com"
    },
    {
        "name": "Notion",
        "description": "All-in-one workspace for notes, docs, and collaboration",
        "industry": "Technology",
        "website": "https://notion.so"
    },
    {
        "name": "Netflix",
        "description": "Streaming service for movies and TV shows",
        "industry": "Entertainment",
        "website": "https://netflix.com"
    }
]


def seed_companies():
    """Seed default companies into the database."""
    
    logger.info("Seeding default companies...")
    
    db = SessionLocal()
    
    try:
        repo = CompanyRepository()
        created_count = 0
        existing_count = 0
        
        for company_data in COMPANIES:
            company = repo.get_or_create(db, **company_data)
            if company.created_at == company.updated_at:
                created_count += 1
                logger.info(f"✅ Created: {company.name}")
            else:
                existing_count += 1
                logger.info(f"ℹ️  Exists: {company.name}")
        
        logger.info(f"\n✅ Seeding complete: {created_count} created, {existing_count} already existed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to seed companies: {e}", exc_info=True)
        return False
        
    finally:
        db.close()
