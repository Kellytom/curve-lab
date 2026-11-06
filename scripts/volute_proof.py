"""Volute proof 01: the exact p-triple spiral under the plant-form rules.

    .venv/bin/python scripts/volute_proof.py

The spine is `pythagorean-spiral`'s open curl on the thinnest triangle under
3125 — 33 equal chords, each turned by a whole multiple of the triangle angle.
Every node is an exact rational point. The plant grammar adds the rest:

- two rails at ±d, separated by 2d (numeric normal offsets; the spiral's exact
  partner is a *scaled and rotated* spiral, so a constant width is fitted and
  is labelled so);
- a cone terminal at the open tip, R = 2 × offset;
- a branch off an exact node, with its own seagrass ending.

The counts and angles are recomputed here from the spine package, so the page
cannot drift from the chain it claims to draw.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from curve_lab import spine as SL  # noqa: E402
from curve_lab import plant as P  # noqa: E402
import plant_forms as PF  # noqa: E402

INK, BLUE, RED, GOLD, GREEN = "#2e2413", "#1f5fa8", "#a23b2a", "#c9a441", "#2f6f4f"
MUTED, PAPER, GRID = "#7b6c4e", "#fffdf7", "#e4dcc6"

STEPS = 33
OFFSET = 0.26
BRANCH_NODE = 12
BRANCH_LENGTH = 2.8


def _chain():
    pkg = SL.load()
    tri = pkg.thinnest(3125)
    chain = pkg.Spiral(tri, 1)
    chain.extend(range(STEPS))
    return pkg, tri, chain


def proof_data() -> dict:
    pkg, tri, chain = _chain()
    return {
        "chords": STEPS,
        "nodes": len(chain.nodes),
        "alpha": tri.degrees,
        "peak": chain.peak_degrees,
        "triangle": f"{tri.a}-{tri.b}-{tri.c}",
        "offset": OFFSET,
        "width": 2.0 * OFFSET,
        "radius": 2.0 * OFFSET,
        "branch_node": BRANCH_NODE,
        "branch_length": BRANCH_LENGTH,
    }


def build_items():
    _, tri, chain = _chain()
    pts = chain.floats()
    plus, minus = PF.normal_offsets(pts, OFFSET)
    items = [
        (plus, BLUE, 1.2, None),
        (minus, RED, 1.2, None),
        (pts, INK, 2.2, None),
    ]

    tip = pts[-1]
    tangent = (pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1])
    cone = P.cone_terminal(tip, tangent, OFFSET)
    items.append((cone["left"], INK, 1.8, None))
    items.append((cone["right"], INK, 1.8, None))

    bp, heading = chain.knots()[BRANCH_NODE]
    angle = math.atan2(float(heading.im), float(heading.re))
    br = P.branch((float(bp[0]), float(bp[1])), (math.cos(angle), math.sin(angle)),
                  1, BRANCH_LENGTH)
    bp_plus, bp_minus = PF.normal_offsets(br, 0.42 * OFFSET)
    items.append((bp_plus, BLUE, 0.8, None))
    items.append((bp_minus, RED, 0.8, None))
    items.append((br, INK, 1.5, None))
    btip = br[-1]
    btan = (br[-1][0] - br[-2][0], br[-1][1] - br[-2][1])
    for blade in P.seagrass(btip, btan, 0.45 * OFFSET):
        items.append((blade, GREEN, 1.1, None))
    bx, by = float(bp[0]), float(bp[1])
    items.append(([(bx - 0.09, by), (bx, by + 0.09), (bx + 0.09, by),
                   (bx, by - 0.09), (bx - 0.09, by)], GOLD, 0.8, None, GOLD))
    return items


def main() -> int:
    data = proof_data()
    items = build_items()
    figure = PF.figure(items, 900, 720)

    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Volute proof 01 — the exact spiral on the plant grammar</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1000px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 18px}}
h2{{font:600 12px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.10em;text-transform:uppercase;color:{MUTED};margin:30px 0 8px}}
.panel{{background:{PAPER};border:1px solid #d8ccae;padding:16px 18px;margin:0 0 18px}}
.art{{background:{PAPER};border:1px solid #d8ccae;padding:8px;margin:0 0 8px}}
svg{{display:block;width:100%;height:auto}}
.legend{{display:flex;gap:16px;flex-wrap:wrap;font:11px ui-monospace,Menlo,monospace;color:{MUTED};margin:6px 0 0}}
.sw{{display:inline-block;width:20px;height:0;border-top:3px solid {INK};margin-right:5px;vertical-align:middle}}
.sw.b{{border-top:2px solid {BLUE}}}.sw.r{{border-top:2px solid {RED}}}
.sw.g{{border-top:2px solid {GOLD}}}.sw.e{{border-top:2px solid {GREEN}}}
table{{border-collapse:collapse;width:100%;font:12px/1.5 ui-monospace,Menlo,monospace;margin:8px 0 0}}
td,th{{border-bottom:1px solid #d8ccae;padding:5px 8px;text-align:left}}
th{{color:{MUTED};font-weight:600}}
code{{font:12px ui-monospace,Menlo,monospace}}
</style></head><body><main>
<h1>Volute proof 01</h1>
<p class="lead">A scroll from the exact spine, finished by the plant grammar:
two rails, a cone terminal, and a branch with its own ending.</p>

<div class="panel">
<p><strong>The chain.</strong> {data['chords']} equal chords on the
{data['triangle']} triangle, each turned by a whole multiple of
{data['alpha']:.4f}°. Every node is an exact rational point; the peak heading is
{data['peak']:.1f}°, a little over two turns. This is the spine, not a fitted
spiral.</p>
<p><strong>The grammar.</strong> The rails stand at ±{data['offset']:g}, so the
band is 2d = {data['width']:g} wide. The open tip ends in a cone terminal of
radius 2 × offset = {data['radius']:g}. A branch leaves node
{data['branch_node']} and ends in seagrass, because a branch inherits the
ending rule. No bare tip.</p>
<p class="note">The rails are numeric normal offsets: a log-spiral's exact
partner is scaled <em>and</em> rotated, so a constant width here is fitted.
The spine is exact; the band is the stated approximation.</p>
</div>

<div class="art">{figure}</div>
<div class="legend">
<span><i class="sw"></i> exact spine</span>
<span><i class="sw b"></i> +offset rail</span>
<span><i class="sw r"></i> −offset rail</span>
<span><i class="sw g"></i> branch node</span>
<span><i class="sw e"></i> seagrass branch ending</span>
</div>

<h2>The three aspects</h2>
<div class="panel">
<p><strong>Linearity:</strong> every chord is straight; the chain is a polygon
before it is a curve. <strong>Curve:</strong> the heading turns by a growing
whole-number multiple, so the curvature changes from chord to chord.
<strong>Infinity:</strong> the open spiral tends to a limit heading and a limit
circle it never reaches. The volute is a complete design under the rule: all
three aspects are present, and none of them is decorative.</p>
<p><strong>Grounded:</strong> the start tangent is the declared horizontal; the
90° heading is the vertical. The scroll stands on the one and rises through
the other.</p>
</div>

<h2>The numbers</h2>
<div class="panel">
<table>
<tr><th>chords</th><td>{data['chords']} equal chords · {data['nodes']} nodes</td></tr>
<tr><th>triangle</th><td>{data['triangle']} · acute angle {data['alpha']:.4f}°</td></tr>
<tr><th>peak heading</th><td>{data['peak']:.1f}° · exact rational nodes</td></tr>
<tr><th>rails</th><td>±{data['offset']:g} · 2d = {data['width']:g}</td></tr>
<tr><th>cone terminal</th><td>R = 2 × offset = {data['radius']:g}</td></tr>
<tr><th>branch</th><td>node {data['branch_node']} · {data['branch_length']:g} long · seagrass ending</td></tr>
</table>
</div>

<h2>Why it is a proof</h2>
<div class="panel">
<p>The volute is not a special drawing: it is the same spine layer that carries
the S-curves and the 3-4-5 lobe, with the plant rules applied to it. The rails
are offsets, the tip is a terminal, the branch leaves an exact node and gets the
same ending vocabulary. The 2 × offset rule and the no-bare-tip rule hold on a
scroll, which is the ornament the plant grammar has to survive.</p>
<p class="note">Re-derive: <code>python scripts/volute_proof.py</code> ·
<code>python -m unittest tests.test_volute_proof</code></p>
</div>
</main></body></html>
'''
    out = ROOT / "workbench" / "volute-proof.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
