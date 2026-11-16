"""A review page for the curve figures: old beside new, accept or reject each one.

    .venv/bin/python scripts/curve_figures.py

Two pictures per curve and a decision:

  * **page** — the sandbox's own loop view (`figure.png`), which is what the page draws;
  * **factored** — drawn from the flat spots in exact arithmetic, with y stretched by a
    stated factor so a curve that hugs the axis can be seen (`figure-exact.png`).

Choices live in the browser's storage while you look, and the box at the foot holds the
JSON to hand back: `{"loop-8-11-mid-1": "factored", ...}`. Nothing is applied until that
JSON comes back.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURVES = ROOT / "curves"
OUT = ROOT / "workbench" / "curve-figures.html"

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Curve figures: accept or reject</title>
<style>
:root{--paper:#fbf7ec;--ink:#2e2413;--muted:#7b6c4e;--rule:#d8ccae}
*{box-sizing:border-box}
body{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}
main{max-width:1280px;margin:0 auto;padding:30px 22px 90px}
h1{font-size:26px;margin:0 0 6px}
p{max-width:78ch}
.row{display:grid;grid-template-columns:1fr 1fr;gap:14px;background:var(--paper);
     border:1px solid var(--rule);padding:14px;margin:0 0 18px}
.row h2{grid-column:1 / -1;font-size:17px;margin:0 0 4px}
.row .facts{grid-column:1 / -1;font:11px/1.5 ui-monospace,Menlo,monospace;color:var(--muted)}
.cell img{width:100%;height:auto;display:block;border:1px solid var(--rule);background:#fbf7ec}
.cell .label{font:11px/1.4 ui-monospace,Menlo,monospace;color:var(--muted);margin:0 0 4px}
.cell .missing{display:flex;align-items:center;justify-content:center;height:220px;
  border:1px dashed var(--rule);color:var(--muted);font-size:13px}
.row .decide{grid-column:1 / -1;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
button{font:12px/1.2 ui-monospace,Menlo,monospace;padding:6px 10px;background:#fbf7ec;
  color:var(--ink);border:1px solid var(--rule);border-radius:3px;cursor:pointer}
button.pressed{background:#2e2413;color:#fbf7ec}
.state{font:11px/1.4 ui-monospace,Menlo,monospace;color:var(--muted)}
textarea{width:100%;height:120px;font:12px ui-monospace,Menlo,monospace;padding:8px;
  border:1px solid var(--rule);background:#fffdf7}
</style></head><body><main>
<h1>Curve figures: accept or reject</h1>
<p>Two pictures for each curve. <strong>page</strong> is the sandbox's loop view, drawn from the
speed row in double precision. <strong>factored</strong> is drawn from the flat spots, where
nothing cancels, with y stretched by the factor printed under the picture &mdash; these curves hug
the x axis, so the stretch is what makes the shape visible at all. Nothing is applied until the
JSON at the foot comes back.</p>
__ROWS__
<h2>Decisions</h2>
<p>Your choices, ready to hand back. Nothing else is stored in the repository.</p>
<textarea id="decisions" readonly></textarea>
<p><button type="button" id="copy-decisions">copy the decisions</button>
<button type="button" id="clear-decisions">clear</button>
<span class="state" id="state"></span></p>
</main>
<script>
(function () {
  const key = "curve-figure-decisions";
  const saved = () => { try { return JSON.parse(localStorage.getItem(key) || "{}"); } catch (e) { return {}; } };
  const store = value => localStorage.setItem(key, JSON.stringify(value));
  const show = () => {
    const decisions = saved();
    document.querySelectorAll(".row[data-slug]").forEach(row => {
      const choice = decisions[row.dataset.slug] || "";
      row.querySelectorAll("button[data-choice]").forEach(button => {
        button.classList.toggle("pressed", button.dataset.choice === choice);
      });
      const state = row.querySelector(".state");
      if (state) state.textContent = choice ? `chosen: ${choice}` : "no choice yet";
    });
    const box = document.getElementById("decisions");
    if (box) box.value = JSON.stringify(decisions, null, 1);
    const note = document.getElementById("state");
    if (note) note.textContent = `${Object.keys(decisions).length} decided`;
  };
  document.querySelectorAll(".row[data-slug] button[data-choice]").forEach(button => {
    button.addEventListener("click", () => {
      const row = button.closest(".row");
      const decisions = saved();
      decisions[row.dataset.slug] = button.dataset.choice;
      store(decisions);
      show();
    });
  });
  const copy = document.getElementById("copy-decisions");
  if (copy) copy.addEventListener("click", () => {
    const box = document.getElementById("decisions");
    box.select();
    if (navigator.clipboard) navigator.clipboard.writeText(box.value).catch(() => {});
  });
  const clear = document.getElementById("clear-decisions");
  if (clear) clear.addEventListener("click", () => { store({}); show(); });
  show();
})();
</script></body></html>
"""


def row_for(folder):
    record = json.loads((folder / "curve.json").read_text())
    page_figure = folder / "figure.png"
    exact = folder / "figure-exact.png"
    svg = (folder / "figure-exact.svg")
    stretch = ""
    if svg.exists():
        text = svg.read_text()
        marker = text.find("y stretched")
        if marker > 0:
            stretch = text[marker:text.find("x to be seen", marker) + 1]
    slug = folder.name
    cells = []
    if page_figure.exists():
        cells.append(f'<div class="cell"><p class="label">page (the sandbox loop view)</p>'
                     f'<img src="../curves/{slug}/figure.png" alt="{slug}, page view"></div>')
    else:
        cells.append('<div class="cell"><p class="label">page (withdrawn)</p>'
                     '<div class="missing">the page draws this row as a flat line</div></div>')
    if exact.exists():
        cells.append(f'<div class="cell"><p class="label">factored {stretch}</p>'
                     f'<img src="../curves/{slug}/figure-exact.png" alt="{slug}, factored view"></div>')
    else:
        cells.append('<div class="cell"><p class="label">factored</p>'
                     '<div class="missing">not drawn</div></div>')
    facts = (f'{record.get("crossings", "?")} crossings &middot; grid 1/{record.get("grid", "?")} '
             f'&middot; flat spots {record.get("roots", "")}')
    return (f'<div class="row" data-slug="{slug}">\n<h2>{record.get("name", slug)}</h2>\n'
            f'<p class="facts">{facts}</p>\n' + "\n".join(cells) +
            '\n<div class="decide">'
            '<button type="button" data-choice="factored">accept factored</button>'
            '<button type="button" data-choice="page">keep page</button>'
            '<button type="button" data-choice="none">no figure</button>'
            '<span class="state">no choice yet</span></div>\n</div>')


def build():
    folders = [folder for folder in sorted(CURVES.iterdir())
               if folder.is_dir() and (folder / "curve.json").exists()]
    rows = "\n".join(row_for(folder) for folder in folders)
    OUT.write_text(PAGE.replace("__ROWS__", rows))
    print(OUT.relative_to(ROOT), len(folders), "curves")


if __name__ == "__main__":
    build()
