"""Integer cubic Béziers from Pythagorean triples.

For any integer triple a² + b² = c², set

    P0 = (0, 0)
    P1 = (a, -b)
    P2 = (2c - a, b)
    P3 = (2c, 0)

The control points are integers. The chord is 2c, both handle arms have
length c, and both endpoint tangents are -atan2(b, a). The curve is a symmetric
S-shaped cubic. It is an exact integer-control cubic, not a fitted curve.

Rotating by an angle with rational sine and cosine maps these points to
rationals; scaling by the denominator clears it. A 3-4-5 rotation and scale 5
keeps every point integral.
"""

from __future__ import annotations

import math


def case(a: int, b: int, c: int) -> dict:
    """One integer S cubic from a, b, c with a² + b² = c²."""
    if a <= 0 or b <= 0 or c <= 0 or a * a + b * b != c * c:
        raise ValueError(f"not a positive Pythagorean triple: {(a, b, c)}")
    return {
        "a": a, "b": b, "c": c,
        "label": f"{a}-{b}-{c}",
        "angle": -math.degrees(math.atan2(b, a)),
        "p0": (0, 0),
        "p1": (a, -b),
        "p2": (2 * c - a, b),
        "p3": (2 * c, 0),
        "chord": 2 * c,
        "arm": c,
    }


def cases(triples=None) -> list[dict]:
    triples = triples or (
        (3, 4, 5), (4, 3, 5), (5, 12, 13), (12, 5, 13),
        (8, 15, 17), (15, 8, 17), (7, 24, 25), (24, 7, 25),
        (20, 21, 29), (21, 20, 29),
    )
    return [case(*t) for t in triples]


def rotate_scale(points, cos: float, sin: float, scale: float):
    """Rotate 2-D points by cos/sin, then scale."""
    return [(scale * (x * cos - y * sin), scale * (x * sin + y * cos))
            for x, y in points]


def checks(c: dict) -> bool:
    """The integer construction's invariants."""
    return (
        c["p1"][0] ** 2 + c["p1"][1] ** 2 == c["c"] ** 2
        and c["p2"][0] + c["p1"][0] == 2 * c["c"]
        and c["p3"] == (2 * c["c"], 0)
        and c["chord"] == 2 * c["c"]
        and c["arm"] == c["c"]
    )
