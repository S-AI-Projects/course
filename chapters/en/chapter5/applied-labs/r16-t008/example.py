"""R16-T008: rectangular geofence filter with failure and recovery (simulation).

Companion to the chapter 5 "End-of-chapter quiz" (chapters/en/chapter5/8.mdx).
Question 3 filters a dataset with a predicate, e.g.
`pets_dataset.filter(lambda x: x["name"].startswith("L"))`. This lab writes a
predicate of the same shape for coordinate records and runs it over a small
local list (no 🤗 Datasets install needed).

Teaching geofence (inclusive on every edge):
    latitude  in [10, 20]
    longitude in [70, 80]

Coordinate order: records use named keys {"lat": ..., "lon": ...}, so latitude
and longitude cannot be swapped silently. (15, 75) in the task means lat=15, lon=75.

Failure and recovery: `classify_records` checks each record on its own. An
invalid record (latitude outside [-90, 90], longitude outside [-180, 180],
missing or non-numeric values) is marked "rejected" with the reason, and
processing continues with the next record.

NOT A SPHERICAL-DISTANCE MODEL: this is a flat rectangle in degrees. It does
not compute distances on the Earth's surface, and it does not handle boxes
that cross the 180° meridian or reach the poles. The coordinates are made-up
fixtures, not real locations or GPS readings.
"""

from numbers import Real

LAT_MIN, LAT_MAX = 10, 20
LON_MIN, LON_MAX = 70, 80

RECORDS = [
    {"id": "r1-centre", "lat": 15, "lon": 75},
    {"id": "r2-corner", "lat": 10, "lon": 70},
    {"id": "r3-north", "lat": 21, "lon": 75},
    {"id": "r4-bad-lat", "lat": 100, "lon": 75},
    {"id": "r5-recovery", "lat": 19.5, "lon": 79.9},
    {"id": "r6-no-lon", "lat": 12, "lon": None},
    {"id": "r7-far-corner", "lat": 20, "lon": 80},
]


def _coordinate(record, key, low, high):
    value = record.get(key)
    if value is None:
        raise ValueError(f"{key} is missing")
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{key} must be a number, got {value!r}")
    if not low <= value <= high:
        raise ValueError(f"{key} {value} is outside the valid range [{low}, {high}]")
    return value


def in_geofence(record):
    """Predicate (like a Dataset.filter function): True if inside the box.

    Raises ValueError for an invalid record.
    """
    lat = _coordinate(record, "lat", -90, 90)
    lon = _coordinate(record, "lon", -180, 180)
    return LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX


def classify_records(records):
    """Classify every record. Never stops early; invalid records are reported."""
    results = []
    for record in records:
        try:
            status = "inside" if in_geofence(record) else "outside"
            reason = ""
        except ValueError as exc:
            status, reason = "rejected", str(exc)
        results.append({"id": record.get("id"), "status": status, "reason": reason})
    return results


if __name__ == "__main__":
    print(f"Geofence: lat [{LAT_MIN}, {LAT_MAX}], lon [{LON_MIN}, {LON_MAX}], edges included")
    print("Flat rectangle in degrees - NOT a spherical-distance model.\n")
    results = classify_records(RECORDS)
    for record, result in zip(RECORDS, results):
        line = f"{result['id']:14} lat={record['lat']!s:5} lon={record['lon']!s:5} -> {result['status']}"
        if result["reason"]:
            line += f"  ({result['reason']})"
        print(line)
    inside = [r["id"] for r in results if r["status"] == "inside"]
    print(f"\ninside the geofence: {inside}")
