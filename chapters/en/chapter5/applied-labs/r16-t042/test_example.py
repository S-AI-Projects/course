"""Unit tests for Applied Lab R16-T042: Streaming Aggregation."""

import os
import sys
import unittest

LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    MalformedLineError,
    StreamAggregationResult,
    count_categories_from_stream,
    stream_aggregate_jsonl,
)


class TestStreamingAggregation(unittest.TestCase):
    """Test suite validating streaming aggregation contract and boundary cases."""

    def test_standard_stream_a_b_a_c(self):
        """Input records A, B, A, C give category counts A:2, B:1, C:1 without errors."""
        stream = [
            '{"category": "A"}',
            '{"category": "B"}',
            '{"category": "A"}',
            '{"category": "C"}',
        ]
        result = stream_aggregate_jsonl(stream)
        self.assertEqual(result.category_counts, {"A": 2, "B": 1, "C": 1})
        self.assertEqual(result.malformed_records, [])
        self.assertEqual(result.total_lines_processed, 4)
        self.assertEqual(result.valid_records_count, 4)

        # Also verify convenience function
        counts = count_categories_from_stream(stream)
        self.assertEqual(counts, {"A": 2, "B": 1, "C": 1})

    def test_empty_stream_gives_empty_dict(self):
        """Empty input stream gives empty counts {} and no errors."""
        result = stream_aggregate_jsonl([])
        self.assertEqual(result.category_counts, {})
        self.assertEqual(result.malformed_records, [])
        self.assertEqual(result.total_lines_processed, 0)
        self.assertEqual(result.valid_records_count, 0)

    def test_whitespace_and_blank_lines_skipped(self):
        """Blank or whitespace-only lines are ignored and do not produce errors."""
        stream = [
            "",
            "   ",
            '{"category": "A"}',
            "\n\t  ",
            '{"category": "B"}',
            "",
        ]
        result = stream_aggregate_jsonl(stream)
        self.assertEqual(result.category_counts, {"A": 1, "B": 1})
        self.assertEqual(result.malformed_records, [])

    def test_smallest_valid_input(self):
        """Single line valid record gives single category count."""
        stream = ['{"category": "X"}']
        result = stream_aggregate_jsonl(stream)
        self.assertEqual(result.category_counts, {"X": 1})
        self.assertEqual(result.malformed_records, [])
        self.assertEqual(result.total_lines_processed, 1)

    def test_malformed_json_syntax_reported_with_line_number(self):
        """Malformed JSON syntax is caught and reported with exact line number."""
        stream = [
            '{"category": "A"}',
            '{this is bad json}',
            '{"category": "B"}',
        ]
        result = stream_aggregate_jsonl(stream)
        self.assertEqual(result.category_counts, {"A": 1, "B": 1})
        self.assertEqual(len(result.malformed_records), 1)
        err = result.malformed_records[0]
        self.assertEqual(err.line_number, 2)
        self.assertEqual(err.raw_content, "{this is bad json}")
        self.assertIn("Invalid JSON", err.error_message)

    def test_missing_category_field_reported_with_line_number(self):
        """JSON missing the required category field is reported with line number."""
        stream = [
            '{"wrong_key": "val"}',
            '{"category": "A"}',
        ]
        result = stream_aggregate_jsonl(stream)
        self.assertEqual(result.category_counts, {"A": 1})
        self.assertEqual(len(result.malformed_records), 1)
        self.assertEqual(result.malformed_records[0].line_number, 1)
        self.assertIn("Missing required field", result.malformed_records[0].error_message)

    def test_non_dict_json_reported_with_line_number(self):
        """JSON primitive or list is reported with line number."""
        stream = [
            '"just a string"',
            '12345',
            '["a", "b"]',
            '{"category": "Z"}',
        ]
        result = stream_aggregate_jsonl(stream)
        self.assertEqual(result.category_counts, {"Z": 1})
        self.assertEqual(len(result.malformed_records), 3)
        self.assertEqual(result.malformed_records[0].line_number, 1)
        self.assertEqual(result.malformed_records[1].line_number, 2)
        self.assertEqual(result.malformed_records[2].line_number, 3)

    def test_generator_input_demonstrating_streaming_nature(self):
        """Verify stream is processed as a generator without loading entire sequence at once."""
        def record_generator():
            yield '{"category": "A"}'
            yield '{"category": "B"}'
            yield '{"category": "A"}'
            yield '{"category": "C"}'

        result = stream_aggregate_jsonl(record_generator())
        self.assertEqual(result.category_counts, {"A": 2, "B": 1, "C": 1})

    def test_deliberate_wrong_result_fails(self):
        """Deliberate wrong expectation triggers an assertion failure."""
        stream = ['{"category": "A"}', '{"category": "B"}']
        result = stream_aggregate_jsonl(stream)
        wrong_expected = {"A": 99, "B": 99}
        with self.assertRaises(AssertionError):
            self.assertEqual(result.category_counts, wrong_expected)


if __name__ == "__main__":
    unittest.main()
