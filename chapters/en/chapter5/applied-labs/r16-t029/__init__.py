"""
R16-T029: Inclusive rectangular geofence membership and evaluation experiment.
"""

from .example import (
    GeofenceResult,
    InvalidCoordinateError,
    RectangularGeofence,
    run_controlled_evaluation,
)

__all__ = [
    "GeofenceResult",
    "InvalidCoordinateError",
    "RectangularGeofence",
    "run_controlled_evaluation",
]
