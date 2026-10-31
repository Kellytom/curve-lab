"""Spiral families at dress-curve proportions: 8 inches wide, 1-5 high.

    .venv/bin/python scripts/curve_families.py
    open docs/curve-families.html

Each strip is 8 x n inches (n = 1..5). For each family the arc is chosen so its
bounding box has that 8:n aspect, then scaled to fill the strip. A shallow arc
is a small turn; a tall one is a large turn. That is the honest way to compare
"which curve fills an 8 by 3 inch dress curve".
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
W = 800.0
MARGIN = 14.0


def log_points(b: float, phi: float):
    n = 300
    return [(math.exp(b * phi * i / n) * math.cos(phi * i / n),
             math.exp(b * phi * i / n) * math.sin(phi * i / n))
            for i in range(n + 1)]


def hyper_points(t0: float, phi: float):
    n = 300
    pts = []
    for i in range(n + 1):
        t = t0 + phi * i / n
        pts.append((math.cos(t) / t, math.sin(t) / t))
    return pts


def clothoid_points(phi: float):
    length = 1.0
    k = 2.0 * phi / length          # turn = 0.5 * k * L
    x = y = s = 0.0
    pts = []
    ds = 0.004
    while s <= length:
        theta = s * s * k / (2 * length)
        pts.append((x, y))
        x += ds * math.cos(theta)
        y += ds * math.sin(theta)
        s += ds
    return pts


def orient(points):
    """Rotate so the chord from first to last point is horizontal."""
    a = math.atan2(points[-1][1] - points[0][1],
                   points[-1][0] - points[0][0])
    c, s = math.cos(-a), math.sin(-a)
    return [(c * x - s * y, s * x + c * y) for x, y in points]


def aspect(points) -> float:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (max(xs) - min(xs)) / max(max(ys) - min(ys), 1e-9)


def fit_arc(make, target: float, lo: float = 0.005, hi: float = math.pi):
    """The arc turn whose bbox aspect is closest to the target.

    The aspect is not monotonic for a log spiral once it wraps, so scan and
    take the closest, then refine locally.
    """
    best, best_err = lo, float("inf")
    steps = 400
    for i in range(steps + 1):
        phi = lo + (hi - lo) * i / steps
        err = abs(aspect(orient(make(phi))) - target)
        if err < best_err:
            best, best_err = phi, err
    span = (hi - lo) / steps
    for _ in range(30):
        for phi in (best - span, best + span):
            if lo <= phi <= hi:
                err = abs(aspect(orient(make(phi))) - target)
                if err < best_err:
                    best, best_err = phi, err
        span *= 0.5
    return orient(make(best))


def fit_hyper(target: float):
    """A window of r=a/θ whose oriented bbox has the target aspect."""
    best = (float("inf"), 1.4, 3.1)
    for t0 in [0.3 + 0.1 * i for i in range(30)]:
        for phi in [0.2 + 0.1 * j for j in range(60)]:
            err = abs(aspect(orient(hyper_points(t0, phi))) - target)
            if err < best[0]:
                best = (err, t0, phi)
    _, t0, phi = best
    return orient(hyper_points(t0, phi)), t0, phi


def placed(points, h: float, w: float = W):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    scale = min((w - 2 * MARGIN) / max(x1 - x0, 1e-9),
                (h - 2 * MARGIN) / max(y1 - y0, 1e-9))
    dx = (w - (x1 - x0) * scale) / 2
    dy = (h - (y1 - y0) * scale) / 2
    return [(dx + (x - x0) * scale, h - (dy + (y - y0) * scale))
            for x, y in points]



def hip_strip(label: str, points) -> str:
    """A 24 x 5 inch frame (100 units per inch), curve scaled to fit."""
    w, h = 2400.0, 500.0
    pts = placed(points, h, w)
    d = " ".join(f"{'M' if i == 0 else 'L'} {x:.2f} {y:.2f}"
                 for i, (x, y) in enumerate(pts))
    grid = "".join(f'<line x1="{i * 100}" y1="0" x2="{i * 100}" y2="{h}"/>'
                   for i in range(1, 24))
    grid += "".join(f'<line x1="0" y1="{i * 100}" x2="{w}" y2="{i * 100}"/>'
                    for i in range(1, 5))
    fill = min(24.0, 5.0 * aspect(points))
    return f"""<div class="strip">
  <svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <g stroke="#e8dfc8" stroke-width="0.6">{grid}</g>
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="none"
          stroke="#d8ccae" stroke-width="1"/>
    <path d="{d}" fill="none" stroke="#2e2413" stroke-width="2.2"/>
  </svg>
  <p><strong>{label}</strong> · at 5 in high it spans {fill:.1f} in of 24</p>
</div>"""


def strip(label: str, points, n: int) -> str:
    h = n * 100.0
    pts = placed(points, h)
    d = " ".join(f"{'M' if i == 0 else 'L'} {x:.2f} {y:.2f}"
                 for i, (x, y) in enumerate(pts))
    grid = "".join(f'<line x1="{g * 100}" y1="0" x2="{g * 100}" y2="{h}"/>'
                   for g in range(1, 8))
    grid += "".join(f'<line x1="0" y1="{g * 100}" x2="{W}" y2="{g * 100}"/>'
                    for g in range(1, n))
    return f"""<div class="strip">
  <svg viewBox="0 0 {W:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <g stroke="#e8dfc8" stroke-width="0.6">{grid}</g>
    <rect x="0" y="0" width="{W:.0f}" height="{h:.0f}" fill="none"
          stroke="#d8ccae" stroke-width="1"/>
    <path d="{d}" fill="none" stroke="#2e2413" stroke-width="2.2"/>
  </svg>
  <p><strong>{label}</strong> · 8 × {n} in
    {"" if abs(aspect(points) - 8.0 / n) < 0.06 else
     f"· the arc itself fills 8 × {8.0 / aspect(points):.1f}"}</p>
</div>"""


def main() -> int:
    rows = []
    for family in ("log spiral · b = 0.18", "hyperbolic", "clothoid"):
        strips = []
        for n in (1, 2, 3, 4, 5):
            if family.startswith("log"):
                points = fit_arc(lambda phi: log_points(0.18, phi), 8.0 / n)
                label = family
            elif family.startswith("hyper"):
                points, t0, phi = fit_hyper(8.0 / n)
                label = f"hyperbolic · θ {t0:.1f}–{t0 + phi:.1f}"
            else:
                points = fit_arc(clothoid_points, 8.0 / n)
                label = family
            strips.append(strip(label, points, n))
        rows.append((family, "".join(strips)))

    hip = "".join((
        hip_strip("log spiral · 180°", fit_arc(lambda p: log_points(0.18, p), 4.8)),
        hip_strip("hyperbolic · 180° window", fit_hyper(4.8)[0]),
        hip_strip("clothoid · 180°", fit_arc(clothoid_points, 4.8)),
    ))
    sections = "".join(
        f'<h2>{family}</h2><div class="panel">{strips}</div>'
        for family, strips in rows)

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Spirals at dress-curve proportions</title>
<style>
  :root {{ color-scheme: light; --paper:#f6f1e4; --card:#fffdf7; --ink:#2e2413;
    --muted:#7b6c4e; --gold:#8c6a21; --line:#d8ccae;
    --mono: ui-monospace,"SF Mono",Menlo,Consolas,monospace;
    --serif:"EB Garamond",Georgia,"Palatino Linotype",Palatino,serif; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; color:var(--ink); font:16px/1.55 var(--serif);
    background: radial-gradient(900px 440px at 12% -8%, #fcf9ef 0, transparent 60%), var(--paper); }}
  main {{ max-width: 920px; margin: 0 auto; padding: 34px 22px 70px; }}
  h1 {{ font-size: 28px; margin: 0 0 4px; }}
  .lead {{ color: var(--gold); margin: 0 0 18px; }}
  h2 {{ font: 600 11px/1.2 var(--mono); letter-spacing:.12em; text-transform:uppercase;
    color:var(--muted); margin:26px 0 8px; }}
  .panel {{ background:var(--card); border:1px solid var(--line); border-radius:6px; padding:12px; }}
  .strip {{ margin: 0 0 14px; }}
  .strip:last-child {{ margin-bottom: 0; }}
  .strip svg {{ display:block; width:100%; height:auto; background:#fff;
    border:1px solid var(--line); border-radius:3px; }}
  .strip p {{ margin:5px 0 0; font:10px/1.3 var(--mono); color:var(--muted); }}
  .strip strong {{ color:var(--ink); }}
  table {{ border-collapse:collapse; width:100%; font:12px/1.5 var(--mono); }}
  th, td {{ border-bottom:1px solid var(--line); padding:6px 4px; text-align:left; }}
  th {{ color:var(--muted); font-weight:500; }}
  .scroll {{ overflow-x:auto; }}
  .back {{ font:12px var(--mono); margin-bottom:16px; }}
  a {{ color:var(--gold); }}
  @media (max-width:620px) {{
    main {{ padding:22px 14px 60px; }}
    table {{ font-size:10px; }} th,td {{ padding:4px 2px; }}
  }}
</style>
</head>
<body>
<main>
  <p class="back"><a href="sandbox.html">← sandbox</a></p>
  <h1>Spirals at dress-curve proportions</h1>
  <p class="lead">8 inches wide, 1 to 5 inches high. Each strip uses the arc of
  that family whose bounding box is 8:n, so it fills the shape.</p>

  <div class="panel" style="margin-bottom:18px">
    <p>Shallow strips are small turns; tall strips are large turns. Compare the
    <em>asymmetry</em>: a log spiral tightens toward one end by a fixed ratio;
    a clothoid tightens continuously; a hyperbolic has a long asymptotic arm.</p>
  </div>

  <h2>The real hip curve: 24 × 5 with a 180° hook</h2>
  <div class="panel">
    <p>A 24 × 5 shape is 4.8:1. A single log-spiral or clothoid arc over 180°
    only reaches about 2:1, so at 5 inches high it spans about 10–11 inches, not
    24. The hyperbolic reaches 4.8:1 with a long asymptotic arm and a hook — the
    closest single-curve match. If the real curve is a long arm followed by a
    separate 180° hook, it is a compound, not one spiral.</p>
    {hip}
  </div>

  {sections}

  <h2>How to identify the real one</h2>
  <div class="panel">
    <div class="scroll"><table>
      <tr><th>family</th><th>equation</th><th>signature</th></tr>
      <tr><td>log spiral</td><td>r = a e^(bθ)</td><td>tangent–radius angle constant; ρ ∝ s</td></tr>
      <tr><td>clothoid</td><td>κ = s / A²</td><td>curvature linear in arc length; ρ ∝ 1/s</td></tr>
      <tr><td>hyperbolic</td><td>r = a / θ</td><td>rθ constant; asymptote</td></tr>
      <tr><td>log-aesthetic</td><td>ρ^α = c₀s + c₁</td><td>α = 1 log; α = −1 clothoid</td></tr>
    </table></div>
    <p style="margin-top:10px">Pick the strip closest to the physical curve, then
    scan it: the fit gives b, the θ window or α. The page is an eye test, not a
    proof.</p>
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
