# Applied Lab R16-T030: Dataset Selection Semantics — Scenario Assessment

This applied lab extends Chapter 5, Section 3 (**"Time to slice and dice"**) with a concrete, contract-tested implementation of functional dataset filtering, column projection, and source collection immutability, complemented by an interactive 3-question scenario assessment.

## Educational Context and Lesson Connection

In [Chapter 5, Section 3](/course/chapter5/3), 🤗 Datasets demonstrates techniques for cleaning, filtering (`Dataset.filter()`), selecting (`Dataset.select()`), and projecting subsets of data.

In production data processing, two guarantees are paramount:
1. **Source Immutability**: Transforming, filtering, or projecting a collection must never mutate the original in-memory records.
2. **Deterministic Sequence & Identity Preservation**: Output rows must preserve their original identifier linkage and order.

### Canonical Contract
Given input rows:
```python
[
    {"id": "id1", "score": 2},
    {"id": "id2", "score": 5},
    {"id": "id3", "score": 5},
]
```
Filtering by `score >= 5` and projecting column `'id'` yields:
```python
["id2", "id3"]
```
in exact encounter order, leaving the source rows untouched.

## Scenario Assessment

This lab provides three applied scenario assessment questions with full rationales and executable checks:

### 1. Predict an Output (Q1)
- **Question**: What is the exact sequence of IDs for rows `[(id1, 2), (id2, 5), (id3, 5)]` filtered with `score >= 5` and projected `'id'`?
- **Answer**: `['id2', 'id3']`
- **Rationale**: Row `id1` has `score = 2 < 5` (excluded). Rows `id2` and `id3` have `score = 5 >= 5` (included). Column projection preserves row sequence.

### 2. Diagnose a Failure (Q2)
- **Question**: How does the selection pipeline diagnose a record missing the predicate column `'score'`?
- **Answer**: In strict mode, accessing missing keys raises a `DatasetSelectionError` reporting the exact row index and offending record.
- **Rationale**: Explicit diagnostics prevent silent data corruption from schema drift.

### 3. Choose a Boundary Policy (Q3)
- **Question**: What is the impact of choosing an inclusive (`score >= 5`) vs strict (`score > 5`) boundary policy on rows with `score == 5`?
- **Answer**: Inclusive (`>=`) retains `['id2', 'id3']`; strict (`>`) drops boundary rows, yielding `[]`.
- **Rationale**: Boundary inclusion policy governs threshold-edge data retention.

## Running the Lab

### 1. Execute Worked Example & Scenario Checks
```bash
python3 chapters/en/chapter5/applied-labs/r16-t030/example.py
```

### 2. Run Automated Unit Tests
```bash
python3 -m unittest discover -s chapters/en/chapter5/applied-labs/r16-t030 -p "test_*.py"
```

## Scope and Simplifications

- **Standard Library Implementation**: Implemented purely in Python 3 (`copy`, `dataclasses`, `unittest`) without external libraries.
- **Simulation Notice**: Operates offline on local fixtures; does not require Apache Arrow, GPUs, or remote datasets.
