# R16-T008 evidence

Coursework evidence for the S-AI-Projects fork. Remove `work/R16-T008/` before
any upstream PR.

## Tool versions

- Python 3.14.7 (standard library only)
- Darwin 27.2.0

## Inputs and expected vs. actual

Geofence: lat [10, 20], lon [70, 80], edges included. This is a flat rectangle in degrees, not a spherical-distance model. The coordinates are made-up fixtures.

| Record | (lat, lon) | Expected | Actual |
|---|---|---|---|
| r1-centre | (15, 75) | inside | inside |
| r2-corner | (10, 70) | inside (boundary) | inside |
| r3-north | (21, 75) | outside | outside |
| r4-bad-lat | (100, 75) | rejected: `lat 100 is outside the valid range [-90, 90]` | same |
| r5-recovery | (19.5, 79.9) | inside (processed after the failure) | inside |
| r6-no-lon | (12, None) | rejected: `lon is missing` | same |
| r7-far-corner | (20, 80) | inside (boundary) | inside |
| swapped order | (75, 15) | outside | outside (test) |

## Example run

Command (from the repo root): `python3 chapters/en/chapter5/applied-labs/r16-t008/example.py`

```
Geofence: lat [10, 20], lon [70, 80], edges included
Flat rectangle in degrees - NOT a spherical-distance model.

r1-centre      lat=15    lon=75    -> inside
r2-corner      lat=10    lon=70    -> inside
r3-north       lat=21    lon=75    -> outside
r4-bad-lat     lat=100   lon=75    -> rejected  (lat 100 is outside the valid range [-90, 90])
r5-recovery    lat=19.5  lon=79.9  -> inside
r6-no-lon      lat=12    lon=None  -> rejected  (lon is missing)
r7-far-corner  lat=20    lon=80    -> inside

inside the geofence: ['r1-centre', 'r2-corner', 'r5-recovery', 'r7-far-corner']
```

Exit code: 0

## Test run (passing)

Command: `python3 -m unittest discover -s chapters/en/chapter5/applied-labs/r16-t008 -p "test_*.py" -v`

```
test_every_edge_and_corner_is_inside (test_example.Boundaries.test_every_edge_and_corner_is_inside) ... ok
test_just_outside_each_edge (test_example.Boundaries.test_just_outside_each_edge) ... ok
test_swapped_order_gives_a_different_answer (test_example.Boundaries.test_swapped_order_gives_a_different_answer) ... ok
test_valid_extremes_are_accepted (test_example.Boundaries.test_valid_extremes_are_accepted) ... ok
test_every_record_gets_a_result (test_example.FailureAndRecovery.test_every_record_gets_a_result) ... ok
test_fixture_statuses (test_example.FailureAndRecovery.test_fixture_statuses) ... ok
test_other_invalid_values_are_rejected (test_example.FailureAndRecovery.test_other_invalid_values_are_rejected) ... ok
test_record_after_an_invalid_one_is_still_classified (test_example.FailureAndRecovery.test_record_after_an_invalid_one_is_still_classified) ... ok
test_rejection_reasons_explain_the_error (test_example.FailureAndRecovery.test_rejection_reasons_explain_the_error) ... ok
test_boundary_corner_is_inside (test_example.TaskContract.test_boundary_corner_is_inside) ... ok
test_centre_is_inside (test_example.TaskContract.test_centre_is_inside) ... ok
test_latitude_100_is_rejected (test_example.TaskContract.test_latitude_100_is_rejected) ... ok
test_north_of_box_is_outside (test_example.TaskContract.test_north_of_box_is_outside) ... ok

----------------------------------------------------------------------
Ran 13 tests in 0.001s

OK
```

Exit code: 0. Ran 13 tests in 0.001s.

## Deliberate wrong result (test must fail)

In a throwaway copy of the lab, I changed one line in `example.py`:

```diff
- return LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX
+ return LAT_MIN < lat <= LAT_MAX and LON_MIN < lon <= LON_MAX
```

Running the same test command against that copy:

```
FAIL: test_every_edge_and_corner_is_inside  (x5 subtests)
FAIL: test_fixture_statuses
FAIL: test_boundary_corner_is_inside

Ran 13 tests in 0.003s
FAILED (failures=7)
```

Exit code: 1. The tests catch the wrong result. The committed code was not changed.
