"""The experimental sandbox: fractional exponents, and every find at the foot.

    .venv/bin/python scripts/ph_nth_sandbox_exp.py

The speed rows may step by 1, 1/2, 1/3 or 1/4, so a row can carry t^0.5, t^1.5,
t^2.5 (5/2), t^3.5 (7/2) and so on. With a step of 1/2 the row is a polynomial in
sqrt(t): a flat spot at u = 1/9 sits at t = 1/81.

The gallery at the foot is the finds from `workbench/found-curves.json`, tangliest
first and odd shapes included, because this is the page for looking at odd shapes.
The seeds are switched off here so the found curves are not mixed with them.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_nth_sandbox as base  # noqa: E402

OUT = ROOT / "workbench" / "ph-nth-sandbox-exp.html"
FOUND = ROOT / "workbench" / "found-curves.json"

GALLERY_HEAD = (
    "<h2>Found curves</h2>\n"
    "<p class=\"small\">Every curve the search has landed, tangliest first. The line under each name "
    "is its bend and its grid; the expanded cell gives the flat spots, the meetings and the "
    "self-crossings. Odd shapes are kept on purpose. Loading one sets the exponent step back to 1, "
    "because every stored curve is a whole-power row.</p>\n"
)

INTRO = (
    "<p class=\"small\"><strong>Experimental.</strong> The rows below step by the exponent chosen at "
    "the top: 1/2 gives <code>t^0.5</code>, <code>t^1.5</code>, <code>t^2.5</code> (5/2), "
    "<code>t^3.5</code> (7/2). Bend and closest are measured from the curve; the grid and the "
    "inflection count are marked not applicable, because neither exists off the whole powers. A "
    "fractional step cannot be mirror-symmetric: symmetry needs <code>t = 2^(-1/s)</code>, which is "
    "irrational for every rational step but 1.</p>\n"
)


def found_entries():
    """The finds, tangliest first: self-crossings, then meetings, then the cheap grid."""
    import curve_records
    document = curve_records.read(FOUND)
    newer = [curve for curve in document["curves"]
             if curve.get("provenance", {}).get("batch") == "new"]
    # newest first: the page is where new curves are worked on, so they lead. Ties
    # fall back to the tangliest, then the cheapest grid.
    position = {id(curve): index for index, curve in enumerate(document["curves"])}
    ordered = sorted(newer,
                     key=lambda curve: (-position[id(curve)],
                                        -curve.get("measured", {}).get("self", 0),
                                        -curve.get("measured", {}).get("meetings", 0),
                                        curve.get("measured", {}).get("grid", 0)))
    entries = []
    for curve in ordered:
        x, y = curve_records.rows_from_terms(curve["terms"])
        recorded = curve.get("measured", {})
        entries.append({
            "name": curve["name"],
            "terms": curve["terms"],
            "speedX": x,
            "speedY": y,
            "bend": recorded.get("bend"),
            "pitch": recorded.get("grid"),
            "from": "found",
            "truncation": curve.get("truncation"),
            "source": (f"flat spots {curve.get('provenance', {}).get('roots', '')}; "
                       f"{recorded.get('meetings', 0)} meetings, {recorded.get('self', 0)} self-crossings"),
        })
    return entries


def build():
    page = base.PAGE
    page = page.replace("__GALLERY__", json.dumps(found_entries(), separators=(",", ":")))
    page = page.replace("window.phSpeedDegree = 5;",
                        "window.phHideSeeds = true;\nwindow.phNoComplement = true;\nwindow.phSpeedDegree = 5;")
    page = page.replace("__MATH__", base.MATH.read_text())
    page = page.replace("__PANELS__", base.PANELS.read_text())
    page = page.replace("<title>The eleventh power: a PH curve of degree 11</title>",
                        "<title>Experiment: fractional exponents</title>")
    page = page.replace("<h1>The eleventh power</h1>", "<h1>Experiment: fractional exponents</h1>")

    # the complementary curve goes, and a mirror-safe tweak panel takes its place
    box_start = page.index('<div class="curve-box complement" id="n-complement-box">')
    box_end = page.index('<p class="small mono" id="n-readout">')
    tweak = """<div class="curve-box" id="n-tweak-box">
  <h3>Tweak the primary curve, mirror kept</h3>
  <p class="small">Each button adds a balanced change, so the curve stays mirrored about the middle.
  <strong>size</strong> scales it, as a fraction: 1 is bold, 1/4 is a nudge. Use halves,
  quarters, eighths or whole numbers — <strong>not thirds or sevenths</strong>, which cannot be written
  exactly in the machine and blow the integer grid up (measured: 1/3 took 3,465 to 8.7e13). The
  status line says what the grid cost is, and at step 1 the readout shows the grid itself. The primary curve above redraws at
  once. On the y row the pattern has three numbers, because that row reads as its own negative from
  the far end, so a two-number swap would lean it.</p>
  <div class="solver-row">
    <label class="dial" for="n-tweak-size">size
      <input id="n-tweak-size" type="text" list="n-tweak-sizes" value="1/4" size="6"
             title="a fraction such as 1/4; decimals work but cost more grid">
      <datalist id="n-tweak-sizes">
        <option value="1/8"></option><option value="1/4"></option><option value="1/2"></option>
        <option value="1"></option><option value="2"></option><option value="3"></option>
      </datalist></label>
    <label class="dial" for="n-tweak-divisor" title="take a share of the coefficient itself: 16 divided by 8 gives a whole-number tweak of 2">share of the x pair
      <select id="n-tweak-divisor">
        <option value="0">absolute size</option>
        <option value="2">1/2 of the pair</option>
        <option value="4">1/4 of the pair</option>
        <option value="8">1/8 of the pair</option>
        <option value="16">1/16 of the pair</option>
      </select></label>
    <button type="button" id="n-tweak-x1" title="add -size on t^1 and +size on t^2">x: t1, t2</button>
    <button type="button" id="n-tweak-x2" title="add +1, -2, +1 times size on t^2 to t^4">x: t2 to t4</button>
    <button type="button" id="n-tweak-x3" title="add +1, -3, +3, -1 times size on t^3 to t^6">x: t3 to t6</button>
    <button type="button" id="n-tweak-y1" title="add -1, +3, -2 times size on t^1 to t^3">y: t1 to t3</button>
    <button type="button" id="n-tweak-y2" title="add -1, +4, -5, +2 times size on t^2 to t^5">y: t2 to t5</button>
    <button type="button" id="n-tweak-both" title="multiply both rows by 1 + size (t - t^2)">both rows: 1 + size(t - t2)</button>
    <button type="button" id="n-tweak-undo" title="take back the last tweak">undo</button>
  </div>
  <p class="small mono" id="n-tweak-status"></p>
  <p class="small mono" id="n-tweak-total">no change from the starting curve yet</p>
</div>
"""
    page = page[:box_start] + tweak + page[box_end:]

    # the leg-cutting controls are parked on their own notes page: they cannot work
    # on this family (the crossings span the curve), and leaving them here only
    # invited the operator to try them again. Removed by exact markup, so the row
    # that keeps the zoom and the focus is untouched.
    arc_row = """<div class="solver-row" id="n-arc-row">
  <label class="dial" for="n-arc-percent">keep the middle
    <input id="n-arc-percent" type="number" min="10" max="99" step="1" value="70"> % of the ink</label>
  <button type="button" id="n-arc-rebuild" title="cut in arc length, then rebuild the kept arc as exact rows">cut and rebuild</button>
  <span class="small">arc length belongs to the shape, not to <code>t</code></span>
</div>
"""
    page = page.replace(arc_row, "")
    for markup in (
        '  <button type="button" id="n-cut-knot" title="restrict the drawing to the knot; the curve itself is unchanged">show only the knot</button>\n',
        '  <button type="button" id="n-rebuild-span" title="rebuild the knot\'s span as a new curve: exact whole numbers, no legs left in the rows">rebuild without the legs</button>\n',
    ):
        page = page.replace(markup, "")
    page = page.replace("Knot experiments</h3>",
                        "Look closer</h3>\n<p class=\"small\">Optical only: these change the frame, "
                        "never the numbers. The knot-cutting controls that did not work are "
                        "<a href=\"ph-nth-exp-notes.html\">parked with their measurements</a>.</p>", 1)

    # the gallery keeps its host, and gets a heading of its own
    head_start = page.index("<h2>Gallery: the spines so far</h2>")
    head_end = page.index('<div class="gallery" id="n-gallery"></div>')
    page = page[:head_start] + GALLERY_HEAD + page[head_end:]

    # fifteen numbers per axis, so step 1/2 reaches t^7, and the step applies from
    # the first draw rather than only once the slider moves
    page = page.replace("window.phSpeedDegree = 5;",
                        "window.phSpeedDegree = 14;\nwindow.phPowerStep = 0.5;")

    page = page.replace(
        "<p>One row of numbers for <code>x</code> and one for <code>y</code>, from <code>t^0</code> upward.",
        INTRO + "<p>One row of numbers for <code>x</code> and one for <code>y</code>, from <code>t^0</code> upward.")

    # the curve being worked on opens on refresh: step 1 first, so its terms land
    # in the whole-power boxes, then the curve itself
    starter = (
        "<script>\n"
        "(() => {\n"
        "  const step = document.getElementById('n-step');\n"
        "  if (step) { step.value = '0.5'; step.dispatchEvent(new Event('input', { bubbles: true })); }\n"
        "  const wanted = (window.phNthGallery || []).find(entry => entry.name === 'wide-knot-x20');\n"
        "  if (wanted && window.phNthLoad) window.phNthLoad(wanted);\n"
        "})();\n"
        "</script>\n"
    )
    page = page.replace("</body></html>", starter + "</body></html>")
    OUT.write_text(base.stamped(page))
    print(OUT.relative_to(ROOT), len(found_entries()), "found curves,", len(page), "bytes")


if __name__ == "__main__":
    build()
