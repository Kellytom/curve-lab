"""Curves from tangent directions: the exact vocabulary, and a search over it.

    .venv/bin/python scripts/direction_curves.py

A flat spot is where the tangent is horizontal: the imaginary part q of the speed is
zero. Every other exact rational direction is reachable too, and one integer indexes
them. With z' = w^2 and w = p + iq the tangent is (p^2 - q^2, 2pq), so its slope is

    2pq / (p^2 - q^2)

Setting that to m gives m p^2 - 2pq - m q^2 = 0, quadratic in (p, q) unless 1 + m^2 is
a rational square. When it is, the equation splits into two straight conditions, and
every such direction is

    (k^2 - 1, 2k)     meaning   q = p / k   or   q = -k p

    k = 1 -> vertical (p = 0)      k = 3 -> slope 3/4      k = 5 -> slope 5/12
    k = 2 -> slope 4/3             k = 4 -> slope 8/15     k -> infinity -> horizontal

The hypotenuse is k^2 + 1, so the 5, 13, 17, 25 in the triples are the hypotenuse
numbers of these directions. The diagonal (45 degrees, m = 1) is not in the family:
1 + 1 = 2 is not a rational square, so whole numbers cannot hit it.

The search keeps the mirror: with u = 2t - 1, p is even in u and q is odd. It forces a
vertical tangent at the middle and one k-direction at a chosen point, which leaves four
free whole numbers; it enumerates those, solves for the last one exactly, keeps whole
solutions, then ranks by grid first and counts crossings only for the survivors — the
grid is a closed form and costs nothing, the crossing count is the expensive part.
"""

from __future__ import annotations

import sys
from fractions import Fraction as F
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ph_crossings import self_crossings  # noqa: E402

NAMES = {1: "vertical", 2: "4/3", 3: "3/4", 4: "8/15", 5: "5/12", 7: "7/24", 12: "12/5"}


def lcm(a: int, b: int) -> int:
    return a * b // gcd(a, b)


def from_u(row_u):
    """A row in u = 2t - 1, as a row in t."""
    def power(p):
        out = [F(1)]
        for _ in range(p):
            nxt = [F(0)] * (len(out) + 1)
            for k, value in enumerate(out):
                nxt[k] += -value
                nxt[k + 1] += 2 * value
            out = nxt
        return out

    out = [F(0)] * (len(row_u) + 2)
    for p, value in enumerate(row_u):
        if not value:
            continue
        for k, coefficient in enumerate(power(p)):
            out[k] += value * coefficient
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def integers(rows):
    scale = 1
    for row in rows:
        for value in row:
            if value:
                scale = lcm(scale, value.denominator)
    return [[int(value * scale) for value in row] for row in rows]


def grid_of(speed_x, speed_y):
    n = max(len(speed_x), len(speed_y))
    xs = list(speed_x) + [0] * (n - len(speed_x))
    ys = list(speed_y) + [0] * (n - len(speed_y))
    pitch = 1
    for m in range(2 * n - 1):
        real = sum(xs[i] * xs[m - i] for i in range(n) if 0 <= m - i < n) \
            - sum(ys[i] * ys[m - i] for i in range(n) if 0 <= m - i < n)
        imag = 2 * sum(xs[i] * ys[m - i] for i in range(n) if 0 <= m - i < n)
        for num in (real, imag):
            if num:
                denominator = F(num, m + 1).denominator
                pitch = pitch * denominator // gcd(pitch, denominator)
    return pitch


def candidates(k: int, t_point: F, box: int = 4):
    """Mirror-symmetric rows with a k-direction at t_point and vertical at 1/2.

    p = a1 u^2 + a2 u^4 (a0 = 0 is the vertical tangent at the middle)
    q = b0 u + b1 u^3 + b2 u^5, and b2 follows from the direction condition.
    """
    u = 2 * t_point - 1
    if not u:
        return
    for a1 in range(-box, box + 1):
        for a2 in range(-box, box + 1):
            p_at = F(a1) * u ** 2 + F(a2) * u ** 4
            if not p_at:
                continue
            for b0 in range(-box, box + 1):
                for b1 in range(-box, box + 1):
                    b2 = (p_at / k - (F(b0) * u + F(b1) * u ** 3)) / u ** 5
                    if b2.denominator != 1:
                        continue
                    row_p = [F(0), F(0), F(a1), F(0), F(a2), F(0)]
                    row_q = [F(0), F(b0), F(0), F(b1), F(0), b2]
                    yield integers([from_u(row_p), from_u(row_q)])


def main():
    for k, t_point in ((3, F(1, 3)), (3, F(1, 4)), (2, F(1, 3)), (4, F(1, 4)), (5, F(1, 4))):
        found = []
        for speed_x, speed_y in candidates(k, t_point):
            if not any(speed_y[1:]) or not any(speed_x):
                continue
            found.append((grid_of(speed_x, speed_y), speed_x, speed_y))
        found.sort(key=lambda item: item[0])
        # only the cheapest quarter is worth counting crossings for
        shortlist = found[:max(40, len(found) // 4)]
        ranked = []
        for pitch, speed_x, speed_y in shortlist:
            crossings = len(self_crossings(speed_x, speed_y, samples=1024))
            if crossings:
                ranked.append((crossings, pitch, speed_x, speed_y))
        ranked.sort(key=lambda item: (-item[0], item[1]))
        print(f"k = {k} ({NAMES.get(k, '')}) at t = {t_point}: {len(found)} whole solutions, "
              f"{len(ranked)} on the shortlist that cross")
        for crossings, pitch, speed_x, speed_y in ranked[:3]:
            print(f"   {crossings:>2} crossings, grid 1/{pitch:<8} "
                  f"x {' '.join(map(str, speed_x))} | y {' '.join(map(str, speed_y))}")
        print()


if __name__ == "__main__":
    main()
