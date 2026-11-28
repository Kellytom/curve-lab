#!/usr/bin/env python3
"""Keep docs/QUINTIC-EXPLAINED.md true and build its HTML twin.

    .venv/bin/python scripts/quintic_explained.py            # rewrite the numbers, write the twin
    .venv/bin/python scripts/quintic_explained.py --check    # fail when either file is stale

The measured block between the `numbers` markers is computed from
`workbench/quintic-guides.json` with `inkscape/quintic_math.py` — the same
functions the extension runs — so a number in the page cannot be recalled or
typed by hand. The HTML twin is `docs/quintic-explained.html`, generated from
the Markdown with the venv's `markdown` package, so the two cannot drift.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "inkscape"))

import quintic_math as qm  # noqa: E402

MD = ROOT / "docs" / "QUINTIC-EXPLAINED.md"
HTML = ROOT / "docs" / "quintic-explained.html"
SHEET = ROOT / "workbench" / "quintic-guides.json"
START = "<!-- numbers:start -->"
END = "<!-- numbers:end -->"

CASES = ("q6-flattened-arch-10", "q6-parabola-01")
SPANS = (1, 2, 3, 4, 6)


def num(value: float) -> str:
    """Plain decimal, the house style: no exponents, no trailing zeros."""
    if value == 0:
        return "0"
    if value >= 1:
        return f"{value:.1f}"
    if value >= 0.01:
        return f"{value:.3f}".rstrip("0").rstrip(".")
    return f"{value:.6f}".rstrip("0").rstrip(".")


def third_difference(seg):
    """The cubic's constant third derivative (unit parameter, per t^3)."""
    a0, a1, a2, a3 = seg
    return (
        a3[0] - 3 * a2[0] + 3 * a1[0] - a0[0],
        a3[1] - 3 * a2[1] + 3 * a1[1] - a0[1],
    )


def seam_jump(chain):
    """How far the two cubics' third derivatives differ at the shared node."""
    left = third_difference(chain[0])
    right = third_difference(chain[-1])
    return ((left[0] - right[0]) ** 2 + (left[1] - right[1]) ** 2) ** 0.5


def recover(chain):
    """A naive recovery: six arc-length samples of the chain, one quintic through them."""
    return qm.solve_through_samples(qm.samples_along(chain, [i / 5 for i in range(6)]))


def worst_control_miss(original, recovered) -> float:
    return max(
        ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
        for a, b in zip(original, recovered)
    )


def build_table() -> str:
    sheet = json.loads(SHEET.read_text())
    curves = {c["uid"]: c for c in sheet["curves"]}
    rows = []
    for uid in CASES:
        curve = curves[uid]
        control = [tuple(p) for p in curve["spans"][0]["points"]]
        chain = qm.cubic_chain(control, 2)
        recovered = recover(chain)
        cells = [num(qm.measure_max_error(control, qm.cubic_chain(control, n))) for n in SPANS]
        rows.append(
            "| `%s` | %s | %s | %s |"
            % (
                uid,
                " | ".join(cells),
                num(seam_jump(chain)),
                num(worst_control_miss(control, recovered)),
            )
        )

    header = (
        "| curve on the sheet | "
        + " | ".join("1 span" if n == 1 else f"{n} spans" for n in SPANS)
        + " | C3 jump at the seam, 2 spans (px) | worst recovered point (px) |"
    )
    rule = "|" + "---|" * (len(SPANS) + 3)
    note = (
        "\nMeasured in the sheet's own units (the cages are in px) by "
        "`scripts/quintic_explained.py`, which calls the extension's "
        "`quintic_math.py`. The last two columns test the \"hidden quintic\" claim: "
        "the seam jump is the difference between the two cubics' third derivatives "
        "at the shared node, and the recovered point is the worst of the six points "
        "a naive recovery gets back from the two-cubic chain.\n"
    )
    return "\n".join([START, "", header, rule, *rows, note, END])


def render(markdown_text: str) -> str:
    import markdown

    body = markdown.markdown(
        markdown_text,
        extensions=["tables", "fenced_code", "toc", "sane_lists"],
        output_format="html5",
    )
    return HTML_TEMPLATE.replace("{{body}}", body)


HTML_TEMPLATE = """<!doctype html>
<html lang="en-GB">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The quintic in Inkscape — Curve Lab</title>
<style>
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  body {
    margin: 0 auto; padding: 2.5rem 1.25rem 5rem; max-width: 46rem;
    font: 17px/1.6 "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
    color: #17150f; background: #fffdf7;
  }
  h1, h2, h3, h4 { font-family: "Avenir Next", "Helvetica Neue", Arial, sans-serif;
    line-height: 1.25; margin: 2.2rem 0 0.6rem; }
  h1 { font-size: 2rem; margin-top: 0; }
  h2 { font-size: 1.35rem; border-top: 1px solid #e3ddcc; padding-top: 1.4rem; }
  h3 { font-size: 1.05rem; }
  p, li { max-width: 65ch; }
  code, pre { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 0.86em; }
  code { background: #f2eddf; padding: 0.1em 0.3em; border-radius: 3px; }
  pre { background: #f7f2e6; border: 1px solid #e3ddcc; padding: 0.9rem 1rem;
    overflow-x: auto; border-radius: 4px; }
  pre code { background: none; padding: 0; }
  table { border-collapse: collapse; margin: 1rem 0; font-size: 0.92em;
    font-family: "Avenir Next", "Helvetica Neue", Arial, sans-serif;
    display: block; overflow-x: auto; }
  th, td { border-bottom: 1px solid #e3ddcc; padding: 0.4rem 0.7rem; text-align: left;
    white-space: nowrap; }
  th { background: #f7f2e6; font-weight: 600; }
  blockquote { margin: 1rem 0; padding: 0.2rem 1rem; border-left: 3px solid #c9b98a;
    color: #4a4335; }
  a { color: #7a3b00; }
  hr { border: 0; border-top: 1px solid #e3ddcc; margin: 2.5rem 0; }
  .foot { margin-top: 3rem; font-size: 0.85em; color: #6b6455; }
</style>
{{body}}
"""


def main(argv: list[str]) -> int:
    check = "--check" in argv
    text = MD.read_text()
    if START not in text or END not in text:
        print(f"missing {START} / {END} in {MD}")
        return 1
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    fresh = head + build_table() + tail
    page = render(fresh)

    if check:
        stale = []
        if fresh != text:
            stale.append(str(MD))
        if HTML.exists() and HTML.read_text() != page:
            stale.append(str(HTML))
        if stale:
            print("stale: " + ", ".join(stale) + "\nrun: .venv/bin/python scripts/quintic_explained.py")
            return 1
        print("ok: the explainer and its twin match the computed numbers")
        return 0

    MD.write_text(fresh)
    HTML.write_text(page)
    print(f"wrote {MD.relative_to(ROOT)}")
    print(f"wrote {HTML.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
