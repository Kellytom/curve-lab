"""Render the scale-1 asymmetric G2 pair as an actual Piece/Trace.

    .venv/bin/python scripts/integer_g2_piece.py

This uses cubic spans directly through `Trace(spans=...)`, not a fitted
clothoid bridge. The clearance check is the real `piece_clearance()` rule.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import pyth_g2  # noqa: E402
from curve_lab.clearance import piece_clearance  # noqa: E402
from curve_lab.contact import Contact  # noqa: E402
from curve_lab.piece import Piece, Trace, render_piece  # noqa: E402


def main():
    pair = pyth_g2.asymmetric_pair()

    def span(points):
        return {"p0": points[0], "c1": points[1],
                "c2": points[2], "p3": points[3]}

    piece = Piece(
        name="integer G2 pair",
        traces=[
            Trace("A", spans=[span(pair["a_points"])]),
            Trace("B", spans=[span(pair["b_points"])]),
        ],
        contacts=[Contact((50, 0), radius=2.0, a="ink/A", b="ink/B")],
    )
    piece.stroke = 0.4
    marks = []
    a, b = pair["a_points"], pair["b_points"]
    labels = (
        ("A0 (0,0)", a[0], 2.0, -1.2),
        ("A1 (7,−24)", a[1], 2.0, -1.2),
        ("A2 (46,3)", a[2], -10.0, 1.2),
        ("G2 join (50,0)", a[3], -12.0, 2.2),
        ("B1 (54,−3)", b[1], 2.0, -1.5),
        ("B2 (39,−48)", b[2], -12.0, -1.2),
        ("B3 (64,−48)", b[3], -12.0, 2.0),
    )
    for text, point, dx, dy in labels:
        marks.append({"kind": "text", "x": point[0], "y": point[1],
                      "dx": dx, "dy": dy, "text": text, "size": 1.15,
                      "front": True, "fill": "#2e2413"})
        marks.append({"kind": "circle", "x": point[0], "y": point[1],
                      "r": 0.45, "fill": "#2e2413", "front": True})
    drawing, info = render_piece(piece, margin=8.0, annotations=marks)
    result = piece_clearance(
        piece, clearance=5.0, tol=0.02, roles=("spine",))
    rows = [
        ("piece", piece.name),
        ("traces", len(piece.traces)),
        ("fit_ok", info["fit_ok"]),
        ("clearance ok", result["ok"]),
        ("violations", len(result["violations"])),
        ("warnings", len(result["warnings"])),
        ("allowed crossings", sum(1 for c in result["crossings"]
                                  if c.get("allowed"))),
        ("min distance", result["min"]["distance"] if result["min"] else "n/a"),
    ]
    table = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows)
    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Integer G2 piece</title>
<style>
:root{{--paper:#fbf7ec;--ink:#2e2413;--muted:#7b6c4e;--rule:#d8ccae;--gold:#c9a441}}
*{{box-sizing:border-box}}
body{{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}}
main{{max-width:1280px;margin:0 auto;padding:34px 22px 70px}}
.eyebrow{{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
h1{{font-size:32px;line-height:1.1;margin:0 0 7px}}
h2{{font-size:21px;margin:0 0 9px}}
.lede{{max-width:900px;color:var(--muted);margin:0 0 20px}}
.panel{{background:var(--paper);border:1px solid var(--rule);padding:17px 19px;margin:0 0 18px}}
.figure{{margin:0;background:var(--paper);border:1px solid var(--rule);padding:10px}}
.figure h3{{font:600 14px/1.3 Georgia,serif;margin:0 0 8px}}
.figure svg{{display:block;width:100%;height:auto}}
table{{border-collapse:collapse;width:100%;font:11px/1.5 ui-monospace,Menlo,monospace;margin:10px 0}}
th,td{{border:1px solid var(--rule);padding:5px 7px;text-align:left}}
th{{width:34%;color:var(--muted);font-weight:400}}
code{{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}}
.small{{font:12px/1.55 ui-monospace,Menlo,monospace;color:var(--muted)}}
</style>
</head>
<body>
<main>
<p class="eyebrow">curve-lab · Piece / Trace integration</p>
<h1>Integer G2 pair as a piece</h1>
<p class="lede">The scale-1 asymmetric pair now travels through the actual <code>Piece</code>/<code>Trace</code> path. The traces carry cubic spans directly; no clothoid fit is pretending to be the exact curve.</p>
<section class="panel">
  <h2>Fig. G4 · the piece</h2>
  <div class="figure"><h3>Fig. G4 · integer G2 piece · scale 1</h3>{drawing}</div>
  <p class="small">A ends at the declared join; B starts there. The join is a contact in the piece model, so the clearance rule allows it and still measures every other approach.</p>
</section>
<section class="panel">
  <h2>Piece report</h2>
  <table>{table}</table>
  <p class="small">Cubic spans are exact; the SVG and clearance path are the same ones used by the rest of the workbench. This is a hairline trace, not a ribbon.</p>
</section>
</main>
</body>
</html>
'''
    out = ROOT / "workbench" / "integer-g2-piece.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    print(f"  fit_ok={info['fit_ok']} clearance_ok={result['ok']} "
          f"violations={len(result['violations'])} crossings={len(result['crossings'])}")


if __name__ == "__main__":
    main()
