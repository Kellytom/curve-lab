"""Where the curvature is tightest on the power curves: compute, never recall.

    .venv/bin/python scripts/curvature_power.py            # print the table
    .venv/bin/python scripts/curvature_power.py --check    # exit 1 if the doc disagrees

Every number in `app/src/content/docs/docs/curvature-power-curves.md` comes from here. The maximum
of y = x^n is found from the derivative of curvature in closed form and checked
against a numeric scan; the septic hyperbola and superellipse are scanned.

Why this exists: the page was written by the side chat with a correct formula
and a wrong table (n = 4), and a septic superellipse section that had the
maximum and minimum the wrong way round. A script is the difference between a
number and a guess.
"""

from __future__ import annotations

import math
import sys

NS = (2, 3, 4, 5, 6, 7, 10, 20, 100)


def kappa_power(n: float, x: float) -> float:
    if x <= 0:
        return 0.0
    y1 = n * x ** (n - 1)
    y2 = n * (n - 1) * x ** (n - 2)
    return abs(y2) / (1 + y1 * y1) ** 1.5


def x_max_formula(n: float) -> float:
    if n == 2:
        return 0.0
    return ((n - 2) / (n * n * (2 * n - 1))) ** (1 / (2 * n - 2))


def x_max_numeric(n: float, samples: int = 20000) -> float:
    lo, hi = 1e-9, 1.0
    best_x, best_k = lo, kappa_power(n, lo)
    for i in range(1, samples + 1):
        x = lo + (hi - lo) * i / samples
        k = kappa_power(n, x)
        if k > best_k:
            best_k, best_x = k, x
    return best_x


def septic_hyperbola(samples: int = 40000):
    """x^7 - y^7 = 1: the curvature maximum along the branch, numerically."""
    def y_of(x):
        return (x ** 7 - 1) ** (1 / 7)

    best = (0.0, 0.0)
    h = 1e-6
    for i in range(1, samples + 1):
        x = 1 + i / samples
        y1 = (y_of(x + h) - y_of(x - h)) / (2 * h)
        y2 = (y_of(x + h) - 2 * y_of(x) + y_of(x - h)) / (h * h)
        k = abs(y2) / (1 + y1 * y1) ** 1.5
        if k > best[0]:
            best = (k, x)
    return best[1], y_of(best[1])


def septic_superellipse(samples: int = 200000):
    """|x|^7 + |y|^7 = 1 in the first quadrant: parameter t, x=cos^(2/7), y=sin^(2/7)."""
    def point(t):
        # |cos|^(2/7) with the sign kept: a plain fractional power of a negative
        # base is complex, and t - h dips below zero at the first sample.
        c, s = math.cos(t), math.sin(t)
        return (math.copysign(abs(c) ** (2 / 7), c),
                math.copysign(abs(s) ** (2 / 7), s))

    h = 1e-5
    best_k, best_t = -1.0, 0.0
    for i in range(samples + 1):
        t = (math.pi / 4) * i / samples
        (x0, y0), (x1, y1), (x2, y2) = point(t - h), point(t), point(t + h)
        dx, dy = (x2 - x0) / (2 * h), (y2 - y0) / (2 * h)
        ddx, ddy = (x2 - 2 * x1 + x0) / h ** 2, (y2 - 2 * y1 + y0) / h ** 2
        k = abs(dx * ddy - dy * ddx) / (dx * dx + dy * dy) ** 1.5
        if k > best_k:
            best_k, best_t = k, t
    return point(best_t), best_k, math.degrees(best_t)


def rows():
    out = []
    for n in NS:
        x = x_max_formula(n)
        out.append({"n": n, "x": x, "y": x ** n, "x_numeric": x_max_numeric(n)})
    return out


def main(argv: list[str]) -> int:
    table = rows()
    print("n    x_max (closed form)  x_max (scan)  y_max     kappa_max")
    for row in table:
        print(f"{row['n']:3}  {row['x']:.4f}               {row['x_numeric']:.4f}"
              f"        {row['y']:.4f}    {kappa_power(row['n'], max(row['x'], 1e-9)):.3f}")

    hx, hy = septic_hyperbola()
    print(f"\nseptic hyperbola x^7 - y^7 = 1: max curvature at ({hx:.3f}, {hy:.3f})")
    (sx, sy), sk, st = septic_superellipse()
    print(f"septic superellipse |x|^7+|y|^7=1: max curvature at ({sx:.4f}, {sy:.4f})"
          f" — {st:.1f}° — k={sk:.3f}; at the axis crossing k=0")

    if "--check" in argv:
        problems = []
        # the two numbers the side chat got wrong, held as regressions
        if abs(table[2]["x"] - 0.5113) > 5e-4:
            problems.append(f"n=4 x_max {table[2]['x']:.4f} != 0.5113")
        if abs(hx - 1.049) > 5e-3 or abs(hy - 0.876) > 5e-3:
            problems.append(f"septic hyperbola ({hx:.3f},{hy:.3f}) != (1.049, 0.876)")
        if abs(st - 45.0) > 0.5:
            problems.append(f"superellipse maximum at {st:.1f}°, not 45°")
        for problem in problems:
            print(f"  {problem}")
        return 1 if problems else 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
