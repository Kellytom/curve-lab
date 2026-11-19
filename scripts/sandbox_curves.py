#!/usr/bin/env python3
"""Two sandboxes' worth of data, computed once and written as JSON.

    .venv/bin/python scripts/sandbox_curves.py

Writes `workbench/sandbox-curves.json` (format curve-lab.sandbox/1):

1. **The visual adder.** For each named polynomial, every term sampled on its
   own over the same window, and the sum sampled over the same window. The page
   draws one small figure per term, three across, then a large figure for the
   sum — so the reader sees the sum being made.

2. **The imaginary variable.** For each coefficient list, the curve at `z = b i`:
   even powers give x, odd powers give y, signs rotate. The degenerate case is
   kept and explained rather than dropped.

Sampling only; the page claims no exactness for a drawing. The imaginary cases
also carry exact numbers (grid, inflections) from the one core.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import measure  # noqa: E402

OUT = ROOT / "workbench" / "sandbox-curves.json"
WINDOW = 1.25
POINTS = 121

VIZ = [
    {"name": "the operator's alternating odd", "terms": [[1, 1], [-1, 3], [1, 5], [-1, 7]],
     "note": "signs alternate, powers odd, coefficients one"},
    {"name": "the plain climb", "terms": [[1, 1], [1, 2], [1, 3], [1, 4]],
     "note": "every power from 1 to 4, all adding the same way"},
    {"name": "the folded leaf", "terms": [[1, 1], [-2, 3], [1, 5]],
     "note": "the cubic doubled and negative, so the middle folds back"},
    {"name": "the parabola alone", "terms": [[1, 0], [-1, 2]],
     "note": "one even term: the simplest curve the adder can show"},
    {"name": "high mixed", "terms": [[1, 7], [-1, 6], [1, 5], [-1, 4]],
     "note": "mixed parity at degree 7: this is also the shape the imaginary variable needs"},
]

# Coefficients by power, lowest first: P(z) = sum a_k z^k.
IMAGINARY = [
    {"name": "odd only", "coeffs": [0, 1, 0, -1, 0, 1, 0, -1],
     "note": "every odd power of i b is imaginary, so x is identically zero: a vertical line"},
    {"name": "one even term added", "coeffs": [0, 1, 0, -1, 0, 1, 1, -1],
     "note": "one even term is enough to open the curve; x is that term, sign-rotated"},
    {"name": "even and odd balanced", "coeffs": [0, 1, 1, -1, -1, 1, 1, -1],
     "note": "both parities at every power: the widest curve the substitution makes"},
]


def sample(terms):
    xs = [-WINDOW + (2 * WINDOW * i) / (POINTS - 1) for i in range(POINTS)]
    y = [sum(c * (x ** p) for c, p in terms) for x in xs]
    return [[round(x, 5), round(v, 5)] for x, v in zip(xs, y)]


def imaginary_rows(coeffs):
    """P(i b): even powers -> x, odd powers -> y, with the sign of i^k."""
    x = [0] * len(coeffs)
    y = [0] * len(coeffs)
    for k, a in enumerate(coeffs):
        if k % 2 == 0:
            x[k] = a * (-1) ** (k // 2)
        else:
            y[k] = a * (-1) ** ((k - 1) // 2)
    while len(x) > 1 and x[-1] == 0:
        x.pop()
    while len(y) > 1 and y[-1] == 0:
        y.pop()
    return x, y


def deriv(row):
    return [i * row[i] for i in range(1, len(row))] or [0]


def imaginary(curve):
    x, y = imaginary_rows(curve["coeffs"])
    degenerate = len(x) == 1 and x[0] == 0
    result = {"name": curve["name"], "note": curve["note"], "x": x, "y": y, "degenerate": degenerate}
    if not degenerate:
        speeds = (deriv(x), deriv(y))
        m = measure.metrics(*speeds)
        result["grid"] = int(m["grid"])
        result["inflections"] = int(m["inflection_count"])
        result["bend"] = round(float(m["bend"]), 4)
        # sample the parametric curve for the small figure
        pts = []
        for i in range(POINTS):
            b = -WINDOW + (2 * WINDOW * i) / (POINTS - 1)
            pts.append([sum(c * b ** k for k, c in enumerate(x)),
                        sum(c * b ** k for k, c in enumerate(y))])
        result["points"] = [[round(a, 5), round(b, 5)] for a, b in pts]
    return result


def main() -> int:
    adders = []
    for item in VIZ:
        terms = [tuple(t) for t in item["terms"]]
        adders.append({
            "name": item["name"],
            "note": item["note"],
            "terms": [{"coef": c, "power": p, "points": sample([(c, p)])} for c, p in terms],
            "sum": sample(terms),
        })

    payload = {
        "format": "curve-lab.sandbox/1",
        "window": WINDOW,
        "note": "sampled drawings for the two sandboxes; the imaginary cases also carry exact grid and inflections",
        "adders": adders,
        "imaginary": [imaginary(curve) for curve in IMAGINARY],
    }
    OUT.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(adders)} adders, {len(payload['imaginary'])} imaginary curves")
    for curve in payload["imaginary"]:
        if curve["degenerate"]:
            print(f"  {curve['name']}: degenerate (x is a point)")
        else:
            print(f"  {curve['name']}: grid {curve['grid']}, inflections {curve['inflections']}, bend {curve['bend']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
