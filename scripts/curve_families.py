"""Spiral families at dress-curve proportions: 8 inches wide, 1-5 high.

    .venv/bin/python scripts/curve_families.py
    open workbench/curve-families.html

Each strip is 8 x n inches (n = 1..5). For each family the arc is chosen so its
bounding box has that 8:n aspect, then scaled to fill the strip. A shallow arc
is a small turn; a tall one is a large turn. That is the honest way to compare
"which curve fills an 8 by 3 inch dress curve".
"""

from __future__ import annotations

import math
from fractions import Fraction
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
W = 800.0
MARGIN = 14.0


def log_points(b: float, phi: float):
    n = 300
    return [(math.exp(b * phi * i / n) * math.cos(phi * i / n),
             math.exp(b * phi * i / n) * math.sin(phi * i / n))
            for i in range(n + 1)]


def hyper_points(t0: float, phi: float):
    n = 300
    pts = []
    for i in range(n + 1):
        t = t0 + phi * i / n
        pts.append((math.cos(t) / t, math.sin(t) / t))
    return pts


def clothoid_points(phi: float):
    length = 1.0
    k = 2.0 * phi / length          # turn = 0.5 * k * L
    x = y = s = 0.0
    pts = []
    ds = 0.004
    while s <= length:
        theta = s * s * k / (2 * length)
        pts.append((x, y))
        x += ds * math.cos(theta)
        y += ds * math.sin(theta)
        s += ds
    return pts


def orient(points):
    """Rotate so the chord from first to last point is horizontal."""
    a = math.atan2(points[-1][1] - points[0][1],
                   points[-1][0] - points[0][0])
    c, s = math.cos(-a), math.sin(-a)
    return [(c * x - s * y, s * x + c * y) for x, y in points]


def poly_points(power: float, turn: float, ds: float = 0.002):
    """Generalized Euler spiral: kappa proportional to s**power."""
    length = 1.0
    c = turn * (power + 1) / length ** (power + 1)
    x = y = s_arc = 0.0
    pts = []
    while s_arc <= length:
        theta = c * s_arc ** (power + 1) / (power + 1)
        pts.append((x, y))
        x += ds * math.cos(theta)
        y += ds * math.sin(theta)
        s_arc += ds
    return pts


def aspect(points) -> float:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (max(xs) - min(xs)) / max(max(ys) - min(ys), 1e-9)


def fit_arc(make, target: float, lo: float = 0.005, hi: float = math.pi):
    """The arc turn whose bbox aspect is closest to the target.

    The aspect is not monotonic for a log spiral once it wraps, so scan and
    take the closest, then refine locally.
    """
    best, best_err = lo, float("inf")
    steps = 400
    for i in range(steps + 1):
        phi = lo + (hi - lo) * i / steps
        err = abs(aspect(orient(make(phi))) - target)
        if err < best_err:
            best, best_err = phi, err
    span = (hi - lo) / steps
    for _ in range(30):
        for phi in (best - span, best + span):
            if lo <= phi <= hi:
                err = abs(aspect(orient(make(phi))) - target)
                if err < best_err:
                    best, best_err = phi, err
        span *= 0.5
    return orient(make(best))


def fit_hyper(target: float):
    """A window of r=a/θ whose oriented bbox has the target aspect."""
    best = (float("inf"), 1.4, 3.1)
    for t0 in [0.3 + 0.1 * i for i in range(30)]:
        for phi in [0.2 + 0.1 * j for j in range(60)]:
            err = abs(aspect(orient(hyper_points(t0, phi))) - target)
            if err < best[0]:
                best = (err, t0, phi)
    _, t0, phi = best
    return orient(hyper_points(t0, phi)), t0, phi


def fitter(points, h: float, w: float = W, margin: float = MARGIN):
    """A uniform model->screen map that fits the bbox, centred, +y up -> SVG.

    This is the one place the y axis flips: everything upstream is y-up.
    """
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    scale = min((w - 2 * margin) / max(x1 - x0, 1e-9),
                (h - 2 * margin) / max(y1 - y0, 1e-9))
    dx = (w - (x1 - x0) * scale) / 2
    dy = (h - (y1 - y0) * scale) / 2

    def draw(points_):
        return [(dx + (x - x0) * scale, h - (dy + (y - y0) * scale))
                for x, y in points_]

    return draw, scale


def ladder(max_h: int = 500, max_deg: float = 62.0):
    """Pythagorean slopes as angles, sorted: the rungs the chain may use.

    `deg` is the angle of the legs *as laid* -- atan2(v, u), measured from the
    horizontal, because a chord is (u, v) in x, y order.  Measuring it from the
    vertical instead puts every chord at 90 - theta, which turns a catenary
    into a check mark.
    """
    seen, rungs = set(), []
    for u in range(1, max_h):
        for v in range(u + 1, max_h):
            h = math.isqrt(u * u + v * v)
            if h * h != u * u + v * v or h > max_h:
                continue
            for legs in ((u, v), (v, u)):
                ang = math.degrees(math.atan2(legs[1], legs[0]))
                if ang > max_deg:
                    continue
                key = round(ang, 2)
                if key in seen:
                    continue
                seen.add(key)
                rungs.append({"deg": ang, "triple": (legs[0], legs[1], h)})
    rungs.sort(key=lambda r: r["deg"])
    return rungs


def exact_spine(top: int, triple, rungs):
    """A spine whose every node is an integer point.

    The ideal chain turns by a fixed angle, so its chords run at k*alpha and
    cos(k*alpha) is irrational -- those nodes can never be integers.  Here each
    chord is an integer multiple of a triple's legs instead: the direction is
    the nearest rung to the ideal heading, the length is rounded to whole
    hypotenuses of that rung.  The nodes are exactly integral; the curve is an
    approximation of the ideal, and the error is reported.
    """
    ideal = doubling_chain(top, triple)
    pts = [(0, 0)]
    rows = []
    x = y = 0
    for i in range(len(ideal) - 1):
        dx = ideal[i + 1][0] - ideal[i][0]
        dy = ideal[i + 1][1] - ideal[i][1]
        want = math.degrees(math.atan2(dy, dx))
        rung = min(rungs, key=lambda r: abs(r["deg"] - want))
        u, v, h = rung["triple"]
        m = max(1, round(math.hypot(dx, dy) / h))
        sx, sy = m * u, m * v
        x, y = x + sx, y + sy
        pts.append((x, y))
        rows.append({"want": want, "deg": rung["deg"], "triple": (u, v, h),
                     "m": m, "chord": (sx, sy)})
    return pts, rows, ideal


def exact_plate(pts, d):
    """The offset of an integer chain, in Fractions: exact, no snapping."""
    lines = []
    for i in range(len(pts) - 1):
        dx = pts[i + 1][0] - pts[i][0]
        dy = pts[i + 1][1] - pts[i][1]
        h = math.isqrt(dx * dx + dy * dy)
        shift_x = Fraction(-dy, 1) * d / h
        shift_y = Fraction(dx, 1) * d / h
        lines.append(((Fraction(pts[i][0]) + shift_x,
                       Fraction(pts[i][1]) + shift_y),
                      (Fraction(dx), Fraction(dy))))

    out = [lines[0][0]]
    for i in range(1, len(lines)):
        (ax, ay), (ux, uy) = lines[i - 1]
        (bx, by), (vx, vy) = lines[i]
        den = ux * vy - uy * vx
        if den == 0:
            out.append(bx)
            continue
        t = ((bx - ax) * vy - (by - ay) * vx) / den
        out.append((ax + ux * t, ay + uy * t))
    return out


def common_denominator(pts):
    """Rescale exact points so every coordinate is an integer again."""
    den = 1
    for x, y in pts:
        for v in (x, y):
            den = den * v.denominator // math.gcd(den, v.denominator)
    return [(x * den, y * den) for x, y in pts], den


def placed(points, h: float, w: float = W):
    return fitter(points, h, w)[0](points)


def turn_of(points, i: int) -> float:
    """Signed turn at node i of a polyline, in radians."""
    (x0, y0), (x1, y1), (x2, y2) = points[i - 1], points[i], points[i + 1]
    a = math.atan2(y1 - y0, x1 - x0)
    b = math.atan2(y2 - y1, x2 - x1)
    d = b - a
    while d > math.pi:
        d -= 2 * math.pi
    while d < -math.pi:
        d += 2 * math.pi
    return d


def offset_chain(points, d):
    """Offset a chain by d to the left of travel (negative: right).

    Each chord is slid by d along its left normal, then consecutive slid chords
    are intersected.  That is the polygon offset, exactly: the node angles do
    not change and every chord shortens by d*tan(turn/2) at each end.
    """
    if d == 0:
        return list(points)
    segs = []
    for i in range(len(points) - 1):
        (x0, y0), (x1, y1) = points[i], points[i + 1]
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        ux, uy = dx / length, dy / length
        segs.append(((x0 - uy * d, y0 + ux * d), (ux, uy), length))

    out = [segs[0][0]]
    for i in range(1, len(segs)):
        (p0, u0, _), (p1, u1, _) = segs[i - 1], segs[i]
        denom = u0[0] * u1[1] - u0[1] * u1[0]
        if abs(denom) < 1e-12:
            out.append(p1)
            continue
        t = ((p1[0] - p0[0]) * u1[1] - (p1[1] - p0[1]) * u1[0]) / denom
        out.append((p0[0] + u0[0] * t, p0[1] + u0[1] * t))
    (sx, sy), (ux, uy), length = segs[-1]
    turn = abs(turn_of(points, len(points) - 2))
    trim = abs(d) * math.tan(turn / 2)
    out.append((sx + ux * length, sy + uy * length))     # free end, untrimmed
    return out


def path_d(points) -> str:
    return " ".join(f"{'M' if i == 0 else 'L'} {x:.2f} {y:.2f}"
                    for i, (x, y) in enumerate(points))


THIN = (237, 3116, 3125)      # a thin p-triple: 4.35 degrees a chord
THICK = (7, 24, 25)           # the wide one: 16.26 degrees a chord


def triple_angle(triple) -> float:
    """The thin angle of a p-triple -- the turn contributed by one chord."""
    return math.atan2(triple[0], triple[1])


def doubling_chain(top: int, triple=THIN):
    """Stack k = top, top-1, ... 1 triangles; the triple doubles each stack.

    One chord per triangle, the heading turning by the triple's angle at every
    chord.  A doubled triple is the same shape -- (474,6232,6250) has the same
    angle as (237,3116,3125) -- so doubling changes the chord, never the turn.
    """
    alpha = triple_angle(triple)
    x = y = heading = 0.0
    pts = [(0.0, 0.0)]
    for i, k in enumerate(range(top, 0, -1)):
        chord = float(triple[2]) * 2.0 ** i
        for _ in range(k):
            x += chord * math.cos(heading)
            y += chord * math.sin(heading)
            pts.append((x, y))
            heading += alpha
    return pts


def series_top(top: int, triple=THIN) -> dict:
    """What a stack of k = top ... 1 does, in its own numbers."""
    alpha = triple_angle(triple)
    chords = top * (top + 1) // 2
    turn = chords * alpha
    return {
        "top": top,
        "chords": chords,
        "turn": math.degrees(turn),
        "growth": 2.0 ** (top - 1),
        "b_eff": math.log(2.0 ** (top - 1)) / turn,
        "b_in": math.log(2.0) / (top * alpha),
        "b_out": math.log(2.0) / alpha,
    }



def hip_strip(label: str, points, margin: float = MARGIN,
              over=None, note: str = "") -> str:
    """A 24 x 5 inch frame (100 units per inch), curve scaled to fit."""
    w, h = 2400.0, 500.0
    pts = fitter(points, h, w, margin)[0](points)
    d = path_d(pts)
    gold = ""
    if over is not None:
        gold = (f'<path d="{path_d(fitter(over, h, w, margin)[0](over))}" '
                f'fill="none" stroke="#c9a441" stroke-width="5" '
                f'stroke-dasharray="14 10" stroke-linecap="round"/>')
    grid = "".join(f'<line x1="{i * 100}" y1="0" x2="{i * 100}" y2="{h}"/>'
                   for i in range(1, 24))
    grid += "".join(f'<line x1="0" y1="{i * 100}" x2="{w}" y2="{i * 100}"/>'
                    for i in range(1, 5))
    fill = min(24.0, 5.0 * aspect(points))
    return f"""<div class="strip">
  <svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <g stroke="#e8dfc8" stroke-width="0.6">{grid}</g>
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="none"
          stroke="#d8ccae" stroke-width="1"/>
    {gold}
    <path d="{d}" fill="none" stroke="#2e2413" stroke-width="2.2"/>
  </svg>
  <p><strong>{label}</strong> · at 5 in high it spans {fill:.1f} in of 24
  {note}</p>
</div>"""


def strip(label: str, points, n: int) -> str:
    h = n * 100.0
    pts = placed(points, h)
    d = " ".join(f"{'M' if i == 0 else 'L'} {x:.2f} {y:.2f}"
                 for i, (x, y) in enumerate(pts))
    grid = "".join(f'<line x1="{g * 100}" y1="0" x2="{g * 100}" y2="{h}"/>'
                   for g in range(1, 8))
    grid += "".join(f'<line x1="0" y1="{g * 100}" x2="{W}" y2="{g * 100}"/>'
                    for g in range(1, n))
    return f"""<div class="strip">
  <svg viewBox="0 0 {W:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <g stroke="#e8dfc8" stroke-width="0.6">{grid}</g>
    <rect x="0" y="0" width="{W:.0f}" height="{h:.0f}" fill="none"
          stroke="#d8ccae" stroke-width="1"/>
    <path d="{d}" fill="none" stroke="#2e2413" stroke-width="2.2"/>
  </svg>
  <p><strong>{label}</strong> · 8 × {n} in
    {"" if abs(aspect(points) - 8.0 / n) < 0.06 else
     f"· the arc itself fills 8 × {8.0 / aspect(points):.1f}"}</p>
</div>"""


def seg_dist(p, a, b) -> float:
    ax, ay = a
    bx, by = b
    px, py = p
    vx, vy = bx - ax, by - ay
    length = vx * vx + vy * vy
    t = 0.0 if length == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / length))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


def curve_gap(a, b):
    """How far two chains are apart: mean and worst, % of their joint size."""
    xs = [p[0] for p in a] + [p[0] for p in b]
    ys = [p[1] for p in a] + [p[1] for p in b]
    diag = math.hypot(max(xs) - min(xs), max(ys) - min(ys))

    def nearest(points, other):
        return [min(seg_dist(pt, other[i], other[i + 1])
                    for i in range(len(other) - 1)) for pt in points]

    d = nearest(a, b)
    return 100.0 * sum(d) / len(d) / diag, 100.0 * max(d) / diag


def square_panel(points, caption: str, top: int | None = None) -> str:
    """A square panel; `top` marks the stack boundaries with dots."""
    draw, _ = fitter(points, 760, 760)
    pts = draw(points)
    dots = ""
    if top:
        start, circles = 0, []
        for k in range(top, 0, -1):
            circles.append(f'<circle cx="{pts[start][0]:.1f}" '
                           f'cy="{pts[start][1]:.1f}" r="4"/>')
            start += k
        dots = f'<g fill="#8c6a21">{"".join(circles)}</g>'
    return f"""<div class="strip">
  <svg viewBox="0 0 760 760" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="760" height="760" fill="#fff"
          stroke="#d8ccae" stroke-width="1"/>
    <path d="{path_d(pts)}" fill="none" stroke="#2e2413" stroke-width="2.2"/>
    {dots}
  </svg>
  <p>{caption}</p>
</div>"""


def triple_label(triple) -> str:
    return "-".join(str(v) for v in triple)


def counts_table(triple, counts, chosen: int) -> str:
    rows = []
    for n in counts:
        st = series_top(n, triple)
        fill = 5.0 * aspect(doubling_chain(n, triple))
        mark = ' class="now"' if n == chosen else ""
        rows.append(
            f"<tr{mark}><td>{n}..1</td><td>{st['chords']}</td>"
            f"<td>{st['turn']:.0f}°</td><td>{st['growth']:.0f}×</td>"
            f"<td>{st['b_eff']:.2f}</td><td>{fill:.1f} in</td></tr>")
    return f"""<table>
      <tr><th>stacks</th><th>chords</th><th>turn</th><th>growth</th>
      <th>b</th><th>fills at 5 in</th></tr>
      {"".join(rows)}
    </table>"""


def doubling_section() -> str:
    """The doubling stack for two triples: one compact, one reaching."""
    hip_log = fit_arc(lambda p: log_points(1.6, p), 4.8)
    cases = ((THICK, 4), (THIN, 9))

    panels, tables = [], []
    stats = {}
    for triple, top in cases:
        chain = doubling_chain(top, triple)
        st = series_top(top, triple)
        stats[triple] = st
        label = triple_label(triple)
        fill = 5.0 * aspect(chain)

        panels.append(square_panel(
            chain,
            f"<strong>{label}, {top} stacks</strong> · {st['chords']} chords "
            f"· {st['turn']:.0f}° of turn · radius grows {st['growth']:.0f}× "
            f"· one dot per stack", top=top))

        ink = fitter(chain, 500, 2400, 45.0)[0](chain)
        gold = fitter(hip_log, 500, 2400, 45.0)[0](hip_log)
        gap = curve_gap(ink, gold)
        panels.append(hip_strip(
            f"{label} · {top} stacks · {st['turn']:.0f}°", chain,
            margin=45.0, over=hip_log,
            note=f"· over the b = 1.6 hip spiral (gold) · mean offset "
                 f"{gap[0]:.1f}% of the frame"))

        counts = (3, 4, 5) if triple is THICK else (7, 8, 9, 10, 11)
        tables.append(counts_table(triple, counts, top))

    thick_st, thin_st = stats[THICK], stats[THIN]
    thick_fill = 5.0 * aspect(doubling_chain(4, THICK))
    thin_fill = 5.0 * aspect(doubling_chain(9, THIN))

    return f"""
  <h2>The doubling stack</h2>
  <div class="panel">
    <p>Stack k triangles, then k-1 of the same shape at twice the size, down to
    one. A doubled triple is the same <em>shape</em> — (474,6232,6250) has the
    same angle as (237,3116,3125) — so the chord grows and the turn never
    changes. That is what makes it a log spiral: radius and arc grow together.
    Read from the tight end it is a hook, then a sweep that runs away.</p>
    <p>Two triples carry the work, and both are good:</p>
    <table>
      <tr><th>triple</th><th>angle per chord</th><th>the hook arrives at</th>
      <th>reach</th></tr>
      <tr><td>7-24-25</td><td>16.26°</td><td>4 stacks · 163°</td>
      <td>compact · {thick_fill:.1f} in of the 24</td></tr>
      <tr class="now"><td>237-3116-3125</td><td>4.35°</td>
      <td>9 stacks · 196°</td><td>long · {thin_fill:.1f} in of the 24</td></tr>
    </table>
    <p style="margin-top:10px">The angle is the lever: a chord of the wide
    triple turns 3.7 times as far as one of the thin, so the same schedule gives
    a compact hook or a long reaching one. Which you want is a choice about the
    garment, not about the maths.</p>
  </div>

  <h2>The two landings</h2>
  <div class="panel">
    <p>Each triple at the stack count where the hook comes out near 180°,
    then the same chain over the b = 1.6 hip spiral from the panel above,
    in the same 24 × 5 frame.</p>
    {panels[0]}
    {panels[1]}
    {panels[2]}
    {panels[3]}
  </div>

  <h2>How many stacks</h2>
  <div class="panel">
    <div class="tables">
      <div><h3>7-24-25</h3>{tables[0]}</div>
      <div><h3>237-3116-3125</h3>{tables[1]}</div>
    </div>
    <p style="margin-top:12px">Turn grows with the square of the count and
    growth doubles with the count, so the count sets both at once. The wide
    triple lands on the hook at four stacks: {thick_st['turn']:.0f}°, but only
    {thick_st['growth']:.0f}× growth over it, so b = {thick_st['b_eff']:.2f} —
    a compact hook, rounder than the hip spiral. The thin one needs nine for
    {thin_st['turn']:.0f}°, and because it has grown
    {thin_st['growth']:.0f}× over that same turn, b =
    {thin_st['b_eff']:.2f}, which is the panel's 1.6.</p>
    <p>So the angle sets the count, and the count sets the rate: to hold a hook
    near 180° the wide triple can only afford four stacks, the thin one nine.
    That is why the two triples land on different curves — same law, same hook,
    one compact and one reaching. Both are worth keeping for that reason.</p>
    <p>The fill column is a bounding-box measure, so it swings when the last
    chord doubles back over the start — eight stacks of the thin triple do
    exactly that. Read the turn column for the hook and the fill column for the
    slot, and expect them to disagree by a stack.</p>
    <p>No single b describes either chain: the doubling is constant, but the
    turn it is spread over shrinks, so the thin curve runs from
    {thin_st['b_in']:.1f} at the hook to {thin_st['b_out']:.1f} at the last
    chord, and the wide one from {thick_st['b_in']:.1f} to
    {thick_st['b_out']:.1f}. The tables' b is the average over the whole run.</p>
  </div>
"""


def main() -> int:
    rows = []
    for family in ("log spiral · b = 0.18", "hyperbolic", "clothoid"):
        strips = []
        for n in (1, 2, 3, 4, 5):
            if family.startswith("log"):
                points = fit_arc(lambda phi: log_points(0.18, phi), 8.0 / n)
                label = family
            elif family.startswith("hyper"):
                points, t0, phi = fit_hyper(8.0 / n)
                label = f"hyperbolic · θ {t0:.1f}–{t0 + phi:.1f}"
            else:
                points = fit_arc(clothoid_points, 8.0 / n)
                label = family
            strips.append(strip(label, points, n))
        rows.append((family, "".join(strips)))

    hip = "".join((
        hip_strip("log spiral · b = 1.6", fit_arc(lambda p: log_points(1.6, p), 4.8)),
        hip_strip("polynomial spiral · κ ∝ s⁵·⁵",
                  fit_arc(lambda p: poly_points(5.5, p), 4.8)),
        hip_strip("hyperbolic · 180° window", fit_hyper(4.8)[0]),
    ))
    sections = "".join(
        f'<h2>{family}</h2><div class="panel">{strips}</div>'
        for family, strips in rows)

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Spirals at dress-curve proportions</title>
<style>
  :root {{ color-scheme: light; --paper:#f6f1e4; --card:#fffdf7; --ink:#2e2413;
    --muted:#7b6c4e; --gold:#8c6a21; --line:#d8ccae;
    --mono: ui-monospace,"SF Mono",Menlo,Consolas,monospace;
    --serif:"EB Garamond",Georgia,"Palatino Linotype",Palatino,serif; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; color:var(--ink); font:16px/1.55 var(--serif);
    background: radial-gradient(900px 440px at 12% -8%, #fcf9ef 0, transparent 60%), var(--paper); }}
  main {{ max-width: 920px; margin: 0 auto; padding: 34px 22px 70px; }}
  h1 {{ font-size: 28px; margin: 0 0 4px; }}
  .lead {{ color: var(--gold); margin: 0 0 18px; }}
  h2 {{ font: 600 11px/1.2 var(--mono); letter-spacing:.12em; text-transform:uppercase;
    color:var(--muted); margin:26px 0 8px; }}
  .panel {{ background:var(--card); border:1px solid var(--line); border-radius:6px; padding:12px; }}
  .strip {{ margin: 0 0 14px; }}
  .strip:last-child {{ margin-bottom: 0; }}
  .strip svg {{ display:block; width:100%; height:auto; background:#fff;
    border:1px solid var(--line); border-radius:3px; }}
  .strip p {{ margin:5px 0 0; font:10px/1.3 var(--mono); color:var(--muted); }}
  .strip strong {{ color:var(--ink); }}
  table {{ border-collapse:collapse; width:100%; font:12px/1.5 var(--mono); }}
  th, td {{ border-bottom:1px solid var(--line); padding:6px 4px; text-align:left; }}
  th {{ color:var(--muted); font-weight:500; }}
  tr.now td {{ background:#fbf3dc; font-weight:600; }}
  .tables {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
  .tables h3 {{ font:600 11px/1.3 var(--mono); letter-spacing:.08em;
    color:var(--gold); margin:0 0 6px; }}
  .scroll {{ overflow-x:auto; }}
  .back {{ font:12px var(--mono); margin-bottom:16px; }}
  a {{ color:var(--gold); }}
  @media (max-width:620px) {{
    main {{ padding:22px 14px 60px; }}
    table {{ font-size:10px; }} th,td {{ padding:4px 2px; }}
    .tables {{ grid-template-columns:1fr; }}
  }}
</style>
</head>
<body>
<main>
  <p class="back"><a href="workbench.html">← workbench</a></p>
  <h1>Spirals at dress-curve proportions</h1>
  <p class="lead">8 inches wide, 1 to 5 inches high. Each strip uses the arc of
  that family whose bounding box is 8:n, so it fills the shape.</p>

  <div class="panel" style="margin-bottom:18px">
    <p>Shallow strips are small turns; tall strips are large turns. Compare the
    <em>asymmetry</em>: a log spiral tightens toward one end by a fixed ratio;
    a clothoid tightens continuously; a hyperbolic has a long asymptotic arm.</p>
  </div>

  <h2>The real hip curve: 24 × 5 with a 180° hook</h2>
  <div class="panel">
    <p>A 24 × 5 shape is 4.8:1. The gentle log spiral (b = 0.18) and the
    clothoid only reach about 2:1, but the sharpness is a parameter: a log spiral
    at b ≈ 1.6, a polynomial spiral κ ∝ s⁵·⁵, and a hyperbolic window all reach
    4.8:1 with a long arm and a 180° hook. The three panels are those sharp
    members; the earlier 8-inch strips use the gentle ones.</p>
    {hip}
  </div>

  {sections}

  {doubling_section()}

  <h2>How to identify the real one</h2>
  <div class="panel">
    <div class="scroll"><table>
      <tr><th>family</th><th>equation</th><th>signature</th></tr>
      <tr><td>log spiral</td><td>r = a e^(bθ)</td><td>tangent–radius angle constant; ρ ∝ s</td></tr>
      <tr><td>clothoid</td><td>κ = s / A²</td><td>curvature linear in arc length; ρ ∝ 1/s</td></tr>
      <tr><td>hyperbolic</td><td>r = a / θ</td><td>rθ constant; asymptote</td></tr>
      <tr><td>log-aesthetic</td><td>ρ^α = c₀s + c₁</td><td>α = 1 log; α = −1 clothoid</td></tr>
    </table></div>
    <p style="margin-top:10px">Pick the strip closest to the physical curve, then
    scan it: the fit gives b, the θ window or α. The page is an eye test, not a
    proof.</p>
  </div>
</main>
</body>
</html>
"""
    path = ROOT / "workbench" / "curve-families.html"
    path.write_text(page, encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
