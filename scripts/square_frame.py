"""The interactive square/rectangle lab: controls, and a page that draws live.

    .venv/bin/python scripts/square_frame.py

Writes `workbench/square-frame.html`. The geometry lives in
`workbench/square_lab.js` (the same file the page loads); this generator writes
only the shell, the controls and the app that wires them. Squares and
rectangles only: the leg rule is 45° because the corner is 90°.

The page measures in points (1/72 in). The stroke is `SquareLab.strokeFor`, so
it is 1 point at every print size from 1 to 4 inches.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

OUT = ROOT / "workbench" / "square-frame.html"

APP = r"""
const $ = (id) => document.getElementById(id);
const stage = $("sf-stage");
const readout = $("sf-readout");

function show(id, value) {
  const el = $(id + "-v");
  if (el) el.textContent = value;
}

function draw() {
  const a = SquareLab.CURVES[$("sf-a").value].points;
  const b = SquareLab.CURVES[$("sf-b").value].points;
  const perW = Number($("sf-per-w").value);
  const perH = Number($("sf-per-h").value);
  const pattern = $("sf-pattern").value;
  const leg = Number($("sf-leg").value);
  const sizeIn = Number($("sf-size").value);
  const fill = Number($("sf-fill").value);
  const alternate = $("sf-alternate").checked;
  const showFrame = $("sf-frame").checked;
  const showLeaf = $("sf-leaf").checked;

  show("sf-per-w", perW);
  show("sf-per-h", perH);
  show("sf-leg", leg + "°");
  show("sf-size", sizeIn.toFixed(2) + " in");
  show("sf-fill", Math.round(fill * 100) + "%");

  const L = SquareLab.chord(a);
  const boxW = perW * L;
  const boxH = perH * L;
  const frame = showFrame
    ? SquareLab.frameRect(a, b, perW, perH, leg, pattern, alternate)
    : { W: boxW, H: boxH, curves: [] };

  let leafCurves = [];
  let tips = null;
  if (showLeaf) {
    const leaf = SquareLab.central(a, b, leg);
    tips = leaf.tips;
    const cx = boxW / 2 - leaf.feet / 2;
    const cy = boxH / 2;
    leafCurves = leaf.curves.map((curve) => ({
      ...curve,
      points: curve.points.map(([x, y]) => [x + cx, y + cy]),
    }));
  }

  const all = frame.curves.concat(leafCurves);
  if (!all.length) {
    stage.innerHTML = "";
    readout.textContent = "nothing to draw";
    return;
  }

  const W = sizeIn * 72;
  const H = W;
  const margin = W * 0.06;
  const [x0, y0, x1, y1] = SquareLab.bbox(all);
  const k = Math.min((W - 2 * margin) / (x1 - x0), (H - 2 * margin) / (y1 - y0)) * fill;
  const ox = (W - (x1 - x0) * k) / 2 - x0 * k;
  const oy = (H - (y1 - y0) * k) / 2 - y0 * k;
  const toSvg = ([x, y]) => [ox + x * k, H - (oy + y * k)];
  const stroke = SquareLab.strokeFor(W);

  stage.setAttribute("viewBox", `0 0 ${W} ${H}`);
  stage.setAttribute("width", W);
  stage.setAttribute("height", H);

  const line = (points, colour) => {
    const text = points.map((p) => toSvg(p).map((v) => v.toFixed(2)).join(",")).join(" ");
    return `<polyline points="${text}" fill="none" stroke="${colour}" `
      + `stroke-width="${stroke.toFixed(2)}" stroke-linecap="round" `
      + `stroke-linejoin="round"/>`;
  };
  stage.innerHTML =
    frame.curves.map((c) => line(SquareLab.sample(c.points, 120), "#2e2413")).join("")
    + leafCurves.map((c) => line(SquareLab.sample(c.points, 120), "#7b6c4e")).join("");

  const parts = [];
  parts.push(`box ${((frame.W * k) / 72).toFixed(2)} × ${((frame.H * k) / 72).toFixed(2)} in`);
  parts.push(`copy ${((L * k) / 72).toFixed(2)} in`);
  parts.push(`stroke ${stroke.toFixed(2)} pt`);
  if (showFrame) {
    const joins = SquareLab.distinctKinks(SquareLab.ringKinks(frame.curves)).join(" / ");
    parts.push(`${frame.curves.length} frame curves · joins ${joins}°`);
  }
  if (tips) {
    parts.push(`leaf tips ${Math.round(tips.left)}° / ${Math.round(tips.right)}°`);
  }
  readout.textContent = parts.join(" · ");
}

["sf-a", "sf-b", "sf-per-w", "sf-per-h", "sf-pattern", "sf-leg",
 "sf-size", "sf-fill", "sf-alternate", "sf-frame", "sf-leaf"].forEach((id) => {
  $(id).addEventListener("input", draw);
});
draw();
"""


def page_html() -> str:
    curves = [
        ("arch-345", "arch 3-4-5"),
        ("s-345", "S 3-4-5"),
        ("arch-5-12-13", "arch 5-12-13"),
        ("s-5-12-13", "S 5-12-13"),
    ]
    options = "".join(f'<option value="{value}">{label}</option>'
                      for value, label in curves)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Square and frame lab</title>
<style>
body{{margin:0;background:#f6f1e4;color:#2e2413;font:15px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:28px 22px 60px}}
h1{{font-size:24px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 20px}}
.wrap{{display:grid;grid-template-columns:300px minmax(0,1fr);gap:22px;align-items:start}}
.controls{{background:#fffdf7;border:1px solid #d8ccae;padding:14px 16px}}
.controls label{{display:block;margin:0 0 13px;font-size:13px}}
.controls .row{{display:flex;justify-content:space-between;align-items:baseline;gap:8px}}
.controls input[type=range]{{width:100%;margin:4px 0 0}}
.controls select,.controls input[type=text]{{width:100%;padding:4px;
  font:13px ui-monospace,Menlo,monospace;border:1px solid #d8ccae;background:#fff}}
.controls .check{{display:flex;gap:8px;align-items:center}}
.stage{{background:#fff;border:1px solid #d8ccae;padding:8px}}
.stage svg{{display:block;width:100%;height:auto}}
#sf-readout{{font:11px/1.5 ui-monospace,Menlo,monospace;color:#555;margin:0 0 8px}}
.note{{font-size:12px;color:#7b6c4e;margin-top:16px}}
code{{font:12px ui-monospace,Menlo,monospace}}
</style></head><body><main>
<h1>Square and frame lab</h1>
<p class="lead">Squares and rectangles only. One rule: the leg bisects the
90° corner, so it is 45°. An arch joins continuously; an S joins at a right
angle. The frame and the leaf are built separately and only share the page.</p>

<div class="wrap">
<div class="controls">
  <label>curve a
    <select id="sf-a">{options}</select>
  </label>
  <label>curve b
    <select id="sf-b">{options}</select>
  </label>
  <label>
    <span class="row"><span>curves across</span><b id="sf-per-w-v">2</b></span>
    <input id="sf-per-w" type="range" min="1" max="6" step="1" value="2">
  </label>
  <label>
    <span class="row"><span>curves down</span><b id="sf-per-h-v">3</b></span>
    <input id="sf-per-h" type="range" min="1" max="6" step="1" value="3">
  </label>
  <label>frame pattern (a/b)
    <input id="sf-pattern" type="text" value="aba" maxlength="8" spellcheck="false">
  </label>
  <label>
    <span class="row"><span>leg angle</span><b id="sf-leg-v">45°</b></span>
    <input id="sf-leg" type="range" min="20" max="70" step="1" value="45">
  </label>
  <label>
    <span class="row"><span>print size</span><b id="sf-size-v">4.00 in</b></span>
    <input id="sf-size" type="range" min="1" max="4" step="0.25" value="4">
  </label>
  <label>
    <span class="row"><span>frame fills</span><b id="sf-fill-v">100%</b></span>
    <input id="sf-fill" type="range" min="0.5" max="1" step="0.05" value="1">
  </label>
  <label class="check"><input id="sf-alternate" type="checkbox">
    flip every other copy</label>
  <label class="check"><input id="sf-frame" type="checkbox" checked>
    show the frame</label>
  <label class="check"><input id="sf-leaf" type="checkbox" checked>
    show the leaf</label>
</div>
<div>
  <div id="sf-readout">…</div>
  <div class="stage"><svg id="sf-stage" viewBox="0 0 288 288" role="img"
    aria-label="square or rectangular frame and a central leaf"></svg></div>
</div>
</div>

<p class="note"><strong>The leaf</strong> is curve a below and curve b above,
flipped, with the feet forced onto the same two points. The tip angles are
printed: 90° / 90° means the two curves meet cleanly at both feet; a mismatch
(e.g. 90° / 0°) means one foot is smooth and the other is square, which is the
attach problem to watch.</p>
<p class="note">The stroke floor is <strong>1 point</strong> at every size:
the page measures in points, and <code>strokeFor</code> never returns less. The
box is <code>curves across × the chord</code> by <code>curves down × the
chord</code>, so 2 × 3 gives a tall frame. The pattern cycles a/b along each
side.</p>
<p class="note">Re-derive: <code>python scripts/square_frame.py</code> ·
<code>node --test tests/js</code></p>
</main>
<script src="square_lab.js"></script>
<script>{APP}</script>
</body></html>
'''


def main() -> int:
    OUT.write_text(page_html(), encoding="utf-8")
    import hub
    hub.decorate_file(OUT.name)
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
