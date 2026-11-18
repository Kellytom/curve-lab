"""Solved crossings, one curve per rational pair — systematic, not random.

    .venv/bin/python scripts/solved_finder.py

For each pair t1 < t2 the coefficients are *solved* so that z(t1) = z(t2):

    P(t) = t + d t^3 + b t^5 + t^7      (odd)
    Q(t) = 1 + e t^2 + c t^4            (even, c = 1)

    P(t1) = P(t2)  and  Q(t1) = Q(t2)   ->  d (or b) and e, exactly

Every curve therefore has a guaranteed crossing. What is left is quality:
whether the speed vanishes anywhere (a cusp), and what angle the two branches
make. Both are measured; the best are written to workbench/finder.json.
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

from curve_lab.datafile import FORMATS  # noqa: E402
from curve_finder import peak  # noqa: E402

OUT = ROOT / "workbench" / "finder.json"
PAIRS = [(Fraction(1, 5), Fraction(2, 5)), (Fraction(1, 5), Fraction(3, 5)),
         (Fraction(1, 4), Fraction(1, 2)), (Fraction(1, 4), Fraction(3, 4)),
         (Fraction(1, 3), Fraction(2, 3)), (Fraction(2, 5), Fraction(3, 5)),
         (Fraction(1, 2), Fraction(3, 4)), (Fraction(1, 3), Fraction(3, 4)),
         (Fraction(2, 5), Fraction(4, 5)), (Fraction(1, 5), Fraction(4, 5))]
KEEP = 8
SAMPLES = 320
SPAN = (-1.0, 1.0)


def solve(t1, t2, c=Fraction(1)):
    """d and e so P(t1)=P(t2) and Q(t1)=Q(t2), exactly."""
    def pw(a, n):
        return a ** n
    d = -((t1 - t2) + (pw(t1, 7) - pw(t2, 7))) / (pw(t1, 3) - pw(t2, 3))
    e = -c * (pw(t1, 4) - pw(t2, 4)) / (pw(t1, 2) - pw(t2, 2))
    return d, e


def curve(d, e, c=Fraction(1)):
    P = [Fraction(0), Fraction(1), Fraction(0), d, Fraction(0), Fraction(0), Fraction(0), Fraction(1)]
    Q = [Fraction(1), Fraction(0), e, Fraction(0), c]
    n = max(len(P), len(Q))
    P += [Fraction(0)] * (n - len(P)); Q += [Fraction(0)] * (n - len(Q))
    return [q - p for p, q in zip(P, Q)], [q + p for p, q in zip(P, Q)]


def evaluate(poly, t):
    total = 0.0
    for coefficient in reversed(poly):
        total = total * t + float(coefficient)
    return total


def derivative(poly):
    return [poly[i] * i for i in range(1, len(poly))] or [Fraction(0)]


def speed_at(x, y, t):
    dx, dy = derivative(x), derivative(y)
    return math.hypot(evaluate(dx, t), evaluate(dy, t))


def min_speed(x, y, samples=600):
    lo, hi = SPAN
    return min(speed_at(x, y, lo + (hi - lo) * i / samples) for i in range(samples + 1))


def tangent(x, y, t):
    dx, dy = derivative(x), derivative(y)
    return math.atan2(evaluate(dy, t), evaluate(dx, t))


def crossing_angle(x, y, t1, t2):
    """The acute angle between the two branches, in degrees."""
    a, b = tangent(x, y, float(t1)), tangent(x, y, float(t2))
    difference = abs(math.degrees(a - b)) % 180
    return min(difference, 180 - difference)


def path(x, y, lo, hi, steps=SAMPLES):
    return [[round(evaluate(x, lo + (hi - lo) * i / steps), 6),
             round(evaluate(y, lo + (hi - lo) * i / steps), 6)] for i in range(steps + 1)]


def rails(points, share=0.012):
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


def main():
    found = []
    for t1, t2 in PAIRS:
        d, e = solve(t1, t2)
        x, y = curve(d, e)
        m = min_speed(x, y)
        angle = crossing_angle(x, y, t1, t2)
        p = peak(x, y, samples=800)
        found.append({
            "name": f"cross {t1}–{t2}",
            "pair": [str(t1), str(t2)],
            "coefficients": {"d": str(d), "e": str(e), "c": "1"},
            "degree": 7,
            "proper": True,
            "path": path(x, y, *SPAN),
            "rails": rails(path(x, y, *SPAN)),
            "peak": None if p is None else {
                "t": float(p["t"]), "kappa": float(p["kappa"]),
                "angle": round(p["angle"], 2)},
            "crossing": {"angle": round(angle, 1), "min_speed": round(m, 4)},
            "features": {"crossing_pairs": 1, "tangent_45": [], "tangent_-45": []},
            "flags": ([] if m > 0.05 else ["cusp at the crossing"]) + [f"{angle:.0f}° branches"],
        })
    # Prefer a clean crossing: no cusp, and an angle near 90 degrees.
    found.sort(key=lambda item: (item["crossing"]["min_speed"] < 0.05,
                                 abs(item["crossing"]["angle"] - 90)))
    best = found[:KEEP]
    OUT.write_text(json.dumps({
        "format": FORMATS["finder.json"],
        "note": "Crossings solved at rational parameter pairs; ranked by cusp-free and right-angled.",
        "curves": best,
    }, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for item in best:
        c = item["crossing"]
        print(f'{item["name"]:20} angle {c["angle"]:5.1f}°  min speed {c["min_speed"]:6.3f}  '
              f'{"CUSP" if c["min_speed"] <= 0.05 else "clean"}')
    print(f"wrote {OUT.relative_to(ROOT)} with {len(best)} curves")
    return 0


if __name__ == "__main__":
    sys.exit(main())
