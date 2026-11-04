"""Two elevated quadratics: a G1 S, not a G2 S.

    .venv/bin/python scripts/quadratic_s.py

The two halves are exact parabolas (degree-elevated cubics). They meet with
matching tangent direction, but their signed curvatures are opposite. A
nondegenerate parabola has one curvature sign, so a G2 join across a curvature
reversal is not available in this family.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab.quadratic import ascent, at, elevate  # noqa: E402


def curvature_end(P):
    v = (P[3][0] - P[2][0], P[3][1] - P[2][1])
    w = (P[3][0] - 2*P[2][0] + P[1][0], P[3][1] - 2*P[2][1] + P[1][1])
    cross = v[0]*w[1] - v[1]*w[0]
    return (2/3)*float(cross)/(math.hypot(float(v[0]), float(v[1]))**3)


def curvature_start(P):
    v = (P[1][0] - P[0][0], P[1][1] - P[0][1])
    w = (P[2][0] - 2*P[1][0] + P[0][0], P[2][1] - 2*P[1][1] + P[0][1])
    cross = v[0]*w[1] - v[1]*w[0]
    return (2/3)*float(cross)/(math.hypot(float(v[0]), float(v[1]))**3)


def svg(left, right, w=1000, h=560):
    pts = left + right
    x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts)
    x1, y1 = max(p[0] for p in pts), max(p[1] for p in pts)
    dx, dy = x1-x0 or 1, y1-y0 or 1
    pad = .18
    xa, xb = x0-pad*dx, x1+pad*dx
    ya, yb = y0-pad*dy, y1+pad*dy
    k = min((w-80)/(xb-xa), (h-100)/(yb-ya))
    ox = (w-(xb-xa)*k)/2
    oy = 42+(h-78-(yb-ya)*k)/2

    def put(p):
        return ox+(p[0]-xa)*k, h-(oy+(p[1]-ya)*k)

    body = []
    for gx in range(int(xa)//10*10, int(xb)+10, 10):
        a, b = put((gx, ya)), put((gx, yb))
        body.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#e4dcc6"/>')
    for gy in range(int(ya)//5*5, int(yb)+5, 5):
        a, b = put((xa, gy)), put((xb, gy))
        body.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#e4dcc6"/>')

    def path(P, colour):
        d = " ".join(f"{put(at(P, i/100))[0]:.1f} {put(at(P, i/100))[1]:.1f}" for i in range(101))
        body.append(f'<path d="M {d}" fill="none" stroke="{colour}" stroke-width="2.6" stroke-linejoin="round"/>')
        d = " ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in P)
        body.append(f'<path d="M {d}" fill="none" stroke="{colour}" stroke-width="1" stroke-dasharray="4 4" opacity=".85"/>')

    path(left, "#c9a441")
    path(right, "#1f5fa8")
    labels = [
        ("L0 (−30,0)", left[0], 2, -1.2),
        ("L1 (−20,10)", left[1], 2, 1.4),
        ("L2 (−10,10)", left[2], -17, 1.4),
        ("join (0,0)", left[3], 2, -1.4),
        ("R1 (10,−10)", right[1], 2, -1.2),
        ("R2 (20,−10)", right[2], 2, -1.2),
        ("R3 (30,0)", right[3], -12, 1.4),
    ]
    for text, p, dx, dy in labels:
        q = put(p)
        body.append(f'<text x="{q[0]+dx:.1f}" y="{q[1]+dy:.1f}" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="#2e2413" stroke="#fbf7ec" stroke-width="3" paint-order="stroke">{text}</text>')
    q = put(left[3])
    body.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="4.5" fill="#2e2413" stroke="#fbf7ec"/>')
    body.append('<text x="12" y="19" font-family="Georgia,serif" font-size="14" font-weight="600" fill="#2e2413">Fig. Q1 · two elevated quadratics · G1 join</text>')
    body.append('<text x="12" y="34" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#7b6c4e">join tangent (10,−10) · curvature left −0.023570 · right +0.023570 · G2 no</text>')
    body.append(f'<text x="12" y="{h-34}" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="#7b6c4e">— left parabola   — right parabola   -- control   • join</text>')
    body.append(f'<text x="12" y="{h-8}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#7b6c4e">x →</text>')
    body.append(f'<text x="{w-38}" y="{h-8}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#7b6c4e">y ↑</text>')
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{w}" height="{h}" fill="#fbf7ec" stroke="#d8ccae"/>'
            + "".join(body) + "</svg>")


def main():
    left, right = ascent()
    k_left = curvature_end(left)
    k_right = curvature_start(right)
    drawing = svg(left, right)
    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Two-parabola S probe</title>
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
.figure svg{{display:block;width:100%;height:auto}}
table{{border-collapse:collapse;width:100%;font:11px/1.5 ui-monospace,Menlo,monospace;margin:10px 0}}
th,td{{border:1px solid var(--rule);padding:5px 7px;text-align:left}}
th{{width:30%;color:var(--muted);font-weight:400}}
code{{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}}
.small{{font:12px/1.55 ui-monospace,Menlo,monospace;color:var(--muted)}}
</style>
</head>
<body>
<main>
<p class="eyebrow">curve-lab · quadratic elevation probe</p>
<h1>Two-parabola S probe</h1>
<p class="lede">Two quadratics can make a clean S with a G1 join. They cannot make a <strong>G2</strong> S across a curvature reversal: a nondegenerate parabola has one curvature sign, and the two halves meet with opposite signed curvature.</p>
<section class="panel">
  <h2>Fig. Q1 · the two elevated quadratics</h2>
  <div class="figure">{drawing}</div>
  <table>
    <tr><th>join tangent</th><td><code>(10,−10)</code></td></tr>
    <tr><th>left end curvature</th><td><code>{k_left:.6f}</code></td></tr>
    <tr><th>right start curvature</th><td><code>{k_right:.6f}</code></td></tr>
    <tr><th>G1</th><td>yes</td></tr>
    <tr><th>G2</th><td>no — curvature sign reverses</td></tr>
    <tr><th>elevated controls</th><td><code>L=(−30,0),(−20,10),(−10,10),(0,0)</code>; <code>R=(0,0),(10,−10),(20,−10),(30,0)</code></td></tr>
  </table>
</section>
<section class="panel">
  <h2>What this means</h2>
  <p>Degree elevation is exact, but it does not add a curvature reversal. A single parabola has one curvature sign. Joining two parabolas across the middle can give a visual S with a tangent match; the curvature jumps from one sign to the other. That is a G1 joint, not a G2 joint.</p>
  <p>The integer cubic family is the right home for an exact S with a genuine inflection. Keep quadratic elevation for a one-bend arc, or for a piecewise-parabolic S that accepts a measured G1 curvature jump.</p>
</section>
</main>
</body>
</html>
'''
    out = ROOT / "workbench" / "quadratic-s.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    print(f"  left κ={k_left:.6f} right κ={k_right:.6f} G1=yes G2=no")


if __name__ == "__main__":
    main()
