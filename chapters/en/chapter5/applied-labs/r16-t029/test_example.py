"""
Unit and contract tests for Rectangular Geofence Membership and Evaluation Experiment.

Validates:
  1. (15, 75) is inside.
  2. Boundary (10, 70) is inside (inclusive).
  3. (21, 75) is outside.
  4. Invalid latitude 100 is rejected.
  5. Controlled evaluation compares 3 configurations with appropriate metrics and trade-off reporting.
  6. Deliberate failure triggers assertion error.
"""

from __future__ import annotations

import unittest

try:
    from .example import (
        POINT_BOUNDARY,
        POINT_INSIDE,
        POINT_INVALID,
        POINT_OUTSIDE,
        GeofenceResult,
        InvalidCoordinateError,
        RectangularGeofence,
        run_controlled_evaluation,
    )
except ImportError:
    from example import (
        POINT_BOUNDARY,
        POINT_INSIDE,
        POINT_INVALID,
        POINT_OUTSIDE,
        GeofenceResult,
        InvalidCoordinateError,
        RectangularGeofence,
        run_controlled_evaluation,
    )


class TestRectangularGeofence(unittest.TestCase):
    """Test suite verifying contract compliance, boundary inclusion, and error handling."""

    def setUp(self) -> None:
        self.geofence = RectangularGeofence(
            min_lat=10.0, max_lat=20.0, min_lon=70.0, max_lon=80.0
        )

    def test_point_inside(self) -> None:
        """Verify (15, 75) is inside the geofence."""
        self.assertTrue(self.geofence.contains(POINT_INSIDE[0], POINT_INSIDE[1]))
        res = self.geofence.classify_point(POINT_INSIDE[0], POINT_INSIDE[1])
        self.assertEqual(res.status, "INSIDE")
        self.assertTrue(res.is_inside)

    def test_boundary_inclusion(self) -> None:
        """Verify boundary points such as (10, 70) and (20, 80) are classified as inside."""
        # Lower corner
        self.assertTrue(self.geofence.contains(POINT_BOUNDARY[0], POINT_BOUNDARY[1]))
        res_lower = self.geofence.classify_point(POINT_BOUNDARY[0], POINT_BOUNDARY[1])
        self.assertEqual(res_lower.status, "INSIDE")

        # Upper corner
        self.assertTrue(self.geofence.contains(20.0, 80.0))
        # Edge boundaries
        self.assertTrue(self.geofence.contains(10.0, 75.0))
        self.assertTrue(self.geofence.contains(20.0, 75.0))
        self.assertTrue(self.geofence.contains(15.0, 70.0))
        self.assertTrue(self.geofence.contains(15.0, 80.0))

    def test_point_outside(self) -> None:
        """Verify points outside the rectangular fence are classified as outside."""
        self.assertFalse(self.geofence.contains(POINT_OUTSIDE[0], POINT_OUTSIDE[1]))
        res = self.geofence.classify_point(POINT_OUTSIDE[0], POINT_OUTSIDE[1])
        self.assertEqual(res.status, "OUTSIDE")
        self.assertFalse(res.is_inside)

        # Points just beyond boundaries
        self.assertFalse(self.geofence.contains(9.9999, 75.0))
        self.assertFalse(self.geofence.contains(20.0001, 75.0))
        self.assertFalse(self.geofence.contains(15.0, 69.9999))
        self.assertFalse(self.geofence.contains(15.0, 80.0001))

    def test_invalid_latitude_rejected(self) -> None:
        """Verify invalid latitude (e.g., 100.0 or -95.0) raises InvalidCoordinateError."""
        with self.assertRaises(InvalidCoordinateError) as ctx:
            self.geofence.contains(POINT_INVALID[0], POINT_INVALID[1])
        self.assertIn("must be within [-90.0, 90.0]", str(ctx.exception))

        with self.assertRaises(InvalidCoordinateError):
            self.geofence.contains(-95.0, 75.0)

    def test_invalid_longitude_rejected(self) -> None:
        """Verify invalid longitude (e.g., 185.0 or -190.0) raises InvalidCoordinateError."""
        with self.assertRaises(InvalidCoordinateError) as ctx:
            self.geofence.contains(15.0, 185.0)
        self.assertIn("must be within [-180.0, 180.0]", str(ctx.exception))

        with self.assertRaises(InvalidCoordinateError):
            self.geofence.contains(15.0, -190.0)

    def test_non_numeric_coordinates_rejected(self) -> None:
        """Verify non-numeric input types raise InvalidCoordinateError."""
        with self.assertRaises(InvalidCoordinateError):
            self.geofence.contains("invalid_lat", 75.0)

    def test_safe_classification_mode(self) -> None:
        """Verify safe mode captures invalid coordinates without raising."""
        res = self.geofence.classify_point(100.0, 75.0, safe=True)
        self.assertEqual(res.status, "INVALID")
        self.assertIsNone(res.is_inside)
        self.assertIsNotNone(res.error_message)

    def test_batch_classification(self) -> None:
        """Verify classification of mixed records (tuples and dicts)."""
        batch = [
            (15.0, 75.0),
            {"lat": 10.0, "lon": 70.0},
            (21.0, 75.0),
            {"lat": 100.0, "lon": 75.0},
        ]
        results = self.geofence.classify_batch(batch, safe=True)
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0].status, "INSIDE")
        self.assertEqual(results[1].status, "INSIDE")
        self.assertEqual(results[2].status, "OUTSIDE")
        self.assertEqual(results[3].status, "INVALID")

    def test_controlled_evaluation_three_configurations(self) -> None:
        """Verify that 3 controlled configurations are evaluated with accuracy and throughput trade-offs."""
        report = run_controlled_evaluation()
        self.assertIn("configurations", report)
        configs = report["configurations"]
        self.assertEqual(len(configs), 3)

        sizes = [c["sample_size"] for c in configs]
        self.assertEqual(sizes, [5, 25, 100])

        for c in configs:
            self.assertEqual(c["accuracy_pct"], 100.0)
            self.assertGreater(c["throughput_rec_per_sec"], 0)
            self.assertGreaterEqual(c["inside_count"], 0)
            self.assertGreaterEqual(c["outside_count"], 0)
            self.assertGreaterEqual(c["invalid_rejected_count"], 0)

    def test_deliberate_wrong_result_fails(self) -> None:
        """Verify that deliberate incorrect assertions trigger failure."""
        with self.assertRaises(AssertionError):
            # Deliberate wrong check: claiming outside point is inside
            self.assertTrue(self.geofence.contains(POINT_OUTSIDE[0], POINT_OUTSIDE[1]))

        with self.assertRaises(AssertionError):
            # Deliberate wrong check: claiming inside point is outside
            self.assertFalse(self.geofence.contains(POINT_INSIDE[0], POINT_INSIDE[1]))


if __name__ == "__main__":
    unittest.main()
