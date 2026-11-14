"""The experimental sandbox: the same page as part 2, with fractional exponents.

    .venv/bin/python scripts/ph_nth_sandbox_exp.py

The speed rows may step by 1, 1/2, 1/3 or 1/4, so a row can carry t^0.5, t^1.5,
t^2.5 (5/2), t^3.5 (7/2) and so on. With a step of 1/2 the row is a polynomial in
sqrt(t): a flat spot at u = 1/9 sits at t = 1/81.

There is no gallery on this page. It is for trying things, so a curve under test
is not mixed in with the ones we keep. The maths follows the step
(`scripts/ph_math.js`); the grid and the inflection count are reported as not
applicable, because neither exists for a fractional exponent.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_nth_sandbox as base  # noqa: E402

OUT = ROOT / "workbench" / "ph-nth-sandbox-exp.html"

STEP_SELECT = ''

def build():
    page = base.PAGE
    page = page.replace("__GALLERY__", "[]")
    page = page.replace("__MATH__", base.MATH.read_text())
    page = page.replace("__PANELS__", base.PANELS.read_text())
    page = page.replace("<title>The eleventh power: a PH curve of degree 11</title>",
                        "<title>Experiment: fractional exponents</title>")
    page = page.replace("<h1>The eleventh power</h1>", "<h1>Experiment: fractional exponents</h1>")
    # no gallery on this page: drop its heading, its note and its host, so the
    # seeds have nothing to render into
    start = page.index("<h2>Gallery: the spines so far</h2>")
    end = page.index('<div class="gallery" id="n-gallery"></div>') + len('<div class="gallery" id="n-gallery"></div>')
    page = page[:start] + page[end:]
    # the step applies from the first draw, not only once the select changes
    page = page.replace("window.phNthGallery = [];", "window.phNthGallery = [];\nwindow.phPowerStep = 0.5;")
    # fifteen numbers per axis, so step 1/2 reaches t^7: the two rows of the
    # ladder are doubled from the twelve that part 1 opens with
    page = page.replace("window.phSpeedDegree = 5;", "window.phSpeedDegree = 14;")
    page = page.replace(
        "<p>One row of numbers for <code>x</code> and one for <code>y</code>, from <code>t^0</code> upward.",
        "<p class=\"small\"><strong>Experimental.</strong> The rows below step by the exponent chosen "
        "at the top: 1/2 gives <code>t^0.5</code>, <code>t^1.5</code>, <code>t^2.5</code> (5/2), "
        "<code>t^3.5</code> (7/2). Bend and closest are measured from the curve; the grid and the "
        "inflection count are marked not applicable, because neither exists off the whole powers. "
        "There is no gallery on this page: it is for trying things.</p>\n"
        "<p>One row of numbers for <code>x</code> and one for <code>y</code>, from <code>t^0</code> upward.")
    page = page.replace("<p>Part 1 carries curves whose speeds", "<p>Part 1 carries curves whose speeds")
    OUT.write_text(page)
    print(OUT.relative_to(ROOT), len(page), "bytes")


if __name__ == "__main__":
    build()
