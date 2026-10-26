"""Build the W01 sandbox: one piece, several traces, a mirror.

Run from the repo root:

    .venv/bin/python scripts/piece_sandbox.py
    open docs/piece-model.html
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clothoid_lab.model import Design, Segment
from clothoid_lab.piece import Piece, Trace, render_piece
from clothoid_lab.presets import s_curve


def band() -> Design:
    return Design(
        name="band",
        segments=[Segment(kd=0.0, length=90.0, kappa0=0.0)],
        anchor={"x": -45.0, "y": 58.0, "angle": 0.0},
    )


def main() -> int:
    piece = Piece(
        name="W01 sandbox",
        mirror=True,
        stroke=0.6,
        traces=[
            Trace("half", s_curve(), width=6.0, layer="ink"),
            Trace("band", band(), mirror=False, layer="guide"),
        ],
    )
    svg, info = render_piece(piece, tol=0.05, margin=8)

    rows = "\n".join(
        f"<tr><td><code>{trace['layer']}/{trace['name']}</code></td>"
        f"<td>{trace['fit_error']:.4f} mm</td>"
        f"<td>{trace['rails']}</td>"
        f"<td>{'yes' if trace['mirrored'] else 'no'}</td></tr>"
        for trace in info["traces"]
    )

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>W01 — the piece model</title>
<style>
  :root {{
    color-scheme: light;
    --paper: #f6f1e4; --card: #fffdf7; --ink: #2e2413;
    --muted: #7b6c4e; --gold: #8c6a21; --line: #d8ccae;
    --mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
    --serif: "EB Garamond", Georgia, "Palatino Linotype", Palatino, serif;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; color: var(--ink);
    background: radial-gradient(900px 440px at 12% -8%, #fcf9ef 0, transparent 60%), var(--paper);
    font: 16px/1.55 var(--serif);
  }}
  main {{ max-width: 900px; margin: 0 auto; padding: 34px 22px 70px; }}
  h1 {{ font-size: 28px; margin: 0 0 4px; }}
  .lead {{ color: var(--gold); margin: 0 0 18px; }}
  h2 {{ font: 600 11px/1.2 var(--mono); letter-spacing: .12em;
        text-transform: uppercase; color: var(--muted); margin: 26px 0 8px; }}
  .panel {{ background: var(--card); border: 1px solid var(--line);
            border-radius: 6px; padding: 14px; }}
  .art svg {{ display: block; width: 100%; height: auto; background: #fff; }}
  p {{ margin: 0 0 10px; }}
  ul {{ margin: 0 0 10px 20px; padding: 0; }}
  li {{ margin: 4px 0; }}
  code {{ font: 12px/1 var(--mono); background: #fbf8ee;
          border: 1px solid var(--line); border-radius: 3px; padding: 2px 4px; }}
  table {{ border-collapse: collapse; width: 100%; font: 12px/1.5 var(--mono); }}
  th, td {{ border-bottom: 1px solid var(--line); padding: 6px 4px; text-align: left; }}
  th {{ color: var(--muted); font-weight: 500; }}
  a {{ color: var(--gold); }}
  .back {{ font: 12px var(--mono); margin-bottom: 16px; }}
  @media (max-width: 560px) {{ main {{ padding: 22px 14px 60px; }} h1 {{ font-size: 23px; }} }}
</style>
</head>
<body>
<main>
  <p class="back"><a href="ornament-board.html">← back to the ornament board</a></p>
  <h1>W01 — the piece model</h1>
  <p class="lead">One drawing, several traces, one mirror. This is the structure the ornaments need before the fleur grammar can be ported.</p>

  <h2>What you are looking at</h2>
  <div class="panel">
    <ul>
      <li><code>ink/half</code> — one clothoid chain, drawn as the centre line of a ribbon.</li>
      <li><code>ink/half rail ±3</code> — the two edges, each offset 3 mm from the centre line; together they make a 6 mm ribbon.</li>
      <li><code>ink/half mirrored</code> — the same three paths reflected across x = 0. The mirror is one setting on the piece, not a second drawing.</li>
      <li><code>guide/band</code> — a straight guide, explicitly <em>not</em> mirrored, so it does not draw twice.</li>
    </ul>
  </div>

  <h2>The piece</h2>
  <div class="panel art">
    {svg}
  </div>

  <h2>The report</h2>
  <div class="panel">
    <table>
      <tr><th>trace</th><th>fit</th><th>rails</th><th>mirrored</th></tr>
      {rows}
    </table>
  </div>

  <h2>What this proves</h2>
  <div class="panel">
    <p>The engine still draws one chain at a time. A <code>Piece</code> holds named traces, each with its own <code>Design</code>, optional ribbon width and mirror rule. <code>render_piece()</code> builds every trace, mirrors the groups that ask for it, and writes one SVG with one page, one frame and one y-flip. The path ids are the trace names, so a later grammar can address a band or a petal directly.</p>
    <p>The next steps are W02 (point, arc, round and taper terminals) and W03 (the fleur grammar on top of this structure).</p>
  </div>
</main>
</body>
</html>
"""
    path = Path(__file__).resolve().parents[1] / "docs" / "piece-model.html"
    path.write_text(html, encoding="utf-8")
    print(path)
    print(f"traces={len(info['traces'])} fit_ok={info['fit_ok']}")
    for trace in info["traces"]:
        print(f"  {trace['layer']}/{trace['name']}: fit {trace['fit_error']:.4f} mm, "
              f"rails {trace['rails']}, mirrored {trace['mirrored']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
