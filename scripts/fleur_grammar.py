"""Fleur grammar 01: the W03 report on the ported study.

    .venv/bin/python scripts/fleur_grammar.py
    open workbench/fleur-grammar.html

The page draws `curve_lab.grammar.study_01` and reports what the grammar
actually produces: 26 spans, nine declared corners (the port keeps its source's
G0 breaks), two declared seam contacts between the mirrored halves, no rail
folds, and a clearance report with no disallowed crossing. Copy error against
the ornaments source is not measured here: that source is not in this repo.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab.grammar import study_01, study_01_report  # noqa: E402
from curve_lab.piece import render_piece  # noqa: E402

INK, MUTED, PAPER = "#2e2413", "#7b6c4e", "#fffdf7"


def main() -> int:
    report = study_01_report()
    piece = study_01()
    figure, info = render_piece(piece, frame=(640, 820), margin=20, grid=True, marks=True)

    corner_rows = "".join(
        f"<tr><td>{c['trace']}</td><td>{c['index']}</td>"
        f"<td>{c['degrees']:.2f}</td></tr>"
        for c in study_01_report_corners()
    )

    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fleur grammar 01 — the W03 report</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1000px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 18px}}
h2{{font:600 12px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.10em;text-transform:uppercase;color:{MUTED};margin:30px 0 8px}}
.panel{{background:{PAPER};border:1px solid #d8ccae;padding:16px 18px;margin:0 0 18px}}
.art{{background:{PAPER};border:1px solid #d8ccae;padding:8px;margin:0 0 8px}}
.art svg{{display:block;width:100%;height:auto}}
table{{border-collapse:collapse;width:100%;font:12px/1.5 ui-monospace,Menlo,monospace}}
td,th{{border-bottom:1px solid #d8ccae;padding:5px 8px;text-align:left}}
th{{color:{MUTED};font-weight:600}}
code{{font:12px ui-monospace,Menlo,monospace}}
.note{{font:11px/1.6 ui-monospace,Menlo,monospace;color:{MUTED}}}
</style></head><body><main>
<h1>Fleur grammar 01</h1>
<p class="lead">The ported study, with the report the grammar owes: spans,
joins, folds and the declared seam.</p>

<div class="panel">
<p><strong>The object.</strong> The right half (11 spans) is mirrored
({report['spans_half']} more) and closed with the band
({report['spans_band']} spans): <strong>{report['spans']} spans</strong> in all.
No fill. The band is a hairline; the half is a 25-unit ribbon.</p>
<p><strong>The joins.</strong> The port keeps the old grammar's corners rather
than smoothing them away: <strong>{report['corners']}</strong> declared breaks,
the largest <strong>{report['max_corner']:.2f}°</strong> at the foot-to-tail
turn. They are G0 by construction, and the report says so instead of calling
the piece G1.</p>
<p><strong>The seam.</strong> The two halves meet at two places on the centre
line, the foot crossover and the inner-bow crossover. Both are
<strong>declared contacts</strong> ({report['contacts']} in the piece), not
inferred from proximity. With them, the clearance report has
{report['crossings']} crossing, {report['disallowed']} disallowed, and
{report['folds']} rail folds.</p>
<p class="note">Copy error against the ornaments source is not measured: that
source is not in this repository. The report is about the port's own geometry.</p>
</div>

<div class="art">{figure}</div>

<h2>The numbers</h2>
<div class="panel">
<table>
<tr><th>spans</th><td>{report['spans_half']} half + {report['spans_half']} mirrored + {report['spans_band']} band = {report['spans']}</td></tr>
<tr><th>corners</th><td>{report['corners']} · max {report['max_corner']:.2f}°</td></tr>
<tr><th>seam contacts</th><td>{report['contacts']} declared</td></tr>
<tr><th>crossings</th><td>{report['crossings']} total · {report['disallowed']} disallowed</td></tr>
<tr><th>rail folds</th><td>{report['folds']}</td></tr>
<tr><th>clearance</th><td>{'ok' if report['clearance_ok'] else 'not ok'}</td></tr>
<tr><th>copy error</th><td>not measured (source absent)</td></tr>
</table>
</div>

<h2>The corners</h2>
<div class="panel">
<table>
<thead><tr><th>trace</th><th>segment</th><th>turn (°)</th></tr></thead>
<tbody>{corner_rows}</tbody>
</table>
</div>

<div class="panel">
<p><strong>What W03 still owes.</strong> A clothoid or fillet at the largest
corner, and a copy-error measurement once the ornaments source is available.
The port itself is complete: every span lands on its node, the mirror seam is
declared, and the report is reproducible from the module.</p>
<p class="note">Re-derive: <code>python scripts/fleur_grammar.py</code> ·
<code>python -m unittest tests.test_fleur_grammar</code></p>
</div>
</main></body></html>
'''
    out = ROOT / "workbench" / "fleur-grammar.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    print(report)
    return 0


def study_01_report_corners():
    from curve_lab.grammar import STUDY_01, fleur_right
    import math

    right = fleur_right(STUDY_01)
    out = []
    for index, segment in enumerate(right["spans"]):
        corner = math.degrees(getattr(segment, "corner", 0.0))
        if abs(corner) > 1e-9:
            out.append({"trace": "half", "index": index,
                        "degrees": corner})
    return out


if __name__ == "__main__":
    raise SystemExit(main())
