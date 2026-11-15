"""Part 2: the same sandbox, with a gallery of fitted showcase curves.

    .venv/bin/python scripts/ph_fit_showcase.py --write 80   # refresh the fits
    .venv/bin/python scripts/ph_nth_sandbox2.py
    open workbench/ph-nth-sandbox-2.html

Part 1 carries exact curves: their speeds are the curves. Part 2 carries
*fitted* ones: each showcase curve is sampled, its speed taken as sqrt(z'),
a degree-5 polynomial fitted by least squares, and the residual recorded. The
cells are labelled `fitted`, with the rms in the expanded panel, so the grade
is never in doubt. If a fitted curve is worth keeping, it moves to part 1 by
name.

The page is generated: edit this file, never the HTML.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_nth_sandbox as base  # noqa: E402
import ph_quintic_metrics as metrics  # noqa: E402

OUT = ROOT / "workbench" / "ph-nth-sandbox-2.html"
FITTED = ROOT / "workbench" / "ph-fitted-curves.json"
FOUND = ROOT / "workbench" / "found-curves.json"
LIMIT = 80


def curve_points(sx, sy, n=240):
    x = y = 0.0
    points = [(0.0, 0.0)]
    for i in range(n):
        t = (i + 0.5) / n
        p = sum(c * t ** k for k, c in enumerate(sx))
        q = sum(c * t ** k for k, c in enumerate(sy))
        x += (p * p - q * q) / n
        y += 2 * p * q / n
        points.append((x, y))
    return points


def normalised(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    size = max(1e-12, max(xs) - min(xs), max(ys) - min(ys))
    return [(x / size, y / size) for x, y in points]


def deviation(sx, sy, tx, ty):
    a = normalised(curve_points(sx, sy))
    b = normalised(curve_points(tx, ty))
    return max(math.hypot(ax - bx, ay - by) for (ax, ay), (bx, by) in zip(a, b))


def simplify(sx, sy, tolerance=0.03):
    """A rough grade: the speeds divided by a common step and rounded, so they
    become small integers (at most 8, 16, 32 ... of the largest). The coarsest
    step whose normalised curve stays within `tolerance` of the fit is kept.
    Dividing by a constant only rescales the curve, so the shape is untouched
    by the change of units; the rounding is the only simplification."""
    largest = max(abs(v) for v in sx + sy) or 1
    for divisions in (8, 16, 32, 64, 128, 256, 1024):
        step = largest / divisions
        simple_x = [round(v / step) for v in sx]
        simple_y = [round(v / step) for v in sy]
        if not any(simple_x) and not any(simple_y):
            continue
        error = deviation(sx, sy, simple_x, simple_y)
        if error <= tolerance:
            break
    measured = metrics.metrics(simple_x, simple_y)
    return {
        "speedX": simple_x,
        "speedY": simple_y,
        "pitch": measured["pitch"],
        "bend": round(measured["bend"], 3),
        "deviation": round(error, 4),
    }


def found_gallery():
    """The root walk's finds, first in the gallery.

    These are exact, not fitted: their speeds are the curve. They sit here
    because this is the page the operator reads them on. `simple` is left out
    on purpose, so the transfer button does not offer a rough grade of a curve
    that needs no grading.
    """
    if not FOUND.exists():
        return []
    import curve_records
    document = curve_records.read(FOUND)
    # part 2 keeps the earlier family; the newer finds live on the experimental page
    curves = sorted([curve for curve in document["curves"]
                     if curve.get("provenance", {}).get("batch", "first") == "first"],
                    key=lambda curve: (-curve.get("measured", {}).get("meetings", 0),
                                       curve.get("measured", {}).get("grid", 0),
                                       curve.get("measured", {}).get("bend", 0)))
    entries = []
    for curve in curves:
        # the page wants flat rows and a number to print; the file keeps terms and
        # the measurements the search made, so both are derived here, once
        x, y = curve_records.rows_from_terms(curve["terms"])
        recorded = curve.get("measured", {})
        entries.append({
            "name": curve["name"],
            "terms": curve["terms"],
            "speedX": x,
            "speedY": y,
            "bend": recorded.get("bend"),
            "pitch": recorded.get("grid"),
            "original": [],
            "from": "found",
            "truncation": curve.get("truncation"),
            "source": (f"roots {curve.get('provenance', {}).get('roots', '')}; "
                       f"{recorded.get('meetings', 0)} meetings, {recorded.get('self', 0)} self-crossings"),
        })
    return entries


def gallery():
    document = json.loads(FITTED.read_text())
    entries = apply_operator_order(operator_pins() + found_gallery())
    for curve in document["curves"][:LIMIT]:
        measured = metrics.metrics(curve["speedX"], curve["speedY"])
        entries.append({
            "name": curve["name"],
            "speedX": curve["speedX"],
            "speedY": curve["speedY"],
            "bend": round(measured["bend"], 3),
            "pitch": measured["pitch"],
            "original": curve.get("original", []),
            "from": curve["from"],
            "source": curve.get("source", ""),
            "simple": simplify(curve["speedX"], curve["speedY"]),
        })
    return entries


def operator_pins():
    """The six curves the operator keeps as the knotlike examples, first in the section.

    Pasted from the sandbox as JSON on 2026-11-14. Every one is symmetric, and the
    repeated rows are kept as he saved them (`knot` and `knot-2` are `wave3` padded
    to ten numbers, which is the same polynomial).
    """
    pasted = [
        ("wave3", [1, 0, 0, 0, 0, 0], [-5, 46, -108, 72, 0, 0], 2.329, 105),
        ("knot", [1] + [0] * 9, [-5, 46, -108, 72] + [0] * 6, 2.329, 105),
        ("bud", [0.5] + [0] * 9, [-5, 46, -108, 72] + [0] * 6, 1.222, 420),
        ("knot-2", [1] + [0] * 9, [-5, 46, -108, 72] + [0] * 6, 2.329, 105),
        ("wave5", [1, 0, 0, 0, 0, 0], [-10, 137, -675, 1530, -1620, 648], 1.374, 462),
        ("hersheys copy", [1] + [0] * 9, [-3, 30, -120, 240, -240, 96] + [0] * 4, 10, 11),
        # found by the operator 2026-11-14: two mirrored pairs and one middle, with
        # a bow of 9, which is what keeps it from reading as a flat band
        ("wave-1of7-1of5-1-bow9", [1, 9, -9, 0, 0, 0],
         [-24, 394, -2263, 5592, -6125, 2450], 1.525, 6930),
        # operator's find 2026-11-14: the lace's low powers with a small tail at
        # t^11..t^14. The tail loosens the knot and breaks the mirror on purpose.
        ("loose-knot-tail14",
         [3, 0, -16, 0, 16, 0, 0, 0, 0, 0, 0, -1, 1, 0, -1],
         [-9, 0, 154, 0, -808, 0, 1872, 0, -2000, 0, 800, -1, 1, -1, -2], 1.756, 3465),
    ]
    return [{
        "name": name,
        "speedX": speed_x,
        "speedY": speed_y,
        "bend": bend,
        "pitch": pitch,
        "original": [],
        "from": "operator",
        "source": "the operator's knotlike examples, pasted 2026-11-14",
    } for name, speed_x, speed_y, bend, pitch in pasted]


# The operator's ordering, 2026-11-14, stated by NAME. It used to be stated by
# position, and adding one curve shifted every number, so the section re-shuffled
# on its own. Names do not drift.
#   this block sits below the anchor, in this order
DEMOTE = ("wave5", "lace-1of9-3", "lace-1of12-3", "wave-1of5-1of3-3", "lace-1of8-1of3-0",
          "lace-1of10-3", "wave-1of8-1of3-2", "wave-1of5-1of4-3", "wave-1of6-2")
AFTER = "wave-1of3-2"
# single moves, by name: the subjects keep their own order under the anchor
MOVES = ((("wave-1of7-3",), "lace-1of8-3"),
         (("lace-1of9-3", "lace-1of12-3"), "wave-1of7-3"),
         (("lace-1of10-3",), "lace-1of12-3"))


def apply_operator_order(entries):
    """The operator's order: the named block below its anchor, then the named moves."""
    names = [entry["name"] for entry in entries]
    moving = [entry for entry in entries if entry["name"] in DEMOTE]
    kept = [entry for entry in entries if entry["name"] not in DEMOTE]
    if AFTER in [entry["name"] for entry in kept]:
        cut = next(i for i, entry in enumerate(kept) if entry["name"] == AFTER) + 1
        ordered = kept[:cut] + moving + kept[cut:]
    else:
        ordered = kept + moving
    for subjects, anchor in MOVES:
        lifted = [entry for entry in ordered if entry["name"] in subjects]
        if not lifted:
            continue
        for entry in lifted:
            ordered.remove(entry)
        place = next((i for i, entry in enumerate(ordered) if entry["name"] == anchor), None)
        if place is None:
            ordered.extend(lifted)
        else:
            ordered[place + 1:place + 1] = lifted
    return ordered


def knot_names():
    """The knotlike section, in the operator's order: his six, then every find.

    It reads one list, the same one the gallery is built from, so a move made in
    `apply_operator_order` shows up in the section as well.
    """
    return [entry["name"] for entry in apply_operator_order(operator_pins() + found_gallery())]


def build():
    page = base.PAGE
    knots = json.dumps(knot_names(), separators=(",", ":"))
    page = page.replace("window.phNthGallery = __GALLERY__;",
                        "window.phNthGallery = __GALLERY__;\n"
                        f"window.phNthKnots = {knots};")
    page = page.replace("__GALLERY__", json.dumps(gallery(), separators=(",", ":")))
    page = page.replace("__MATH__", base.MATH.read_text())
    page = page.replace("__PANELS__", base.PANELS.read_text())
    page = page.replace("<title>The eleventh power: a PH curve of degree 11</title>",
                        "<title>Part 2: fitted curves at degree 11</title>")
    page = page.replace("<h1>The eleventh power</h1>", "<h1>Part 2: fitted curves</h1>")
    page = page.replace(
        "<p>The septic sandbox stops at position degree 7,",
        "<p>Part 1 carries curves whose speeds <em>are</em> the curve. This page carries "
        "<strong>fitted</strong> curves: each showcase path sampled, its speed taken as the square "
        "root of the derivative, a degree-5 polynomial fitted, and the residual recorded. "
        "The sharpest fits come first. If one is worth keeping, it moves to part 1 by name.</p>\n"
        "<p class=\"small\">The old text follows for reference. The septic sandbox stops at position degree 7,")
    page = page.replace(
        "<p class=\"small\">Spine only, one cell per curve, two columns. Started with the first two curves made\n"
        "here, then everything the septic sandbox and the quintic page already carried. Degree 7 curves are\n"
        "padded with a zero pair, which changes nothing: the speed is the same polynomial.</p>",
        "<p class=\"small\">Spine only, one cell per curve, two columns, best fit first. Every cell is\n"
        "<strong>fitted</strong>, not exact: the tag says so and the expanded panel gives the rms as a\n"
        "fraction of the curve's size. The showcase has no speed polynomials, so this is the only honest\n"
        "way to bring its shapes here.</p>")
    OUT.write_text(base.stamped(page))
    print(OUT.relative_to(ROOT), len(gallery()), "fitted curves")


if __name__ == "__main__":
    build()
