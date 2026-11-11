"""
R16-T015: Dataset Manifest Validation — Offline Service Adapter
===============================================================
Chapter 5, Section 2: "What if my dataset isn't on the Hub?"

Lesson connection
-----------------
The lesson shows how load_dataset() validates schema and split provenance
when loading local/remote JSONL files. This lab reproduces the same
validation logic using only the Python 3 standard library — no Hugging
Face Datasets library, no network, no GPU.

What this mock does NOT establish
----------------------------------
- It does not test actual Hub connectivity or remote URL resolution.
- It does not test streaming or Arrow-backed memory-mapped files.
- It does not test automatic decompression (gzip/zip/tar).
- It does not validate tokenizer output or feature encodings.
All such behaviour requires real service credentials/hardware and is
outside the scope of this task.

Contract (explicitly labelled as SIMULATION/MOCK)
-------------------------------------------------
Input : manifest dict mapping split names → list of JSONL record dicts
        Each record must have string fields: "id", "text", "label"
Output: ValidationResult with fields:
          ok (bool), errors (list[str])

Rules
-----
1. Missing required field   → error "line N: missing field '<field>'"
2. Duplicate ID across any two splits → error "duplicate id '<id>' in splits <A> and <B>"
3. All records valid, all IDs unique → ok=True, errors=[]
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Dict, List, Any


REQUIRED_FIELDS = ("id", "text", "label")


@dataclass
class ValidationResult:
    """Result of JSONL manifest validation (SIMULATED — no real Hub call)."""
    ok: bool
    errors: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public interface (callable adapter — the seam for real-service injection)
# ---------------------------------------------------------------------------

def validate_manifest(manifest: Dict[str, List[Dict[str, Any]]]) -> ValidationResult:
    """
    Validate a dataset manifest (SIMULATED offline adapter).

    Parameters
    ----------
    manifest : dict
        Keys are split names (e.g. "train", "validation").
        Values are lists of record dicts with required fields id/text/label.

    Returns
    -------
    ValidationResult
        ok=True  when every record has the required fields and no ID is
                 shared across splits.
        ok=False when any validation rule is violated; errors lists all
                 violations found.

    NOTE: This is a pure-Python simulation. It replicates the schema and
    provenance checks performed by HuggingFace Datasets load_dataset() but
    makes no network calls and requires no installed packages.
    """
    errors: List[str] = []
    # Maps id → split name, for cross-split duplicate detection
    seen_ids: Dict[str, str] = {}

    for split_name, records in manifest.items():
        for line_no, record in enumerate(records, start=1):
            # --- schema check ---
            for req in REQUIRED_FIELDS:
                if req not in record:
                    errors.append(
                        f"line {line_no} in split '{split_name}': missing field '{req}'"
                    )
            # --- cross-split duplicate ID check (only if id field is present) ---
            if "id" in record:
                rid = record["id"]
                if rid in seen_ids:
                    prev_split = seen_ids[rid]
                    if prev_split != split_name:
                        errors.append(
                            f"duplicate id '{rid}' in splits '{prev_split}' and '{split_name}'"
                        )
                else:
                    seen_ids[rid] = split_name

    return ValidationResult(ok=len(errors) == 0, errors=errors)


# ---------------------------------------------------------------------------
# Deterministic local adapter (fixture-based, no I/O)
# ---------------------------------------------------------------------------

def load_jsonl_fixture(raw_lines: List[str]) -> List[Dict[str, Any]]:
    """Parse a list of JSONL strings into record dicts (SIMULATED file load)."""
    return [json.loads(line) for line in raw_lines if line.strip()]


# ---------------------------------------------------------------------------
# Demonstration (run directly for a quick sanity check)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Fixture 1: valid two-split dataset
    train_records = [
        {"id": "1", "text": "Hello world", "label": "positive"},
        {"id": "2", "text": "Goodbye world", "label": "negative"},
    ]
    validation_records = [
        {"id": "3", "text": "Neutral statement", "label": "neutral"},
    ]
    manifest_valid = {"train": train_records, "validation": validation_records}
    result = validate_manifest(manifest_valid)
    print(f"[VALID MANIFEST]  ok={result.ok}  errors={result.errors}")
    # Expected: ok=True, errors=[]

    # Fixture 2: missing 'label' field on line 2 of train split
    manifest_missing = {
        "train": [
            {"id": "10", "text": "Good", "label": "positive"},
            {"id": "11", "text": "Bad"},          # label missing
        ]
    }
    result2 = validate_manifest(manifest_missing)
    print(f"[MISSING FIELD]   ok={result2.ok}  errors={result2.errors}")
    # Expected: ok=False, errors contain "line 2 in split 'train': missing field 'label'"

    # Fixture 3: duplicate ID across splits
    manifest_dup = {
        "train":      [{"id": "A", "text": "First", "label": "pos"}],
        "validation": [{"id": "A", "text": "Second", "label": "neg"}],
    }
    result3 = validate_manifest(manifest_dup)
    print(f"[DUPLICATE ID]    ok={result3.ok}  errors={result3.errors}")
    # Expected: ok=False, errors contain duplicate id 'A'

