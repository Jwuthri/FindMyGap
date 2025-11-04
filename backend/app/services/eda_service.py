"""
EDA Service - generates and manages table EDA using LLM.
"""

from typing import Any, Dict, List, Optional

import pandas as pd
from agno.models.openai import OpenAIChat
from sqlalchemy.orm import Session

from app import get_logger
from app.core.llm.eda_generator import EDAGenerator
from app.database.repositories.table_eda import TableEDARepository
from app.utils import database as db_utils

logger = get_logger(__name__)


class EDAService:
    """Service for generating and managing table EDA."""

    def __init__(self, db: Session):
        """Initialize EDA service."""
        self.db = db
        self.eda_repo = TableEDARepository()
        self.eda_generator = EDAGenerator()

    def _log_prefix(self, table_name: Optional[str] = None) -> str:
        """Generate log prefix."""
        return f"[EDAService] | [table={table_name or 'None'}]"

    def compute_column_stats(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Compute column-level statistics from a DataFrame.
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            Dict mapping column names to their statistics
        """
        stats = {}
        
        for col_name in df.columns:
            col_stats = {
                "non_null_count": int(df[col_name].notna().sum()),
                "null_count": int(df[col_name].isna().sum()),
                "dtype": str(df[col_name].dtype)
            }
            
            # Get non-null values
            non_null = df[col_name].dropna()
            
            if len(non_null) == 0:
                stats[col_name] = col_stats
                continue
            
            # Numeric columns
            if pd.api.types.is_numeric_dtype(df[col_name]):
                col_stats["min"] = float(non_null.min())
                col_stats["max"] = float(non_null.max())
                col_stats["mean"] = float(non_null.mean())
                col_stats["median"] = float(non_null.median())
                col_stats["distinct_count"] = int(non_null.nunique())
            
            # String columns
            elif pd.api.types.is_string_dtype(df[col_name]) or df[col_name].dtype == 'object':
                try:
                    col_stats["distinct_count"] = int(non_null.nunique())
                    # Get top 10 most common values
                    top_values = non_null.value_counts().head(10).to_dict()
                    col_stats["top_values"] = {str(k): int(v) for k, v in top_values.items()}
                    # Sample values (first 5 unique)
                    col_stats["sample_values"] = [str(v) for v in non_null.unique()[:5]]
                except (TypeError, ValueError):
                    # Handle unhashable types (e.g., JSON/dict columns)
                    col_stats["data_type"] = "JSON"
                    col_stats["sample_values"] = [str(v)[:100] for v in non_null.head(3)]
            
            # Boolean columns
            elif pd.api.types.is_bool_dtype(df[col_name]):
                col_stats["true_count"] = int((non_null == True).sum())
                col_stats["false_count"] = int((non_null == False).sum())
            
            # Datetime columns
            elif pd.api.types.is_datetime64_any_dtype(df[col_name]):
                col_stats["min"] = str(non_null.min())
                col_stats["max"] = str(non_null.max())
                col_stats["distinct_count"] = int(non_null.nunique())
            
            stats[col_name] = col_stats
        
        return stats

    async def generate_llm_insights(
        self,
        table_name: str,
        column_stats: Dict[str, Dict[str, Any]],
        row_count: int,
        model: OpenAIChat
    ):
        """
        Use LLM to generate summary and field metadata from column statistics.
        
        Args:
            table_name: Name of the table
            column_stats: Column statistics
            row_count: Total row count
            model: LLM model
            
        Returns:
            TableEDAResponse with summary and field metadata
        """
        return await self.eda_generator.generate_table_eda(
            table_name=table_name,
            column_stats=column_stats,
            row_count=row_count,
            model=model
        )

    async def generate_eda_for_table(
        self,
        table_name: str,
        model: OpenAIChat,
        sample_size: int = 10000
    ) -> Dict[str, Any]:
        """
        Generate complete EDA for a table.
        
        Args:
            table_name: Name of the table
            model: LLM model for generating insights
            sample_size: Number of rows to sample for analysis
            
        Returns:
            Dict with EDA results
        """
        logger.info(f"{self._log_prefix(table_name)} | Starting EDA generation")
        
        try:
            # Read table sample
            df = db_utils.read_table_sample(self.db, table_name, limit=sample_size)
            
            if df is None or df.empty:
                logger.warning(f"{self._log_prefix(table_name)} | Table is empty or doesn't exist")
                return {"success": False, "error": "Table is empty or doesn't exist"}
            
            row_count = db_utils.get_table_row_count(self.db, table_name)
            logger.info(f"{self._log_prefix(table_name)} | Loaded {len(df)} rows (total: {row_count})")
            
            # Compute column statistics
            column_stats = self.compute_column_stats(df)
            logger.info(f"{self._log_prefix(table_name)} | Computed stats for {len(column_stats)} columns")
            
            # Generate LLM insights
            llm_response = await self.generate_llm_insights(
                table_name, column_stats, row_count, model
            )
            
            # Convert field metadata to dict for storage
            field_metadata_dict = [fm.model_dump() for fm in llm_response.field_metadata]
            
            # Save to database
            eda = self.eda_repo.upsert(
                db=self.db,
                table_name=table_name,
                row_count=row_count,
                column_stats=column_stats,
                summary=llm_response.summary,
                insights=field_metadata_dict  # Store field metadata in insights column
            )
            
            logger.info(f"{self._log_prefix(table_name)} | EDA saved successfully")
            
            return {
                "success": True,
                "table_name": table_name,
                "row_count": row_count,
                "column_count": len(column_stats),
                "summary": llm_response.summary,
                "field_metadata": field_metadata_dict
            }
            
        except Exception as e:
            logger.error(f"{self._log_prefix(table_name)} | EDA generation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def refresh_eda_for_all_tables(
        self,
        model: OpenAIChat,
        table_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Refresh EDA for multiple tables.
        
        Args:
            model: LLM model
            table_names: Optional list of table names (if None, refreshes all)
            
        Returns:
            Dict with results
        """
        if table_names is None:
            # Get all table names from database
            from sqlalchemy import inspect
            inspector = inspect(self.db.bind)
            table_names = inspector.get_table_names()
            # Filter out system tables
            table_names = [t for t in table_names if not t.startswith('alembic_')]
        
        logger.info(f"{self._log_prefix()} | Refreshing EDA for {len(table_names)} tables")
        
        results = []
        for table_name in table_names:
            result = await self.generate_eda_for_table(table_name, model)
            results.append(result)
        
        success_count = sum(1 for r in results if r.get("success"))
        
        return {
            "success": True,
            "total_tables": len(table_names),
            "success_count": success_count,
            "failed_count": len(table_names) - success_count,
            "results": results
        }

    def get_eda(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Get EDA for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dict with EDA data or None
        """
        eda = self.eda_repo.get_by_table_name(self.db, table_name)
        if not eda:
            return None
        
        return {
            "table_name": eda.table_name,
            "row_count": eda.row_count,
            "column_stats": eda.column_stats,
            "summary": eda.summary,
            "insights": eda.insights,
            "updated_at": eda.updated_at.isoformat()
        }
