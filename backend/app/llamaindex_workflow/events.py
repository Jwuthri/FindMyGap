"""
Event definitions for LlamaIndex workflow.

Events are used to pass data between workflow steps.
"""

from typing import Any, Dict, List, Optional
from llama_index.core.workflow import Event


class QueryAnalysisEvent(Event):
    """Trigger event for query analysis step."""
    pass


class FormatDetectionEvent(Event):
    """Trigger event for format detection step."""
    pass


class RetrievalPlanEvent(Event):
    """Trigger event for retrieval planning step."""
    pass


class DataRetrievalEvent(Event):
    """Trigger event for data retrieval step."""
    pass


class NLPAnalysisEvent(Event):
    """Trigger event for NLP analysis step."""
    pass


class WriterContextEvent(Event):
    """Trigger event for answer generation step."""
    pass
