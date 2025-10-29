"""
Create the PostgreSQL database if it doesn't exist.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError

from app import get_logger
from app.config import SETTINGS

logger = get_logger(__name__)


def create_database():
    """Create the database if it doesn't exist."""
    
    # Parse database URL to get database name
    db_url = SETTINGS.DATABASE_URL
    
    # Connect to postgres database (default) to create our database
    if "postgresql" in db_url:
        # Replace database name with 'postgres' to connect to default db
        parts = db_url.rsplit('/', 1)
        postgres_url = f"{parts[0]}/postgres"
        db_name = parts[1].split('?')[0]  # Remove query params if any
        
        logger.info(f"Checking if database '{db_name}' exists...")
        
        try:
            # Try to connect to the target database
            engine = create_engine(db_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"✅ Database '{db_name}' already exists")
            return True
            
        except OperationalError:
            # Database doesn't exist, create it
            logger.info(f"Database '{db_name}' doesn't exist, creating...")
            
            try:
                # Connect to postgres database
                engine = create_engine(postgres_url, isolation_level="AUTOCOMMIT")
                with engine.connect() as conn:
                    conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                logger.info(f"✅ Database '{db_name}' created successfully")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to create database: {e}")
                return False
                
    elif "sqlite" in db_url:
        logger.info("Using SQLite - database will be created automatically")
        return True
        
    else:
        logger.error(f"Unsupported database type in URL: {db_url}")
        return False


if __name__ == "__main__":
    success = create_database()
    sys.exit(0 if success else 1)
