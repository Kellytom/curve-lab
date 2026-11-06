"""showcase-effects.html: the effects layer.

Clouds now, and the composite curves they belong to — Euler clouds built from
the same grammar. The showcase keeps the curve argument; this page holds the
effects that are made *from* those curves.

    .venv/bin/python scripts/showcase_effects.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import showcase as S  # noqa: E402
from showcase_catalogue import FAMILIES  # noqa: E402

INK, MUTED, PAPER = S.INK, S.MUTED, S.PAPER


def main() -> int:
    clouds = next(f for f in FAMILIES if f[0] == "clouds")
    panels = clouds[3]
    rows = [panels[i:i + 3] for i in range(0, len(panels), 3)]
    body = "".join(
        '<div class="row">' + "".join(
            S.panel(p["fig"], p["title"], p["curves"], p["note"],
                    dots=p["dots"], key=p["key"], curve=p["curve"])
            for p in chunk) + "</div>"
        for chunk in rows)
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Showcase effects · clouds</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:30px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 18px}}
h2{{font:600 12px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.10em;
   text-transform:uppercase;color:{MUTED};margin:30px 0 8px}}
.row{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:0 0 14px}}
.fig{{display:block;background:{PAPER};border:1px solid #d8ccae;padding:8px}}
svg{{display:block;width:100%;height:auto}}
.note{{font:12px/1.6 ui-monospace,Menlo,monospace;color:{MUTED}}}
@media(max-width:900px){{.row{{grid-template-columns:1fr}}}}
</style></head><body><main>
<h1>Showcase effects</h1>
<p class="lead">Effects made from the curves, not curves themselves: the cloud
layer now, and the composite Euler clouds next.</p>
<p class="note"><a href="showcase.html">← the showcase</a> ·
<a href="showcase-notes.html">the notes</a></p>

<h2>34 · Cloud effects</h2>
<p class="note">the whole veil and its six billow layers</p>
{body}

<h2>Composite curves</h2>
<p class="note">Euler clouds: billow layers built from Euler spans rather than
sampled points, so each layer carries its own curvature law. To come — the
section is here so the page has its place.</p>
</main></body></html>
'''
    out = ROOT / "workbench" / "showcase-effects.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
