"""Tests for example.py. Run from the repository root with:

    python3 -m unittest discover -s chapters/en/chapter5/applied-labs/r16-t008 -p "test_*.py"
"""

import unittest

from example import RECORDS, classify_records, in_geofence


def point(lat, lon):
    return {"lat": lat, "lon": lon}


class TaskContract(unittest.TestCase):
    def test_centre_is_inside(self):
        self.assertTrue(in_geofence(point(15, 75)))

    def test_boundary_corner_is_inside(self):
        self.assertTrue(in_geofence(point(10, 70)))

    def test_north_of_box_is_outside(self):
        self.assertFalse(in_geofence(point(21, 75)))

    def test_latitude_100_is_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            in_geofence(point(100, 75))
        self.assertIn("lat 100 is outside the valid range [-90, 90]", str(ctx.exception))


class Boundaries(unittest.TestCase):
    def test_every_edge_and_corner_is_inside(self):
        for lat, lon in [(10, 70), (10, 80), (20, 70), (20, 80), (10, 75), (20, 75), (15, 70), (15, 80)]:
            with self.subTest(lat=lat, lon=lon):
                self.assertTrue(in_geofence(point(lat, lon)))

    def test_just_outside_each_edge(self):
        for lat, lon in [(9.999, 75), (20.001, 75), (15, 69.999), (15, 80.001)]:
            with self.subTest(lat=lat, lon=lon):
                self.assertFalse(in_geofence(point(lat, lon)))

    def test_swapped_order_gives_a_different_answer(self):
        # (15, 75) read the wrong way round is lat=75, lon=15: valid, but far outside.
        self.assertTrue(in_geofence(point(15, 75)))
        self.assertFalse(in_geofence(point(75, 15)))

    def test_valid_extremes_are_accepted(self):
        self.assertFalse(in_geofence(point(-90, -180)))
        self.assertFalse(in_geofence(point(90, 180)))


class FailureAndRecovery(unittest.TestCase):
    def test_fixture_statuses(self):
        statuses = {r["id"]: r["status"] for r in classify_records(RECORDS)}
        self.assertEqual(statuses, {
            "r1-centre": "inside",
            "r2-corner": "inside",
            "r3-north": "outside",
            "r4-bad-lat": "rejected",
            "r5-recovery": "inside",
            "r6-no-lon": "rejected",
            "r7-far-corner": "inside",
        })

    def test_record_after_an_invalid_one_is_still_classified(self):
        results = classify_records(RECORDS)
        ids = [r["id"] for r in results]
        bad = ids.index("r4-bad-lat")
        self.assertEqual(results[bad]["status"], "rejected")
        self.assertEqual(results[bad + 1], {"id": "r5-recovery", "status": "inside", "reason": ""})

    def test_every_record_gets_a_result(self):
        self.assertEqual(len(classify_records(RECORDS)), len(RECORDS))

    def test_rejection_reasons_explain_the_error(self):
        reasons = {r["id"]: r["reason"] for r in classify_records(RECORDS) if r["status"] == "rejected"}
        self.assertEqual(reasons, {
            "r4-bad-lat": "lat 100 is outside the valid range [-90, 90]",
            "r6-no-lon": "lon is missing",
        })

    def test_other_invalid_values_are_rejected(self):
        for bad in [point("15", 75), point(15, True), point(15, 200), {"lat": 15}]:
            with self.subTest(record=bad), self.assertRaises(ValueError):
                in_geofence(bad)


if __name__ == "__main__":
    unittest.main()
