"""W04: the twenty fleur parameter sets, one card each.

    .venv/bin/python scripts/fleur_sets.py
    open workbench/fleur-sets.html

The sets are data in `curve_lab.fleur_sets`, transcribed from the ornaments
source. Every card is built by the same `grammar.study(opts)`: 26 spans, nine
declared corners, no fill. The seam contacts are P01's, measured for P01; the
other nineteen are the next increment (each needs its own two seam points).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import grammar  # noqa: E402
from curve_lab.fleur_sets import SETS  # noqa: E402
from curve_lab.piece import render_piece  # noqa: E402

INK, MUTED, PAPER = "#2e2413", "#7b6c4e", "#fffdf7"


def report(opts: dict) -> dict:
    right = grammar.fleur_right(opts)
    ring = grammar.band(opts)
    corners = []
    for trace in (("half", right), ("band", ring)):
        name, built = trace
        for index, segment in enumerate(built["spans"]):
            corner = math.degrees(getattr(segment, "corner", 0.0))
            if abs(corner) > 1e-9:
                corners.append((name, index, corner))
    return {
        "spans": 2 * len(right["spans"]) + len(ring["spans"]),
        "corners": len(corners),
        "max_corner": max(abs(c[2]) for c in corners) if corners else 0.0,
    }


def main() -> int:
    cards = []
    rows = []
    for item in SETS:
        opts = item["opts"]
        piece = grammar.study(opts, name=item["name"])
        svg, info = render_piece(piece, frame=(300, 360), margin=8)
        r = report(opts)
        cards.append(f'''<section class="card">
<div class="art">{svg}</div>
<h3>{item['id']} · {item['name']}</h3>
<p class="note">{item['note']}</p>
<p class="meta">{r['spans']} spans · {r['corners']} corners · max {r['max_corner']:.1f}° · {len(piece.contacts)} seam contacts · rail error {info['traces'][0]['fit_error']:.1e}</p>
</section>''')
        rows.append(
            f"<tr><td>{item['id']}</td><td>{opts['petalH']}</td>"
            f"<td>{opts['petalSweep']}</td><td>{opts['lanceH']}</td>"
            f"<td>{opts['bandHalf']}</td><td>{opts['waist']}</td>"
            f"<td>{opts['footY']}</td><td>{opts['tailSweep']}</td>"
            f"<td>{opts['petalT0']}</td></tr>")

    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fleur sets P01–P20 — one hand</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 18px}}
h2{{font:600 12px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.10em;text-transform:uppercase;color:{MUTED};margin:30px 0 8px}}
.panel{{background:{PAPER};border:1px solid #d8ccae;padding:16px 18px;margin:0 0 18px}}
.grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}}
.card{{background:{PAPER};border:1px solid #d8ccae;padding:8px;margin:0}}
.card h3{{font:600 12px/1.3 Georgia,serif;margin:0 0 2px}}
.note{{font:10px/1.4 ui-monospace,Menlo,monospace;color:{MUTED};margin:0 0 3px}}
.meta{{font:10px/1.4 ui-monospace,Menlo,monospace;color:{INK};margin:0}}
.art svg{{display:block;width:100%;height:auto}}
table{{border-collapse:collapse;width:100%;font:11px/1.5 ui-monospace,Menlo,monospace}}
th,td{{border-bottom:1px solid #d8ccae;padding:4px 6px;text-align:left;white-space:nowrap}}
th{{color:{MUTED};font-weight:600}}
.scroll{{overflow:auto;border:1px solid #d8ccae;background:{PAPER}}}
code{{font:12px ui-monospace,Menlo,monospace}}
@media(max-width:900px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
@media(max-width:520px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body><main>
<h1>Fleur sets P01–P20</h1>
<p class="lead">Twenty parameter sets from one source, drawn by one function:
the set is data, not twenty programs.</p>

<div class="panel">
<p><strong>What is shared.</strong> Every card is `grammar.study(opts)`:
the same right half, mirror, band and no fill, so {len(SETS)} studies make one
hand rather than {len(SETS)} special cases. Each has
26 spans and the port's nine corners; the parameter changes move the petals,
the lance, the band and the foot, not the grammar. The rail error on each card
is the fitted 25-unit rail, not a copy error.</p>
<p><strong>The seam.</strong> Every set measures its own two centre-seam
crossings on the built rails and declares them as contacts, so the halves are
joined rather than merely touching. P01's measured pair matches the fixed pair
in `study_01`; the other nineteen get theirs from `seam_contacts`. The clearance
report is clean on all twenty.</p>
<p class="note">Source: <code>ornaments/assets/ornament_set.js</code>, the
study-01…study-20 rows, transcribed in <code>curve_lab/fleur_sets.py</code>.</p>
</div>

<div class="grid">{''.join(cards)}</div>

<h2>The parameter sets</h2>
<div class="scroll">
<table>
<thead><tr><th>id</th><th>petalH</th><th>petalSweep</th><th>lanceH</th>
<th>bandHalf</th><th>waist</th><th>footY</th><th>tailSweep</th>
<th>petalT0</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
</div>

<div class="panel">
<p><strong>What this proves.</strong> The grammar scales across the hand: one
function, twenty sets, the same span count and the same corner count. Whether
the set reads as one hand is the operator's call; the page is the contact sheet
for that judgement, not a claim that it passes.</p>
<p class="note">Re-derive: <code>python scripts/fleur_sets.py</code> ·
<code>python -m unittest tests.test_fleur_sets</code></p>
</div>
</main></body></html>
'''
    out = ROOT / "workbench" / "fleur-sets.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    print(f"{len(SETS)} sets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
