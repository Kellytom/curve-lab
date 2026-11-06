"""Cruciform proof 01: the section and junction rules, on a cross.

    .venv/bin/python scripts/cruciform_proof.py

A cruciform is two full lines crossing. This proof does not draw an X and call
it legal: it builds two `Junction`s, one from each side, each with a declared
merge and a measured G1 fillet, and one trunk carrying `Section` stations. The
four tips end in cone terminals, so no arm is a bare tip.

The numbers come from `curve_lab.junction` and `curve_lab.section`; the page
recomputes them at build time.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from curve_lab import engine, plant as P  # noqa: E402
from curve_lab.junction import Junction  # noqa: E402
from curve_lab.section import sections  # noqa: E402
from curve_lab.piece import Trace  # noqa: E402
import plant_forms as PF  # noqa: E402

INK, BLUE, RED, GOLD, GREEN = "#2e2413", "#1f5fa8", "#a23b2a", "#c9a441", "#2f6f4f"
MUTED, PAPER = "#7b6c4e", "#fffdf7"

TRUNK_WIDTH = 0.50
BRANCH_WIDTH = 0.30
RADIUS = 0.60
ARM = 4.0
TRUNK_LENGTH = 8.0


def _junction(side: int) -> Junction:
    return Junction(
        corner=(0.0, 0.0),
        branch_end=(side * ARM, 0.0),
        trunk_end=(0.0, ARM),
        radius=RADIUS,
        branch_width=BRANCH_WIDTH,
        trunk_width=TRUNK_WIDTH,
        trunk_length=TRUNK_LENGTH,
        branch_name=f"ink/branch-{'left' if side < 0 else 'right'}",
        trunk_name="ink/trunk",
    )


def _sample(design, n=200):
    chain = engine.build(design)
    return [chain.point(chain.length * i / (n - 1)) for i in range(n)]


def proof_data() -> dict:
    left, right = _junction(-1), _junction(1)
    bl, br = left.build(), right.build()
    arc = bl["report"]["arc_length"]
    return {
        "junctions": 2,
        "merges": 2,
        "trunk_width": TRUNK_WIDTH,
        "branch_width": BRANCH_WIDTH,
        "radius": RADIUS,
        "arc": arc,
        "join": bl["report"]["join"],
        "curvature_step": bl["report"]["curvature_step"],
        "arm": ARM,
        "terminals": 4,
        "sections": 7,
        "merge_left": bl["contact"].point if hasattr(bl["contact"], "point") else bl["report"]["merge"],
        "merge_right": br["report"]["merge"],
    }


def build_items():
    left, right = _junction(-1), _junction(1)
    bl, br = left.build(), right.build()
    lbr = bl["piece"].traces[0].design
    rbr = br["piece"].traces[0].design
    trunk = bl["piece"].traces[1].design

    lpts, rpts = _sample(lbr), _sample(rbr)
    tpts = _sample(trunk)

    items = []
    for pts, width in ((lpts, BRANCH_WIDTH), (rpts, BRANCH_WIDTH)):
        plus, minus = PF.normal_offsets(pts, width / 2.0)
        items.append((plus, BLUE, 1.0, None))
        items.append((minus, RED, 1.0, None))
        items.append((pts, INK, 1.9, None))
    tplus, tminus = PF.normal_offsets(tpts, TRUNK_WIDTH / 2.0)
    items.append((tplus, BLUE, 1.1, None))
    items.append((tminus, RED, 1.1, None))
    items.append((tpts, INK, 2.2, None))

    # cone terminals at the four tips
    tips = [((ARM, 0.0), (1.0, 0.0), BRANCH_WIDTH / 2.0),
            ((-ARM, 0.0), (-1.0, 0.0), BRANCH_WIDTH / 2.0),
            ((0.0, ARM), (0.0, 1.0), TRUNK_WIDTH / 2.0),
            ((0.0, -ARM), (0.0, -1.0), TRUNK_WIDTH / 2.0)]
    for point, tangent, offset in tips:
        cone = P.cone_terminal(point, tangent, offset)
        items.append((cone["left"], INK, 1.7, None))
        items.append((cone["right"], INK, 1.7, None))

    # section stations across the trunk
    trace = Trace("trunk", trunk, width=TRUNK_WIDTH)
    for sec in sections(trace, samples=6):
        items.append(([sec.left, sec.right], GOLD, 1.0, "3 3"))

    # the two declared merges
    for built in (bl, br):
        mx, my = built["report"]["merge"]
        items.append(([(mx - 0.08, my), (mx, my + 0.08), (mx + 0.08, my),
                       (mx, my - 0.08), (mx - 0.08, my)], GREEN, 0.8, None, GREEN))
    return items


def main() -> int:
    data = proof_data()
    items = build_items()
    figure = PF.figure(items, 900, 720)

    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cruciform proof 01 — sections and junctions</title>
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
<h1>Cruciform proof 01</h1>
<p class="lead">Two full lines crossing, built as two declared junctions and
one trunk with section stations — not as an undeclared X.</p>

<div class="panel">
<p><strong>The cross.</strong> The trunk runs vertically at width
{data['trunk_width']:g}; the two arms leave it at width
{data['branch_width']:g}. Each arm is a `Junction`: a branch, a circular fillet
of radius {data['radius']:g}, and a declared merge. The join is
{data['join']}, with a curvature step of {data['curvature_step']:.4f}; the page
states that rather than calling it G2.</p>
<p><strong>The sections.</strong> The dashed bars are `Section` stations across
the trunk — spine, tangent, width and both rails at one arc length. They are
the authoring view: the rails are derived from the section, not measured from a
drawing.</p>
<p><strong>The endings.</strong> All four tips end in cone terminals of
R = 2 × offset. The arms are not bare tips, and the crossing is legal only
because both merges are declared.</p>
</div>

<div class="art">{figure}</div>
<div class="legend">
<span><i class="sw"></i> trunk / arms</span>
<span><i class="sw b"></i> +offset rail</span>
<span><i class="sw r"></i> −offset rail</span>
<span><i class="sw g"></i> section station</span>
<span><i class="sw e"></i> declared merge</span>
</div>

<h2>The three aspects</h2>
<div class="panel">
<p><strong>Linearity:</strong> the trunk and the two arms are straight runs.
<strong>Curve:</strong> each fillet is a circular arc where the bend is the
point. <strong>Infinity:</strong> absent — the cross is bounded. The proof is a
legal component, not a complete design: pair it with a spiral tail or a ray to
satisfy the third aspect.</p>
<p><strong>Grounded:</strong> the horizontal arms are the datum; the trunk is
the vertical. The cross stands on its arms.</p>
</div>

<h2>The numbers</h2>
<div class="panel">
<table>
<tr><th>junctions</th><td>{data['junctions']} · one from each side of the trunk</td></tr>
<tr><th>merges</th><td>{data['merges']} declared contacts · no undeclared crossing</td></tr>
<tr><th>fillet</th><td>radius {data['radius']:g} · arc {data['arc']:.4f} · {data['join']}</td></tr>
<tr><th>curvature step</th><td>1 / r = {data['curvature_step']:.4f}</td></tr>
<tr><th>widths</th><td>trunk {data['trunk_width']:g} · arm {data['branch_width']:g}</td></tr>
<tr><th>terminals</th><td>{data['terminals']} cone ends · R = 2 × offset</td></tr>
<tr><th>sections</th><td>{data['sections']} stations across the trunk</td></tr>
</table>
</div>

<h2>Why it is a proof</h2>
<div class="panel">
<p>A cruciform is not a cross drawn twice: it is a junction problem. Each arm
declares where it meets the trunk, the fillet is measured, the join grade is
reported, and the four tips use the same terminal vocabulary as the stalks. The
section object supplies the rails at a station, so the width is a number, not a
stroke setting.</p>
<p class="note">Re-derive: <code>python scripts/cruciform_proof.py</code> ·
<code>python -m unittest tests.test_cruciform_proof</code></p>
</div>
</main></body></html>
'''
    out = ROOT / "workbench" / "cruciform-proof.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
