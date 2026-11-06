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


def interior_angle(row: dict) -> float:
    """The control-polygon interior angle at P1, in degrees.

    With equal arms c and chord 2c the angle depends only on a/c, and the
    cosine is exact: cos θ = √((c − a) / 2c). It is the S family's one shape
    parameter; the C family's is height/chord.
    """
    return math.degrees(math.acos(math.sqrt((row["c"] - row["a"])
                                           / (2.0 * row["c"]))))


def _smallest(rows: list[dict]) -> dict:
    return min(rows, key=lambda r: (r["c"], r["a"], r["b"]))


def representatives(width_deg: float = 4.3495, height_step: float = 0.05,
                    c_max: int = 3125) -> dict:
    """One curve per bin of each shape range — the smallest c in the bin.

    The 316 S curves at c ≤ 1000 are not 316 shapes: arms equal and chord 2c
    leave one degree of freedom, the interior angle at P1 (46.3°–88.7°). The C
    curves are the same story with height/chord (0.023–0.499). This samples the
    two ranges instead of keeping every triple: 11 S, 10 C.

    Bins divide the observed range into ⌈span / width⌉ equal parts, so no bin
    is wider than `width_deg` (S) or `height_step` (C) and the whole range is
    covered. The full catalogue stays the table of record.
    """
    s_rows = catalogue(c_max)
    c_rows = catalogue_c(c_max)
    s_vals = [interior_angle(r) for r in s_rows]
    c_vals = [r["height"] / r["chord"] for r in c_rows]

    def ladder(vals, rows, width):
        lo, hi = min(vals), max(vals)
        n = max(1, math.ceil((hi - lo) / width))
        step = (hi - lo) / n
        bins = {}
        for v, row in zip(vals, rows):
            bins.setdefault(min(n - 1, int((v - lo) / step)), []).append(row)
        keys = sorted(bins)
        return {
            "rows": [_smallest(bins[k]) for k in keys],
            "bins": [(lo + k * step, lo + (k + 1) * step) for k in keys],
            "step": step, "range": (lo, hi), "n": n,
        }

    s = ladder(s_vals, s_rows, width_deg)
    c = ladder(c_vals, c_rows, height_step)
    return {
        "c_max": c_max,
        "width_deg": width_deg,
        "height_step": height_step,
        "s": s["rows"], "c": c["rows"],
        "s_bins": s["bins"], "c_bins": c["bins"],
        "s_step": s["step"], "c_step": c["step"],
        "s_range": s["range"], "c_range": c["range"],
        "counts": (len(s_rows), len(c_rows)),
    }

def lattice_hits(row: dict, scale: int = 1, q_max: int = 12) -> list[dict]:
    """Integer points on the curve at t = k/q, for q up to `q_max`.

    The cubic at t = k/q has denominator dividing q³, so `scale` multiplies
    that: at scale 1 only t = 0, ½, 1 are integer (every curve has exactly
    three), at 27 the thirds join, at 64 the quarters, at 125 the fifths, at
    3125 the twenty-fifths. This is the lattice-hit ledger behind the
    catalogue's key-distance table.
    """
    p0, p1, p2, p3 = row["p0"], row["p1"], row["p2"], row["p3"]
    out = []
    for q in range(1, q_max + 1):
        for k in range(q + 1):
            t = Fraction(k, q)
            mt = 1 - t
            x = (mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0]
                 + 3 * mt * t * t * p2[0] + t ** 3 * p3[0]) * scale
            y = (mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1]
                 + 3 * mt * t * t * p2[1] + t ** 3 * p3[1]) * scale
            if x.denominator == 1 and y.denominator == 1:
                out.append({"t": (k, q), "point": (int(x), int(y))})
    return out


def hit_table(c_max: int = 1000, q_max: int = 25) -> list[dict]:
    """Hits per key distance for every S curve, and the same for C curves."""
    keys = (1, 8, 27, 64, 125, 1000, 15625)
    rows = catalogue(c_max)
    c_rows = catalogue_c(c_max)
    out = []
    for scale in keys:
        s_hits = [len({h["point"] for h in lattice_hits(r, scale, q_max)})
                  for r in rows]
        c_hits = [len({h["point"] for h in lattice_hits(r, scale, q_max)})
                  for r in c_rows]
        out.append({"scale": scale,
                    "s_median": sorted(s_hits)[len(s_hits) // 2],
                    "s_min": min(s_hits), "s_max": max(s_hits),
                    "c_median": sorted(c_hits)[len(c_hits) // 2],
                    "c_min": min(c_hits), "c_max": max(c_hits)})
    return out
