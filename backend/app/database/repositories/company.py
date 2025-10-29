"""
Company repository.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app import get_logger
from app.database.models.company import CompanyTable

logger = get_logger(__name__)


class CompanyRepository:
    """Repository for Company model operations."""

    def _log_prefix(self, user_id: Optional[str] = None, company_id: Optional[int] = None) -> str:
        """Generate log prefix following team standards."""
        return f"[CompanyRepository] | [user_id={user_id or 'None'}] | [company_id={company_id or 'None'}]"

    def create(
        self,
        db: Session,
        name: str,
        description: Optional[str] = None,
        industry: Optional[str] = None,
        website: Optional[str] = None
    ) -> CompanyTable:
        """Create a new company."""
        company = CompanyTable(
            name=name,
            description=description,
            industry=industry,
            website=website
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        logger.info(f"{self._log_prefix(company_id=company.id)} | Created company: {name}")
        return company

    def get_by_id(self, db: Session, company_id: int) -> Optional[CompanyTable]:
        """Get company by ID."""
        return db.query(CompanyTable).filter(CompanyTable.id == company_id).first()

    def get_by_name(self, db: Session, name: str) -> Optional[CompanyTable]:
        """Get company by name."""
        return db.query(CompanyTable).filter(CompanyTable.name == name).first()

    def get_or_create(self, db: Session, name: str, **kwargs) -> CompanyTable:
        """Get company by name or create if doesn't exist."""
        company = self.get_by_name(db, name)
        if company:
            return company
        return self.create(db, name, **kwargs)

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[CompanyTable]:
        """Get all companies with pagination."""
        return (
            db.query(CompanyTable)
            .order_by(CompanyTable.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, db: Session, company_id: int, **kwargs) -> Optional[CompanyTable]:
        """Update company."""
        company = self.get_by_id(db, company_id)
        if not company:
            return None

        for key, value in kwargs.items():
            if hasattr(company, key):
                setattr(company, key, value)

        company.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(company)
        logger.info(f"{self._log_prefix(company_id=company_id)} | Updated company")
        return company

    def delete(self, db: Session, company_id: int) -> bool:
        """Delete company by ID."""
        company = self.get_by_id(db, company_id)
        if company:
            db.delete(company)
            db.commit()
            logger.info(f"{self._log_prefix(company_id=company_id)} | Deleted company")
            return True
        return False
