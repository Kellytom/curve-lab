"""Rosettes from linkages, done exactly: the closure test, and a search.

    .venv/bin/python scripts/linkage_exact.py            # the search and its verdict
    .venv/bin/python scripts/linkage_exact.py --check a b c d

The second algorithmic idea (spec: "Rosettes from linkages, done exactly"): a coupler
curve is asymmetric, and the crank run backwards gives its mirror, so the pair is a
rosette. A rosette made this way is exact only if every joint of the linkage is a
rational point at every crank station.

**Why that is a real condition.** The crank end `A` is a rational point of the circle.
The rocker joint `B` is the intersection of two circles: centre `A` with radius `b`, and
centre the ground pivot `D` with radius `c`. Writing `s = |A − D|`, the projection is

    p = (b² + s² − c²) / (2 s),        h² = b² − p²,        B = D + p·u ± h·n

where `u` and `n` are rational unit vectors. Everything is rational except `h`, so the
joint is exact **if and only if `h²` is a perfect square of a rational**.

The search below tries small whole-number links against p-triple crank directions and
reports the sets whose closure is exact at every station. The check mode refuses a set
whose closure is not exact, which is the rule the page's linkage figure will follow.
"""

from __future__ import annotations

import argparse
import itertools
import math
from fractions import Fraction


def rational_root(value: Fraction):
    """The exact square root of a non-negative Fraction, or None."""
    if value < 0:
        return None
    numerator, denominator = value.numerator, value.denominator
    top, bottom = math.isqrt(numerator), math.isqrt(denominator)
    if top * top == numerator and bottom * bottom == denominator:
        return Fraction(top, bottom)
    return None


def unit_points(limit=13):
    """Rational points on the unit circle from p-triples, with the signs and 90° turns."""
    points = set()
    for x, y in itertools.permutations(range(1, limit), 2):
        zz = x * x + y * y
        root = math.isqrt(zz)
        if root * root != zz:
            continue
        for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            points.add((Fraction(sx * x, root), Fraction(sy * y, root)))
    points.add((Fraction(1), Fraction(0)))
    points.add((Fraction(0), Fraction(1)))
    points.add((Fraction(-1), Fraction(0)))
    points.add((Fraction(0), Fraction(-1)))
    return sorted(points)


def closure(A, b, c, d):
    """The rocker joint for crank end `A`, exactly, or None when it is not rational.

    Both joint conditions are circles; subtracting them leaves a **line** with rational
    coefficients, `(D − A)·B = k`, so a rational point on it exists and the circle meets
    it where a quadratic in `t` has a rational square discriminant. No square root of a
    distance is ever taken, which is what made the first version of this test wrong.
    """
    ax, ay = Fraction(A[0]), Fraction(A[1])
    dx, dy = Fraction(d), Fraction(0)
    nx, ny = dx - ax, dy - ay
    nn = nx * nx + ny * ny
    if nn == 0:
        return None
    k = (Fraction(b * b - c * c) + Fraction(d * d) - (ax * ax + ay * ay)) / 2
    bx0, by0 = k * nx / nn, k * ny / nn
    tx, ty = -ny, nx
    vx, vy = bx0 - ax, by0 - ay
    qa = tx * tx + ty * ty
    qb = 2 * (vx * tx + vy * ty)
    qc = vx * vx + vy * vy - Fraction(b * b)
    root = rational_root(qb * qb - 4 * qa * qc)
    if root is None:
        return None
    t = (-qb + root) / (2 * qa)
    return (bx0 + t * tx, by0 + t * ty)


def check_set(a, b, c, d, points):
    """How many crank stations close rationally, and the first that does not."""
    exact = 0
    missing = []
    for A in points:
        A = (a * A[0], a * A[1])
        if closure(A, b, c, d) is None:
            missing.append(A)
        else:
            exact += 1
    return exact, len(points), missing


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", nargs=4, type=int, metavar=("a", "b", "c", "d"))
    parser.add_argument("--limit", type=int, default=8, help="largest link length tried")
    args = parser.parse_args(argv)

    points = unit_points()
    print(f"{len(points)} rational crank directions, from p-triples up to 12")

    if args.check:
        a, b, c, d = args.check
        exact, total, missing = check_set(a, b, c, d, points)
        print(f"links a={a} b={b} c={c} d={d}: {exact}/{total} crank stations close exactly")
        if missing:
            print(f"not exact at, for example, {missing[0]}")
            return 1
        print("every station closes exactly: this linkage can make an exact rosette")
        return 0

    winners = []
    tried = 0
    for a, b, c, d in itertools.product(range(1, args.limit + 1), repeat=4):
        if not (a < d + c and d < a + c and c < a + d):
            continue          # the four-bar inequality: a linkage that can turn
        tried += 1
        exact, total, _ = check_set(a, b, c, d, points)
        if exact == total:
            winners.append((a, b, c, d, exact))
    winners.sort(key=lambda row: sum(row[:4]))
    print(f"{tried} link sets tried; {len(winners)} close exactly at every crank station")
    for a, b, c, d, exact in winners[:8]:
        print(f"   a={a:2d} b={b:2d} c={c:2d} d={d:2d}   {exact} stations")
    if not winners:
        print("none in this range: a linkage whose closure is rational everywhere is rare,")
        print("and the page's linkage figure is a sampled figure, not an exact one.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
