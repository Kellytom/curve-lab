"""The spiral families that make a dress curve: log, hyperbolic, clothoid.

    .venv/bin/python scripts/curve_families.py
    open docs/curve-families.html

Each panel is a quarter-turn or so of the family, scaled to the same 100-point
cell so the *bend* is comparable. A hip curve is a gentle single arc; a vary
form is a compound. This page is for the eye; the fit is what settles it.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CELL = 100.0
MARGIN = 8.0


def log_spiral(b: float, start: float = 0.0, end: float = math.pi / 2,
               a: float = 1.0):
    n = 240
    return [(a * math.exp(b * (start + (end - start) * i / n))
             * math.cos(start + (end - start) * i / n),
             a * math.exp(b * (start + (end - start) * i / n))
             * math.sin(start + (end - start) * i / n)) for i in range(n + 1)]


def hyperbolic(start: float = 0.5, end: float = 2.5, a: float = 1.0):
    n = 240
    pts = []
    for i in range(n + 1):
        t = start + (end - start) * i / n
        pts.append((a / t * math.cos(t), a / t * math.sin(t)))
    return pts


def clothoid(turn: float = math.pi / 2, ds: float = 0.005):
    """kappa = s/A^2, with A chosen so the arc turns `turn` over length 1."""
    length = 1.0
    area = math.sqrt(length * length / (2 * turn))
    x = y = s = 0.0
    pts = []
    while s <= length:
        theta = s * s / (2 * area * area)
        pts.append((x, y))
        x += ds * math.cos(theta)
        y += ds * math.sin(theta)
        s += ds
    return pts


def placed(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    scale = (CELL - 2 * MARGIN) / max(x1 - x0, y1 - y0, 1e-9)
    return [(MARGIN + (x - x0) * scale, CELL - (MARGIN + (y - y0) * scale))
            for x, y in points]


def panel(label: str, formula: str, points, note: str) -> str:
    d = " ".join(f"{'M' if i == 0 else 'L'} {x:.2f} {y:.2f}"
                 for i, (x, y) in enumerate(placed(points)))
    return f"""<div class="cell">
  <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <g stroke="#e8dfc8" stroke-width="0.25">
      {''.join(f'<line x1="{g}" y1="0" x2="{g}" y2="100"/>' for g in range(10, 100, 10))}
      {''.join(f'<line x1="0" y1="{g}" x2="100" y2="{g}"/>' for g in range(10, 100, 10))}
    </g>
    <rect x="0" y="0" width="100" height="100" fill="none" stroke="#d8ccae" stroke-width="0.4"/>
    <path d="{d}" fill="none" stroke="#2e2413" stroke-width="1.1"/>
  </svg>
  <p><strong>{label}</strong><br><code>{formula}</code><br>{note}</p>
</div>"""


def main() -> int:
    log_panels = [
        (b, panel(f"log spiral · b = {b:g}", "r = a e^(bθ)",
                  log_spiral(b),
                  f"radius grows {math.exp(b * math.pi / 2):.2f}× over 90°"))
        for b in (0.10, 0.18, 0.25, 0.35, 0.50)
    ]
    hyper_panels = [
        (start, end, panel(f"hyperbolic · θ {start:g}–{end:g}", "r = a / θ",
                           hyperbolic(start, end),
                           "asymptote at y = a; rθ is constant"))
        for start, end in ((0.5, 2.5), (0.3, 1.8), (0.8, 3.2))
    ]
    cloth_panel = panel("clothoid · 90°", "κ = s / A²", clothoid(),
                        "curvature linear in arc length")

    log_html = "".join(p for _, p in log_panels)
    hyper_html = "".join(p for _, _, p in hyper_panels)

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Spirals that make a dress curve</title>
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
  h2 {{ font: 600 11px/1.2 var(--mono); letter-spacing:.12em; text-transform:uppercase;
    color:var(--muted); margin:26px 0 8px; }}
  .panel {{ background:var(--card); border:1px solid var(--line); border-radius:6px; padding:14px; }}
  .cells {{ display:grid; grid-template-columns:repeat(3,1fr); gap:10px; }}
  .cell {{ border:1px solid var(--line); border-radius:4px; padding:8px; background:#fff; }}
  .cell svg {{ display:block; width:100%; height:auto; }}
  .cell p {{ margin:6px 0 0; font:10px/1.45 var(--mono); color:var(--muted); }}
  .cell strong {{ color:var(--ink); }}
  code {{ font:11px/1 var(--mono); background:#fbf8ee; border:1px solid var(--line);
    border-radius:3px; padding:2px 4px; }}
  table {{ border-collapse:collapse; width:100%; font:12px/1.5 var(--mono); }}
  th, td {{ border-bottom:1px solid var(--line); padding:6px 4px; text-align:left; }}
  th {{ color:var(--muted); font-weight:500; }}
  .scroll {{ overflow-x:auto; }}
  .back {{ font:12px var(--mono); margin-bottom:16px; }}
  a {{ color:var(--gold); }}
  @media (max-width:620px) {{
    main {{ padding:22px 14px 60px; }}
    .cells {{ grid-template-columns:1fr; }}
    table {{ font-size:10px; }} th,td {{ padding:4px 2px; }}
  }}
</style>
</head>
<body>
<main>
  <p class="back"><a href="sandbox.html">← sandbox</a></p>
  <h1>Spirals that make a dress curve</h1>
  <p class="lead">Log spirals, hyperbolic spirals and a clothoid, all at the same scale.
  Which bend does the hip curve have?</p>

  <h2>Logarithmic spirals: r = a e^(bθ)</h2>
  <div class="panel">
    <p>The tangent makes a constant angle with the radius. Small b is almost a
    circle; large b opens fast. A hip curve is a gentle arc, so it would sit at
    the small end.</p>
    <div class="cells">{log_html}</div>
  </div>

  <h2>Hyperbolic spirals: r = a / θ</h2>
  <div class="panel">
    <p>The radius falls as 1/θ. It has a horizontal asymptote at y = a and winds
    into the pole; the curves below are different windows on the same spiral.</p>
    <div class="cells">{hyper_html}</div>
  </div>

  <h2>Clothoid, for comparison</h2>
  <div class="panel">
    <div class="cells">{cloth_panel}</div>
    <p style="margin-top:10px">The clothoid's curvature is linear in arc length;
    the log spiral's radius of curvature is proportional to the radius; the
    hyperbolic has rθ constant. Those are three different signatures.</p>
  </div>

  <h2>How to tell which one you have</h2>
  <div class="panel">
    <div class="scroll"><table>
      <tr><th>family</th><th>equation</th><th>signature</th><th>fit</th></tr>
      <tr><td>log spiral</td><td>r = a e^(bθ)</td>
          <td>tangent–radius angle constant; ρ ∝ s</td>
          <td>log ρ vs log s has slope +1; b = tan(angle)</td></tr>
      <tr><td>clothoid</td><td>κ = s / A²</td>
          <td>curvature linear in arc length; ρ ∝ 1/s</td>
          <td>log ρ vs log s has slope −1</td></tr>
      <tr><td>hyperbolic</td><td>r = a / θ</td>
          <td>rθ constant; asymptote at y = a</td>
          <td>fit rθ; the asymptote gives a</td></tr>
      <tr><td>log-aesthetic</td><td>ρ^α = c₀s + c₁</td>
          <td>α = 1 is log, α = −1 is clothoid</td>
          <td>fit α; the slope of log ρ vs log s is 1/α</td></tr>
    </table></div>
    <p style="margin-top:10px">If the hip curve is one of these, the fitted
    numbers will say which; if it is a compound (as the vary form often is),
    it will fit two segments with different α or b.</p>
  </div>
</main>
</body>
</html>
"""
    path = ROOT / "docs" / "curve-families.html"
    path.write_text(page, encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
