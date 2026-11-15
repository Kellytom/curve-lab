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

# The seven families to work from: one outer flat spot, its mirror, and three
# copies at 1/2. Five spots, so the row ends at t^5. A button writes those spots
# into the field and presses the same "fill from the dots" the operator presses,
# so what loads is exactly what the strip shows.
FAMILIES = ("1/15", "1/14", "1/13", "1/12", "1/11", "1/10", "1/9")


def family_section():
    buttons = []
    for text in FAMILIES:
        numerator, denominator = (int(part) for part in text.split("/"))
        spots = f"{text}, 1/2, 1/2, 1/2, {denominator - numerator}/{denominator}"
        buttons.append(
            f'    <button type="button" class="family" data-spots="{spots}" '
            f'title="flat spots {spots}">{text}</button>')
    return (
        '<div class="curve-box" id="n-families">\n'
        '<h3>Seven families: one outer flat spot, its mirror, three at 1/2</h3>\n'
        '<p class="small">One flat spot and its mirror, plus three copies at 1/2, is five spots, '
        'so the row runs to <code>t^5</code>. The outer spot picks the family. Click one to load '
        'it, then nudge the numbers above to find its children; the dots it loads are on the strip '
        'in your own hand, so you can move one and watch the row follow.</p>\n'
        '<div class="solver-row" id="n-family-buttons">\n'
        + "\n".join(buttons) + "\n"
        '</div>\n'
        '<p class="small">Families first; the found curves stay below the line, for later.</p>\n'
        '</div>\n'
        '<hr style="border:0;border-top:2px solid #2e2413;margin:22px 0 16px">\n'
    )

INTRO = (
    "<p class=\"small\"><strong>Experimental.</strong> The rows below step by the exponent chosen at "
    "the top: 1/2 gives <code>t^0.5</code>, <code>t^1.5</code>, <code>t^2.5</code> (5/2), "
    "<code>t^3.5</code> (7/2). Bend and closest are measured from the curve. The grid and the "
    "inflection count need whole powers; when the step is 1/2 or 1/3 but every number still sits on a "
    "whole power &mdash; the half boxes left empty &mdash; the row is folded back and both are reported "
    "as usual. Only a number that really sits on a fractional power turns them off. A "
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
  <p class="small">Pick a change in the dropdown, then press one of the four buttons; each press
  adds that change once more, so ten presses give ten times the nudge. Every pattern is balanced about
  the middle, so the curve stays mirrored: <strong>x: t1, t2</strong> and <strong>x: t2 to t4</strong>
  push the width, <strong>x: t3 to t6</strong> and the two y patterns push the vertical gesture.
  <strong>nudge</strong> is one step, <strong>bump</strong> is five. A minus button subtracts the
  pattern, which is just as safe as adding it — the rows already carry negative numbers. The status
  line prints the grid after every press, because the grid after a change depends on arithmetic and
  not on how round the number looks: on <code>1/15</code> a nudge of 3 keeps 1/154, of 5 gives 1/1386
  and of 6 gives 1/770. <strong>Widen the ink</strong> multiplies both rows by <code>1 + s(t - t^2)</code>,
  which re-times the stroke rather than adding a term; that lifts the top power, so a divisor it has
  not met before (13) joins the grid unless <code>s</code> is a multiple of 13 — 39 measures 1/210,
  the cheapest of the four.</p>
  <div class="solver-row">
    <label class="dial" for="n-tweak-pattern">change
      <select id="n-tweak-pattern">
        <option value="x1">x: t1, t2</option>
        <option value="x2" selected>x: t2 to t4</option>
        <option value="x3">x: t3 to t6</option>
        <option value="y1">y: t1 to t3</option>
        <option value="y2">y: t2 to t5</option>
      </select></label>
    <button type="button" class="tweak-step" data-step="-5" title="subtract 5 times the pattern">bump &minus;5</button>
    <button type="button" class="tweak-step" data-step="-1" title="subtract the pattern once">nudge &minus;1</button>
    <button type="button" class="tweak-step" data-step="1" title="add the pattern once">nudge +1</button>
    <button type="button" class="tweak-step" data-step="5" title="add 5 times the pattern">bump +5</button>
    <button type="button" id="n-tweak-undo" title="take back the last change">undo</button>
  </div>
  <div class="solver-row">
    <label class="dial" for="n-tweak-spread" title="multiplying both rows re-times the stroke; 13 is the divisor the new top power introduces, so a multiple of 13 keeps it out of the grid">widen the ink, s =
      <select id="n-tweak-spread">
        <option value="1">1</option>
        <option value="5">5</option>
        <option value="13">13</option>
        <option value="39">39</option>
      </select></label>
    <button type="button" id="n-tweak-both" title="multiply both rows by 1 + s (t - t^2)">widen the ink</button>
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

    # the gallery keeps its host, and gets a heading of its own, under the families
    head_start = page.index("<h2>Gallery: the spines so far</h2>")
    head_end = page.index('<div class="gallery" id="n-gallery"></div>')
    page = page[:head_start] + family_section() + GALLERY_HEAD + page[head_end:]

    # fifteen numbers per axis, so step 1/2 reaches t^7, and the step applies from
    # the first draw rather than only once the slider moves
    page = page.replace("window.phSpeedDegree = 5;",
                        "window.phSpeedDegree = 14;\nwindow.phPowerStep = 0.5;")

    page = page.replace(
        "<p>One row of numbers for <code>x</code> and one for <code>y</code>, from <code>t^0</code> upward.",
        INTRO + "<p>One row of numbers for <code>x</code> and one for <code>y</code>, from <code>t^0</code> upward.")

    # a family button writes its spots into the field and presses the same control
    # the operator presses, so the curve that loads is the one the dots describe
    starter = (
        "<script>\n"
        "(() => {\n"
        "  const step = document.getElementById('n-step');\n"
        "  if (step) { step.value = '0.5'; step.dispatchEvent(new Event('input', { bubbles: true })); }\n"
        "  const wanted = (window.phNthGallery || []).find(entry => entry.name === 'wide-knot-x20');\n"
        "  if (wanted && window.phNthLoad) window.phNthLoad(wanted);\n"
        "})();\n"
        "(() => {\n"
        "  // the seven families: one click loads the spots, and the strip follows\n"
        "  document.querySelectorAll('#n-family-buttons .family').forEach(button => {\n"
        "    button.addEventListener('click', () => {\n"
        "      const field = document.getElementById('n-roots');\n"
        "      const fill = document.getElementById('n-roots-dots-fill');\n"
        "      if (!field || !fill) return;\n"
        "      // a family row is whole powers: put the step at 1 first, so the six\n"
        "      // numbers land in six boxes instead of every other half-power box\n"
        "      const stepBox = document.getElementById('n-step');\n"
        "      if (stepBox) { stepBox.value = '1'; stepBox.dispatchEvent(new Event('input', { bubbles: true })); }\n"
        "      field.value = button.dataset.spots;\n"
        "      field.dispatchEvent(new Event('change', { bubbles: true }));\n"
        "      fill.click();\n"
        "      const box = document.getElementById('n-roots-box');\n"
        "      if (box) box.scrollIntoView({ behavior: 'smooth', block: 'start' });\n"
        "    });\n"
        "  });\n"
        "})();\n"
        "</script>\n"
    )
    page = page.replace("</body></html>", starter + "</body></html>")
    OUT.write_text(base.stamped(page))
    print(OUT.relative_to(ROOT), len(found_entries()), "found curves,", len(page), "bytes")


if __name__ == "__main__":
    build()
