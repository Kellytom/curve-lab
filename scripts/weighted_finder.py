"""Weighted derivative balance: sum w_k z^(k) = 0 at a chosen parameter.

    .venv/bin/python scripts/weighted_finder.py

The cascade idea, made into a curve. Each derivative gets a weight that decays —
exponentially (w_k = r^k) or like a parabola (w_k = 1/k^2) — and the weighted sum
of all derivative vectors is set to zero at a chosen t. In the swap family

    x = Q - P,  y = Q + P

that vector equation splits into two scalar ones, T_w(P) = 0 and T_w(Q) = 0, both
linear in the coefficients. Two coefficients are therefore solved, exactly, and
the rest choose the shape.

"The more north it goes, the less east" is this split: P carries the difference
(across the diagonal) and Q the sum (along it), so a balance in one is paid for
by the other.
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from math import factorial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from curve_lab.datafile import FORMATS  # noqa: E402
from finder_store import save_family  # noqa: E402
from curve_finder import peak  # noqa: E402

OUT = ROOT / "workbench" / "finder.json"
SAMPLES = 320
SPAN = (-1.0, 1.0)


def weighted_sum(poly, t, weights):
    """sum_k w_k * poly^(k) evaluated at t, with w_k from the weights list."""
    total = Fraction(0)
    for j, coefficient in enumerate(poly):
        if coefficient == 0:
            continue
        for k in range(1, j + 1):
            if k - 1 < len(weights):
                total += coefficient * weights[k - 1] * Fraction(factorial(j), factorial(j - k)) * t ** (j - k)
    return total


def weights_of(kind, count=8):
    if kind == "exp":
        r = Fraction(1, 2)
        return [r ** k for k in range(1, count + 1)]
    if kind == "flat":
        # 1/(2^k k!): every order contributes comparably, the Taylor terms
        # already carrying 1/k!, so the curve spends its motion evenly
        return [Fraction(1, 2 ** k * factorial(k)) for k in range(1, count + 1)]
    # parabola: 1/k^2, the decay a thrown object's height has with time
    return [Fraction(1, k * k) for k in range(1, count + 1)]


def solve(t0, kind):
    """b and e so that T_w(P)(t0) = 0 and T_w(Q)(t0) = 0."""
    w = weights_of(kind)
    base_P = [Fraction(0), Fraction(1), Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(1)]
    unit_P = [Fraction(0)] * 8
    unit_P[5] = Fraction(1)                     # b t^5
    b = -weighted_sum(base_P, t0, w) / weighted_sum(unit_P, t0, w)
    base_Q = [Fraction(1), Fraction(0), Fraction(0), Fraction(0), Fraction(1)]   # 1 + t^4
    unit_Q = [Fraction(0), Fraction(0), Fraction(1)]                             # e t^2
    e = -weighted_sum(base_Q, t0, w) / weighted_sum(unit_Q, t0, w)
    return b, e, w


def curve(b, e):
    P = [Fraction(0), Fraction(1), Fraction(0), Fraction(0), Fraction(0), b, Fraction(0), Fraction(1)]
    Q = [Fraction(1), Fraction(0), e, Fraction(0), Fraction(1)]
    n = max(len(P), len(Q))
    P += [Fraction(0)] * (n - len(P)); Q += [Fraction(0)] * (n - len(Q))
    return [q - p for p, q in zip(P, Q)], [q + p for p, q in zip(P, Q)]


def evaluate(poly, t):
    total = 0.0
    for c in reversed(poly):
        total = total * t + float(c)
    return total


def derivative(poly):
    return [poly[i] * i for i in range(1, len(poly))] or [Fraction(0)]


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
    curves = []
    for kind in ("exp", "parabola", "flat"):
        for t0 in (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)):
            b, e, _ = solve(t0, kind)
            x, y = curve(b, e)
            dx, dy = derivative(x), derivative(y)
            speeds = [math.hypot(evaluate(dx, ton), evaluate(dy, ton))
                      for ton in [SPAN[0] + (SPAN[1] - SPAN[0]) * i / 400 for i in range(401)]]
            p = peak(x, y, samples=800)
            points = path(x, y, *SPAN)
            curves.append({
                "name": f"{kind} balance at t={t0}",
                "coefficients": {"b": str(b), "e": str(e)},
                "definition": {"family": "weighted-balance", "kind": kind,
                               "t0": str(t0), "coefficients": {"b": str(b), "e": str(e)}},
                "degree": 7, "proper": True,
                "path": points, "rails": rails(points),
                "peak": None if p is None else {
                    "t": float(p["t"]), "kappa": float(p["kappa"]),
                    "angle": round(p["angle"], 2)},
                "features": {"crossing_pairs": 0, "tangent_45": [], "tangent_-45": []},
                "flags": [f"min speed {min(speeds):.3f}"],
            })
            print(f"{kind:9} t0={t0}  b={float(b):9.4f} e={float(e):9.4f}  min speed {min(speeds):.3f}")
    save_family("weighted-balance", curves, note="Weighted derivative balance at a chosen t.")
    print(f"wrote {OUT.relative_to(ROOT)} with {len(curves)} curves")
    return 0


if __name__ == "__main__":
    sys.exit(main())
