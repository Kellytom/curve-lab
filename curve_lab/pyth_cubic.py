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
from fractions import Fraction


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


def catalogue(c_max: int = 1000, primitive_only: bool = True) -> list[dict]:
    """The canonical integer-cubic catalogue from every triple up to `c_max`.

    One row per ordered arm pair. Each row carries both sign variants of the
    construction (P1 = (a, -b), the canonical one, and its mirror P1 = (a, b)),
    the chord and arm, the tangent angle, and the exact integer rotation by the
    triple's own angle at scale c.

    Rotations are a group action, not a finite column: the row records the one
    rotation the triple supplies, and every power of it is again exact.
    """
    from .pyth_triples import base_triples

    triples = [t for t in base_triples(c_max)
               if not primitive_only or t["k"] == 1]
    rows = []
    for t in triples:
        a0, b0, c = t["a"], t["b"], t["c"]
        for a, b in ((a0, b0), (b0, a0)):
            row = case(a, b, c)
            row.update({
                "m": t["m"], "n": t["n"], "k": t["k"],
                "order": "ab" if (a, b) == (a0, b0) else "ba",
                "mirror_p1": (a, b),
                "mirror_p2": (2 * c - a, -b),
                "mirror_p3": (2 * c, 0),
                "rotation": (a, -b, b, a, c),
            })
            # exact rational rotation at scale c: every point is an integer
            co, si = Fraction(a, c), Fraction(b, c)
            rotated = [((co * x - si * y) * c, (si * x + co * y) * c)
                       for x, y in (row["p0"], row["p1"], row["p2"], row["p3"])]
            if not all(x.denominator == 1 and y.denominator == 1
                       for x, y in rotated):
                raise AssertionError(f"rotation is not integral for {row['label']}")
            row["rotation_points"] = [(int(x), int(y)) for x, y in rotated]
            rows.append(row)
    return rows


def case_c(a: int, b: int, c: int) -> dict:
    """The C-shaped integer cubic: both handles on the same side of the chord."""
    if a <= 0 or b <= 0 or c <= 0 or a * a + b * b != c * c:
        raise ValueError(f"not a positive Pythagorean triple: {(a, b, c)}")
    return {
        "a": a, "b": b, "c": c,
        "label": f"{a}-{b}-{c} C",
        "angle": math.degrees(math.atan2(b, a)),
        "p0": (0, 0), "p1": (a, b), "p2": (2 * c - a, b), "p3": (2 * c, 0),
        "chord": 2 * c, "arm": c, "height": b,
        "shape": "C",
    }


def catalogue_c(c_max: int = 1000) -> list[dict]:
    """Every ordered arm pair as a C cubic, one row per order."""
    from .pyth_triples import base_triples

    rows = []
    for t in base_triples(c_max):
        if t["k"] != 1:
            continue
        a0, b0, c = t["a"], t["b"], t["c"]
        for a, b in ((a0, b0), (b0, a0)):
            row = case_c(a, b, c)
            row.update({"m": t["m"], "n": t["n"],
                        "order": "ab" if (a, b) == (a0, b0) else "ba"})
            rows.append(row)
    return rows
