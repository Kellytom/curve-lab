"""Constant width: the Reuleaux triangle, at 60° and at the Pell limit.

    .venv/bin/python scripts/reuleaux.py

The Reuleaux triangle is three arcs of radius 1 centred on the vertices of an
equilateral triangle of side 1. Its width is 1 in every direction. The
equilateral triangle needs sin 60° = √3/2, and √3 is not a ratio of integers:
p-triples give rational sines and cosines, 60° is not one of their angles.
So the exact shape is drawn with √3 and is declared irrational; the Pell
copy uses 13/15 for √3/2 (from 26/15 → √3) and measures what that costs.
"""

from __future__ import annotations

import math

ROOT_SIN = math.sqrt(3.0) / 2.0          # sin 60°, irrational
PELL_SIN = 13.0 / 15.0                   # 26/15 approximates √3, so 13/15 the sine


def arc(centre, r, a0, a1, n=400):
    cx, cy = centre
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n),
             cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def reuleaux(sin60=ROOT_SIN):
    """Three unit arcs on the vertices A=(0,0), B=(1,0), C=(½, sin60)."""
    A, B = (0.0, 0.0), (1.0, 0.0)
    C = (0.5, sin60)
    aC = math.atan2(sin60, 0.5)                 # direction A → C
    aCB = math.atan2(sin60, -0.5)               # direction B → C (120°)
    pts = []
    pts += arc(A, 1.0, 0.0, aC)[:-1]            # B to C, about A
    pts += arc(B, 1.0, aCB, math.pi)[:-1]       # C to A, about B
    pts += arc(C, 1.0, math.pi + aC, 2 * math.pi - aC)  # A to B, about C
    return pts


def width(points, directions=720):
    """Max minus min projection, then the spread of that width over directions."""
    widths = []
    for k in range(directions):
        th = math.pi * k / directions
        nx, ny = math.cos(th), math.sin(th)
        proj = [p[0] * nx + p[1] * ny for p in points]
        widths.append(max(proj) - min(proj))
    return max(widths), min(widths), max(widths) - min(widths)


def closure_gap(points):
    """Distance between the last point and the first, for the Pell copy."""
    return math.dist(points[0], points[-1])


def cubic(p0, p1, p2, p3, n=80):
    out = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        out.append((mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0]
                    + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
                    mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1]
                    + 3 * mt * t * t * p2[1] + t ** 3 * p3[1]))
    return out


def bezier_arc(centre, r, a0, a1):
    """One cubic for a circular arc: handles on the tangents, length (4/3)tan(θ/4)r."""
    h = (4.0 / 3.0) * math.tan((a1 - a0) / 4.0) * r
    cx, cy = centre
    p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0))
    p3 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
    t0 = (-math.sin(a0), math.cos(a0))
    t3 = (-math.sin(a1), math.cos(a1))
    p1 = (p0[0] + h * t0[0], p0[1] + h * t0[1])
    p2 = (p3[0] - h * t3[0], p3[1] - h * t3[1])
    return p0, p1, p2, p3


def reuleaux_bezier(sin60=ROOT_SIN):
    """The Reuleaux triangle as three cubic arcs, with their control points."""
    A, B = (0.0, 0.0), (1.0, 0.0)
    C = (0.5, sin60)
    aC = math.atan2(sin60, 0.5)
    aCB = math.atan2(sin60, -0.5)
    arcs = [bezier_arc(A, 1.0, 0.0, aC),
            bezier_arc(B, 1.0, aCB, math.pi),
            bezier_arc(C, 1.0, math.pi + aC, 2 * math.pi - aC)]
    pts = []
    for p0, p1, p2, p3 in arcs:
        pts += cubic(p0, p1, p2, p3)
    return pts, arcs


def arc_error(arc, centre, r, n=400):
    """Maximum radial error of the cubic against the circle it approximates."""
    p0, p1, p2, p3 = arc
    worst = 0.0
    for x, y in cubic(p0, p1, p2, p3, n):
        worst = max(worst, abs(math.dist((x, y), centre) - r))
    return worst


def cases():
    exact = reuleaux(ROOT_SIN)
    pell = reuleaux(PELL_SIN)
    bez, arcs = reuleaux_bezier()
    err = max(arc_error(arc, c, 1.0) for arc, c in
              zip(arcs, [(0.0, 0.0), (1.0, 0.0), (0.5, ROOT_SIN)]))
    return [
        ("Reuleaux · 60° arcs", exact,
         "three unit arcs · width 1 · sin 60° is irrational, so declared outside NAMED",
         "scripts/reuleaux.py"),
        ("Reuleaux · Bézier handles at 60°", bez,
         f"three cubics, handle length (4/3)tan15° · radial error {err:.2e}",
         "scripts/reuleaux.py · one cubic per 60° arc"),
        ("Reuleaux · Pell limit 13/15", pell,
         f"the same arcs with 13/15 for sin 60° · closure gap {closure_gap(pell):.2e}",
         "scripts/reuleaux.py · Pell 26/15"),
    ]


if __name__ == "__main__":
    for title, pts, note, source in cases():
        wmax, wmin, spread = width(pts)
        print(f"{title}: width {wmin:.9f}..{wmax:.9f} (spread {spread:.2e}), "
              f"gap {closure_gap(pts):.2e}")
