"""
Table EDA repository.
"""

from typing import Dict, List, Optional, Any

from sqlalchemy.orm import Session

from app import get_logger
from app.database.models.table_eda import TableEDATable

logger = get_logger(__name__)


class TableEDARepository:
    """Repository for TableEDA model operations."""

    def _log_prefix(self, table_name: Optional[str] = None) -> str:
        """Generate log prefix following team standards."""
        return f"[TableEDARepository] | [table={table_name or 'None'}]"

    def create(
        self,
        db: Session,
        table_name: str,
        row_count: int,
        column_stats: Dict[str, Any],
        summary: Optional[str] = None,
        insights: Optional[List[str]] = None
    ) -> TableEDATable:
        """Create a new table EDA record."""
        eda = TableEDATable(
            table_name=table_name,
            row_count=row_count,
            column_stats=column_stats,
            summary=summary,
            insights=insights
        )
        db.add(eda)
        db.commit()
        db.refresh(eda)
        logger.info(f"{self._log_prefix(table_name)} | Created EDA record")
        return eda

    def get_by_table_name(self, db: Session, table_name: str) -> Optional[TableEDATable]:
        """Get EDA by table name."""
        return db.query(TableEDATable).filter(TableEDATable.table_name == table_name).first()

    def update(
        self,
        db: Session,
        table_name: str,
        row_count: int,
        column_stats: Dict[str, Any],
        summary: Optional[str] = None,
        insights: Optional[List[str]] = None
    ) -> Optional[TableEDATable]:
        """Update existing EDA record."""
        eda = self.get_by_table_name(db, table_name)
        if not eda:
            return None

        eda.row_count = row_count
        eda.column_stats = column_stats
        if summary:
            eda.summary = summary
        if insights:
            eda.insights = insights

        db.commit()
        db.refresh(eda)
        logger.info(f"{self._log_prefix(table_name)} | Updated EDA record")
        return eda

    def upsert(
        self,
        db: Session,
        table_name: str,
        row_count: int,
        column_stats: Dict[str, Any],
        summary: Optional[str] = None,
        insights: Optional[List[str]] = None
    ) -> TableEDATable:
        """Create or update EDA record."""
        existing = self.get_by_table_name(db, table_name)
        if existing:
            return self.update(db, table_name, row_count, column_stats, summary, insights)
        return self.create(db, table_name, row_count, column_stats, summary, insights)

    def delete(self, db: Session, table_name: str) -> bool:
        """Delete EDA record."""
        eda = self.get_by_table_name(db, table_name)
        if eda:
            db.delete(eda)
            db.commit()
            logger.info(f"{self._log_prefix(table_name)} | Deleted EDA record")
            return True
        return False

    def get_all(self, db: Session) -> List[TableEDATable]:
        """Get all EDA records."""
        return db.query(TableEDATable).order_by(TableEDATable.table_name).all()
