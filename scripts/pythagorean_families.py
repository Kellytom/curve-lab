"""Plot Pythagorean triples, scaling rays, and fixed-n parabolas.

    .venv/bin/python scripts/pythagorean_families.py

Writes `workbench/pythagorean-families.html`.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import pyth_triples  # noqa: E402

LIMIT = 3500
N_FAMILIES = (1, 2, 3)
CHAIN_N = 2
CHAIN_ANGLE_MAX = 44.0
CHAIN_ANGLE_MIN = 4.0


def svg(points, all_n, all_m, families, chain, rays, w=1000, h=1000):
    n_max = int(LIMIT ** 0.5)
    pad = 62
    scale = (w - 2 * pad) / LIMIT
    ox = oy = pad

    def put(p):
        return ox + p[0] * scale, h - oy - p[1] * scale

    body = []
    for gx in range(0, LIMIT + 1, 500):
        a, b = put((gx, 0)), put((gx, LIMIT))
        body.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#e4dcc6"/>')
        body.append(f'<text x="{a[0]-10:.1f}" y="{h-pad+20}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#7b6c4e">{gx}</text>')
    for gy in range(0, LIMIT + 1, 500):
        a, b = put((0, gy)), put((LIMIT, gy))
        body.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#e4dcc6"/>')
        body.append(f'<text x="{pad-30}" y="{b[1]+4:.1f}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#7b6c4e">{gy}</text>')
    # scaling rays
    for a, b, p in rays:
        q0, q1 = put(a), put(b)
        body.append(f'<line x1="{q0[0]:.1f}" y1="{q0[1]:.1f}" x2="{q1[0]:.1f}" y2="{q1[1]:.1f}" stroke="#b9aa88" stroke-width=".8" stroke-dasharray="2 6"/>')
    # all triples
    for p in points:
        q = put((p["a"], p["b"]))
        body.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="1.35" fill="#8c8a78"/>')
    def curve_path(curve, colour, width, opacity):
        if len(curve) < 2:
            return
        d = " ".join(f"{put(point)[0]:.1f} {put(point)[1]:.1f}" for point in curve)
        body.append(f'<path d="M {d}" fill="none" stroke="{colour}" stroke-width="{width}" opacity="{opacity}"/>')

    # every fixed-Euclid-n and fixed-Euclid-m family inside the plot bound
    for n, curve in all_n.items():
        curve_path(curve, "#3f7d4e", .9, .32)
    for m, curve in all_m.items():
        curve_path(curve, "#c9a441", .9, .26)

    # the 800 band: fixed n=20
    if 20 in all_n:
        curve_path(all_n[20], "#145a32", 2.6, .98)
        for p in pyth_triples.family(20, LIMIT):
            q = put((p["a"], p["b"]))
            body.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="3.2" fill="#145a32" stroke="#fbf7ec" stroke-width=".7"/>')
        q = put((0, 800))
        body.append(f'<text x="{q[0]+6:.1f}" y="{q[1]-8:.1f}" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="#145a32" stroke="#fbf7ec" stroke-width="3" paint-order="stroke">n=20 · 800</text>')

    # fixed-n families as curves and marked points
    colours = {1: "#3f7d4e", 2: "#c9a441", 3: "#1f5fa8"}
    for n, family in families.items():
        if not family:
            continue
        d = " ".join(f"{put((p['a'], p['b']))[0]:.1f} {put((p['a'], p['b']))[1]:.1f}" for p in family)
        body.append(f'<path d="M {d}" fill="none" stroke="{colours[n]}" stroke-width="1.6" opacity=".9"/>')
        for p in family:
            q = put((p['a'], p['b']))
            body.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="2.1" fill="{colours[n]}" stroke="#fbf7ec" stroke-width=".5"/>')
    # Fässler fixed-N parabolas near the dense 1450 cluster
    for N in (1440, 1444, 1445, 1452, 1458):
        curve = pyth_triples.fassler_curve(N, LIMIT, samples=160)
        d = " ".join(
            f"{put(point)[0]:.1f} {put(point)[1]:.1f}"
            for point in curve if point[1] <= LIMIT
        )
        if d:
            body.append(f'<path d="M {d}" fill="none" stroke="#a23b2a" stroke-width="1" opacity=".55" stroke-dasharray="5 5"/>')
    # selected n=2 chain
    for p in chain:
        q = put((p["a"], p["b"]))
        body.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="4" fill="#c9a441" stroke="#2e2413" stroke-width=".8"/>')
    if chain:
        # mark the endpoints of the angle sweep
        for p, label, dx, dy in (
            (chain[0], f"m={chain[0]['m']} · {pyth_triples.angle_deg(chain[0]):.1f}°", 8, -8),
            (chain[-1], f"m={chain[-1]['m']} · {pyth_triples.angle_deg(chain[-1]):.1f}°", 8, -8),
        ):
            q = put((p["a"], p["b"]))
            body.append(f'<text x="{q[0]+dx:.1f}" y="{q[1]+dy:.1f}" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="#2e2413" stroke="#fbf7ec" stroke-width="3" paint-order="stroke">{label}</text>')
    body.append('<text x="12" y="20" font-family="Georgia,serif" font-size="15" font-weight="600" fill="#2e2413">Fig. T1 · Pythagorean triples, rays and families</text>')
    body.append(f'<text x="12" y="36" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#7b6c4e">all triples c≤{LIMIT} · Euclid n=1..{n_max} · Euclid m=2..{n_max} · selected n=2: {len(chain)} points from {pyth_triples.angle_deg(chain[0]):.2f}° down to {pyth_triples.angle_deg(chain[-1]):.2f}°</text>')
    body.append('<text x="12" y="52" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="#7b6c4e">· triple   --- ray   — Euclid n   — Euclid m   — Fässler N≈1450   ● selected n=2</text>')
    body.append(f'<text x="12" y="{h-8}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#7b6c4e">a →</text>')
    body.append(f'<text x="{w-38}" y="{h-8}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#7b6c4e">b ↑</text>')
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{w}" height="{h}" fill="#fbf7ec" stroke="#d8ccae"/>'
            + "".join(body) + "</svg>")


def main():
    points = pyth_triples.base_triples(LIMIT)
    families = {n: pyth_triples.family(n, LIMIT) for n in N_FAMILIES}
    n_max = int(LIMIT ** 0.5)
    all_n = {n: pyth_triples.euclid_n_curve(n, LIMIT)
             for n in range(1, n_max + 1)}
    all_m = {m: pyth_triples.euclid_m_curve(m, LIMIT)
             for m in range(2, n_max + 1)}
    chain = pyth_triples.selected_chain(
        CHAIN_N, LIMIT, CHAIN_ANGLE_MAX, CHAIN_ANGLE_MIN)
    rays = pyth_triples.rays(points, LIMIT, count=12)
    drawing = svg(points, all_n, all_m, families, chain, rays)

    picks = (5, 6, 8, 10, 15, 20, 25, 30, 40, 50, 57)
    n20 = pyth_triples.family(20, LIMIT)
    n20_rows = "".join(
        f'<tr><td>{p["m"]}</td><td>({p["a"]}, {p["b"]}, {p["c"]})</td>'
        f'<td>{pyth_triples.angle_deg(p):.2f}°</td></tr>'
        for p in n20[:6]
    ) + "".join(
        f'<tr><td>{p["m"]}</td><td>({p["a"]}, {p["b"]}, {p["c"]})</td>'
        f'<td>{pyth_triples.angle_deg(p):.2f}°</td></tr>'
        for p in n20[-2:]
    )
    rows = []
    for m in picks:
        p = next((p for p in chain if p["m"] == m), None)
        if p is None:
            continue
        rows.append(
            f'<tr><td>{p["m"]}</td><td>({p["a"]}, {p["b"]}, {p["c"]})</td>'
            f'<td>{pyth_triples.angle_deg(p):.2f}°</td>'
            f'<td>{p["b"] / p["a"]:.4f}</td></tr>')
    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pythagorean families</title>
<style>
:root{{--paper:#fbf7ec;--ink:#2e2413;--muted:#7b6c4e;--rule:#d8ccae;--gold:#c9a441}}
*{{box-sizing:border-box}}
body{{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}}
main{{max-width:1280px;margin:0 auto;padding:34px 22px 70px}}
.eyebrow{{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
h1{{font-size:32px;line-height:1.1;margin:0 0 7px}}
h2{{font-size:21px;margin:0 0 9px}}
.lede{{max-width:900px;color:var(--muted);margin:0 0 20px}}
.panel{{background:var(--paper);border:1px solid var(--rule);padding:17px 19px;margin:0 0 18px}}
.figure{{margin:0;background:var(--paper);border:1px solid var(--rule);padding:10px}}
.figure svg{{display:block;width:100%;height:auto}}
table{{border-collapse:collapse;width:100%;font:11px/1.5 ui-monospace,Menlo,monospace;margin:10px 0}}
th,td{{border:1px solid var(--rule);padding:5px 7px;text-align:right}}
th{{color:var(--muted);font-weight:400}}
.legend{{font:15px/1.65 ui-monospace,Menlo,monospace;color:var(--ink)}}
.legend td{{padding:5px 8px;text-align:left}}
.sw{{font-weight:700}}
code{{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}}
.small{{font:12px/1.55 ui-monospace,Menlo,monospace;color:var(--muted)}}
</style>
</head>
<body>
<main>
<p class="eyebrow">curve-lab · Pythagorean field</p>
<h1>Pythagorean triples, rays and parabolas</h1>
<p class="lede">This is the field of triples, not a hand-picked list. Multiples of a primitive triple lie on rays from the origin. For a fixed Euclid <code>n</code>, varying <code>m</code> gives a parabola <code>a=(b/(2n))²−n²</code>; the <code>n=2</code> family passes through the 43.6° triple <code>(20,21,29)</code> and descends to the 4° region.</p>
<section class="panel">
  <h2>Fig. T1 · the field</h2>
  <div class="figure">{drawing}</div>
  <p class="small">Grey points are all triples with <code>c≤{LIMIT}</code>, including multiples. Dashed lines are scaling rays. Thin green and gold curves are all fixed-Euclid-<code>n</code> and fixed-Euclid-<code>m</code> families inside the bound; the dark green/gold/blue curves are the selected <code>n=1,2,3</code> families. Thin rust dashed curves are the Fässler <code>N≈1450</code> cluster. Larger gold dots are the selected <code>n=2</code> sweep.</p>
</section>
<section class="panel">
  <h2>Legend and family names</h2>
  <table class="legend">
    <tr><td><span class="sw" style="color:#8c8a78">·</span></td><td><strong>triple</strong></td><td>one Pythagorean triple `(a,b,c)`, including multiples.</td></tr>
    <tr><td><span class="sw" style="color:#b9aa88">---</span></td><td><strong>ray</strong></td><td>multiples of a primitive triple; same angle from the origin.</td></tr>
    <tr><td><span class="sw" style="color:#3f7d4e">—</span></td><td><strong>Euclid n</strong></td><td>fixed <code>n</code>: <code>a=(b/(2n))²−n²</code>; right-opening; crosses the b-axis at <code>2n²</code>. Example: <code>n=20</code> crosses at 800.</td></tr>
    <tr><td><span class="sw" style="color:#c9a441">—</span></td><td><strong>Euclid m</strong></td><td>fixed <code>m</code>: <code>b=m²−a²/(4m²)</code>; <strong>downward-opening</strong>; crosses the b-axis at <code>m²</code>. Example: <code>m=20</code> crosses at 400.</td></tr>
    <tr><td><span class="sw" style="color:#a23b2a">---</span></td><td><strong>Fässler N≈1450</strong></td><td>fixed <code>N=(b+c)/2</code>: <code>b=|N−a²/(4N)|</code>; reflected at the a-axis; crosses the b-axis at <code>N</code>; the 1450 cluster is the near-coincident band.</td></tr>
    <tr><td><span class="sw" style="color:#1f5fa8">●</span></td><td><strong>selected n=2</strong></td><td>the 43.60°→4.02° sweep, not the 800 band.</td></tr>
  </table>
</section>
<section class="panel">
  <h2>The n=2 sweep</h2>
  <p>The selected sequence starts at <code>(20,21,29)</code> at <strong>43.60°</strong> and continues down the same parabola to <strong>4.02°</strong> at <code>(3245,228,3253)</code>. The exact triples are irregular along the curve; that is the point.</p>
  <table>
    <tr><th>m</th><th>triple</th><th>angle</th><th>b/a</th></tr>
    {''.join(rows)}
  </table>
</section>
<section class="panel">
  <h2>Parabola census</h2>
  <p>The y-axis crossings identify the family. The values around 400, 800, 1250, 1458 and 1922 are the fixed-Euclid-<code>n</code> curves, not the fixed-<code>m</code> ones:</p>
  <table>
    <tr><th>family</th><th>curve</th><th>crosses b-axis at</th><th>near the observed values</th></tr>
    <tr><td>fixed Euclid n</td><td><code>a=(b/(2n))²−n²</code></td><td><code>2n²</code></td><td><code>n=14→392</code>, <code>20→800</code>, <code>25→1250</code>, <code>27→1458</code>, <code>31→1922</code></td></tr>
    <tr><td>fixed Euclid m</td><td><code>b=m²−a²/(4m²)</code></td><td><code>m²</code></td><td><code>m=20→400</code>, <code>28→784</code>, <code>35→1225</code>, <code>39→1521</code>, <code>43→1849</code></td></tr>
    <tr><td>Fässler fixed N</td><td><code>b=|N−a²/(4N)|</code></td><td><code>N</code></td><td><code>1440, 1444, 1445, 1452, 1458</code></td></tr>
  </table>
  <p class="small">A parabola catalogue is infinite: each parameter value is a curve. The useful catalogue is by family and intercept law. The fixed-n family is the green fan; fixed m is the gold fan; Fässler's cluster is the rust band.</p>
  <p><strong>In a 500×500 box:</strong> the fixed-Euclid-<code>n</code> family has <code>n=1..15</code> because <code>2n²≤500</code>; the fixed-Euclid-<code>m</code> family has <code>m=1..22</code> because <code>m²≤500</code>. The roughly 22 downward curves are the gold fixed-<code>m</code> family; the right-opening green fixed-<code>n</code> family is the other set.</p>
</section>

<section class="panel">
  <h2>The 800 band: n=20</h2>
  <p>The fixed-<code>n=20</code> curve is the strong dark-green curve. Its y-axis intercept is <code>2n²=800</code>, but that intercept is the degenerate <code>m=n=20</code> point, not a triple. The first actual triple is <code>(41,840,841)</code>, at <strong>87.21°</strong>. The family runs to <code>(2625,2200,3425)</code> at about <strong>39.97°</strong>; it is a high-angle band, not the 44°→4° sweep.</p>
  <table>
    <tr><th>m</th><th>triple</th><th>angle</th></tr>
    {n20_rows}
  </table>
  <p>On this curve <code>b=40m</code>, so the points are evenly spaced vertically by 40. The horizontal gaps are <code>a</code> and <code>c</code> steps of <code>2m+1</code>: 43, 45, 47, … — regular in b, increasingly wide in a/c. That is the irregularity visible in the scatter.</p>
</section>

<section class="panel">
  <h2>Fässler's parabolas: a second slicing</h2>
  <p>There is a useful equivalent parameterization. Put <code>N=(b+c)/2</code> with the even leg as <code>a</code>. If <code>a²/(4N)</code> is an integer, then</p>
  <div class="formula">(a, |N − a²/(4N)|, N + a²/(4N))</div>
  <p>is a Pythagorean triple, and every triple can be written this way after possibly exchanging the legs. The triples therefore lie on</p>
  <div class="formula">b = |N − a²/(4N)|</div>
  <p>a parabola reflected in the a-axis. This <code>N</code> is <strong>not</strong> the same as Euclid's <code>n</code> above: the fixed-Euclid-n curves and the fixed-N curves are two different slicings of the same triple field. The plot above uses the Euclid slicing; both are valid.</p>
  <p>At <code>a=2N</code> the parabola meets the axis with derivative <code>−1</code>, so the reflection is at 45°. Swapping <code>a</code> and <code>b</code> gives the perpendicular family, and the axes therefore carry the crossing pattern described in the source.</p>
  <p>Holding Euclid <code>m</code> instead of <code>n</code> gives another family; with <code>a=2mn</code>, <code>b=m²−a²/(4m²)</code>. That is the other set of smooth parabolic slices visible in the scatter.</p>
  <p>Near <code>N≈1450</code> several values are close together: <code>38²=1444</code>, <code>2·27²=1458</code>, <code>3·22²=1452</code>, <code>5·17²=1445</code>, and <code>10·12²=1440</code>. Their parabolas nearly coincide, which is why a dense parabolic strip appears in the scatter.</p>
  <p class="small">Source: <a href="https://en.wikipedia.org/wiki/Pythagorean_triple">Wikipedia, “Pythagorean triple”</a>, distribution section; the references there point to Albert Fässler and conformal-mapping treatments.</p>
</section>

<section class="panel">
  <h2>From triangles to curves</h2>
  <p>The n=2 sweep gives 53 exact integer arm vectors. The first assembly rule is a <strong>triple tangent chain</strong>: use each triple as the endpoint tangent of a cubic, step along a large grid, and make every join by repeating the shared triple. That makes the chain <strong>C1 by construction</strong>; the curvature will generally jump.</p>
  <p>With a step of <code>100000</code>, the x extent is <code>5,200,000</code> and every control point is an integer; a smaller step needs the triple vectors normalised first, which introduces a common denominator and an even larger grid. The other candidate is a <strong>triangle strip</strong>: share triangle vertices and smooth the resulting polyline afterward. The tangent chain is the cleaner first probe because the joins are exact.</p>
  <p class="small">This is a prepared construction, not yet a rendered chain. The decision is in the TODO: tangent chain, triangle strip, or a G2 alternative.</p>
</section>

<section class="panel">
  <h2>Reading it as a curve sequence</h2>
  <p>The plot exposes candidate chains: choose a family/parabola, move along it, and use each triple as an arm vector or angle. The <code>n=2</code> sequence is the first candidate for a G2/G1 chain; it is a list of exact integer arm pairs, not a fitted approximation.</p>
  <p class="small">This page maps the triples; the next probe is to turn one family sequence into a chain and compare its G2/G1 joins. It does not claim the whole field is one curve.</p>
</section>
</main>
</body>
</html>
'''
    out = ROOT / "workbench" / "pythagorean-families.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    print(f"  {len(points)} triples, {len(chain)} selected n=2 points, {len(rays)} rays")


if __name__ == "__main__":
    main()
