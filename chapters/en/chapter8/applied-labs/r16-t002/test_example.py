"""Tests for example.py. Run from the repository root with:

    python3 -m unittest discover -s chapters/en/chapter8/applied-labs/r16-t002 -p "test_*.py"
"""

import os
import unittest
from pathlib import Path
from unittest import mock

from example import (
    FAILING_INPUT,
    FIXED_INPUT,
    MAX_POSITIONS,
    REPORT_FIELDS,
    build_report,
    embed_positions,
    render_report,
)


class BoundaryCases(unittest.TestCase):
    def test_smallest_valid_input_one_token(self):
        self.assertEqual(embed_positions([101]), ["pos0"])

    def test_exactly_max_positions_is_valid(self):
        labels = embed_positions(list(range(MAX_POSITIONS)))
        self.assertEqual(len(labels), MAX_POSITIONS)
        self.assertEqual(labels[-1], f"pos{MAX_POSITIONS - 1}")

    def test_one_over_max_positions_raises_index_error(self):
        with self.assertRaises(IndexError):
            embed_positions(list(range(MAX_POSITIONS + 1)))


class Reproduction(unittest.TestCase):
    def test_fixture_is_one_token_too_long(self):
        self.assertEqual(len(FAILING_INPUT), MAX_POSITIONS + 1)

    def test_failure_is_deterministic(self):
        messages = set()
        for _ in range(3):
            with self.assertRaises(IndexError) as ctx:
                embed_positions(FAILING_INPUT)
            messages.add(str(ctx.exception))
        self.assertEqual(messages, {"list index out of range"})

    def test_removing_trigger_makes_it_succeed(self):
        self.assertEqual(FIXED_INPUT, FAILING_INPUT[:-1])
        self.assertEqual(len(embed_positions(FIXED_INPUT)), MAX_POSITIONS)


class Report(unittest.TestCase):
    def setUp(self):
        self.report = build_report(FAILING_INPUT)

    def test_report_has_exactly_the_five_fields(self):
        self.assertEqual(tuple(self.report), REPORT_FIELDS)
        for field in REPORT_FIELDS:
            self.assertTrue(self.report[field].strip(), f"{field} is empty")

    def test_report_records_the_exception(self):
        self.assertEqual(self.report["actual"], "IndexError: list index out of range")
        self.assertIn("IndexError", self.report["traceback"])
        self.assertIn("embed_positions", self.report["traceback"])
        self.assertIn("example.py", self.report["command"])

    def test_report_contains_no_secrets_or_home_path(self):
        with mock.patch.dict(os.environ, {"HF_TOKEN": "hf_FAKE_SECRET_123"}):
            text = render_report(build_report(FAILING_INPUT))
        self.assertNotIn("hf_FAKE_SECRET_123", text)
        self.assertNotIn(str(Path.home()), text)

    def test_report_for_fixed_input_has_no_exception(self):
        report = build_report(FIXED_INPUT)
        self.assertEqual(report["actual"], f"returned {MAX_POSITIONS} position labels")
        self.assertEqual(report["traceback"], "(no exception)")


class InvalidInput(unittest.TestCase):
    def test_empty_input_is_rejected(self):
        with self.assertRaises(ValueError):
            embed_positions([])

    def test_non_int_token_is_rejected(self):
        with self.assertRaises(TypeError):
            embed_positions([101, "hello"])

    def test_non_list_is_rejected(self):
        with self.assertRaises(TypeError):
            embed_positions("101 102")


if __name__ == "__main__":
    unittest.main()
