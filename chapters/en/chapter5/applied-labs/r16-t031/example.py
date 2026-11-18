"""Validate a tiny local JSONL dataset that has a train/validation manifest.

Teaching fixture, standard library only. It checks file structure (required
fields, labels, duplicate ids). It says nothing about data quality or models.
"""
import json
import tempfile
from pathlib import Path

REQUIRED_FIELDS = ("id", "text", "label")
SPLITS = ("train", "validation")

VALID_TRAIN = [
    '{"id": "a1", "text": "great film", "label": "pos"}',
    '{"id": "a2", "text": "dull film", "label": "neg"}',
]
VALID_VALIDATION = ['{"id": "b1", "text": "fine film", "label": "pos"}']


class ManifestError(ValueError):
    """The manifest or one JSONL line breaks a rule."""


def read_split(path, split):
    """Return [(line_number, record)] for one JSONL file. Blank lines are skipped."""
    rows = []
    with open(path, encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            try:
                record = json.loads(raw)
            except json.JSONDecodeError as err:
                raise ManifestError(f"{split} line {line_no}: invalid JSON ({err.msg})")
            if not isinstance(record, dict):
                raise ManifestError(f"{split} line {line_no}: record must be a JSON object")
            for field in REQUIRED_FIELDS:
                if record.get(field) in (None, ""):
                    raise ManifestError(
                        f"{split} line {line_no}: missing required field '{field}'")
            rows.append((line_no, record))
    return rows


def validate_dataset(manifest):
    """manifest maps 'train' and 'validation' to JSONL paths. Returns row counts."""
    if sorted(manifest) != sorted(SPLITS):
        raise ManifestError("manifest must list exactly these splits: train, validation")
    seen = {}
    counts = {}
    for split in SPLITS:
        rows = read_split(manifest[split], split)
        for line_no, record in rows:
            key = str(record["id"])
            if key in seen:
                other_split, other_line = seen[key]
                raise ManifestError(
                    f"duplicate id '{key}': {other_split} line {other_line} "
                    f"and {split} line {line_no}")
            seen[key] = (split, line_no)
        counts[split] = len(rows)
    return counts


def build_manifest(folder, train_lines, validation_lines):
    """Write the two JSONL files into folder and return the manifest dict."""
    manifest = {}
    for split, lines in (("train", train_lines), ("validation", validation_lines)):
        path = Path(folder) / (split + ".jsonl")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        manifest[split] = str(path)
    return manifest


def main():
    no_label = [VALID_TRAIN[0], '{"id": "a2", "text": "dull film"}']
    repeat = ['{"id": "a1", "text": "again", "label": "pos"}']
    cases = [
        ("valid two splits", VALID_TRAIN, VALID_VALIDATION),
        ("missing label", no_label, VALID_VALIDATION),
        ("duplicate id across splits", VALID_TRAIN, repeat),
    ]
    with tempfile.TemporaryDirectory() as folder:
        for name, train, validation in cases:
            manifest = build_manifest(folder, train, validation)
            try:
                print(f"{name} -> PASS {validate_dataset(manifest)}")
            except ManifestError as err:
                print(f"{name} -> FAIL: {err}")


if __name__ == "__main__":
    main()
