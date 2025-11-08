"""
CLI command to migrate from user_review_feedback to per-user tables.

Usage:
    python -m app.cli.commands.migrate_user_tables
"""

import click
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import get_logger
from app.database.base import SessionLocal
from app.services.user_table_service import UserTableService

logger = get_logger(__name__)


@click.command()
@click.option('--dry-run', is_flag=True, help='Show what would be migrated without actually migrating')
@click.option('--drop-old', is_flag=True, help='Drop the old user_review_feedback table after migration')
def migrate_user_tables(dry_run: bool, drop_old: bool):
    """
    Migrate data from user_review_feedback to per-user tables.
    
    Creates __user_{user_id}_review_feedback tables for each user
    and copies their reviews from the old shared table.
    """
    db: Session = SessionLocal()
    
    try:
        # Check if old table exists
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'user_review_feedback'
            )
        """))
        
        if not result.scalar():
            logger.info("Old user_review_feedback table does not exist. Nothing to migrate.")
            return
        
        # Get all unique user IDs from old table
        result = db.execute(text("""
            SELECT DISTINCT user_id, COUNT(*) as review_count
            FROM user_review_feedback
            GROUP BY user_id
            ORDER BY user_id
        """))
        
        users = result.fetchall()
        
        if not users:
            logger.info("No users found in user_review_feedback table")
            return
        
        logger.info(f"Found {len(users)} users to migrate")
        
        for user_id, review_count in users:
            logger.info(f"\n{'='*60}")
            logger.info(f"Migrating user {user_id} ({review_count} reviews)")
            
            if dry_run:
                logger.info(f"[DRY RUN] Would create table: {UserTableService.get_user_table_name(user_id)}")
                logger.info(f"[DRY RUN] Would copy {review_count} reviews")
                continue
            
            # Create user's table (this also registers in user_datasets and table_eda)
            table_name = UserTableService.get_user_table_name(user_id)
            UserTableService.create_user_table(db, user_id)
            
            # Copy reviews
            copy_sql = f"""
            INSERT INTO {table_name} 
            (company_name, category, rating, text, source, date, author, created_at, updated_at)
            SELECT 
                company_name, category, rating, text, source, date, author, created_at, updated_at
            FROM user_review_feedback
            WHERE user_id = :user_id
            """
            
            db.execute(text(copy_sql), {"user_id": user_id})
            db.commit()
            
            # Verify and update metadata
            verify_result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            migrated_count = verify_result.scalar()
            
            if migrated_count == review_count:
                logger.info(f"✓ Successfully migrated {migrated_count} reviews for user {user_id}")
                # Update row counts in metadata tables
                UserTableService._update_row_counts(db, user_id, table_name)
            else:
                logger.error(f"✗ Mismatch! Expected {review_count}, got {migrated_count}")
        
        logger.info(f"\n{'='*60}")
        logger.info("Migration complete!")
        
        if drop_old and not dry_run:
            logger.info("\nDropping old user_review_feedback table...")
            db.execute(text("DROP TABLE IF EXISTS user_review_feedback CASCADE"))
            db.commit()
            logger.info("✓ Old table dropped")
        elif not dry_run:
            logger.info("\nOld user_review_feedback table preserved (use --drop-old to remove it)")
        
    except Exception as e:
        logger.error(f"Error during migration: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_user_tables()
