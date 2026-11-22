"""
R16-T030: Dataset selection semantics, immutability, and scenario assessment.
"""

from .example import (
    APPLIED_QUESTIONS,
    CANONICAL_ROWS,
    DatasetSelection,
    DatasetSelectionError,
    filter_and_project,
    verify_applied_questions,
)

__all__ = [
    "APPLIED_QUESTIONS",
    "CANONICAL_ROWS",
    "DatasetSelection",
    "DatasetSelectionError",
    "filter_and_project",
    "verify_applied_questions",
]
