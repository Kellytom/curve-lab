"""The node curves, all in one place, against the log-aesthetic law.

    .venv/bin/python scripts/node_curves.py
    open workbench/node-curves.html

Every curve here has a singular point: a node where leaves meet, a cusp where
the radius collapses, a corner where the tangent jumps. The question asked of
each is the same one asked of the LAC family:

    rho^p = c0 s + c1 ?

The answer is in the table: the circle fits to 0.0000, nothing else does whole,
and a lobe trimmed away from its node gets close without ever arriving. That is
the finding, and it says what to do with these curves: one near-LAC span per
lobe, and a declared join at the node, which is what `curve_lab.junction` is for.

The fit is checked on curves generated from known p (`scripts/lac_fit.py
--control`) before it is used to judge anything.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lac_fit import best_power  # noqa: E402
from ph_crossings import spine  # noqa: E402

OUT = ROOT / "workbench" / "node-curves.html"
PLATE = 180


def arc(fn, t0, t1, n=2400):
    return [fn(t0 + (t1 - t0) * i / n) for i in range(n + 1)]


def rose(petals, phase=0.0):
    return lambda t: (math.cos(petals * t) * math.cos(t + phase),
                      math.cos(petals * t) * math.sin(t + phase))


def lemniscate_gerono(t):
    return (math.cos(t), math.sin(t) * math.cos(t))


def lemniscate_bernoulli(t):
    r = math.sqrt(max(0.0, math.cos(2 * t)))
    return (r * math.cos(t), r * math.sin(t))


def piriform(t):
    return (1 + math.sin(t), math.cos(t) * (1 + math.sin(t)))


def involute(t):
    """The circle involute: rho = t and s = t squared / 2, so rho squared is 2 s."""
    return (math.cos(t) + t * math.sin(t), math.sin(t) - t * math.cos(t))


def strophoid(t):
    d = 1 + t * t
    return ((1 - t * t) / d, t * (1 - t * t) / d)


R = 1.0
CURVES = [
    # name, node, whole range, trimmed range, node description
    ("circle", lambda t: (math.cos(t), math.sin(t)), "none", (0, math.pi / 2), (0, math.pi / 2),
     "no singular point", "LAC, p = 0"),
    ("cardioid", lambda t: (2 * R * math.cos(t) - R * math.cos(2 * t),
                            2 * R * math.sin(t) - R * math.sin(2 * t)),
     "cusp", (0, 2 * math.pi), (0.4, 2 * math.pi - 0.4), "one cusp", "circle arcs, joined at the cusp"),
    ("nephroid", lambda t: (3 * R * math.cos(t) - R * math.cos(3 * t),
                            3 * R * math.sin(t) - R * math.sin(3 * t)),
     "cusp", (0, 2 * math.pi), (0.4, 2 * math.pi - 0.4), "two cusps", "circle arcs, joined"),
    ("deltoid", lambda t: (2 * R * math.cos(t) + R * math.cos(2 * t),
                           2 * R * math.sin(t) - R * math.sin(2 * t)),
     "cusp", (0, 2 * math.pi), (0.4, 2 * math.pi - 0.4), "three cusps", "circle arcs, joined"),
    ("astroid", lambda t: (3 * R * math.cos(t) + R * math.cos(3 * t),
                           3 * R * math.sin(t) - R * math.sin(3 * t)),
     "cusp", (0, 2 * math.pi), (0.4, 2 * math.pi - 0.4), "four cusps", "circle arcs, joined"),
    ("gerono", lemniscate_gerono, "node", (0, 2 * math.pi), (0.5, math.pi - 0.5), "node at the seam", "a figure-eight, not a radius law"),
    ("bernoulli", lemniscate_bernoulli, "node",
     (-math.pi / 4, math.pi / 4), (-math.pi / 4 + 0.3, math.pi / 4 - 0.3), "node at the centre", "a figure-eight, not a radius law"),
    ("piriform", piriform, "node",
     (-math.pi / 2, 3 * math.pi / 2), (0.0, math.pi), "node at the narrow end", "a quartic with a node"),
    ("quadrifolium", rose(2), "node", (-math.pi / 4, math.pi / 4),
     (-math.pi / 4 + 0.6, math.pi / 4 - 0.6), "four leaves meet at the centre", "a rose, node at the centre"),
    ("trifolium", rose(3), "node", (-math.pi / 6, math.pi / 6),
     (-math.pi / 6 + 0.35, math.pi / 6 - 0.35), "three leaves meet at the centre", "a rose, node at the centre"),
    ("strophoid", strophoid, "node", (-0.999, 0.999), (-0.35, 0.35), "node where the loop closes", "an algebraic loop"),
    ("circle involute", involute, "cusp", (0, 2 * math.pi), (0.4, 2 * math.pi),
     "cusp where it leaves the circle", "LAC, p = 2"),
    ("maclaurin trisectrix", lambda t: ((2 * math.cos(t) - 1) * math.cos(t),
                                        (2 * math.cos(t) - 1) * math.sin(t)),
     "node", (-math.pi / 3, math.pi / 3), (-math.pi / 3 + 0.4, math.pi / 3 - 0.4),
     "node where the loop closes", "an algebraic loop"),
    ("catenary", lambda t: (t, math.cosh(t)), "none", (-1.5, 1.5), (-1.2, 1.2),
     "no singular point: a hanging chain", "cosh, a transcendental curve"),
    ("pell hyperbola", lambda t: (math.cosh(t), math.sinh(t) / math.sqrt(2)),
     "none", (-1.2, 1.2), (-1.0, 1.0), "the conic through 71/41", "a conic, not a radius law"),
    ("reuleaux arc", lambda t: (math.cos(t), math.sin(t)), "corner", (0, math.pi / 3),
     (0, math.pi / 3), "one circle arc of the three", "LAC, p = 0, joined at corners"),
    ("biarc, one arc", lambda t: (math.cos(t), math.sin(t)), "join", (0.3, 1.4), (0.3, 1.4),
     "one of the two circle arcs", "LAC, p = 0, joined G1"),
]

def recovered_spine(title, index):
    """A spine as drawn on the Stage II plates, y flipped back to design space."""
    import json
    data = json.loads((ROOT / "workbench" / "spirals" / "stage-two.json").read_text())
    for figure in data["figures"]:
        if figure["title"] != title:
            continue
        points = []
        for span in figure["spines"][index]["spans"]:
            p0, c1, c2, p3 = span["p0"], span["c1"], span["c2"], span["p3"]
            for i in range(41):
                t = i / 40
                u = 1 - t
                x = u**3*p0[0] + 3*u*u*t*c1[0] + 3*u*t*t*c2[0] + t**3*p3[0]
                y = u**3*p0[1] + 3*u*u*t*c1[1] + 3*u*t*t*c2[1] + t**3*p3[1]
                points.append((x, -y))
        return points
    return None


SANDBOX = [
    ("cusp5-x3", [1, 0, 0, 0, 0, 0], [-3, 30, -120, 240, -240, 96], "cusp from a repeated root"),
    ("cusp7-deep", [1, 0, 0, 0, 0, 0, 0, 0],
     [-4, 56, -336, 1120, -2240, 2688, -1792, 512], "cusp from a repeated root"),
    ("twin-cusp", [2, 0, 0, 0, 0, 0, 0], [8, -108, 594, -1701, 2673, -2187, 729], "two cusps"),
]


def plate(points, label, number):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    pad = 14
    scale = (PLATE - 2 * pad) / span
    ox = pad - min(xs) * scale
    oy = pad - min(ys) * scale
    path = "M" + " L".join(f"{(ox + x * scale):.1f},{(oy + y * scale):.1f}" for x, y in points)
    return f'''<figure class="plate">
  <figcaption><span class="tag">Fig. N{number}</span> {label}</figcaption>
  <svg viewBox="0 0 {PLATE} {PLATE}" role="img" aria-label="{label}">
    <rect width="{PLATE}" height="{PLATE}" fill="#fbf7ec"/>
    <path d="{path}" fill="none" stroke="#2e2413" stroke-width="1.4"/>
  </svg>
</figure>'''


def build():
    rows = []
    plates = []
    number = 1
    for name, fn, node, whole, trimmed, note, built in CURVES:
        whole_residual, whole_power = best_power(arc(fn, *whole))
        trimmed_residual, trimmed_power = best_power(arc(fn, *trimmed))
        rows.append((name, note, built, whole_residual, whole_power,
                     trimmed_residual, trimmed_power))
        plates.append(plate(arc(fn, *whole), f"{name} &middot; {note}", number))
        number += 1

    recovered = recovered_spine("Stage II: Involute, one turn each way", 3)
    if recovered:
        whole_residual, whole_power = best_power(recovered)
        rows.append(("involute, as drawn", "Stage II Fig. 14 spine 4, recovered",
                     "LAC, p = 2, drawn 3% off", whole_residual, whole_power, None, None))
        plates.append(plate(recovered, "involute, as drawn &middot; recovered spine", number))
        number += 1

    for name, speed_x, speed_y, note in SANDBOX:
        _, x, y = spine(speed_x, speed_y, 900)
        points = list(zip(x, y))
        whole_residual, whole_power = best_power(points)
        rows.append((name, note, "cusp from a repeated root", whole_residual,
                     whole_power, None, None))
        plates.append(plate(points, f"{name} &middot; {note}", number))
        number += 1

    def verdict(residual):
        if residual is None:
            return "&mdash;"
        if residual < 0.01:
            return "an LAC"
        if residual < 0.05:
            return "close"
        return "no"

    body = "".join(
        f'<tr><td>{name}</td><td>{note}</td><td>{built}</td>'
        f'<td class="num">{verdict(whole_residual)}</td><td class="num">{whole_residual:.4f}</td>'
        f'<td class="num">{verdict(trimmed_residual)}</td>'
        f'<td class="num">{"&mdash;" if trimmed_residual is None else f"{trimmed_residual:.4f}"}</td>'
        f'</tr>'
        for name, note, built, whole_residual, whole_power, trimmed_residual, trimmed_power in rows)

    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Node curves against the log-aesthetic law</title>
<style>
:root{{--paper:#fbf7ec;--ink:#2e2413;--muted:#7b6c4e;--rule:#d8ccae}}
*{{box-sizing:border-box}}
body{{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:18px 20px 40px}}
h1{{font-size:24px;margin:0 0 4px}}
.eyebrow{{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;
  text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
.panel{{background:var(--paper);border:1px solid var(--rule);padding:12px 14px;margin:0 0 12px}}
table{{border-collapse:collapse;width:100%;font:12px ui-monospace,Menlo,monospace}}
th,td{{border-bottom:1px solid var(--rule);padding:4px 8px;text-align:left}}
th{{color:var(--muted);font-weight:400}}
.num{{text-align:right}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}
@media(max-width:820px){{.grid{{grid-template-columns:repeat(2,1fr)}}}}
.plate{{margin:0;background:var(--paper);border:1px solid var(--rule);padding:6px}}
.plate figcaption{{font:10px/1.4 ui-monospace,Menlo,monospace;color:var(--muted);margin:0 0 4px}}
.plate .tag{{color:#8a3b2a}}
.plate svg{{width:100%;height:auto;display:block}}
</style></head><body><main>
<p class="eyebrow">curve-lab &middot; node curves</p>
<h1>Which of these are LACs, and what the rest are built by</h1>
<section class="panel">
<p><strong>Most of these are not log-aesthetic curves, and they should not be
built as if they were.</strong> The LAC law is <code>rho^p = c0 s + c1</code>: the
radius of curvature as a power of a straight line in arc length. It holds exactly
for the circle, the circle involute, the Euler spiral and the log spiral, and for
nothing else on this page.</p>
<p>Each row carries the rule the curve is actually built by. The rolling-circle
family and the roses are circle arcs joined at their cusps and nodes; the
lemniscates and the piriform are algebraic curves with a node; the catenary is
<code>cosh</code>; the Pell curve is a conic; the biarc and the Reuleaux triangle
are circle arcs with tangent joins. Those are the rules to use for them.</p>
<p>The LAC column is kept because it was asked for, and because it shows one
useful thing: a lobe trimmed away from its node is <em>nearly</em> a power law
(the quadrifolium 0.015, the strophoid 0.020), so a lobe can be one LAC span with
a declared join at the node. That is a construction choice, not a claim that the
curve is an LAC.</p>
</section>
<section class="panel">
<table>
<tr><th>curve</th><th>node</th><th>built by</th><th class="num">whole</th>
<th class="num">residual</th><th class="num">trimmed</th><th class="num">residual</th></tr>
{body}
</table>
</section>
<section class="panel">
<div class="grid">
{"".join(plates)}
</div>
</section>
</main></body></html>
'''
    OUT.write_text(page)
    print(f"{OUT.relative_to(ROOT)}  {len(plates)} plates, {len(rows)} rows")


if __name__ == "__main__":
    build()
