"""Spiral families at dress-curve proportions: 8 inches wide, 1-5 high.

    .venv/bin/python scripts/curve_families.py
    open docs/curve-families.html

Each strip is 8 x n inches (n = 1..5). For each family the arc is chosen so its
bounding box has that 8:n aspect, then scaled to fill the strip. A shallow arc
is a small turn; a tall one is a large turn. That is the honest way to compare
"which curve fills an 8 by 3 inch dress curve".
"""

from __future__ import annotations

import math
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


def placed(points, h: float, w: float = W):
    return fitter(points, h, w)[0](points)


def path_d(points) -> str:
    return " ".join(f"{'M' if i == 0 else 'L'} {x:.2f} {y:.2f}"
                    for i, (x, y) in enumerate(points))


ALPHA = math.atan2(7.0, 24.0)          # the 7-24-25 angle: 16.26 degrees


def doubling_chain(top: int = 10, base: float = 25.0):
    """Stack k = top, top-1, ... 1 triangles; the triple doubles each stack.

    One chord per triangle, the heading turning ALPHA at every chord.  The angle
    is the same in every stack -- (14,48,50) and (28,96,100) are the same shape
    as (7,24,25) -- so doubling changes the chord and never the turn.
    """
    x = y = heading = 0.0
    pts = [(0.0, 0.0)]
    for i, k in enumerate(range(top, 0, -1)):
        chord = base * 2.0 ** i
        for _ in range(k):
            x += chord * math.cos(heading)
            y += chord * math.sin(heading)
            pts.append((x, y))
            heading += ALPHA
    return pts


def stack_rows(top: int = 10, base: float = 25.0):
    """What the recipe does, stack by stack, in its own numbers."""
    rows, turn = [], 0
    for i, k in enumerate(range(top, 0, -1)):
        chord = base * 2.0 ** i
        turn += k * ALPHA
        rows.append({
            "k": k,
            "triple": f"{7 << i}-{24 << i}-{25 << i}",
            "chord": chord,
            "turn": math.degrees(turn),
            "radius": chord / ALPHA,
            # doubling one stack costs k*ALPHA of turn: d ln r / d theta
            "b": math.log(2.0) / (k * ALPHA),
        })
    return rows


def doubling_gap(top: int = 10) -> dict:
    chords = top * (top + 1) // 2
    turn = chords * ALPHA
    rows = stack_rows(top)
    return {
        "chords": chords,
        "turn": math.degrees(turn),
        "growth": 2.0 ** (top - 1),
        "b_eff": math.log(2.0 ** (top - 1)) / turn,
        "b_hook": rows[0]["b"],
        "b_arm": rows[-1]["b"],
        "hook_180": math.degrees(turn) / 180.0,
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


def doubling_section() -> str:
    """The user's construction, drawn and measured."""
    top = 10
    st = doubling_gap(top)
    rows = stack_rows(top)
    chain = doubling_chain(top)

    # -- the whole chain, square frame, stack boundaries dotted ----------
    draw, _ = fitter(chain, 760, 760)
    pts = draw(chain)
    d = " ".join(f"{'M' if i == 0 else 'L'} {x:.2f} {y:.2f}"
                 for i, (x, y) in enumerate(pts))
    start, dots = 0, []
    for k in range(top, 0, -1):
        dots.append(f'<circle cx="{pts[start][0]:.1f}" cy="{pts[start][1]:.1f}" r="4"/>')
        start += k
    whole = f"""<div class="strip">
  <svg viewBox="0 0 760 760" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="760" height="760" fill="#fff"
          stroke="#d8ccae" stroke-width="1"/>
    <path d="{d}" fill="none" stroke="#2e2413" stroke-width="2.2"/>
    <g fill="#8c6a21">{''.join(dots)}</g>
  </svg>
  <p><strong>all {st['chords']} chords</strong> · {st['turn']:.0f}° of turn ·
  radius grows {st['growth']:.0f}× from hook to arm · one dot per stack</p>
</div>"""

    # -- against the hip spiral the page already uses (b = 1.6) ----------
    hip_log = fit_arc(lambda p: log_points(1.6, p), 4.8)
    fit4 = fitter(doubling_chain(4), 500, 2400, 45.0)[0]
    cut_gap = curve_gap(fit4(doubling_chain(4)),
                        fitter(hip_log, 500, 2400, 45.0)[0](hip_log))

    # -- where 180 degrees actually lands --------------------------------
    cuts = "".join((
        hip_strip("4 stacks (10 chords) · 163°", doubling_chain(4),
                  margin=45.0, over=hip_log,
                  note=f"· over the b = 1.6 spiral (gold), mean offset "
                       f"{cut_gap[0]:.1f}%"),
        hip_strip("5 stacks (15 chords) · 244°", doubling_chain(5),
                  margin=45.0),
    ))

    # -- against the hip spiral the page already uses (b = 1.6) ----------
    draw_c, _ = fitter(chain, 500, 2400)
    draw_g, _ = fitter(hip_log, 500, 2400)
    ink = draw_c(chain)
    gold = draw_g(hip_log)
    d_ink = path_d(ink)
    d_gold = path_d(gold)
    grid = "".join(f'<line x1="{i * 100}" y1="0" x2="{i * 100}" y2="500"/>'
                   for i in range(1, 24))
    grid += "".join(f'<line x1="0" y1="{i * 100}" x2="2400" y2="{i * 100}"/>'
                    for i in range(1, 5))
    hip_gap = curve_gap(ink, gold)
    hip_fill = 5.0 * aspect(chain)
    hip_panel = f"""<div class="strip">
  <svg viewBox="0 0 2400 500" xmlns="http://www.w3.org/2000/svg">
    <g stroke="#e8dfc8" stroke-width="0.6">{grid}</g>
    <rect x="0" y="0" width="2400" height="500" fill="none"
          stroke="#d8ccae" stroke-width="1"/>
    <path d="{d_gold}" fill="none" stroke="#c9a441" stroke-width="5"
          stroke-dasharray="14 10" stroke-linecap="round"/>
    <path d="{d_ink}" fill="none" stroke="#2e2413" stroke-width="2.4"/>
  </svg>
  <p><strong>the doubling stack</strong> (ink) against
  <strong>the b = 1.6 hip spiral</strong> (gold) in the same 24 × 5 frame ·
  the chain fills {hip_fill:.1f} in of the 24 and is rounder than the slot,
  mean offset {hip_gap[0]:.1f}% of the frame, worst {hip_gap[1]:.1f}%</p>
</div>"""

    table_rows = []
    for r in rows:
        table_rows.append(
            f"<tr><td>{r['k']}</td><td>{r['triple']}</td>"
            f"<td>{r['chord']:.0f}</td><td>{r['turn']:.0f}°</td>"
            f"<td>{r['radius']:.0f}</td><td>{r['b']:.2f}</td></tr>")
    table = "".join(table_rows)

    return f"""
  <h2>The doubling stack</h2>
  <div class="panel">
    <p>Ten triangles of 7-24-25, then nine of 14-48-50, then eight of
    28-96-100, down to one. The angle is the same in every stack — a doubled
    triple is the same <em>shape</em> — so the chord doubles and the turn never
    changes. That is what makes it a log spiral: radius and arc grow together.
    Read from the tight end it is a hook, then a sweep that runs away.</p>
    {whole}
    {hip_panel}
  </div>

  <h2>What the series actually delivers</h2>
  <div class="panel">
    <div class="scroll"><table>
      <tr><th>stack</th><th>triple</th><th>chord</th><th>turn so far</th>
      <th>radius</th><th>b here</th></tr>
      {table}
    </table></div>
    <p style="margin-top:10px">The last column is the local log-spiral rate
    <em>b = ln 2 / (k · α)</em> for a stack of k triangles: the doubling
    always doubles, but the turn it is spread over shrinks, so b climbs from
    {st['b_hook']:.2f} at the hook to {st['b_arm']:.2f} at the outer end. No
    single b describes the curve; over its whole length it acts like
    b = {st['b_eff']:.2f}. The hip panel wants b ≈ 1.6, which this schedule
    passes through only at the last two stacks.</p>
    <p>The series is also {st['hook_180']:.1f} times too long for a 180° hook:
    {st['chords']} chords at {math.degrees(ALPHA):.2f}° is {st['turn']:.0f}°.
    Cut it at four or five stacks and the hook lands at 163° or 244°, which is
    why those two strips follow. Cutting the length does not fix the
    <em>proportion</em>, though — every stack both doubles the radius and turns,
    so a longer arm means more turn. To get 4.8:1 you have to break that
    coupling: fewer chords per stack (thinner turning), or grow by more than 2×
    per stack.</p>
    {cuts}
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
  .scroll {{ overflow-x:auto; }}
  .back {{ font:12px var(--mono); margin-bottom:16px; }}
  a {{ color:var(--gold); }}
  @media (max-width:620px) {{
    main {{ padding:22px 14px 60px; }}
    table {{ font-size:10px; }} th,td {{ padding:4px 2px; }}
  }}
</style>
</head>
<body>
<main>
  <p class="back"><a href="sandbox.html">← sandbox</a></p>
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
    path = ROOT / "docs" / "curve-families.html"
    path.write_text(page, encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
