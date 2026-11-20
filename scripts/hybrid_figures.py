#!/usr/bin/env python3
"""One figure per hybrid candidate, and the list the desk reads.

    .venv/bin/python scripts/hybrid_figures.py

Writes app/public/hybrid-figures/<id>.svg (files, not one enormous page) and
workbench/hybrids.json. The stations are one pass of the rational circle,
t = u/(1−|u|), u = i/100: exact fractions, no sin, no cos.

Spec: state/SPEC-hybrids-int.md.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import character_search as cs  # noqa: E402

FIG = ROOT / "app" / "public" / "hybrid-figures"
OUT = ROOT / "workbench" / "hybrids.json"
N = 100
SIZE = 220
POWERS = 7

BLOCKS = {
    "quadratic": [(2, 1, 1)],
    "cubic": [(3, 2, 1), (3, 1, 2)],
    "quintic-central": [(10, 3, 2), (10, 2, 3)],
    "quintic-all-four": [(5, 4, 1), (10, 3, 2), (10, 2, 3), (5, 1, 4)],
    "cubic-and-quintic": [(3, 2, 1), (3, 1, 2), (5, 4, 1), (10, 3, 2), (10, 2, 3), (5, 1, 4)],
    "every-term": [(2, 1, 1), (3, 2, 1), (3, 1, 2), (5, 4, 1), (10, 3, 2), (10, 2, 3), (5, 1, 4)],
}


def power(value, n):
    out = Fraction(1)
    for _ in range(n):
        out *= value
    return out


def stations():
    out = []
    for i in range(-N + 1, N):
        u = Fraction(i, N)
        t = u / (1 - abs(u))
        out.append(((1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)))
    return out


ST = stations()


def figure(points, name, desc=""):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = (max(x1 - x0, y1 - y0) or 1) * 0.06
    x0, x1, y0, y1 = x0 - pad, x1 + pad, y0 - pad, y1 + pad
    k = SIZE / max(x1 - x0, y1 - y0)
    ox = (SIZE - (x1 - x0) * k) / 2 - x0 * k
    oy = (SIZE - (y1 - y0) * k) / 2 + y1 * k

    def px(p):
        return ox + p[0] * k, oy - p[1] * k

    step = max(1, len(points) // 400)
    d = "M" + " L".join(f"{px(p)[0]:.1f},{px(p)[1]:.1f}" for p in points[::step])
    axes = ""
    if x0 <= 0 <= x1 and y0 <= 0 <= y1:
        a, b = px((x0, 0)), px((x1, 0))
        c, e = px((0, y0)), px((0, y1))
        axes = (f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#e6dccb"/>'
                f'<line x1="{c[0]:.1f}" y1="{c[1]:.1f}" x2="{e[0]:.1f}" y2="{e[1]:.1f}" stroke="#e6dccb"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" '
            f'width="{SIZE}" height="{SIZE}" role="img" aria-label="{name}">'
            f'<title>{name}</title><desc>{desc}</desc>'
            f'<rect width="{SIZE}" height="{SIZE}" fill="#fffef9"/>{axes}'
            f'<path d="{d}" fill="none" stroke="#2f6fa8" stroke-width="1.2"/></svg>')


def middle_text(block):
    """P = x^2 + <the block's terms> + y^2, written for a reader."""
    block = BLOCKS.get(block, block)      # a block may arrive by name
    if block in ("none", None):
        block = []
    terms = ["x^2", "y^2"]
    for coefficient, ix, iy in block:
        part = f"{coefficient}*" if coefficient != 1 else ""
        part += (f"x^{ix}" if ix else "") + (f"*y^{iy}" if iy else "")
        terms.insert(len(terms) - 1, part)
    return "P = " + " + ".join(terms)


def formulas(p, q, use, block):
    """Three forms: what the internet calls it, what we compute, and how to search it."""
    plain = f"x = cos^{p}(t), y = sin^{q}(t)"
    internal = (f"x = C(t)^{p}, y = S(t)^{q}   with   "
                f"C(t) = (1 - t^2)/(1 + t^2), S(t) = 2t/(1 + t^2)")
    rational = (f"x = ((1 - t^2)/(1 + t^2))^{p}, "
                f"y = (2t/(1 + t^2))^{q}")
    if use == "colour":
        use_text = "P tints the curve; the shape is set by p and q alone"
    else:
        use_text = f"each station is multiplied by P, the {block} middle terms of (x + y)^n"
    return {
        "plain": plain,
        "internal": internal,
        "rational": rational,
        "middle": middle_text(block),
        "parameter": "t rational; stations at t = u/(1 - |u|), u = i/100",
        "use": use_text,
        "search": f"{plain}  {middle_text(block)}  parametric curve, rational parametrisation",
    }


def main() -> int:
    FIG.mkdir(parents=True, exist_ok=True)
    rows = []
    for p in range(1, POWERS + 1):
        for q in range(1, POWERS + 1):
            base = [(power(C, p), power(S, q)) for C, S in ST]
            pts = [(float(x), float(y)) for x, y in base]
            name = f"h-colour-{p}-{q}"
            formula = formulas(p, q, "colour", "none")
            (FIG / f"{name}.svg").write_text(figure(pts, name, formula["search"]))
            rows.append({"id": name, "p": p, "q": q, "use": "colour", "block": "none",
                         "crossings": cs.crossings(pts), "figure": f"{name}.svg",
                         "formula": formula})

            for block_name, block in BLOCKS.items():
                scaled = []
                for x, y in base:
                    P = x * x + y * y
                    for coefficient, ix, iy in block:
                        P += coefficient * power(x, ix) * power(y, iy)
                    scaled.append((float(x * P), float(y * P)))
                name = f"h-radius-{p}-{q}-{block_name}"
                formula = formulas(p, q, "radius", block_name)
                (FIG / f"{name}.svg").write_text(figure(scaled, name, formula["search"]))
                rows.append({"id": name, "p": p, "q": q, "use": "radius",
                             "block": block_name, "crossings": cs.crossings(scaled),
                             "figure": f"{name}.svg",
                             "formula": formula})

    OUT.write_text(json.dumps({
        "format": "curve-lab.hybrids/1",
        "parameter": "t = u/(1-|u|), u = i/100, i = -99..99",
        "powers": POWERS,
        "blocks": list(BLOCKS),
        "formulaConvention": "plain | rational | parameter | use | search; every record carries it",
        "candidates": rows,
    }, indent=1) + "\n")
    print(f"wrote {len(rows)} figures to {FIG.relative_to(ROOT)} and {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
