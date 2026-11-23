"""Side curves for a sampled outline, using the plate's own law.

The proposal figures on /extra-curves/ have no speed pair, only stations. So the side curves
here are computed the same way the plate treats a stored path:

    distance = base * (1 + strength * profile(t))

on the outside of a turn, and capped at `0.9 / curvature` on the inside, because only the
inside can fold. Nothing is stored; this is a drawing of what the plate would do.
"""

import math


def _normals(points):
    out = []
    n = len(points)
    for i in range(n):
        a = points[max(0, i - 1)]
        b = points[min(n - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        length = math.hypot(tx, ty) or 1.0
        out.append((-ty / length, tx / length))
    return out


def _curvature(points):
    """turn per unit length at each station (signed: + means the centre is on the + normal)"""
    n = len(points)
    out = []
    for i in range(n):
        a0 = points[max(0, i - 1)]
        a1 = points[i]
        b0 = points[i]
        b1 = points[min(n - 1, i + 1)]
        v1 = (a1[0] - a0[0], a1[1] - a0[1])
        v2 = (b1[0] - b0[0], b1[1] - b0[1])
        l1 = math.hypot(*v1) or 1.0
        l2 = math.hypot(*v2) or 1.0
        cross = (v1[0] * v2[1] - v1[1] * v2[0]) / (l1 * l2)
        dot = (v1[0] * v2[0] + v1[1] * v2[1]) / (l1 * l2)
        turn = math.atan2(max(-1.0, min(1.0, cross)), max(-1.0, min(1.0, dot)))
        step = 0.5 * (l1 + l2) or 1.0
        out.append((turn / step, 1 if turn > 0 else (-1 if turn < 0 else 0)))
    return out


def side_curves(points, width_percent=2.0, strength=1.3):
    """Two side curves for `points`, at the asked width, capped on the inside only."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    size = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    base = width_percent / 100.0 * size
    normals = _normals(points)
    curvature = _curvature(points)
    n = len(points)
    right, left = [], []
    for i, p in enumerate(points):
        t = i / (n - 1)
        bow = 4 * t * (1 - t)
        want = base * (1 + strength * bow)
        k, side = curvature[i]
        out_r = p[0] + want * normals[i][0], p[1] + want * normals[i][1]
        out_l = p[0] - want * normals[i][0], p[1] - want * normals[i][1]
        if side == 1:            # the + normal points at the centre: that side is inside
            kappa = abs(k) if abs(k) > 1e-9 else 0.0
            if kappa:
                safe = 0.9 / kappa
                d = min(want, safe)
                out_r = p[0] + d * normals[i][0], p[1] + d * normals[i][1]
        elif side == -1:
            kappa = abs(k) if abs(k) > 1e-9 else 0.0
            if kappa:
                safe = 0.9 / kappa
                d = min(want, safe)
                out_l = p[0] - d * normals[i][0], p[1] - d * normals[i][1]
        right.append(out_r)
        left.append(out_l)
    return left, right


def line_path(points, to_pixel, colour, width):
    d = "M " + " L ".join(
        f"{to_pixel(p)[0]:.1f} {to_pixel(p)[1]:.1f}" for p in points
    )
    return (f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')
