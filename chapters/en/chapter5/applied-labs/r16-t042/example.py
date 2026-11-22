#!/usr/bin/env python3
"""
Applied Lab R16-T042: Streaming Aggregation — Boundary-Case Lesson Extension.

This module demonstrates streaming aggregation over JSONL records without collecting
the complete input in memory, connecting directly to Chapter 5, Section 4
("Big data? Datasets to the rescue!" [big-data-datasets-to-the-rescue]).

Teaching and Simulation Scope:
- Reads input JSONL line-by-line (one record at a time).
- Maintains a strictly bounded in-memory state: an aggregation counter dictionary
  mapping category names to occurrences, and a list of malformed line errors.
- Never reads or loads the entire dataset into memory at once.
- Deterministic standard library implementation (json, typing, dataclasses).
- Requires no model downloads, external packages, paid cloud services, GPU, or physical hardware.

Contract:
- Inputs: Iterable stream of strings (lines from JSONL or text stream).
- A, B, A, C yields {"A": 2, "B": 1, "C": 1}.
- A malformed line is reported with its 1-indexed line number.
- Empty input gives {}.
- Boundary cases:
  * Empty string or empty line stream -> counts={}, malformed=[].
  * Blank/whitespace-only lines -> skipped cleanly without incrementing line errors.
  * Smallest valid input -> single record {"category": "A"} -> counts={"A": 1}.
  * Missing category field or non-dict JSON -> recorded as malformed with line number.
  * Invalid JSON syntax -> recorded as malformed with line number.
"""

from dataclasses import dataclass, field
import json
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple


@dataclass
class MalformedLineError:
    """Record of a malformed line encountered during streaming."""

    line_number: int
    raw_content: str
    error_message: str

    def as_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "line_number": self.line_number,
            "raw_content": self.raw_content,
            "error_message": self.error_message,
        }


@dataclass
class StreamAggregationResult:
    """Aggregated output resulting from a streaming parse pass."""

    category_counts: Dict[str, int] = field(default_factory=dict)
    malformed_records: List[MalformedLineError] = field(default_factory=list)
    total_lines_processed: int = 0
    valid_records_count: int = 0

    def as_dict(self) -> Dict[str, Any]:
        """Convert full result to dictionary format."""
        return {
            "category_counts": dict(self.category_counts),
            "malformed_records": [m.as_dict() for m in self.malformed_records],
            "total_lines_processed": self.total_lines_processed,
            "valid_records_count": self.valid_records_count,
        }


def stream_aggregate_jsonl(lines: Iterable[str], category_field: str = "category") -> StreamAggregationResult:
    """Aggregate categories one record at a time from a stream of JSONL lines.

    Memory Bound Guarantee:
    Only one line is parsed at a time. The working memory is bounded by the
    number of unique categories observed and recorded malformed error reports,
    never the volume of raw text streamed.

    Boundary decisions:
    1. Empty stream: returns category_counts={}, malformed_records=[].
    2. Blank lines (pure whitespace): treated as empty whitespace gaps and ignored
       (do not raise errors, do not count as malformed).
    3. Syntax errors (unparseable JSON): recorded in malformed_records with 1-based line number.
    4. Schema errors (valid JSON but not an object, or missing category_field, or category is null/non-string):
       recorded in malformed_records with 1-based line number.

    Args:
        lines (Iterable[str]): An iterable emitting JSONL lines one at a time.
        category_field (str): The JSON key holding the category string (default: "category").

    Returns:
        StreamAggregationResult: Counts mapping and malformed records list.
    """
    counts: Dict[str, int] = {}
    malformed: List[MalformedLineError] = []
    line_number = 0
    valid_count = 0

    for raw_line in lines:
        line_number += 1
        line_str = raw_line.strip()

        # Boundary decision: completely blank lines are skipped cleanly
        if not line_str:
            continue

        try:
            record = json.loads(line_str)
        except json.JSONDecodeError as exc:
            malformed.append(
                MalformedLineError(
                    line_number=line_number,
                    raw_content=raw_line.rstrip("\r\n"),
                    error_message=f"Invalid JSON syntax: {exc.msg}",
                )
            )
            continue

        if not isinstance(record, dict):
            malformed.append(
                MalformedLineError(
                    line_number=line_number,
                    raw_content=raw_line.rstrip("\r\n"),
                    error_message=f"Expected JSON object (dict), got {type(record).__name__}",
                )
            )
            continue

        if category_field not in record:
            malformed.append(
                MalformedLineError(
                    line_number=line_number,
                    raw_content=raw_line.rstrip("\r\n"),
                    error_message=f"Missing required field '{category_field}'",
                )
            )
            continue

        category = record[category_field]
        if not isinstance(category, str) or not category.strip():
            malformed.append(
                MalformedLineError(
                    line_number=line_number,
                    raw_content=raw_line.rstrip("\r\n"),
                    error_message=f"Field '{category_field}' must be a non-empty string, got {repr(category)}",
                )
            )
            continue

        category_key = category.strip()
        counts[category_key] = counts.get(category_key, 0) + 1
        valid_count += 1

    return StreamAggregationResult(
        category_counts=counts,
        malformed_records=malformed,
        total_lines_processed=line_number,
        valid_records_count=valid_count,
    )


def count_categories_from_stream(lines: Iterable[str]) -> Dict[str, int]:
    """Convenience functional helper returning only the category counts dictionary."""
    result = stream_aggregate_jsonl(lines)
    return result.category_counts


if __name__ == "__main__":
    print("=== Streaming Aggregation Example (R16-T042) ===")

    # Scenario 1: A, B, A, C -> {"A": 2, "B": 1, "C": 1}
    sample_stream = [
        '{"category": "A"}',
        '{"category": "B"}',
        '{"category": "A"}',
        '{"category": "C"}',
    ]
    res1 = stream_aggregate_jsonl(sample_stream)
    print("\nScenario 1 (A, B, A, C):")
    print(f"  Counts:    {res1.category_counts}")
    print(f"  Malformed: {res1.malformed_records}")

    # Scenario 2: Empty input -> {}
    res2 = stream_aggregate_jsonl([])
    print("\nScenario 2 (Empty input):")
    print(f"  Counts:    {res2.category_counts}")

    # Scenario 3: Stream containing a malformed line
    malformed_stream = [
        '{"category": "A"}',
        '{bad json',
        '{"category": "B"}',
    ]
    res3 = stream_aggregate_jsonl(malformed_stream)
    print("\nScenario 3 (Stream with malformed line):")
    print(f"  Counts:    {res3.category_counts}")
    for err in res3.malformed_records:
        print(f"  Malformed Line {err.line_number}: {err.error_message} (content: {repr(err.raw_content)})")
