"""
Streaming aggregation with bounded memory, failure reporting, and error recovery.

This module illustrates the core principles of streaming data ingestion from
Chapter 5, Section 4 ("Big data? 🤗 Datasets to the rescue!").
It processes JSONL lines one at a time, tracks category counts in bounded state O(K),
reports malformed or incomplete records with exact 1-based line numbers, and
demonstrates resilient recovery on subsequent valid records.
"""

from __future__ import annotations

import io
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Union


class StreamingRecordError(Exception):
    """Raised when an unparseable or invalid record is encountered in strict mode."""

    def __init__(self, message: str, line_number: int, raw_line: str = "", error_type: str = "MALFORMED_RECORD") -> None:
        super().__init__(f"Line {line_number}: {message}")
        self.message = message
        self.line_number = line_number
        self.raw_line = raw_line
        self.error_type = error_type


@dataclass(frozen=True)
class StreamingErrorRecord:
    """Diagnostic details for an invalid record encountered during streaming."""

    line_number: int
    error_type: str
    message: str
    raw_line: str


@dataclass
class AggregationResult:
    """Summary of streaming category counts and diagnostics."""

    counts: Dict[str, int] = field(default_factory=dict)
    total_lines: int = 0
    valid_records: int = 0
    errors: List[StreamingErrorRecord] = field(default_factory=list)
    recovered: bool = False

    def to_dict(self) -> dict:
        return {
            "counts": self.counts,
            "total_lines": self.total_lines,
            "valid_records": self.valid_records,
            "errors": [
                {
                    "line_number": err.line_number,
                    "error_type": err.error_type,
                    "message": err.message,
                    "raw_line": err.raw_line,
                }
                for err in self.errors
            ],
            "recovered": self.recovered,
        }


# Standard fixtures for contracts and demonstrations
FIXTURE_ABAC = '{"category": "A"}\n{"category": "B"}\n{"category": "A"}\n{"category": "C"}\n'
FIXTURE_EMPTY = ""
FIXTURE_MALFORMED_WITH_RECOVERY = (
    '{"category": "A"}\n'
    '{"invalid_json": broken\n'
    '{"category": "B"}\n'
    '{"category": "A"}\n'
    '{"category": "C"}\n'
)
FIXTURE_MISSING_KEY_WITH_RECOVERY = (
    '{"category": "A"}\n'
    '{"id": 2, "text": "missing category key"}\n'
    '{"category": "B"}\n'
    '{"category": "A"}\n'
    '{"category": "C"}\n'
)


class StreamingCategoryAggregator:
    """
    Streams JSONL records one-by-one and aggregates category frequencies.

    Bounded Memory Guarantee:
      Does not buffer the stream into memory. Only retains category counts (bounded
      by the number of distinct categories) and an optional diagnostics log.
    """

    def __init__(self, category_field: str = "category") -> None:
        self.category_field = category_field

    def parse_line(self, raw_line: str, line_number: int) -> Optional[str]:
        """
        Parses a single line and extracts the category value.

        Returns None if the line is blank/whitespace.
        Raises StreamingRecordError if the line has syntax errors or lacks the required field.
        """
        stripped = raw_line.strip()
        if not stripped:
            return None

        try:
            record = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise StreamingRecordError(
                message=f"JSON decode failure: {exc.msg} (col {exc.colno})",
                line_number=line_number,
                raw_line=raw_line.rstrip("\r\n"),
                error_type="SYNTAX_ERROR",
            ) from exc

        if not isinstance(record, dict):
            raise StreamingRecordError(
                message=f"Record must be a JSON object, got {type(record).__name__}",
                line_number=line_number,
                raw_line=raw_line.rstrip("\r\n"),
                error_type="INVALID_TYPE",
            )

        if self.category_field not in record:
            raise StreamingRecordError(
                message=f"Missing required field '{self.category_field}'",
                line_number=line_number,
                raw_line=raw_line.rstrip("\r\n"),
                error_type="MISSING_FIELD",
            )

        val = record[self.category_field]
        if val is None or not isinstance(val, (str, int)):
            raise StreamingRecordError(
                message=f"Field '{self.category_field}' must be a non-null string or integer, got {type(val).__name__}",
                line_number=line_number,
                raw_line=raw_line.rstrip("\r\n"),
                error_type="INVALID_VALUE",
            )

        return str(val)

    def aggregate_stream(
        self,
        stream: Iterable[str],
        on_error: str = "recover",
    ) -> AggregationResult:
        """
        Aggregates categories from an iterable of lines (generator, file, or list).

        Args:
            stream: Iterable yielding string lines.
            on_error: 'recover' to log errors and continue streaming;
                      'raise' to abort and raise StreamingRecordError on first failure.

        Returns:
            AggregationResult containing counts, line totals, and diagnostics.
        """
        counts: Dict[str, int] = {}
        errors: List[StreamingErrorRecord] = []
        total_lines = 0
        valid_records = 0
        encountered_error = False
        recovered = False

        for line_number, raw_line in enumerate(stream, start=1):
            total_lines += 1
            try:
                category = self.parse_line(raw_line, line_number)
                if category is None:
                    continue

                counts[category] = counts.get(category, 0) + 1
                valid_records += 1

                # If we previously saw an error and successfully processed this record,
                # we have demonstrated recovery!
                if encountered_error:
                    recovered = True

            except StreamingRecordError as err:
                encountered_error = True
                if on_error == "raise":
                    raise

                errors.append(
                    StreamingErrorRecord(
                        line_number=err.line_number,
                        error_type=err.error_type,
                        message=err.message,
                        raw_line=err.raw_line,
                    )
                )

        return AggregationResult(
            counts=counts,
            total_lines=total_lines,
            valid_records=valid_records,
            errors=errors,
            recovered=recovered,
        )

    def aggregate_string(self, content: str, on_error: str = "recover") -> AggregationResult:
        """Streams lines from an in-memory string using an iterator."""
        return self.aggregate_stream(io.StringIO(content), on_error=on_error)

    def aggregate_file(self, path: Union[str, Path], on_error: str = "recover") -> AggregationResult:
        """Streams lines directly from a file path without preloading contents."""
        file_path = Path(path)
        with file_path.open("r", encoding="utf-8") as f:
            return self.aggregate_stream(f, on_error=on_error)


def main() -> None:
    """Executes worked examples illustrating normal, empty, and failure/recovery scenarios."""
    aggregator = StreamingCategoryAggregator()

    print("=== Streaming Aggregation: Worked Example with Failure & Recovery ===\n")

    # Scenario 1: Canonical A, B, A, C -> A:2, B:1, C:1
    print("[Scenario 1: Canonical Stream A, B, A, C]")
    res1 = aggregator.aggregate_string(FIXTURE_ABAC)
    print(f"  Input:         A, B, A, C")
    print(f"  Result counts: {res1.counts}")
    print(f"  Total lines:   {res1.total_lines}, Valid records: {res1.valid_records}, Errors: {len(res1.errors)}")
    print(f"  Outcome:       {'PASS' if res1.counts == {'A': 2, 'B': 1, 'C': 1} else 'FAIL'}\n")

    # Scenario 2: Empty Stream -> {}
    print("[Scenario 2: Empty Stream]")
    res2 = aggregator.aggregate_string(FIXTURE_EMPTY)
    print(f"  Input:         <empty>")
    print(f"  Result counts: {res2.counts}")
    print(f"  Total lines:   {res2.total_lines}, Valid records: {res2.valid_records}, Errors: {len(res2.errors)}")
    print(f"  Outcome:       {'PASS' if res2.counts == {} else 'FAIL'}\n")

    # Scenario 3: Malformed JSON with Recovery
    print("[Scenario 3: Malformed JSON Line with Resilient Recovery]")
    res3 = aggregator.aggregate_string(FIXTURE_MALFORMED_WITH_RECOVERY)
    print(f"  Total lines:   {res3.total_lines}, Valid records: {res3.valid_records}")
    print(f"  Reported error count: {len(res3.errors)}")
    for err in res3.errors:
        print(f"    -> Line {err.line_number} [{err.error_type}]: {err.message}")
        print(f"       Raw snippet: '{err.raw_line}'")
    print(f"  Recovered on next valid input: {res3.recovered}")
    print(f"  Final aggregated counts:      {res3.counts}")
    print(f"  Outcome: {'PASS' if res3.counts == {'A': 2, 'B': 1, 'C': 1} and res3.recovered else 'FAIL'}\n")

    # Scenario 4: Missing Key with Recovery
    print("[Scenario 4: Missing Required Key with Resilient Recovery]")
    res4 = aggregator.aggregate_string(FIXTURE_MISSING_KEY_WITH_RECOVERY)
    print(f"  Total lines:   {res4.total_lines}, Valid records: {res4.valid_records}")
    print(f"  Reported error count: {len(res4.errors)}")
    for err in res4.errors:
        print(f"    -> Line {err.line_number} [{err.error_type}]: {err.message}")
    print(f"  Recovered on next valid input: {res4.recovered}")
    print(f"  Final aggregated counts:      {res4.counts}")
    print(f"  Outcome: {'PASS' if res4.counts == {'A': 2, 'B': 1, 'C': 1} and res4.recovered else 'FAIL'}\n")

    print("All streaming scenarios executed successfully.")


if __name__ == "__main__":
    main()
