"""How many turns fit before an Euler spiral is a circle — and before it merges.

    .venv/bin/python scripts/spiral_turns.py
    open docs/spiral-turns.html

Two experiments, both with 1-unit chords on a 100-unit grid:

1. A clothoid from rest. Scale it so the bounding box is 80 and the final
   radius is 15 (a 30-wide circle). Most of that box is the long near-straight
   approach; only about one turn is left at the end, and the gap between the
   last two windings is ~16 units — no line width collides.

2. A clothoid already winding at an outer radius R. With the same final radius,
   the number of turns is set by (R/r)^2, and the radial gap between successive
   windings is about r/(2N). That is the useful rule: a 1-unit line at r=15
   merges at about 7.5 turns; a 5-unit ribbon at about 1.5 turns.

The page draws experiment 1 to the grid and prints the table for experiment 2.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GRID = 100.0
CHORD = 1.0
R_END = 15.0          # a 30-wide circle
MARGIN = 10.0


def chain(turns: int, alpha: float):
    x = y = theta = 0.0
    points = [(0.0, 0.0)]
    headings = [0.0]
    for k in range(turns):
        theta += alpha * k
        x += CHORD * math.cos(theta)
        y += CHORD * math.sin(theta)
        points.append((x, y))
        headings.append(theta)
    return points, headings


def bbox(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), max(xs), min(ys), max(ys)


def fit_from_rest(target: float = 80.0):
    """Fewest/most chords whose bbox is `target` with r_end = R_END."""
    lo, hi = 10, 4000
    while lo < hi:
        mid = (lo + hi) // 2
        points, _ = chain(mid, 1.0 / (R_END * mid))
        x0, x1, y0, y1 = bbox(points)
        if max(x1 - x0, y1 - y0) < target:
            lo = mid + 1
        else:
            hi = mid
    count = lo
    points, headings = chain(count, 1.0 / (R_END * count))
    return points, headings, count


def fit_radius(rend: float, target: float = 80.0):
    """Fit a from-rest spiral ending at radius `rend` into the same box."""
    lo, hi = 10, 6000
    while lo < hi:
        mid = (lo + hi) // 2
        points, _ = chain(mid, 1.0 / (rend * mid))
        x0, x1, y0, y1 = bbox(points)
        if max(x1 - x0, y1 - y0) < target:
            lo = mid + 1
        else:
            hi = mid
    count = lo
    points, headings = chain(count, 1.0 / (rend * count))
    x0, x1, y0, y1 = bbox(points)
    last, theta = points[-1], headings[-1]
    gap = min((math.dist(last, p) for p, h in zip(points, headings)
               if abs(h - theta) > 0.5
               and abs(math.remainder(h - (theta - 2 * math.pi), 2 * math.pi)) < 0.2),
              default=float("nan"))
    centre = (last[0] - rend * math.sin(theta),
              last[1] + rend * math.cos(theta))
    return count, theta / (2 * math.pi), x1 - x0, y1 - y0, gap, centre


def winding_gap(radius: float, turns: int) -> float:
    """Radial gap between successive windings, r/(2N)."""
    return radius / (2.0 * turns)



CALCULATOR = """
<div class="calc">
  <div class="fields">
    <label>page L <input id="calc-L" type="number" value="100" min="10" max="2000" step="10"></label>
    <label>stroke w <input id="calc-w" type="number" value="1" min="0.05" max="20" step="0.05"></label>
    <label>final radius r <input id="calc-r" type="number" value="15" min="0.1" max="1000" step="0.5"></label>
  </div>
  <table id="calc-out"></table>
  <p class="hint" id="calc-note"></p>
  <div class="calc-illus">
    <svg id="calc-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"></svg>
    <p class="hint">Blue dashed: the final circle. Red dot: where the spiral meets it.</p>
  </div>
</div>
<script>
(function () {
  const L = document.getElementById("calc-L");
  const w = document.getElementById("calc-w");
  const r = document.getElementById("calc-r");
  const out = document.getElementById("calc-out");
  const note = document.getElementById("calc-note");
  const svg = document.getElementById("calc-svg");
  const f = (x, d = 2) => Number.isFinite(x) ? x.toFixed(d) : "—";
  function update() {
    const page = Math.max(1, +L.value || 100);
    const stroke = Math.max(0.01, +w.value || 1);
    const radius = Math.max(0.01, +r.value || 15);
    const rmin = 2 * stroke;
    const rmax = page / 2;
    const rbest = Math.cbrt(stroke * page * page / 2);
    const nmerge = radius / (2 * stroke);
    const nbox = Math.pow(page / (2 * radius), 2);
    const nmax = Math.min(nmerge, nbox);
    const gap = nmax > 0 ? radius / (2 * Math.max(nmax, 0.0001)) : NaN;
    out.innerHTML =
      "<tr><th>smallest circle (2w)</th><td>" + f(rmin) + "</td></tr>" +
      "<tr><th>largest full circle (L/2)</th><td>" + f(rmax) + "</td></tr>" +
      "<tr><th>best radius (wL²/2)^⅓</th><td>" + f(rbest) + "</td></tr>" +
      "<tr><th>turns before merging (r/2w)</th><td>" + f(nmerge, 1) + "</td></tr>" +
      "<tr><th>turns that fit the box</th><td>" + f(nbox, 1) + "</td></tr>" +
      "<tr><th>turns available</th><td><strong>" + f(nmax, 1) + "</strong></td></tr>" +
      "<tr><th>gap at that turn</th><td>" + f(gap) + " units</td></tr>";
    let verdict;
    if (radius < rmin) verdict = "Below 2w: the ribbon has no hole; it reads as a dot.";
    else if (radius > rmax) verdict = "Above L/2: a full circle does not fit; only an arc appears.";
    else if (radius > 1.25 * rbest) verdict = "Large and roomy, but few turns fit before the edge.";
    else if (radius < 0.75 * rbest) verdict = "Small and tight: it merges after only a turn or two.";
    else verdict = "Near the best radius: the most turns that fit without merging.";
    note.textContent = verdict;
    draw(page, stroke, radius);
  }

  function draw(page, stroke, radius) {
    const L = Math.max(page, 10);
    const nmerge = radius / (2 * stroke);
    const nbox = Math.pow(L / (2 * radius), 2);
    let N = Math.min(nmerge, nbox);
    if (!isFinite(N) || N <= 0) N = 1;
    const path = [];
    const centre = L / 2;
    if (N <= 1.0001) {
      for (let k = 0; k <= 240; k++) {
        const a = 2 * Math.PI * k / 240;
        path.push([centre + radius * Math.cos(a), centre + radius * Math.sin(a)]);
      }
    } else {
      const R = Math.min(radius * Math.sqrt(N), L / 2);
      const k0 = 1 / R, k1 = 1 / radius, theta = 2 * Math.PI * N;
      const kd = (k1 * k1 - k0 * k0) / (2 * theta);
      const len = (k1 - k0) / kd, n = 400, h = len / n;
      let x = 0, y = 0;
      const f = (sv) => {
        const t = k0 * sv + 0.5 * kd * sv * sv;
        return [Math.cos(t), Math.sin(t)];
      };
      for (let i = 0; i <= n; i++) {
        const sv = i * h;
        path.push([x, y]);
        const a = f(sv), b = f(sv + h / 2), c = f(sv + h);
        x += h * (a[0] + 4 * b[0] + c[0]) / 6;
        y += h * (a[1] + 4 * b[1] + c[1]) / 6;
      }
      const th = k0 * len + 0.5 * kd * len * len;
      const ex = x - radius * Math.sin(th), ey = y + radius * Math.cos(th);
      path.forEach(p => { p[0] += centre - ex; p[1] += centre - ey; });
    }
    const S = 100 / L;
    const d = path.map((p, i) => (i ? "L" : "M") + " " +
      (p[0] * S).toFixed(2) + " " + (100 - p[1] * S).toFixed(2)).join(" ");
    const end = path[path.length - 1];
    let grid = "";
    for (let g = 10; g < 100; g += 10) {
      grid += '<line x1="' + g + '" y1="0" x2="' + g + '" y2="100" stroke="#e8dfc8" stroke-width="0.25"/>';
      grid += '<line x1="0" y1="' + g + '" x2="100" y2="' + g + '" stroke="#e8dfc8" stroke-width="0.25"/>';
    }
    svg.innerHTML =
      grid +
      '<rect x="0" y="0" width="100" height="100" fill="none" stroke="#d8ccae" stroke-width="0.4"/>' +
      '<path d="' + d + '" fill="none" stroke="#2e2413" stroke-width="0.85"/>' +
      '<circle cx="50" cy="50" r="' + (radius * S).toFixed(2) + '" fill="none" ' +
      'stroke="#2f6f8f" stroke-width="0.45" stroke-dasharray="1.5 1.5"/>' +
      '<circle cx="' + (end[0] * S).toFixed(2) + '" cy="' + (100 - end[1] * S).toFixed(2) +
      '" r="1.3" fill="#b04a3a"/>';
  }
  [L, w, r].forEach(el => el.addEventListener("input", update));
  update();
})();
</script>
"""


def winding_points(radius: float, turns: float, entry: float, ds: float = 0.5):
    """A clothoid from an entry radius to `radius`, wound `turns` times.

    Curvature runs linearly from 1/entry to 1/radius. The path is translated
    so the osculating centre of its last chord sits at (50, 50), which is the
    centre of one 100-unit cell.
    """
    if turns <= 1.0000001:
        # one turn: a circle; a clothoid with no rate is the same thing
        pts = [(50 + radius * math.cos(2 * math.pi * k / 720),
                50 + radius * math.sin(2 * math.pi * k / 720)) for k in range(721)]
        return pts
    theta = 2 * math.pi * turns
    k0, k1 = 1.0 / entry, 1.0 / radius
    kd = (k1 * k1 - k0 * k0) / (2 * theta)
    length = (k1 - k0) / kd
    n = max(2, int(length / ds))
    h = length / n
    x = y = 0.0
    pts = []
    for i in range(n + 1):
        s_loc = i * h
        heading = k0 * s_loc + 0.5 * kd * s_loc * s_loc
        # osculating centre at the end, used only for the last point
        pts.append((x, y))
        def f(sv):
            t = k0 * sv + 0.5 * kd * sv * sv
            return math.cos(t), math.sin(t)
        a = f(s_loc); b = f(s_loc + h / 2); c = f(s_loc + h)
        x += h * (a[0] + 4 * b[0] + c[0]) / 6
        y += h * (a[1] + 4 * b[1] + c[1]) / 6
    end_heading = k0 * length + 0.5 * kd * length * length
    cx = x - radius * math.sin(end_heading)
    cy = y + radius * math.cos(end_heading)
    return [(50 + px - cx, 50 + py - cy) for px, py in pts]


def grid_markup() -> str:
    return ('<g stroke="#e8dfc8" stroke-width="0.25">'
            + "".join(f'<line x1="{g}" y1="0" x2="{g}" y2="100"/>' for g in range(10, 100, 10))
            + "".join(f'<line x1="0" y1="{g}" x2="100" y2="{g}"/>' for g in range(10, 100, 10))
            + "</g>")

def main() -> int:
    points, headings, count = fit_from_rest()
    theta = headings[-1]
    alpha = math.degrees(1.0 / (R_END * count))
    x0, x1, y0, y1 = bbox(points)
    width, height = x1 - x0, y1 - y0
    turns = theta / (2 * math.pi)

    # Gap to the previous winding: points whose heading is one turn behind the
    # last point's heading. Nearest is a distance, not a chord.
    last, last_heading = points[-1], headings[-1]
    merge_gap = min(
        (math.dist(last, p) for p, h in zip(points, headings)
         if abs(h - last_heading) > 0.5
         and abs(math.remainder(h - (last_heading - 2 * math.pi), 2 * math.pi)) < 0.2),
        default=float("nan"))

    # scale to the grid with a margin, y-up in the design, flip at output
    scale = (GRID - 2 * MARGIN) / max(width, height)
    def place(p):
        return (MARGIN + (p[0] - x0) * scale,
                # flip: the SVG y axis is down
                GRID - (MARGIN + (p[1] - y0) * scale))

    path = " ".join(
        f"{'M' if i == 0 else 'L'} {place(p)[0]:.2f},{place(p)[1]:.2f}"
        for i, p in enumerate(points))
    cx, cy = place((x0 + x1 / 2, y0 + y1 / 2))

    # three true-scale examples: the limits and the best turn budget
    three = []
    for label, radius, turns in (
            ("r 2 · 1 turn · dot", 2.0, 1.0),
            ("r 17 · 8.5 turns · best", 17.1, 8.55),
            ("r 40 · 1 turn · 40° tail", 40.0, 1.0 + 40.0 / 360.0)):
        entry = radius * math.sqrt(turns)
        pts = winding_points(radius, turns, max(entry, radius))
        d = " ".join(f"{'M' if i == 0 else 'L'} {x:.2f},{100 - y:.2f}"
                     for i, (x, y) in enumerate(pts))
        three.append(
            '<div class="cell"><svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">'
            + grid_markup()
            + f'<path d="{d}" fill="none" stroke="#2e2413" stroke-width="0.8"/>'
            + f'<circle cx="50" cy="50" r="{radius:g}" fill="none" stroke="#2f6f8f" '
              'stroke-width="0.35" stroke-dasharray="1.5 1.5"/>'
            + f'<circle cx="{pts[-1][0]:.2f}" cy="{100 - pts[-1][1]:.2f}" '
              'r="1.1" fill="#b04a3a"/>'
            + '</svg><p>' + label + '</p></div>')
    three_panels = '<div class="three">' + "".join(three) + '</div>'

    table = []
    for radius in (15.0, 30.0):
        for stroke in (0.5, 1.0, 2.0, 5.0):
            n = radius / (2.0 * stroke)
            table.append((radius, stroke, n, 2 * radius * math.sqrt(n)))

    rows = "\n".join(
        f"<tr><td>{radius:g}</td><td>{stroke:g}</td><td>{n:.1f}</td>"
        f"<td>{box:.0f}</td></tr>"
        for radius, stroke, n, box in table)

    family = []
    for radius in (5.0, 10.0, 15.0, 20.0, 30.0, 40.0):
        count_r, turns_r, width_r, height_r, gap_r, centre_r = fit_radius(radius)
        family.append((radius, turns_r, width_r, height_r, gap_r, centre_r))
    bounds = []
    for stroke in (0.5, 1.0, 2.0, 5.0):
        r_min = 2.0 * stroke
        r_max = GRID / 2.0
        r_best = (stroke * GRID * GRID / 2.0) ** (1.0 / 3.0)
        bounds.append((stroke, r_min, r_max, r_best, r_best / (2.0 * stroke)))
    bounds_rows = "\n".join(
        f"<tr><td>{w:g}</td><td>{rmin:g}</td><td>{rmax:g}</td>"
        f"<td>{rbest:.1f}</td><td>{nbest:.1f}</td></tr>"
        for w, rmin, rmax, rbest, nbest in bounds)

    family_rows = "\n".join(
        f"<tr><td>{radius:g}</td><td>{turns_r:.2f}</td>"
        f"<td>{width_r:.1f} × {height_r:.1f}</td>"
        f"<td>{'—' if math.isnan(gap_r) else f'{gap_r:.2f}'}</td>"
        f"<td>({centre_r[0]:.1f}, {centre_r[1]:.1f})</td></tr>"
        for radius, turns_r, width_r, height_r, gap_r, centre_r in family)

    # Osculating centre of the last chord, for the dashed final circle.
    centre = (last[0] - R_END * math.sin(last_heading),
              last[1] + R_END * math.cos(last_heading))
    circle = (f'<circle cx="{place(centre)[0]:.2f}" cy="{place(centre)[1]:.2f}" '
              f'r="{R_END * scale:.2f}" fill="none" stroke="#2f6f8f" '
              f'stroke-width="0.4" stroke-dasharray="2 2"/>')
    end_dot = (f'<circle cx="{place(points[-1])[0]:.2f}" '
               f'cy="{place(points[-1])[1]:.2f}" r="1.1" fill="#b04a3a"/>')

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Euler spiral — how many turns, and when the windings merge</title>
<style>
  :root {{ color-scheme: light; --paper:#f6f1e4; --card:#fffdf7; --ink:#2e2413;
    --muted:#7b6c4e; --gold:#8c6a21; --line:#d8ccae;
    --mono: ui-monospace,"SF Mono",Menlo,Consolas,monospace;
    --serif:"EB Garamond",Georgia,"Palatino Linotype",Palatino,serif; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; color:var(--ink); font:16px/1.55 var(--serif);
    background: radial-gradient(900px 440px at 12% -8%, #fcf9ef 0, transparent 60%), var(--paper); }}
  main {{ max-width: 900px; margin: 0 auto; padding: 34px 22px 70px; }}
  h1 {{ font-size: 28px; margin: 0 0 4px; }}
  .lead {{ color: var(--gold); margin: 0 0 18px; }}
  h2 {{ font: 600 11px/1.2 var(--mono); letter-spacing: .12em; text-transform: uppercase;
    color: var(--muted); margin: 26px 0 8px; }}
  .panel {{ background: var(--card); border: 1px solid var(--line); border-radius: 6px; padding: 14px; }}
  .art svg {{ display:block; width:100%; height:auto; background:#fff; }}
  table {{ border-collapse: collapse; width: 100%; font: 12px/1.5 var(--mono); }}
  th, td {{ border-bottom: 1px solid var(--line); padding: 6px 4px; text-align: left; }}
  th {{ color: var(--muted); font-weight: 500; }}
  .scroll {{ overflow-x: auto; }}
  code {{ font: 12px/1 var(--mono); background:#fbf8ee; border:1px solid var(--line);
    border-radius:3px; padding:2px 4px; }}
  .three {{ display:grid; grid-template-columns:repeat(3, 1fr); gap:10px; }}
  .three .cell {{ border:1px solid var(--line); border-radius:4px; padding:6px; background:#fff; }}
  .three svg {{ display:block; width:100%; height:auto; }}
  .three p {{ margin:6px 0 0; font:10px/1.4 var(--mono); color:var(--muted); text-align:center; }}
  .calc .fields {{ display:flex; flex-wrap:wrap; gap:10px; margin-bottom:10px; font:12px var(--mono); }}
  .calc label {{ display:flex; flex-direction:column; gap:4px; color:var(--muted); }}
  .calc input {{ font:13px var(--mono); padding:4px 6px; border:1px solid var(--line);
    border-radius:4px; background:#fff; width:110px; color:var(--ink); }}
  .calc .hint {{ margin:10px 0 0; color:var(--gold); }}
  .calc-illus {{ margin-top:12px; }}
  .calc-illus svg {{ display:block; width:100%; max-width:300px; height:auto;
    margin:0 auto; background:#fff; border:1px solid var(--line); border-radius:4px; }}
  .back {{ font: 12px var(--mono); margin-bottom: 16px; }}
  a {{ color: var(--gold); }}
  @media (max-width: 620px) {{
    main {{ padding:22px 14px 60px; }}
    table {{ font-size:10px; }}
    th,td {{ padding:4px 2px; }}
    .three {{ grid-template-columns:1fr; }}
  }}
</style>
</head>
<body>
<main>
  <p class="back"><a href="sandbox.html">← sandbox</a></p>
  <h1>Euler spiral: turns and merging</h1>
  <p class="lead">One-unit chords on a 100 grid. How many times around, and when the windings touch.</p>

  <h2>1. From rest, fitted to the grid</h2>
  <div class="panel art">
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <g stroke="#e8dfc8" stroke-width="0.25">
        {''.join(f'<line x1="{g}" y1="0" x2="{g}" y2="100"/>' for g in range(10, 100, 10))}
        {''.join(f'<line x1="0" y1="{g}" x2="100" y2="{g}"/>' for g in range(10, 100, 10))}
      </g>
      <path d="{path}" fill="none" stroke="#2e2413" stroke-width="0.7"/>
      {circle}
      {end_dot}
    </svg>
  </div>
  <div class="panel" style="margin-top:12px">
    <table>
      <tr><th>chords</th><td>{count}</td><th>turn per chord</th><td>{alpha:.4f}°</td></tr>
      <tr><th>turns</th><td>{turns:.2f}</td><th>bounding box</th><td>{width:.1f} × {height:.1f}</td></tr>
      <tr><th>final radius</th><td>{R_END:g}</td><th>gap to the previous winding</th><td>{merge_gap:.1f} units</td></tr>
    </table>
    <p style="margin-top:10px">The blue dashed circle is the final radius; the red dot is
    where the spiral meets it. Almost the whole box is the long near-straight approach, so
    the curve makes only <strong>{turns:.2f} turns</strong> before it is already the circle. The previous winding is <strong>{merge_gap:.1f} units</strong> away: no line
    width collides on this grid.</p>
  </div>

  <h2>2. Already winding: the rule</h2>
  <div class="panel">
    <p>A spiral that enters already curved can wind many turns inside the same circle. The radial
    gap between successive windings is about <code>r / (2N)</code> for N turns at final radius r.
    Setting that equal to the stroke width w gives <code>N = r / (2w)</code>. The outer radius
    needed is about <code>r √N</code>, so the box grows as <code>2r √N</code>.</p>
    <div class="scroll"><table>
      <tr><th>final radius r</th><th>stroke width w</th><th>turns before merging</th><th>box about</th></tr>
      {rows}
    </table></div>
    <p style="margin-top:10px">So for a 30-wide circle (r = 15): a 1-unit line merges at about
    <strong>7.5 turns</strong>, a 2-unit line at 3.8, a 5-unit ribbon at 1.5. For a 60-wide circle
    (r = 30) double those. The “it looks like a circle” point and the “the windings touch” point are
    the same event: the radius changes by 1/(2N) per turn, which is 5% at N=10 and 2% at N=25, by
    which time the gap is smaller than any drawn line.</p>
  </div>

  <h2>3. The family in the same box</h2>
  <div class="panel">
    <p>A clothoid has a scale, not a fixed size. Fit the box to 80 and vary the final
    radius: every row is the same construction, and every one has a different turn
    count, a different centre and a different last gap. The radius and centre are
    outputs of the scale, not inputs.</p>
    <div class="scroll"><table>
      <tr><th>final radius r</th><th>turns from rest</th><th>box</th>
          <th>last-winding gap</th><th>osculating centre</th></tr>
      {family_rows}
    </table></div>
    <p style="margin-top:10px">Smaller final radius packs more turns into the same box and
    closes the gap fast: at r = 5 the gap is 0.31 units, so even a half-unit line merges
    before the end. At r = 15 the gap is 16.3 units: from rest, this spiral is nowhere near
    touching itself. The winding case above is the other way to get many turns — start at an
    entry radius instead of at rest.</p>
  </div>

  <h2>4. Is there a maximum and minimum circle?</h2>
  <div class="panel">
    <p>Nothing in the clothoid has a size: scale it and every length scales with it. On a
    bounded page the limits are the page and the stroke width.</p>
    <ul>
      <li><strong>Largest full circle:</strong> half the page, <code>r = L/2</code>. At
      L = 100 that is r = 50, a 100-wide circle touching the edges. Larger radii still
      appear as arcs, never as a closed circle in the box.</li>
      <li><strong>Smallest circle with a stroke:</strong> <code>r = 2w</code>, where w is the
      stroke width. At r = 2w the inner hole is exactly one stroke wide; any smaller and the
      ribbon has no hole and reads as a disc. With 1-unit drafting points there is also a
      floor at r = 0.5, but the stroke is almost always the binding limit.</li>
      <li><strong>The turn budget:</strong> a winding spiral of N turns at radius r needs a
      box about <code>2r√N</code>, and its gap is <code>r/(2N)</code>. Both must hold, so
      <code>N ≤ min(r/(2w), (L/2r)²)</code>. The two limits meet at
      <code>r* = (wL²/2)^(1/3)</code>, which is the radius that buys the most turns without
      merging.</li>
    </ul>
    <div class="scroll"><table>
      <tr><th>stroke w</th><th>r min (2w)</th><th>r max (L/2)</th>
          <th>best r*</th><th>turns at r*</th></tr>
      {bounds_rows}
    </table></div>
    <p style="margin-top:10px">For a 100 grid and a 1-unit line: the smallest circle is
    r = 2 (4 across), the largest is r = 50 (100 across), and the best compromise is
    r ≈ 17 with about 8.5 turns. A 5-unit ribbon moves the best radius to ≈ 29 and cuts the
    turns to about 3. That is the real trade: the wider the stroke, the larger the circle
    must be, and the fewer turns it can carry.</p>
  </div>

  <h2>5. The three sizes, at the same scale</h2>
  <div class="panel">
    <p>Same 100 grid, same 1-unit stroke. Left: the smallest circle with a hole
    (r = 2w = 2), one turn, no room for a tail. Middle: the best turn budget
    (r ≈ 17, about 8.5 turns), the Euler spiral winding in from the page edge.
    Right: r = 40 with a 40° entry tail — the full-circle bound is 50, but 50
    leaves no room for a tail, so the largest example is set back to 40. The blue
    dashed circle is the final radius; the red dot is where the spiral meets it; the
    grid is 10 units.</p>
    {three_panels}
  </div>

  <h2>6. Try your own numbers</h2>
  <div class="panel">
    {CALCULATOR}
  </div>

  <h2>What the napkin got right, and what it missed</h2>
  <div class="panel">
    <p>The 80 box and a 30-wide final circle are right: the computed box is
    {width:.1f} × {height:.1f}, and the ink ends at ({points[-1][0]:.1f}, {points[-1][1]:.1f}).
    The <em>centre</em> is about (51, 51), not 65 — 65 is where the ink stops, not the middle
    of the circle. The missed part is the count: a clothoid from rest spends most of its
    length almost straight, so only about one turn is left in the box. To get many turns you
    must start already curving (an entry radius), which is the same object trimmed.</p>
    <p>With a finite entry radius R the turn count is set by <code>(R/r)²</code>. For R = 41 and
    r = 15 that is 7.5 turns — exactly the collision count for a 1-unit line. That is the real
    answer: <strong>about seven and a half turns</strong>, and the last gap is one unit.</p>
  </div>
</main>
</body>
</html>
"""
    path = ROOT / "docs" / "spiral-turns.html"
    path.write_text(page, encoding="utf-8")
    print(path)
    print(f"from rest: {count} chords, {turns:.2f} turns, box {width:.1f}x{height:.1f}, "
          f"last gap {merge_gap:.1f}")
    for radius, stroke, n, box in table:
        print(f"  r={radius:g} w={stroke:g}: N={n:.1f}, box~{box:.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
