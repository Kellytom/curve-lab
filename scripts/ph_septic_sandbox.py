"""The septic sandbox: a general polynomial and a PH septic, side by side.

    .venv/bin/python scripts/ph_septic_sandbox.py
    open workbench/ph-septic-sandbox.html

A polynomial PH curve has odd degree: `r' = w^2` with `w` of degree n gives a
position of degree `2n + 1`.  So degree 6 is not a polynomial PH curve at all;
degree 7 is `w` cubic.  Panel A is the general degree-7 polynomial (both axes
free, no PH promise); panel B is the PH septic, which keeps rational offsets
and integer hits.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "ph-septic-sandbox.html"
PANELS = ROOT / "scripts" / "ph_septic_panels.js"
MATH = ROOT / "scripts" / "ph_math.js"
CURVES = ROOT / "workbench" / "septic-curves.json"
SAMPLES = ROOT / "workbench" / "septic-samples.json"

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The septic sandbox: a general degree-7 curve and a PH septic</title>
<style>
:root{--paper:#fbf7ec;--ink:#2e2413;--muted:#7b6c4e;--rule:#d8ccae}
*{box-sizing:border-box}
body{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}
main{max-width:1120px;margin:0 auto;padding:34px 22px 70px}
.eyebrow{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}
h1{font-size:30px;line-height:1.12;margin:0 0 8px}
h2{font-size:20px;margin:0 0 8px}
.panel{background:var(--paper);border:1px solid var(--rule);padding:18px 20px;margin:0 0 22px}
p{margin:0 0 12px}
code{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}
pre{background:#fffdf7;border:1px solid var(--rule);padding:12px 14px;overflow:auto}
.small{font-size:13px;color:var(--muted)}
.mono{font:12px/1.5 ui-monospace,Menlo,monospace}
.spine-row{display:flex;gap:10px;align-items:center;margin:4px 0}
.spine-row>span{width:34px;color:#8a3b2a;font:13px ui-monospace,Menlo,monospace}
#b-controls .spine-row{flex-direction:column;align-items:stretch;gap:6px}
#b-controls .spine-cell{width:100%}
.spine-cell{display:flex;flex-direction:row;align-items:center;gap:8px;flex:1;min-width:110px;font:11px ui-monospace,Menlo,monospace;color:var(--muted)}
.cell-inputs{display:flex;gap:6px;align-items:center;flex:1}
.cell-inputs input[type=number]{width:56px;font:12px ui-monospace,Menlo,monospace;padding:2px 4px}
.cell-inputs input[type=range]{flex:1;min-width:56px}
#b-controls .cell-inputs input[type=number]{width:auto;min-width:96px;max-width:176px;field-sizing:content;font-variant-numeric:tabular-nums}
#b-controls .cell-inputs input[type=range]{min-width:36px}
#b-controls .cell-inputs input[type=range].decade{flex:0 0 64px;min-width:64px}
.control-row{display:flex;align-items:center;gap:8px;margin:4px 0;font:12px ui-monospace,Menlo,monospace}
.control-row span{min-width:120px;color:#8a3b2a}
.control-row input[type=number]{width:70px;font:12px ui-monospace,Menlo,monospace;padding:2px 4px}
.control-row input[type=range]{flex:1;min-width:90px}
#c-controls .control-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
.samples{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:10px 0 0}
.samples svg{width:100%;height:auto;display:block;border:1px solid var(--rule);background:var(--paper)}
@media(max-width:900px){.samples{grid-template-columns:1fr}}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start}
@media(max-width:900px){.pair{grid-template-columns:1fr}}
.trio{display:grid;grid-template-columns:1.6fr 1fr 1fr;gap:12px;align-items:start;margin:6px 0 0}
@media(max-width:1000px){.trio{grid-template-columns:1fr 1fr}}
@media(max-width:700px){.trio{grid-template-columns:1fr}}
.trio svg{margin:0}
#a-controls,#b-controls{margin:6px 0 12px}
.solver-row{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 12px}
.save-row{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 8px}
.save-row input{font:12px ui-monospace,Menlo,monospace;padding:4px 8px;width:200px}
.save-row button,.saved-row button{font:12px/1.2 ui-monospace,Menlo,monospace;padding:5px 9px;background:#fbf7ec;color:var(--ink);border:1px solid var(--rule);border-radius:3px;cursor:pointer}
.paste-row{display:flex;gap:10px;align-items:flex-start;margin:0 0 6px}
.paste-row textarea{flex:1;min-height:64px;font:12px/1.4 ui-monospace,Menlo,monospace;padding:6px 8px;border:1px solid var(--rule);background:#fffdf7;color:var(--ink)}
#b-json{width:100%;font:12px/1.5 ui-monospace,Menlo,monospace;padding:6px 8px;border:1px solid var(--rule);background:#fffdf7;color:var(--ink);resize:vertical}
.saved-row{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 12px}
.solver-row button{font:12px/1.2 ui-monospace,Menlo,monospace;padding:5px 9px;background:#fbf7ec;color:var(--ink);border:1px solid var(--rule);border-radius:3px;cursor:pointer}
svg{width:100%;height:auto;display:block;border:1px solid var(--rule);background:var(--paper)}
</style></head><body><main>
<p class="eyebrow">curve-lab | PH curves | degrees 6 and 7</p>
<h1>Demand 6 and 7: the two curves</h1>
<p>A polynomial PH curve has odd degree. With <code>r' = w^2</code>, a speed of degree <code>n</code>
gives a position of degree <code>2n + 1</code>: 5 for a quadratic speed, <strong>7 for a cubic
speed</strong>. Degree 6 is therefore not a polynomial PH curve at all - which is why this page
shows two different things, side by side.</p>
<p><strong>A</strong> is the general degree-7 polynomial: both axes free, seven <code>n_k</code> each,
no PH promise. <strong>B</strong> is the PH septic: a cubic speed, so the curve keeps rational
offsets and exact integer hits.</p>

<section class="panel">
<h2>A | the general polynomial</h2>
<p><code>x(t) = span * sum n_k t^k</code> and the same for <code>y</code>, <code>k = 1..7</code>.
Positive low orders lift, negative high orders brake, and the mix is what makes an arch or an S
rather than a ramp. The control vectors <code>u_k = n_k * span * k!</code> are the derivatives at
<code>t = 0</code>.</p>
<div id="a-controls"></div>
<svg id="a-plot" viewBox="0 0 720 520" role="img" aria-label="the general degree-7 polynomial"></svg>
<p class="small mono" id="a-readout"></p>
</section>

<section class="panel">
<h2>B | the PH septic</h2>
<p><code>w = (b_x0 + b_x1 t + b_x2 t^2 + b_x3 t^3) + i (b_y0 + ... + b_y3 t^3)</code>, and
<code>r = integral of w^2</code>. Degree 7, rational offsets, exact pitch and integer hits - the
same machinery as the quintic, one degree up.</p>
<div id="b-controls"></div>
<div class="trio">
<svg id="b-plot" viewBox="0 0 720 520" role="img" aria-label="the PH septic"></svg>
<svg id="b-chord-b1" viewBox="0 0 400 460" role="img" aria-label="chord terms B1, chained in two shapes"></svg>
<svg id="b-chord-b2" viewBox="0 0 400 460" role="img" aria-label="chord terms B2, the same terms as a fan"></svg>
</div>
<p class="small mono" id="b-terms-values" style="white-space:pre-line"></p>
<div class="solver-row">
  <button type="button" id="b-right">make the terms right-angled</button>
  <button type="button" id="b-close">close the chord</button>
</div>
<div class="save-row">
  <input id="b-name" type="text" placeholder="name this curve">
  <button type="button" id="b-save">save this curve</button>
  <button type="button" id="b-download">download JSON</button>
</div>
<div class="saved-row" id="b-saved"></div>
<div class="paste-row">
  <textarea id="b-paste" rows="3" placeholder='paste a curve: {"name": "x", "speedX": [2,-3,3,0.5], "speedY": [2,-12,12,-0.5]} - or a whole {"curves": [...]} document'></textarea>
  <button type="button" id="b-load">load pasted JSON</button>
</div>
<p class="small mono" id="b-paste-status"></p>
<p class="small mono">current curve, ready to select and cut — the same shape the paste box and
<code>workbench/septic-curves.json</code> take:</p>
<textarea id="b-json" rows="11" readonly></textarea>
<p class="small mono" id="b-readout"></p>
<p class="small mono" id="b-grade"></p>
<p class="small mono" id="b-formula" style="white-space:pre-line"></p>
<p class="small">The two boxes beside the curve are the same seven chord terms, drawn two ways: <strong>B1</strong>
chains them head to tail and rings where the quintic ends, <strong>B2</strong> fans each term from the
origin so its own size and direction show. All three use the same scale, so a vector is the same
length in any box. The dashed arrows are the sums: quintic-only, and all seven.</p>
</section>

<section class="panel">
<h2>C | G2 Hermite interpolation at degree 7</h2>
<p>Two points, two tangent angles and two curvatures go in; a PH septic comes out and matches all
six. The curve is <code>r' = w^2</code> with <code>w</code> cubic - eight real unknowns for six
conditions, so the two that remain are spent on the fairest curve near the start. Drag the angles and
curvatures and watch the curve follow; the curvature circles are dashed.</p>
<div id="c-controls"></div>
<svg id="c-plot" viewBox="0 0 720 520" role="img" aria-label="G2 Hermite interpolation at degree 7"></svg>
<p class="small mono" id="c-readout"></p>
</section>

<section class="panel">
<h2>D | small integer speeds</h2>
<p>Forty curves found by scanning small integer speeds - every coefficient in
<code>[-2, 2]</code> exhaustively, then a random sweep of <code>[-4, 4]</code> - with the
inflection strictly inside, the speed path away from the origin, and the pitch read exactly. The
numbers above each curve are its <code>speedX</code> and <code>speedY</code>: type them into panel B
to take one apart.</p>
<div class="samples">__SAMPLES__</div>
</section>

<section class="panel">
<h2>What the difference costs</h2>
<p><strong>Panel A</strong> can make any degree-7 shape, including the even/odd split that a sextic
or septic control pair wants: the <code>t^6</code> term lifts the middle without skewing the ends,
the <code>t^7</code> term tilts one end against the other. What it cannot do is promise a rational
offset or an integer lattice.</p>
<p><strong>Panel B</strong> keeps those promises but has fewer knobs: a cubic speed is eight real
numbers, and the position degree-7 terms are not free - they are the square of the speed. The
trade is exactness for control.</p>
<p class="small">Generate: <code>.venv/bin/python scripts/ph_septic_sandbox.py</code> - page and
JavaScript both checked into scripts.</p>
</section>
</main>
__CURVES__
<script>
__PANELS__
</script>
</body></html>
"""


def build():
    import json
    curves = json.loads(CURVES.read_text())["curves"]
    import septic_samples
    samples = json.loads(SAMPLES.read_text())["curves"]
    grid = "".join(septic_samples.panel_svg(record) for record in samples)
    page = PAGE.replace("__SAMPLES__", grid)
    page = page.replace("__CURVES__", "<script>window.septicCurves = "
                        + json.dumps(curves, separators=(",", ":")) + ";</script>")
    OUT.write_text(page.replace("__PANELS__", MATH.read_text() + "\n" + PANELS.read_text()))
    print(OUT.relative_to(ROOT))


if __name__ == "__main__":
    build()
