# R16-T015: Dataset Manifest Validation — Offline Service Adapter

**Task**: R16-T015 · Issue #18  
**Chapter**: 5 — Section 2: "What if my dataset isn't on the Hub?"  
**Branch**: `R16-T015`  
**Type**: Offline service adapter

---

## Overview

This applied lab extends the lesson on loading local/remote JSONL datasets
by demonstrating the schema and split-provenance validation logic that
`load_dataset()` performs internally — implemented here using **only the
Python 3 standard library** (no Hugging Face Datasets, no network, no GPU).

The external dependency (`load_dataset`) is placed behind a callable
interface (`validate_manifest`) with a deterministic local adapter, so the
same interface can later be swapped for a real-service implementation by
providing real credentials and hardware.

---

## Contract

| Scenario | Input | Expected output |
|---|---|---|
| Valid two-split manifest | train (2 records) + validation (1 record), all fields present, unique IDs | `ok=True`, `errors=[]` |
| Missing `label` on line 2 | train record 2 has no `label` key | `ok=False`, error contains `"line 2 … missing field 'label'"` |
| Duplicate ID across splits | Same `id` appears in both `train` and `validation` | `ok=False`, error contains `"duplicate id"` and both split names |

---

## Files

| File | Purpose |
|---|---|
| `example.py` | `validate_manifest()` adapter + `load_jsonl_fixture()` helper |
| `test_example.py` | 18 unit tests covering normal, boundary and failure scenarios |
| `README.md` | This file |

---

## Running

```bash
# From the repository root:
python3 -m unittest discover \
  -s chapters/en/chapter5/applied-labs/r16-t015 \
  -p "test_*.py" -v
```

Or run the demo directly:

```bash
python3 chapters/en/chapter5/applied-labs/r16-t015/example.py
```

---

## What this mock does NOT establish

> **SIMULATION NOTE**: This lab is a pure-Python simulation of
> `load_dataset()` schema validation. It does **not** test:
>
> - Real Hugging Face Hub connectivity or remote URL resolution
> - Streaming or Arrow-backed memory-mapped file access
> - Automatic decompression of gzip / zip / tar archives
> - Tokenizer output or feature encodings
> - Any cloud-service SLA, latency, or availability guarantees
>
> All such behaviour requires real service credentials/hardware and is
> outside the scope of this task.

---

## Lesson link

See the linked section at the end of
[`chapters/en/chapter5/2.mdx`](../../2.mdx)
for the exact invocation, fixture, and expected output.

