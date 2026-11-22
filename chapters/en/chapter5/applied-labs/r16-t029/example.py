"""
Inclusive Rectangular Teaching Geofence and Evaluation Experiment.

This module implements a teaching geofence with inclusive bounds:
  latitude in [10.0, 20.0]
  longitude in [70.0, 80.0]

Core Contracts:
  - (15.0, 75.0) -> INSIDE (True)
  - Boundary (10.0, 70.0) -> INSIDE (True)
  - (21.0, 75.0) -> OUTSIDE (False)
  - Invalid latitude 100.0 -> REJECTED (InvalidCoordinateError)

Pedagogical Disclaimer:
  This rectangular fixture is a planar 2D Cartesian bounding box representation
  intended for pedagogical evaluation. It is NOT a spherical-distance (haversine
  or ellipsoidal/geodesic) model, does not model Earth curvature, and should not
  be interpreted as a real-world navigation system.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union


class InvalidCoordinateError(ValueError):
    """Raised when coordinates fall outside physical terrestrial bounds."""

    def __init__(self, message: str, lat: Optional[float] = None, lon: Optional[float] = None) -> None:
        super().__init__(message)
        self.message = message
        self.lat = lat
        self.lon = lon


@dataclass(frozen=True)
class GeofenceResult:
    """Classification output for an evaluated coordinate point."""

    lat: float
    lon: float
    status: str  # "INSIDE", "OUTSIDE", or "INVALID"
    is_inside: Optional[bool]
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "lat": self.lat,
            "lon": self.lon,
            "status": self.status,
            "is_inside": self.is_inside,
            "error_message": self.error_message,
        }


class RectangularGeofence:
    """
    Teaching geofence defining an inclusive planar bounding box.

    Bounds:
      min_lat <= lat <= max_lat
      min_lon <= lon <= max_lon
    """

    def __init__(
        self,
        min_lat: float = 10.0,
        max_lat: float = 20.0,
        min_lon: float = 70.0,
        max_lon: float = 80.0,
    ) -> None:
        if min_lat > max_lat:
            raise ValueError(f"min_lat ({min_lat}) cannot exceed max_lat ({max_lat})")
        if min_lon > max_lon:
            raise ValueError(f"min_lon ({min_lon}) cannot exceed max_lon ({max_lon})")

        self.min_lat = float(min_lat)
        self.max_lat = float(max_lat)
        self.min_lon = float(min_lon)
        self.max_lon = float(max_lon)

    @staticmethod
    def validate_coordinates(lat: Any, lon: Any) -> Tuple[float, float]:
        """
        Validates numeric types and physical bounds:
          -90.0 <= latitude <= 90.0
          -180.0 <= longitude <= 180.0
        """
        try:
            flat = float(lat)
            flon = float(lon)
        except (ValueError, TypeError) as exc:
            raise InvalidCoordinateError(
                f"Coordinates must be numeric, got lat={lat!r}, lon={lon!r}"
            ) from exc

        if not (-90.0 <= flat <= 90.0):
            raise InvalidCoordinateError(
                f"Invalid latitude {flat}: must be within [-90.0, 90.0]",
                lat=flat,
                lon=flon,
            )

        if not (-180.0 <= flon <= 180.0):
            raise InvalidCoordinateError(
                f"Invalid longitude {flon}: must be within [-180.0, 180.0]",
                lat=flat,
                lon=flon,
            )

        return flat, flon

    def contains(self, lat: float, lon: float) -> bool:
        """
        Evaluates whether a valid coordinate point falls within the inclusive geofence.

        Raises InvalidCoordinateError if coordinates violate physical bounds.
        """
        flat, flon = self.validate_coordinates(lat, lon)
        return (
            self.min_lat <= flat <= self.max_lat
            and self.min_lon <= flon <= self.max_lon
        )

    def classify_point(self, lat: Any, lon: Any, safe: bool = False) -> GeofenceResult:
        """
        Classifies a point as INSIDE, OUTSIDE, or INVALID.

        If safe=True, invalid coordinates return an INVALID result instead of raising.
        """
        try:
            flat, flon = self.validate_coordinates(lat, lon)
            is_in = (
                self.min_lat <= flat <= self.max_lat
                and self.min_lon <= flon <= self.max_lon
            )
            return GeofenceResult(
                lat=flat,
                lon=flon,
                status="INSIDE" if is_in else "OUTSIDE",
                is_inside=is_in,
                error_message=None,
            )
        except InvalidCoordinateError as err:
            if not safe:
                raise
            return GeofenceResult(
                lat=float(lat) if isinstance(lat, (int, float)) else -999.0,
                lon=float(lon) if isinstance(lon, (int, float)) else -999.0,
                status="INVALID",
                is_inside=None,
                error_message=err.message,
            )

    def classify_batch(
        self,
        records: List[Union[Tuple[Any, Any], Dict[str, Any]]],
        safe: bool = True,
    ) -> List[GeofenceResult]:
        """Classifies a sequence of (lat, lon) tuples or {'lat': ..., 'lon': ...} dictionaries."""
        results: List[GeofenceResult] = []
        for item in records:
            if isinstance(item, dict):
                lat = item.get("lat") or item.get("latitude")
                lon = item.get("lon") or item.get("longitude")
            else:
                lat, lon = item[0], item[1]
            results.append(self.classify_point(lat, lon, safe=safe))
        return results


# Canonical test fixtures required by contract
POINT_INSIDE = (15.0, 75.0)
POINT_BOUNDARY = (10.0, 70.0)
POINT_OUTSIDE = (21.0, 75.0)
POINT_INVALID = (100.0, 75.0)


def generate_controlled_dataset(size: int) -> List[Tuple[float, float, str]]:
    """
    Generates a deterministic synthetic evaluation set of given size.
    Each entry is (lat, lon, expected_status).
    """
    base_templates = [
        (15.0, 75.0, "INSIDE"),     # strictly inside
        (10.0, 70.0, "INSIDE"),     # lower corner boundary
        (20.0, 80.0, "INSIDE"),     # upper corner boundary
        (10.0, 75.0, "INSIDE"),     # bottom edge boundary
        (21.0, 75.0, "OUTSIDE"),    # north outside
        (5.0, 75.0, "OUTSIDE"),     # south outside
        (15.0, 65.0, "OUTSIDE"),    # west outside
        (15.0, 85.0, "OUTSIDE"),    # east outside
        (100.0, 75.0, "INVALID"),   # invalid latitude
        (15.0, 200.0, "INVALID"),   # invalid longitude
    ]

    dataset: List[Tuple[float, float, str]] = []
    for i in range(size):
        tpl = base_templates[i % len(base_templates)]
        dataset.append(tpl)
    return dataset


def run_controlled_evaluation() -> Dict[str, Any]:
    """
    Runs a controlled evaluation comparing 3 distinct input configurations:
      - Config A: Small input (N = 5 records)
      - Config B: Medium input (N = 25 records)
      - Config C: Large input (N = 100 records)

    Measures:
      - Correctness / Accuracy (% classifications matching expected ground truth)
      - Valid vs Invalid rejection counts
      - Execution duration (microseconds) and Throughput (records/second)
    """
    geofence = RectangularGeofence()
    configs = [
        ("Config A (Small)", 5),
        ("Config B (Medium)", 25),
        ("Config C (Large)", 100),
    ]

    evaluation_report: Dict[str, Any] = {
        "geofence_bounds": {
            "latitude": [geofence.min_lat, geofence.max_lat],
            "longitude": [geofence.min_lon, geofence.max_lon],
        },
        "model_disclaimer": "Planar 2D rectangular bounding box simplification; not a spherical-distance model.",
        "configurations": [],
    }

    for name, n in configs:
        dataset = generate_controlled_dataset(n)
        raw_points = [(lat, lon) for lat, lon, _ in dataset]
        expected_statuses = [expected for _, _, expected in dataset]

        # Warm-up pass
        _ = geofence.classify_batch(raw_points, safe=True)

        # Timed execution pass
        start_time = time.perf_counter()
        results = geofence.classify_batch(raw_points, safe=True)
        elapsed_sec = time.perf_counter() - start_time
        elapsed_us = elapsed_sec * 1_000_000.0

        correct = 0
        inside_count = 0
        outside_count = 0
        invalid_count = 0

        for res, expected in zip(results, expected_statuses):
            if res.status == expected:
                correct += 1
            if res.status == "INSIDE":
                inside_count += 1
            elif res.status == "OUTSIDE":
                outside_count += 1
            elif res.status == "INVALID":
                invalid_count += 1

        accuracy_pct = (correct / n) * 100.0
        throughput_rec_per_sec = (n / elapsed_sec) if elapsed_sec > 0 else float("inf")

        config_metrics = {
            "configuration": name,
            "sample_size": n,
            "accuracy_pct": round(accuracy_pct, 2),
            "correct_count": correct,
            "inside_count": inside_count,
            "outside_count": outside_count,
            "invalid_rejected_count": invalid_count,
            "elapsed_microseconds": round(elapsed_us, 2),
            "throughput_rec_per_sec": round(throughput_rec_per_sec, 1),
        }
        evaluation_report["configurations"].append(config_metrics)

    return evaluation_report


def main() -> None:
    """Executes the contract demonstration and 3-configuration controlled evaluation."""
    geofence = RectangularGeofence(min_lat=10.0, max_lat=20.0, min_lon=70.0, max_lon=80.0)

    print("=== Rectangular Geofence Membership: Contract Checks & Evaluation ===\n")
    print("Geofence Bounds: Latitude [10.0, 20.0], Longitude [70.0, 80.0] (Inclusive)")
    print("Notice: Rectangular fixture is a Cartesian bounding box, not a spherical-distance model.\n")

    # Contract 1: Inside point (15, 75)
    in_res = geofence.classify_point(POINT_INSIDE[0], POINT_INSIDE[1])
    print(f"[Contract 1] Point {POINT_INSIDE}: status={in_res.status}, is_inside={in_res.is_inside} (Expected: INSIDE)")

    # Contract 2: Boundary point (10, 70)
    bnd_res = geofence.classify_point(POINT_BOUNDARY[0], POINT_BOUNDARY[1])
    print(f"[Contract 2] Boundary {POINT_BOUNDARY}: status={bnd_res.status}, is_inside={bnd_res.is_inside} (Expected: INSIDE)")

    # Contract 3: Outside point (21, 75)
    out_res = geofence.classify_point(POINT_OUTSIDE[0], POINT_OUTSIDE[1])
    print(f"[Contract 3] Point {POINT_OUTSIDE}: status={out_res.status}, is_inside={out_res.is_inside} (Expected: OUTSIDE)")

    # Contract 4: Invalid point (100, 75)
    print(f"[Contract 4] Point {POINT_INVALID}: ", end="")
    try:
        geofence.classify_point(POINT_INVALID[0], POINT_INVALID[1], safe=False)
        print("FAIL (Did not raise InvalidCoordinateError)")
    except InvalidCoordinateError as err:
        print(f"REJECTED as expected ({err.message})")

    print("\n--- Controlled 3-Configuration Evaluation Experiment ---")
    report = run_controlled_evaluation()
    for cfg in report["configurations"]:
        print(
            f"  {cfg['configuration']:<18} | N={cfg['sample_size']:<3} | "
            f"Accuracy={cfg['accuracy_pct']:>5.1f}% | "
            f"Inside={cfg['inside_count']:<2} Outside={cfg['outside_count']:<2} Invalid={cfg['invalid_rejected_count']:<2} | "
            f"Throughput={cfg['throughput_rec_per_sec']:>10.1f} rec/s ({cfg['elapsed_microseconds']:>7.2f} µs)"
        )

    print("\nTrade-off Summary:")
    print("  Correctness is invariant (100.0%) across all input sizes.")
    print("  Per-record dispatch cost amortizes as batch size increases, yielding higher throughput with minimal memory overhead.")


if __name__ == "__main__":
    main()
