#!/usr/bin/env python3
"""Contact sheets for every hybrid candidate: p, q = 1…7 against every middle-term block.

    .venv/bin/python scripts/hybrid_sheets.py

Two families, because only one of them changes the shape:

    colour   the middle terms only tint the curve, so there are 49 shapes (one per p, q)
    radius   the polynomial scales each station, so there are 49 × 6 distinct figures

The stations are one pass round the rational circle: t = u/(1−|u|), u = i/100, so
nothing is drawn with sin or cos. The join between stations is a line, and every tile
says so at the sheet's foot.

Writes workbench/hybrid-sheets/*.svg and index.json.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import character_search as cs  # noqa: E402

OUT = ROOT / "workbench" / "hybrid-sheets"
N = 100
TILE = 168
GAP = 16
COLS = 7
POWERS = 7

BLOCKS = {
    "quadratic": [(2, 1, 1)],
    "cubic": [(3, 2, 1), (3, 1, 2)],
    "quintic central": [(10, 3, 2), (10, 2, 3)],
    "quintic all four": [(5, 4, 1), (10, 3, 2), (10, 2, 3), (5, 1, 4)],
    "cubic + quintic": [(3, 2, 1), (3, 1, 2), (5, 4, 1), (10, 3, 2), (10, 2, 3), (5, 1, 4)],
    "every term": [(2, 1, 1), (3, 2, 1), (3, 1, 2), (5, 4, 1), (10, 3, 2), (10, 2, 3), (5, 1, 4)],
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


def tile(index, points, label, sub):
    col, row = index % COLS, index // COLS
    x = GAP + col * (TILE + GAP)
    y = GAP + row * (TILE + 46)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    span = max(x1 - x0, y1 - y0) or 1
    pad = span * 0.08
    x0, x1, y0, y1 = x0 - pad, x1 + pad, y0 - pad, y1 + pad
    k = TILE / max(x1 - x0, y1 - y0)
    ox = x + (TILE - (x1 - x0) * k) / 2 - x0 * k
    oy = y + (TILE - (y1 - y0) * k) / 2 + y1 * k
    def px(p):
        return ox + p[0] * k, oy - p[1] * k
    d = "M" + " L".join(f"{px(p)[0]:.1f},{px(p)[1]:.1f}" for p in points[:: max(1, len(points) // 400)])
    # axes through the tile's own origin, if it is in view
    axes = ""
    if x0 <= 0 <= x1 and y0 <= 0 <= y1:
        a, b = px((x0, 0)), px((x1, 0))
        c, e = px((0, y0)), px((0, y1))
        axes = (f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#d9cdb8"/>'
                f'<line x1="{c[0]:.1f}" y1="{c[1]:.1f}" x2="{e[0]:.1f}" y2="{e[1]:.1f}" stroke="#d9cdb8"/>')
    return (f'<g><rect x="{x}" y="{y}" width="{TILE}" height="{TILE}" fill="#fffef9" stroke="#e6dccb"/>'
            f'{axes}<path d="{d}" fill="none" stroke="#2f6fa8" stroke-width="1.1"/>'
            f'<text x="{x + 4}" y="{y + TILE + 16}" font-size="15" fill="#3b2d1c">{label}</text>'
            f'<text x="{x + 4}" y="{y + TILE + 34}" font-size="15" fill="#7a6a55">{sub}</text></g>')


def sheet(title, note, tiles, rows):
    width = GAP + COLS * (TILE + GAP)
    height = 66 + rows * (TILE + 46) + GAP
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" role="img" aria-label="{title}">'
            f'<rect width="{width}" height="{height}" fill="#fffdf7"/>'
            f'<text x="{GAP}" y="34" font-size="17" font-weight="600" fill="#3b2d1c">{title}</text>'
            f'<text x="{GAP}" y="54" font-size="15" fill="#5a4a36">{note}</text>'
            f'{"".join(tiles)}</svg>')


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    index = []
    shapes = []
    for p in range(1, POWERS + 1):
        for q in range(1, POWERS + 1):
            xp = [power(C, p) for C, S in ST]
            yq = [power(S, q) for C, S in ST]
            base = list(zip(xp, yq))
            shapes.append((p, q, base))

    # the colour family: one shape per (p, q); the blocks are tints, not shapes
    tiles = []
    for i, (p, q, base) in enumerate(shapes):
        pts = [(float(x), float(y)) for x, y in base]
        tiles.append(tile(i, pts, f"p={p}, q={q}", f"{cs.crossings(pts)} pairs"))
        index.append({"use": "colour", "p": p, "q": q, "crossings": cs.crossings(pts)})
    path = OUT / "colour.svg"
    path.write_text(sheet("Fig. H-C · the 49 shapes, x = C^p, y = S^q",
                          "colour use: the middle-term polynomial tints the curve and does not move it.",
                          tiles, POWERS))
    sheets = [path.name]

    for n, (block_name, block) in enumerate(BLOCKS.items(), start=1):
        tiles = []
        for i, (p, q, base) in enumerate(shapes):
            pts = []
            for x, y in base:
                P = x * x + y * y
                for coefficient, ix, iy in block:
                    P += coefficient * power(x, ix) * power(y, iy)
                pts.append((float(x * P), float(y * P)))
            crossings = cs.crossings(pts)
            tiles.append(tile(i, pts, f"p={p}, q={q}", f"{crossings} pairs"))
            index.append({"use": "radius", "block": block_name, "p": p, "q": q,
                          "crossings": crossings})
        path = OUT / f"radius-{n}-{block_name.replace(' ', '-').replace('+', 'and')}.svg"
        path.write_text(sheet(f"Fig. H-R{n} · radius, {block_name} middle terms",
                              "radius use: each station is multiplied by P. Axes are the tile's own origin.",
                              tiles, POWERS))
        sheets.append(path.name)
        print(f"{path.name}: 49 tiles")

    (OUT / "index.json").write_text(json.dumps({
        "format": "curve-lab.hybrid-sheets/1",
        "parameter": "t = u/(1-|u|), u = i/100, i = -99..99",
        "powers": POWERS, "blocks": list(BLOCKS),
        "sheets": sheets, "candidates": index,
    }, indent=1) + "\n")
    print(f"wrote {len(sheets)} sheets and index.json to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
