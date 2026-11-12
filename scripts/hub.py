"""Build the workbench hub and put a shared bar on every input page.

    .venv/bin/python scripts/hub.py

Two jobs, one source. `workbench/manifest.json` says what each input page is
for; this script reads that, reads each page for its first SVG (so the
thumbnail is the page's own drawing, not a copy), and writes the hub. Then it
injects the same one-line bar into every listed page, guarded so a re-run
replaces rather than stacks.

Run this **after** any page generator: a generator rewrites its page and the
bar goes with it.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / "workbench"
MANIFEST = WB / "manifest.json"
from overlay_lattice import overlay_html  # noqa: E402
HUB = WB / "workbench.html"
MARK_A, MARK_B = "<!-- hub-bar -->", "<!-- /hub-bar -->"

INK, GOLD, MUTED, LINE, PAPER, CARD = (
    "#2e2413", "#8c6a21", "#7b6c4e", "#d8ccae", "#f6f1e4", "#fffdf7")

DECISIONS = """
<section class="decision">
  <h2>I want a curve</h2>
  <p>You have a shape in mind, or you need points that a machine can cut. If the
  numbers are the design — a degree, a few integers, a step — start in
  <strong>Generators</strong>, where the curve comes out with whole-number
  control points and you are told what grid it needs. If you are following a
  known profile (a hanging chain, a spiral), the fitted studies show how close a
  small number of cubics gets, and where it stops.</p>
  <p class="one"><a href="generators.html">→ Generators</a></p>
</section>

<section class="decision">
  <h2>I want a terminal</h2>
  <p>A stroke that simply stops looks like an accident. A terminal is the
  decision about how it ends: a cap that closes the end, a taper that thins it,
  or a point. Start with the <strong>piece model</strong>, which carries a kind,
  a reach and a fold, and refuses a terminal that would turn the stroke back on
  itself. The recovered corpus shows what real ends actually measure.</p>
  <p class="one"><a href="piece-model.html">→ Piece model and terminals</a></p>
</section>

<section class="decision">
  <h2>I want a strand</h2>
  <p>One line that swings — the long curve of a leaf edge, a volute, a drape.
  A strand is a chain, and the question is always how many segments buy how much
  fidelity. Start from the <strong>recovered spirals</strong>: 121 real spines,
  each tagged with the curve family it was drawn from, so you can see what the
  old pages actually did before deciding what yours should do.</p>
  <p class="one"><a href="spirals/index.html">→ Recovered spirals</a></p>
</section>

<section class="decision">
  <h2>I want a sheet</h2>
  <p>A whole ornament, or a page of them: fleur, acanthus, palmette, and the
  primals underneath. This is where pieces, strands and terminals are assembled
  and where the work is ordered. Start with the <strong>ornament board</strong>:
  85 plates, 26 work items and 11 open decisions, with a beginner gloss for
  every word the other pages assume.</p>
  <p class="one"><a href="ornament-board.html">→ Ornament board</a></p>
</section>
"""

CSS = """
:root{--paper:%(paper)s;--card:%(card)s;--ink:%(ink)s;--muted:%(muted)s;
--gold:%(gold)s;--line:%(line)s;
--mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
--serif:"EB Garamond",Georgia,"Palatino Linotype",Palatino,serif}
*{box-sizing:border-box}
body{margin:0;color:var(--ink);font:16px/1.55 var(--serif);
background:radial-gradient(900px 440px at 12%% -8%%,#fcf9ef 0,transparent 60%%),var(--paper)}
main{max-width:980px;margin:0 auto;padding:34px 22px 80px}
h1{font-size:30px;margin:0 0 6px}
.lead{color:var(--gold);margin:0 0 26px;font-size:17px}
.showcase{margin:0 0 18px;padding:12px 16px;border-left:4px solid var(--gold);background:#fffdf7;font:15px/1.5 Georgia,serif}
.showcase a{font-size:18px;font-weight:600;color:var(--gold);text-decoration:none}
.showcase a:hover{text-decoration:underline}
.showcase span{color:var(--muted);font-size:13px}
h2{font:600 11px/1.2 var(--mono);letter-spacing:.12em;text-transform:uppercase;
color:var(--muted);margin:0 0 8px}
.decision{background:var(--card);border:1px solid var(--line);border-radius:7px;
padding:16px 18px;margin:0 0 14px}
.decision p{font-size:15px;margin:0 0 10px;max-width:70ch}
.decision .one{margin:0}
.decision .one a{font:600 13px/1.2 var(--mono);text-decoration:none}
a{color:var(--gold)}
a:hover{text-decoration:underline}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:8px 0 26px}
.card{background:var(--card);border:1px solid var(--line);border-radius:7px;
padding:12px;display:flex;flex-direction:column;gap:8px}
.card .thumb{height:120px;display:flex;align-items:center;justify-content:center;
overflow:hidden;background:#fffdf7;border:1px solid #f0e8d4;border-radius:4px}
.card .thumb.empty{font:10px/1.4 var(--mono);color:#a89b7e}
.card .thumb svg{max-width:100%%;max-height:118px;width:auto;height:auto}
.card h3{font:600 15px/1.3 var(--serif);margin:0;color:var(--ink)}
.card .purpose{margin:0;font-size:13.5px;color:var(--ink)}
.card .io{margin:0;font:11px/1.45 var(--mono);color:var(--muted)}
.card .io b{color:var(--gold);font-weight:600}
.grouphead{font:600 11px/1.2 var(--mono);letter-spacing:.12em;text-transform:uppercase;
color:var(--gold);margin:22px 0 8px}
.hub-bar{display:flex;gap:10px;flex-wrap:wrap;align-items:baseline;
padding:7px 22px;background:#efe7d3;border-bottom:1px solid var(--line);
font:11px/1.4 var(--mono);color:%(muted)s}
.hub-bar a{color:%(gold)s;text-decoration:none;font-weight:600}
.hub-bar b{color:%(gold)s;font-weight:600}
footer{margin-top:34px;font:11px/1.5 var(--mono);color:var(--muted)s}
@media(max-width:720px){.cards{grid-template-columns:1fr}}
""" % dict(paper=PAPER, card=CARD, ink=INK, muted=MUTED, gold=GOLD, line=LINE)


def load():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def first_svg(page: Path, limit: int = 60000):
    if not page.exists():
        return None
    raw = page.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"<svg\b.*?</svg>", raw, re.S)
    if not m or len(m.group(0)) > limit:
        return None
    svg = m.group(0)
    svg = re.sub(r'(<svg\b[^>]*?)\swidth="[^"]*"', r"\1", svg, count=1)
    svg = re.sub(r'(<svg\b[^>]*?)\sheight="[^"]*"', r"\1", svg, count=1)
    return "\n".join(line.rstrip() for line in svg.splitlines())


BAR_CSS = (
    ".hub-bar{display:flex;flex-wrap:wrap;gap:14px;align-items:baseline;"
    "margin:0;padding:7px 22px;background:#efe7d3;border-bottom:1px solid #d8ccae;"
    "font:11px/1.5 ui-monospace,'SF Mono',Menlo,Consolas,monospace;color:#7b6c4e}"
    ".hub-bar a{color:#8c6a21;text-decoration:none;font-weight:600}"
    ".hub-bar a:hover{text-decoration:underline}"
    ".hub-bar b{color:#8c6a21;font-weight:600}"
    ".hub-bar .grp{text-transform:uppercase;letter-spacing:.1em}"
    "@media(max-width:640px){.hub-bar{padding:6px 12px;gap:8px}}"
)


def bar(entry: dict) -> str:
    return (f'{MARK_A}<style>{BAR_CSS}</style>'
            f'<div class="hub-bar">'
            f'<a href="workbench.html">&lt;- all inputs</a>'
            f'<span class="grp">{entry["group"]}</span>'
            f'<span><b>in</b> {entry["inputs"]} | '
            f'<b>out</b> {entry["outputs"]}</span></div>{MARK_B}')


def inject(entry: dict) -> str:
    path = WB / entry["file"]
    if not path.exists() or path == HUB:
        return "missing"
    raw = path.read_text(encoding="utf-8")
    before = raw
    tag = bar(entry)
    if MARK_A in raw:
        raw = re.sub(re.escape(MARK_A) + r".*?" + re.escape(MARK_B), tag,
                     raw, flags=re.S)
        state = "replaced"
    else:
        m = re.search(r"<body[^>]*>", raw)
        if not m:
            return "no-body"
        raw = raw[:m.end()] + "\n" + tag + raw[m.end():]
        state = "added"
    if raw == before:
        return "unchanged"
    path.write_text(raw, encoding="utf-8")
    return state


def card(entry: dict) -> str:
    svg = first_svg(WB / entry["file"])
    thumb = f'<div class="thumb">{svg}</div>' if svg else '<div class="thumb"></div>'
    return f"""<article class="card">
  {thumb}
  <h3><a href="{entry['file']}">{entry['title']}</a></h3>
  <p class="purpose">{entry['purpose']}</p>
  <p class="io"><b>in</b> {entry['inputs']}<br><b>out</b> {entry['outputs']}</p>
</article>"""


def build(manifest):
    groups = [g["key"] for g in manifest["groups"]]
    labels = {g["key"]: g["label"] for g in manifest["groups"]}

    sections = []
    for g in groups:
        pages = [p for p in manifest["pages"] if p["group"] == g]
        if not pages:
            continue
        sections.append(f'<p class="grouphead">{labels[g]} | {len(pages)}</p>'
                        f'<div class="cards">{"".join(card(p) for p in pages)}</div>')

    hub = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Clothoid workbench — choose by intent</title>
<style>{CSS}</style>
</head>
<body>
<main>
<h1>The workbench</h1>
<p class="showcase"><a href="showcase.html">→ The showcase: every curve on one page</a><br>
<span>Every named curve, every stem cut, every family — the inventory to choose
from before drawing anything in Inkscape.</span></p>
<p class="lead">Pick the kind of decision you are making. Each one names the
page that starts it; the full list is underneath.</p>
{DECISIONS}
<h2 style="margin-top:30px">Everything, by page</h2>
<p style="margin:0 0 6px;font-size:14px;color:var(--muted);max-width:70ch">
Every card below is read from the page itself — its first drawing is the
thumbnail — so nothing here can drift from what the page actually shows.</p>
{''.join(sections)}
<footer>generated by scripts/hub.py from workbench/manifest.json |
{len(manifest['pages'])} pages · do not edit by hand</footer>
</main>
</body></html>
"""
    HUB.write_text(hub, encoding="utf-8")


def main() -> int:
    manifest = load()
    build(manifest)
    counts = {}
    for p in manifest["pages"]:
        st = inject(p)
        counts[st] = counts.get(st, 0) + 1
    # one lattice pass over every page, then rebuild so the hub thumbnails
    # are cut from the decorated figures rather than the bare ones.
    for p in manifest["pages"]:
        path = WB / p["file"]
        if path.exists():
            raw = path.read_text(encoding="utf-8")
            new = overlay_html(raw)
            if new != raw:
                path.write_text(new, encoding="utf-8")
    build(manifest)
    print(HUB)
    print("  pages:", len(manifest["pages"]), "·", ", ".join(
        f"{k} {v}" for k, v in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
