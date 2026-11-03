"""Plant-form geometry: endings, lattice growth marks, and branches.

The plant-form sequence after the offset catalogue:

- a **cone terminal** of two arcs, radius 2 × offset, one from each rail,
  meeting at the centreline tip (a cone, not a round cap);
- a **seagrass** ending of three blades;
- a **flower** head;
- **growth marks** — a pyramid on each rail at an integer-lattice hit;
- **branches** — smaller curves from selected growth points, lower bigger
  than upper.

Coordinates are model space, +y up. The page flips y once at SVG output.
"""

from __future__ import annotations

import math


def frame(tangent):
    """Unit tangent and left normal (model +y up)."""
    length = math.hypot(*tangent) or 1.0
    tx, ty = tangent[0] / length, tangent[1] / length
    return (tx, ty), (-ty, tx)


def _arc(center, radius, a0, a1, n=28):
    out = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        out.append((center[0] + radius * math.cos(a),
                    center[1] + radius * math.sin(a)))
    return out


def cone_terminal(point, tangent, offset, n=28):
    """Two tangent arcs, R = 2 × offset, meeting at the centreline.

    The rail ends are ``point ± offset·N``; the tip is ``point + √3·offset·T``.
    The arcs are tangent to the rails at their bases and meet at a point, so
    the end is a cone. Returns both arc points, the tip, the radius and the
    extension.
    """
    T, N = frame(tangent)
    w = float(offset)
    R = 2.0 * w
    a = (point[0] + w * N[0], point[1] + w * N[1])       # left rail
    b = (point[0] - w * N[0], point[1] - w * N[1])       # right rail
    tip = (point[0] + math.sqrt(3.0) * w * T[0],
           point[1] + math.sqrt(3.0) * w * T[1])
    ca = (a[0] - R * N[0], a[1] - R * N[1])
    cb = (b[0] + R * N[0], b[1] + R * N[1])

    def angle(c, p):
        return math.atan2(p[1] - c[1], p[0] - c[0])

    def sweep(start, end):
        d = math.atan2(math.sin(end - start), math.cos(end - start))
        return d

    a0, a1 = angle(ca, a), angle(ca, tip)
    left = _arc(ca, R, a0, a0 + sweep(a0, a1), n)
    b0, b1 = angle(cb, b), angle(cb, tip)
    right = _arc(cb, R, b0, b0 + sweep(b0, b1), n)
    return {"left": left, "right": right, "tip": tip,
            "rails": (a, b), "radius": R, "extension": math.sqrt(3.0) * w}


def seagrass(point, tangent, offset, blades=3, n=24):
    """A fan of tapered blades; the centre blade is the longest."""
    T, N = frame(tangent)
    out = []
    angles = [-0.48, 0.0, 0.48] if blades == 3 else [
        -0.55 + 1.1 * i / max(blades - 1, 1) for i in range(blades)]
    lengths = [2.3, 2.9, 2.3] if blades == 3 else [
        2.1 + 0.8 * math.cos(a) for a in angles]
    for k, (ang, mult) in enumerate(zip(angles, lengths)):
        ca, sa = math.cos(ang), math.sin(ang)
        d = (T[0] * ca - T[1] * sa, T[0] * sa + T[1] * ca)
        length = offset * mult
        pts = []
        for i in range(n + 1):
            t = i / n
            # a slight outward bend; the blade stays a thin line
            bend = math.sin(math.pi * t) * 0.28 * length * (k - 1)
            pts.append((point[0] + d[0] * length * t + N[0] * bend,
                        point[1] + d[1] * length * t + N[1] * bend))
        out.append(pts)
    return out


def flower(point, tangent, offset, petals=6, n=180):
    """A simple rosette head; one petal points along the stalk tangent."""
    T, N = frame(tangent)
    radius = 2.3 * offset
    center = (point[0] + 2.0 * offset * T[0],
              point[1] + 2.0 * offset * T[1])
    out = []
    for i in range(n + 1):
        th = 2 * math.pi * i / n
        r = radius * (0.58 + 0.42 * math.cos(petals * th))
        # rotate so a petal points along the stalk
        ang = th + math.atan2(T[1], T[0]) - math.pi / 2
        out.append((center[0] + r * math.cos(ang),
                    center[1] + r * math.sin(ang)))
    return out


def lattice_hits(points, step=1.0):
    """Where the stalk crosses horizontal integer-grid lines.

    The hit is a point on the centreline and its local tangent. A curve that
    crosses *both* coordinates exactly is rarer; these are the grid-line hits
    the growth marks sit on, which is what the vine mark needs.
    """
    if len(points) < 2:
        return []
    ys = [p[1] for p in points]
    lo, hi = min(ys), max(ys)
    out = []
    k = math.ceil(lo / step)
    while k * step <= hi:
        level = k * step
        for i in range(len(points) - 1):
            y0, y1 = points[i][1], points[i + 1][1]
            if (y0 <= level <= y1) or (y1 <= level <= y0):
                if abs(y1 - y0) < 1e-12:
                    continue
                t = (level - y0) / (y1 - y0)
                x = points[i][0] + t * (points[i + 1][0] - points[i][0])
                dx = points[i + 1][0] - points[i][0]
                dy = points[i + 1][1] - points[i][1]
                out.append({"point": (x, level), "tangent": (dx, dy),
                            "value": level, "index": i, "t": t})
                break
        k += 1
    return out


def pyramid(rail_point, tangent, outward, size):
    """A small triangle with its base on the rail and its apex outward."""
    T, _ = frame(tangent)
    sx, sy = size
    base = [(rail_point[0] - sx * T[0], rail_point[1] - sx * T[1]),
            (rail_point[0] + sx * T[0], rail_point[1] + sx * T[1])]
    apex = (rail_point[0] + sy * outward[0],
            rail_point[1] + sy * outward[1])
    return base + [apex]


def branch(origin, tangent, side, length, bend=0.35, n=40):
    """A small branch curve leaving the stalk at `side` (+1 left, -1 right)."""
    T, N = frame(tangent)
    d = (T[0] + side * 0.55 * N[0], T[1] + side * 0.55 * N[1])
    l = math.hypot(*d) or 1.0
    d = (d[0] / l, d[1] / l)
    out = []
    for i in range(n + 1):
        t = i / n
        bendv = bend * length * math.sin(math.pi * t) * side
        out.append((origin[0] + d[0] * length * t + N[0] * bendv,
                    origin[1] + d[1] * length * t + N[1] * bendv))
    return out
