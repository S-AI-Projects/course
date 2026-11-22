# Applied Lab R16-T048: Chronological Evaluation Split (Failure and Recovery Example)

## Related Lesson
- **Chapter**: Chapter 2: Using 🤗 Transformers
- **Section**: [Putting it all together (`putting-it-all-together`)](../../6.mdx)

## Objective & Focus
In Chapter 2, Section 6, end-to-end tokenization and modeling workflows are unified. In realistic production ML evaluation, datasets frequently contain temporal properties. Random shuffling causes future data leakage into training folds.

This applied lab demonstrates:
1. Chronological splitting of timestamped records into the earliest 60% (train), next 20% (validation), and latest 20% (test).
2. Automatic sorting of shuffled inputs prior to splitting.
3. Strict timestamp uniqueness validation to prevent ambiguous temporal order.
4. **Failure and Recovery**: Exercising a documented invalid case (duplicate timestamps), explaining the error, and demonstrating immediate clean recovery on the next valid batch.

## Public Input/Output Contract
- **Input**: List of observation dictionaries with non-negative, unique `timestamp` keys.
- **Contract Test Case**:
  - 10 ordered/shuffled observations yield exactly **6 train**, **2 validation**, and **2 test** observations.
  - Future observations strictly remain out of training (`max(train.timestamp) < min(validation.timestamp) < min(test.timestamp)`).
  - Shuffled input is sorted chronologically before partitioning.
  - Duplicate timestamps are rejected with `ValueError`.
  - Missing timestamps are rejected with `KeyError`.

## Scope & Limitations
- **Pure Local Fixture**: Implemented purely using Python standard library.
- **No External Dependencies**: Requires no model weights, paid cloud services, GPU hardware, or external dataset downloads.
- **Hardware Neutral**: Focuses on evaluation partitioning logic without hardware performance assertions.

## Running the Lab Locally

### Run Example Script
```bash
python3 chapters/en/chapter2/applied-labs/r16-t048/example.py
```

### Run Automated Unit Tests
```bash
python3 -m unittest discover -s chapters/en/chapter2/applied-labs/r16-t048 -p "test_*.py" -v
```

### Run Verification & Checks
```bash
python3 work/R16-T048/check.py
```
