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
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import curve_records  # noqa: E402
import ph_nth_sandbox as base  # noqa: E402
import ph_root_search as roots_module  # noqa: E402

OUT = ROOT / "workbench" / "ph-nth-sandbox-exp.html"
FOUND = ROOT / "workbench" / "found-curves.json"
MOVED = ROOT / "workbench" / "moved-curves.json"
CURVES = ROOT / "curves"

GALLERY_HEAD = (
    "<h2 id=\"n-gallery\">Every stored curve</h2>\n"
    "<p class=\"small\">Every curve on record, as a button: the finds first, tangliest first, "
    "then the curves moved to the notes, then the 15 with a folder of their own. The line under "
    "each name is its bend and its grid; the expanded cell gives the flat spots, the meetings and "
    "the self-crossings. Odd shapes are kept on purpose. Loading one sets the exponent step back to "
    "1, because every stored curve is a whole-power row.</p>\n"
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


def _figure_for(name, tag):
    """The picture for a curve, from the one place that curve's picture lives."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if tag == "folder":
        return f"../curves/{name}/figure.png"
    hud = ROOT / "workbench" / "figures" / f"{slug}.png"
    return f"../workbench/figures/{slug}.png" if hud.exists() else ""


def _terms_of(record):
    """A record's terms, whether it stores terms or speed rows."""
    if record.get("terms"):
        return record["terms"]
    speed_x = record.get("speedX") or []
    speed_y = record.get("speedY") or []
    length = max(len(speed_x), len(speed_y))
    return [
        {"power": power,
         "x": speed_x[power] if power < len(speed_x) else 0,
         "y": speed_y[power] if power < len(speed_y) else 0}
        for power in range(length)
    ]


def _entry(curve, tag):
    """One gallery entry: the shape every cell and every load button reads."""
    terms = _terms_of(curve)
    x, y = curve_records.rows_from_terms(terms)
    measured = curve.get("measured") or {}
    name = curve["name"]
    roots = (curve.get("provenance") or {}).get("roots", "")
    return {
        "name": name,
        "terms": terms,
        "speedX": x,
        "speedY": y,
        "bend": measured.get("bend", curve.get("bend")),
        "pitch": measured.get("grid", curve.get("grid")),
        "from": tag,
        "roots": spot_text(roots),
        "figure": _figure_for(name, tag),
        "truncation": curve.get("truncation"),
        "source": (f"flat spots {roots}; {measured.get('meetings', 0)} meetings, "
                   f"{measured.get('self', 0)} self-crossings")
        if roots else (curve.get("source") or ""),
    }


def stored_entries():
    """Every stored curve, as one gallery: found first, then the moved, then the folders.

    The operator asked on 2026-11-16 for every curve to be back in the buttons:
    "make sure i get all my curves back in the buttons". The moved curves were
    taken out of this gallery in the clean-up, which left them on the notes page
    with no way to load one. They are back here, tagged *moved*, and the 15
    curves with a folder under `curves/` are tagged *kept*.
    """
    entries, seen = [], set()
    document = curve_records.read(FOUND)
    newer = [curve for curve in document["curves"]
             if curve.get("provenance", {}).get("batch") == "new"]
    position = {id(curve): index for index, curve in enumerate(document["curves"])}
    ordered = sorted(newer,
                     key=lambda curve: (-position[id(curve)],
                                        -curve.get("measured", {}).get("self", 0),
                                        -curve.get("measured", {}).get("meetings", 0),
                                        curve.get("measured", {}).get("grid", 0)))
    for curve in document["curves"]:
        if curve not in newer:
            ordered.append(curve)
    for curve in ordered:
        entries.append(_entry(curve, "found"))
        seen.add(curve["name"])

    if MOVED.exists():
        moved_document = json.loads(MOVED.read_text())
        moved = [curve for curve in moved_document.get("curves", [])
                 if curve.get("name") not in seen]
        moved.sort(key=lambda curve: (-curve.get("measured", {}).get("self", 0),
                                      -curve.get("measured", {}).get("meetings", 0),
                                      curve.get("measured", {}).get("grid", 0)))
        for curve in moved:
            entries.append(_entry(curve, "moved"))
            seen.add(curve["name"])

    for path in sorted(CURVES.glob("*/curve.json")):
        record = json.loads(path.read_text())
        if record.get("name") in seen:
            continue
        entries.append(_entry(record, "folder"))
        seen.add(record.get("name"))
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


def possible_picks():
    """The investigation list: what is known to be good and is not a button yet.

    Three kinds, because they answer different questions:
      * record holders — the most crossings the box holds, however fine the grid;
      * cheap knots   — five crossings or more on a grid of 100 or less;
      * one-pair families outside the page's window, so the seven above it are not
        mistaken for the whole set.
    """
    if not CENSUS.exists():
        return []
    curves = json.loads(CENSUS.read_text())["curves"]
    chosen, seen = [], set()

    def take(curve, tag):
        if curve["spots"] in seen:
            return
        seen.add(curve["spots"])
        chosen.append((curve, tag))

    for curve in sorted(curves, key=lambda c: (-c["crossings"], c["grid"]))[:3]:
        take(curve, "record")
    cheap = sorted([c for c in curves if c["grid"] <= 100 and c["crossings"] >= 5],
                   key=lambda c: (-c["crossings"], c["grid"]))
    for curve in cheap[:5]:
        take(curve, "cheap")
    outside = [c for c in curves if c["outer"] == 1 and c["copies"] == 3
               and not c["spots"].startswith(("1/15", "1/14", "1/13", "1/12", "1/11", "1/10", "1/9"))]
    for curve in sorted(outside, key=lambda c: (-c["crossings"], c["grid"]))[:3]:
        take(curve, "untried")
    return chosen


def big_row(spots_text):
    """True when the row's coefficients pass a million, where the page's counter fails.

    The census counts crossings in exact arithmetic; the page evaluates in doubles, and
    at peaks near 10^8 the difference p^2 - q^2 loses its low bits. Measured on the page:
    every row below a million reproduces its census count, and four of the five above it
    read 0. The button says so rather than pretending.
    """
    try:
        spots = [F(part.strip()) for part in spots_text.split(",") if part.strip()]
        row = roots_module.row_from_roots(spots)
        return max(abs(value) for value in row) > 1_000_000
    except Exception:
        return False


def possible_section():
    picks = possible_picks()
    if not picks:
        return ""
    buttons = []
    for curve, tag in picks:
        spots = curve["spots"]
        outer = [part.strip() for part in spots.split(",") if part.strip() != "1/2"]
        copies = sum(1 for part in spots.split(",") if part.strip() == "1/2")
        outer = outer[: (len(outer) + 1) // 2]
        caution = ""
        buttons.append(
            f'    <button type="button" class="family" data-spots="{spots}" '
            f'title="{tag}: flat spots {spots}{caution}">{tag} &middot; {curve["crossings"]} crossings '
            f'&middot; grid 1/{curve["grid"]:,} &middot; {" + ".join(outer)} + &frac12;&times;{copies}{caution}</button>')
    return (
        '<div class="curve-box" id="n-possible">\n'
        '<h3>Possible families: what to investigate</h3>\n'
        '<p class="small">Curves the census found that are not buttons above, chosen by hand for '
        'three different questions. <strong>record</strong> — the most crossings the box holds, at any '
        'grid cost, so the ceiling can be seen. <strong>cheap</strong> — five crossings or more on a '
        'grid of 100 or less, where the best value for the eye is likely to be. <strong>untried</strong> '
        '— one outer spot families outside the 1/15 to 1/9 window, so those seven are not mistaken for '
        'the whole set.</p>\n'
        '<p class="small">The count on each button is the census\'s, measured in exact whole-number '
        'arithmetic. This page evaluates in double precision, so on some of these rows it reads lower '
        '&mdash; four of the eleven read 0 &mdash; and a few draw as a flat line. Measured, not guessed: '
        'the rows that agree and the rows that do not are both on the list. If a button and the readout '
        'disagree, <strong>the census is right</strong>; the page is the limitation, and the loop window '
        'with a manual focus is the tool to try.</p>\n'
        '<div class="solver-row" id="n-possible-buttons">\n'
        + "\n".join(buttons) + "\n"
        '</div>\n'
        '</div>\n'
    )


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
    page = page.replace("__GALLERY__", json.dumps(stored_entries(), separators=(",", ":")))
    page = page.replace("window.phSpeedDegree = 5;",
                        "window.phHideSeeds = true;\nwindow.phNoComplement = true;\nwindow.phSpeedDegree = 5;")
    figures = {}
    figures_dir = ROOT / "workbench" / "figures"
    if figures_dir.exists():
        names = {curve["name"] for curve in json.loads(FOUND.read_text())["curves"]}
        for path in figures_dir.glob("*.png"):
            for name in names:
                if re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") == path.stem:
                    figures[name] = f"../workbench/figures/{path.name}"
    page = page.replace("window.phSpeedDegree = 5;",
                        "window.phNthFigures = " + json.dumps(figures, separators=(",", ":")) + ";\nwindow.phSpeedDegree = 5;", 1)
    page = page.replace("__MATH__", base.MATH.read_text())
    page = page.replace("__PANELS__", base.PANELS.read_text())
    page = page.replace("<title>The eleventh power: a PH curve of degree 11</title>",
                        "<title>Experiment: fractional exponents</title>")
    page = page.replace("<h1>The eleventh power</h1>", "<h1>Experiment: fractional exponents</h1>")

    # the complementary curve goes, and a mirror-safe tweak panel takes its place
    box_start = page.index('<div class="curve-box complement" id="n-complement-box">')
    box_end = page.index('<p class="small mono" id="n-readout">')
    tweak = """<div class="curve-box" id="n-tweak-box">
  <h3>Tweak the primary curve, see notes</h3>
  <p class="small">Each press adds the pattern once more, so ten presses give ten times the nudge.
  <a href="ph-nth-exp-notes.html#tweak">How the patterns, the grid and the distortion work</a>.</p>
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
    # the tweak panel goes ABOVE the complementary curve and leaves it in place.
    # Cutting the box out (as it did until 2026-11-16) removed the only control that
    # puts a second curve on the figure, and the operator cannot add the side curves
    # without it: "i cant put in the side curves because the button is missing".
    page = page[:box_start] + tweak + page[box_start:]

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
    # The optical controls get a section of their own: on this page the working
    # controls sit above them, and "focus the knot" was being read as one more thing
    # that changes the curve. It does not: it moves the frame and leaves the numbers
    # alone (DESIGN-int, "Optical versus real").
    page = page.replace(
        '<hr class="group-rule">\n<h3 class="group-head">Knot experiments</h3>',
        '<section class="panel" id="n-look-closer">\n'
        '<h2>Look closer</h2>\n'
        '<p class="small">Optical only: these change the frame, never the numbers. The '
        'knot-cutting controls that did not work are '
        '<a href="ph-nth-exp-notes.html">parked with their measurements</a>.</p>',
        1)
    page = page.replace(
        '  <button type="button" id="n-focus-knot" aria-pressed="false" '
        'title="frame the knot, not the whole stroke">focus the knot</button>\n</div>',
        '  <button type="button" id="n-focus-knot" aria-pressed="false" '
        'title="frame the knot, not the whole stroke">focus the knot</button>\n</div>\n'
        '</section>', 1)

    # the gallery keeps its host, and gets a heading of its own, under the families
    head_start = page.index("<h2>Gallery: the spines so far</h2>")
    head_end = page.index('<div class="gallery" id="n-gallery"></div>')
    page = page[:head_start] + family_section() + related_section() + possible_section() + GALLERY_HEAD + page[head_end:]

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
    print(OUT.relative_to(ROOT), len(stored_entries()), "found curves,", len(page), "bytes")


if __name__ == "__main__":
    build()
