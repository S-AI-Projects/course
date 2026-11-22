# Applied Lab R16-T042: Streaming Aggregation (Boundary-Case Lesson Extension)

## Related Lesson
- **Chapter**: Chapter 5: The 🤗 Datasets Library
- **Section**: [Big data? 🤗 Datasets to the rescue! (`big-data-datasets-to-the-rescue`)](../../4.mdx)

## Objective & Focus
In Chapter 5, Section 4, the course demonstrates that loading multi-gigabyte datasets (such as the 825 GB Pile corpus) into memory causes out-of-memory errors. The solution introduced is **dataset streaming** (`streaming=True`), which allows processing examples iteratively on the fly without downloading or loading the entire corpus into RAM.

This lab implements a minimal, complete local concept example of **streaming aggregation** over JSONL records:
- Evaluates lines from an iterable stream one record at a time.
- Aggregates category counts into a bounded in-memory dictionary.
- Reports malformed lines along with their 1-indexed line numbers without crashing the stream.
- Operates deterministically using only the Python standard library.

## Public Input/Output Contract
- **Input**: An `Iterable[str]` emitting JSONL lines one at a time.
- **Contract Cases**:
  - `A, B, A, C` yields category counts `{"A": 2, "B": 1, "C": 1}`.
  - An empty input stream yields `{}`.
  - A malformed line is caught and recorded with its 1-indexed line number.

### Exact Boundary Decisions
1. **Empty Stream**:
   - Input: `[]`
   - Outcome: `category_counts = {}`, `malformed_records = []`, `total_lines_processed = 0`.
2. **Whitespace / Blank Lines**:
   - Blank or whitespace-only lines are treated as blank spacing and skipped cleanly (not counted as malformed errors).
3. **Smallest Valid Record**:
   - Single valid line `{"category": "X"}` produces `{"X": 1}`.
4. **Invalid JSON Syntax**:
   - Lines with invalid JSON syntax (e.g., `{bad json`) are caught via `json.JSONDecodeError` and reported with the 1-based line number.
5. **Schema Violations**:
   - Non-dictionary JSON or missing `category` key or empty category string are captured and reported with line numbers.

## Teaching Approximation & Scope
- **Pure Local Simulation**: Implemented with pure Python standard library (`json`, `dataclasses`, `typing`).
- **No Heavy Dependencies**: No downloads of the Pile, no external libraries (such as `zstandard` or Hugging Face `datasets`), no network access, and no GPU or physical hardware are required.
- **Hardware Neutral**: The example makes no unsupported claims regarding physical disk speed or cloud performance.

## Running the Lab Locally

### Run Example Script
```bash
python3 chapters/en/chapter5/applied-labs/r16-t042/example.py
```

### Run Automated Unit Tests
```bash
python3 -m unittest discover -s chapters/en/chapter5/applied-labs/r16-t042 -p "test_*.py" -v
```

### Run Verification & Checks
```bash
python3 work/R16-T042/check.py
```
