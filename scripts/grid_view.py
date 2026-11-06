"""The design lattice behind a figure: a round grid and its intersection marks.

One implementation, used by every figure renderer that draws curves on the
grid. A curve can cross hundreds of lattice points; an ornament needs a few
anchors, not a feather, so the marks are decimated to a small budget.
"""

from __future__ import annotations

import math

TARGET_LINES = 10   # aim for this many lines across the longer side
MAX_MARKS = 24      # lattice marks per figure, before decimation


def nice_step(span: float, target: int = TARGET_LINES) -> float:
    """A round step (1, 2, 2.5, 5 x 10^k) giving about `target` lines."""
    if span <= 0:
        return 1.0
    raw = span / target
    p = 10.0 ** math.floor(math.log10(raw))
    for k in (1.0, 2.0, 2.5, 5.0, 10.0):
        if raw <= k * p:
            return k * p
    return 10.0 * p


def grid_lines(put, x0: float, x1: float, y0: float, y1: float, step: float,
               colour: str, width: float = 0.5) -> list[str]:
    """Vertical and horizontal rules at every multiple of `step`."""
    out = []
    gx = math.floor(x0 / step) * step
    while gx <= x1 + 1e-9:
        a, b = put((gx, y0)), put((gx, y1))
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                   f'y2="{b[1]:.1f}" stroke="{colour}" stroke-width="{width}"/>')
        gx += step
    gy = math.floor(y0 / step) * step
    while gy <= y1 + 1e-9:
        a, b = put((x0, gy)), put((x1, gy))
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                   f'y2="{b[1]:.1f}" stroke="{colour}" stroke-width="{width}"/>')
        gy += step
    return out


def best_step(curves, span: float, target: int = TARGET_LINES) -> float:
    """The readable step that puts the most lattice hits on these curves.

    More hits is the point of the exercise: the grid is the field, and a curve
    that touches it more often is a better-placed curve. The search is bounded
    to 6–14 lines across, so the figure stays readable; a coarser step wins a
    tie.
    """
    base = nice_step(span, target)
    cands = [base * f for f in (1.5, 1.25, 1.0, 0.85, 0.75, 0.66, 0.6)]
    cands = [c for c in cands if 6 <= span / c <= 14] or [base]
    best, best_n = cands[0], -1
    for step in sorted(cands, reverse=True):
        n = len(crossings(curves, step, limit=10_000))
        if n > best_n:
            best, best_n = step, n
    return best

def crossings(curves, step: float, limit: int = MAX_MARKS,
              tol: float = 1e-3) -> list[tuple[float, float]]:
    """Where each solid curve crosses a grid line — the lattice's own marks.

    This is `plant.lattice_hits`' method, applied to both axes: walk each
    segment, take the point where it meets x = k·step or y = k·step. One mark
    per crossing, deduped, thinned to `limit` so a dense curve reads as an
    ornament and not as a feather. `tol` is unused for exact crossings; it is
    kept for callers that pass a sample tolerance.
    """
    seen, cand = set(), []

    def add(axis, k, x, y, ci):
        key = (ci, axis, k)
        if key not in seen:
            seen.add(key)
            cand.append((x, y))

    for ci, pts in enumerate(curves):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x1 != x0:
                g = math.ceil(min(x0, x1) / step) * step
                while g <= max(x0, x1) + 1e-12:
                    t = (g - x0) / (x1 - x0)
                    if 0.0 <= t <= 1.0:
                        add("x", round(g / step), g, y0 + t * (y1 - y0), ci)
                    g += step
            if y1 != y0:
                g = math.ceil(min(y0, y1) / step) * step
                while g <= max(y0, y1) + 1e-12:
                    t = (g - y0) / (y1 - y0)
                    if 0.0 <= t <= 1.0:
                        add("y", round(g / step), x0 + t * (x1 - x0), g, ci)
                    g += step
    if len(cand) > limit:
        stride = len(cand) / limit
        cand = [cand[int(i * stride)] for i in range(limit)]
    return cand
