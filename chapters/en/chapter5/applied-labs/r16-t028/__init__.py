"""
R16-T028: Streaming aggregation with bounded state, failure reporting, and error recovery.
"""

from .example import (
    AggregationResult,
    StreamingCategoryAggregator,
    StreamingErrorRecord,
    StreamingRecordError,
)

__all__ = [
    "AggregationResult",
    "StreamingCategoryAggregator",
    "StreamingErrorRecord",
    "StreamingRecordError",
]
