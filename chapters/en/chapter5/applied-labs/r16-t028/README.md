# Applied Lab R16-T028: Streaming Aggregation — Failure and Recovery

This lab extends Chapter 5, Section 4 (**"Big data? 🤗 Datasets to the rescue!"**) with a runnable, contract-verified example of streaming data ingestion with bounded memory, per-line diagnostics, and resilient recovery.

## Overview and Educational Context

In [Chapter 5, Section 4](/course/chapter5/4), 🤗 Datasets demonstrates streaming large corpora (such as the 825 GB *Pile*) via `IterableDataset` and `load_dataset(..., streaming=True)` without requiring hundreds of gigabytes of RAM or local disk space.

In real-world data pipelines, large streamed JSONL files frequently contain corrupted lines, truncated records, or missing schema fields. A robust streaming processor must:
1. **Maintain Bounded Memory State ($O(K)$)**: Ingest records one at a time using iterators without loading the entire dataset into memory.
2. **Provide Precise Line Diagnostics**: Report any malformed or invalid records with 1-based line numbers and specific failure reasons.
3. **Recover Gracefully**: Log errors without crashing the entire stream, resuming aggregation immediately on the next valid record.

## Architecture

- **`StreamingCategoryAggregator`**: Reads lines from any iterable (file, generator, or string stream) one by one. Updates category frequencies in-place in a dictionary.
- **`StreamingRecordError`**: Custom exception with `line_number`, `error_type`, and `raw_line`.
- **`StreamingErrorRecord`**: Structured dataclass recording non-fatal diagnostic events during streaming.
- **`AggregationResult`**: Encapsulates final counts, line counts, valid record counts, error details, and recovery status (`recovered=True`).

## Fixtures and Contracts

1. **Canonical Stream (`A, B, A, C`)**:
   - Input: `{"category": "A"}\n{"category": "B"}\n{"category": "A"}\n{"category": "C"}\n`
   - Output: `{"A": 2, "B": 1, "C": 1}` with 0 errors.
2. **Empty Stream**:
   - Input: `""`
   - Output: `{}` with 0 errors and 0 lines.
3. **Malformed JSON with Resilient Recovery**:
   - Input:
     ```text
     Line 1: {"category": "A"}
     Line 2: {"invalid_json": broken
     Line 3: {"category": "B"}
     Line 4: {"category": "A"}
     Line 5: {"category": "C"}
     ```
   - Behavior: Line 2 is reported with `line_number=2`, `error_type='SYNTAX_ERROR'`. Ingestion immediately recovers on line 3 (`"category": "B"`). Final aggregated counts reach `{"A": 2, "B": 1, "C": 1}` with `recovered=True`.
4. **Missing Key with Resilient Recovery**:
   - Input: Line 2 lacks required key `"category"`.
   - Behavior: Line 2 reported with `line_number=2`, `error_type='MISSING_FIELD'`. Ingestion recovers on line 3, yielding `{"A": 2, "B": 1, "C": 1}`.

## Execution and Verification

### 1. Run Worked Example
```bash
python3 chapters/en/chapter5/applied-labs/r16-t028/example.py
```

### 2. Run Automated Unittests
```bash
python3 -m unittest discover -s chapters/en/chapter5/applied-labs/r16-t028 -p "test_*.py"
```

## Scope and Simplifications

- **Pedagogical Scope**: This lab demonstrates streaming aggregation and error recovery using Python's standard library (`json`, `dataclasses`, `unittest`).
- **No External Dependencies**: Operates offline without network access, cloud APIs, GPUs, or model downloads.
