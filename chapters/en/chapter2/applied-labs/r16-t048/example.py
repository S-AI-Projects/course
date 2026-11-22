#!/usr/bin/env python3
"""
Applied Lab R16-T048: Chronological Evaluation Split — Failure and Recovery Example.

This module implements a chronological evaluation split for timestamped observations,
connecting directly to Chapter 2, Section 6 ("Putting it all together" [putting-it-all-together]).

Lesson Context:
In end-to-end model evaluation pipelines (when "putting it all together"), real-world
data often arrives with temporal dependencies (e.g. news articles, log sequences, time series).
Randomly splitting temporal data creates data leakage (training on future information to
predict the past). A chronological evaluation split enforces temporal ordering:
- Sorts shuffled input chronologically by timestamp.
- Validates that timestamps are strictly unique (rejects duplicates to prevent ambiguous splits).
- Splits observations into earliest 60% (train), next 20% (validation), and latest 20% (test).
- Ensures future observations are never leaked into the training set.

Failure and Recovery Focus:
- Evaluates documented invalid/missing-data cases (e.g. duplicate timestamps, missing timestamps).
- Explains the exact failure reasons.
- Demonstrates immediate, clean recovery on the next valid input sequence.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union


@dataclass(frozen=True)
class Observation:
    """Represents a timestamped data observation."""

    timestamp: Union[int, float]
    data: Any

    def as_dict(self) -> Dict[str, Any]:
        return {"timestamp": self.timestamp, "data": self.data}


@dataclass
class SplitResult:
    """Holds train, validation, and test observation partitions."""

    train: List[Observation]
    validation: List[Observation]
    test: List[Observation]
    total_count: int

    def as_dict(self) -> Dict[str, Any]:
        return {
            "train": [o.as_dict() for o in self.train],
            "validation": [o.as_dict() for o in self.validation],
            "test": [o.as_dict() for o in self.test],
            "total_count": self.total_count,
            "train_count": len(self.train),
            "val_count": len(self.validation),
            "test_count": len(self.test),
        }


def chronological_split(
    observations: List[Dict[str, Any]],
    train_ratio: float = 0.6,
    val_ratio: float = 0.2,
    test_ratio: float = 0.2,
) -> SplitResult:
    """Split timestamped observations chronologically into train, validation, and test sets.

    Validates:
    - Input is a non-empty list of dicts with 'timestamp'.
    - Timestamps are strictly unique (duplicate timestamps raise ValueError).
    - Shuffled inputs are sorted in strictly ascending chronological order.
    - Future observations remain out of training (max(train.timestamp) < min(val.timestamp) < min(test.timestamp)).

    Ratios:
    - 10 observations yield exactly 6 train, 2 validation, 2 test.
    """
    if not isinstance(observations, list):
        raise TypeError(f"observations must be a list, got {type(observations).__name__}")
    if not observations:
        raise ValueError("observations list cannot be empty")

    parsed: List[Observation] = []
    seen_timestamps = set()

    for idx, obs in enumerate(observations):
        if not isinstance(obs, dict):
            raise TypeError(f"Item at index {idx} must be a dict, got {type(obs).__name__}")
        if "timestamp" not in obs or obs["timestamp"] is None:
            raise KeyError(f"Item at index {idx} is missing required 'timestamp' field")

        ts = obs["timestamp"]
        if not isinstance(ts, (int, float)) or isinstance(ts, bool):
            raise TypeError(f"Timestamp at index {idx} must be int or float, got {type(ts).__name__}")

        if ts in seen_timestamps:
            raise ValueError(f"Duplicate timestamp detected: {ts}. Timestamps must be strictly unique.")
        seen_timestamps.add(ts)

        parsed.append(Observation(timestamp=ts, data=obs.get("data", obs)))

    # Sort strictly by timestamp in ascending order
    sorted_obs = sorted(parsed, key=lambda o: o.timestamp)
    n = len(sorted_obs)

    train_count = round(n * train_ratio)
    val_count = round(n * val_ratio)
    # Remaining goes to test to guarantee sum == n
    test_count = n - (train_count + val_count)

    train_set = sorted_obs[:train_count]
    val_set = sorted_obs[train_count : train_count + val_count]
    test_set = sorted_obs[train_count + val_count :]

    return SplitResult(
        train=train_set,
        validation=val_set,
        test=test_set,
        total_count=n,
    )


# ==============================================================================
# Failure and Recovery Pipeline Demonstration
# ==============================================================================
def process_observation_batches(
    batches: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Process a sequence of batches, recording failure details and demonstrating subsequent recovery."""
    history = []

    for batch in batches:
        batch_id = batch["batch_id"]
        obs_list = batch["observations"]

        try:
            split_res = chronological_split(obs_list)
            history.append({
                "batch_id": batch_id,
                "status": "SUCCESS",
                "train_count": len(split_res.train),
                "val_count": len(split_res.validation),
                "test_count": len(split_res.test),
                "total_count": split_res.total_count,
                "error": None,
            })
        except Exception as e:
            history.append({
                "batch_id": batch_id,
                "status": "FAILED",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "train_count": 0,
                "val_count": 0,
                "test_count": 0,
                "total_count": len(obs_list) if isinstance(obs_list, list) else 0,
            })

    return history


if __name__ == "__main__":
    print("=== Chronological Evaluation Split & Recovery (R16-T048) ===")

    # 10 shuffled observations
    ten_obs_shuffled = [
        {"timestamp": 10, "data": "obs_10"},
        {"timestamp": 2, "data": "obs_02"},
        {"timestamp": 8, "data": "obs_08"},
        {"timestamp": 1, "data": "obs_01"},
        {"timestamp": 4, "data": "obs_04"},
        {"timestamp": 7, "data": "obs_07"},
        {"timestamp": 3, "data": "obs_03"},
        {"timestamp": 9, "data": "obs_09"},
        {"timestamp": 5, "data": "obs_05"},
        {"timestamp": 6, "data": "obs_06"},
    ]

    res = chronological_split(ten_obs_shuffled)
    print("Split Results for 10 observations:")
    print(f"  Train ({len(res.train)}): {[o.timestamp for o in res.train]}")
    print(f"  Val   ({len(res.validation)}): {[o.timestamp for o in res.validation]}")
    print(f"  Test  ({len(res.test)}): {[o.timestamp for o in res.test]}\n")

    # Failure and Recovery
    demo_batches = [
        {"batch_id": "batch_1_valid", "observations": ten_obs_shuffled},
        {"batch_id": "batch_2_duplicate_error", "observations": [{"timestamp": 1}, {"timestamp": 1}]},
        {"batch_id": "batch_3_recovered_valid", "observations": [{"timestamp": 100}, {"timestamp": 200}, {"timestamp": 300}, {"timestamp": 400}, {"timestamp": 500}, {"timestamp": 600}, {"timestamp": 700}, {"timestamp": 800}, {"timestamp": 900}, {"timestamp": 1000}]},
    ]

    print("Pipeline Execution with Failure & Recovery:")
    history = process_observation_batches(demo_batches)
    for h in history:
        print(f"  [{h['status']}] {h['batch_id']}: Error={h['error_type']} | Train={h['train_count']}")
