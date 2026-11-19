# R16-T008: Geofence membership, failure and recovery

A small, standard-library-only example for the chapter 5
[End-of-chapter quiz](../../8.mdx). Question 3 filters a dataset with a
function, as in `pets_dataset.filter(lambda x: x["name"].startswith("L"))`.
This lab writes a function of the same shape, `in_geofence(record)`, for
coordinate records and runs it over a small local list. 🤗 Datasets is not needed.

> **Not a spherical-distance model.** The geofence is a flat rectangle in
> degrees. It does not measure distances on the Earth's surface, and it does
> not handle boxes that cross the 180° meridian or reach the poles. All
> coordinates are made-up fixtures, not real locations.

## The geofence

| Axis | Range | Edges |
|---|---|---|
| latitude (`lat`) | [10, 20] | included |
| longitude (`lon`) | [70, 80] | included |

**Coordinate order:** records use named keys, `{"lat": 15, "lon": 75}`, so the
two values can't be swapped by accident. The task's `(15, 75)` means
lat=15, lon=75. A test shows that the swapped pair `(75, 15)` gives a
different answer: it is a valid point, but far outside the box.

## Fixture and results

| Record | lat | lon | Status | Why |
|---|---|---|---|---|
| r1-centre | 15 | 75 | inside | middle of the box |
| r2-corner | 10 | 70 | inside | corner, and edges are included |
| r3-north | 21 | 75 | outside | 1° north of the box |
| r4-bad-lat | 100 | 75 | **rejected** | latitude must be in [-90, 90] |
| r5-recovery | 19.5 | 79.9 | inside | the next valid record is processed normally |
| r6-no-lon | 12 | None | **rejected** | longitude is missing |
| r7-far-corner | 20 | 80 | inside | opposite corner |

## Failure and recovery

`in_geofence` raises `ValueError` with a clear reason when a record can't be
judged: a latitude outside [-90, 90], a longitude outside [-180, 180], or a
missing, non-numeric or `bool` value.

`classify_records` checks **each record on its own**. When a record fails, it
is marked `rejected`, the error message is kept as its `reason`, and the loop
moves on. One bad row does not stop the batch or affect the records after it.
In the fixture, `r4-bad-lat` is rejected and the very next record,
`r5-recovery`, is still classified `inside`.

## Run it

From the repository root (Python 3, no extra packages):

```bash
python3 chapters/en/chapter5/applied-labs/r16-t008/example.py
```

Expected output:

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

Tests:

```bash
python3 -m unittest discover -s chapters/en/chapter5/applied-labs/r16-t008 -p "test_*.py"
```

Expected: `Ran 13 tests ... OK`, exit code 0.

## Limitations

- A flat lat/lon rectangle, not a spherical-distance or polygon geofence.
- No real GPS data, device or mapping service is used.
- With 🤗 Datasets you would remove or mark invalid rows before calling
  `Dataset.filter(in_geofence)`, because the function raises an error on bad
  rows. That step is not shown here.
