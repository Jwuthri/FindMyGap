"""
Find My Gaps - Agent Systems

This module contains:
- teams.py: Team-based architecture with coordinator delegation
- product_gap_workflow.py: Workflow-based architecture with conditional execution
"""

# Import workflow (doesn't depend on teams.py)
from app.agents.product_gap_workflow import create_product_gap_workflow

# Try to import teams (may fail if guardrails not available)
try:
    from app.agents.teams import create_findmygaps_team
    __all__ = [
        'create_findmygaps_team',
        'create_product_gap_workflow',
    ]
except ImportError as e:
    # Guardrails module may not be available in current agno version
    __all__ = [
        'create_product_gap_workflow',
    ]


