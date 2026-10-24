"""Parallel rails: the offset of a clothoid chain, and where it folds.

The offset of a clothoid is not a clothoid, so a rail is built the honest way.
Sample the spine, step along its normal, and fit cubics to what comes out. The
fit reports its own error against a dense offset sampling, so the rail's shape
is a measured approximation and not a claim.

A rail folds where the offset distance reaches the local centre of curvature,
|d * kappa| >= 1. The design decision for this tool is to draw the fold and
report where it starts, because a fold is often what a ribbon or a fold of
drapery is supposed to look like. What must not happen is a fold the operator
did not choose, so every rail carries its cusp radius and its margin.
"""

from __future__ import annotations

from .bezier import cubic_at, distance_to_curve, fit_interval, span_error


def rail_functions(chain, distance: float):
    """Point and tangent callables for the rail at a signed normal distance."""

    def point(s: float) -> tuple[float, float]:
        # The backend's own offset when it has one: Bertolazzi's X_ISO and Y_ISO
        # are the exact parallel curve, not a sampled normal step.
        return chain.offset_point(s, distance)

    def tangent(s: float) -> float:
        return chain.tangent(s)

    return point, tangent


def cusp_ranges(chain, distance: float, steps: int = 512) -> list[tuple[float, float]]:
    """Arc-length ranges where the rail has folded, |d * kappa| >= 1."""
    ranges: list[tuple[float, float]] = []
    open_at = None
    for i in range(steps + 1):
        s = chain.length * i / steps
        folded = abs(distance * chain.kappa(s)) >= 1.0
        if folded and open_at is None:
            open_at = s
        elif not folded and open_at is not None:
            ranges.append((open_at, s))
            open_at = None
    if open_at is not None:
        ranges.append((open_at, chain.length))
    return ranges


def build_rail(chain, distance: float, tol: float = 0.02,
               max_spans_per_segment: int = 64, split: int = 2) -> dict:
    """Fit one rail, with its fold report."""
    point, tangent = rail_functions(chain, distance)
    spans: list[dict] = []
    for placed in chain.segments:
        spans.extend(fit_interval(placed.s_base, placed.s_base + placed.length,
                                  point, tangent,
                                  tol=tol, max_spans=max_spans_per_segment, split=split))
    errors = [span_error(s, point) for s in spans]
    folds = cusp_ranges(chain, distance)
    r_min, r_at = chain.min_radius()
    return {
        "distance": distance,
        "spans": spans,
        "spans_count": len(spans),
        "error_max": max(errors) if errors else 0.0,
        "folds": folds,
        "min_radius": r_min,
        "min_radius_at": r_at,
        "margin": r_min - abs(distance),
        "clipped": False,
        "point": point,
    }


def build_rails(chain, distances, tol: float = 0.02,
                max_spans_per_segment: int = 64, split: int = 2) -> list[dict]:
    return [build_rail(chain, float(d), tol=tol, split=split,
                       max_spans_per_segment=max_spans_per_segment) for d in distances]


def ribbon_outline(chain, width: float, tol: float = 0.02, split: int = 2) -> dict:
    """Two rails at half width, joined at both ends, as one closed outline.

    The end joins are straight lines, which is the blunt terminal. Tapered and
    round terminals are their own problem and are not pretended here.
    """
    half = width / 2.0
    left = build_rail(chain, half, tol=tol, split=split)
    right = build_rail(chain, -half, tol=tol, split=split)
    folds = left["folds"] + right["folds"]
    return {
        "width": width,
        "left": left,
        "right": right,
        "folds": folds,
        "error_max": max(left["error_max"], right["error_max"]),
        "margin": chain.min_radius()[0] - half,
    }


def rail_deviation(rail: dict, chain, samples: int = 13) -> float:
    """Spacing between the fitted rail and the true offset, measured to the curve."""
    point = rail["point"]
    worst = 0.0
    for span in rail["spans"]:
        s0, s1 = span["s0"], span["s1"]
        for i in range(samples):
            x, y = cubic_at(span, i / (samples - 1))
            worst = max(worst, distance_to_curve(x, y, s0, s1, point))
    return worst
