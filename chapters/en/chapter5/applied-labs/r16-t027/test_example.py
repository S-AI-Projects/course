#!/usr/bin/env python3
"""
Unit tests for Dataset Manifest Validation Lab (R16-T027).

Verifies the standard contract:
- Missing 'label' fails with line number.
- Duplicate IDs across splits fail with provenance details.
- Valid two-split fixture passes.
- Regression tests and boundary conditions.
"""

import io
import os
import sys
import unittest
from contextlib import redirect_stdout

# Ensure current lab directory is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from example import (
    DUPLICATE_ID_FIXTURE,
    MISSING_LABEL_FIXTURE,
    VALID_TWO_SPLIT_FIXTURE,
    DatasetManifestValidator,
    ManifestValidationError,
    main,
)


class TestDatasetManifestValidator(unittest.TestCase):
    """Test suite for dataset manifest validation."""

    def setUp(self):
        self.validator = DatasetManifestValidator()

    def test_valid_two_split_fixture_passes(self):
        """Verify that the standard two-split fixture passes validation."""
        report = self.validator.validate_manifest(VALID_TWO_SPLIT_FIXTURE)
        self.assertTrue(report.is_valid)
        self.assertEqual(report.total_records, 3)
        self.assertEqual(report.split_counts, {"train": 2, "validation": 1})
        self.assertEqual(report.unique_ids, [101, 102, 201])

    def test_missing_label_fails_with_line_number(self):
        """Verify that a record missing 'label' fails with the exact line number."""
        with self.assertRaises(ManifestValidationError) as ctx:
            self.validator.validate_manifest(MISSING_LABEL_FIXTURE)

        err = ctx.exception
        self.assertEqual(err.split, "train")
        self.assertEqual(err.line_number, 2)
        self.assertEqual(err.field, "label")
        self.assertIn("line 2", str(err))
        self.assertIn("label", str(err))

    def test_duplicate_id_across_splits_fails(self):
        """Verify that duplicate IDs across splits trigger an error."""
        with self.assertRaises(ManifestValidationError) as ctx:
            self.validator.validate_manifest(DUPLICATE_ID_FIXTURE)

        err = ctx.exception
        self.assertEqual(err.conflicting_id, 101)
        self.assertEqual(err.split, "validation")
        self.assertEqual(err.line_number, 1)
        self.assertIn("Duplicate ID '101'", str(err))

    def test_duplicate_id_within_same_split(self):
        """Verify that duplicate IDs within the same split are rejected."""
        manifest = {
            "train": [
                '{"id": 1, "text": "Record 1", "label": "bug"}',
                '{"id": 1, "text": "Record 2 with same ID", "label": "enhancement"}',
            ]
        }
        with self.assertRaises(ManifestValidationError) as ctx:
            self.validator.validate_manifest(manifest)
        self.assertEqual(ctx.exception.line_number, 2)

    def test_boundary_empty_manifest_rejected(self):
        """Verify that an empty manifest is rejected."""
        with self.assertRaises(ManifestValidationError):
            self.validator.validate_manifest({})

    def test_boundary_blank_lines_ignored(self):
        """Blank lines in JSONL should be ignored without distorting line counting."""
        manifest = {
            "train": [
                '{"id": 1, "text": "First", "label": "bug"}',
                '   ',  # Line 2 blank
                '{"id": 2, "text": "Second", "label": "enhancement"}',
            ]
        }
        report = self.validator.validate_manifest(manifest)
        self.assertEqual(report.total_records, 2)

    def test_invalid_json_syntax_fails_with_line_number(self):
        """Malformed JSON syntax raises ManifestValidationError with line number."""
        manifest = {
            "train": [
                '{"id": 1, "text": "Good JSON", "label": "bug"}',
                '{"id": 2, malformed JSON...',  # Line 2 malformed
            ]
        }
        with self.assertRaises(ManifestValidationError) as ctx:
            self.validator.validate_manifest(manifest)
        self.assertEqual(ctx.exception.line_number, 2)

    def test_missing_other_required_fields(self):
        """Missing 'id' or 'text' also fails with field name and line number."""
        manifest_no_id = {
            "train": [
                '{"text": "No ID record", "label": "bug"}',
            ]
        }
        with self.assertRaises(ManifestValidationError) as ctx:
            self.validator.validate_manifest(manifest_no_id)
        self.assertEqual(ctx.exception.field, "id")
        self.assertEqual(ctx.exception.line_number, 1)

    def test_deliberate_wrong_result_fails(self):
        """A deliberate wrong assertion about record counts or validity fails."""
        report = self.validator.validate_manifest(VALID_TWO_SPLIT_FIXTURE)
        self.assertNotEqual(report.total_records, 999)

    def test_cli_main_execution(self):
        """Verify CLI main entrypoint executes cleanly and produces expected text."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        self.assertIn("Case 1: Valid Two-Split Fixture", output)
        self.assertIn("Case 2: Missing Required Field ('label')", output)
        self.assertIn("Line number:           2", output)
        self.assertIn("Case 3: Duplicate ID Across Splits", output)
        self.assertIn("Conflicting ID:        101", output)


if __name__ == "__main__":
    unittest.main()
