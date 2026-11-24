"""Crossing pairs of a polyline, counted once per segment pair.

Seven scripts grew their own double loop over every segment pair. On a 720-station trace that is
260k pair tests per curve; a coupler sweep of 729 linkages is 190M. This is the one counter: a
uniform grid over the segments, then the same strict-orientation test, so the answer is identical
to the brute-force loop (the test compares them on random polylines).

    crossing_pairs(points) -> int

A pair is (i, j) with j >= i + 2 — adjacent segments share an endpoint by construction — and the
meeting must be strictly inside both segments, so a vertex where the path merely touches does not
count. Crossing pairs, not places: a triple point is three pairs.

Two other counters in `scripts/` count **places** on purpose — `character_search.crossings` and
`lattice_circle_mobile.crossings` dedupe by the rounded meeting point, because their readers see a
place, not a pair. They are not duplicates of this one; do not "unify" them without changing what
their pages say. (`bezier_knots.crossings` and the coupler's are pair counts with this meaning.)
"""

from __future__ import annotations

import math


def _meet(points, i, j) -> bool:
    ax, ay = points[i]
    bx, by = points[i + 1]
    cx, cy = points[j]
    dx, dy = points[j + 1]
    denominator = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx)
    if abs(denominator) < 1e-12:
        return False
    s = ((cx - ax) * (dy - cy) - (cy - ay) * (dx - cx)) / denominator
    u = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / denominator
    return 0.0 < s < 1.0 and 0.0 < u < 1.0


def crossing_pairs(points) -> int:
    points = [(float(x), float(y)) for x, y in points]
    segments = len(points) - 1
    if segments < 3:
        return 0

    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    width = max(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    # roughly one segment per cell on average; long segments spill into their bbox cells
    cell = width / max(1.0, math.sqrt(segments))
    def cell_of(value, low):
        return int((value - low) // cell)

    x0, y0 = min(xs), min(ys)
    buckets: dict[tuple[int, int], list[int]] = {}
    for i in range(segments):
        ax, ay = points[i]
        bx, by = points[i + 1]
        cx0, cx1 = cell_of(min(ax, bx), x0), cell_of(max(ax, bx), x0)
        cy0, cy1 = cell_of(min(ay, by), y0), cell_of(max(ay, by), y0)
        for cx in range(cx0, cx1 + 1):
            for cy in range(cy0, cy1 + 1):
                buckets.setdefault((cx, cy), []).append(i)

    seen: set[tuple[int, int]] = set()
    count = 0
    for ids in buckets.values():
        for a in range(len(ids)):
            i = ids[a]
            for b in range(a + 1, len(ids)):
                j = ids[b]
                if j - i < 2:
                    continue
                key = (i, j)
                if key in seen:
                    continue
                seen.add(key)
                if _meet(points, i, j):
                    count += 1
    return count
