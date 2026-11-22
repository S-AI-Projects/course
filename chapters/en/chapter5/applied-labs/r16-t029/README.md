# Applied Lab R16-T029: Inclusive Rectangular Geofence Membership — Evaluation Experiment

This applied lab extends Chapter 5, Section 8 (**"End-of-chapter quiz"**) with a concrete, contract-tested implementation of an inclusive rectangular geofence and a controlled 3-configuration evaluation experiment.

## Educational Context and Lesson Connection

Chapter 5 explored filtering, mapping, and streaming tabular and coordinate datasets. A common post-processing requirement when cleaning spatial metadata is geofencing: determining whether geographical coordinate pairs `(latitude, longitude)` belong to a specified bounding region.

### Explicit Pedagogical Scope & Limitations
> [!NOTE]
> **Planar Cartesian Fixture Notice:** This lab implements an inclusive 2D Cartesian bounding box over latitude $[10.0, 20.0]$ and longitude $[70.0, 80.0]$.
> It is **NOT** a spherical-distance model (such as haversine or ellipsoidal geodesic algorithms), does not calculate curvature or surface distance, and does not claim real-world navigation accuracy.

## Geofence Contract Specifications

The geofence is defined by inclusive limits:
$$10.0 \le \text{latitude} \le 20.0 \quad \text{and} \quad 70.0 \le \text{longitude} \le 80.0$$

1. **Inside Point**: `(15.0, 75.0)` $\rightarrow$ `INSIDE` (`is_inside = True`)
2. **Boundary Point**: `(10.0, 70.0)` $\rightarrow$ `INSIDE` (`is_inside = True`, inclusive lower bound)
3. **Outside Point**: `(21.0, 75.0)` $\rightarrow$ `OUTSIDE` (`is_inside = False`)
4. **Invalid Coordinate**: `(100.0, 75.0)` $\rightarrow$ `REJECTED` (`InvalidCoordinateError`, latitude exceeds $[-90.0, 90.0]$)

## Controlled Evaluation Experiment

The evaluation experiment compares 3 controlled input configurations using deterministic synthetic datasets:
- **Config A (Small)**: Sample size $N = 5$
- **Config B (Medium)**: Sample size $N = 25$
- **Config C (Large)**: Sample size $N = 100$

### Metrics & Trade-off Analysis
- **Correctness / Accuracy**: Evaluated against ground-truth labels. Attains $100.0\%$ accuracy across all configurations.
- **Error Rejection**: Reliably isolates out-of-bounds terrestrial coordinates.
- **Throughput & Latency**: Demonstrates how per-record call overhead amortizes as batch size increases, yielding higher throughput without memory degradation.

## Running the Lab

### 1. Execute Demonstration & Evaluation
```bash
python3 chapters/en/chapter5/applied-labs/r16-t029/example.py
```

### 2. Run Automated Unit Tests
```bash
python3 -m unittest discover -s chapters/en/chapter5/applied-labs/r16-t029 -p "test_*.py"
```
