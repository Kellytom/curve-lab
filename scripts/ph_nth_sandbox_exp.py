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
    ordered = sorted(newer,
                     key=lambda curve: (-curve.get("measured", {}).get("self", 0),
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
            "source": (f"flat spots {curve.get('provenance', {}).get('roots', '')}; "
                       f"{recorded.get('meetings', 0)} meetings, {recorded.get('self', 0)} self-crossings"),
        })
    return entries


def build():
    page = base.PAGE
    page = page.replace("__GALLERY__", json.dumps(found_entries(), separators=(",", ":")))
    page = page.replace("window.phSpeedDegree = 5;", "window.phHideSeeds = true;\nwindow.phSpeedDegree = 5;")
    page = page.replace("__MATH__", base.MATH.read_text())
    page = page.replace("__PANELS__", base.PANELS.read_text())
    page = page.replace("<title>The eleventh power: a PH curve of degree 11</title>",
                        "<title>Experiment: fractional exponents</title>")
    page = page.replace("<h1>The eleventh power</h1>", "<h1>Experiment: fractional exponents</h1>")

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
        "  const wanted = (window.phNthGallery || []).find(entry => entry.name === 'lace-1of10-3-2');\n"
        "  if (wanted && window.phNthLoad) window.phNthLoad(wanted);\n"
        "})();\n"
        "</script>\n"
    )
    page = page.replace("</body></html>", starter + "</body></html>")
    OUT.write_text(base.stamped(page))
    print(OUT.relative_to(ROOT), len(found_entries()), "found curves,", len(page), "bytes")


if __name__ == "__main__":
    build()
