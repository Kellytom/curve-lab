"""The eleventh power: a PH curve whose position is degree 11.

    .venv/bin/python scripts/ph_nth_sandbox.py
    open workbench/ph-nth-sandbox.html

The septic page stops at position degree 7 (w cubic). This one is the same
sandbox one step up: w of degree 5, twelve speed numbers, position degree
2*5 + 1 = 11. The degree is the only thing that changed, which is the point -
if the machinery is right, the next power is a constant, not a rewrite.

The page is generated: edit this file or scripts/ph_nth_panels.js, never the
HTML.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "ph-nth-sandbox.html"
PANELS = ROOT / "scripts" / "ph_nth_panels.js"
MATH = ROOT / "scripts" / "ph_math.js"

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The eleventh power: a PH curve of degree 11</title>
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
.small{font-size:13px;color:var(--muted)}
.mono{font:12px/1.5 ui-monospace,Menlo,monospace}
.spine-row{display:flex;gap:10px;align-items:center;margin:4px 0}
.spine-row>span{width:34px;color:#8a3b2a;font:13px ui-monospace,Menlo,monospace}
#n-controls .spine-row{flex-direction:column;align-items:stretch;gap:6px}
.spine-cell{display:flex;flex-direction:row;align-items:center;gap:8px;flex:1;min-width:110px;font:11px ui-monospace,Menlo,monospace;color:var(--muted)}
.cell-inputs{display:flex;gap:6px;align-items:center;flex:1}
#n-controls .cell-inputs input[type=number]{width:auto;min-width:96px;max-width:176px;field-sizing:content;font:12px ui-monospace,Menlo,monospace;padding:2px 4px;font-variant-numeric:tabular-nums}
#n-controls .cell-inputs input[type=range]{flex:1;min-width:36px}
#n-controls .cell-inputs input[type=range].decade{flex:0 0 64px;min-width:64px}
.solver-row{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 12px}
.solver-row button.is-on{background:#2e2413;color:#fbf7ec;border-color:#2e2413}
.solver-row button,.save-row button,.saved-row button{font:12px/1.2 ui-monospace,Menlo,monospace;padding:5px 9px;background:#fbf7ec;color:var(--ink);border:1px solid var(--rule);border-radius:3px;cursor:pointer}
.dial{display:flex;align-items:center;gap:6px;font:12px ui-monospace,Menlo,monospace;color:#8a3b2a}
.dial input[type=number]{width:64px;font:12px ui-monospace,Menlo,monospace;padding:2px 4px}
#n-open-slider{flex:1;min-width:120px;max-width:240px}
.save-row{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 8px}
.save-row input{font:12px ui-monospace,Menlo,monospace;padding:4px 8px;width:200px}
.saved-row{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 12px}
.paste-row{display:flex;gap:10px;align-items:flex-start;margin:0 0 6px}
.paste-row textarea{flex:1;min-height:64px;font:12px/1.4 ui-monospace,Menlo,monospace;padding:6px 8px;border:1px solid var(--rule);background:#fffdf7;color:var(--ink)}
#n-json{width:100%;font:12px/1.5 ui-monospace,Menlo,monospace;padding:6px 8px;border:1px solid var(--rule);background:#fffdf7;color:var(--ink);resize:vertical}
svg{width:100%;height:auto;display:block;border:1px solid var(--rule);background:var(--paper)}
</style></head><body><main>
<p class="eyebrow">curve-lab | PH curves | position degree 11</p>
<h1>The eleventh power</h1>
<p>The septic sandbox stops at position degree 7, where the speed <code>w</code> is cubic. This page is
the same machine one step up: <code>r' = w^2</code> with <code>w</code> of degree 5, so twelve speed
numbers and a position of degree <strong>2 &times; 5 + 1 = 11</strong>. The offsets stay rational, the
pitch is still the lcm of the integrated coefficients' denominators, and the closure algebra is
unchanged &mdash; more terms, same rules.</p>

<section class="panel">
<h2>A | the PH curve of degree 11</h2>
<p>Six numbers for <code>x</code> and six for <code>y</code>, from <code>t^0</code> to <code>t^5</code>.
The last pair is zero by default, which makes the curve a septic with two unused knobs: lift it and the
eleventh power appears. <code>close chord</code> drives the endpoint home; <code>close to &hellip;</code>
holds a chosen openness instead, because a fully closed curve has no chord and bend is arc over chord.</p>
<div id="n-controls"></div>
<svg id="n-plot" viewBox="0 0 720 520" role="img" aria-label="the PH curve of degree 11"></svg>
<p class="small mono" id="n-readout"></p>
<p class="small mono" id="n-grade"></p>
<p class="small mono" id="n-formula" style="white-space:pre-line"></p>
<div class="solver-row">
  <label class="dial" for="n-d0">d0 <input id="n-d0" type="number" min="0.02" max="4" step="0.01" value="0.35"></label>
  <label class="dial" for="n-k">k <input id="n-k" type="number" min="0" max="8" step="0.05" value="1.2"></label>
  <label class="dial" for="n-p">p <input id="n-p" type="number" min="1" max="8" step="1" value="2"></label>
</div>
<div class="solver-row">
  <button type="button" id="n-rails" title="show or hide the two flared rails">rails</button>
  <button type="button" id="n-terminal-start" title="an arc terminal at the start">start terminal</button>
  <button type="button" id="n-terminal-end" title="an arc terminal at the end">end terminal</button>
</div>
<p class="small mono" id="n-width-readout"></p>
<p class="small">A serif foot as a PH appendix is parked:
<a href="ph-nth-serif-notes.html">ph-nth-serif-notes.html</a> holds that code, the button and its
residual, so it can be picked up later without carrying it on this page.</p>
</section>



<section class="panel">
<h2>B | the eleven chord terms</h2>
<p>One row per position power, <code>x</code> above <code>y</code>, on a shared zero line. The first six
rows are what a sextic can hold; the rest exist only because the position reaches <code>t^11</code>.
The numbers are in the panel above and in the JSON box below.</p>
<svg id="n-bars" viewBox="0 0 720 460" role="img" aria-label="the eleven chord terms as signed bars"></svg>
</section>

<section class="panel">
<h2>C | solve, save, take away</h2>
<div class="solver-row">
  <button type="button" id="n-close">close chord</button>
  <button type="button" id="n-open" title="solve until |chord| / arc reaches the dial">close to &hellip;</button>
  <label class="dial" for="n-open-value">openness
    <input id="n-open-value" type="number" min="0.02" max="1" step="0.01" value="0.25">
  </label>
  <input id="n-open-slider" type="range" min="0.02" max="1" step="0.01" value="0.25" aria-label="target openness">
  <button type="button" id="n-zero-top" title="set x t^5 and y t^5 to zero: back to a septic">zero the top pair</button>
</div>
<div class="save-row">
  <input id="n-name" type="text" placeholder="name this curve">
  <button type="button" id="n-save">save this curve</button>
</div>
<div class="saved-row" id="n-saved"></div>
<div class="paste-row">
  <textarea id="n-paste" rows="3" placeholder='paste a curve: {"name": "x", "speedX": [2,-5,6,1,0,0], "speedY": [4,-22,22,-2,0,0]} - or a whole {"curves": [...]} document'></textarea>
  <button type="button" id="n-load">load pasted JSON</button>
</div>
<p class="small mono" id="n-paste-status"></p>
<p class="small mono">current curve, ready to select and cut:</p>
<textarea id="n-json" rows="12" readonly></textarea>
</section>

<section class="panel">
<h2>What the eleventh power costs</h2>
<p>Every extra degree adds one speed pair and two position powers. The closure condition stays two
equations, so the closed family grows by two dimensions per degree &mdash; more room for loops, which is
what the septic already showed over the quintic. The price is the pitch: the integrated coefficients
carry <code>1/(k+1)</code> and the squares of the decimal denominators, so the integer scale climbs
faster than the shape count. The low-pitch form of each saved curve is the same shape on a coarser
grid; it is a change of units, not a new curve.</p>
<p>The flare is the reason for this page: a serif is a width story, not a curvature story. The rail
distance is a declared number, and the terminal radius is twice it, so flare, terminal and foot are one
number apart rather than three drawings agreeing by eye.</p>
<p class="small">Generate: <code>.venv/bin/python scripts/ph_nth_sandbox.py</code> &mdash; the page and
<code>scripts/ph_nth_panels.js</code> are both checked in.</p>
</section>
</main>
<script>
__MATH__
</script>
<script>
__PANELS__
</script>
</body></html>
"""


def build():
    page = PAGE.replace("__MATH__", MATH.read_text()).replace("__PANELS__", PANELS.read_text())
    OUT.write_text(page)
    print(OUT.relative_to(ROOT))


if __name__ == "__main__":
    build()
