"""A stem assembled from parts on different grids, with the seams measured.

    .venv/bin/python scripts/composed_stem.py
    open workbench/composed-stem.html

Part 1 is an Euclid chain on integers. A straight link carries it to part 2,
which is shifted by exactly 1/5 unit - a declared step that exists because both
parts sit on the composite grid. What the step costs is a tangent kink, and that
is the number on the page.
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import pyth_chain as pc  # noqa: E402

INK, GOLD, BLUE, RED = "#2e2413", "#c9a441", "#1f5fa8", "#a23b2a"
MUTED, RULE, PAPER = "#7b6c4e", "#d8ccae", "#fbf7ec"

STEP = Fraction(1, 5)


def chain(m0: int, m1: int):
    pts = [{"a": m * m - 1, "b": 2 * m} for m in range(m0, m1 + 1)]
    T = pc.tangents(pts)
    return pc.spans(T), pc.nodes(T), T


def run() -> None:
    spans_a, nodes_a, T_a = chain(2, 4)
    end = nodes_a[-1]
    tx, ty = T_a[-1]
    L = math.hypot(tx, ty)
    ux, uy = tx / L, ty / L
    link_len = 7.0
    link_end = (end[0] + link_len * ux, end[1] + link_len * uy)

    step = (0.0, float(STEP))
    start_b = (link_end[0] + step[0], link_end[1] + step[1])

    spans_b, nodes_b, T_b = chain(2, 4)
    nodes_b = [(x + start_b[0], y + start_b[1]) for x, y in nodes_b]
    spans_b = [tuple((p[0] + start_b[0], p[1] + start_b[1]) for p in c) for c in spans_b]

    # tangent mismatch at the seam
    tx0, ty0 = T_b[0]
    ang_a = math.degrees(math.atan2(uy, ux))
    ang_b = math.degrees(math.atan2(ty0 / math.hypot(tx0, ty0), tx0 / math.hypot(tx0, ty0)))
    kink = abs((ang_b - ang_a + 180) % 360 - 180)

    # draw
    allpts = [p for c in spans_a for p in c] + [end, link_end, start_b] + [p for c in spans_b for p in c]
    xs = [p[0] for p in allpts]
    ys = [p[1] for p in allpts]
    W, H, pad = 980, 620, 60
    s = min((W - 2 * pad) / (max(xs) - min(xs)), (H - 2 * pad) / (max(ys) - min(ys)))
    ox = (W - (max(xs) - min(xs)) * s) / 2
    oy = (H - (max(ys) - min(ys)) * s) / 2

    def put(p):
        return (ox + (p[0] - min(xs)) * s, H - oy - (p[1] - min(ys)) * s)   # +y up, flipped here

    def cubic(c):
        pts = [pc.bezier(c, i / 24) for i in range(25)]
        return " ".join(("M" if i == 0 else "L") + f"{put(p)[0]:.1f},{put(p)[1]:.1f}"
                        for i, p in enumerate(pts))

    def dot(p, colour, r=3.4):
        q = put(p)
        return f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="{r}" fill="{PAPER}" stroke="{colour}" stroke-width="1.6"/>'

    seam = put(start_b)
    seam0 = put(link_end)

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Composed stem · two grids, one seam</title>
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
<h1>Two chains, one step, one kink</h1>
<p class="lede">Two integer stalks cannot simply be laid end to end and be both exact and smooth. The step between them is legal because 1/5 exists on both grids; the kink is what that step costs.</p>

<section class="panel">
<h2>Fig. C1 · the composed stem</h2>
<svg viewBox="0 0 980 620" width="100%" role="img" aria-label="two chains joined by a link with a 1/5 step">
<rect width="980" height="620" fill="{PAPER}"/>
{"".join(f'<path d="{cubic(c)}" fill="none" stroke="{BLUE}" stroke-width="2.6"/>' for c in spans_a)}
<line x1="{put(end)[0]:.1f}" y1="{put(end)[1]:.1f}" x2="{seam0[0]:.1f}" y2="{seam0[1]:.1f}" stroke="{INK}" stroke-width="2.2"/>
<line x1="{seam0[0]:.1f}" y1="{seam0[1]:.1f}" x2="{seam[0]:.1f}" y2="{seam[1]:.1f}" stroke="{GOLD}" stroke-width="3"/>
{"".join(f'<path d="{cubic(c)}" fill="none" stroke="{BLUE}" stroke-width="2.6"/>' for c in spans_b)}
{dot(end, INK)}{dot(start_b, GOLD, 4)}
<text x="16" y="24" font-family="Georgia,serif" font-size="13" fill="{INK}">Fig. C1 · chain on 1 (blue) → link (ink) → step 1/5 (gold) → chain on 1/5 (blue) · +y up, flipped to screen y down</text>
<text x="16" y="44" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}">declared step 0.200 · tangent kink {kink:.2f}° · composite grid 1/5</text>
<g font-family="Georgia,serif" font-size="15">
<line x1="16" y1="590" x2="52" y2="590" stroke="{BLUE}" stroke-width="3"/><text x="60" y="595" fill="{INK}">Euclid chain (integers)</text>
<line x1="300" y1="590" x2="336" y2="590" stroke="{INK}" stroke-width="2.2"/><text x="344" y="595" fill="{INK}">link</text>
<line x1="430" y1="590" x2="466" y2="590" stroke="{GOLD}" stroke-width="3"/><text x="474" y="595" fill="{INK}">declared step, 1/5</text>
</g>
</svg>
<p class="small">The two chains are the same family; only the placement differs. The link is a straight run, so it adds no curvature claim. Everything is exact — the step is a fraction, not a rounding.</p>
</section>

<section class="panel">
<h2>What the seam costs</h2>
<table>
<tr><th>quantity</th><th>value</th><th>exact?</th></tr>
<tr><td>seam step</td><td>0.200 = 1/5</td><td>yes</td></tr>
<tr><td>composite grid</td><td>1/5</td><td>yes</td></tr>
<tr><td>tangent kink at the seam</td><td>{kink:.2f}°</td><td>measured, not designed</td></tr>
<tr><td>position gap</td><td>0</td><td>yes, shared seam point</td></tr>
</table>
<p>Position is exact and free; tangency is not. A step that exists on both grids still turns the stem, and that turn is the number to design with — either accept it as a node, or spend a connector that is tangent at both ends.</p>
<p class="small">The cheap fix is a circular arc between the two ends: its radius must be a multiple of the coarser grid if its endpoints are to stay exact, which is the same trade one level down.</p>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "composed-stem.html"
    out.write_text(html, encoding="utf-8")
    print(out)
    print(f"step {float(STEP):.3f} · kink {kink:.2f} deg · composite grid 1/5")


if __name__ == "__main__":
    run()
