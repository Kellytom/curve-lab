"""One place that answers "where are the p-triangle joins, and are they on it".

The showcase and the dot solver both need the same three things:

1. a p-triple chain for each solid curve, in that curve's own frame;
2. a resolution high enough that the joins sit on the ink — solved, not fixed;
3. the join projected onto the curve, so a mark is never beside the curve,
   with the distance it had to move kept as the chain's fit error.

Keeping it here means the page that draws the marks and the page that audits
them cannot drift apart.
"""

from __future__ import annotations

import math

TOL_PX = 2.0
SCALE_PX = 336.0


def _dist_point_segment(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.dist(p, a)
    t = ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.dist(p, (ax + t * dx, ay + t * dy))


def nearest_on(points, p):
    """The closest point of a polyline, and how far away it was."""
    best, at = float("inf"), points[0]
    for a, b in zip(points, points[1:]):
        d = _dist_point_segment(p, a, b)
        if d < best:
            best = d
            ax, ay = a
            bx, by = b
            dx, dy = bx - ax, by - ay
            t = 0.0 if dx == 0 and dy == 0 else (
                ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy))
            t = max(0.0, min(1.0, t))
            at = (ax + t * dx, ay + t * dy)
    return at, best


def chain_of(points, n=24):
    """The p-triple chain for one curve, in that curve's own frame."""
    from curve_lab.euler_polygon import convert
    d = convert(points, n=n)
    x0, y0 = points[0]
    dx, dy = points[1][0] - points[0][0], points[1][1] - points[0][1]
    a = math.atan2(dy, dx)
    c, s = math.cos(a), math.sin(a)
    joins = [(x0 + X * c - Y * s, y0 + X * s + Y * c) for X, Y in d["polygon"]]
    return joins, d["chord"]


def solved_marks(curves, tol_px=TOL_PX, cap=25):
    """Marks for every solid curve: joins, on the curve, at a solved resolution.

    `curves` is a sequence of polylines. Returns a dict with the marks, the
    worst distance a join had to move (model units and panel pixels), the
    chain resolution used, and the chain chord so a caller can anchor its grid.
    """
    curves = [c for c in curves if c and len(c) > 3]
    if not curves:
        return {"marks": [], "fit": 0.0, "fit_px": 0.0, "chords": 0,
                "chord": 0.0}
    xs = [p[0] for c in curves for p in c]
    ys = [p[1] for c in curves for p in c]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    px_per_unit = SCALE_PX / span

    marks, worst, chords, chord = [], 0.0, 24, 0.0
    for pts in curves:
        if len(pts) < 8:                 # an explicit construction polyline
            marks.extend(pts[:cap])
            continue
        best = None
        for n in (24, 48, 96, 192, 384):
            try:
                joins, ch = chain_of(pts, n=n)
            except Exception:
                joins = []
            if not joins:
                continue
            err = max(nearest_on(pts, j)[1] for j in joins)
            if best is None or err < best[0]:
                best = (err, joins, n, ch)
            if err * px_per_unit <= tol_px:
                break
        if best is None:
            continue
        err, joins, n, ch = best
        if len(joins) > cap:
            stride = len(joins) / cap
            joins = [joins[int(i * stride)] for i in range(cap)]
        for j in joins:
            at, _ = nearest_on(pts, j)
            marks.append(at)
        worst = max(worst, err)
        chords, chord = n, float(ch)
    return {"marks": marks, "fit": worst, "fit_px": worst * px_per_unit,
            "chords": chords, "chord": chord}

def dot_finder(curves, step, cap=32):
    """Every dot the figure should carry: even spacing, both ends, no dupes.

    Guarantees, in order:
    - one dot per `step` of arc length, capped at `cap`, so no part of a curve
      is bare and no section is bunched;
    - both endpoints of every open curve, whatever the spacing did;
    - every dot lies on one of the input polylines;
    - no two dots at the same place.
    """
    curves = [c for c in curves if c and len(c) > 1]
    out = []
    for pts in curves:
        segs = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
        total = sum(segs)
        if total <= 0:
            out.append(pts[0])
            continue
        n = min(cap, max(2, int(round(total / (step or total))) + 1))
        targets = [total * i / (n - 1) for i in range(n)]
        acc, idx = 0.0, 0
        for want in targets:
            while idx < len(segs) and acc + segs[idx] < want:
                acc += segs[idx]
                idx += 1
            if idx >= len(segs):
                out.append(pts[-1])
                continue
            t = 0.0 if segs[idx] == 0 else (want - acc) / segs[idx]
            a, b = pts[idx], pts[idx + 1]
            out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
        if math.dist(pts[0], pts[-1]) > 1e-9:      # open: pin both ends
            out = [pts[0]] + out + [pts[-1]]
    seen, clean = set(), []
    for q in out:
        sig = (round(q[0], 9), round(q[1], 9))
        if sig not in seen:
            seen.add(sig)
            clean.append(q)
    return clean


def audit_dots(curves, marks, tol=1e-6):
    """(off_curve, missing_ends, max_gap_ratio) — the three failures worth naming."""
    curves = [c for c in curves if c and len(c) > 1]
    off = sum(1 for m in marks if nearest_on([q for c in curves for q in c], m)[1] > tol)
    missing = 0
    for c in curves:
        if math.dist(c[0], c[-1]) <= 1e-9:
            continue                            # closed: no ends to pin
        for end in (c[0], c[-1]):
            if not marks or min(math.dist(end, m) for m in marks) > tol:
                missing += 1
    gaps = [math.dist(a, b) for a, b in zip(marks, marks[1:])] if len(marks) > 1 else [0]
    med = sorted(gaps)[len(gaps) // 2] or 1.0
    return off, missing, (max(gaps) / med if med else 0.0)
