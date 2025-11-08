"""
Service for managing per-user dynamic tables.

Creates and manages tables with pattern: __user_{user_id}_review_feedback
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Table, Column, Integer, String, Text, DateTime, MetaData,
    create_engine, inspect, text
)
from sqlalchemy.orm import Session
from datetime import datetime

from app import get_logger
from app.database.base import Base

logger = get_logger(__name__)


class UserTableService:
    """Service for managing per-user review feedback tables."""
    
    @staticmethod
    def get_user_table_name(user_id: int) -> str:
        """Get the table name for a specific user."""
        return f"__user_{user_id}_review_feedback"
    
    @staticmethod
    def create_user_table(db: Session, user_id: int) -> bool:
        """
        Create a review feedback table for a specific user.
        Also registers it in user_datasets and table_eda.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            True if created, False if already exists
        """
        table_name = UserTableService.get_user_table_name(user_id)
        
        # Check if table already exists
        inspector = inspect(db.bind)
        if table_name in inspector.get_table_names():
            logger.info(f"Table {table_name} already exists")
            return False
        
        # Create the table
        create_sql = f"""
        CREATE TABLE {table_name} (
            id SERIAL PRIMARY KEY,
            company_name VARCHAR(255) NOT NULL,
            category VARCHAR(255),
            rating INTEGER,
            text TEXT NOT NULL,
            source VARCHAR(255),
            date TIMESTAMP,
            author VARCHAR(255),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX idx_{table_name}_company ON {table_name}(company_name);
        CREATE INDEX idx_{table_name}_date ON {table_name}(date);
        CREATE INDEX idx_{table_name}_rating ON {table_name}(rating);
        """
        
        try:
            db.execute(text(create_sql))
            db.commit()
            logger.info(f"Created table {table_name} for user {user_id}")
            
            # Register in user_datasets
            UserTableService._register_in_user_datasets(db, user_id, table_name)
            
            # Register in table_eda
            UserTableService._register_in_table_eda(db, table_name)
            
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating table {table_name}: {e}")
            raise
    
    @staticmethod
    def _register_in_user_datasets(db: Session, user_id: int, table_name: str):
        """Register the user table in user_datasets."""
        from app.database.models.dataset import UserDatasetTable
        
        # Check if already registered
        existing = db.query(UserDatasetTable).filter(
            UserDatasetTable.table_name == table_name
        ).first()
        
        if existing:
            logger.info(f"Table {table_name} already registered in user_datasets")
            return
        
        # Create dataset entry
        dataset = UserDatasetTable(
            user_id=user_id,
            table_name=table_name,
            original_filename=None,
            description=f"User's review feedback table (auto-generated)",
            column_metadata={
                "company_name": {"type": "string", "description": "Company name"},
                "category": {"type": "string", "description": "Review category"},
                "rating": {"type": "integer", "description": "Rating (1-5)"},
                "text": {"type": "text", "description": "Review text content"},
                "source": {"type": "string", "description": "Review source"},
                "date": {"type": "timestamp", "description": "Review date"},
                "author": {"type": "string", "description": "Review author"}
            },
            row_count=0
        )
        
        db.add(dataset)
        db.commit()
        logger.info(f"Registered {table_name} in user_datasets")
    
    @staticmethod
    def _register_in_table_eda(db: Session, table_name: str):
        """Register the user table in table_eda with initial stats."""
        from app.database.models.table_eda import TableEDATable
        
        # Check if already registered
        existing = db.query(TableEDATable).filter(
            TableEDATable.table_name == table_name
        ).first()
        
        if existing:
            logger.info(f"Table {table_name} already registered in table_eda")
            return
        
        # Create EDA entry with initial stats
        eda = TableEDATable(
            table_name=table_name,
            row_count=0,
            column_stats={
                "company_name": {"type": "string", "distinct_count": 0},
                "category": {"type": "string", "distinct_count": 0},
                "rating": {"type": "integer", "min": None, "max": None, "distinct_count": 0},
                "text": {"type": "text"},
                "source": {"type": "string", "distinct_count": 0},
                "date": {"type": "timestamp", "min": None, "max": None},
                "author": {"type": "string", "distinct_count": 0}
            },
            summary="User's review feedback table (newly created, no data yet)",
            insights=["Table created but empty", "Waiting for review data to be added"]
        )
        
        db.add(eda)
        db.commit()
        logger.info(f"Registered {table_name} in table_eda")
    
    @staticmethod
    def drop_user_table(db: Session, user_id: int) -> bool:
        """
        Drop a user's review feedback table.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            True if dropped, False if doesn't exist
        """
        table_name = UserTableService.get_user_table_name(user_id)
        
        # Check if table exists
        inspector = inspect(db.bind)
        if table_name not in inspector.get_table_names():
            logger.info(f"Table {table_name} does not exist")
            return False
        
        try:
            db.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
            db.commit()
            logger.info(f"Dropped table {table_name}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error dropping table {table_name}: {e}")
            raise
    
    @staticmethod
    def insert_review(
        db: Session,
        user_id: int,
        company_name: str,
        review_text: str,
        rating: Optional[int] = None,
        category: Optional[str] = None,
        source: Optional[str] = None,
        date: Optional[datetime] = None,
        author: Optional[str] = None,
        update_counts: bool = True
    ) -> int:
        """
        Insert a review into user's table.
        
        Args:
            db: Database session
            user_id: User ID
            company_name: Company name
            review_text: Review text content
            rating: Rating (1-5)
            category: Category
            source: Source
            date: Review date
            author: Author name
            update_counts: Whether to update row counts in metadata tables
            
        Returns:
            ID of inserted review
        """
        from sqlalchemy import text as sql_text
        
        table_name = UserTableService.get_user_table_name(user_id)
        
        # Ensure table exists
        UserTableService.create_user_table(db, user_id)
        
        insert_sql = f"""
        INSERT INTO {table_name} 
        (company_name, text, rating, category, source, date, author, created_at, updated_at)
        VALUES 
        (:company_name, :text, :rating, :category, :source, :date, :author, :created_at, :updated_at)
        RETURNING id
        """
        
        result = db.execute(
            sql_text(insert_sql),
            {
                "company_name": company_name,
                "text": review_text,
                "rating": rating,
                "category": category,
                "source": source,
                "date": date,
                "author": author,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        )
        db.commit()
        
        review_id = result.fetchone()[0]
        logger.info(f"Inserted review {review_id} into {table_name}")
        
        # Update row counts in metadata tables
        if update_counts:
            UserTableService._update_row_counts(db, user_id, table_name)
        
        return review_id
    
    @staticmethod
    def _update_row_counts(db: Session, user_id: int, table_name: str):
        """Update row counts in user_datasets and table_eda."""
        from app.database.models.dataset import UserDatasetTable
        from app.database.models.table_eda import TableEDATable
        
        # Get actual row count
        count_result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        row_count = count_result.scalar()
        
        # Update user_datasets
        db.execute(
            text("UPDATE user_datasets SET row_count = :count, updated_at = :now WHERE table_name = :table_name"),
            {"count": row_count, "now": datetime.utcnow(), "table_name": table_name}
        )
        
        # Update table_eda
        db.execute(
            text("UPDATE table_eda SET row_count = :count, updated_at = :now WHERE table_name = :table_name"),
            {"count": row_count, "now": datetime.utcnow(), "table_name": table_name}
        )
        
        db.commit()
        logger.debug(f"Updated row count to {row_count} for {table_name}")
    
    @staticmethod
    def get_reviews(
        db: Session,
        user_id: int,
        company_name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get reviews from user's table.
        
        Args:
            db: Database session
            user_id: User ID
            company_name: Optional company filter
            limit: Max results
            offset: Offset for pagination
            
        Returns:
            List of review dictionaries
        """
        table_name = UserTableService.get_user_table_name(user_id)
        
        # Check if table exists
        inspector = inspect(db.bind)
        if table_name not in inspector.get_table_names():
            logger.warning(f"Table {table_name} does not exist")
            return []
        
        where_clause = f"WHERE company_name = :company_name" if company_name else ""
        
        query_sql = f"""
        SELECT * FROM {table_name}
        {where_clause}
        ORDER BY date DESC NULLS LAST, created_at DESC
        LIMIT :limit OFFSET :offset
        """
        
        params = {"limit": limit, "offset": offset}
        if company_name:
            params["company_name"] = company_name
        
        result = db.execute(text(query_sql), params)
        
        columns = result.keys()
        rows = result.fetchall()
        
        return [dict(zip(columns, row)) for row in rows]
    
    @staticmethod
    def count_reviews(
        db: Session,
        user_id: int,
        company_name: Optional[str] = None
    ) -> int:
        """
        Count reviews in user's table.
        
        Args:
            db: Database session
            user_id: User ID
            company_name: Optional company filter
            
        Returns:
            Count of reviews
        """
        table_name = UserTableService.get_user_table_name(user_id)
        
        # Check if table exists
        inspector = inspect(db.bind)
        if table_name not in inspector.get_table_names():
            return 0
        
        where_clause = f"WHERE company_name = :company_name" if company_name else ""
        
        query_sql = f"SELECT COUNT(*) FROM {table_name} {where_clause}"
        
        params = {"company_name": company_name} if company_name else {}
        result = db.execute(text(query_sql), params)
        
        return result.scalar()
    
    @staticmethod
    def get_user_companies(db: Session, user_id: int) -> List[str]:
        """
        Get all companies in user's table.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of company names
        """
        table_name = UserTableService.get_user_table_name(user_id)
        
        # Check if table exists
        inspector = inspect(db.bind)
        if table_name not in inspector.get_table_names():
            return []
        
        query_sql = f"""
        SELECT DISTINCT company_name 
        FROM {table_name}
        ORDER BY company_name
        """
        
        result = db.execute(text(query_sql))
        return [row[0] for row in result.fetchall()]
    
    @staticmethod
    def table_exists(db: Session, user_id: int) -> bool:
        """
        Check if user's table exists.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            True if table exists
        """
        table_name = UserTableService.get_user_table_name(user_id)
        inspector = inspect(db.bind)
        return table_name in inspector.get_table_names()
