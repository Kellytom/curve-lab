"""Euler spiral to cubic: the 2021 endpoint-parabola rule, measured.

    .venv/bin/python scripts/euler_parabola_fit.py

Writes `workbench/euler-parabola-fit.html`. The interactive canvas is a free
cubic editor: drag the two ends, or drag the two handles along their endpoint
parabolas. The comparison panels measure the house seam against the true Euler
spiral. The house seam already uses this exact rule, so the numbers are a
validation rather than a new optional fit.
"""

from __future__ import annotations

import html
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import euler_fit
from curve_lab.bezier import cubic_at, fit_span
INK = "#2e2413"
MUTED = "#7b6c4e"
PAPER = "#fffdf7"
GRID = "#e4dcc6"
GOLD = "#c9a441"
DOT = "#8c6a21"
BLUE = "#1f5fa8"
GREEN = "#3f7d4e"


def fmt(x: float) -> str:
    if x == 0:
        return "0"
    if abs(x) < 1e-3 or abs(x) >= 1e4:
        return f"{x:.3e}"
    return f"{x:.6f}"


def study_svg(kind: str, fig: str, n: int = 4, compare: int | None = None,
              label: str | None = None, show_handles: bool = False,
              w: int = 470, h: int = 360, data: dict | None = None):
    data = data or euler_fit.study(kind)
    seg = data["segment"]
    fit = euler_fit.fit_segment(seg, n)
    truth = [seg.point(i / 240) for i in range(241)]
    cubic = []
    for span in fit["spans"]:
        cubic.extend(cubic_at(span, i / 30) for i in range(31))
    other = []
    if compare is not None:
        other_fit = euler_fit.fit_segment(seg, compare)
        for span in other_fit["spans"]:
            other.extend(cubic_at(span, i / 30) for i in range(31))
    pts = truth + cubic + other
    if show_handles:
        for span in fit["spans"]:
            pts.extend([span["p0"], span["c1"], span["c2"], span["p3"]])
    x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts)
    x1, y1 = max(p[0] for p in pts), max(p[1] for p in pts)
    dx, dy = (x1 - x0) or 1, (y1 - y0) or 1
    pad = 0.14
    x0, x1 = x0 - pad * dx, x1 + pad * dx
    y0, y1 = y0 - pad * dy, y1 + pad * dy
    k = min((w - 26) / (x1 - x0), (h - 34) / (y1 - y0))
    ox, oy = (w - (x1 - x0) * k) / 2, 18 + (h - 26 - (y1 - y0) * k) / 2

    def put(p):
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k)

    body = []
    # grid and axes
    for gx in [i / 10 for i in range(11)]:
        if x0 <= gx <= x1:
            a, b = put((gx, y0)), put((gx, y1))
            body.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GRID}"/>')
    for gy in [i / 20 for i in range(-4, 21)]:
        if y0 <= gy <= y1:
            a, b = put((x0, gy)), put((x1, gy))
            body.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GRID}"/>')
    def path(points, colour, width, dash=None):
        d = " ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in points)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        body.append(f'<path d="M {d}" fill="none" stroke="{colour}" stroke-width="{width}" stroke-linejoin="round"{da}/>')
    path(truth, INK, 2.4)
    if other:
        path(other, MUTED, 1.4, "6 4")
    path(cubic, GOLD, 1.7, "5 4")
    if show_handles:
        for piece, span in enumerate(fit["spans"], start=1):
            path([span["p0"], span["c1"], span["c2"], span["p3"]],
                 MUTED, 1.0, [4, 4])
            for point, tag in ((span["c1"], f"c{2*piece-1}"),
                               (span["c2"], f"c{2*piece}")):
                q = put(point)
                body.append(f'<rect x="{q[0]-3:.1f}" y="{q[1]-3:.1f}" width="6" height="6" fill="{GOLD}" stroke="{INK}" stroke-width="0.8"/>')
                body.append(f'<text x="{q[0]+4:.1f}" y="{q[1]-4:.1f}" font-family="ui-monospace,Menlo,monospace" font-size="8" fill="{MUTED}">{tag}</text>')
    for p in (truth[0], truth[-1]):
        q = put(p)
        body.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="3.5" fill="{DOT}" stroke="{PAPER}"/>')
    title = label or f"{kind} Euler"
    body.append(f'<text x="12" y="18" font-family="Georgia,serif" font-size="13" font-weight="600" fill="{INK}">Fig. {fig} · {title} · n={n}</text>')
    body.append(f'<text x="12" y="{h-8}" font-family="ui-monospace,Menlo,monospace" font-size="9" fill="{MUTED}">x →</text>')
    body.append(f'<text x="12" y="34" font-family="ui-monospace,Menlo,monospace" font-size="9" fill="{MUTED}">y ↑</text>')
    legend = "— true Euler   --- current seam"
    if other:
        legend = "— true Euler   --- one piece   — two pieces"
    elif show_handles:
        legend = f"— true Euler   — {'one piece' if n == 1 else 'two pieces'}   -- control + handles"
    if show_handles and other:
        legend += "   -- control + handles"
    body.append(f'<text x="12" y="48" font-family="ui-monospace,Menlo,monospace" font-size="9" fill="{MUTED}">{legend}</text>')
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{w}" height="{h}" fill="{PAPER}" stroke="{GRID}"/>'
            + "".join(body) + "</svg>")


def table_html(data: dict) -> str:
    rows = []
    for i, r in enumerate(data["rows"]):
        ratio = "—"
        if i and data["rows"][i - 1]["error"] > 0:
            ratio = fmt(data["rows"][i - 1]["error"] / r["error"])
        rel = abs(r["arclength_error"]) / data["true_arclength"]
        rows.append(
            f"<tr><td>{r['n']}</td><td>{fmt(r['error'])}</td><td>{ratio}</td>"
            f"<td>{fmt(r['arclength'])}</td><td>{fmt(r['arclength_error'])}</td>"
            f"<td>{rel:.2e}</td><td>{r['clamped']}</td></tr>")
    # asymptotic slope only from n=4 on; the n=1 symmetric case is accidentally
    # good because the first error mode is small.
    slopes = []
    for a, b in zip(data["rows"][2:], data["rows"][3:]):
        if a["error"] > 0 and b["error"] > 0:
            slopes.append(math.log(a["error"] / b["error"]) / math.log(2))
    slope = sum(slopes) / len(slopes) if slopes else 0.0
    return (
        f"<p class=\"meta\">endpoint tangents: "
        f"{math.degrees(data['endpoint_tangents'][0]):.2f}° / "
        f"{math.degrees(data['endpoint_tangents'][1]):.2f}° · "
        f"true arclength: {data['true_arclength']:.6f} · "
        f"asymptotic slope n=4→16: <strong>{slope:.2f}</strong></p>"
        "<div class=\"table-wrap\"><table><tr><th>n</th><th>max error</th>"
        "<th>error ratio</th><th>cubic arc</th><th>arc error</th>"
        "<th>relative arc error</th><th>clamped</th></tr>"
        + "".join(rows) + "</table></div>")


def handle_table(kind: str, n: int = 2, data: dict | None = None) -> str:
    data = data or euler_fit.study(kind)
    fit = euler_fit.fit_segment(data["segment"], n)
    rows = []
    for i, span in enumerate(fit["spans"], start=1):
        def p(v):
            return f"({v[0]:.6f}, {v[1]:.6f})"
        rows.append(f"<tr><td>{i}</td><td>{p(span['p0'])}</td><td>{p(span['c1'])}</td>"
                    f"<td>{p(span['c2'])}</td><td>{p(span['p3'])}</td></tr>")
    label = "one-piece" if n == 1 else "two-piece"
    return (f"<p class=\"meta\">{label} control points, normalized to the chord</p>"
            "<div class=\"table-wrap\"><table><tr><th>piece</th><th>P0</th>"
            "<th>c1</th><th>c2</th><th>P3</th></tr>" + "".join(rows) + "</table></div>")


def angle_meta(data: dict) -> str:
    rows = data["rows"]
    return (f"<p class=\"meta\">θ = {math.degrees(data['endpoint_tangents'][0]):.1f}° · "
            f"one-piece error {rows[0]['error']:.5f} · "
            f"two-piece error {rows[1]['error']:.5f} · "
            f"n=4 {rows[2]['error']:.5f}</p>")


PYTH_ANGLES = (0.0, 4.34948822922, 16.260204708312, 20.609692937532,
               32.520409416624, 36.869897645844, 53.130102354156,
               57.479590583376, 69.390307062468, 73.739795291688,
               85.65051177078, 90.0)


def _fast_spans(seg, n: int):
    return [fit_span(i / n, (i + 1) / n, seg.point, seg.tangent)
            for i in range(n)]


def _span_json(span: dict) -> dict:
    return {key: [float(span[key][0]), float(span[key][1])]
            for key in ("p0", "c1", "c2", "p3")}


def _fast_error(seg, true_points, spans, samples: int = 17) -> float:
    worst = 0.0
    for span in spans:
        for i in range(samples):
            x, y = cubic_at(span, i / (samples - 1))
            d = min(math.hypot(x - tx, y - ty) for tx, ty in true_points)
            worst = max(worst, d)
    return worst


def smooth_records():
    """True curves and 1/2-piece fits on a 0.5-degree grid + 3125 angles."""
    angles = sorted({round(i * 0.5, 6) for i in range(181)} |
                    {round(a, 6) for a in PYTH_ANGLES})
    records = []
    for angle in angles:
        seg = euler_fit.s_angle(angle)
        true_points = [seg.point(i / 60) for i in range(61)]
        error_points = [seg.point(i / 400) for i in range(401)]
        one_spans = _fast_spans(seg, 1)
        two_spans = _fast_spans(seg, 2)
        records.append({
            "a": angle,
            "true": [[float(x), float(y)] for x, y in true_points],
            "one": [_span_json(sp) for sp in one_spans],
            "two": [_span_json(sp) for sp in two_spans],
            "e1": _fast_error(seg, error_points, one_spans),
            "e2": _fast_error(seg, error_points, two_spans),
        })
    return records


PYTH_TRIPLES = ((3, 4, 5), (4, 3, 5), (5, 12, 13), (12, 5, 13),
                (8, 15, 17), (15, 8, 17), (7, 24, 25), (24, 7, 25),
                (20, 21, 29), (21, 20, 29))


def pyth_cases():
    out = []
    for a, b, c in PYTH_TRIPLES:
        out.append({
            "a": a, "b": b, "c": c,
            "label": f"{a}-{b}-{c}",
            "angle": -math.degrees(math.atan2(b, a)),
            "p0": [0, 0],
            "p1": [a, -b],
            "p2": [2*c-a, b],
            "p3": [2*c, 0],
        })
    return out


def main():
    studies = {kind: euler_fit.study(kind) for kind in ("symmetric", "asymmetric", "s90")}
    sym_svg = study_svg("symmetric", "E2")
    asym_svg = study_svg("asymmetric", "E3")
    records = smooth_records()
    records_json = json.dumps(records, separators=(",", ":"))
    default_index = min(range(len(records)),
                        key=lambda i: abs(records[i]["a"] - 90.0))
    button_html = "".join(
        f'<button type="button" data-angle="{a:.12f}">{a:.2f}°</button>'
        for a in PYTH_ANGLES)
    pyth = pyth_cases()
    pyth_json = json.dumps(pyth, separators=(",", ":"))
    pyth_buttons = "".join(
        f'<button type="button" data-index="{i}">{c["label"]}</button>'
        for i, c in enumerate(pyth))
    pyth_rows = "".join(
        f'<tr><td>{c["label"]}</td><td>{c["angle"]:.2f}°</td>'
        f'<td>{2*c["c"]}</td><td>({c["p1"][0]}, {c["p1"][1]})</td>'
        f'<td>({c["p2"][0]}, {c["p2"][1]})</td></tr>'
        for c in pyth)
    pyth_table = ("<div class=\"table-wrap\"><table><tr><th>triple</th><th>tangent</th>"
                  "<th>chord</th><th>P1</th><th>P2</th></tr>" + pyth_rows +
                  "</table></div>")
    sym_table = table_html(studies["symmetric"])
    asym_table = table_html(studies["asymmetric"])
    s48_table = table_html(studies["s90"])

    template = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Euler spiral to cubic · parabola handles</title>
<style>
:root{--paper:#fbf7ec;--ink:#2e2413;--muted:#7b6c4e;--rule:#d8ccae;--gold:#c9a441;--green:#3f7d4e;--blue:#1f5fa8}
*{box-sizing:border-box}
body{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}
main{max-width:1480px;margin:0 auto;padding:32px 22px 70px}
.eyebrow{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}
h1{font-size:30px;line-height:1.1;margin:0 0 6px}
.lede{max-width:880px;color:var(--muted);margin:0 0 20px}
.panel{background:var(--paper);border:1px solid var(--rule);padding:16px 18px;margin:0 0 18px}
h2{font-size:20px;margin:0 0 8px}
p{margin:0 0 10px}
canvas{display:block;width:100%;height:auto;background:var(--paper);border:1px solid var(--rule);touch-action:none;cursor:crosshair}
.controls{display:flex;flex-wrap:wrap;gap:12px 22px;align-items:center;margin:10px 0 2px;font:12px/1.4 ui-monospace,Menlo,monospace;color:var(--muted)}
.controls button{font:12px ui-monospace,Menlo,monospace;background:var(--paper);border:1px solid var(--rule);padding:5px 10px;color:var(--ink);cursor:pointer}
.controls button:hover{background:#f4ecd7}
.readout{font:11px/1.6 ui-monospace,Menlo,monospace;color:var(--muted);margin:9px 0 0;white-space:pre-wrap}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}
.stack{display:grid;grid-template-columns:1fr;gap:18px}
.variant[hidden]{display:none}
.slider{display:flex;gap:10px;align-items:center;font:11px ui-monospace,Menlo,monospace;color:var(--muted);margin:0 0 10px}
.slider input{flex:1;max-width:360px}
.slider span{min-width:36px;color:var(--ink)}
.figure{margin:0;background:var(--paper);border:1px solid var(--rule);padding:10px}
.smooth-figure{background:var(--paper);border:1px solid var(--rule);padding:10px;margin:0 0 18px}
.smooth-figure h3{font:600 14px/1.3 Georgia,serif;margin:0 0 9px}
.angle-bar{display:grid;grid-template-columns:minmax(220px,1fr) 2fr;gap:10px 16px;align-items:start;margin:0 0 8px}
.angle-buttons{display:flex;flex-wrap:wrap;gap:5px}
.angle-buttons button{font:10px ui-monospace,Menlo,monospace;border:1px solid var(--rule);background:var(--paper);color:var(--ink);padding:3px 5px;cursor:pointer}
.angle-buttons button:hover{background:#f4ecd7}
.smooth-figure canvas{border:1px solid var(--rule)}
.pyth-buttons{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 10px}
.pyth-buttons button{font:10px ui-monospace,Menlo,monospace;border:1px solid var(--rule);background:var(--paper);color:var(--ink);padding:4px 7px;cursor:pointer}
.pyth-buttons button:hover{background:#f4ecd7}
#pyth-canvas{border:1px solid var(--rule);margin:0 0 8px}
.figure svg{display:block;width:100%;height:auto}
.meta{font:11px/1.55 ui-monospace,Menlo,monospace;color:var(--muted);margin:8px 0}
.table-wrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;font:10px/1.4 ui-monospace,Menlo,monospace}
th,td{border:1px solid var(--rule);padding:4px 5px;text-align:right;white-space:nowrap}
th{color:var(--muted);font-weight:400}
.small{font:11px/1.55 ui-monospace,Menlo,monospace;color:var(--muted)}
a{color:var(--blue)}
code{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}
</style>
</head>
<body>
<main>
<p class="eyebrow">curve-lab · fitted option</p>
<h1>Euler spiral → cubic Bézier</h1>
<p class="lede">The current cubic seam already uses the 2021 endpoint-parabola rule: the handle sits where the endpoint tangent meets the parabola. The editor below is the handle construction made draggable; the panels measure the current seam against the true Euler spiral, not a second fit.</p>

<section class="panel">
  <h2>Fig. E1 · move the ends and the handles</h2>
  <canvas id="editor" width="1440" height="1296" aria-label="Interactive cubic with endpoint-parabola handle constraints"></canvas>
  <div class="controls">
    <button id="reset" type="button">reset</button>
    <label><input type="checkbox" id="show-parab" checked> endpoint parabolas</label>
    <label><input type="checkbox" id="show-offset" checked> offsets</label>
    <label><input type="checkbox" id="show-target" checked> Euler target</label>
    <label><input type="checkbox" id="snap-int" checked> snap points to integers</label>
    <label><input type="checkbox" id="free-handles"> integer handles (off-guide)</label>
    <button id="preset-345" type="button">6-8-10 chord</button>
    <button id="preset-345-handles" type="button">345 integer handles</button>
    <button id="preset-s53" type="button">S 53° integer</button>
    <button id="snap-handles" type="button">snap handles</button>
    <label>d <input type="range" id="offset-d" min="0" max="1" step="0.05" value="0.55"></label>
    <button id="save-state" type="button">save state</button>
    <button id="restore-state" type="button">restore state</button>
    <button id="save-json" type="button">save JSON</button>
    <span id="save-status"></span>
    <span>drag ○ ends · drag □ handles</span>
  </div>
  <p class="readout" id="readout" aria-live="polite"></p>
  <p class="small"><strong>Save state / save JSON apply to Fig. E1 only.</strong> Figs. E4 and E5 are static comparison plates.</p>
  <p class="small">The violet solid curve is the true Euler segment through the current endpoints and endpoint tangents — what the cubic is trying to copy. A single cubic follows a C-shaped Euler to roughly 90° of endpoint tangent, but an S-shaped Euler needs a curvature reversal and starts to visibly degrade around 45°. Beyond those limits, split at the inflection or into more spans. The blue/red offset curves are dense normal offsets of the current cubic, drawn for comparison; they are not the exact Euler parallel.</p>
  <p class="small"><strong>3-4-5 note.</strong> The endpoints and the chord can sit on an integer Pythagorean vector such as (6,8,10). The handle guides themselves are parabolas, and for a unit chord they have no integer local points: <code>12u = 4 − 9v²</code> (left) and <code>12u = 8 + 9v²</code> (right) are impossible for integers. “Snap handles” therefore rounds to the nearest integer and reports how far the handle left the guide. The 3-4-5 offset hits come from the normal direction, not from placing a handle on the lattice.</p>
</section>

<section class="panel" id="section-ii">
  <h2>Section II · the integer cubic</h2>
  <p>This is the part that is actually integer-friendly. For a Pythagorean triple \(a^2+b^2=c^2\), take</p>
  <div class="formula">P0 = (0,0),  P1 = (a,−b),  P2 = (2c−a,b),  P3 = (2c,0)</div>
  <p>The chord is <code>2c</code>, both handle arms have length <code>c</code>, and both endpoint tangents are at <code>−atan2(b,a)</code>. Every control point is an integer. This is a cubic construction; it is not claiming the handles are on the Euler guide parabolas.</p>
  <p><strong>Base case.</strong> (3,4,5): P0=(0,0), P1=(3,−4), P2=(7,4), P3=(10,0). Chord 10, arms 5, tangents −53.13°, integer handles.</p>
  <p><strong>Rotation.</strong> Rotate by a Pythagorean angle and scale by the denominator: (3,4,5) rotated by 53.13° and scaled by 5 becomes P0=(0,0), P1=(25,0), P2=(5,40), P3=(30,40). Rotated by 36.87° instead it becomes P0=(0,0), P1=(24,−7), P2=(16,37), P3=(40,30). The angle between each handle and the chord stays 53.13°.</p>
  <p><strong>Other slopes.</strong> The same construction works for every Pythagorean triple. Select one:</p>
  <div class="pyth-buttons" id="pyth-buttons">__PYTH_BUTTONS__</div>
  <canvas id="pyth-canvas" width="1000" height="380"></canvas>
  <p class="meta" id="pyth-meta"></p>
  __PYTH_TABLE__
</section>

<section class="panel">
  <h2>What is being measured</h2>
  <p>The current seam's arm is</p>
  <p class="small"><code>arm = |chord| / (3 cos²(θ/2)) = 2|chord| / (3(1 + cos θ))</code></p>
  <p>which is exactly the intersection of the endpoint tangent with <code>x = 1/3 − (3/4)y²</code> on the normalized chord. So there is <strong>no separate fitted option to switch to</strong>; the comparison is a validation of the existing seam. The error is the maximum sampled normal distance from the cubic to the true Euler spiral; arclength is the true arclength normalized to chord 1.</p>
</section>

<section class="panel">
  <h2>Comparison</h2>
  <div class="grid">
    <figure class="figure">
      __SYM_SVG__
      __SYM_TABLE__
    </figure>
    <figure class="figure">
      __ASYM_SVG__
      __ASYM_TABLE__
    </figure>
  </div>
  <p class="small">The asymptotic slope is taken from n=4, 8, 16. The n=1 symmetric fit is accidentally good, so it is not used to estimate the exponent. A slope near 5 is the claimed n⁵ behavior; doubling n should reduce error by about 32×.</p>
</section>

<section class="panel">
  <h2>Second example · smooth S angle, one piece vs two</h2>
  <p>The sliders move both handle angles continuously in 0.5° steps. The side buttons jump to the integer points on a <strong>3125-radius circle</strong> — the Pythagorean slopes.</p>
  <div class="smooth-figure">
    <h3>Fig. E4 · one piece</h3>
    <div class="angle-bar">
      <label class="slider">angle <input type="range" id="e4-angle" min="0" max="__MAX__" step="1" value="__DEFAULT__"> <span id="e4-angle-value"></span></label>
      <div class="angle-buttons" id="e4-buttons">__E4_BUTTONS__</div>
    </div>
    <canvas id="e4-canvas" width="1000" height="360"></canvas>
    <p class="meta" id="e4-meta"></p>
  </div>
  <div class="smooth-figure">
    <h3>Fig. E5 · two pieces</h3>
    <div class="angle-bar">
      <label class="slider">angle <input type="range" id="e5-angle" min="0" max="__MAX__" step="1" value="__DEFAULT__"> <span id="e5-angle-value"></span></label>
      <div class="angle-buttons" id="e5-buttons">__E5_BUTTONS__</div>
    </div>
    <canvas id="e5-canvas" width="1000" height="360"></canvas>
    <p class="meta" id="e5-meta"></p>
  </div>
  <p class="small">The 3125-circle angle set is 0°, 4.35°, 16.26°, 20.61°, 32.52°, 36.87°, 53.13°, 57.48°, 69.39°, 73.74°, 85.65°, 90°. The table below remains the 90° reference.</p>
  <div class="table-wrap">__S48_TABLE__</div>
</section>

<section class="panel">
  <h2>Verdict</h2>
  <p>The rule is a good fitted seam and is already in use. The p-triple polygon and rational rails remain the exact route; this is a drawing approximation. It does not make handles integer, and it is not the bounding-parabola intersection method.</p>
</section>

<section class="panel">
  <h2>Source</h2>
  <p><a href="https://raphlinus.github.io/curves/2021/02/19/parallel-curves.html">Levien, “Cleaner parallel curves with Euler spirals” (2021)</a>, section “Euler spirals to cubic Béziers”; and <a href="https://raphlinus.github.io/curves/2018/12/08/euler-spiral.html">“Secrets of smooth Béziers revealed” (2018)</a>.</p>
  <p class="small">Implementation reference: <a href="https://github.com/linebender/kurbo/pull/169">kurbo PR #169</a>, <code>src/euler.rs</code> (<code>EulerSeg::to_cubics</code>), Apache-2.0, © 2021 The kurbo Authors. The Python measurement here is an independent port of the published rule.</p>
</section>
</main>

<script>
(() => {
  const W = 1440, H = 1296, PAD = 52;
  const canvas = document.getElementById('editor');
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  canvas.width = W * dpr; canvas.height = H * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  const DOM = {x0: 0, x1: 20, y0: 0, y1: 18};
  const scale = Math.min((W - 2*PAD)/(DOM.x1-DOM.x0), (H - 2*PAD)/(DOM.y1-DOM.y0));
  const ox = (W - (DOM.x1-DOM.x0)*scale)/2, oy = (H - (DOM.y1-DOM.y0)*scale)/2;
  const SX = x => ox + (x-DOM.x0)*scale;
  const SY = y => H - oy - (y-DOM.y0)*scale;

  const START = {p0:{x:4,y:2}, p3:{x:16,y:2}, v0:-0.25, v1:0.25};
  let P0={...START.p0}, P3={...START.p3}, v0=START.v0, v1=START.v1;
  let freeHandles = false;
  let H1 = null, H2 = null;
  let drag = null;

  function clamp(v,lo,hi){return Math.max(lo,Math.min(hi,v));}
  function frame(){
    const dx=P3.x-P0.x, dy=P3.y-P0.y, L=Math.hypot(dx,dy)||1e-9;
    const e={x:dx/L,y:dy/L}, n={x:-dy/L,y:dx/L};
    return {L,e,n};
  }
  function local(u,v){
    const {L,e,n}=frame();
    return {x:P0.x+L*(u*e.x+v*n.x), y:P0.y+L*(u*e.y+v*n.y)};
  }
  function handles(){
    if(freeHandles && H1 && H2) return {p1:{...H1}, p2:{...H2}};
    return {
      p1: local(1/3 - 0.75*v0*v0, v0),
      p2: local(2/3 + 0.75*v1*v1, v1),
    };
  }
  function cubic(t){
    const {p1,p2}=handles();
    const u=1-t;
    return {
      x:u*u*u*P0.x+3*u*u*t*p1.x+3*u*t*t*p2.x+t*t*t*P3.x,
      y:u*u*u*P0.y+3*u*u*t*p1.y+3*u*t*t*p2.y+t*t*t*P3.y,
    };
  }
  function cubicDeriv(t){
    const {p1,p2}=handles();
    const u=1-t;
    return {
      x:3*u*u*(p1.x-P0.x)+6*u*t*(p2.x-p1.x)+3*t*t*(P3.x-p2.x),
      y:3*u*u*(p1.y-P0.y)+6*u*t*(p2.y-p1.y)+3*t*t*(P3.y-p2.y),
    };
  }
  function offsetPoint(t,d){
    const p=cubic(t), v=cubicDeriv(t), l=Math.hypot(v.x,v.y)||1e-9;
    return {x:p.x-d*v.y/l, y:p.y+d*v.x/l};
  }
  function offsetPath(d){
    const out=[]; for(let i=0;i<=220;i++) out.push(offsetPoint(i/220,d)); return out;
  }
  // Euler target: normalized by the chord, then transformed onto P0-P3.
  function integEuler(k0,k1){
    const N=160, ds=1/N; let sx=0, sy=0;
    for(let i=0;i<=N;i++){
      const s=-0.5+i*ds;
      const w=(i===0||i===N)?1:(i%2?4:2);
      const th=k0*s+0.5*k1*s*s;
      sx+=w*Math.cos(th); sy+=w*Math.sin(th);
    }
    return {u:sx*ds/3, v:sy*ds/3};
  }
  function fitEuler(th0,th1){
    let k1old=0;
    const dth=th1-th0, k0=th0+th1;
    let k1=(6-dth*dth/70-0.1*k0*k0)*dth;
    let errorOld=dth;
    for(let it=0;it<12;it++){
      const iv=integEuler(k0,k1);
      const chth=Math.atan2(iv.v,iv.u);
      const error=dth-(0.25*k1-2*chth);
      if(!Number.isFinite(error)) return null;
      if(Math.abs(error)<1e-9){
        const chord=Math.hypot(iv.u,iv.v);
        if(!Number.isFinite(chord)||chord<1e-9) return null;
        return {k0,k1,chord,chth};
      }
      const newK1=k1+(k1old-k1)*error/(error-errorOld);
      k1old=k1; errorOld=error; k1=newK1;
      if(!Number.isFinite(k1)||Math.abs(k1)>200) return null;
    }
    return null;
  }
  function eulerNorm(fit,t){
    const u=t*0.5-0.5;
    const thm=(0.5*fit.k1*u+fit.k0)*u-fit.chth;
    const iv=integEuler((fit.k0+fit.k1*0.5*(t-1))*t, fit.k1*t*t);
    const s=t/fit.chord*Math.sin(thm), c=t/fit.chord*Math.cos(thm);
    return {x:iv.u*c-iv.v*s, y:-iv.v*c-iv.u*s};
  }
  function eulerTarget(){
    const {p1,p2}=handles();
    const d01={x:p1.x-P0.x,y:p1.y-P0.y};
    const d23={x:P3.x-p2.x,y:P3.y-p2.y};
    const d03={x:P3.x-P0.x,y:P3.y-P0.y};
    const cross=(a,b)=>a.x*b.y-a.y*b.x;
    const dot=(a,b)=>a.x*b.x+a.y*b.y;
    const th0=Math.atan2(cross(d03,d01),dot(d03,d01));
    const th1=Math.atan2(cross(d23,d03),dot(d23,d03));
    const fit=fitEuler(th0,th1);
    if(!fit) return {pts:null,th0,th1,fit:null};
    const f=frame(), pts=[];
    for(let i=0;i<=180;i++){
      const q=eulerNorm(fit,i/180);
      pts.push({x:P0.x+f.L*(q.x*f.e.x+q.y*f.n.x), y:P0.y+f.L*(q.x*f.e.y+q.y*f.n.y)});
    }
    return {pts,th0,th1,fit};
  }
  function parab(side){
    const pts=[];
    for(let i=0;i<=80;i++){
      const v=-2/3 + (4/3)*i/80;
      const u=side==='left' ? 1/3-0.75*v*v : 2/3+0.75*v*v;
      pts.push(local(u,v));
    }
    return pts;
  }
  function setPreset345(){
    freeHandles=false; H1=H2=null;
    document.getElementById('free-handles').checked=false;
    P0={x:6,y:1}; P3={x:12,y:9}; v0=-0.22; v1=0.22; draw();
  }
  function setPreset345Handles(){
    P0={x:0,y:0}; P3={x:8,y:6};
    H1={x:4,y:-1}; H2={x:4,y:8};
    freeHandles=true; document.getElementById('free-handles').checked=true;
    draw();
  }
  function setPresetS53(){
    P0={x:2,y:5}; P3={x:12,y:5};
    H1={x:5,y:1}; H2={x:9,y:9};
    freeHandles=true; document.getElementById('free-handles').checked=true;
    draw();
  }
  function snapHandles(){
    const h=handles();
    H1={x:Math.round(h.p1.x), y:Math.round(h.p1.y)};
    H2={x:Math.round(h.p2.x), y:Math.round(h.p2.y)};
    freeHandles=true; document.getElementById('free-handles').checked=true;
    draw();
  }
  function stateObject(){
    const h=handles(), f=frame(), ca=Math.atan2(f.e.y,f.e.x);
    const wrap=a=>Math.atan2(Math.sin(a),Math.cos(a));
    const t0=wrap(Math.atan2(h.p1.y-P0.y,h.p1.x-P0.x)-ca);
    const t1=wrap(Math.atan2(P3.y-h.p2.y,P3.x-h.p2.x)-ca);
    const loc=(p)=>({u:((p.x-P0.x)*f.e.x+(p.y-P0.y)*f.e.y)/f.L,
                     v:((p.x-P0.x)*f.n.x+(p.y-P0.y)*f.n.y)/f.L});
    const a=loc(h.p1), b=loc(h.p2);
    return {
      version: 1,
      mode: freeHandles ? 'free' : 'guide',
      p0: {...P0}, p3: {...P3},
      v0, v1,
      handles: {p1:{...h.p1}, p2:{...h.p2}},
      chord: f.L,
      endpoint_tangents_deg: [t0*180/Math.PI, t1*180/Math.PI],
      guide_residual: [
        Math.abs(a.u-(1/3-0.75*a.v*a.v))*f.L,
        Math.abs(b.u-(2/3+0.75*b.v*b.v))*f.L,
      ],
      offset_d: Number(document.getElementById('offset-d').value),
      show_parabolas: document.getElementById('show-parab').checked,
      show_offsets: document.getElementById('show-offset').checked,
      show_euler: document.getElementById('show-target').checked,
      snap_integers: document.getElementById('snap-int').checked,
    };
  }
  function applyState(o){
    if(!o || o.version !== 1) return false;
    P0={x:Number(o.p0.x),y:Number(o.p0.y)}; P3={x:Number(o.p3.x),y:Number(o.p3.y)};
    v0=Number(o.v0); v1=Number(o.v1);
    freeHandles=o.mode==='free';
    H1=o.handles && o.handles.p1 ? {x:Number(o.handles.p1.x),y:Number(o.handles.p1.y)} : null;
    H2=o.handles && o.handles.p2 ? {x:Number(o.handles.p2.x),y:Number(o.handles.p2.y)} : null;
    document.getElementById('free-handles').checked=freeHandles;
    document.getElementById('offset-d').value=String(o.offset_d ?? 0.55);
    document.getElementById('show-parab').checked=!!o.show_parabolas;
    document.getElementById('show-offset').checked=!!o.show_offsets;
    document.getElementById('show-target').checked=!!o.show_euler;
    document.getElementById('snap-int').checked=!!o.snap_integers;
    draw();
    return true;
  }
  function setStatus(text){ document.getElementById('save-status').textContent=text; }
  function saveState(){
    try{
      localStorage.setItem('curve-lab/euler-parabola-fit', JSON.stringify(stateObject()));
      setStatus('state saved locally');
    }catch(err){ setStatus('could not save state'); }
  }
  function restoreState(){
    try{
      const raw=localStorage.getItem('curve-lab/euler-parabola-fit');
      if(!raw){ setStatus('no saved state'); return; }
      setStatus(applyState(JSON.parse(raw))?'state restored':'saved state is invalid');
    }catch(err){ setStatus('could not restore state'); }
  }
  function saveJSON(){
    const blob=new Blob([JSON.stringify(stateObject(),null,2)],{type:'application/json'});
    const a=document.createElement('a'); a.href=URL.createObjectURL(blob);
    a.download='euler-parabola-state.json'; a.click();
    setTimeout(()=>URL.revokeObjectURL(a.href),1000);
    setStatus('JSON downloaded');
  }
  function draw(){
    ctx.clearRect(0,0,W,H);
    ctx.fillStyle='#fbf7ec'; ctx.fillRect(0,0,W,H);
    // fine quarter-unit grid under the integer grid
    ctx.lineWidth=1;
    ctx.strokeStyle='#f0e9da';
    for(let i=0;i<=80;i++){
      if(i%4===0) continue;
      const g=i*0.25;
      ctx.beginPath(); ctx.moveTo(SX(g),SY(0)); ctx.lineTo(SX(g),SY(18)); ctx.stroke();
      if(i<=72){
        ctx.beginPath(); ctx.moveTo(SX(0),SY(g)); ctx.lineTo(SX(20),SY(g)); ctx.stroke();
      }
    }
    ctx.strokeStyle='#e2d8c0';
    for(let i=0;i<=20;i++){
      ctx.beginPath(); ctx.moveTo(SX(i),SY(0)); ctx.lineTo(SX(i),SY(18)); ctx.stroke();
    }
    for(let i=0;i<=18;i++){
      ctx.beginPath(); ctx.moveTo(SX(0),SY(i)); ctx.lineTo(SX(20),SY(i)); ctx.stroke();
    }
    ctx.strokeStyle='#b9aa88'; ctx.strokeRect(SX(0),SY(18),SX(20)-SX(0),SY(0)-SY(18));
    // rulers just outside the grid
    ctx.save();
    ctx.strokeStyle='#b9aa88'; ctx.fillStyle='#7b6c4e';
    ctx.font='10px ui-monospace, Menlo, monospace';
    ctx.textAlign='center'; ctx.textBaseline='top';
    for(let i=0;i<=20;i++){
      const x=SX(i);
      ctx.beginPath(); ctx.moveTo(x,SY(0)); ctx.lineTo(x,SY(0)+4); ctx.stroke();
      ctx.fillText(String(i), x, SY(0)+7);
    }
    ctx.textAlign='right'; ctx.textBaseline='middle';
    for(let i=0;i<=18;i++){
      const y=SY(i);
      ctx.beginPath(); ctx.moveTo(SX(0)-4,y); ctx.lineTo(SX(0),y); ctx.stroke();
      ctx.fillText(String(i), SX(0)-7, y);
    }
    ctx.restore();
    // endpoint parabolas
    if(document.getElementById('show-parab').checked){
      for(const side of ['left','right']){
        const pts=parab(side);
        ctx.save(); ctx.beginPath();
        pts.forEach((p,i)=> i?ctx.lineTo(SX(p.x),SY(p.y)):ctx.moveTo(SX(p.x),SY(p.y)));
        ctx.strokeStyle='#3f7d4e'; ctx.lineWidth=1.2; ctx.setLineDash([4,4]); ctx.stroke(); ctx.restore();
      }
    }
    const {p1,p2}=handles();
    // control polygon
    ctx.save(); ctx.beginPath();
    [P0,p1,p2,P3].forEach((p,i)=> i?ctx.lineTo(SX(p.x),SY(p.y)):ctx.moveTo(SX(p.x),SY(p.y)));
    ctx.strokeStyle='#9b8b67'; ctx.lineWidth=1.1; ctx.setLineDash([4,4]); ctx.stroke(); ctx.restore();
    // dense normal offsets of the cubic
    if(document.getElementById('show-offset').checked){
      const d=Number(document.getElementById('offset-d').value);
      if(d>0){
        for(const sign of [1,-1]){
          const pts=offsetPath(sign*d);
          ctx.save(); ctx.beginPath();
          pts.forEach((p,i)=> i?ctx.lineTo(SX(p.x),SY(p.y)):ctx.moveTo(SX(p.x),SY(p.y)));
          ctx.strokeStyle=sign>0?'#1f5fa8':'#b23a2b'; ctx.lineWidth=1.3; ctx.stroke(); ctx.restore();
        }
      }
    }
    // true Euler target through the current ends/tangents; draw it after
    // the cubic so a close target remains visible.
    let target=null;
    if(document.getElementById('show-target').checked) target=eulerTarget();
    if(target && target.pts){
      ctx.save(); ctx.beginPath();
      target.pts.forEach((p,i)=> i?ctx.lineTo(SX(p.x),SY(p.y)):ctx.moveTo(SX(p.x),SY(p.y)));
      ctx.strokeStyle='#6b4c9a'; ctx.lineWidth=2.6; ctx.lineCap='round'; ctx.stroke(); ctx.restore();
    }
    // cubic
    ctx.beginPath();
    for(let i=0;i<=300;i++){const p=cubic(i/300); i?ctx.lineTo(SX(p.x),SY(p.y)):ctx.moveTo(SX(p.x),SY(p.y));}
    ctx.strokeStyle='#2e2413'; ctx.lineWidth=2.4; ctx.lineJoin='round'; ctx.setLineDash([5,4]); ctx.stroke(); ctx.setLineDash([]);
    // points
    for(const [name,p,square] of [['P0',P0,false],['P1',p1,true],['P2',p2,true],['P3',P3,false]]){
      const x=SX(p.x), y=SY(p.y);
      ctx.save(); ctx.strokeStyle='#2e2413'; ctx.lineWidth=1.4;
      if(square){ctx.fillStyle='#c9a441'; ctx.fillRect(x-5,y-5,10,10); ctx.strokeRect(x-5,y-5,10,10);}
      else{ctx.fillStyle='#fbf7ec'; ctx.beginPath(); ctx.arc(x,y,5.5,0,7); ctx.fill(); ctx.stroke();}
      ctx.fillStyle='#2e2413'; ctx.font='11px ui-monospace, Menlo, monospace';
      ctx.fillText(name,x+8,y-7); ctx.restore();
    }
    // labels
    ctx.fillStyle='#2e2413'; ctx.font='600 15px Georgia, serif';
    ctx.fillText('Fig. E1 · cubic with endpoint-parabola handles',16,24);
    ctx.font='10px ui-monospace, Menlo, monospace'; ctx.fillStyle='#7b6c4e';
    ctx.fillText('x →',W-34,H-12); ctx.fillText('y ↑',16,42);
    // 2pt swatches so the actual colours are visible.
    const legendY = 58;
    const items = [
      {kind:'line', color:'#2e2413', dash:[5,4], label:'cubic'},
      {kind:'line', color:'#7b6c4e', dash:[4,4], label:'control'},
      {kind:'line', color:'#3f7d4e', dash:[3,4], label:'parabolas'},
      {kind:'square', color:'#c9a441', label:'handles'},
      {kind:'line', color:'#1f5fa8', dash:[], label:'+d'},
      {kind:'line', color:'#b23a2b', dash:[], label:'−d'},
      {kind:'line', color:'#6b4c9a', dash:[], label:'Euler'},
    ];
    let lx = SX(0) + 8;
    ctx.textBaseline = 'middle';
    for (const item of items) {
      ctx.save();
      ctx.strokeStyle = item.color; ctx.fillStyle = item.color; ctx.lineWidth = 2;
      if (item.kind === 'line') {
        ctx.beginPath(); ctx.setLineDash(item.dash);
        ctx.moveTo(lx, legendY); ctx.lineTo(lx + 18, legendY); ctx.stroke();
        ctx.setLineDash([]);
      } else {
        ctx.fillRect(lx + 5, legendY - 3.5, 7, 7);
        ctx.strokeStyle = '#2e2413'; ctx.lineWidth = 1; ctx.strokeRect(lx + 5, legendY - 3.5, 7, 7);
      }
      ctx.restore();
      ctx.fillStyle = '#7b6c4e';
      ctx.fillText(item.label, lx + 23, legendY + 1);
      lx += 23 + ctx.measureText(item.label).width + 13;
    }
    ctx.textBaseline = 'alphabetic';
    const f=frame();
    const chordAngle=Math.atan2(P3.y-P0.y,P3.x-P0.x);
    const wrap=a=>Math.atan2(Math.sin(a),Math.cos(a));
    const t0=wrap(Math.atan2(p1.y-P0.y,p1.x-P0.x)-chordAngle);
    const t1=wrap(Math.atan2(P3.y-p2.y,P3.x-p2.x)-chordAngle);
    const maxAngle=Math.max(Math.abs(t0),Math.abs(t1))*180/Math.PI;
    const sameSign=t0*t1>0;
    const shape=sameSign?'S':'C';
    const comfortLimit=sameSign?45:90;
    const comfort=maxAngle>comfortLimit;
    document.getElementById('readout').textContent =
      `chord = ${f.L.toFixed(3)}   Δ = (${(P3.x-P0.x).toFixed(1)}, ${(P3.y-P0.y).toFixed(1)})   v0 = ${v0.toFixed(3)}   v1 = ${v1.toFixed(3)}\n`+
      `P1 = (${p1.x.toFixed(3)}, ${p1.y.toFixed(3)})   P2 = (${p2.x.toFixed(3)}, ${p2.y.toFixed(3)})   d = ${Number(document.getElementById('offset-d').value).toFixed(2)}\n`+
      `endpoint tangents: ${(t0*180/Math.PI).toFixed(1)}° / ${(t1*180/Math.PI).toFixed(1)}°   ${shape}-shape single-span limit ≈ ${comfortLimit}°`+
      (comfort?'   ⚠ split at the inflection / add spans':'')+
      (target && target.pts ? '   · Euler target shown' : '   · Euler target unavailable at these ends')+
      (freeHandles?'\nfree handles: guide-constrained construction is off; parabola residual is shown below':'\nhandles are on the endpoint parabolas');
    if(freeHandles){
      const {e,n}=f; const loc=(p)=>({u:((p.x-P0.x)*e.x+(p.y-P0.y)*e.y)/f.L, v:((p.x-P0.x)*n.x+(p.y-P0.y)*n.y)/f.L});
      const a=loc(H1), b=loc(H2);
      const r0=Math.abs(a.u-(1/3-0.75*a.v*a.v))*f.L;
      const r1=Math.abs(b.u-(2/3+0.75*b.v*b.v))*f.L;
      document.getElementById('readout').textContent += `\nP1 guide residual = ${r0.toFixed(4)}   P2 guide residual = ${r1.toFixed(4)}`;
    }
  }
  function toWorld(ev){
    const r=canvas.getBoundingClientRect();
    const sx=(ev.clientX-r.left)*W/r.width, sy=(ev.clientY-r.top)*H/r.height;
    return {x:(sx-ox)/scale+DOM.x0, y:(H-oy-sy)/scale+DOM.y0};
  }
  function nearest(ev){
    const w=toWorld(ev); const {p1,p2}=handles();
    let best=null,bd=18;
    for(const [k,p] of [['p0',P0],['p1',p1],['p2',p2],['p3',P3]]){
      const d=Math.hypot(SX(p.x)-SX(w.x), SY(p.y)-SY(w.y));
      if(d<bd){bd=d;best=k;}
    }
    return best;
  }
  canvas.addEventListener('pointerdown',ev=>{
    const k=nearest(ev); if(!k)return; drag=k; canvas.setPointerCapture(ev.pointerId); ev.preventDefault();
  });
  canvas.addEventListener('pointermove',ev=>{
    if(!drag){canvas.style.cursor=nearest(ev)?'grab':'crosshair';return;}
    const w=toWorld(ev);
    if(drag==='p0'||drag==='p3'){
      const p=drag==='p0'?P0:P3;
      p.x=clamp(w.x,0.35,19.65); p.y=clamp(w.y,0.35,17.65);
      if(document.getElementById('snap-int').checked){
        p.x=Math.round(p.x); p.y=Math.round(p.y);
        p.x=clamp(p.x,1,19); p.y=clamp(p.y,1,17);
      }
      if(Math.hypot(P3.x-P0.x,P3.y-P0.y)<0.2){ // avoid collapsed frame
        if(drag==='p0'){P0.x=P3.x-0.2;} else {P3.x=P0.x+0.2;}
      }
    } else if(freeHandles){
      const p=drag==='p1'?H1:H2;
      p.x=clamp(w.x,0.35,19.65); p.y=clamp(w.y,0.35,17.65);
      if(document.getElementById('snap-int').checked){
        p.x=Math.round(p.x); p.y=Math.round(p.y);
      }
    } else {
      const {L,e,n}=frame();
      const dx=w.x-P0.x, dy=w.y-P0.y;
      const v=(dx*n.x+dy*n.y)/L;
      if(drag==='p1') v0=clamp(v,-2/3,2/3); else v1=clamp(v,-2/3,2/3);
    }
    draw();
  });
  canvas.addEventListener('pointerup',ev=>{drag=null;try{canvas.releasePointerCapture(ev.pointerId);}catch(_){}});
  canvas.addEventListener('pointercancel',()=>{drag=null;});
  document.getElementById('show-parab').addEventListener('change',draw);
  document.getElementById('show-offset').addEventListener('change',draw);
  document.getElementById('show-target').addEventListener('change',draw);
  document.getElementById('offset-d').addEventListener('input',draw);
  document.getElementById('preset-345').addEventListener('click',setPreset345);
  document.getElementById('preset-345-handles').addEventListener('click',setPreset345Handles);
  document.getElementById('preset-s53').addEventListener('click',setPresetS53);
  document.getElementById('snap-handles').addEventListener('click',snapHandles);
  document.getElementById('save-state').addEventListener('click',saveState);
  document.getElementById('restore-state').addEventListener('click',restoreState);
  document.getElementById('save-json').addEventListener('click',saveJSON);
  document.getElementById('free-handles').addEventListener('change',ev=>{
    if(ev.target.checked){
      const h=handles(); H1={...h.p1}; H2={...h.p2}; freeHandles=true;
    } else { freeHandles=false; }
    draw();
  });
  document.getElementById('reset').addEventListener('click',()=>{
    P0={...START.p0}; P3={...START.p3}; v0=START.v0; v1=START.v1;
    freeHandles=false; H1=H2=null; document.getElementById('free-handles').checked=false; draw();
  });
  const RECORDS = __EULER_RECORDS__;
  const CANVAS_W = 1000, CANVAS_H = 360, CPAD = 38;
  const X0 = -0.06, X1 = 1.06, Y0 = -0.23, Y1 = 0.23;
  const CSCALE = Math.min((CANVAS_W - 2*CPAD)/(X1-X0),
                          (CANVAS_H - 2*CPAD)/(Y1-Y0));
  const COX = (CANVAS_W - (X1-X0)*CSCALE)/2;
  const COY = (CANVAS_H - (Y1-Y0)*CSCALE)/2;
  const CSX = x => COX + (x-X0)*CSCALE;
  const CSY = y => CANVAS_H - COY - (y-Y0)*CSCALE;

  function drawSmooth(prefix, mode){
    const canvas=document.getElementById(prefix+'-canvas');
    const ctx=canvas.getContext('2d');
    const dpr=window.devicePixelRatio||1;
    canvas.width=CANVAS_W*dpr; canvas.height=CANVAS_H*dpr;
    ctx.setTransform(dpr,0,0,dpr,0,0);
    const slider=document.getElementById(prefix+'-angle');
    const rec=RECORDS[Number(slider.value)];
    document.getElementById(prefix+'-angle-value').textContent=rec.a.toFixed(2)+'°';
    ctx.clearRect(0,0,CANVAS_W,CANVAS_H);
    ctx.fillStyle='#fbf7ec'; ctx.fillRect(0,0,CANVAS_W,CANVAS_H);
    ctx.strokeStyle='#e4dcc6'; ctx.lineWidth=1;
    for(const x of [0,0.25,0.5,0.75,1]){
      ctx.beginPath(); ctx.moveTo(CSX(x),CSY(Y0)); ctx.lineTo(CSX(x),CSY(Y1)); ctx.stroke();
    }
    for(const y of [-0.2,0,0.2]){
      ctx.beginPath(); ctx.moveTo(CSX(X0),CSY(y)); ctx.lineTo(CSX(X1),CSY(y)); ctx.stroke();
    }
    ctx.strokeStyle='#b9aa88'; ctx.strokeRect(CSX(X0),CSY(Y1),CSX(X1)-CSX(X0),CSY(Y0)-CSY(Y1));
    // true curve
    ctx.beginPath();
    rec.true.forEach((p,i)=> i?ctx.lineTo(CSX(p[0]),CSY(p[1])):ctx.moveTo(CSX(p[0]),CSY(p[1])));
    ctx.strokeStyle='#2e2413'; ctx.lineWidth=2.2; ctx.stroke();
    // fit pieces
    const colours= mode==='one' ? ['#c9a441'] : ['#c9a441','#1f5fa8'];
    rec[mode].forEach((sp,piece)=>{
      const colour=colours[piece%colours.length];
      const pts=[];
      for(let i=0;i<=40;i++){
        const t=i/40,u=1-t;
        pts.push([u*u*u*sp.p0[0]+3*u*u*t*sp.c1[0]+3*u*t*t*sp.c2[0]+t*t*t*sp.p3[0],
                  u*u*u*sp.p0[1]+3*u*u*t*sp.c1[1]+3*u*t*t*sp.c2[1]+t*t*t*sp.p3[1]]);
      }
      ctx.beginPath(); pts.forEach((p,i)=> i?ctx.lineTo(CSX(p[0]),CSY(p[1])):ctx.moveTo(CSX(p[0]),CSY(p[1])));
      ctx.strokeStyle=colour; ctx.lineWidth=1.6; ctx.setLineDash([5,4]); ctx.stroke(); ctx.setLineDash([]);
      // control polygon
      ctx.beginPath();
      [sp.p0,sp.c1,sp.c2,sp.p3].forEach((p,i)=> i?ctx.lineTo(CSX(p[0]),CSY(p[1])):ctx.moveTo(CSX(p[0]),CSY(p[1])));
      ctx.strokeStyle='#7b6c4e'; ctx.lineWidth=1; ctx.setLineDash([4,4]); ctx.stroke(); ctx.setLineDash([]);
      for(const [q,tag] of [[sp.c1,'c'+(2*piece+1)],[sp.c2,'c'+(2*piece+2)]]){
        const x=CSX(q[0]),y=CSY(q[1]);
        ctx.fillStyle='#c9a441'; ctx.strokeStyle='#2e2413'; ctx.lineWidth=1;
        ctx.fillRect(x-3,y-3,6,6); ctx.strokeRect(x-3,y-3,6,6);
        ctx.fillStyle='#7b6c4e'; ctx.font='8px ui-monospace,Menlo,monospace';
        ctx.fillText(tag,x+4,y-4);
      }
    });
    ctx.fillStyle='#2e2413'; ctx.font='600 14px Georgia, serif';
    ctx.fillText(`Fig. ${prefix==='e4'?'E4':'E5'} · S ${rec.a.toFixed(2)}° · ${mode==='one'?'one piece':'two pieces'}`,12,18);
    ctx.font='9px ui-monospace,Menlo,monospace'; ctx.fillStyle='#7b6c4e';
    ctx.fillText('— true Euler   --- fit   -- control',12,32);
    ctx.fillText('x →',CANVAS_W-28,CANVAS_H-9); ctx.fillText('y ↑',12,CANVAS_H-9);
    document.getElementById(prefix+'-meta').textContent =
      `θ=${rec.a.toFixed(3)}° · sampled one-piece error ${rec.e1.toFixed(5)} · two-piece ${rec.e2.toFixed(5)}`;
  }

  const PYTH = __PYTH_DATA__;
  const PYTH_W = 1000, PYTH_H = 380, PPAD = 42;
  function drawPyth(index){
    const canvas=document.getElementById('pyth-canvas');
    const ctx=canvas.getContext('2d');
    const dpr=window.devicePixelRatio||1;
    canvas.width=PYTH_W*dpr; canvas.height=PYTH_H*dpr;
    ctx.setTransform(dpr,0,0,dpr,0,0);
    const c=PYTH[index];
    const pts=[c.p0,c.p1,c.p2,c.p3];
    const xs=pts.map(p=>p[0]), ys=pts.map(p=>p[1]);
    const x0=Math.min(...xs), x1=Math.max(...xs);
    const y0=Math.min(...ys), y1=Math.max(...ys);
    const dx=x1-x0||1, dy=y1-y0||1, pad=.12;
    const xa=x0-pad*dx, xb=x1+pad*dx, ya=y0-pad*dy, yb=y1+pad*dy;
    const k=Math.min((PYTH_W-2*PPAD)/(xb-xa),(PYTH_H-2*PPAD)/(yb-ya));
    const ox=(PYTH_W-(xb-xa)*k)/2, oy=(PYTH_H-(yb-ya)*k)/2;
    const px=x=>ox+(x-xa)*k, py=y=>PYTH_H-oy-(y-ya)*k;
    ctx.clearRect(0,0,PYTH_W,PYTH_H);
    ctx.fillStyle='#fbf7ec'; ctx.fillRect(0,0,PYTH_W,PYTH_H);
    // light integer grid, decimated for large triples
    const step=Math.max(1,Math.ceil(Math.max(dx,dy)/24));
    ctx.strokeStyle='#e4dcc6'; ctx.lineWidth=1;
    for(let gx=Math.ceil(xa/step)*step;gx<=xb;gx+=step){
      ctx.beginPath(); ctx.moveTo(px(gx),py(ya)); ctx.lineTo(px(gx),py(yb)); ctx.stroke();
    }
    for(let gy=Math.ceil(ya/step)*step;gy<=yb;gy+=step){
      ctx.beginPath(); ctx.moveTo(px(xa),py(gy)); ctx.lineTo(px(xb),py(gy)); ctx.stroke();
    }
    ctx.strokeStyle='#b9aa88'; ctx.strokeRect(px(xa),py(yb),px(xb)-px(xa),py(ya)-py(yb));
    // control polygon
    ctx.beginPath(); pts.forEach((p,i)=>i?ctx.lineTo(px(p[0]),py(p[1])):ctx.moveTo(px(p[0]),py(p[1])));
    ctx.strokeStyle='#7b6c4e'; ctx.lineWidth=1; ctx.setLineDash([4,4]); ctx.stroke(); ctx.setLineDash([]);
    // cubic
    ctx.beginPath();
    for(let i=0;i<=120;i++){
      const t=i/120,u=1-t;
      const x=u*u*u*c.p0[0]+3*u*u*t*c.p1[0]+3*u*t*t*c.p2[0]+t*t*t*c.p3[0];
      const y=u*u*u*c.p0[1]+3*u*u*t*c.p1[1]+3*u*t*t*c.p2[1]+t*t*t*c.p3[1];
      i?ctx.lineTo(px(x),py(y)):ctx.moveTo(px(x),py(y));
    }
    ctx.strokeStyle='#2e2413'; ctx.lineWidth=2.4; ctx.stroke();
    for(const [name,p] of [['P0',c.p0],['P1',c.p1],['P2',c.p2],['P3',c.p3]]){
      const x=px(p[0]),y=py(p[1]);
      ctx.fillStyle=name==='P1'||name==='P2'?'#c9a441':'#fbf7ec';
      ctx.strokeStyle='#2e2413'; ctx.lineWidth=1.2;
      if(name==='P1'||name==='P2'){ctx.fillRect(x-4,y-4,8,8);ctx.strokeRect(x-4,y-4,8,8);}
      else{ctx.beginPath();ctx.arc(x,y,4.5,0,7);ctx.fill();ctx.stroke();}
      ctx.fillStyle='#2e2413'; ctx.font='10px ui-monospace,Menlo,monospace';
      ctx.fillText(`${name} (${p[0]}, ${p[1]})`,x+6,y-6);
    }
    ctx.fillStyle='#2e2413'; ctx.font='600 14px Georgia,serif';
    ctx.fillText(`Fig. P1 · ${c.label} · integer S cubic`,12,20);
    ctx.font='9px ui-monospace,Menlo,monospace'; ctx.fillStyle='#7b6c4e';
    ctx.fillText(`chord ${2*c.c} · arm ${c.c} · tangent ${c.angle.toFixed(2)}°`,12,35);
    document.getElementById('pyth-meta').textContent =
      `${c.label} · P1=(${c.p1[0]}, ${c.p1[1]}) · P2=(${c.p2[0]}, ${c.p2[1]}) · chord ${2*c.c} · tangent ${c.angle.toFixed(3)}°`;
  }
  function wirePyth(){
    const buttons=document.getElementById('pyth-buttons');
    buttons.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>drawPyth(Number(b.dataset.index))));
    drawPyth(0);
  }

  function wireSmooth(prefix, mode){
    const slider=document.getElementById(prefix+'-angle');
    const buttons=document.getElementById(prefix+'-buttons');
    function show(){drawSmooth(prefix,mode);}
    slider.addEventListener('input',show);
    buttons.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{
      const target=Number(b.dataset.angle);
      let best=0;
      for(let i=0;i<RECORDS.length;i++) if(Math.abs(RECORDS[i].a-target)<Math.abs(RECORDS[best].a-target)) best=i;
      slider.value=String(best); show();
    }));
    show();
  }
  wireSmooth('e4','one'); wireSmooth('e5','two');
  wirePyth();
  draw();
})();
</script>
</body>
</html>"""

    page = (template
            .replace("__SYM_SVG__", sym_svg)
            .replace("__SYM_TABLE__", sym_table)
            .replace("__ASYM_SVG__", asym_svg)
            .replace("__ASYM_TABLE__", asym_table)
            .replace("__S48_TABLE__", s48_table)
            .replace("__E4_BUTTONS__", button_html)
            .replace("__E5_BUTTONS__", button_html)
            .replace("__MAX__", str(len(records)-1))
            .replace("__DEFAULT__", str(default_index))
            .replace("__EULER_RECORDS__", records_json)
            .replace("__PYTH_BUTTONS__", pyth_buttons)
            .replace("__PYTH_DATA__", pyth_json)
            .replace("__PYTH_TABLE__", pyth_table))
    out = ROOT / "workbench" / "euler-parabola-fit.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    for kind, data in studies.items():
        slopes = []
        for a, b in zip(data["rows"][2:], data["rows"][3:]):
            if a["error"] > 0 and b["error"] > 0:
                slopes.append(math.log(a["error"] / b["error"]) / math.log(2))
        print(f"  {kind}: slope n=4..16 {sum(slopes) / len(slopes):.2f}")


if __name__ == "__main__":
    main()
