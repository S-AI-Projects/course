#!/usr/bin/env python3
"""
Applied Lab R16-T027: Dataset Manifest Validation Worked Example with Checks.

This module illustrates schema enforcement, stable ID uniqueness, and split
provenance for local JSONL datasets, connecting to Chapter 5 Section 5
("Creating your own dataset") of the Hugging Face course.

Contract:
- Local JSONL dataset with required schema fields: 'id', 'text', 'label'.
- Train/Validation split manifest validation:
  1. A missing 'label' field fails with the exact line number.
  2. Duplicate IDs across splits (e.g., ID appearing in both train and validation)
     fail with a provenance conflict error.
  3. A valid two-split fixture passes with a verified record count report.
- Standard Library only: No external dependencies, models, or cloud calls required.
"""

from dataclasses import dataclass
import json
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple, Union
import sys


class ManifestValidationError(Exception):
    """Raised when a dataset manifest or JSONL split violates validation rules."""

    def __init__(
        self,
        message: str,
        split: Optional[str] = None,
        line_number: Optional[int] = None,
        field: Optional[str] = None,
        conflicting_id: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.split = split
        self.line_number = line_number
        self.field = field
        self.conflicting_id = conflicting_id


@dataclass(frozen=True)
class ValidationReport:
    """Detailed summary of manifest validation."""

    is_valid: bool
    total_records: int
    split_counts: Dict[str, int]
    unique_ids: List[Any]
    message: str


# ==============================================================================
# Standard Fixtures
# ==============================================================================
# 1. Valid Two-Split Fixture (Train + Validation)
VALID_TWO_SPLIT_FIXTURE = {
    "train": [
        '{"id": 101, "text": "Issue with dataset download timeout", "label": "bug"}',
        '{"id": 102, "text": "Feature request: add WebDataset loader", "label": "enhancement"}',
    ],
    "validation": [
        '{"id": 201, "text": "Clarify map batched=True documentation", "label": "documentation"}',
    ],
}

# 2. Missing-Label Fixture (Line 2 in train lacks 'label')
MISSING_LABEL_FIXTURE = {
    "train": [
        '{"id": 101, "text": "First issue record", "label": "bug"}',
        '{"id": 102, "text": "Second issue record without label"}',
    ],
    "validation": [
        '{"id": 201, "text": "Third issue record", "label": "documentation"}',
    ],
}

# 3. Duplicate-ID Fixture (ID 101 appears in both train and validation)
DUPLICATE_ID_FIXTURE = {
    "train": [
        '{"id": 101, "text": "First issue in train", "label": "bug"}',
        '{"id": 102, "text": "Second issue in train", "label": "enhancement"}',
    ],
    "validation": [
        '{"id": 101, "text": "Duplicate issue ID 101 in validation", "label": "bug"}',
    ],
}


# ==============================================================================
# Dataset Manifest Validator
# ==============================================================================
class DatasetManifestValidator:
    """
    Validates local JSONL datasets and split manifests against schema requirements,
    ensuring ID uniqueness across splits and field completeness.
    """

    DEFAULT_REQUIRED_FIELDS: Tuple[str, ...] = ("id", "text", "label")

    def __init__(self, required_fields: Sequence[str] = DEFAULT_REQUIRED_FIELDS) -> None:
        self.required_fields: Tuple[str, ...] = tuple(required_fields)

    def validate_split(
        self,
        split_name: str,
        lines: Iterable[str],
        id_provenance: Dict[Any, Tuple[str, int]],
    ) -> List[Dict[str, Any]]:
        """
        Validate a single JSONL split line by line.

        Args:
            split_name: Name of the split (e.g. 'train', 'validation').
            lines: Iterable of JSON strings (one per line).
            id_provenance: Registry mapping seen record IDs to (split_name, line_number).

        Returns:
            List of parsed record dictionaries.

        Raises:
            ManifestValidationError: On missing required fields, invalid JSON, or duplicate IDs.
        """
        records: List[Dict[str, Any]] = []

        for line_idx, line in enumerate(lines, start=1):
            raw = line.strip()
            if not raw:
                continue

            try:
                record = json.loads(raw)
            except json.JSONDecodeError as err:
                raise ManifestValidationError(
                    f"Invalid JSON in split '{split_name}' at line {line_idx}: {err}",
                    split=split_name,
                    line_number=line_idx,
                ) from err

            if not isinstance(record, dict):
                raise ManifestValidationError(
                    f"Line {line_idx} in split '{split_name}' is not a JSON object",
                    split=split_name,
                    line_number=line_idx,
                )

            # Check required fields
            for field in self.required_fields:
                if field not in record or record[field] is None:
                    raise ManifestValidationError(
                        f"Missing required field '{field}' in split '{split_name}' at line {line_idx}",
                        split=split_name,
                        line_number=line_idx,
                        field=field,
                    )

            rec_id = record["id"]

            # Check duplicate IDs across splits
            if rec_id in id_provenance:
                first_split, first_line = id_provenance[rec_id]
                raise ManifestValidationError(
                    f"Duplicate ID '{rec_id}' detected across splits: "
                    f"first defined in '{first_split}' at line {first_line}, "
                    f"duplicated in '{split_name}' at line {line_idx}",
                    split=split_name,
                    line_number=line_idx,
                    conflicting_id=rec_id,
                )

            id_provenance[rec_id] = (split_name, line_idx)
            records.append(record)

        return records

    def validate_manifest(
        self,
        manifest: Dict[str, Iterable[str]],
    ) -> ValidationReport:
        """
        Validate an entire dataset manifest across all splits.

        Args:
            manifest: Mapping from split name to iterable of JSONL lines.

        Returns:
            ValidationReport summarizing verification metrics.
        """
        if not manifest:
            raise ManifestValidationError("Dataset manifest is empty: must contain at least one split")

        id_provenance: Dict[Any, Tuple[str, int]] = {}
        split_counts: Dict[str, int] = {}
        total_records = 0

        for split_name, lines in manifest.items():
            records = self.validate_split(split_name, lines, id_provenance)
            count = len(records)
            split_counts[split_name] = count
            total_records += count

        return ValidationReport(
            is_valid=True,
            total_records=total_records,
            split_counts=split_counts,
            unique_ids=list(id_provenance.keys()),
            message=f"Manifest passed validation: {total_records} records verified across {len(split_counts)} splits.",
        )


def main() -> int:
    """Execute worked example explaining valid, missing-field, and duplicate-ID cases."""
    print("=== Dataset Manifest Validation: Worked Example with Checks ===")
    validator = DatasetManifestValidator()

    # Case 1: Valid Two-Split Fixture
    print("\n[Case 1: Valid Two-Split Fixture]")
    report = validator.validate_manifest(VALID_TWO_SPLIT_FIXTURE)
    print(f"  Status:         {'VALID' if report.is_valid else 'INVALID'}")
    print(f"  Total records:  {report.total_records}")
    print(f"  Split counts:   {report.split_counts}")
    print(f"  Verified IDs:   {report.unique_ids}")
    print(f"  Outcome:        {report.message}")

    # Case 2: Missing Label Scenario
    print("\n[Case 2: Missing Required Field ('label')]")
    try:
        validator.validate_manifest(MISSING_LABEL_FIXTURE)
        print("  ERROR: Missing label fixture was unexpectedly accepted!")
        return 1
    except ManifestValidationError as err:
        print(f"  Caught expected error: {err}")
        print(f"  Failed split:          {err.split}")
        print(f"  Line number:           {err.line_number}")
        print(f"  Missing field:         {err.field}")

    # Case 3: Duplicate ID Across Splits Scenario
    print("\n[Case 3: Duplicate ID Across Splits]")
    try:
        validator.validate_manifest(DUPLICATE_ID_FIXTURE)
        print("  ERROR: Duplicate ID fixture was unexpectedly accepted!")
        return 1
    except ManifestValidationError as err:
        print(f"  Caught expected error: {err}")
        print(f"  Conflicting ID:        {err.conflicting_id}")
        print(f"  Duplicated in split:   {err.split} at line {err.line_number}")

    print("\nAll worked validation scenarios behaved exactly according to specification.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
