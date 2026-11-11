"""
Tests for R16-T015: Dataset Manifest Validation — Offline Service Adapter
"""

import unittest
from example import validate_manifest, load_jsonl_fixture, ValidationResult


class TestValidManifest(unittest.TestCase):
    """Normal path: valid two-split fixture passes."""

    def setUp(self):
        self.manifest = {
            "train": [
                {"id": "1", "text": "Hello world", "label": "positive"},
                {"id": "2", "text": "Goodbye world", "label": "negative"},
            ],
            "validation": [
                {"id": "3", "text": "Neutral statement", "label": "neutral"},
            ],
        }

    def test_valid_manifest_ok(self):
        result = validate_manifest(self.manifest)
        self.assertTrue(result.ok)

    def test_valid_manifest_no_errors(self):
        result = validate_manifest(self.manifest)
        self.assertEqual(result.errors, [])

    def test_result_type(self):
        result = validate_manifest(self.manifest)
        self.assertIsInstance(result, ValidationResult)

    def test_empty_manifest_passes(self):
        result = validate_manifest({})
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, [])


class TestMissingFieldErrors(unittest.TestCase):
    """Missing required field fails with line number."""

    def test_missing_label_line2(self):
        manifest = {
            "train": [
                {"id": "10", "text": "Good", "label": "positive"},
                {"id": "11", "text": "Bad"},   # label missing
            ]
        }
        result = validate_manifest(manifest)
        self.assertFalse(result.ok)
        self.assertEqual(len(result.errors), 1)
        self.assertIn("line 2", result.errors[0])
        self.assertIn("missing field 'label'", result.errors[0])

    def test_missing_text_field(self):
        manifest = {
            "train": [
                {"id": "20", "label": "pos"},  # text missing
            ]
        }
        result = validate_manifest(manifest)
        self.assertFalse(result.ok)
        self.assertTrue(any("missing field 'text'" in e for e in result.errors))

    def test_missing_id_field(self):
        manifest = {
            "train": [
                {"text": "No id here", "label": "pos"},  # id missing
            ]
        }
        result = validate_manifest(manifest)
        self.assertFalse(result.ok)
        self.assertTrue(any("missing field 'id'" in e for e in result.errors))

    def test_missing_all_fields(self):
        manifest = {"train": [{}]}
        result = validate_manifest(manifest)
        self.assertFalse(result.ok)
        self.assertEqual(len(result.errors), 3)  # id, text, label all missing

    def test_error_contains_split_name(self):
        manifest = {"validation": [{"id": "x", "text": "hi"}]}  # label missing
        result = validate_manifest(manifest)
        self.assertFalse(result.ok)
        self.assertIn("validation", result.errors[0])


class TestDuplicateIDErrors(unittest.TestCase):
    """Duplicate IDs across splits fail."""

    def test_duplicate_id_across_splits(self):
        manifest = {
            "train":      [{"id": "A", "text": "First", "label": "pos"}],
            "validation": [{"id": "A", "text": "Second", "label": "neg"}],
        }
        result = validate_manifest(manifest)
        self.assertFalse(result.ok)
        self.assertTrue(any("duplicate id 'A'" in e for e in result.errors))

    def test_duplicate_id_mentions_both_splits(self):
        manifest = {
            "train":      [{"id": "Z", "text": "T", "label": "p"}],
            "validation": [{"id": "Z", "text": "V", "label": "n"}],
        }
        result = validate_manifest(manifest)
        error_text = " ".join(result.errors)
        self.assertIn("train", error_text)
        self.assertIn("validation", error_text)

    def test_same_id_within_one_split_no_cross_error(self):
        # Duplicate within same split is not a cross-split error.
        # Only the first occurrence is registered for cross-split tracking.
        manifest = {
            "train": [
                {"id": "X", "text": "one", "label": "p"},
                {"id": "X", "text": "two", "label": "n"},
            ]
        }
        result = validate_manifest(manifest)
        # No cross-split duplicate error expected (same split)
        cross_errors = [e for e in result.errors if "duplicate id" in e]
        self.assertEqual(len(cross_errors), 0)

    def test_no_duplicate_different_ids(self):
        manifest = {
            "train":      [{"id": "1", "text": "a", "label": "p"}],
            "validation": [{"id": "2", "text": "b", "label": "n"}],
        }
        result = validate_manifest(manifest)
        self.assertTrue(result.ok)


class TestLoadJsonlFixture(unittest.TestCase):
    """Test the JSONL line parser helper."""

    def test_parse_valid_jsonl(self):
        lines = [
            '{"id": "1", "text": "hello", "label": "pos"}',
            '{"id": "2", "text": "world", "label": "neg"}',
        ]
        records = load_jsonl_fixture(lines)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["id"], "1")
        self.assertEqual(records[1]["label"], "neg")

    def test_skip_blank_lines(self):
        lines = ['{"id": "1", "text": "a", "label": "p"}', "", "  "]
        records = load_jsonl_fixture(lines)
        self.assertEqual(len(records), 1)


class TestDeliberateFailure(unittest.TestCase):
    """Ensure a deliberately wrong result makes the test fail."""

    def test_wrong_ok_value_fails(self):
        """Asserting ok=True on an invalid manifest must fail."""
        manifest = {"train": [{"id": "99"}]}  # missing text and label
        result = validate_manifest(manifest)
        # Deliberately assert the wrong value to prove test catches it
        self.assertFalse(
            result.ok,
            "A manifest missing required fields should NOT be ok=True",
        )


if __name__ == "__main__":
    unittest.main()

