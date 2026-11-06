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


def crossings(curves, step: float, limit: int = MAX_MARKS,
              tol: float = 1e-3) -> list[tuple[float, float]]:
    """Points where a solid curve crosses a grid intersection, interpolated.

    `curves` is a sequence of point lists. `tol` is in grid steps: the chord
    error of a sampled polyline is about 1e-5 of a step, so 1e-3 keeps true
    hits and rejects arbitrary near-misses.
    """
    seen, cand = set(), []

    def add(kx, ky, x, y):
        if (kx, ky) not in seen:
            seen.add((kx, ky))
            cand.append((x, y))

    for pts in curves:
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x1 != x0:
                g = math.ceil(min(x0, x1) / step) * step
                while g <= max(x0, x1) + 1e-12:
                    t = (g - x0) / (x1 - x0)
                    if 0.0 <= t <= 1.0:
                        y = y0 + t * (y1 - y0)
                        ky = round(y / step)
                        if abs(y - ky * step) <= tol * step:
                            add(round(g / step), ky, g, ky * step)
                    g += step
            if y1 != y0:
                g = math.ceil(min(y0, y1) / step) * step
                while g <= max(y0, y1) + 1e-12:
                    t = (g - y0) / (y1 - y0)
                    if 0.0 <= t <= 1.0:
                        x = x0 + t * (x1 - x0)
                        kx = round(x / step)
                        if abs(x - kx * step) <= tol * step:
                            add(kx, round(g / step), kx * step, g)
                    g += step
    if len(cand) > limit:
        stride = len(cand) / limit
        cand = [cand[int(i * stride)] for i in range(limit)]
    return cand
