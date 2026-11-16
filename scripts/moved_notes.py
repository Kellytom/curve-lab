"""The notes page for curves taken out of the gallery.

    .venv/bin/python scripts/moved_notes.py

`workbench/moved-curves.json` holds the records; this writes them as a page with their figures,
so a curve moved out of the gallery is still readable and nothing is lost. Moved is not deleted:
the record still carries its rows, its grid and its crossings.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "workbench" / "moved-curves.json"
OUT = ROOT / "workbench" / "moved-curves.html"
FIGURES = ROOT / "workbench" / "figures"

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Curves moved to the notes</title>
<style>
:root{--paper:#fbf7ec;--ink:#2e2413;--muted:#7b6c4e;--rule:#d8ccae}
body{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}
main{max-width:1120px;margin:0 auto;padding:30px 22px 80px}
h1{font-size:26px;margin:0 0 6px}
p{max-width:78ch}
.grid{display:grid;grid-template-columns:repeat(3, minmax(0, 1fr));gap:14px;margin-top:18px}
figure{margin:0;background:var(--paper);border:1px solid var(--rule);padding:8px}
figure img{width:100%;height:auto;display:block;border:1px solid var(--rule);background:#fbf7ec}
figcaption{font:11px/1.4 ui-monospace,Menlo,monospace;color:var(--ink);margin-bottom:4px}
.facts{font:10px/1.4 ui-monospace,Menlo,monospace;color:var(--muted);margin-top:4px}
@media(max-width:760px){.grid{grid-template-columns:minmax(0,1fr)}}
</style></head><body><main>
<h1>Curves moved to the notes</h1>
<p>Out of the found gallery, kept here with their figures. Nothing is deleted: every record still
carries its speed rows, its grid and its crossing count, and the gallery is shorter by exactly
these. __COUNT__ curves.</p>
<div class="grid">
__FIGURES__
</div>
</main></body></html>
"""


def main():
    document = json.loads(SOURCE.read_text())
    curves = document["curves"]
    blocks = []
    for curve in curves:
        slug = re.sub(r"[^a-z0-9]+", "-", curve["name"].lower()).strip("-")
        figure = FIGURES / f"{slug}.png"
        image = (f'<img src="figures/{figure.name}" alt="{curve["name"]}, its HUD picture">'
                 if figure.exists() else "")
        measured = curve.get("measured", {})
        blocks.append(
            f'<figure><figcaption>{curve["name"]}</figcaption>{image}'
            f'<p class="facts">bend {measured.get("bend", "-")} &middot; grid 1/{measured.get("grid", "-")}'
            f' &middot; self {measured.get("self", "-")}</p></figure>')
    OUT.write_text(PAGE.replace("__COUNT__", str(len(curves))).replace("__FIGURES__", "\n".join(blocks)))
    print(OUT.relative_to(ROOT), len(curves), "curves")


if __name__ == "__main__":
    main()
