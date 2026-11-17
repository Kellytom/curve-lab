"""Fitted cubic-Bézier parallel rails, after Levien's parallel Béziers.

The exact offset of a cubic Bézier is an analytic curve of degree ten; it is
not tractable to work with. Levien's 2022 method fits a cubic-Bézier chain to
the true parallel and subdivides until the error is acceptable. This module is
the house implementation of that *option*, not a line-by-line port of the
area/moment solver in the article:

- sample the exact normal offset of each source cubic;
- fit a cubic chain with the house adaptive fitter;
- report the maximum error against the dense exact offset;
- flag the intervals where |d * kappa| >= 1, where the rail folds/cusps.

Reference: Raph Levien, "Parallel curves of cubic Béziers", 2022-09-09,
`reference/external/parallel-beziers.html`.

Output is cubic Bézier spans (`p0`, `c1`, `c2`, `p3`, `s0`, `s1`), so it is
SVG-friendly and can be compared directly with the exact PH rail and the LAC
chain rail. It is always a fitted option; never call it exact.
"""

from __future__ import annotations

import math


def _cubic_deriv(span: dict, t: float) -> tuple[float, float]:
    u = 1.0 - t
    (x0, y0), (x1, y1) = span["p0"], span["c1"]
    (x2, y2), (x3, y3) = span["c2"], span["p3"]
    a = 3.0 * u * u
    b = 6.0 * u * t
    c = 3.0 * t * t
    return (a * (x1 - x0) + b * (x2 - x1) + c * (x3 - x2),
            a * (y1 - y0) + b * (y2 - y1) + c * (y3 - y2))


def _cubic_curvature(span: dict, t: float) -> float:
    dx, dy = _cubic_deriv(span, t)
    # second derivative
    u = 1.0 - t
    (x0, y0), (x1, y1) = span["p0"], span["c1"]
    (x2, y2), (x3, y3) = span["c2"], span["p3"]
    ddx = 6.0 * u * (x2 - 2.0 * x1 + x0) + 6.0 * t * (x3 - 2.0 * x2 + x1)
    ddy = 6.0 * u * (y2 - 2.0 * y1 + y0) + 6.0 * t * (y3 - 2.0 * y2 + y1)
    den = (dx * dx + dy * dy) ** 1.5
    if den < 1e-15:
        return 0.0
    return (dx * ddy - dy * ddx) / den


def _offset_point(span: dict, t: float, distance: float):
    from .bezier import cubic_at

    x, y = cubic_at(span, t)
    dx, dy = _cubic_deriv(span, t)
    length = math.hypot(dx, dy)
    if length < 1e-15:
        return x, y
    # left normal
    return x - distance * dy / length, y + distance * dx / length


def _offset_tangent(span: dict, t: float) -> float:
    dx, dy = _cubic_deriv(span, t)
    return math.atan2(dy, dx)


def cusp_ranges(span: dict, distance: float, steps: int = 96):
    """Intervals of t where |distance * kappa| >= 1; the rail folds there."""
    out = []
    opened = None
    for i in range(steps + 1):
        t = i / steps
        folded = abs(distance * _cubic_curvature(span, t)) >= 1.0
        if folded and opened is None:
            opened = t
        elif not folded and opened is not None:
            out.append((opened, t))
            opened = None
    if opened is not None:
        out.append((opened, 1.0))
    return out


def fit_offset(point, tangent, tol: float = 0.01, max_spans: int = 64):
    """Fit a cubic chain to an exact offset given as point/tangent callables.

    This is the same adaptive fit `fit_span` uses, opened up so a source that
    is not a cubic (a degree-7 PH curve, say) can be fitted from its exact
    offset instead of from a cubic approximation of the source.
    """
    from .bezier import fit_interval, span_error

    fitted = fit_interval(0.0, 1.0, point, tangent, tol=tol,
                          max_spans=max_spans)
    errors = [span_error(span, point) for span in fitted]
    return {
        "spans": fitted,
        "error_max": max(errors) if errors else 0.0,
        "clamped": sum(1 for span in fitted if span.get("clamped")),
    }


def fit_span(span: dict, distance: float, tol: float = 0.01,
             max_spans: int = 64):
    """Fit one source cubic's normal offset with a cubic chain."""
    fitted = fit_offset(lambda t: _offset_point(span, t, distance),
                        lambda t: _offset_tangent(span, t),
                        tol=tol, max_spans=max_spans)
    fitted["cusps"] = cusp_ranges(span, distance)
    return fitted


def fit_chain(spans: list[dict], distance: float, tol: float = 0.01,
              max_spans: int = 64):
    """Fit a cubic chain's normal offset; one source span at a time.

    Returns a dict with all fitted spans, the worst error, the cusp intervals
    (source-span index plus t range), and the clamped count. The spans are
    cubic Béziers; the caller can draw them or hand them to the SVG writer.
    """
    all_spans = []
    error = 0.0
    cusps = []
    clamped = 0
    for index, span in enumerate(spans):
        item = fit_span(span, distance, tol=tol, max_spans=max_spans)
        all_spans.extend(item["spans"])
        error = max(error, item["error_max"])
        clamped += item["clamped"]
        if item["cusps"]:
            cusps.append({"span": index, "ranges": item["cusps"]})
    return {"spans": all_spans, "error_max": error, "cusps": cusps,
            "clamped": clamped, "tol": tol}
