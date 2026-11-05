"""Three grids in one design, and what they cost.

    .venv/bin/python scripts/multi_grid.py
    open workbench/multi-grid.html

A design does not need one grid. The stalk can sit on integers, the connector on
fifths, the flower on twenty-fifths - provided every join is a point that exists
in both grids, which is automatic when the grids form a chain of multiples. The
composite grid is the lcm of the parts, and the price of a chain of per-span
grids is the same explosion the spine pays.
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INK, GOLD, BLUE, RED, GREEN = "#2e2413", "#c9a441", "#1f5fa8", "#a23b2a", "#3f7d4e"
MUTED, RULE, PAPER = "#7b6c4e", "#d8ccae", "#fbf7ec"


def svg_design() -> str:
    # three parts laid left to right, each on its own grid
    W, H = 980, 520
    out = [f'<rect width="{W}" height="{H}" fill="{PAPER}"/>']
    panels = [(60, "stalk · grid 1"), (370, "connector · grid 1/5"), (680, "flower · grid 1/25")]
    widths = 240

    for (x0, label), step_px, colour in zip(panels, (24.0, 24.0 / 5, 24.0 / 25), (INK, BLUE, RED)):
        out.append(f'<text x="{x0}" y="40" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}">{label}</text>')
        # grid
        n = int(widths / step_px) + 1
        for i in range(n):
            x = x0 + i * step_px
            if x > x0 + widths:
                break
            out.append(f'<line x1="{x:.1f}" y1="70" x2="{x:.1f}" y2="380" stroke="{RULE}" stroke-width="0.8"/>')
        for j in range(14):
            y = 70 + j * 24
            out.append(f'<line x1="{x0}" y1="{y}" x2="{x0+widths}" y2="{y}" stroke="{RULE}" stroke-width="0.8"/>')

    # stalk: a stem of two straight runs on integer nodes
    stalk = [(60, 380), (60, 300), (140, 300), (140, 220), (220, 220)]
    out.append('<path d="' + " ".join(("M" if i == 0 else "L") + f"{x},{y}" for i, (x, y) in enumerate(stalk)) +
               f'" fill="none" stroke="{INK}" stroke-width="3"/>')
    # connector: an S on fifths
    out.append(f'<path d="M 370 380 C 420 380, 440 300, 490 300 S 560 220, 610 220" fill="none" stroke="{BLUE}" stroke-width="3"/>')
    # flower: a rosette on twenty-fifths
    cx, cy, r = 800, 300, 62
    petals = []
    for k in range(6):
        a = k * math.pi / 3
        petals.append(f'<circle cx="{cx + r*0.55*math.cos(a):.1f}" cy="{cy + r*0.55*math.sin(a):.1f}" r="{r*0.45:.1f}" fill="none" stroke="{RED}" stroke-width="2"/>')
    out.append("".join(petals))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="8" fill="{GOLD}"/>')

    # seams
    for x, label in ((300, "seam 1"), (610, "seam 2")):
        out.append(f'<line x1="{x}" y1="60" x2="{x}" y2="390" stroke="{GOLD}" stroke-width="1.2" stroke-dasharray="5 4"/>')
        out.append(f'<text x="{x+6}" y="405" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="{MUTED}">{label}</text>')
    out.append(f'<text x="60" y="440" font-family="Georgia,serif" font-size="13" fill="{INK}">Fig. G1 · stalk on 1, connector on 1/5, flower on 1/25 · composite grid 1/25 (25 cells per unit)</text>')
    out.append(f'<g font-family="Georgia,serif" font-size="15">'
               f'<line x1="60" y1="470" x2="96" y2="470" stroke="{INK}" stroke-width="3"/><text x="104" y="475" fill="{INK}">integer grid</text>'
               f'<line x1="250" y1="470" x2="286" y2="470" stroke="{BLUE}" stroke-width="3"/><text x="294" y="475" fill="{INK}">fifths</text>'
               f'<line x1="390" y1="470" x2="426" y2="470" stroke="{RED}" stroke-width="3"/><text x="434" y="475" fill="{INK}">twenty-fifths</text>'
               f'<line x1="620" y1="470" x2="656" y2="470" stroke="{GOLD}" stroke-width="2" stroke-dasharray="5 4"/><text x="664" y="475" fill="{INK}">declared seam</text>'
               f'</g>')
    return "\n".join(out)


def svg_cost() -> str:
    # grid lines per span for a 6-span spine: 5, 25, ..., 15625
    W, H = 980, 360
    out = [f'<rect width="{W}" height="{H}" fill="{PAPER}"/>']
    gx, gy, gw, gh = 90, 70, 800, 220
    values = [5 ** k for k in range(1, 7)]
    logs = [math.log10(v) for v in values]
    top = max(logs) * 1.15
    out.append(f'<line x1="{gx}" y1="{gy+gh}" x2="{gx+gw}" y2="{gy+gh}" stroke="{INK}" stroke-width="1.2"/>')
    out.append(f'<line x1="{gx}" y1="{gy}" x2="{gx}" y2="{gy+gh}" stroke="{INK}" stroke-width="1.2"/>')
    bw = gw / len(values) * 0.55
    for i, (v, lg) in enumerate(zip(values, logs)):
        x = gx + (i + 0.5) * gw / len(values) - bw / 2
        h = lg / top * gh
        out.append(f'<rect x="{x:.1f}" y="{gy+gh-h:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="{BLUE}" opacity="0.75"/>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{gy+gh+18}" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="{MUTED}" text-anchor="middle">span {i+1}</text>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{gy+gh-h-6:.1f}" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="{INK}" text-anchor="middle">{v:,}</text>')
    out.append(f'<text x="{gx}" y="40" font-family="Georgia,serif" font-size="13" fill="{INK}">Fig. G2 · one grid per span: denominator 5^k, composite 5⁶ = 15,625</text>')
    out.append(f'<text x="{gx}" y="58" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}">cells needed to carry the whole chain on one integer grid</text>')
    out.append(f'<g font-family="Georgia,serif" font-size="15"><rect x="{gx}" y="330" width="18" height="10" fill="{BLUE}" opacity="0.75"/><text x="{gx+26}" y="339" fill="{INK}">grid cells for span k</text></g>')
    return "\n".join(out)


def run() -> None:
    parts = [(1, "stalk"), (5, "connector"), (25, "flower")]
    comp = 1
    for d, _ in parts:
        comp = comp * d // math.gcd(comp, d)
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Multi-grid design</title>
<style>
:root{{--paper:{PAPER};--ink:{INK};--muted:{MUTED};--rule:{RULE}}}
*{{box-sizing:border-box}} body{{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:31px;line-height:1.12;margin:0 0 8px}} h2{{font-size:20px;margin:0 0 8px}}
.lede{{max-width:920px;color:var(--muted)}} .panel{{background:var(--paper);border:1px solid var(--rule);padding:16px 18px;margin:0 0 18px}}
table{{border-collapse:collapse;font:12px/1.5 ui-monospace,Menlo,monospace;margin:10px 0;width:100%}}
th,td{{border:1px solid var(--rule);padding:5px 8px;text-align:right}} th{{color:var(--muted);font-weight:400}}
.small{{font:12px/1.55 ui-monospace,Menlo,monospace;color:var(--muted)}}
code{{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}}
</style></head><body><main>
<p class="eyebrow">curve-lab · composition</p>
<h1>One design, three grids</h1>
<p class="lede">Nothing forces a design onto a single ruling. Each part can declare the grid its own detail needs, as long as every join is a point that exists in both grids — which is automatic when the grids are a chain of multiples.</p>

<section class="panel">
<h2>Fig. G1 · stalk, connector, flower</h2>
<svg viewBox="0 0 980 520" width="100%" role="img" aria-label="three parts on three grids">
{svg_design()}
</svg>
<p class="small">The stalk is on integers because it only has to land on lattice marks. The connector needs fifths to meet the flower's forty-five degree seams. The flower is on twenty-fifths. The dashed lines are declared seams, not accidents.</p>
</section>

<section class="panel">
<h2>The rule</h2>
<p>A part on grid <code>1/d</code> can join a part on grid <code>1/e</code> exactly when the shared point's coordinates are multiples of <code>1/lcm(d,e)</code> — true whenever the finer grid is a multiple of the coarser. The composite grid is the lcm, and the cost is the number of cells it needs:</p>
<table><tr><th>part</th><th>grid</th><th>cells per unit</th></tr>
{"".join(f"<tr><td>{name}</td><td>1/{d}</td><td>{d}</td></tr>" for d, name in parts)}
<tr><td>composite</td><td>1/{comp}</td><td>{comp}</td></tr></table>
<p class="small">Three parts, 25 cells — cheaper than putting every part on the finest grid from the start, and exactly as exact.</p>
</section>

<section class="panel">
<h2>Fig. G2 · the per-span version, and its price</h2>
<svg viewBox="0 0 980 360" width="100%" role="img" aria-label="grid cells per span">
{svg_cost()}
</svg>
<p>Give each span of a turn-exact chain its own grid — <code>5</code>, <code>25</code>, <code>125</code> … — and the design is legal; but any single global grid that holds all of them is the product, <code>5^k</code>. Six spans cost <b>15,625</b> cells per unit, twelve cost <b>244 million</b>. That is the same explosion as the scaling table, now visible as a layout cost rather than a number-theory one.</p>
<p class="small">The practical rule: per-part grids are cheap when the parts are few and the multiples are small; per-span grids are cheap only for short chains. Past about six spans, the composite grid is no longer a drawing surface but a data structure.</p>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "multi-grid.html"
    out.write_text(html, encoding="utf-8")
    print(out)
    print("composite grid:", comp)


if __name__ == "__main__":
    run()
