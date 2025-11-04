"""
Table EDA model - stores exploratory data analysis for tables.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, JSON

from ..base import Base


class TableEDATable(Base):
    """Stores EDA (Exploratory Data Analysis) for database tables."""
    __tablename__ = "table_eda"

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(255), unique=True, nullable=False, index=True)
    row_count = Column(Integer, nullable=False)
    
    # Column-level statistics (JSON)
    column_stats = Column(JSON, nullable=False)
    # Example: {
    #   "rating": {"min": 1, "max": 5, "distinct_count": 5, "null_count": 0},
    #   "company_name": {"distinct_count": 4, "sample_values": ["Spotify", "Netflix"]}
    # }
    
    # LLM-generated summary
    summary = Column(Text, nullable=True)
    # Example: "This table contains 150 reviews across 4 companies. 
    #           Ratings range from 1-5 with an average of 3.2..."
    
    # Key insights from LLM
    insights = Column(JSON, nullable=True)
    # Example: ["Most reviews are for Spotify (45%)", "Rating distribution is skewed negative"]
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<TableEDA(table_name={self.table_name}, row_count={self.row_count})>"
