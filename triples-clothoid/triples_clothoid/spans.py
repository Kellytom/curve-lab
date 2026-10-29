"""Chords to cubics, in the span format the existing writer already takes.

`clothoid_lab.svg.path_d` and `clothoid_lab.piece` speak one span shape:

    {"s0", "s1", "p0", "c1", "c2", "p3"}

so a polygon from this package can be drawn by the existing SVG writer without
a backend, a `Design`, or a `Chain`.  That is the integration seam, and it is
deliberately the *only* one.

The cubic between two nodes uses the parabola rule, which is exact for a
circular arc: the control arm is `chord / (3 cos^2(delta/2))` where `delta` is
the angle between the chord and the end tangent.  A group is closed once its
turns add up to `max_turn`, so no single cubic has to carry a large heading
change -- the "45 to 60 degrees" rule, applied to the fit rather than the curve.
"""

from __future__ import annotations

import math

from .spiral import Spiral


def spans(path: Spiral, max_turn: float = math.radians(50.0)) -> list[dict]:
    """Group the chords of `path` into cubics, each within `max_turn`."""
    nodes = path.floats()
    heads = [h.angle for h in path.headings]
    if len(nodes) < 2:
        return []

    alpha = path.triangle.radians
    groups: list[tuple[int, int]] = []
    i = 0
    while i < len(nodes) - 1:
        j, turn = i + 1, 0.0
        sign = 0
        while j < len(nodes) - 1:
            step = alpha * path.turns[j]
            # a curvature reversal means the cubic has to change its bulge
            # sense inside the span, which no single cubic does well
            if step and sign and (step > 0) != (sign > 0):
                break
            if abs(turn + step) > max_turn:
                break
            turn += step
            if step:
                sign = 1 if step > 0 else -1
            j += 1
        groups.append((i, j))
        i = j

    out = []
    for i, j in groups:
        p0, p3 = nodes[i], nodes[j]
        # arriving tangents: a span is tangent to the chords it replaces, so a
        # one-chord span is exactly that chord and no span invents curvature
        out.append(_cubic(p0, p3, heads[i], heads[j - 1], s0=float(i), s1=float(j)))
    return out


def sagitta(path: Spiral) -> float:
    """The resolution floor: how far the smooth curve sits from the chords.

    A chord of length L subtending a turn `d` belongs to a circle of radius
    `L / (2 sin(d/2))`; the curve bulges away from the chord by its sagitta.
    No cubic fit can beat this, so a deviation near it means the fit is done
    and the *chain* is the limit.
    """
    worst = 0.0
    for turn in path.turns:
        d = abs(path.triangle.radians * turn)
        if d <= 0 or d >= math.pi:
            continue
        R = float(path.length) / (2 * math.sin(d / 2))
        worst = max(worst, R * (1 - math.cos(d / 2)))
    return worst


def _cubic(p0, p3, t0, t1, s0=0.0, s1=1.0) -> dict:
    cx, cy = p3[0] - p0[0], p3[1] - p0[1]
    chord = math.hypot(cx, cy)
    if chord < 1e-12:
        return {"s0": s0, "s1": s1, "p0": p0, "c1": p0, "c2": p3, "p3": p3}

    def arm(theta):
        cos = (cx * math.cos(theta) + cy * math.sin(theta)) / chord
        half = (1.0 + max(-1.0, min(1.0, cos))) / 2.0
        return chord / (3.0 * half) if half > 1e-9 else chord

    a0, a1 = arm(t0), arm(t1)
    return {
        "s0": s0, "s1": s1, "p0": p0,
        "c1": (p0[0] + a0 * math.cos(t0), p0[1] + a0 * math.sin(t0)),
        "c2": (p3[0] - a1 * math.cos(t1), p3[1] - a1 * math.sin(t1)),
        "p3": p3,
    }


def cubic_at(span: dict, t: float) -> tuple[float, float]:
    u = 1.0 - t
    b = (u * u * u, 3 * u * u * t, 3 * u * t * t, t * t * t)
    px = (span["p0"][0], span["c1"][0], span["c2"][0], span["p3"][0])
    py = (span["p0"][1], span["c1"][1], span["c2"][1], span["p3"][1])
    return (sum(w * v for w, v in zip(b, px)), sum(w * v for w, v in zip(b, py)))


def _segment_distance(p, a, b) -> float:
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    den = dx * dx + dy * dy
    if den < 1e-18:
        return math.hypot(p[0] - ax, p[1] - ay)
    t = ((p[0] - ax) * dx + (p[1] - ay) * dy) / den
    t = max(0.0, min(1.0, t))
    return math.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy))


def deviation(span: dict, nodes: list[tuple[float, float]], samples: int = 33) -> float:
    """Worst distance from the cubic to the polyline it replaces."""
    lo, hi = int(span["s0"]), int(span["s1"])
    worst = 0.0
    for k in range(samples):
        p = cubic_at(span, k / (samples - 1))
        best = min(_segment_distance(p, nodes[i], nodes[i + 1])
                   for i in range(lo, hi))
        worst = max(worst, best)
    return worst
