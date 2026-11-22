# Applied Lab R16-T027: Dataset Manifest Validation Worked Example

A minimal, runnable concept lab demonstrating schema validation, split provenance, and stable ID uniqueness for local JSONL datasets, complementing [Chapter 5, Section 5 ("Creating your own dataset")](../../5.mdx).

---

## 1. Concept and Lesson Connection

In [Chapter 5, Section 5](../../5.mdx), custom datasets are assembled from raw sources (such as GitHub issues) and structured as local JSONL files before being loaded into `Dataset` objects or pushed to the Hugging Face Hub.

When preparing dataset splits (`train` and `validation`), data integrity requires:
1. **Mandatory Schema Fields**: Every record must provide required keys (e.g. `id`, `text`, `label`) to prevent runtime crashes during tokenization and training.
2. **Stable Unique Identifiers**: Each observation must have a unique identifier across the entire dataset. An ID appearing in both the training split and validation split violates **split provenance**, introducing severe evaluation leakage.
3. **Exact Line-Level Error Diagnostics**: When parsing gigabytes of raw JSONL data, validation errors must pinpoint the exact split and line number of invalid records.

---

## 2. Worked Scenarios: Input-to-Output Walkthrough

### Scenario 1: Valid Two-Split Fixture (Normal Case)
- **Train split**:
  - Line 1: `{"id": 101, "text": "Issue with dataset download timeout", "label": "bug"}`
  - Line 2: `{"id": 102, "text": "Feature request: add WebDataset loader", "label": "enhancement"}`
- **Validation split**:
  - Line 1: `{"id": 201, "text": "Clarify map batched=True documentation", "label": "documentation"}`
- **Validation Outcome**: `PASS`
  - Total records: `3`
  - Split counts: `{"train": 2, "validation": 1}`
  - Unique verified IDs: `[101, 102, 201]`

---

### Scenario 2: Missing Required Field (`label`)
- **Train split**:
  - Line 1: `{"id": 101, "text": "First issue record", "label": "bug"}`
  - Line 2: `{"id": 102, "text": "Second issue record without label"}` *(Missing 'label')*
- **Validation Outcome**: `FAIL` (`ManifestValidationError`)
  - Error: `Missing required field 'label' in split 'train' at line 2`
  - Exact diagnosis: Identifies split (`train`), failing field (`label`), and line number (`2`).

---

### Scenario 3: Duplicate ID Across Splits (Split Provenance Leakage)
- **Train split**:
  - Line 1: `{"id": 101, "text": "First issue in train", "label": "bug"}`
  - Line 2: `{"id": 102, "text": "Second issue in train", "label": "enhancement"}`
- **Validation split**:
  - Line 1: `{"id": 101, "text": "Duplicate issue ID 101 in validation", "label": "bug"}` *(Duplicate ID 101)*
- **Validation Outcome**: `FAIL` (`ManifestValidationError`)
  - Error: `Duplicate ID '101' detected across splits: first defined in 'train' at line 1, duplicated in 'validation' at line 1`
  - Exact diagnosis: Prevents data contamination between evaluation and training sets.

---

## 3. Scope and Limitations

- **Pedagogical Scope**: Pure Python standard library implementation of line-by-line JSONL manifest validation and ID provenance tracking.
- **Prerequisites**: Python 3 standard library (`json`, `dataclasses`, `unittest`, `typing`, `sys`).
- **No External Dependencies**: Requires no GPU, network calls, GitHub API tokens, or external packages.
- **Simplifications**: Validates schema presence and ID uniqueness; does not validate complex semantic embeddings or label distributions.

---

## 4. Usage and Invocations

### Direct CLI Invocation
```bash
python3 chapters/en/chapter5/applied-labs/r16-t027/example.py
```
Output:
```text
=== Dataset Manifest Validation: Worked Example with Checks ===

[Case 1: Valid Two-Split Fixture]
  Status:         VALID
  Total records:  3
  Split counts:   {'train': 2, 'validation': 1}
  Verified IDs:   [101, 102, 201]
  Outcome:        Manifest passed validation: 3 records verified across 2 splits.

[Case 2: Missing Required Field ('label')]
  Caught expected error: Missing required field 'label' in split 'train' at line 2
  Failed split:          train
  Line number:           2
  Missing field:         label

[Case 3: Duplicate ID Across Splits]
  Caught expected error: Duplicate ID '101' detected across splits: first defined in 'train' at line 1, duplicated in 'validation' at line 1
  Conflicting ID:        101
  Duplicated in split:   validation at line 1

All worked validation scenarios behaved exactly according to specification.
```

### Python API
```python
from example import DatasetManifestValidator, VALID_TWO_SPLIT_FIXTURE

validator = DatasetManifestValidator(required_fields=("id", "text", "label"))
report = validator.validate_manifest(VALID_TWO_SPLIT_FIXTURE)
print(report.is_valid)        # True
print(report.total_records)   # 3
print(report.split_counts)    # {'train': 2, 'validation': 1}
```

---

## 5. Automated Testing

Run unit tests via `unittest`:
```bash
python3 -m unittest discover -s chapters/en/chapter5/applied-labs/r16-t027 -p "test_*.py" -v
```
All 10 unit tests pass in a fresh process, verifying schema rules, exact line-number error reporting, cross-split provenance checks, and boundary handling.
