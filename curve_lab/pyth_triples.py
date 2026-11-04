"""Pythagorean-triple families and their parabolas.

Every primitive triple comes from Euclid:

    a = m^2 - n^2,  b = 2mn,  c = m^2 + n^2,  m > n, coprime, opposite parity.

For a fixed `n`, varying `m` gives a parabola in the (a,b) plane:

    a = (b / (2n))^2 - n^2

Multiples of a triple lie on a ray from the origin. This module builds the
points, rays, and selected family sequences used by the probe page.
"""

from __future__ import annotations

import math
from math import gcd


def base_triples(c_max: int):
    """Every triple up to c_max, including multiples, with its m/n route."""
    seen = set()
    out = []
    for m in range(2, int(math.isqrt(c_max)) + 1):
        for n in range(1, m):
            if (m - n) % 2 == 0 or gcd(m, n) != 1:
                continue
            a = m * m - n * n
            b = 2 * m * n
            c = m * m + n * n
            if c > c_max:
                continue
            k = 1
            while k * c <= c_max:
                triple = (a * k, b * k, c * k)
                if triple not in seen:
                    seen.add(triple)
                    out.append({
                        "a": triple[0], "b": triple[1], "c": triple[2],
                        "m": m, "n": n, "k": k,
                    })
                k += 1
    return sorted(out, key=lambda t: (t["c"], t["a"], t["b"]))


def family(n: int, c_max: int):
    """The k=1 family with fixed Euclid n; these points lie on one parabola."""
    out = []
    for m in range(n + 1, int(math.isqrt(c_max)) + 2):
        a = m * m - n * n
        b = 2 * m * n
        c = m * m + n * n
        if c > c_max:
            break
        out.append({"a": a, "b": b, "c": c, "m": m, "n": n, "k": 1})
    return out


def euclid_n_curve(n: int, b_max: int, samples: int = 200):
    """Holding Euclid n: a=(b/(2n))^2-n^2, clipped to the positive quadrant."""
    out = []
    for i in range(samples + 1):
        b = b_max * i / samples
        a = (b / (2.0 * n)) ** 2 - n * n
        if a >= 0:
            out.append((a, b))
    return out


def euclid_m_curve(m: int, a_max: int, samples: int = 200):
    """Holding Euclid m: b=m^2-a^2/(4m^2), clipped to the positive quadrant."""
    out = []
    for i in range(samples + 1):
        a = a_max * i / samples
        b = m * m - a * a / (4.0 * m * m)
        if b >= 0:
            out.append((a, b))
    return out


def fassler_curve(N: int, a_max: int, samples: int = 240):
    """The Fässler parabola b=|N - a^2/(4N)|, sampled in a."""
    return [
        (a, abs(N - a * a / (4.0 * N)))
        for a in [a_max * i / samples for i in range(samples + 1)]
    ]


def angle_deg(point) -> float:
    return math.degrees(math.atan2(point["b"], point["a"]))


def selected_chain(n: int, c_max: int, angle_max: float, angle_min: float):
    """The fixed-n family points between two angles, smallest angle last."""
    return [
        point for point in family(n, c_max)
        if angle_min <= angle_deg(point) <= angle_max
    ]


def rays(points, limit: int, count: int = 10):
    """A readable sample of primitive scaling rays from the origin."""
    picks = sorted(
        (p for p in points if p["k"] == 1),
        key=lambda p: (p["c"], p["a"], p["b"]),
    )
    if len(picks) > count:
        stride = max(1, len(picks) // count)
        picks = picks[::stride][:count]
    return [
        ((0, 0), (p["a"] * limit / p["c"], p["b"] * limit / p["c"]), p)
        for p in picks
    ]
