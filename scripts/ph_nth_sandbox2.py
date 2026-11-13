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
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_nth_sandbox as base  # noqa: E402
import ph_quintic_metrics as metrics  # noqa: E402

OUT = ROOT / "workbench" / "ph-nth-sandbox-2.html"
FITTED = ROOT / "workbench" / "ph-fitted-curves.json"
LIMIT = 80


def gallery():
    document = json.loads(FITTED.read_text())
    entries = []
    for curve in document["curves"][:LIMIT]:
        measured = metrics.metrics(curve["speedX"], curve["speedY"])
        entries.append({
            "name": curve["name"],
            "speedX": curve["speedX"],
            "speedY": curve["speedY"],
            "bend": round(measured["bend"], 3),
            "pitch": measured["pitch"],
            "from": curve["from"],
            "source": curve.get("source", ""),
        })
    return entries


def build():
    page = base.PAGE
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
    OUT.write_text(page)
    print(OUT.relative_to(ROOT), len(gallery()), "fitted curves")


if __name__ == "__main__":
    build()
