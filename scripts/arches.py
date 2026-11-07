"""Arches from genus-1 and higher curves: parts, not whole curves.

    .venv/bin/python scripts/arches.py

Elliptic curves and Fermat curves are not rational, so they cannot join the
exact catalogue. But parts of them are perfectly usable arches: an arc between
two integer points is drawn from the implicit equation, and its endpoints are
exact. What the number theory contributes is the integer points themselves —
Mordell for the elliptic curves, Fermat's Last Theorem for x^n + y^n = 1.
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def elliptic_arch(a, b, x0, x1, sign=1, n=400):
    """y = ±sqrt(x³ + a x + b) over [x0, x1], where the radicand is non-negative."""
    out = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        v = x ** 3 + a * x + b
        if v < 0:
            continue
        out.append((x, sign * math.sqrt(v)))
    return out


def fermat_arc(n, m=400):
    """x^n + y^n = 1 in the first quadrant, from (1,0) to (0,1)."""
    out = []
    for i in range(m + 1):
        t = i / m
        out.append((t, (max(0.0, 1.0 - t ** n)) ** (1.0 / n)))
    return out


def integer_points_elliptic(a, b, bound=200):
    """Integer (x, y) on y² = x³ + a x + b for |x| ≤ bound."""
    out = []
    for x in range(-bound, bound + 1):
        v = x ** 3 + a * x + b
        if v < 0:
            continue
        r = math.isqrt(v)
        if r * r == v:
            out.append((x, r))
            if r:
                out.append((x, -r))
    return out


def fermat_integer_solutions(n, bound=200):
    """Integer (x, y) with x^n + y^n = 1, |x|,|y| ≤ bound."""
    out = []
    for x in range(-bound, bound + 1):
        for y in range(-bound, bound + 1):
            if x ** n + y ** n == 1:
                out.append((x, y))
    return out


def cases():
    oval = elliptic_arch(0, 1, -1.0, 0.0)
    branch = elliptic_arch(0, 1, 0.0, 2.0)
    f3 = fermat_arc(3)
    f4 = fermat_arc(4)
    return [
        ("elliptic · y² = x³+1 · the oval", oval,
         "x ∈ [−1, 0] · (−1,0) to (0,1) · genus 1, no rational parametrisation",
         "scripts/arches.py · implicit y² = x³ + 1"),
        ("elliptic · y² = x³+1 · the branch", branch,
         "x ∈ [0, 2] · (0,1) to (2,3) · both endpoints integer",
         "scripts/arches.py · implicit y² = x³ + 1"),
        ("Fermat n = 3 · x³+y³ = 1", f3,
         "(0,1) to (1,0) · the only integer points are the two ends (FLT)",
         "scripts/arches.py · Fermat cubic"),
        ("Fermat n = 4 · x⁴+y⁴ = 1", f4,
         "(0,1) to (1,0) · genus 3 · integer points only (±1,0), (0,±1)",
         "scripts/arches.py · Fermat quartic"),
    ]


if __name__ == "__main__":
    print("y² = x³ + 1 integer points:",
          integer_points_elliptic(0, 1, 60))
    print("x³ + y³ = 1 integer points:",
          fermat_integer_solutions(3, 40))
    print("x⁴ + y⁴ = 1 integer points:",
          fermat_integer_solutions(4, 40))
    for title, pts, note, source in cases():
        print(f"{title}: {len(pts)} points · {note}")
