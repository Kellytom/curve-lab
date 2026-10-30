"""Gate 4: study 01 drawn from Pythagorean chains.

    .venv/bin/python scripts/spine_study_01.py
    open docs/spine-study-01.html

Draws the right half and the band as composite chains at the default turn step
on the 200 x 250 mm sheet, and prints the drift of every span end from P01's
node. The study passes the operator's fidelity rule — worst span-end drift at
most 1.6% of study height — and is still not P01 parity. See
`docs/FIDELITY.md`.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clothoid_lab import spine_study  # noqa: E402
from clothoid_lab.piece import render_piece  # noqa: E402

PAGE = (200.0, 250.0)


def main() -> int:
    result = spine_study.report(spine_study.ALPHA_DEG)
    piece = spine_study.study_01_from_chains(spine_study.ALPHA_DEG)
    svg, info = render_piece(piece, frame=PAGE, margin=12)
    if not info["fit_ok"]:
        raise SystemExit("a chain trace did not fit")

    rows = "\n".join(
        f"<tr><td>{index + 1:02d}</td><td>{drift:.2f}</td>"
        f"<td>{100 * drift / result['height']:.2f}%</td></tr>"
        for index, drift in enumerate(result["drifts"]))

    facts = [
        ("turn step", f"{result['alpha_deg']:g} deg"),
        ("chords, right half", str(result["chords"])),
        ("spans, right half", str(result["spans"])),
        ("study height", f"{result['height']:.0f} units"),
        ("worst drift", f"{result['worst']:.2f} units "
                        f"({100 * result['worst_fraction']:.2f}%)"),
        ("end heading", f"{result['end_heading_deg']:.2f} deg"),
        ("sheet", "200 x 250 mm, +y up"),
    ]
    fact_rows = "\n".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in facts)

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Study 01 from chains — gate 4</title>
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
  .note {{ border-left: 3px solid var(--gold); padding: 10px 14px; background: #fbf6e6;
    border-radius: 0 6px 6px 0; margin: 14px 0; }}
  table {{ border-collapse: collapse; width: 100%; font: 12px/1.5 var(--mono); }}
  th, td {{ border-bottom: 1px solid var(--line); padding: 6px 4px; text-align: left; }}
  th {{ color: var(--muted); font-weight: 500; }}
  .scroll {{ max-height: 300px; overflow: auto; }}
  code {{ font: 12px/1 var(--mono); background: #fbf8ee; border: 1px solid var(--line);
    border-radius: 3px; padding: 2px 4px; }}
  .back {{ font: 12px var(--mono); margin-bottom: 16px; }}
  a {{ color: var(--gold); }}
  @media (max-width: 620px) {{ .grid {{ grid-template-columns: 1fr; }} main {{ padding: 22px 14px 60px; }} }}
</style>
</head>
<body>
<main>
  <p class="back"><a href="ornament-board.html">← back to the ornament board</a></p>
  <h1>Study 01 from chains</h1>
  <p class="lead">Gate 4: every stroke a Pythagorean chain, measured against P01.</p>

  <div class="note">
    <strong>Meets the 1.6% fidelity rule; not P01 parity.</strong> The operator
    accepted a worst span-end drift of at most 1.6% of the study height
    (2026-10-30); this drawing measures 1.29% at a 0.5° turn step. P01's start
    heading (77.97°) and corners are not in the chain's rotation group, so this
    is a chain <em>plan</em> with a measured resemblance, not P01's node table.
    The rule, its precedent and its caveats are in <code>docs/FIDELITY.md</code>.
  </div>

  <h2>The drawing</h2>
  <div class="panel art">
    {svg}
  </div>

  <div class="grid" style="margin-top:12px">
    <div class="panel"><table>{fact_rows}</table></div>
    <div class="panel">
      <table>
        <tr><th>span end</th><th>drift (units)</th><th>of height</th></tr>
        {rows}
      </table>
    </div>
  </div>

  <h2>What the chains say</h2>
  <div class="panel">
    <p>Each span keeps its own law: a line is zero turns, an arc is a constant
    turn, the Euler span opens 0, 1, 2, … turns. The chords are exact rational
    lengths on exact rational headings, so every node is rational before the
    sheet places it. The engine receives the chain as straight segments with the
    chain's own corner at each node — one geometry kind, no second kernel.</p>
    <p>The strokes are drawn as centre lines on purpose. A ribbon width would
    ask the engine's rail builder to offset a chain that turns a degree at every
    node; those rails cross at the corners, because they are built for smooth
    clothoids. The filled ribbon is the spine layer's miter job
    (<code>ribbon.outline</code>), and that is the next connection to make.</p>
    <p>The drift is the price of the group: the start heading is snapped to the
    nearest whole turn and every corner with it, so each quantised corner swings
    the rest of the stroke on a long lever. The table is the honest measurement,
    not an error to be hidden. Finer turns do converge: 0.125° reaches 0.11%,
    while 0.0625° did not finish in a minute in whole-number arithmetic. The
    limit is cost, not principle.</p>
  </div>
</main>
</body>
</html>
"""
    path = ROOT / "docs" / "spine-study-01.html"
    path.write_text(page, encoding="utf-8")
    print(path)
    print(f"alpha {result['alpha_deg']:g} deg: {result['chords']} chords, "
          f"worst drift {result['worst']:.2f} units "
          f"({100 * result['worst_fraction']:.2f}% of height)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
