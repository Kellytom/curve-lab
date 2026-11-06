"""The promotion gate, steps 2 and 3: one spine on the sheet, one declared join.

    .venv/bin/python scripts/spine_sheet.py
    open workbench/spine-sheet.html

A curl from the spine layer, a branch forked off one of its exact nodes, and a
contact declared at that node. The piece is drawn on the 200 x 250 mm sheet
through the normal writer (which flips y once, at the SVG boundary), and the
same built groups are measured by `piece_clearance()`.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import engine, spine  # noqa: E402
from curve_lab.clearance import piece_clearance  # noqa: E402
from curve_lab.contact import Contact  # noqa: E402
from curve_lab.piece import Piece, render_piece  # noqa: E402

TRUNK_WIDTH = 3.0
BRANCH_WIDTH = 1.5
PAGE = (200.0, 250.0)


def build():
    package = spine.load()
    trunk = package.design.curl(peak=200, chord=6)
    node = len(trunk.nodes) - 1          # the free end: a branch has room here
    anchor, branch = package.design.fork(
        trunk, node, steps=9, length=1.5, quarter=1)
    point = (float(anchor[0][0]), float(anchor[0][1]))
    piece = Piece(
        name="spine sheet",
        stroke=0.5,
        contacts=[Contact(point, 3.0, "ink/trunk", "ink/branch")],
        traces=[
            spine.trace_from_chain(trunk, "trunk", width=TRUNK_WIDTH),
            spine.trace_from_chain(branch, "branch", width=BRANCH_WIDTH),
        ],
    )
    return trunk, branch, piece, point, node


def anchor_error(chain, name):
    """Worst distance between a fitted segment join and its span anchor."""
    design = spine.design_from_chain(chain, name=name)
    spans = spine.chain_spans(chain)
    placed = engine.build(design)
    s, worst = 0.0, 0.0
    for index, segment in enumerate(design.segments):
        x, y = placed.point(s)
        worst = max(worst, math.dist((x, y), spans[index]["p0"]))
        s += segment.length
    return worst, len(design.segments)


def main() -> int:
    trunk, branch, piece, point, node = build()
    svg, info = render_piece(piece, frame=PAGE, margin=12, grid=True, marks=True)
    report = piece_clearance(piece)
    trunk_error, trunk_segments = anchor_error(trunk, "trunk")
    branch_error, branch_segments = anchor_error(branch, "branch")

    if not report["ok"]:
        raise SystemExit(f"the declared contact did not pass: {report['violations']}")

    facts = [
        ("chain", "curl, power 1"),
        ("chord budget", "6 deg"),
        ("chords", str(len(trunk.turns))),
        ("peak heading", f"{trunk.peak_degrees:.2f} deg"),
        ("anchors", str(len(trunk.nodes))),
        ("spans", str(len(spine.chain_spans(trunk)))),
        ("fitted segments", str(trunk_segments)),
        ("worst anchor error", f"{trunk_error:.2e} units"),
    ]
    branch_facts = [
        ("branch node", str(node)),
        ("branch spans", str(len(spine.chain_spans(branch)))),
        ("fitted segments", str(branch_segments)),
        ("worst anchor error", f"{branch_error:.2e} units"),
        ("declared contact", f"({point[0]:.3f}, {point[1]:.3f}), r 3 mm"),
    ]
    clearance_facts = [
        ("minimum edge gap", f"{report['min']['distance']:.3f} mm"),
        ("between", f"{report['min']['a']} and {report['min']['b']}"),
        ("violations", str(len(report["violations"]))),
        ("warnings", str(len(report["warnings"]))),
        ("crossings", str(len(report["crossings"]))),
        ("merged by contact", str(len(report["merged"]))),
    ]

    def rows(items):
        return "\n".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in items)

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Spine on the sheet — promotion gate 2 and 3</title>
<style>
  :root {{ color-scheme: light; --paper:#f6f1e4; --card:#fffdf7; --ink:#2e2413;
    --muted:#7b6c4e; --gold:#8c6a21; --line:#d8ccae;
    --mono: ui-monospace,"SF Mono",Menlo,Consolas,monospace;
    --serif:"EB Garamond",Georgia,"Palatino Linotype",Palatino,serif; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; color:var(--ink); font:16px/1.55 var(--serif);
    background: radial-gradient(900px 440px at 12% -8%, #fcf9ef 0, transparent 60%), var(--paper); }}
  main {{ max-width: 900px; margin: 0 auto; padding: 34px 22px 70px; }}
  h1 {{ font-size: 28px; margin: 0 0 4px; }}
  .lead {{ color: var(--gold); margin: 0 0 18px; }}
  h2 {{ font: 600 11px/1.2 var(--mono); letter-spacing: .12em; text-transform: uppercase;
    color: var(--muted); margin: 26px 0 8px; }}
  .panel {{ background: var(--card); border: 1px solid var(--line); border-radius: 6px; padding: 14px; }}
  .art svg {{ display: block; width: 100%; height: auto; background: #fff; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
  table {{ border-collapse: collapse; width: 100%; font: 12px/1.5 var(--mono); }}
  th, td {{ border-bottom: 1px solid var(--line); padding: 6px 4px; text-align: left; }}
  th {{ color: var(--muted); font-weight: 500; width: 52%; }}
  code {{ font: 12px/1 var(--mono); background: #fbf8ee; border: 1px solid var(--line);
    border-radius: 3px; padding: 2px 4px; }}
  .back {{ font: 12px var(--mono); margin-bottom: 16px; }}
  a {{ color: var(--gold); }}
  @media (max-width: 620px) {{ .grid {{ grid-template-columns: 1fr; }} main {{ padding: 22px 14px 60px; }} }}
</style>
</head>
<body>
<main>
  <p class="back"><a href="workbench.html">← workbench</a> · <a href="ornament-board.html">the ornament board</a></p>
  <h1>Spine on the sheet</h1>
  <p class="lead">Promotion gate 2: a chain on 200 × 250 mm, +y up. Gate 3: a declared join passes the clearance check.</p>

  <h2>The drawing</h2>
  <div class="panel art">
    {svg}
  </div>

  <div class="grid" style="margin-top:12px">
    <div class="panel"><table>{rows(facts)}</table></div>
    <div class="panel"><table>{rows(branch_facts)}</table></div>
  </div>

  <h2>Clearance through the same build</h2>
  <div class="panel">
    <table>{rows(clearance_facts)}</table>
    <p style="margin-top:10px">The branch leaves the last node at an exact right angle and
    crosses the trunk there. That is allowed only because the drawing declares the contact
    at the shared node; remove the <code>Contact</code> and the crossing is disallowed and
    the gap is a violation.</p>
  </div>

  <h2>What is proved</h2>
  <div class="panel">
    <p>The chain arrives as ordinary clothoid segments, one per span, so the rails,
    the SVG writer and the clearance check need no second geometry kind. Every
    segment join lands on a chain anchor to machine precision, and the tangent jump
    the spine layer keeps at a curvature reversal travels as a segment corner.
    The writer flips y once at the SVG boundary: the design stays +y up, and the
    start at y = 0 sits at the bottom of the page.</p>
  </div>
</main>
</body>
</html>
"""
    path = ROOT / "workbench" / "spine-sheet.html"
    path.write_text(page, encoding="utf-8")
    print(path)
    print(f"sheet {PAGE[0]:g}x{PAGE[1]:g} mm, fit_ok={info['fit_ok']}")
    print(f"anchors: trunk {trunk_error:.2e}, branch {branch_error:.2e}")
    print(f"clearance ok={report['ok']} min={report['min']['distance']:.3f} "
          f"violations={len(report['violations'])} merged={len(report['merged'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
