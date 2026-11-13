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
#n-controls .spine-row{display:grid;grid-template-columns:1fr 1fr;gap:6px;align-items:stretch}
.spine-cell{display:flex;flex-direction:row;align-items:center;gap:8px;flex:1;min-width:110px;font:11px ui-monospace,Menlo,monospace;color:var(--muted)}
.cell-inputs{display:flex;gap:6px;align-items:center;flex:1}
#n-controls .cell-inputs input[type=number]{width:auto;min-width:96px;max-width:176px;field-sizing:content;font:12px ui-monospace,Menlo,monospace;padding:2px 4px;font-variant-numeric:tabular-nums}
#n-controls .cell-inputs input[type=range]{flex:1;min-width:36px}
#n-controls .cell-inputs input[type=range]{flex:1;min-width:36px}
.scales,.steppers{display:inline-flex;gap:2px}
.scales button,.steppers button{font:10px/1 ui-monospace,Menlo,monospace;padding:2px 4px;
  background:#fbf7ec;color:var(--ink);border:1px solid var(--rule);border-radius:2px;cursor:pointer}
.scales button:hover,.steppers button:hover{background:#efe7d3}
.steppers button{padding:2px 3px}
.solver-row{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 6px}
.solver-row button.is-on{background:#2e2413;color:#fbf7ec;border-color:#2e2413}
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
#n-plot{max-height:60vh}
.gallery{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:700px){.gallery{grid-template-columns:1fr}}
.gallery figure{margin:0;background:var(--paper);border:1px solid var(--rule);padding:8px}
.gallery figure.open{grid-column:1 / -1}
.gallery .gallery-open{display:flex;justify-content:space-between;gap:8px;width:100%;
  background:none;border:0;padding:0 0 6px;cursor:pointer;text-align:left}
.gallery .gallery-name{font:12px/1.4 ui-monospace,Menlo,monospace;color:var(--ink);font-weight:600}
.gallery .gallery-metrics{font:11px/1.4 ui-monospace,Menlo,monospace;color:var(--muted)}
.gallery .gallery-tags{display:inline-flex;gap:6px;align-items:baseline}
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
  <button type="button" id="n-character" title="the same PH formula with the speed perturbed by its own next coefficient">character offsets</button>
  <button type="button" id="n-terminal-start" title="an arc terminal at the start">start terminal</button>
  <button type="button" id="n-terminal-end" title="an arc terminal at the end">end terminal</button>
</div>
<p class="small mono" id="n-width-readout"></p>
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
  <button type="button" id="n-rename" title="rename the saved curve this one came from, or name it">rename</button>
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

<hr style="border:0;border-top:1px solid var(--rule);margin:26px 0 18px">
<section class="panel">
<h2>Gallery: the spines so far</h2>
<p class="small">Spine only, one cell per curve, two columns. Started with the first two curves made
here, then everything the septic sandbox and the quintic page already carried. Degree 7 curves are
padded with a zero pair, which changes nothing: the speed is the same polynomial.</p>
<div class="gallery" id="n-gallery"></div>
</section>
</main>
<script>
window.phNthGallery = __GALLERY__;
</script>
<script>
__MATH__
</script>
<script>
__PANELS__
</script>
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


def build():
    page = PAGE.replace("__GALLERY__", json.dumps(gallery(), separators=(",", ":"))).replace("__MATH__", MATH.read_text()).replace("__PANELS__", PANELS.read_text())
    OUT.write_text(page)
    print(OUT.relative_to(ROOT))


if __name__ == "__main__":
    build()
