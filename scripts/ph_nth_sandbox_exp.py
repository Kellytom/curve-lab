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


def spot_text(provenance):
    """The flat spots as the ruler reads them, or "" when the note is prose.

    A few records describe themselves in words ("y from lace-1of10-3-2; x = ..."), and
    writing that into the field would put nonsense on the ruler, so only a plain list
    of fractions is offered.
    """
    text = str(provenance or "").strip()
    if not text:
        return ""
    parts = [part.strip() for part in text.split(",")]
    for part in parts:
        top, _, bottom = part.partition("/")
        if not top.isdigit() or (bottom and not bottom.isdigit()):
            return ""
    return ", ".join(parts)


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
            "roots": spot_text(curve.get("provenance", {}).get("roots")),
            "truncation": curve.get("truncation"),
            "source": (f"flat spots {curve.get('provenance', {}).get('roots', '')}; "
                       f"{recorded.get('meetings', 0)} meetings, {recorded.get('self', 0)} self-crossings"),
        })
    return entries


# Two outer flat spots and their mirrors, with three copies at 1/2: seven spots, so a
# t^7 row. The pairs below were measured one by one; the count beside each is the
# number of times the spine crosses itself, which is the number the page reports.
RELATED = (
    ("1/15 + 1/12", 15, 12, 9),
    ("1/16 + 1/13", 16, 13, 9),
    ("1/11 + 1/7", 11, 7, 9),
    ("1/11 + 1/5", 11, 5, 9),
    ("1/12 + 1/5", 12, 5, 7),
    ("1/16 + 1/4", 16, 4, 7),
    ("1/17 + 1/4", 17, 4, 7),
)


def related_section():
    buttons = []
    for label, first, second, crossings in RELATED:
        spots = (f"1/{first}, 1/{second}, 1/2, 1/2, 1/2, "
                 f"{second - 1}/{second}, {first - 1}/{first}")
        buttons.append(
            f'    <button type="button" class="family" data-spots="{spots}" '
            f'title="flat spots {spots}">{label} &middot; {crossings} crossings</button>')
    return (
        '<div class="curve-box" id="n-related">\n'
        '<h3>Related families: two outer flat spots, its mirror, three at 1/2</h3>\n'
        '<p class="small">Two outer spots on one side and their two mirrors, plus the three copies at '
        '1/2, is seven spots, so the row runs to <code>t^7</code>. Each button carries the number of '
        'times that curve crosses itself, read from this page\'s own counter after loading it; the number '
        'in the button is that count. These seven are the best of the 171 such families over denominators '
        '2 to 20: every pair was measured, and the list is by crossings first, then by the cheapest grid '
        '&mdash; 1/15 + 1/12 reaches nine at 1/182, where 1/11 + 1/5 costs 1/6,006 for the same nine. '
        'Adding a third outer pair reaches fifteen crossings at 1/3 + 1/7 + 1/11, but its grid is '
        '1/19,399,380, so it is not offered here.</p>\n'
        '<div class="solver-row" id="n-related-buttons">\n'
        + "\n".join(buttons) + "\n"
        '</div>\n'
        '<p class="small">These sit above the line too: the found gallery stays below it.</p>\n'
        '</div>\n'
    )


CENSUS = ROOT / "workbench" / "family-census.json"


def census_picks(knotty=6, cheap=6):
    """The best of the census, so every copy count and pair count is reachable.

    The two sections above it fix the copy count at three; the census did not. It found
    9 crossings at grid 1/42 with one copy at 1/2, and 6 at grid 1/36 with three outer
    pairs — neither is a button anywhere else. Ranked by crossings, then by grid, with a
    second list for the cheap ones (grid 100 or less).
    """
    if not CENSUS.exists():
        return []
    curves = json.loads(CENSUS.read_text())["curves"]
    curves = sorted(curves, key=lambda c: (-c["crossings"], c["grid"]))
    chosen = list(curves[:knotty])
    below = sorted([c for c in curves if c["grid"] <= 100 and c["crossings"] >= 5],
                   key=lambda c: (-c["crossings"], c["grid"]))
    seen = {c["spots"] for c in chosen}
    chosen += [c for c in below if c["spots"] not in seen][:cheap]
    return chosen


def census_section():
    picks = census_picks()
    if not picks:
        return ""
    buttons = []
    for curve in picks:
        spots = curve["spots"]
        outer = [part.strip() for part in spots.split(",") if part.strip() != "1/2"]
        copies = sum(1 for part in spots.split(",") if part.strip() == "1/2")
        outer = outer[: (len(outer) + 1) // 2]          # the lower half names the spots
        label = (f"{curve['crossings']} crossings &middot; grid 1/{curve['grid']:,} "
                 f"&middot; {' + '.join(outer)} + &frac12;&times;{copies}")
        buttons.append(
            f'    <button type="button" class="family" data-spots="{spots}" '
            f'title="flat spots {spots}">{label}</button>')
    return (
        '<div class="curve-box" id="n-census">\n'
        '<h3>Best of the census: every copy count</h3>\n'
        '<p class="small">The two sections above hold the copy count at three. The census '
        'did not: it measured 1 to 5 copies at 1/2 and 1 to 3 outer pairs, 7,068 curves in '
        'all, and these twelve are the best of them &mdash; the six tangliest, then the six '
        'cheapest with five crossings or more. Each button says its crossings, its grid and '
        'its spots, so a cheap knot can be found without opening the JSON.</p>\n'
        '<div class="solver-row" id="n-census-buttons">\n'
        + "\n".join(buttons) + "\n"
        '</div>\n'
        '<p class="small">The full list is <code>workbench/family-census.json</code>; '
        '<code>scripts/family_census.py --report</code> prints the ranking again.</p>\n'
        '</div>\n'
    )


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
  and of 6 gives 1/770. <strong>Expand and change</strong> multiplies both rows by <code>1 + s(t - t^2)</code>,
  which re-times the stroke rather than adding a term. It used to keep the two new powers, and
  those brought the divisors 13, 14 and 15 into the grid &mdash; 1/210 at best, against a base of 1/154.
  It now fits the widened rows back into the numbers that already exist and rounds them to whole
  numbers, so the degree does not change. The price is distortion, and the status line prints it —
  the worst miss as a share of the row, and the grid the new whole numbers give, which is not
  promised to stay put. Press it twice and the second press widens what the first produced.</p>
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
    <label class="dial" for="n-tweak-spread" title="how hard the expansion pushes: s in 1 + s(t - t^2)">expand and change, s =
      <select id="n-tweak-spread">
        <option value="1">1</option>
        <option value="2">2</option>
        <option value="3">3</option>
        <option value="5" selected>5</option>
        <option value="8">8</option>
        <option value="13">13</option>
      </select></label>
    <button type="button" id="n-tweak-both" title="multiply both rows by 1 + s (t - t^2), then fit them back to the same powers">expand and change</button>
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
    page = page[:head_start] + family_section() + related_section() + census_section() + GALLERY_HEAD + page[head_end:]

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
        "  document.querySelectorAll('.family').forEach(button => {\n"
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
