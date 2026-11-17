"""The curves a book plate may draw: a spine and its two rails, in floats.

Three sources, one output shape:

- `ph` — a speed pair `(u, v)`; the curve is PH, so the rail is exact and is
  sampled from the rational offset.
- `record` — a stored curve's speed rows (also a PH pair, by construction).
- `cubic` — an integer cubic from a Pythagorean triple; not PH, so the rail is
  the true normal offset, sampled. It is drawn, never claimed exact.

`load()` returns the spine, both rails, the bounding box, the distance and the
fold margin. Nothing here writes a file; `plate_export.py` does that.
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import ph_offset as ph  # noqa: E402
from curve_lab.pyth_cubic import case  # noqa: E402

SAMPLES = 1600


def _sample(point, samples=SAMPLES):
    return [point(i / samples) for i in range(samples + 1)]


def _bbox(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def _diagonal(points):
    x0, y0, x1, y1 = _bbox(points)
    return math.hypot(x1 - x0, y1 - y0)


def _speed_pair(spec):
    """The PH pair for a `ph` or `record` plate."""
    if spec["kind"] == "ph":
        return ([Fraction(value) for value in spec["u"]],
                [Fraction(value) for value in spec["v"]], "exact rational rail")
    path = ROOT / "curves" / spec["slug"] / "curve.json"
    if not path.exists():
        raise FileNotFoundError(f"no record at {path}")
    record = json.loads(path.read_text(encoding="utf-8"))
    u = [Fraction(str(value)) for value in record["speedX"]]
    v = [Fraction(str(value)) for value in record["speedY"]]
    return u, v, f"exact rational rail · record {spec['slug']}"


def _cubic(spec):
    """Control points and a normal-offset sampler for an integer cubic."""
    a, b, c = spec["triple"]
    row = case(a, b, c)
    p0, p1, p2, p3 = row["p0"], row["p1"], row["p2"], row["p3"]

    def point(t):
        mt = 1.0 - t
        return (mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0]
                + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
                mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1]
                + 3 * mt * t * t * p2[1] + t ** 3 * p3[1])

    def derivative(t):
        mt = 1.0 - t
        return (3 * mt * mt * (p1[0] - p0[0]) + 6 * mt * t * (p2[0] - p1[0])
                + 3 * t * t * (p3[0] - p2[0]),
                3 * mt * mt * (p1[1] - p0[1]) + 6 * mt * t * (p2[1] - p1[1])
                + 3 * t * t * (p3[1] - p2[1]))

    def second(t):
        mt = 1.0 - t
        ax, ay = p2[0] - 2 * p1[0] + p0[0], p2[1] - 2 * p1[1] + p0[1]
        bx, by = p3[0] - 2 * p2[0] + p1[0], p3[1] - 2 * p2[1] + p1[1]
        return 6 * (mt * ax + t * bx), 6 * (mt * ay + t * by)

    return point, derivative, second, f"true normal offset, sampled · {row['label']} cubic"


def _curvature_peak(derivative, second, samples=1200):
    worst = 0.0
    for i in range(samples + 1):
        t = i / samples
        dx, dy = derivative(t)
        speed = math.hypot(dx, dy)
        if speed < 1e-12:
            return math.inf
        ddx, ddy = second(t)
        worst = max(worst, abs(dx * ddy - dy * ddx) / speed ** 3)
    return worst


def load(spec) -> dict:
    """Spine, both rails and the numbers a plate needs."""
    if spec["kind"] in ("ph", "record"):
        u, v, rail_kind = _speed_pair(spec)
        point, _ = ph.float_sampler(u, v, 0)
        spine = _sample(point)
        size = _diagonal(spine)
        distance = spec["offsetShare"] * size
        left, _ = ph.float_sampler(u, v, distance)
        right, _ = ph.float_sampler(u, v, -distance)
        rail_left = _sample(left)
        rail_right = _sample(right)
        peak = ph.curvature_peak(u, v, samples=1200)
    else:
        base, derivative, second, rail_kind = _cubic(spec)
        spine = _sample(base)
        size = _diagonal(spine)
        distance = spec["offsetShare"] * size

        def offset(t, signed):
            x, y = base(t)
            dx, dy = derivative(t)
            speed = math.hypot(dx, dy) or 1.0
            return (x - dy / speed * signed, y + dx / speed * signed)

        rail_left = _sample(lambda t: offset(t, distance))
        rail_right = _sample(lambda t: offset(t, -distance))
        peak = _curvature_peak(derivative, second)

    fold = abs(distance) * peak
    if fold >= 0.98:
        raise ValueError(f"{spec['id']}: the rail folds (|d·κ| = {fold:.2f}); "
                         "lower offsetShare")
    return {
        "id": spec["id"],
        "spine": spine,
        "rails": [rail_left, rail_right],
        "bbox": _bbox(spine + rail_left + rail_right),
        "size": size,
        "distance": distance,
        "fold": fold,
        "railKind": rail_kind,
    }
