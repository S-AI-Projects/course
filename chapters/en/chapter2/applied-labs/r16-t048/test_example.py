"""Unit tests for Applied Lab R16-T048: Chronological Evaluation Split & Recovery."""

import os
import sys
import unittest

LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from example import (
    Observation,
    SplitResult,
    chronological_split,
    process_observation_batches,
)


class TestChronologicalSplit(unittest.TestCase):
    """Test suite validating chronological evaluation split and recovery contract."""

    def test_ten_ordered_observations_yield_6_train_2_val_2_test(self):
        """Ten ordered observations yield 6 train, 2 validation, 2 test."""
        obs = [{"timestamp": i, "val": f"val_{i}"} for i in range(1, 11)]
        res = chronological_split(obs)

        self.assertEqual(len(res.train), 6)
        self.assertEqual(len(res.validation), 2)
        self.assertEqual(len(res.test), 2)
        self.assertEqual([o.timestamp for o in res.train], [1, 2, 3, 4, 5, 6])
        self.assertEqual([o.timestamp for o in res.validation], [7, 8])
        self.assertEqual([o.timestamp for o in res.test], [9, 10])

    def test_shuffled_input_is_sorted_first(self):
        """Shuffled input is sorted before partitioning."""
        shuffled = [
            {"timestamp": 10},
            {"timestamp": 3},
            {"timestamp": 1},
            {"timestamp": 7},
            {"timestamp": 4},
            {"timestamp": 9},
            {"timestamp": 2},
            {"timestamp": 8},
            {"timestamp": 5},
            {"timestamp": 6},
        ]
        res = chronological_split(shuffled)
        self.assertEqual([o.timestamp for o in res.train], [1, 2, 3, 4, 5, 6])
        self.assertEqual([o.timestamp for o in res.validation], [7, 8])
        self.assertEqual([o.timestamp for o in res.test], [9, 10])

    def test_future_observations_remain_out_of_training(self):
        """Strict temporal boundary: max(train.timestamp) < min(validation.timestamp) < min(test.timestamp)."""
        obs = [{"timestamp": i * 10} for i in range(1, 11)]
        res = chronological_split(obs)

        max_train = max(o.timestamp for o in res.train)
        min_val = min(o.timestamp for o in res.validation)
        max_val = max(o.timestamp for o in res.validation)
        min_test = min(o.timestamp for o in res.test)

        self.assertLess(max_train, min_val)
        self.assertLess(max_val, min_test)

    def test_duplicate_timestamps_are_rejected(self):
        """Duplicate timestamps raise ValueError to prevent ambiguous ordering."""
        duplicates = [
            {"timestamp": 1},
            {"timestamp": 2},
            {"timestamp": 2},  # duplicate
            {"timestamp": 3},
        ]
        with self.assertRaises(ValueError):
            chronological_split(duplicates)

    def test_missing_timestamp_rejected(self):
        """Observation missing 'timestamp' key raises KeyError."""
        invalid_obs = [
            {"timestamp": 1},
            {"wrong_key": 2},
        ]
        with self.assertRaises(KeyError):
            chronological_split(invalid_obs)

    def test_failure_and_recovery_across_batches(self):
        """Exercise documented invalid data case, explain error, and demonstrate recovery on next valid input."""
        batches = [
            {
                "batch_id": "valid_batch_1",
                "observations": [{"timestamp": i} for i in range(1, 11)],
            },
            {
                "batch_id": "invalid_duplicate_batch",
                "observations": [{"timestamp": 5}, {"timestamp": 5}],
            },
            {
                "batch_id": "recovered_valid_batch",
                "observations": [{"timestamp": i * 100} for i in range(1, 11)],
            },
        ]

        history = process_observation_batches(batches)
        self.assertEqual(len(history), 3)

        # Batch 1 succeeded
        self.assertEqual(history[0]["status"], "SUCCESS")
        self.assertEqual(history[0]["train_count"], 6)

        # Batch 2 failed gracefully with documented ValueError
        self.assertEqual(history[1]["status"], "FAILED")
        self.assertEqual(history[1]["error_type"], "ValueError")
        self.assertIn("Duplicate timestamp detected", history[1]["error_message"])

        # Batch 3 cleanly recovered
        self.assertEqual(history[2]["status"], "SUCCESS")
        self.assertEqual(history[2]["train_count"], 6)
        self.assertEqual(history[2]["error"], None)

    def test_deliberate_wrong_result_fails(self):
        """Demonstrate that an intentional wrong result makes the test fail."""
        obs = [{"timestamp": i} for i in range(1, 11)]
        res = chronological_split(obs)
        wrong_train_count = 99
        with self.assertRaises(AssertionError):
            self.assertEqual(len(res.train), wrong_train_count)


if __name__ == "__main__":
    unittest.main()
