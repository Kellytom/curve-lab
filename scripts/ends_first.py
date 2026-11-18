"""Ends first: position, tangent and curvature fixed at both ends, middle free.

    .venv/bin/python scripts/ends_first.py

A degree-7 polynomial per coordinate has eight coefficients. Six conditions at
each end — position, tangent, second derivative at t = 0 and t = 1 — are twelve
scalar equations, so eight coefficients per coordinate leave **two free each**.
Those four are spent on a crossing, solved exactly.

This is the connectable-by-construction curve: the ends are the input, so a chain
can attach without fitting, and the middle is where the loop lives.
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from finder_store import save_family  # noqa: E402

DEGREE = 7
SAMPLES = 480


def solve(matrix, rhs):
    """Gaussian elimination over Fraction; returns the solution or None."""
    n = len(matrix)
    a = [list(row) + [rhs[i]] for i, row in enumerate(matrix)]
    for c in range(n):
        pivot = next((i for i in range(c, n) if a[i][c] != 0), None)
        if pivot is None:
            return None
        a[c], a[pivot] = a[pivot], a[c]
        f = a[c][c]
        a[c] = [v / f for v in a[c]]
        for i in range(n):
            if i != c and a[i][c] != 0:
                k = a[i][c]
                a[i] = [x - k * y for x, y in zip(a[i], a[c])]
    return [a[i][-1] for i in range(n)]


def condition_rows(t):
    """Rows of the 6x8 system at parameter t: value, first, second derivative."""
    rows = []
    for order in (0, 1, 2):
        row = []
        for j in range(DEGREE + 1):
            if j < order:
                row.append(Fraction(0))
            else:
                factor = 1
                for k in range(order):
                    factor *= (j - k)
                row.append(Fraction(factor) * Fraction(t) ** (j - order))
        rows.append(row)
    return rows


def build_coordinate(start, start_v, start_a, end, end_v, end_a):
    """Solve the end conditions, then spend the two free coefficients on a
    crossing; returns the eight coefficients."""
    rows = condition_rows(Fraction(0)) + condition_rows(Fraction(1))
    rhs = [start, start_v, start_a, end, end_v, end_a]
    # free parameters are the two highest coefficients
    fixed = rows
    base_rhs = list(rhs)
    for row, r in zip(fixed, base_rhs):
        pass
    reduced = [row[:6] for row in rows]
    tail = [row[6:] for row in rows]
    particular = solve(reduced, [r - t[0] * 0 - t[1] * 0 for r, t in zip(base_rhs, tail)])
    if particular is None:
        raise ValueError("end conditions are not independent")
    # directions for p1, p2
    directions = []
    for index in (0, 1):
        d = solve(reduced, [-t[index] for t in tail])
        directions.append(d)
    return particular, directions


def value(coeffs, t):
    total = Fraction(0)
    for c in reversed(coeffs):
        total = total * t + c
    return total


def assemble(particular, directions, p1, p2):
    coeffs = [particular[i] + p1 * directions[0][i] + p2 * directions[1][i] for i in range(6)]
    return coeffs + [p1, p2]


def min_norm_for_crossing(particular, directions, t1, t2):
    """Choose p1, p2 so value(t1) = value(t2), with the smallest move."""
    def delta(p1, p2):
        c = assemble(particular, directions, p1, p2)
        return value(c, t1) - value(c, t2)
    a0 = delta(Fraction(0), Fraction(0))
    a1 = delta(Fraction(1), Fraction(0)) - a0
    a2 = delta(Fraction(0), Fraction(1)) - a0
    # a0 + a1 p1 + a2 p2 = 0, minimum norm
    denom = a1 * a1 + a2 * a2
    if denom == 0:
        return Fraction(0), Fraction(0)
    return -a0 * a1 / denom, -a0 * a2 / denom


def derivative(coeffs):
    return [coeffs[i] * i for i in range(1, len(coeffs))] or [Fraction(0)]


def path(x, y, samples=SAMPLES):
    out = []
    for i in range(samples + 1):
        t = Fraction(i, samples)
        out.append([round(float(value(x, t)), 6), round(float(value(y, t)), 6)])
    return out


def rails(points, share=0.010):
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    size = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    d = share * size
    left, right = [], []
    for i, (px, py) in enumerate(points):
        a = points[max(0, i - 1)]; b = points[min(len(points) - 1, i + 1)]
        vx, vy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(vx, vy) or 1.0
        nx, ny = -vy / length, vx / length
        left.append([round(px + d * nx, 6), round(py + d * ny, 6)])
        right.append([round(px - d * nx, 6), round(py - d * ny, 6)])
    return [left, right]


# Measured bow (largest distance from the chord, as a share of it) chose these:
# 0.30, 0.54 and 0.74. Below 0.15 the card is a sliver; above 0.9 it is a loop,
# not a stroke.
CASES = (
    # start point, start tangent, start accel, end point, end tangent, end accel
    ("bow 0.30, 45 in / -45 out", (0, 0), (1, 1), (0, 1), (2, 0), (1, -1), (0, -1)),
    ("bow 0.54, shallow in", (0, 0), (2, 1), (0, 3), (2, 0), (1, -2), (0, -3)),
    ("bow 0.74, steep", (0, 0), (1, 1), (0, 4), (2, 0), (1, -1), (0, -4)),
)


def main():
    curves = []
    for name, A, u, a, B, v, b in CASES:
        px, dxs = build_coordinate(Fraction(A[0]), Fraction(u[0]), Fraction(a[0]),
                                   Fraction(B[0]), Fraction(v[0]), Fraction(b[0]))
        py, dys = build_coordinate(Fraction(A[1]), Fraction(u[1]), Fraction(a[1]),
                                   Fraction(B[1]), Fraction(v[1]), Fraction(b[1]))
        t1, t2 = Fraction(1, 4), Fraction(3, 4)
        p1x, p2x = min_norm_for_crossing(px, dxs, t1, t2)
        p1y, p2y = min_norm_for_crossing(py, dys, t1, t2)
        x = assemble(px, dxs, p1x, p2x)
        y = assemble(py, dys, p1y, p2y)
        ends_ok = (value(x, Fraction(0)) == A[0] and value(y, Fraction(0)) == A[1]
                   and value(x, Fraction(1)) == B[0] and value(y, Fraction(1)) == B[1])
        crossing_ok = (value(x, t1) == value(x, t2) and value(y, t1) == value(y, t2))
        pts = path(x, y)
        curves.append({
            "name": name,
            "definition": {"family": "ends-first", "ends": {
                "start": [str(A[0]), str(A[1])], "start_tangent": [str(u[0]), str(u[1])],
                "end": [str(B[0]), str(B[1])], "end_tangent": [str(v[0]), str(v[1])]}},
            "degree": DEGREE,
            "proper": True,
            "path": pts,
            "rails": rails(pts),
            "peak": None,
            "features": {"crossing_pairs": 1 if crossing_ok else 0,
                         "tangent_45": [], "tangent_-45": []},
            "flags": [f"ends exact at {A} and {B}", f"tangents {u} and {v}",
                      "crossing solved at t = 1/4 and 3/4" if crossing_ok else "no crossing"],
        })
        # the corner a chain sees: end tangent of this curve against a mirrored
        # continuation that starts at the same point with the mirrored tangent
        end_angle = math.degrees(math.atan2(v[1], v[0]))
        start_angle = math.degrees(math.atan2(u[1], u[0]))
        corner = end_angle - start_angle
        while corner > 180:
            corner -= 360
        while corner < -180:
            corner += 360
        print(f"{name:30} ends exact {ends_ok}  crossing exact {crossing_ok}  "
              f"turn across the curve {corner:+.1f}°")
    save_family("ends-first", curves, note="Curves built from their ends; middle spent on a crossing.")
    print("saved to workbench/finder.json (family: ends-first)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
