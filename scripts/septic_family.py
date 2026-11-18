"""The parametric septic family: x = Q - P, y = Q + P, with P odd and Q even.

    .venv/bin/python scripts/septic_family.py

Eight curves, different numbers, nothing assumed about symmetry. The point is to
look at them: what the coefficients do to the shape, where the curve crosses the
45-degree line, where the tangent is flat or vertical. The drawing goes to
workbench/finder.json for the /finder page.

P(t) = t^7 + b t^5 + d t^3 + k t        (the odd part)
Q(t) = a t^6 + c t^4 + e t^2           (the even part)

The curve meets y = x exactly where P = 0, and its tangent is at 45 degrees
exactly where P' = 0 — but those are consequences, not conditions here.
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
SAMPLES = 320
RAIL_SHARE = 0.012
SPAN = (-1.0, 1.0)

CURVES = (
    ("k only", dict(k=1)),
    ("b +1", dict(k=1, b=1)),
    ("b -1", dict(k=1, b=-1)),
    ("d -1", dict(k=1, d=-1)),
    ("d +1", dict(k=1, d=1)),
    ("a +1", dict(k=1, a=1)),
    ("c -1", dict(k=1, c=-1)),
    ("e +1", dict(k=1, e=1)),
    ("b,d mixed", dict(k=1, b=1, d=-1)),
    ("a,c,e mixed", dict(k=1, a=1, c=-1, e=1)),
    ("f +1", dict(k=1, f=1)),
    # Solved, not guessed: d chosen so P'(1/2) = 0 — a 45-degree tangent halfway.
    ("45deg at t=1/2", dict(k=1, d=Fraction(-71, 48))),
    ("45deg, b=1 at t=1/2", dict(k=1, b=1, d=Fraction(-91, 48))),
    # Solved crossings: two parameters forced onto one point.
    ("loop t=1/2,3/4", dict(k=1, d=Fraction(-6155, 4864), c=1, e=Fraction(-13, 16))),
    ("loop t=1/3,2/3", dict(k=1, d=Fraction(-856, 567), c=1, e=Fraction(-5, 9))),
    ("loop t=1/4,3/4", dict(k=1, d=Fraction(-5189, 3328), c=1, e=Fraction(-5, 8))),
    # Three conditions: cross at 1/4 and 3/4, and a 45° tangent at 1/4.
    ("cross+45deg at t=1/4", dict(k=1, b=Fraction(9443, 1192),
                                  d=Fraction(-235259, 38144), c=1, e=Fraction(-5, 8))),
    # Middle-dominant: t^4 outweighs t^7 inside |t| < 0.7, so it leaves the diagonal.
    ("c=10 middle", dict(k=1, c=10, e=-2)),
)


def build(spec):
    k = Fraction(spec.get("k", 1))
    a = Fraction(spec.get("a", 0))
    b = Fraction(spec.get("b", 0))
    c = Fraction(spec.get("c", 0))
    d = Fraction(spec.get("d", 0))
    e = Fraction(spec.get("e", 0))
    f = Fraction(spec.get("f", 0))
    P = [Fraction(0), k, Fraction(0), d, Fraction(0), b, Fraction(0), Fraction(1)]
    Q = [f, Fraction(0), e, Fraction(0), c, Fraction(0), a, Fraction(0)]
    x = [q - p for p, q in zip(P, Q)]
    y = [q + p for p, q in zip(P, Q)]
    return x, y


def evaluate(poly, t):
    total = 0.0
    for coefficient in reversed(poly):
        total = total * t + float(coefficient)
    return total


def derivative(poly):
    return [poly[i] * i for i in range(1, len(poly))] or [Fraction(0)]


def path(x, y, lo, hi, steps=SAMPLES):
    return [[round(evaluate(x, lo + (hi - lo) * i / steps), 6),
             round(evaluate(y, lo + (hi - lo) * i / steps), 6)] for i in range(steps + 1)]


def rails(points, share=RAIL_SHARE):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    size = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    d = share * size
    left, right = [], []
    for i, (px, py) in enumerate(points):
        a = points[max(0, i - 1)]
        b = points[min(len(points) - 1, i + 1)]
        vx, vy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(vx, vy) or 1.0
        nx, ny = -vy / length, vx / length
        left.append([round(px + d * nx, 6), round(py + d * ny, 6)])
        right.append([round(px - d * nx, 6), round(py - d * ny, 6)])
    return [left, right]


def cluster(values, gap=0.02):
    """Consecutive samples of one root collapse to a single number."""
    out = []
    for value in values:
        if out and abs(value - out[-1]) <= gap:
            out[-1] = (out[-1] + value) / 2
        else:
            out.append(value)
    return [round(v, 3) for v in out]


def readings(x, y, lo, hi):
    """Where the tangent is 45 degrees (P'=0) and where it is -45 (Q'=0)."""
    dx, dy = derivative(x), derivative(y)
    flat, vertical = [], []
    for i in range(0, 4001):
        t = lo + (hi - lo) * i / 4000
        vx, vy = evaluate(dx, t), evaluate(dy, t)
        if abs(vx - vy) < 0.01:
            flat.append(t)
        if abs(vx + vy) < 0.01:
            vertical.append(t)
    return {"tangent_45": cluster(flat), "tangent_-45": cluster(vertical)}


def main():
    curves = []
    for name, spec in CURVES:
        x, y = build(spec)
        points = path(x, y, *SPAN)
        p = peak(x, y, samples=1200)
        curves.append({
            "name": name,
            "x": [str(c) for c in x],
            "y": [str(c) for c in y],
            "spec": {k: str(v) for k, v in spec.items()},
            "degree": 7,
            "proper": True,
            "path": points,
            "rails": rails(points),
            "peak": None if p is None else {
                "t": float(p["t"]), "kappa": float(p["kappa"]),
                "angle": round(p["angle"], 3), "x": float(p["x"]), "y": float(p["y"])},
            "features": readings(x, y, *SPAN),
            "flags": [],
        })
        r = curves[-1]["features"]
        print(f'{name:14} 45deg at t={r["tangent_45"]}  -45deg at t={r["tangent_-45"]}')
    # The solved curves lead: they are the ones worth looking at.
    curves.sort(key=lambda c: 0 if ("loop" in c["name"] or "45deg" in c["name"]) else 1)
    OUT.write_text(json.dumps({
        "format": FORMATS["finder.json"],
        "note": "The parametric septic family, eight settings, nothing assumed.",
        "curves": curves,
    }, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} with {len(curves)} curves")
    return 0


if __name__ == "__main__":
    sys.exit(main())
