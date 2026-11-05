"""Every named curve the project has, drawn by the project.

    .venv/bin/python scripts/all_curves.py
    open workbench/curves-all.html

No curve here is drawn by hand: each panel is `generators.named_figure` on the
same `NAMED` table the catalogue tests use. If a curve is in the repo, it is on
this page; if it is on this page, it came from the table.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generators as G  # noqa: E402
import heart_forms as H  # noqa: E402

INK, MUTED, RULE, PAPER = "#2e2413", "#7b6c4e", "#d8ccae", "#fbf7ec"


def panel(spec) -> tuple[str, str]:
    item = G.named_data(spec)
    svg = G.named_figure(item, 360, 260)
    label = spec["key"]
    deg = spec.get("deg")
    note = f"degree {deg}" if deg else "sampled"
    return label, (f'<figure class="card">{svg}'
                   f'<figcaption><strong>{label}</strong> · {note}</figcaption></figure>')


def main() -> None:
    cards = []
    missing = []
    for spec in G.NAMED:
        try:
            cards.append(panel(spec))
        except Exception as exc:                     # noqa: BLE001
            missing.append(f"{spec.get('key')}: {type(exc).__name__}")

    preset_cards = []

    hearts = []
    for form in H.FORMS:
        try:
            svg = H.figure(form["branches"](), 360, 300)
            hearts.append(f'<figure class="card">{svg}'
                          f'<figcaption><strong>{form["key"]}</strong> · {form["kind"]}</figcaption></figure>')
        except Exception as exc:                     # noqa: BLE001
            missing.append(f"heart {form.get('key')}: {type(exc).__name__}")

    body = "".join(c for _, c in cards)
    presets = "".join(c for _, c in preset_cards)
    warn = ("<p class='warn'>Not drawn: " + ", ".join(missing) + "</p>") if missing else ""

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Every named curve</title>
<style>
:root{{--paper:{PAPER};--ink:{INK};--muted:{MUTED};--rule:{RULE}}}
*{{box-sizing:border-box}} body{{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}}
main{{max-width:1160px;margin:0 auto;padding:32px 20px 70px}}
h1{{font-size:30px;margin:0 0 6px}} h2{{font-size:20px;margin:26px 0 10px}}
.lede{{color:var(--muted);max-width:900px}}
.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}}
@media (max-width:900px){{.grid{{grid-template-columns:1fr}}}}
.card{{margin:0;background:var(--paper);border:1px solid var(--rule);padding:6px}}
.card svg{{display:block;width:100%;height:auto}}
figcaption{{font:12px/1.5 ui-monospace,Menlo,monospace;color:var(--muted);padding:4px 4px 0}}
.warn{{font:12px ui-monospace,Menlo,monospace;color:#a23b2a}}
</style></head><body><main>
<p class="lede" style="font:11px ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase">curve-lab · generated from NAMED</p>
<h1>Every named curve</h1>
<p class="lede">Drawn by <code>scripts/generators.py</code> itself — the same table the catalogue tests read. {len(cards)} named curves and {len(hearts)} heart forms. Nothing here is hand-drawn.</p>
{warn}
<h2>Named curves</h2>
<div class="grid">{body}</div>
<h2>Degree presets</h2>
<p class="lede">The four degree presets (cubic, quartic, quintic, sextic) have their own renderer and live on <a href="generators.html">generators.html</a>; they are not re-drawn here.</p>
<h2>Hearts</h2>
<p class="lede">{len(hearts)} heart forms from <code>scripts/heart_forms.py</code>; one of them, the Beutel sextic, is the same shape as the sampled heart in the named table.</p>
<div class="grid">{"".join(hearts)}</div>
</main></body></html>
"""
    out = ROOT / "workbench" / "curves-all.html"
    out.write_text(html, encoding="utf-8")
    print(out)
    print(f"{len(cards)} named, {len(preset_cards)} presets, {len(missing)} skipped")
    if missing:
        print("skipped:", "; ".join(missing))


if __name__ == "__main__":
    main()
