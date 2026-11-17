"""The interactive square/rectangle lab: controls, and a page that draws live.

    .venv/bin/python scripts/square_frame.py

Writes `workbench/square-frame.html`. The maths is `workbench/plate_math.js`
(the same file the plates use), and the curves are the saved set in
`workbench/real-curves.json`. This generator writes only the shell; the page
loads the data and computes on every control change.

The page measures in points (1/72 in). The stroke is `PlateMath.strokeFor`, so
it is 1 point at every print size from 1 to 4 inches.
"""

from __future__ import annotations

import json
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
const params = new URLSearchParams(location.search);
let rows = null;

function show(id, value) {
  const el = $(id + "-v");
  if (el) el.textContent = value;
}

function loadCharacter(name) {
  const row = rows[name];
  if (!row) return;
  const width = (row.width && row.width.percent) || 1.5;
  const character = row.character || {};
  $("sf-width").value = width;
  $("sf-plus").value = character.plus ?? 2;
  $("sf-minus").value = character.minus ?? 2;
  $("sf-profile").value = ["bow", "s", "taper"].includes(character.profile)
    ? character.profile : "bow";
}

function start() {
  rows = Object.fromEntries(window.REAL_CURVES.curves.map((row) => [row.name, row]));
  const names = Object.keys(rows).sort();
  ["sf-a", "sf-b"].forEach((id) => {
    const extra = id === "sf-b" ? ["none", "same"] : [];
    $(id).innerHTML = [...extra, ...names]
      .map((name) => `<option>${name}</option>`).join("");
  });
  $("sf-a").value = "u-bowl";
  $("sf-b").value = "none";
  $("sf-form").value = "single";
  $("sf-natural").checked = true;
  loadCharacter($("sf-a").value);
  if (params.has("width")) $("sf-width").value = params.get("width");
  draw();
}

function draw() {
  if (!rows) return;
  const aName = $("sf-a").value;
  const bChoice = $("sf-b").value;
  const bName = bChoice === "none" ? null : bChoice === "same" ? aName : bChoice;
  let form = $("sf-form").value;
  let fallback = "";
  if (form === "leaf" && !bName) {
    form = "single";
    fallback = " · curve b none, drawn single";
  }
  const perW = Number($("sf-per-w").value);
  const perH = Number($("sf-per-h").value);
  const pattern = $("sf-pattern").value;
  const natural = $("sf-natural").checked;
  const leg = natural ? null : Number($("sf-leg").value);
  const sizeIn = Number($("sf-size").value);
  const fill = Number($("sf-fill").value);
  const alternate = $("sf-alternate").checked;
  const showFrame = $("sf-frame").checked;
  const width = Number($("sf-width").value);
  const plus = Number($("sf-plus").value);
  const minus = Number($("sf-minus").value);
  const profile = $("sf-profile").value;

  show("sf-per-w", perW);
  show("sf-per-h", perH);
  show("sf-leg", natural ? "natural" : leg + "°");
  show("sf-size", sizeIn.toFixed(2) + " in");
  show("sf-fill", Math.round(fill * 100) + "%");
  show("sf-width", width.toFixed(1) + "%");
  show("sf-plus", plus.toFixed(1) + " / " + minus.toFixed(1));

  const patch = (name) => ({ ...rows[name], width: { percent: width },
    character: { plus, minus, profile } });
  const patched = { ...rows, [aName]: patch(aName) };
  if (bName) patched[bName] = patch(bName);

  let data;
  try {
    if (form === "single") {
      const group = PlateMath.group(patched[aName]);
      data = { paths: group.paths, bbox: PlateMath.bbox(group.paths.flat()), note: group.note };
    } else {
      data = PlateMath.design({
        form, curve: aName, curveB: bName || undefined, leg,
        frame: showFrame ? { perWidth: perW, perHeight: perH } : null,
        pattern, alternate,
      }, patched);
    }
  } catch (error) {
    stage.innerHTML = "";
    readout.textContent = String(error);
    return;
  }

  const W = sizeIn * 72;
  const H = W;
  const margin = W * 0.06;
  const [x0, y0, x1, y1] = data.bbox;
  const k = Math.min((W - 2 * margin) / (x1 - x0), (H - 2 * margin) / (y1 - y0)) * fill;
  const ox = (W - (x1 - x0) * k) / 2 - x0 * k;
  const oy = (H - (y1 - y0) * k) / 2 - y0 * k;
  const toSvg = ([x, y]) => [ox + x * k, H - (oy + y * k)];
  const stroke = PlateMath.strokeFor(W);

  stage.setAttribute("viewBox", `0 0 ${W} ${H}`);
  stage.setAttribute("width", W);
  stage.setAttribute("height", H);
  stage.innerHTML = data.paths.map((path) => {
    const text = path.map((p) => toSvg(p).map((v) => v.toFixed(2)).join(",")).join(" ");
    return `<polyline points="${text}" fill="none" stroke="#2e2413" `
      + `stroke-width="${stroke.toFixed(2)}" stroke-linecap="round" `
      + `stroke-linejoin="round"/>`;
  }).join("");

  readout.textContent =
    `${((x1 - x0) * k / 72).toFixed(2)} × ${((y1 - y0) * k / 72).toFixed(2)} in · `
    + `${data.paths.length} paths · stroke ${stroke.toFixed(2)} pt · ${data.note}`
    + fallback;
}

["sf-per-w", "sf-per-h", "sf-pattern", "sf-leg", "sf-natural", "sf-size",
 "sf-fill", "sf-alternate", "sf-frame", "sf-width", "sf-plus", "sf-minus",
 "sf-profile"].forEach((id) => $(id).addEventListener("input", draw));
$("sf-a").addEventListener("input", () => { loadCharacter($("sf-a").value); draw(); });
$("sf-b").addEventListener("input", draw);
start();
"""


def _curves_json() -> str:
    """The curve data to inline, checked before it is written into the page.

    A failed or damaged read must never become an empty page: the count must
    match, and no curve may be a row of zeros. This is the fault that once
    emptied two thirds of the saved curves.
    """
    path = ROOT / "workbench" / "real-curves.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    curves = data.get("curves") or []
    if not curves:
        raise SystemExit("refusing to write the lab: real-curves.json has no curves")
    if data.get("count") is not None and int(data["count"]) != len(curves):
        raise SystemExit("refusing: count does not match the curve list")
    for row in curves:
        speeds = list(row.get("speedX") or []) + list(row.get("speedY") or [])
        if not speeds or not any(float(value) for value in speeds):
            raise SystemExit(f"refusing: {row.get('name')!r} has no nonzero speed")
    return json.dumps(data)


def page_html() -> str:
    curves = _curves_json()
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
.controls label{{display:block;margin:0 0 12px;font-size:13px}}
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
<p class="lead">The saved curves, on 90° edges. The leg bisects the corner
(45°) for a cross or a frame; an arch keeps its natural legs. Every copy carries
its character rails and is closed at the ends.</p>

<div class="wrap">
<div class="controls">
  <label>curve a <select id="sf-a"></select></label>
  <label>curve b <select id="sf-b"></select></label>
  <label>
    <span class="row"><span>rail width</span><b id="sf-width-v">1.5%</b></span>
    <input id="sf-width" type="range" min="0.5" max="6" step="0.1" value="1.5">
  </label>
  <label>
    <span class="row"><span>plus / minus</span><b id="sf-plus-v">2.0 / 2.0</b></span>
    <input id="sf-plus" type="range" min="0" max="3" step="0.1" value="2">
    <input id="sf-minus" type="range" min="0" max="3" step="0.1" value="2">
  </label>
  <label>profile
    <select id="sf-profile">
      <option value="bow">bow</option>
      <option value="s">s</option>
      <option value="taper">taper</option>
    </select>
  </label>
  <label>form
    <select id="sf-form">
      <option value="cross">cross</option>
      <option value="leaf">leaf</option>
      <option value="arch">arch</option>
      <option value="single">single curve</option>
    </select>
  </label>
  <label>
    <span class="row"><span>curves across</span><b id="sf-per-w-v">3</b></span>
    <input id="sf-per-w" type="range" min="1" max="6" step="1" value="3">
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
  <label class="check"><input id="sf-natural" type="checkbox"> natural legs
    (for the arch)</label>
  <label>
    <span class="row"><span>print size</span><b id="sf-size-v">4.00 in</b></span>
    <input id="sf-size" type="range" min="1" max="4" step="0.25" value="4">
  </label>
  <label>
    <span class="row"><span>drawing fills</span><b id="sf-fill-v">100%</b></span>
    <input id="sf-fill" type="range" min="0.5" max="1" step="0.05" value="1">
  </label>
  <label class="check"><input id="sf-alternate" type="checkbox">
    flip every other copy</label>
  <label class="check"><input id="sf-frame" type="checkbox" checked>
    show the frame</label>
</div>
<div>
  <div id="sf-readout">loading…</div>
  <div class="stage"><svg id="sf-stage" viewBox="0 0 288 288" role="img"
    aria-label="saved curves on the edges of a square or rectangle"></svg></div>
</div>
</div>

<p class="note">The page loads the same <code>plate_math.js</code> the book
plates use and the same saved set in <code>real-curves.json</code>. A rail that
would fold is shrunk, and a plate at the floor is drawn spine-only. The stroke
floor is <strong>1 point</strong> at 1–4 inches.</p>
<p class="note">Re-derive: <code>python scripts/square_frame.py</code> ·
<code>node --test tests/js</code></p>
</main>
<script src="plate_math.js"></script>
<script>window.REAL_CURVES = __CURVES__;</script>
<script>{APP}</script>
</body></html>
'''.replace("__CURVES__", curves)


def main() -> int:
    OUT.write_text(page_html(), encoding="utf-8")
    import hub
    hub.decorate_file(OUT.name)
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
