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

import json
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
main{max-width:1120px;margin:0 auto;padding:18px 20px 40px}
.eyebrow{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}
h1{font-size:24px;line-height:1.1;margin:0 0 4px}
h2{font-size:18px;margin:0 0 6px}
.panel{background:var(--paper);border:1px solid var(--rule);padding:12px 14px;margin:0 0 12px}
p{margin:0 0 6px}
code{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}
.small{font-size:13px;color:var(--muted)}
.mono{font:12px/1.5 ui-monospace,Menlo,monospace}
.spine-row{display:flex;gap:8px;align-items:center;margin:2px 0}
.spine-row>span{width:34px;color:#8a3b2a;font:13px ui-monospace,Menlo,monospace}
.spine-grid .spine-row{display:grid;grid-template-columns:repeat(2, minmax(0, 1fr));gap:6px;align-items:stretch}
/* the axis letter gets its own line, so the x row and the y row start level */
.spine-grid .spine-row>span:first-child{grid-column:1 / -1;width:auto;margin:2px 0 0}
.spine-cell{display:flex;flex-direction:row;align-items:center;gap:8px;flex:1;min-width:110px;font:11px ui-monospace,Menlo,monospace;color:var(--muted)}
.cell-inputs{display:flex;gap:6px;align-items:center;flex:1;min-width:0;flex-wrap:wrap}
.spine-grid .cell-inputs input[type=number]{width:auto;min-width:96px;max-width:176px;field-sizing:content;font:12px ui-monospace,Menlo,monospace;padding:2px 4px;font-variant-numeric:tabular-nums}
.spine-grid .cell-inputs input[type=range]{flex:1;min-width:80px;height:18px;accent-color:#8a1f1f}
.cell-inputs input[type=range].decade{flex:0 0 64px;min-width:64px;accent-color:#1f4f8a}
.cell-inputs input[type=range]::before{content:""}
.cell-inputs .sign{font:12px/1 ui-monospace,Menlo,monospace;padding:2px 5px;background:#fbf7ec;color:var(--ink);border:1px solid var(--rule);border-radius:2px;cursor:pointer}
.cell-inputs .sign:hover{background:#efe7d3}
.pair-grid{display:grid;grid-template-columns:auto 1fr 1fr;gap:6px 10px;align-items:center}
.pair-grid .axis-head{font:11px ui-monospace,Menlo,monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.pair-grid .power-label{font:11px ui-monospace,Menlo,monospace;color:#8a3b2a}
.pair-grid .spine-cell{min-width:0}
#n-compass{max-width:50%}
table.figures{border-collapse:collapse;margin:6px 0 10px;font:12px ui-monospace,Menlo,monospace}
table.figures th,table.figures td{border:1px solid var(--rule);padding:2px 10px;text-align:right}
table.figures th{color:var(--muted);font-weight:400;text-align:left}

.pair-boxes{display:block}
.box-head{display:flex;align-items:baseline;justify-content:space-between;gap:14px;flex-wrap:wrap}
.box-head h3{margin:0}
.solver-row.tight{margin:0;gap:10px}
#n-roots-box h3{margin:0 0 2px}
.group-rule{border:0;border-top:1px solid var(--rule);margin:18px 0 10px}
.group-head{margin:0 0 8px;font-size:16px;letter-spacing:.01em}
.roots-ruler{position:relative;margin:0 0 26px}
.ruler-strip{position:relative;height:146px;border-bottom:2px solid var(--ink)}
.ruler-strip + .ruler-strip{margin-top:8px}
.ruler-lower{cursor:crosshair}
.ruler-upper{cursor:default}
.ruler-strip .tick{position:absolute;bottom:0;width:1px;background:#b9ae97}
.ruler-strip .tick-label{position:absolute;transform:translateX(-50%);font-size:11px;color:#6b6152;white-space:nowrap}
.ruler-upper .tick{background:#cbbfa4}
.ruler-upper .tick-label{color:#8a7f68}
.ruler-strip .spot-count{position:absolute;top:0;transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;line-height:1;background:#fbf7ec;padding:0 2px;user-select:none}
.ruler-strip .spot-value{font:700 12px ui-monospace,Menlo,monospace;color:#8a1f1f;cursor:pointer;padding:0 3px}
.ruler-strip .spot-step{font:8px/1 ui-monospace,Menlo,monospace;color:#8a1f1f;background:none;border:0;padding:1px 3px;cursor:pointer}
.ruler-strip .spot-step:hover{color:#1f4f8a}
.ruler-strip .spot-count:hover{color:#1f4f8a}
.ruler-strip .spot{position:absolute;width:13px;height:13px;border-radius:50%;background:#2e2413;border:2px solid #fbf7ec;bottom:8px;transform:translateX(-50%);cursor:pointer;font-size:9px;color:#fbf7ec;text-align:center;line-height:13px}
.ruler-strip .spot:hover{background:#8a1f1f}
#n-square-ruler{height:74px;border-bottom:2px solid var(--ink);cursor:crosshair;margin:0 0 22px}
.curve-box{margin:10px 0;padding:8px 10px;border:1px solid var(--rule);background:#f7f1e2}
.curve-box.complement{border-style:dashed}
.curve-box h3{font-size:14px;margin:0 0 6px;display:flex;justify-content:space-between;gap:8px}
.curve-box h3 .small{font-weight:400;color:var(--muted)}
.curve-box .spine-row{grid-template-columns:1fr}
.scales,.steppers{display:inline-flex;gap:2px}
.scales button,.steppers button{font:10px/1 ui-monospace,Menlo,monospace;padding:2px 4px;
  background:#fbf7ec;color:var(--ink);border:1px solid var(--rule);border-radius:2px;cursor:pointer}
.scales button:hover,.steppers button:hover{background:#efe7d3}
.steppers button{padding:2px 3px}
.solver-row{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 6px}
.solver-row button.is-on{background:#2e2413;color:#fbf7ec;border-color:#2e2413}
.rung-row{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 8px}
.rung{font:11px/1.2 ui-monospace,Menlo,monospace;padding:4px 7px;background:#fbf7ec;color:var(--ink);border:1px solid var(--rule);border-radius:3px;cursor:pointer}
.rung.is-on{background:#2e2413;color:#fbf7ec;border-color:#2e2413}
button{transition:background .08s ease,transform .05s ease}
button:hover{background:#efe7d3}
button:active{background:#d9cba8;transform:translateY(1px)}
button[aria-pressed="true"]{background:#2e2413;color:#fbf7ec;border-color:#2e2413}
button[aria-pressed="true"]:hover{background:#463a24}
button:disabled{opacity:.45;cursor:not-allowed}
.solver-row button,.save-row button,.saved-row button{font:12px/1.2 ui-monospace,Menlo,monospace;padding:5px 9px;background:#fbf7ec;color:var(--ink);border:1px solid var(--rule);border-radius:3px;cursor:pointer}
.dial{display:flex;align-items:center;gap:6px;font:12px ui-monospace,Menlo,monospace;color:#8a3b2a}
.dial input[type=number]{width:64px;font:12px ui-monospace,Menlo,monospace;padding:2px 4px}
#n-open-slider{flex:1;min-width:120px;max-width:240px}
.save-row{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 6px}
.save-row input{font:12px ui-monospace,Menlo,monospace;padding:4px 8px;width:200px}
.saved-row{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 6px}
.saved-row .saved-item{display:inline-flex;gap:2px;align-items:center}
.saved-row .saved-remove{padding:2px 6px;color:#8a3b2a}
.paste-row{display:flex;gap:10px;align-items:flex-start;margin:0 0 6px}
.paste-row textarea{flex:1;min-height:64px;font:12px/1.4 ui-monospace,Menlo,monospace;padding:6px 8px;border:1px solid var(--rule);background:#fffdf7;color:var(--ink)}
#n-json{width:100%;font:12px/1.5 ui-monospace,Menlo,monospace;padding:6px 8px;border:1px solid var(--rule);background:#fffdf7;color:var(--ink);resize:vertical}
svg{width:100%;height:auto;display:block;border:1px solid var(--rule);background:var(--paper)}
.plot-legend{display:flex;flex-wrap:wrap;gap:16px;align-items:center;margin:10px 0 4px;font:15px/1.4 Georgia,serif;color:var(--ink)}
.legend-item{display:inline-flex;align-items:center;gap:8px}
.legend-rule{display:inline-block;width:26px;height:3px;border-radius:2px}
.plot-row{display:grid;grid-template-columns:minmax(0,1fr) 210px;gap:14px;align-items:start}
@media(max-width:760px){.plot-row{grid-template-columns:1fr}}
.plot-host{min-width:0}
#n-plot{width:100%;height:auto;display:block}
.hud{background:var(--paper);border:1px solid var(--rule);padding:10px 12px;font:12px/1.5 ui-monospace,Menlo,monospace}
.hud h4{margin:0 0 8px;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.hud-row{display:block;margin:0 0 8px}
.hud-row input[type=range]{width:100%}
.hud-row input[type=number]{width:100%}
.gallery{display:grid;grid-template-columns:repeat(2, minmax(0, 1fr));gap:16px}
.gallery figure>img{width:100%;height:auto;display:block;border:1px solid var(--rule);background:#fbf7ec}
.gallery .cell-tools{display:flex;gap:4px;align-items:center;margin:5px 0 0;flex-wrap:wrap}
.gallery .cell-tools button{font:10px/1 ui-monospace,Menlo,monospace;padding:4px 6px;background:#fbf7ec;color:#7b6c4e;border:1px solid var(--rule);border-radius:2px;cursor:pointer}
.gallery .cell-tools button:hover{background:#2e2413;color:#fbf7ec}
.gallery .gallery-star.starred{background:#2e2413;color:#fbf7ec;border-color:#2e2413}
.gallery .cell-archive{display:block;width:100%;margin:5px 0 0;font:10px/1 ui-monospace,Menlo,monospace;padding:4px 5px;background:#fbf7ec;color:#7b6c4e;border:1px solid var(--rule);border-radius:2px;cursor:pointer}
.gallery .cell-archive:hover{background:#2e2413;color:#fbf7ec}
.gallery .gallery-head{grid-column:1 / -1;margin:10px 0 0;font-size:20px;border-top:2px solid var(--ink);padding-top:8px}
.gallery .gallery-note{grid-column:1 / -1;margin:0 0 4px;color:var(--muted);font-size:14px;max-width:80ch}
@media(max-width:700px){.gallery{grid-template-columns:minmax(0, 1fr)}}
.gallery figure{margin:0;background:var(--paper);border:1px solid var(--rule);padding:8px}
.gallery figure.open{grid-column:1 / -1}
.more-grid{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:14px;align-items:start}
.more-figure{display:flex;gap:10px;flex-wrap:wrap;align-items:flex-start}
.more-figure svg{width:min(100%,340px);height:auto;max-height:260px}
.gallery figure.open>svg{display:none}
.gallery figure{position:relative}
.thumb-zoom{position:absolute;top:6px;right:6px;display:flex;gap:3px;z-index:2}
.thumb-zoom button{font:12px/1 ui-monospace,Menlo,monospace;padding:2px 5px;background:#fbf7ec;color:#2e2413;border:1px solid var(--rule);border-radius:2px;cursor:pointer}
.thumb-zoom button:hover{background:#efe7d3}
.gallery figure>svg{width:100%;height:auto;display:block;margin:0 auto}
.more-actions{min-width:0;display:flex;flex-direction:column;gap:6px}
.more-actions textarea{width:100%;font:11px ui-monospace,Menlo,monospace}
@media(max-width:820px){.more-grid{grid-template-columns:1fr}}
.gallery .gallery-open{display:block;width:100%;
  background:none;border:0;padding:0 0 6px;cursor:pointer;text-align:left}
.gallery .gallery-open>span{display:block}
.gallery .gallery-number{display:inline;font:10px/1.4 ui-monospace,Menlo,monospace;color:#8a3b2a;margin-right:8px}
.gallery .gallery-name{display:inline;font:12px/1.4 ui-monospace,Menlo,monospace;color:var(--ink);font-weight:600}
.gallery .gallery-metrics{font:11px/1.4 ui-monospace,Menlo,monospace;color:var(--muted)}
.gallery .gallery-tags{display:flex;gap:6px;align-items:baseline;flex-wrap:wrap;margin:2px 0 0}
.gallery .tag{font:10px/1.4 ui-monospace,Menlo,monospace;padding:0 4px;border:1px solid var(--rule);
  border-radius:2px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.gallery .more{margin:8px 0 0}
.gallery .pair-row{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:0 0 8px}
.gallery .pair-cell{margin:0;border:1px solid var(--rule);padding:6px}
.gallery .pair-cell figcaption{font:11px/1.3 ui-monospace,Menlo,monospace;color:var(--muted);margin:0 0 4px}
.gallery .more textarea{width:100%;font:11px/1.4 ui-monospace,Menlo,monospace;padding:6px 8px;
  border:1px solid var(--rule);background:#fffdf7;color:var(--ink);resize:vertical}
.gallery .more-row{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:8px 0 0}
.gallery .more-row button{font:11px/1.2 ui-monospace,Menlo,monospace;padding:4px 8px;background:#fbf7ec;
  color:var(--ink);border:1px solid var(--rule);border-radius:3px;cursor:pointer}
.gallery svg{border:0}
.gallery p{margin:6px 0 0}
</style></head><body><main>
<p class="eyebrow">curve-lab | PH curves | position degree 11</p>
<h1>The eleventh power and up</h1>
<p>The septic sandbox stops at position degree 7, where the speed <code>w</code> is cubic. This page is
the same machine one step up: <code>r' = w^2</code> with <code>w</code> of degree 5, so twelve speed
numbers and a position of degree <strong>2 &times; 5 + 1 = 11</strong>. The offsets stay rational, the
pitch is still the lcm of the integrated coefficients' denominators, and the closure algebra is
unchanged &mdash; more terms, same rules.</p>

<section class="panel">
<h2>A | the PH curve, from degree 11 up</h2>
<p>One row of numbers for <code>x</code> and one for <code>y</code>, from <code>t^0</code> upward.
Each rung adds one number per axis, so the position degree rises by two: 11 up to 29, with
12 to 30 numbers. Doubling the rows is what lets a fractional step reach the same top power:
at step 1/2, fifteen numbers per axis reach t^7. An even position degree cannot occur for polynomial speeds, so the
readout never prints one. A curve saved at a lower rung loads here unchanged: the new boxes are zero,
which leaves the shape alone. <code>close chord</code> drives the endpoint home; <code>close to &hellip;</code>
holds a chosen openness instead, because a fully closed curve has no chord and bend is arc over chord.</p>
<div class="solver-row" id="n-step-row">
  <label class="dial" for="n-step">exponent step
    <input id="n-step" type="range" min="0.05" max="2" step="any" value="1">
    <span class="mono" id="n-step-value">1</span></label>
  <button type="button" class="step-at" data-step="1">whole 1</button>
  <button type="button" class="step-at" data-step="0.5">&frac12;</button>
  <button type="button" class="step-at" data-step="0.3333333333333333">&#8531;</button>
  <button type="button" class="step-at" data-step="0.25">&frac14;</button>
  <span class="small">The step is yours: filling the rows from a suggestion or from the dots
  never changes it.</span>
</div>
<div class="rung-row" id="n-rungs" role="group" aria-label="choose the position degree">
  <button type="button" class="rung is-on" data-speed-degree="5">degree 11 &middot; 12 numbers</button>
  <button type="button" class="rung" data-speed-degree="6">degree 13 &middot; 14 numbers</button>
  <button type="button" class="rung" data-speed-degree="7">degree 15 &middot; 16 numbers</button>
  <button type="button" class="rung" data-speed-degree="8">degree 17 &middot; 18 numbers</button>
  <button type="button" class="rung" data-speed-degree="9">degree 19 &middot; 20 numbers</button>
  <button type="button" class="rung" data-speed-degree="10">degree 21 &middot; 22 numbers</button>
  <button type="button" class="rung" data-speed-degree="11">degree 23 &middot; 24 numbers</button>
  <button type="button" class="rung" data-speed-degree="12">degree 25 &middot; 26 numbers</button>
  <button type="button" class="rung" data-speed-degree="13">degree 27 &middot; 28 numbers</button>
  <button type="button" class="rung" data-speed-degree="14">degree 29 &middot; 30 numbers</button>
</div>
<div class="curve-box" id="n-primary-box">
  <div class="box-head">
    <h3>Primary curve <span class="small mono" id="n-primary-degree"></span>
      <span class="mono" id="n-curve-name" title="the name of the curve you are working on; select it to copy"
            style="user-select:text;background:#efe7d3;border:1px solid var(--rule);border-radius:3px;padding:0 4px">curve</span></h3>
  </div>
  <div class="spine-grid" id="n-controls"></div>
</div>
<div class="curve-box" id="n-roots-box">
  <h3>Build from flat spots: see note below</h3>
<div class="roots-ruler" id="n-roots-ruler" role="group" aria-label="flat spots along t: the top strip runs 0 to 1/2, the bottom strip is its mirror, 1 to 1/2 backwards">
  <div class="ruler-strip ruler-lower" title="0 at the left, 1/2 at the right: click to place a flat spot"></div>
  <div class="ruler-strip ruler-upper" title="the mirror: 1 at the left, 1/2 at the right; 1/19 sits under its partner, 18/19"></div>
</div>
<p class="small">Square fractions: <code>t = 1/k&sup2;</code>, the points where the half-power variable
<code>u = &radic;t</code> is a whole fraction <code>1/k</code>. Clicking one places a flat spot there.</p>
<div class="roots-ruler" id="n-square-ruler" role="group"
     aria-label="square fractions t = 1 over k squared, for k 2 to 13"></div>
  <div class="solver-row">
    <label class="small"><input type="checkbox" id="n-roots-mirror" checked> mirror about 1/2</label>
    <button type="button" id="n-roots-dots-fill" title="write the rows from the dots on the strip">fill from the dots</button>
    <button type="button" id="n-roots-undo">undo</button>
    <button type="button" id="n-roots-clear">clear</button>
    <span class="small" id="n-roots-count"></span>
  </div>
  <div class="solver-row">
    <label class="dial" for="n-roots-half">copies at 1/2
      <input id="n-roots-half" type="range" min="0" max="6" step="1" value="3">
      <span class="mono" id="n-roots-half-value">3</span></label>
    <label class="dial" for="n-bow-slider">bow
      <input id="n-bow-slider" type="range" min="-12" max="12" step="0.25" value="0"></label>
  </div>
  <div class="solver-row">
    <label class="dial" for="n-roots-preset">suggestion
      <select id="n-roots-preset">
        <option value="">choose one&hellip;</option>
        <option value="1/9, 1/2, 1/2, 1/2, 8/9|0|1">knot, cheapest grid &middot; 1/9, 1/2 x3, 8/9 &middot; bow 0 &middot; step 1</option>
        <option value="1/6, 1/2, 5/6|0|1">gentle S &middot; 1/6, 1/2, 5/6 &middot; bow 0 &middot; step 1</option>
        <option value="1/8, 1/2, 1/2, 1/2, 7/8|-2|1">wide knot &middot; 1/8, 1/2 x3, 7/8 &middot; bow &minus;2 &middot; step 1</option>
        <option value="1/12, 1/2, 1/2, 1/2, 11/12|4|1">leaning knot &middot; 1/12, 1/2 x3, 11/12 &middot; bow 4 &middot; step 1</option>
        <option value="1/2, 1/2, 1/2, 1/2, 1/2|0|1">flat stroke &middot; 1/2 x5 &middot; bow 0 &middot; step 1</option>
        <option value="1/6, 1/6, 1/2, 1/2, 5/6, 5/6|0|1">half-turn pair of pairs &middot; 1/6 doubled, 1/2 x2, 5/6 doubled</option>
        <option value="1/7, 1/5, 1/2, 4/5, 6/7|9|1">your find &middot; 1/7, 1/5, 1/2, 4/5, 6/7 &middot; bow 9 &middot; step 1</option>
        <option value="1/9, 1/2, 1/2, 1/2, 8/9|0|0.5">experiment: the same spots at step &frac12; &mdash; no mirror, a different curve</option>
      </select></label>
    <label class="dial" for="n-roots">flat spots <input id="n-roots" type="text" size="26" value="1/9, 1/2, 1/2, 1/2, 8/9"></label>
    <label class="dial" for="n-bow">bow <input id="n-bow" type="number" step="0.5" value="0"></label>
    <button type="button" id="n-roots-fill" title="multiply the flat spots out and write the rows">fill the numbers</button>
  </div>
  <p class="small mono" id="n-roots-status"></p>
</div>
<div class="plot-row" id="n-plot-row">
  <div class="plot-host"><svg id="n-plot" viewBox="0 0 900 380" role="img" aria-label="the PH curve"></svg></div>
  <aside class="hud" id="n-view-hud" aria-label="view controls">
    <h4>View</h4>
    <label class="hud-row" for="n-zoom">zoom
      <input id="n-zoom" type="range" min="-12" max="12" step="0.5" value="1" title="positive zooms in on the knot, negative pulls back">
    </label>
    <label class="hud-row" for="n-zoom-number">zoom
      <input id="n-zoom-number" type="number" step="0.5" value="1" style="width:5em" title="positive in, negative out"></label>
    <button type="button" id="n-zoom-detail"
            title="re-sample the curve at four times the current detail, so a zoomed view is a smooth line instead of a polyline; press again for four times more">recalculate at this zoom</button>
    <p class="small mono" id="n-zoom-detail-note">drawing 700 points</p>
    <p class="small" id="n-zoom-detail-fineprint">(not part of formula;
    <a href="ph-nth-exp-notes.html">see notes page</a>)</p>
    <button type="button" id="n-loop-only"
            title="draw only t 0.02 to 0.98: the two approach strokes at the ends carry a fifth to a half of the ink between them and are not part of the loop">loop only</button>
    <button type="button" id="n-whole-curve" title="draw t 0 to 1 again">whole curve</button>
    <button type="button" id="n-focus-knot-hud" aria-pressed="false"
            title="frame the knot instead of the whole curve; the same switch as the one under the figure">focus the knot</button>
    <label class="hud-row" for="n-focus-x">focus x
      <input id="n-focus-x" type="number" step="0.1" placeholder="x"></label>
    <label class="hud-row" for="n-focus-y">focus y
      <input id="n-focus-y" type="number" step="0.1" placeholder="y"></label>
    <button type="button" id="n-focus-here"
            title="frame this point, so a side inflection can be ignored; saved in the record as focus">focus here</button>
    <button type="button" id="n-focus-clear" title="go back to framing the whole curve">clear focus</button>
    <label class="hud-row" for="n-pan-x">pan x
      <input id="n-pan-x" type="range" min="-50" max="50" step="1" value="0"></label>
    <label class="hud-row" for="n-pan-x-number">pan x
      <input id="n-pan-x-number" type="number" step="0.1" value="0"></label>
    <label class="hud-row" for="n-pan-y">pan y
      <input id="n-pan-y" type="range" min="-50" max="50" step="1" value="0"></label>
    <label class="hud-row" for="n-pan-y-number">pan y
      <input id="n-pan-y-number" type="number" step="0.1" value="0"></label>
    <button type="button" id="n-view-reset" title="zoom 1, no pan, no rotation">reset the view</button>
    <h4>Turn</h4>
    <label class="hud-row" for="n-turn-q">half-angle tan
      <select id="n-turn-q">
        <option value="">choose&hellip;</option>
        <option value="1/2">1/2 &middot; axis slope &minus;3/4</option>
        <option value="1/3">1/3 &middot; axis slope &minus;4/3</option>
        <option value="1/4">1/4 &middot; axis slope &minus;15/8</option>
        <option value="1/5">1/5 &middot; axis slope &minus;12/5</option>
      </select></label>
    <button type="button" id="n-turn-apply"
            title="turn the rows so the mirror axis is Pythagorean; the original is not changed">turn the curve</button>
    <p class="small mono" id="n-turn-status"></p>
  </aside>
</div>
<div class="curve-box complement" id="n-complement-box">
  <h3>Complementary curve <span class="small mono" id="n-crossings"></span></h3>
  <div class="spine-grid" id="n-complement-controls"></div>
  <div class="solver-row">
    <label class="dial" for="n-comp-move-x">move x <input id="n-comp-move-x" type="number" step="0.1" value="0"></label>
    <label class="dial" for="n-comp-move-y">move y <input id="n-comp-move-y" type="number" step="0.1" value="0"></label>
    <label class="dial" for="n-comp-turn" title="turn the complementary curve about the spine's centre">turn <input id="n-comp-turn" type="number" step="15" value="0"></label>
    <button type="button" id="n-comp-hide" aria-pressed="false" title="draw the primary curve alone">hide the grey curve</button>
  </div>
  <div class="solver-row">
    <button type="button" id="n-comp-flip" title="swap the two rows: the same curve drawn across the origin">flip across</button>
    <button type="button" id="n-comp-upside" title="negate the y row: the same curve upside down">upside down</button>
    <button type="button" id="n-comp-reverse" title="run the same curve from its other end">reverse</button>
    <button type="button" id="n-comp-reset" title="the complementary curve becomes the spine, flipped across">reset to the spine</button>
  </div>
</div>
<p class="small mono" id="n-readout"></p>
<p class="small mono" id="n-grade"></p>
<p class="small mono" id="n-formula" style="white-space:pre-line"></p>
<hr class="group-rule">
<h3 class="group-head">Offset curves</h3>
<div class="solver-row">
  <label class="dial" for="n-d">d <input id="n-d" type="number" min="0" max="20" step="0.1" value="1.5"></label>
  <label class="dial" for="n-char-l">character + <input id="n-char-l" type="number" min="0" max="3" step="0.1" value="2"></label>
  <label class="dial" for="n-char-r">character &minus; <input id="n-char-r" type="number" min="0" max="3" step="0.1" value="2"></label>
  <label class="dial" for="n-prof">profile
    <select id="n-prof"><option value="bow">bow</option><option value="s">S</option><option value="taper">taper</option></select>
  </label>
</div>
<div class="solver-row">
  <label class="dial" for="n-shear">end shear <input id="n-shear" type="number" min="-10" max="10" step="0.1" value="0"></label>
  <label class="dial" for="n-hook">hook x <input id="n-hook" type="number" min="-10" max="10" step="0.1" value="0"></label>
  <label class="dial" for="n-hook-y">hook y <input id="n-hook-y" type="number" min="-10" max="10" step="0.1" value="0"></label>
</div>
<div class="solver-row">
  <button type="button" id="n-grid" title="scale the speeds by an integer until the pitch is smallest with the numbers under 6000">coarsest grid</button>
  <button type="button" id="n-rotate" title="view the whole figure turned by -45 degrees">rotate -45&deg;</button>
  <button type="button" id="n-rails" title="parallel offsets at +/- d">rails</button>
</div>
<hr class="group-rule">
<h3 class="group-head">Knot experiments</h3>
<div class="solver-row" id="n-arc-row">
  <label class="dial" for="n-arc-percent">keep the middle
    <input id="n-arc-percent" type="number" min="10" max="99" step="1" value="70"> % of the ink</label>
  <button type="button" id="n-arc-rebuild" title="cut in arc length, then rebuild the kept arc as exact rows">cut and rebuild</button>
  <span class="small">arc length belongs to the shape, not to <code>t</code></span>
</div>
<div class="solver-row" id="n-knot-experiments">
  <button type="button" id="n-cut-knot" title="restrict the drawing to the knot; the curve itself is unchanged">show only the knot</button>
  <button type="button" id="n-rebuild-span" title="rebuild the knot's span as a new curve: exact whole numbers, no legs left in the rows">rebuild without the legs</button>
  <button type="button" id="n-focus-knot" aria-pressed="false" title="frame the knot, not the whole stroke">focus the knot</button>
</div>
<hr class="group-rule">
<div class="solver-row" id="n-view-row">
  <button type="button" id="n-character" title="the same PH formula with the speed perturbed by its own next coefficient">character offsets</button>
  <button type="button" id="n-terminal-start" title="an arc terminal at the start">start terminal</button>
  <button type="button" id="n-terminal-end" title="an arc terminal at the end">end terminal</button>
  <label class="dial" for="n-t-from">t from <input id="n-t-from" type="number" step="0.05" value="0">
    <input id="n-t-from-slider" type="range" min="-10" max="10" step="0.05" value="0" title="drag the start of the window; the box takes any value"></label>
  <label class="dial" for="n-t-to">t to <input id="n-t-to" type="number" step="0.05" value="1">
    <input id="n-t-to-slider" type="range" min="-10" max="10" step="0.05" value="1" title="drag the end of the window; the box takes any value"></label>
  <label class="dial" for="n-end-x">end x <input id="n-end-x" type="number" step="0.05" value="0"></label>
  <label class="dial" for="n-end-y">end y <input id="n-end-y" type="number" step="0.05" value="0"></label>
  <button type="button" id="n-place-end" title="solve the top pair so the curve ends here; the rest of the curve barely moves">place the end</button>
</div>
<p class="small mono" id="n-width-readout"></p>
<div class="plot-legend" id="n-plot-legend" aria-label="legend of the plot"></div>


<p class="small">The offsets are parallel here: <code>r &plusmn; d n</code> with <code>d</code> constant.
<strong>Character offsets</strong> keeps the same construction but turns the speed a little at each
station &mdash; <code>g = w (1 + i &epsilon; b(t))</code> &mdash; and blends back to the parallel at both
ends, so the rail leaves and arrives at exactly <code>&plusmn; d</code> and bows in between. The two
<strong>character</strong> dials set how far each side bows (they can differ, which is what a serif
needs), the <strong>profile</strong> chooses the bow's shape (one swell, an S that crosses the parallel,
or a taper toward the end), <strong>end shear</strong> leans the rails along the tangent by the end, and
<strong>tail hook</strong> adds <code>h e^{i&phi;} t^5</code> to the speed itself, bending the last span
without leaving the PH family. The flare law and the serif foot are parked in
<a href="ph-nth-serif-notes.html">ph-nth-serif-notes.html</a>.</p>
</section>





<section class="panel">
<h2>B | solve, save, take away</h2>
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
  <input id="n-category" type="text" placeholder="category" value="S" size="6">
  <span class="small" title="DK is a double knot: two curves saved as one record. S is a single curve, saved on its own.">DK = double knot &middot; S = single</span>
  <input id="n-name" type="text" placeholder="name this curve">
  <button type="button" id="n-save" title="save both curves as one DK record">save the pair</button>
  <button type="button" id="n-save-primary" title="save only the dark curve, in the flat shape the other pages read">save primary only</button>
  <button type="button" id="n-download" title="write this curve to a file in your Downloads folder">download this curve</button>
  <button type="button" id="n-rename" title="rename the saved curve this one came from, or name it">rename</button>
</div>
<div class="saved-row" id="n-saved"></div>
<p class="small"><button type="button" id="n-download-all" title="write every saved curve to one JSON file, so a browser reset cannot lose them">download all saved curves</button>
<button type="button" id="n-export-everything" title="everything this browser holds — saved curves, the moved list and the star order — as one file to put back in the repo">export everything</button>
<button type="button" id="n-count-saved" title="how many are stored in this browser">count them</button>
<button type="button" id="n-undo-saved" title="put back the list as it was before the last save or delete">undo the last change</button>
<label class="small" title="read a list written by export everything, or by download all, back into this browser; names already here are kept as they are">restore a list
  <input id="n-import-list" type="file" accept="application/json,text/plain">
</label>
<span class="small mono" id="n-saved-count"></span></p>
<div class="paste-row">
  <textarea id="n-paste" rows="3" placeholder='paste a curve: {"name": "x", "speedX": [2,-5,6,1,0,0], "speedY": [4,-22,22,-2,0,0]} - or a whole {"curves": [...]} document'></textarea>
  <button type="button" id="n-load">load pasted JSON</button>
</div>
<p class="small mono" id="n-paste-status"></p>
<p class="small mono">current curve, ready to select and cut:</p>
<textarea id="n-json" rows="12" readonly></textarea>
</section>



<hr style="border:0;border-top:1px solid var(--rule);margin:26px 0 18px">
<section class="panel">
<h2>Note: how the flat spots build a curve</h2>
<p class="small">A <strong>flat spot</strong> is a <code>t</code> where the stroke runs dead horizontal.
List the ones you want, press the button, and the boxes below fill themselves: the row is the
polynomial those spots multiply out to. Mirror every spot about <code>1/2</code> &mdash; <code>1/9</code>
with <code>8/9</code>, <code>1/8</code> with <code>7/8</code> &mdash; and keep <code>1/2</code> for
itself, and the curve comes out exactly symmetric. That is the only way to get symmetry on purpose;
a random row almost never has it.</p>
<p class="small">What to choose: the <strong>outer pair makes the knot</strong> (two swings out and
back). <strong>Three copies of <code>1/2</code></strong> make the long flat middle that lets the stroke
cross itself; one copy is a gentle S, five copies is nearly a straight line and crosses nothing.
Five spots is the cheap degree-11 rung; six or more moves you up a rung, which the page does for you.
<strong>Bow</strong> leans the stroke sideways: 0 is straight, &plusmn;1 to 2 opens the loop,
&plusmn;4 folds it hard.</p>
<p class="small">Click <strong>low on the strip, beside the rule</strong>, to place a flat spot; click
the same place again for another copy (the dots stack at the top of the strip), and click a
<strong>dot</strong> to take that copy away.</p>

<h2>Gallery: the spines so far</h2>
<p class="small">Spine only, one cell per curve, two columns. Started with the first two curves made
here, then everything the septic sandbox and the quintic page already carried. Degree 7 curves are
padded with a zero pair, which changes nothing: the speed is the same polynomial.</p>
<div class="gallery" id="n-gallery"></div>
<div class="panel" id="n-order-panel">
  <h3>Starred order</h3>
  <p class="small">Star a curve and it rises to the top of the gallery; the arrows move it within
  the starred list until 1, 2, 3 are right. The order is kept in this browser and printed below
  to hand back.</p>
  <textarea id="n-order-box" rows="4" readonly></textarea>
  <p><button type="button" id="n-order-copy">copy the order</button>
     <span class="small mono" id="n-order-state"></span></p>
</div>
<div class="panel" id="n-archive-panel">
  <h3>Moved to notes</h3>
  <p class="small">Curves you cleared from the gallery. They are hidden here and listed below;
  hand the list back and they leave <code>found-curves.json</code> for the notes page.</p>
  <textarea id="n-archive-box" rows="4" readonly></textarea>
  <p><button type="button" id="n-archive-copy">copy the list</button>
     <button type="button" id="n-archive-undo">undo the last one</button>
     <span class="small mono" id="n-archive-state"></span></p>
</div>
</section>

<hr style="border:0;border-top:1px solid var(--rule);margin:26px 0 18px">
<section class="panel" id="n-formula-box">
<h2>How your numbers become the curve</h2>
<p>You type two rows of numbers. The <code>x</code> row is how fast the curve moves sideways. The
<code>y</code> row is how fast it moves up. Each number belongs to one power of <code>t</code>, and
<code>t</code> runs from the start of the curve (0) to the end (1). The first number is the plain
amount, the second is the amount that grows with <code>t</code>, the third with <code>t</code> squared,
and so on. <code>t^0</code> means <code>t</code> to the power zero, which is 1, so that first box is a
constant that holds at every <code>t</code>; it is not a value at the start. If only the first boxes are
filled the speed never changes, so the curve is a straight line: the later boxes are what bend it.</p>
<p>To get the curve, the speed is multiplied by itself, then added up from the start. Multiplying the
speed by itself is the step that makes these curves special: the direction comes out of the product,
and the length of the curve stays a whole number instead of a square root.</p>
<p>Multiplying a row by itself makes every number in the row meet every other number. Pairs that land
on the same power are added together, and dividing by the new power turns a speed into a position. So
the <code>t</code> term of the curve comes from just the two first numbers, the <code>t</code> squared
term from the first three, and so on.</p>
<pre class="mono">speed:        w(t) = p(t) + i q(t)      p is the x row, q is the y row
curve:        w(t) multiplied by itself, then added up from 0 to t

the t term of x     = x0*x0 - y0*y0
the t term of y     = 2 * x0 * y0
the next power      adds the next pair of numbers, divided by the new power</pre>
<p>How high the powers reach is set only by how many numbers you type. Six numbers per row reach
<code>t</code> to the fifth in the speed and <code>t</code> to the eleventh in the curve. Ten numbers
per row reach <code>t</code> to the ninth and <code>t</code> to the nineteenth. That is why the ladder
steps by two: the square of the speed always lands on an odd power.</p>
<h3 style="font-size:15px;margin:14px 0 4px">First, the plain arithmetic</h3>
<p class="small">Powers add when you multiply, and signs follow a simple rule. That is all the grid
below is doing.</p>
<svg viewBox="0 0 560 210" role="img" aria-label="a ladder of products: powers add when you multiply, and two minuses make a plus">
  <rect width="560" height="210" fill="#fbf7ec"/>
  <text x="12" y="20" font-size="11" fill="#7b6c4e">the pair</text>
  <text x="180" y="20" font-size="11" fill="#7b6c4e">the product</text>
  <text x="330" y="20" font-size="11" fill="#7b6c4e">why</text>
  <text x="12" y="52" font-size="14" fill="#2e2413">4 &#215; 4 = 16</text>
  <text x="180" y="52" font-size="13" fill="#2e2413">t^0 &#215; t^0 = t^0</text>
  <text x="330" y="52" font-size="12" fill="#7b6c4e">0 + 0 = 0</text>
  <text x="12" y="82" font-size="14" fill="#2e2413">4t &#215; 4 = 16t</text>
  <text x="180" y="82" font-size="13" fill="#2e2413">t^1 &#215; t^0 = t^1</text>
  <text x="330" y="82" font-size="12" fill="#7b6c4e">1 + 0 = 1</text>
  <text x="12" y="112" font-size="14" fill="#2e2413">2t &#215; 3t = 6t^2</text>
  <text x="180" y="112" font-size="13" fill="#2e2413">t^1 &#215; t^1 = t^2</text>
  <text x="330" y="112" font-size="12" fill="#7b6c4e">1 + 1 = 2</text>
  <text x="12" y="142" font-size="14" fill="#2e2413">&#8722;2 &#215; &#8722;2 = 4</text>
  <text x="180" y="142" font-size="13" fill="#2e2413">two minuses</text>
  <text x="330" y="142" font-size="12" fill="#7b6c4e">make a plus</text>
  <text x="12" y="172" font-size="14" fill="#2e2413">&#8722;2 &#215; &#8722;2 &#215; &#8722;2 = &#8722;8</text>
  <text x="180" y="172" font-size="13" fill="#2e2413">three minuses</text>
  <text x="330" y="172" font-size="12" fill="#7b6c4e">leave a minus</text>
  <text x="12" y="198" font-size="11" fill="#8a3b2a">the x term of the curve is x0&#215;x0 &#8722; y0&#215;y0, so these signs decide which way it sets off</text>
  <text x="548" y="14" font-size="10" fill="#7b6c4e" text-anchor="end">Fig. E1</text>
</svg>
<h3 style="font-size:15px;margin:14px 0 4px">Which numbers meet</h3>
<p class="small">Every number in the x row is multiplied by every other, and the cell shows the
product. Cells on the same diagonal add up to one power of the curve: the corner cell alone makes the
<code>t</code> term, the next diagonal makes the <code>t</code> squared term, and so on. The small
number in each corner is that diagonal. The y row does the same sum, and it is subtracted.</p>
<svg id="n-pair-table" viewBox="0 0 560 470" role="img"
     aria-label="a grid of products of the x numbers; cells on one diagonal add to one power of the curve"></svg>

<h3 style="font-size:15px;margin:14px 0 4px">Why the length has no square root</h3>
<p class="small">The length of an ordinary curve needs a square root, and the root rarely comes out
clean. Here the two speeds are a matched pair, so the root cancels exactly and the length is a plain
polynomial.</p>
<svg id="n-length" viewBox="0 0 560 190" role="img"
     aria-label="a triangle whose hypotenuse is a square root, beside the same triangle where the root cancels"></svg>
<p class="small mono" id="n-length-exact"></p>
<h3 style="font-size:15px;margin:14px 0 4px">Which box does what</h3>
<p>The low boxes set the start and the frame. The high boxes set the end. Changing the top x box by
one moves the beginning of the curve by about a hundredth of a unit and the end by about a whole unit,
so the top boxes are where you place the arm that has to meet the next curve. These numbers were
measured on the default curve by changing one box by one and seeing how far the curve moved:</p>
<table class="figures">
<tr><th>box changed</th><th>start moved</th><th>end moved</th></tr>
<tr><td>t^0</td><td>1.80</td><td>4.51</td></tr>
<tr><td>t^3</td><td>0.05</td><td>1.43</td></tr>
<tr><td>t^5</td><td>0.01</td><td>1.06</td></tr>
</table>
<p>A high box also makes the arm longer: the last tenth of the curve measured 1.43 long by default,
2.05 with the top x box at 1, and 3.66 with it at 3. But a high box does not make the curve smaller by
itself &mdash; it reshapes the end. It can shrink the whole curve only if you pull the end back with the
opposite sign, which is a choice you make, not something the box does.</p>
<h3 style="font-size:15px;margin:14px 0 4px">The start heading</h3>
<p class="small">The first pair sets the heading, and the heading is <strong>twice</strong> the angle of
that pair. So a pair and its negative give the same heading &mdash; only the speed differs. The dark
arrow is the curve on this page; it moves as you change the first boxes.</p>
<svg id="n-compass" viewBox="0 0 340 340" role="img"
     aria-label="a compass of start headings: 0 degrees from 1,0; 90 from 1,1; 180 from 0,1; 270 from 1,-1"></svg>
<p class="small">The example below is read from the numbers on the page right now.</p>
<pre class="mono" id="n-formula-explain"></pre>
</section>
</main>
<script>
window.phNthGallery = __GALLERY__;
window.phSpeedDegree = 5;
// The rung buttons: one number per axis per rung, so the degree moves by two.
(() => {
  const rungs = [...document.querySelectorAll("#n-rungs .rung")];
  // the page may ask for a rung other than the first one
  rungs.forEach(button => button.classList.toggle("is-on",
    Number(button.dataset.speedDegree) === window.phSpeedDegree));
  rungs.forEach(button => button.addEventListener("click", () => {
    window.phNthSetDegree(button.dataset.speedDegree);
    rungs.forEach(other => other.classList.toggle("is-on", other === button));
  }));
})();
</script>
<script src="ph_math.js"></script>
<script src="ph_nth_panels.js"></script>
<p class="small mono" id="n-build">build __BUILD__</p>
</body></html>
"""


def gallery():
    """The spines the gallery starts from, in order: the first two made here,
    then the septic set, then the quintic page's cases."""
    import json
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import ph_quintic_metrics as metrics

    named_path = ROOT / "workbench" / "septic-curves.json"
    document = json.loads(named_path.read_text())
    by_name = {curve["name"]: curve for curve in document["curves"]}
    first = ["integer-105", "integer-70"]
    order = [name for name in first if name in by_name]
    order += [curve["name"] for curve in document["curves"] if curve["name"] not in order]
    entries = []
    for name in order:
        curve = by_name[name]
        entries.append({
            "name": name,
            "speedX": (curve["speedX"] + [0] * 6)[:6],
            "speedY": (curve["speedY"] + [0] * 6)[:6],
            "bend": curve["bend"],
            "pitch": curve["pitch"],
            "from": "septic",
        })
    for name, sx, sy in [
        ("quintic u=1+2t+t^2, v=1-t+t^2", (1, 2, 1, 0, 0, 0), (1, -1, 1, 0, 0, 0)),
        ("quintic u=1+t^2, v=2t", (1, 0, 1, 0, 0, 0), (0, 2, 0, 0, 0, 0)),
    ]:
        m = metrics.metrics(sx, sy)
        entries.append({"name": name, "speedX": list(sx), "speedY": list(sy),
                        "bend": round(m["bend"], 3), "pitch": m["pitch"], "from": "quintic"})
    return entries


def stamped(page):
    """Put the build time in the footer, so a stale copy is visible at a glance."""
    import datetime
    return page.replace("__BUILD__", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))


def build():
    page = PAGE.replace("__GALLERY__", json.dumps(gallery(), separators=(",", ":")))
    OUT.write_text(stamped(page))
    import stamp_draft
    stamp_draft.stamp_file(OUT)
    print(OUT.relative_to(ROOT))


if __name__ == "__main__":
    build()
