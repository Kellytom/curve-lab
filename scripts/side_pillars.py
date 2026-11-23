"""The side pillar: a thin border pillar, one line per side.

    .venv/bin/python scripts/side_pillars.py
    open workbench/side-pillars.html

The operator, 2026-11-23: the top and bottom of an illustration border join
curve ends with glue curves; the sides are different — "thin thin pillars, with
some expression to the pillar itself, and with bases and capitals". The pillar
is a border, not architecture: about 48 diameters tall.

The drawing rule is one line per side: the outside edge only, no fill, with the
base and capital read as steps in that one line. The maths is
`workbench/side_pillars.js` — one implementation, shared by this page and its
tests. The spec is `state/SPEC-side-pillars-int.md`.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

INK, MUTED, GOLD, PAPER, RULE = "#2e2413", "#7b6c4e", "#c9a441", "#fffdf7", "#d8ccae"

PAGE = "side-pillars.html"


def slider(name: str, label: str, lo: int, hi: int, value: int, step: int = 1) -> str:
    return (
        f'<label class="ctl">{label}'
        f'<input id="sp-{name}" type="range" min="{lo}" max="{hi}" value="{value}" step="{step}">'
        f'<span class="val" id="sp-{name}-val"></span></label>'
    )


def default_svg() -> str:
    """The first paint: the same maths file, run once under Node.

    The page and the tests share one implementation, so the server's first
    paint cannot disagree with the browser's redraw (register 42's lesson).
    """
    script = (
        "const SP = require(process.argv[1]);"
        "process.stdout.write(SP.svgMarkup({}));"
    )
    out = subprocess.run(
        ["node", "-e", script, str(ROOT / "workbench" / "side_pillars.js")],
        capture_output=True, text=True, check=True,
    )
    return out.stdout


def defaults() -> dict:
    """The maths file's own defaults and limits: the sliders cannot disagree with
    the first paint (register 42: a page whose first paint and redraw differ)."""
    script = (
        "const SP = require(process.argv[1]);"
        "process.stdout.write(JSON.stringify({d: SP.DEFAULTS, l: SP.LIMITS}));"
    )
    out = subprocess.run(
        ["node", "-e", script, str(ROOT / "workbench" / "side_pillars.js")],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)


def page() -> str:
    d = defaults()
    dflt, lim = d["d"], d["l"]
    controls = "".join([
        slider("diameters", "height, in foot widths",
               lim["diameters"][0], lim["diameters"][1], dflt["diameters"]),
        slider("ratio", "top width, 1/100 foot",
               lim["ratio"][0], lim["ratio"][1], dflt["ratio"]),
        slider("swell", "swell, 1/100 foot", 0, 9, dflt["swell"]),
        slider("station", "swell station, 1/100 height",
               lim["station"][0], lim["station"][1], dflt["station"]),
        slider("base", "base height, 1/100 foot",
               lim["base"][0], lim["base"][1], dflt["base"], 5),
        slider("capital", "capital height, 1/100 foot",
               lim["capital"][0], lim["capital"][1], dflt["capital"], 5),
    ])

    first_paint = default_svg()
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Side pillar — the illustration border's two sides: draft A</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1080px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 20px}}
h2{{font:600 11px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.12em;
text-transform:uppercase;color:{MUTED};margin:28px 0 8px}}
.panel{{background:{PAPER};border:1px solid {RULE};padding:16px 18px;margin:0 0 20px}}
.art{{background:{PAPER};border:1px solid {RULE};padding:8px;margin:0 0 10px}}
.art svg{{display:block;width:100%;height:auto}}
.grid{{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:20px;align-items:start}}
@media(max-width:860px){{.grid{{grid-template-columns:minmax(0,1fr)}}}}
.controls{{display:grid;gap:10px;background:{PAPER};border:1px solid {RULE};padding:14px 16px}}
.ctl{{display:grid;grid-template-columns:1fr auto;gap:2px 10px;font:13px/1.4 ui-monospace,Menlo,monospace;color:{MUTED}}}
.ctl input{{grid-column:1 / span 2;width:100%}}
.val{{color:#b23a2b;font:13px ui-monospace,Menlo,monospace}}
.legend{{display:flex;gap:20px;flex-wrap:wrap;font:15px/1.4 ui-monospace,Menlo,monospace;
color:{MUTED};margin:10px 2px 0}}
.legend span{{display:inline-flex;gap:7px;align-items:center}}
.sw{{display:inline-block;width:24px;height:0;border-top:3px solid {INK}}}
.sw.g{{border-top:2px dashed {GOLD}}}
.sw.r{{border-top:1px solid #e8dfc9}}
.sw.t{{border-top:1px dotted #b9a97f}}
table.read{{width:100%;border-collapse:collapse;font:13px/1.5 ui-monospace,Menlo,monospace}}
table.read th,table.read td{{text-align:left;padding:6px 8px;border-bottom:1px solid #e4dcc6;vertical-align:top}}
table.read th{{color:{MUTED};font-weight:400}}
table.read td{{color:{INK};white-space:nowrap}}
#sp-notes{{font:12px/1.5 ui-monospace,Menlo,monospace;color:{MUTED};margin:8px 0 0}}
code{{font:12px ui-monospace,Menlo,monospace;background:#f2ead8;padding:1px 4px}}
</style></head><body>
<div class="draft-a" style="position:fixed;right:.75rem;bottom:.75rem;z-index:9999;background:#1b1b1b;color:#fff;font:12px/1.4 system-ui,sans-serif;padding:.35rem .6rem;border-radius:.25rem;opacity:.9">draft A</div>
<!-- hub-bar --><main>

<h1>Side pillar</h1>
<p class="lead">The border's sides are a pillar, not a joined curve: one thin
line per side, with a base, a swelling shaft and a capital. The top run is the
glue connector's job; it is dashed here as context.</p>

<div class="grid">
<div>
  <div class="art"><div id="sp-figure">{first_paint}</div></div>
  <div class="legend">
    <span><i class="sw"></i> the pillar, one line (outside edge only)</span>
    <span><i class="sw g"></i> the glue-connected run, for context</span>
    <span><i class="sw r"></i> model axes (ground and centre)</span>
    <span><i class="sw t"></i> the straight taper the shaft swells against</span>
  </div>
</div>
<div class="controls">
{controls}
  <p id="sp-notes"></p>
</div>
</div>

<h2>The numbers</h2>
<div class="panel"><table class="read"><tbody id="sp-readout"></tbody></table></div>

<h2>What the figure is</h2>
<div class="panel">
<p>The object is a <strong>pillar</strong> — a column with a base, a shaft and a
capital — drawn as its <strong>outside edge only</strong>. The line steps out at
the base, steps in to the foot of the shaft, follows a <strong>quadratic
Bézier</strong> up the shaft, and steps out again at the capital. There is no
second line and no fill: the field inside the border is empty paper.</p>
<p>The shaft is not a straight taper. It swells against the straight line from
foot to top — the classical <strong>entasis</strong> — and the swell sits at the
station you choose, a third of the height by default. The foot stays the widest
point of the shaft, so the swell is a bulge in the taper, not a barrel.</p>
<p>The swell is small beside the pillar's height: at the default 1/50 of the
foot on a 48-diameter pillar it is well under a pixel on screen. The dotted
line is the straight taper it is measured from; the number in the readout is the
measurement, and the figure is the proportion.</p>
<p>Thinness is the point. A Roman order is 7 to 10 diameters tall; this border
pillar is <strong>48</strong> diameters tall by default, and the page prints the
number so the proportion is read, not assumed. Every value is a ratio of whole
numbers; the readout prints fractions, and the sliders move in hundredths.</p>
<p class="note">Re-derive: <code>python scripts/side_pillars.py</code> ·
<code>node --test tests/js/side-pillars.test.js</code> ·
<code>python -m unittest tests.test_side_pillars</code></p>
</div>

</main>
<script src="side_pillars.js"></script>
<script>SidePillars.mount(document);</script>
</body></html>
'''


def main() -> int:
    out = ROOT / "workbench" / PAGE
    out.write_text(page(), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
