"""Generate log-aesthetic spines from (p, turn), and check them against the plates.

    .venv/bin/python scripts/lac_generate.py --write
    .venv/bin/python scripts/lac_generate.py --parity

The log-aesthetic curve is defined by its curvature radius as a function of arc
length:

    rho^p = c0 s + c1

With p = 0 the radius is constant, which is a circle. p = 1 is the logarithmic
spiral, p = -1 the clothoid. Those are the three that matter, and they are why
p = 0 is the only recovered plate that passes the G3 gate: a circle has constant
curvature, so every join is exact.

The convention here is c0 = 1, c1 = 1, so the curvature at the start is 1 and
falls (p > 0) or grows (p < 0) along the arc. The arc length is then solved by
bisection so the tangent turns exactly the requested angle. The shape is fixed by
(p, turn) alone, which is what makes a parity check meaningful.

Turns stop at 270 degrees on purpose: past that a single PH span cannot hold the
curve, and the spirals are handled by the clothoid and Euler code instead.

Coordinates: built in design space with y up, flipped once to the page's y down
when written, because every consumer of `spirals/*.json` expects page space.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "spirals" / "lac-generated.json"
PLATES = ROOT / "workbench" / "spirals" / "lac.json"

P_VALUES = (-3.0, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 3.0)
TURNS = (45, 90, 180, 270)
SPAN_TURN = 45.0          # degrees per cubic, the same split the plates use
SIZE = 900.0              # the drawn size, in page units


def curvature(alpha, s):
    """kappa(s) for rho^alpha = 1 + s; alpha = 0 is the circle."""
    if alpha == 0.0:
        return 1.0
    return math.pow(1.0 + s, -1.0 / alpha)


def tangent_at(alpha, s, steps=400):
    """The tangent angle, integrated from 0 to s."""
    if s <= 0.0:
        return 0.0
    step = s / steps
    total = 0.0
    for i in range(steps):
        total += curvature(alpha, (i + 0.5) * step) * step
    return total


def arc_for_turn(alpha, turn_deg, low=1e-3, high=200.0):
    """The arc length at which the tangent has turned `turn_deg`."""
    target = math.radians(turn_deg)
    if tangent_at(alpha, high) < target:
        raise ValueError(f"p {alpha}: cannot reach {turn_deg} degrees")
    for _ in range(80):
        middle = (low + high) / 2
        if tangent_at(alpha, middle) < target:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def points_for(alpha, turn_deg, samples=1200):
    """The curve as (x, y, tangent) in design space, y up, unit curvature at 0."""
    length = arc_for_turn(alpha, turn_deg)
    step = length / samples
    x = y = 0.0
    theta = 0.0
    out = [(0.0, 0.0, 0.0)]
    for i in range(samples):
        s = (i + 0.5) * step
        theta += curvature(alpha, s) * step
        x += math.cos(theta) * step
        y += math.sin(theta) * step
        out.append((x, y, theta))
    # scale to the drawn size, measured on the arc
    scale = SIZE / length
    return [(px * scale, py * scale, t) for px, py, t in out]


def fit_span(points):
    """A cubic through the points with their own end tangents.

    Endpoints and directions come from the curve; the two handle lengths are
    solved by least squares over the interior points.
    """
    (x0, y0, t0), (x1, y1, t1) = points[0], points[-1]
    d0 = (math.cos(t0), math.sin(t0))
    d1 = (math.cos(t1), math.sin(t1))
    span = math.hypot(x1 - x0, y1 - y0) or 1.0
    # basis: B(t) = (1-t)^3 P0 + 3(1-t)^2 t (P0 + a d0) + 3(1-t) t^2 (P3 - b d1) + t^3 P3
    aa = ab = bb = ra = rb = 0.0
    for px, py, _ in points[1:-1]:
        t = _parameter(px, py, x0, y0, x1, y1)
        u = 1.0 - t
        e0 = 3 * u * u * t
        e1 = 3 * u * t * t
        base_x = u ** 3 * x0 + 3 * u * u * t * x0 + 3 * u * t * t * x1 + t ** 3 * x1
        base_y = u ** 3 * y0 + 3 * u * u * t * y0 + 3 * u * t * t * y1 + t ** 3 * y1
        rx = px - base_x
        ry = py - base_y
        aa += e0 * e0
        ab += e0 * e1 * (d0[0] * d1[0] + d0[1] * d1[1])
        bb += e1 * e1
        ra += e0 * (rx * d0[0] + ry * d0[1])
        rb += e1 * (rx * d1[0] + ry * d1[1])
    determinant = aa * bb - ab * ab
    if abs(determinant) < 1e-12:
        handle_a = handle_b = span / 3
    else:
        handle_a = (bb * ra - ab * rb) / determinant
        handle_b = (aa * rb - ab * ra) / determinant
    handle_a = min(max(handle_a, span / 20), span * 2)
    handle_b = min(max(handle_b, span / 20), span * 2)
    return {
        "p0": [round(x0, 3), round(y0, 3)],
        "c1": [round(x0 + d0[0] * handle_a, 3), round(y0 + d0[1] * handle_a, 3)],
        "c2": [round(x1 - d1[0] * handle_b, 3), round(y1 - d1[1] * handle_b, 3)],
        "p3": [round(x1, 3), round(y1, 3)],
    }


def _parameter(px, py, x0, y0, x1, y1):
    """Rough t of a point along the chord, good enough for the least squares."""
    dx, dy = x1 - x0, y1 - y0
    length2 = dx * dx + dy * dy
    if length2 < 1e-12:
        return 0.5
    return min(0.999, max(0.001, ((px - x0) * dx + (py - y0) * dy) / length2))


def spans_for(alpha, turn_deg):
    points = points_for(alpha, turn_deg)
    pieces = max(1, int(round(turn_deg / SPAN_TURN)))
    per = (len(points) - 1) / pieces
    spans = []
    for k in range(pieces):
        first = int(round(k * per))
        last = int(round((k + 1) * per))
        spans.append(fit_span(points[first:last + 1]))
    return spans, points


def figure_for(alpha, turn_deg, number):
    spans, _ = spans_for(alpha, turn_deg)
    # one flip, at output: page space is y down
    for span in spans:
        for key in ("p0", "c1", "c2", "p3"):
            span[key][1] = round(-span[key][1], 3)
    title = f"LAC: p = {alpha:g}, turn {turn_deg}"
    return {
        "figure": f"Fig. {number}",
        "title": title,
        "family": "logaesthetic",
        "plate": "generated",
        "k0": 1.0,
        "k1": 1.0,
        "spines": [{
            "id": "spine-1",
            "kind": "spine",
            "stroke": 1.0,
            "spans": spans,
            "d": "M" + " L".join(f"{span['p0'][0]},{span['p0'][1]}" for span in spans),
        }],
    }


def turn_limit(alpha):
    """The most the family can turn, in degrees, or None when it is unbounded.

    With rho^p = 1 + s the curvature is (1 + s)^(-1/p). The integral of that to
    infinity converges only when 1/p > 1, that is when p < 1, and then the total
    turn is p / (1 - p) radians. For p >= 1 the integral diverges, so the log
    spiral and everything above it turn without limit, as does the clothoid
    (p <= 0), where the curvature grows.
    """
    if alpha <= 0.0 or alpha >= 1.0:
        return None
    return math.degrees(alpha / (1.0 - alpha))


def build():
    figures = []
    skipped = []
    number = 1
    for alpha in P_VALUES:
        for turn in TURNS:
            try:
                figures.append(figure_for(alpha, turn, number))
            except ValueError:
                limit = turn_limit(alpha)
                skipped.append((alpha, turn, limit))
                continue
            number += 1
    document = {
        "name": "lac-generated",
        "label": "Log-aesthetic spines generated from (p, turn)",
        "source": "scripts/lac_generate.py",
        "note": ("rho^p = 1 + s, curvature 1 at the start, arc length solved for the "
                 "turn. Cubics split every 45 degrees. Page space, y down."),
        "figures": figures,
    }
    OUT.write_text(json.dumps(document, indent=1) + "\n")
    print(f"{OUT.relative_to(ROOT)}  {len(figures)} curves")
    if skipped:
        print("\nnot in the family at this turn:")
        for alpha, turn, limit in skipped:
            print(f"  p {alpha:4g}  turn {turn:3d}  the most it can turn is {limit:5.1f} degrees")
    return document


def descriptors(points):
    """Scale-free numbers that say what a curve is."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    chord = math.hypot(xs[-1] - xs[0], ys[-1] - ys[0])
    arc = sum(math.hypot(points[i + 1][0] - points[i][0], points[i + 1][1] - points[i][1])
              for i in range(len(points) - 1))
    return {"chord_over_arc": chord / arc if arc else 0.0,
            "turn": math.degrees(points[-1][2] - points[0][2])}


def plate_points(figure):
    """The plate's spine as a dense polyline, y flipped back to design space."""
    spine = figure["spines"][0]
    out = []
    for span in spine["spans"]:
        p0, c1, c2, p3 = (span["p0"], span["c1"], span["c2"], span["p3"])
        for i in range(41):
            t = i / 40
            u = 1 - t
            x = (u ** 3 * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * p3[0])
            y = (u ** 3 * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * p3[1])
            out.append((x, -y, 0.0))
    return out


def similarity_fit(a, b):
    """The best similarity taking a onto b: (deviation, scale, rotation in degrees).

    A curve is self-similar when one half maps onto the next by a similarity with
    a scale other than 1; a circle maps with scale 1, which is only a rotation.
    """
    count = min(len(a), len(b))
    aa = _resample(a, count)
    bb = _resample(b, count)
    ax = [p[0] for p in aa]; ay = [p[1] for p in aa]
    bx = [p[0] for p in bb]; by = [p[1] for p in bb]
    amx, amy = sum(ax) / count, sum(ay) / count
    bmx, bmy = sum(bx) / count, sum(by) / count
    ax = [v - amx for v in ax]; ay = [v - amy for v in ay]
    bx = [v - bmx for v in bx]; by = [v - bmy for v in by]
    sa = math.sqrt(sum(v * v for v in ax) + sum(v * v for v in ay)) or 1e-9
    sb = math.sqrt(sum(v * v for v in bx) + sum(v * v for v in by)) or 1e-9
    ax = [v / sa for v in ax]; ay = [v / sa for v in ay]
    bx = [v / sb for v in bx]; by = [v / sb for v in by]
    real = sum(p * q + r * s for p, r, q, s in zip(ax, ay, bx, by))
    imag = sum(p * s - r * q for p, r, q, s in zip(ax, ay, bx, by))
    angle = math.atan2(imag, real)
    cos, sin = math.cos(angle), math.sin(angle)
    worst = 0.0
    for px, py, qx, qy in zip(ax, ay, bx, by):
        rx = qx * cos + qy * sin
        ry = -qx * sin + qy * cos
        worst = max(worst, math.hypot(px - rx, py - ry))
    return worst / math.sqrt(2), sb / sa, math.degrees(angle)


def procrustes_deviation(a, b):
    """Worst distance between two polylines after the best similarity fit.

    Both are resampled to the same count, centred, scaled to unit RMS, and
    rotated by the complex correlation; the answer is a fraction of the size.
    """
    count = min(len(a), len(b))
    aa = _resample(a, count)
    bb = _resample(b, count)
    ax = [p[0] for p in aa]
    ay = [p[1] for p in aa]
    bx = [p[0] for p in bb]
    by = [p[1] for p in bb]
    amx, amy = sum(ax) / count, sum(ay) / count
    bmx, bmy = sum(bx) / count, sum(by) / count
    ax = [v - amx for v in ax]
    ay = [v - amy for v in ay]
    bx = [v - bmx for v in bx]
    by = [v - bmy for v in by]
    sa = math.sqrt(sum(v * v for v in ax) + sum(v * v for v in ay)) or 1e-9
    sb = math.sqrt(sum(v * v for v in bx) + sum(v * v for v in by)) or 1e-9
    ax = [v / sa for v in ax]
    ay = [v / sa for v in ay]
    bx = [v / sb for v in bx]
    by = [v / sb for v in by]
    real = sum(p * q + r * s for p, r, q, s in zip(ax, ay, bx, by))
    imag = sum(p * s - r * q for p, r, q, s in zip(ax, ay, bx, by))
    angle = math.atan2(imag, real)
    cos, sin = math.cos(angle), math.sin(angle)
    worst = 0.0
    for px, py, qx, qy in zip(ax, ay, bx, by):
        rx = qx * cos + qy * sin
        ry = -qx * sin + qy * cos
        worst = max(worst, math.hypot(px - rx, py - ry))
    return worst / math.sqrt(2)


def _resample(points, count):
    """Even spacing along the polyline, so two curves can be compared point by point."""
    lengths = [0.0]
    for i in range(len(points) - 1):
        lengths.append(lengths[-1] + math.hypot(points[i + 1][0] - points[i][0],
                                                points[i + 1][1] - points[i][1]))
    total = lengths[-1] or 1e-9
    out = []
    for k in range(count):
        target = total * k / (count - 1)
        i = 0
        while i < len(lengths) - 2 and lengths[i + 1] < target:
            i += 1
        span = (lengths[i + 1] - lengths[i]) or 1e-9
        share = (target - lengths[i]) / span
        x = points[i][0] + (points[i + 1][0] - points[i][0]) * share
        y = points[i][1] + (points[i + 1][1] - points[i][1]) * share
        out.append((x, y, 0.0))
    return out


def parity():
    """Compare the generated curve with the recovered plate of the same (p, turn)."""
    plates = json.loads(PLATES.read_text())
    generated = json.loads(OUT.read_text()) if OUT.exists() else build()
    index = {}
    for figure in generated["figures"]:
        index[figure["title"]] = figure
    print(f"{'curve':26s} {'plate chord/arc':>16} {'ours':>8} {'deviation':>10}")
    rows = []
    for figure in plates["figures"]:
        title = figure["title"]
        if title not in index:
            continue
        plate = plate_points(figure)
        ours_spans, ours_points = spans_for(
            _alpha_of(title), _turn_of(title))
        ours = [(x, y, 0.0) for x, y, _ in ours_points]
        plate_d = descriptors(plate)
        ours_d = descriptors(ours)
        # the plates may be drawn from either end, so the smaller of the two
        # directions is the honest comparison of shape
        deviation = min(procrustes_deviation(plate, ours),
                        procrustes_deviation(plate, list(reversed(ours))))
        rows.append((title, plate_d["chord_over_arc"], ours_d["chord_over_arc"], deviation))
    for title, plate_ratio, ours_ratio, deviation in rows:
        print(f"{title:26s} {plate_ratio:16.4f} {ours_ratio:8.4f} {deviation:10.4f}")
    if rows:
        worst = max(row[3] for row in rows)
        print(f"\n{len(rows)} plates compared; worst deviation {worst:.4f} of the size")


def _alpha_of(title):
    return float(title.split("p = ")[1].split(",")[0])


def _turn_of(title):
    return int(title.split("turn ")[1].split()[0])


def points_range(alpha, s0, s1, samples=1200):
    """The curve between two arc lengths, in design space."""
    step = (s1 - s0) / samples
    x = y = theta = 0.0
    # walk from 0 so the position is on the same curve
    total = s0 + (s1 - s0)
    walk = max(1, int(samples * total / max(s1 - s0, 1e-9)))
    out = []
    step_all = total / walk
    for i in range(walk):
        s = (i + 0.5) * step_all
        theta += curvature(alpha, s) * step_all
        x += math.cos(theta) * step_all
        y += math.sin(theta) * step_all
        if s >= s0:
            out.append((x, y, theta))
    return out


def selfsimilar():
    """Is one arc a scaled, turned copy of another?

    For rho^p = 1 + s the copies are not equal arcs: the curve is self-similar
    when the arc from u to u' maps onto the arc from lu to lu' by a scale of l
    and a turn of ln(l). Only p = 1 has that property, because only there is the
    curvature proportional to 1/u.
    """
    lam = 2.0
    print(f"{'curve':26s} {'deviation':>10} {'scale':>8} {'turn':>8}   expected")
    for alpha in P_VALUES:
        try:
            length = arc_for_turn(alpha, 270)
        except ValueError:
            continue
        first = points_range(alpha, 0.0, length)
        second = points_range(alpha, lam - 1.0, lam * (1.0 + length) - 1.0)
        deviation, scale, rotation = similarity_fit(first, second)
        expected = f"scale {lam:g}, turn {math.degrees(math.log(lam)):.1f}"
        note = "  self-similar" if deviation < 0.01 and abs(scale - lam) < 0.02 else ""
        print(f"LAC: p = {alpha:<4g}, turn 270  {deviation:10.4f} {scale:8.4f}"
              f" {rotation:8.2f}   {expected}{note}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--parity", action="store_true")
    parser.add_argument("--selfsimilar", action="store_true")
    args = parser.parse_args()
    if not (args.write or args.parity or args.selfsimilar):
        parser.print_help()
        return
    if args.write or not OUT.exists():
        build()
    if args.parity:
        parity()
    if args.selfsimilar:
        selfsimilar()


if __name__ == "__main__":
    main()
