"""Render the scale-1 asymmetric G2 pair and the three-piece chain as Pieces.

    .venv/bin/python scripts/integer_g2_piece.py

This uses cubic spans directly through `Trace(spans=...)`, not a fitted
clothoid bridge. The clearance checks are the real `piece_clearance()` rule.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import pyth_cubic, pyth_g2  # noqa: E402
from curve_lab.clearance import piece_clearance  # noqa: E402
from curve_lab.contact import Contact  # noqa: E402
from curve_lab.piece import Piece, Trace, render_piece  # noqa: E402


def span(points):
    return {"p0": points[0], "c1": points[1],
            "c2": points[2], "p3": points[3]}


def marks_for(named_pieces):
    marks = []
    for name, piece in named_pieces:
        for index, point in enumerate(piece):
            label = f"{name}{index} ({point[0]}, {point[1]})"
            # Keep labels just off the point; the page text carries the full
            # coordinates if a label runs into a neighbouring curve.
            dx, dy = 1.8, -1.2
            if index in (1, 2):
                dy = 1.4
            if point[0] < 10:
                dx = 1.8
            elif point[0] > 50:
                dx = -12.0
            marks.append({"kind": "text", "x": point[0], "y": point[1],
                          "dx": dx, "dy": dy, "text": label, "size": 0.92,
                          "front": True, "fill": "#2e2413"})
            marks.append({"kind": "circle", "x": point[0], "y": point[1],
                          "r": 0.4, "fill": "#2e2413", "front": True})
    return marks


def report(piece, info, result):
    return [
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


def table(rows):
    return "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows)


def main():
    pair = pyth_g2.asymmetric_pair()
    chain_data = pyth_g2.chain(pyth_cubic.case(3, 4, 5))
    a, b = pair["a_points"], pair["b_points"]
    c, base, d = chain_data["pieces"]

    pair_piece = Piece(
        "integer G2 pair",
        [Trace("A", spans=[span(a)]), Trace("B", spans=[span(b)])],
        contacts=[Contact((50, 0), radius=2.0, a="ink/A", b="ink/B")],
    )
    pair_piece.stroke = 0.4
    chain_piece = Piece(
        "integer G2 chain",
        [Trace("C", spans=[span(c)]), Trace("A", spans=[span(base)]),
         Trace("B", spans=[span(d)])],
        contacts=[
            Contact((0, 0), radius=2.0, a="ink/C", b="ink/A"),
            Contact((50, 0), radius=2.0, a="ink/A", b="ink/B"),
        ],
    )
    chain_piece.stroke = 0.4

    # The pair keeps its explicit label placement; the chain uses the generic
    # generator above.
    pair_marks = []
    pair_labels = (
        ("A0 (0,0)", a[0], 2.0, -1.2),
        ("A1 (7,−24)", a[1], 2.0, -1.2),
        ("A2 (46,3)", a[2], -10.0, 1.2),
        ("G2 join (50,0)", a[3], -12.0, 2.2),
        ("B1 (54,−3)", b[1], 2.0, -1.5),
        ("B2 (39,−48)", b[2], -12.0, -1.2),
        ("B3 (64,−48)", b[3], -12.0, 2.0),
    )
    for text, point, dx, dy in pair_labels:
        pair_marks.append({"kind": "text", "x": point[0], "y": point[1],
                           "dx": dx, "dy": dy, "text": text, "size": 1.15,
                           "front": True, "fill": "#2e2413"})
        pair_marks.append({"kind": "circle", "x": point[0], "y": point[1],
                           "r": 0.45, "fill": "#2e2413", "front": True})

    pair_svg, pair_info = render_piece(
        pair_piece, margin=8.0, annotations=pair_marks)
    chain_svg, chain_info = render_piece(
        chain_piece, margin=8.0,
        annotations=marks_for((("C", c), ("A", base), ("B", d))))
    pair_result = piece_clearance(
        pair_piece, clearance=5.0, tol=0.02, roles=("spine",))
    chain_result = piece_clearance(
        chain_piece, clearance=5.0, tol=0.02, roles=("spine",))
    pair_rows = table(report(pair_piece, pair_info, pair_result))
    chain_rows = table(report(chain_piece, chain_info, chain_result))
    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Integer G2 pieces</title>
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
<h1>Integer G2 pieces</h1>
<p class="lede">The scale-1 pair and the three-piece C–A–B chain now travel through the actual <code>Piece</code>/<code>Trace</code> path. The traces carry cubic spans directly; no clothoid fit is pretending to be the exact curve.</p>
<section class="panel">
  <h2>Fig. G4 · the asymmetric pair</h2>
  <div class="figure"><h3>Fig. G4 · integer G2 pair · scale 1</h3>{pair_svg}</div>
  <p class="small">A ends at the declared join; B starts there. The join is a contact in the piece model, so the clearance rule allows it and still measures every other approach.</p>
</section>
<section class="panel">
  <h2>Pair report</h2>
  <table>{pair_rows}</table>
</section>
<section class="panel">
  <h2>Fig. G5 · the three-piece chain</h2>
  <div class="figure"><h3>Fig. G5 · C–A–B integer G2 chain · scale 5</h3>{chain_svg}</div>
  <p class="small">C ends at A's start; A ends at B's start. Both joins are declared contacts. The chain is carried as three direct cubic spans, not as a clothoid fit.</p>
</section>
<section class="panel">
  <h2>Chain report</h2>
  <table>{chain_rows}</table>
  <p class="small">Hairline traces only. The <code>Piece</code>/<code>Trace</code> path now supports cubic spans; ribbon width for span traces is intentionally not implemented yet.</p>
</section>
</main>
</body>
</html>
'''
    out = ROOT / "workbench" / "integer-g2-piece.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    for label, info, result in (("pair", pair_info, pair_result),
                                ("chain", chain_info, chain_result)):
        print(f"  {label}: fit_ok={info['fit_ok']} "
              f"clearance_ok={result['ok']} "
              f"violations={len(result['violations'])} "
              f"crossings={len(result['crossings'])}")


if __name__ == "__main__":
    main()
