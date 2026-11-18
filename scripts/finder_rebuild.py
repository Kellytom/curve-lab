"""Rebuild a chosen curve from its definition, exactly.

    .venv/bin/python scripts/finder_rebuild.py            # check every definition
    .venv/bin/python scripts/finder_rebuild.py --check    # same, exit 1 on a mismatch

A star is a curve *chosen*, so the definition must be enough to reproduce it:
coefficients and parameters, not sampled points. This reads each curve's
`definition` from workbench/finder.json, rebuilds the position polynomials, and
compares the resulting path with the one stored — a chain of custody from a
chosen curve back to its numbers.
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FINDER = ROOT / "workbench" / "finder.json"
SPAN = (-1.0, 1.0)
SAMPLES = 320


def build_septic(spec):
    k = Fraction(spec.get("k", 1)); a = Fraction(spec.get("a", 0))
    b = Fraction(spec.get("b", 0)); c = Fraction(spec.get("c", 0))
    d = Fraction(spec.get("d", 0)); e = Fraction(spec.get("e", 0))
    f = Fraction(spec.get("f", 0))
    P = [Fraction(0), k, Fraction(0), d, Fraction(0), b, Fraction(0), Fraction(1)]
    Q = [f, Fraction(0), e, Fraction(0), c, Fraction(0), a, Fraction(0)]
    return [q - p for p, q in zip(P, Q)], [q + p for p, q in zip(P, Q)]


def build_solved(definition):
    pair = definition["pair"]; coeff = definition["coefficients"]
    d = Fraction(coeff["d"]); e = Fraction(coeff["e"]); c = Fraction(coeff.get("c", 1))
    P = [Fraction(0), Fraction(1), Fraction(0), d, Fraction(0), Fraction(0), Fraction(0), Fraction(1)]
    Q = [Fraction(1), Fraction(0), e, Fraction(0), c]
    n = max(len(P), len(Q))
    P += [Fraction(0)] * (n - len(P)); Q += [Fraction(0)] * (n - len(Q))
    return [q - p for p, q in zip(P, Q)], [q + p for p, q in zip(P, Q)]


def build_bounded(spec):
    def value(t, a, b, c):
        a, b, c = float(a), float(b), float(c)
        return (a * t * t + b * t + c) / (1 + t * t)
    if "polar" in spec:
        a, b = float(spec["polar"][0]), float(spec["polar"][1])
        return ("polar", a, b)
    return ("poly", spec)


def evaluate(poly, t):
    total = 0.0
    for coefficient in reversed(poly):
        total = total * t + float(coefficient)
    return total


def path_of(x, y, samples=SAMPLES):
    lo, hi = SPAN
    return [[round(evaluate(x, lo + (hi - lo) * i / samples), 6),
             round(evaluate(y, lo + (hi - lo) * i / samples), 6)] for i in range(samples + 1)]


def rebuild(definition):
    family = definition.get("family")
    if family == "septic":
        return path_of(*build_septic(definition["spec"]))
    if family == "solved-crossings":
        return path_of(*build_solved(definition))
    return None  # weighted, bounded and mobile are checked by their own scripts


def main(argv):
    data = json.loads(FINDER.read_text(encoding="utf-8"))
    checked = mismatched = rebuilt = 0
    for curve in data["curves"]:
        definition = curve.get("definition")
        if not definition:
            continue
        points = rebuild(definition)
        if points is None:
            continue
        checked += 1
        stored = curve.get("path") or []
        if len(points) != len(stored):
            mismatched += 1
            print(f"{curve['name']}: stored path has {len(stored)} points, rebuilt {len(points)}")
            continue
        worst = max(math.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(points, stored))
        if worst > 1e-4:
            mismatched += 1
            print(f"{curve['name']}: rebuilt path differs by {worst:.2e}")
        else:
            rebuilt += 1
    print(f"{checked} definitions checked · {rebuilt} rebuilt within 1e-4 · {mismatched} mismatched")
    return 1 if mismatched and "--check" in argv else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
