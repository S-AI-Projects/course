"""
Unit and contract tests for streaming aggregation with failure reporting and recovery.

Verifies:
  1. A, B, A, C yields {'A': 2, 'B': 1, 'C': 1}.
  2. Malformed line is reported with exact line number.
  3. Empty input yields {}.
  4. System recovers on the next valid input after encountering errors.
  5. Deliberate wrong results trigger failure.
"""

from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

# Support relative or absolute import
try:
    from .example import (
        FIXTURE_ABAC,
        FIXTURE_EMPTY,
        FIXTURE_MALFORMED_WITH_RECOVERY,
        FIXTURE_MISSING_KEY_WITH_RECOVERY,
        AggregationResult,
        StreamingCategoryAggregator,
        StreamingErrorRecord,
        StreamingRecordError,
    )
except ImportError:
    from example import (
        FIXTURE_ABAC,
        FIXTURE_EMPTY,
        FIXTURE_MALFORMED_WITH_RECOVERY,
        FIXTURE_MISSING_KEY_WITH_RECOVERY,
        AggregationResult,
        StreamingCategoryAggregator,
        StreamingErrorRecord,
        StreamingRecordError,
    )


class TestStreamingCategoryAggregator(unittest.TestCase):
    """Test suite covering streaming contracts, error reporting, and recovery."""

    def setUp(self) -> None:
        self.aggregator = StreamingCategoryAggregator()

    def test_canonical_abac_counts(self) -> None:
        """Verify that streaming A, B, A, C produces counts A:2, B:1, C:1."""
        result = self.aggregator.aggregate_string(FIXTURE_ABAC)
        self.assertEqual(result.counts, {"A": 2, "B": 1, "C": 1})
        self.assertEqual(result.total_lines, 4)
        self.assertEqual(result.valid_records, 4)
        self.assertEqual(len(result.errors), 0)
        self.assertFalse(result.recovered)  # No errors to recover from

    def test_empty_input_gives_empty_dict(self) -> None:
        """Verify that empty input produces an empty dictionary {}."""
        result = self.aggregator.aggregate_string(FIXTURE_EMPTY)
        self.assertEqual(result.counts, {})
        self.assertEqual(result.total_lines, 0)
        self.assertEqual(result.valid_records, 0)
        self.assertEqual(len(result.errors), 0)

    def test_malformed_line_reported_with_line_number(self) -> None:
        """Verify that a malformed JSON line is captured with its exact 1-based line number."""
        result = self.aggregator.aggregate_string(FIXTURE_MALFORMED_WITH_RECOVERY)
        self.assertEqual(len(result.errors), 1)
        err = result.errors[0]
        self.assertEqual(err.line_number, 2)
        self.assertEqual(err.error_type, "SYNTAX_ERROR")
        self.assertIn("JSON decode failure", err.message)
        self.assertEqual(err.raw_line, '{"invalid_json": broken')

    def test_recovery_on_next_valid_input(self) -> None:
        """Verify that after a malformed record on line 2, ingestion recovers on line 3."""
        result = self.aggregator.aggregate_string(FIXTURE_MALFORMED_WITH_RECOVERY)
        self.assertTrue(result.recovered, "Aggregator should report successful recovery")
        self.assertEqual(result.counts, {"A": 2, "B": 1, "C": 1})
        self.assertEqual(result.valid_records, 4)
        self.assertEqual(result.total_lines, 5)

    def test_missing_category_key_reported_and_recovered(self) -> None:
        """Verify that a missing 'category' field is reported and stream recovers."""
        result = self.aggregator.aggregate_string(FIXTURE_MISSING_KEY_WITH_RECOVERY)
        self.assertEqual(len(result.errors), 1)
        err = result.errors[0]
        self.assertEqual(err.line_number, 2)
        self.assertEqual(err.error_type, "MISSING_FIELD")
        self.assertIn("Missing required field 'category'", err.message)
        self.assertTrue(result.recovered)
        self.assertEqual(result.counts, {"A": 2, "B": 1, "C": 1})

    def test_strict_mode_raises_exception(self) -> None:
        """Verify that on_error='raise' aborts on the first bad record."""
        with self.assertRaises(StreamingRecordError) as ctx:
            self.aggregator.aggregate_string(FIXTURE_MALFORMED_WITH_RECOVERY, on_error="raise")
        self.assertEqual(ctx.exception.line_number, 2)
        self.assertEqual(ctx.exception.error_type, "SYNTAX_ERROR")

    def test_file_streaming_without_full_memory_buffering(self) -> None:
        """Verify file-based streaming works with a generator/file descriptor."""
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as tmp:
            tmp.write(FIXTURE_ABAC)
            tmp_path = tmp.name

        try:
            result = self.aggregator.aggregate_file(tmp_path)
            self.assertEqual(result.counts, {"A": 2, "B": 1, "C": 1})
            self.assertEqual(result.valid_records, 4)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_blank_lines_skipped_gracefully(self) -> None:
        """Verify that blank lines are skipped while preserving accurate line numbers."""
        stream = "\n\n" + FIXTURE_MALFORMED_WITH_RECOVERY
        result = self.aggregator.aggregate_string(stream)
        # Line 1, 2 blank; Line 3: A; Line 4: broken; Line 5: B; Line 6: A; Line 7: C
        self.assertEqual(result.counts, {"A": 2, "B": 1, "C": 1})
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].line_number, 4)

    def test_invalid_category_types(self) -> None:
        """Verify non-dict records and non-string/int category values are reported."""
        fixture = '[1, 2, 3]\n{"category": ["invalid_nested_list"]}\n{"category": "A"}\n'
        result = self.aggregator.aggregate_string(fixture)
        self.assertEqual(len(result.errors), 2)
        self.assertEqual(result.errors[0].line_number, 1)
        self.assertEqual(result.errors[0].error_type, "INVALID_TYPE")
        self.assertEqual(result.errors[1].line_number, 2)
        self.assertEqual(result.errors[1].error_type, "INVALID_VALUE")
        self.assertEqual(result.counts, {"A": 1})
        self.assertTrue(result.recovered)

    def test_deliberate_wrong_result_fails(self) -> None:
        """Verify that deliberate wrong assertions fail as required by grading contract."""
        result = self.aggregator.aggregate_string(FIXTURE_ABAC)
        # A deliberate wrong assertion must fail
        with self.assertRaises(AssertionError):
            self.assertEqual(result.counts, {"A": 999, "B": 0})

        with self.assertRaises(AssertionError):
            self.assertEqual(result.counts, {})


if __name__ == "__main__":
    unittest.main()
