"""
Unit and contract tests for dataset selection semantics, immutability, and scenario assessment.

Validates:
  1. Rows (id1,score2),(id2,score5),(id3,score5), filtered score>=5 and projected id, yield id2,id3 in order.
  2. Source collection immutability.
  3. Execution and correctness of the 3 scenario assessment questions:
     - Predict an output (Q1)
     - Diagnose a failure (Q2)
     - Choose a boundary policy (Q3)
  4. Deliberate failure triggers assertion error.
"""

from __future__ import annotations

import copy
import unittest

try:
    from .example import (
        APPLIED_QUESTIONS,
        CANONICAL_ROWS,
        DatasetSelection,
        DatasetSelectionError,
        check_question_1_predict_output,
        check_question_2_diagnose_failure,
        check_question_3_boundary_policy,
        filter_and_project,
        verify_applied_questions,
    )
except ImportError:
    from example import (
        APPLIED_QUESTIONS,
        CANONICAL_ROWS,
        DatasetSelection,
        DatasetSelectionError,
        check_question_1_predict_output,
        check_question_2_diagnose_failure,
        check_question_3_boundary_policy,
        filter_and_project,
        verify_applied_questions,
    )


class TestDatasetSelection(unittest.TestCase):
    """Test suite verifying functional dataset selection, immutability, and scenario questions."""

    def test_canonical_filter_and_project(self) -> None:
        """Verify (id1,score2),(id2,score5),(id3,score5) with score>=5 yields ['id2', 'id3'] in order."""
        rows = copy.deepcopy(CANONICAL_ROWS)
        projected_ids, projected_records = filter_and_project(
            rows,
            predicate=lambda r: r["score"] >= 5,
            column="id",
        )
        self.assertEqual(projected_ids, ["id2", "id3"])
        self.assertEqual(projected_records, [{"id": "id2"}, {"id": "id3"}])

    def test_source_collection_immutability(self) -> None:
        """Verify filtering and projection never mutate the input sequence or nested dicts."""
        original_rows = copy.deepcopy(CANONICAL_ROWS)
        snapshot = copy.deepcopy(CANONICAL_ROWS)

        table = DatasetSelection(original_rows)
        _ = table.filter(lambda r: r["score"] >= 5)
        _ = table.select(["id"])
        _ = filter_and_project(original_rows, lambda r: r["score"] >= 5, "id")

        self.assertEqual(original_rows, snapshot, "Source rows list should remain completely unchanged")
        self.assertEqual(table.to_list(), snapshot, "Table records should remain completely unchanged")

    def test_empty_dataset_handling(self) -> None:
        """Verify empty dataset yields empty result without error."""
        table = DatasetSelection([])
        filtered = table.filter(lambda r: True)
        self.assertEqual(len(filtered), 0)
        self.assertEqual(filtered.to_list(), [])

    def test_no_matches_predicate(self) -> None:
        """Verify predicate matching no records yields empty list in order."""
        ids, recs = filter_and_project(CANONICAL_ROWS, lambda r: r["score"] > 10, "id")
        self.assertEqual(ids, [])
        self.assertEqual(recs, [])

    def test_all_matches_predicate(self) -> None:
        """Verify predicate matching all records preserves complete sequence order."""
        ids, _ = filter_and_project(CANONICAL_ROWS, lambda r: r["score"] >= 0, "id")
        self.assertEqual(ids, ["id1", "id2", "id3"])

    def test_missing_column_projection_raises_keyerror(self) -> None:
        """Verify projecting a non-existent column raises KeyError."""
        table = DatasetSelection(CANONICAL_ROWS)
        with self.assertRaises(KeyError) as ctx:
            table.select(["non_existent_col"])
        self.assertIn("non_existent_col", str(ctx.exception))

    def test_strict_filter_missing_key_raises_error(self) -> None:
        """Verify missing predicate keys in strict mode raise DatasetSelectionError with diagnostics."""
        rows = [
            {"id": "id1", "score": 2},
            {"id": "id2"},  # Missing 'score'
        ]
        table = DatasetSelection(rows)
        with self.assertRaises(DatasetSelectionError) as ctx:
            table.filter(lambda r: r["score"] >= 5, strict=True)
        self.assertEqual(ctx.exception.record_index, 1)

    def test_lenient_filter_excludes_failing_rows(self) -> None:
        """Verify strict=False safely excludes rows causing exceptions."""
        rows = [
            {"id": "id1", "score": 2},
            {"id": "id2"},  # Missing 'score' -> excluded
            {"id": "id3", "score": 7},  # Valid -> included
        ]
        table = DatasetSelection(rows)
        filtered = table.filter(lambda r: r["score"] >= 5, strict=False)
        self.assertEqual(filtered.project_column("id"), ["id3"])

    def test_scenario_assessment_questions(self) -> None:
        """Verify all 3 scenario assessment questions execute and pass their checks."""
        self.assertTrue(check_question_1_predict_output(), "Q1 (Predict output) check failed")
        self.assertTrue(check_question_2_diagnose_failure(), "Q2 (Diagnose failure) check failed")
        self.assertTrue(check_question_3_boundary_policy(), "Q3 (Boundary policy) check failed")

        verified = verify_applied_questions()
        self.assertEqual(len(verified), 3)
        for q in verified:
            self.assertTrue(q["verified"], f"Question {q['id']} verification failed")

    def test_deliberate_wrong_result_fails(self) -> None:
        """Verify that deliberate incorrect assertions fail as required by test contract."""
        rows = copy.deepcopy(CANONICAL_ROWS)
        ids, _ = filter_and_project(rows, lambda r: r["score"] >= 5, "id")

        with self.assertRaises(AssertionError):
            self.assertEqual(ids, ["id1"])

        with self.assertRaises(AssertionError):
            self.assertEqual(ids, ["id3", "id2"])  # Wrong order


if __name__ == "__main__":
    unittest.main()
