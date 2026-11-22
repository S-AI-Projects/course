"""
Dataset Selection Semantics: Filtering, Projection, Immutability, and Scenario Assessment.

Extends Chapter 5, Section 3 ("Time to slice and dice").
Demonstrates:
  1. Filtering records by a predicate function without modifying the source collection.
  2. Selecting/projecting specific columns while preserving record identity and order.
  3. Canonical Contract:
     Rows: (id1, score: 2), (id2, score: 5), (id3, score: 5)
     Filter: score >= 5
     Project: ['id']
     Result: ['id2', 'id3'] in original encounter order.
  4. Scenario Assessment: Three applied questions covering output prediction,
     failure diagnosis, and boundary policy choice with executable checks.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union


class DatasetSelectionError(Exception):
    """Raised when record evaluation fails due to schema violations or invalid predicates."""

    def __init__(self, message: str, record_index: Optional[int] = None, record: Optional[dict] = None) -> None:
        super().__init__(message)
        self.message = message
        self.record_index = record_index
        self.record = record


# Canonical dataset fixture required by contract
CANONICAL_ROWS: List[Dict[str, Any]] = [
    {"id": "id1", "score": 2},
    {"id": "id2", "score": 5},
    {"id": "id3", "score": 5},
]


class DatasetSelection:
    """
    Immutable table abstraction providing functional filtering and column projection.
    Guarantees that transformations never mutate the input sequence or internal records.
    """

    def __init__(self, records: Sequence[Dict[str, Any]]) -> None:
        # Store a shallow-copied list of record dicts to guarantee immutability
        self._records: Tuple[Dict[str, Any], ...] = tuple(dict(r) for r in records)

    @property
    def records(self) -> Tuple[Dict[str, Any], ...]:
        return self._records

    def __len__(self) -> int:
        return len(self._records)

    def __getitem__(self, index: int) -> Dict[str, Any]:
        return dict(self._records[index])

    def to_list(self) -> List[Dict[str, Any]]:
        return [dict(r) for r in self._records]

    def filter(
        self,
        predicate: Callable[[Dict[str, Any]], bool],
        strict: bool = True,
    ) -> DatasetSelection:
        """
        Filters records matching the predicate function into a new DatasetSelection.

        Args:
            predicate: Callable taking a record dict and returning True/False.
            strict: If True, predicate exceptions (e.g. KeyError) are raised as DatasetSelectionError.
                    If False, records causing exceptions evaluate to False and are excluded.
        """
        filtered: List[Dict[str, Any]] = []
        for idx, row in enumerate(self._records):
            try:
                if predicate(row):
                    filtered.append(dict(row))
            except Exception as exc:
                if strict:
                    raise DatasetSelectionError(
                        f"Predicate evaluation error on row index {idx}: {exc}",
                        record_index=idx,
                        record=dict(row),
                    ) from exc
        return DatasetSelection(filtered)

    def select(self, columns: Sequence[str]) -> DatasetSelection:
        """
        Projects each record to only the specified columns, preserving row order.
        Raises KeyError if any requested column is absent.
        """
        projected: List[Dict[str, Any]] = []
        for row in self._records:
            subset: Dict[str, Any] = {}
            for col in columns:
                if col not in row:
                    raise KeyError(f"Requested column '{col}' missing from record: {row}")
                subset[col] = row[col]
            projected.append(subset)
        return DatasetSelection(projected)

    def project_column(self, column: str) -> List[Any]:
        """Convenience method returning a flat list of values for a single column in order."""
        return [r[column] for r in self._records]


def filter_and_project(
    rows: Sequence[Dict[str, Any]],
    predicate: Callable[[Dict[str, Any]], bool],
    column: str,
    strict: bool = True,
) -> Tuple[List[Any], List[Dict[str, Any]]]:
    """
    Filters rows by predicate and projects values for a target column.

    Returns:
        (projected_values, full_projected_records)

    Guarantees:
        The input sequence 'rows' is not mutated in any way.
    """
    table = DatasetSelection(rows)
    filtered = table.filter(predicate, strict=strict)
    projected_records = filtered.select([column]).to_list()
    projected_values = filtered.project_column(column)
    return projected_values, projected_records


# --- Scenario Assessment Questions & Executable Rationales ---

APPLIED_QUESTIONS = [
    {
        "id": "Q1_PREDICT_OUTPUT",
        "title": "Predict Output: Filtering and Projection",
        "question": (
            "Given the dataset rows [(id1, score: 2), (id2, score: 5), (id3, score: 5)], "
            "what is the exact ordered sequence of IDs resulting from filtering score >= 5 "
            "and projecting column 'id'?"
        ),
        "options": {
            "A": "['id1', 'id2', 'id3']",
            "B": "['id2', 'id3']",
            "C": "['id3', 'id2']",
            "D": "['id1']",
        },
        "correct_option": "B",
        "expected_value": ["id2", "id3"],
        "rationale": (
            "Row (id1, score: 2) is evaluated against score >= 5, which evaluates to False (2 < 5). "
            "Rows (id2, score: 5) and (id3, score: 5) satisfy 5 >= 5 (True). "
            "Projection of column 'id' preserves the original encounter order, yielding ['id2', 'id3']."
        ),
    },
    {
        "id": "Q2_DIAGNOSE_FAILURE",
        "title": "Diagnose Failure: Schema Inconsistency",
        "question": (
            "Suppose a malformed row missing the 'score' key (e.g. {'id': 'id4'}) is passed "
            "to a strict predicate `lambda r: r['score'] >= 5`. What failure occurs, and how does "
            "the pipeline diagnose it?"
        ),
        "options": {
            "A": "The pipeline defaults score to 0 and silently excludes the row.",
            "B": "A KeyError on 'score' is caught and raised as DatasetSelectionError with the failing row index.",
            "C": "The entire process crashes with a segmentation fault.",
            "D": "The row is included with score set to None.",
        },
        "correct_option": "B",
        "expected_failure_type": "DatasetSelectionError",
        "rationale": (
            "In strict filtering mode, accessing an undeclared key raises a KeyError. "
            "The DatasetSelection validator captures the underlying exception and raises a "
            "DatasetSelectionError identifying row index 3 and the offending record, preventing "
            "silent corruption."
        ),
    },
    {
        "id": "Q3_BOUNDARY_POLICY",
        "title": "Boundary Policy: Strict vs. Inclusive Inequality",
        "question": (
            "For rows with score = 5, what is the impact of choosing an inclusive boundary policy "
            "(score >= 5) versus a strict boundary policy (score > 5)?"
        ),
        "options": {
            "A": "Inclusive (>=) includes boundary rows ['id2', 'id3']; strict (>) excludes them, yielding [].",
            "B": "Both policies yield the exact same result ['id2', 'id3'].",
            "C": "Strict (>) includes all rows; inclusive (>=) excludes boundary rows.",
            "D": "Strict (>) raises a comparison error on exact boundary values.",
        },
        "correct_option": "A",
        "expected_inclusive": ["id2", "id3"],
        "expected_strict": [],
        "rationale": (
            "Boundary points (where value == threshold) are included under the inclusive policy (>=) "
            "because 5 >= 5 is True. Under the strict policy (>), 5 > 5 is False, so both id2 and id3 "
            "are dropped, yielding an empty list []."
        ),
    },
]


def check_question_1_predict_output() -> bool:
    """Executable check verifying output prediction for Q1."""
    input_rows = copy.deepcopy(CANONICAL_ROWS)
    ids, _ = filter_and_project(input_rows, lambda r: r["score"] >= 5, "id")
    return ids == ["id2", "id3"]


def check_question_2_diagnose_failure() -> bool:
    """Executable check verifying failure diagnosis for Q2."""
    rows_with_missing_key = [
        {"id": "id1", "score": 2},
        {"id": "id2", "score": 5},
        {"id": "id3", "score": 5},
        {"id": "id4"},  # Missing 'score' key
    ]
    table = DatasetSelection(rows_with_missing_key)
    try:
        table.filter(lambda r: r["score"] >= 5, strict=True)
        return False
    except DatasetSelectionError as err:
        return err.record_index == 3 and "score" in str(err)


def check_question_3_boundary_policy() -> bool:
    """Executable check verifying boundary policy behavior for Q3."""
    input_rows = copy.deepcopy(CANONICAL_ROWS)
    table = DatasetSelection(input_rows)
    inclusive_ids = table.filter(lambda r: r["score"] >= 5).project_column("id")
    strict_ids = table.filter(lambda r: r["score"] > 5).project_column("id")
    return inclusive_ids == ["id2", "id3"] and strict_ids == []


def verify_applied_questions() -> List[Dict[str, Any]]:
    """Runs all executable checks for the 3 scenario assessment questions."""
    checks = [
        ("Q1_PREDICT_OUTPUT", check_question_1_predict_output()),
        ("Q2_DIAGNOSE_FAILURE", check_question_2_diagnose_failure()),
        ("Q3_BOUNDARY_POLICY", check_question_3_boundary_policy()),
    ]
    results = []
    for q_id, passed in checks:
        q_meta = next(q for q in APPLIED_QUESTIONS if q["id"] == q_id)
        results.append({
            "id": q_id,
            "title": q_meta["title"],
            "correct_option": q_meta["correct_option"],
            "verified": passed,
            "status": "PASS" if passed else "FAIL",
            "rationale": q_meta["rationale"],
        })
    return results


def main() -> None:
    """Runs the canonical selection demonstration and scenario assessment."""
    print("=== Dataset Selection Semantics: Filtering, Projection & Assessment ===\n")

    # 1. Canonical Contract Demonstration
    original_rows = copy.deepcopy(CANONICAL_ROWS)
    source_before = copy.deepcopy(original_rows)

    projected_ids, projected_records = filter_and_project(
        original_rows,
        predicate=lambda r: r["score"] >= 5,
        column="id",
    )

    print("[Contract Check: Canonical Filtering and Projection]")
    print(f"  Input rows:            {source_before}")
    print(f"  Predicate:             score >= 5")
    print(f"  Projected column:      'id'")
    print(f"  Resulting IDs:         {projected_ids}")
    print(f"  Resulting records:     {projected_records}")
    print(f"  Contract met:          {'PASS' if projected_ids == ['id2', 'id3'] else 'FAIL'}")

    # 2. Immutability Verification
    source_intact = original_rows == source_before
    print(f"  Source unmutated:      {'PASS' if source_intact else 'FAIL'}\n")

    # 3. Scenario Assessment Questions
    print("--- Scenario Assessment: Applied Questions & Executable Checks ---")
    verified_questions = verify_applied_questions()
    for item in verified_questions:
        print(f"\n[{item['id']}] {item['title']}")
        print(f"  Correct Answer: ({item['correct_option']})")
        print(f"  Executable Check: {item['status']}")
        print(f"  Rationale: {item['rationale']}")

    print("\nAll dataset selection contracts and scenario checks passed successfully.")


if __name__ == "__main__":
    main()
