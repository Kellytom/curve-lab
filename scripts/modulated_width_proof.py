"""Modulated width proof: the rails are not a parallel offset, measured.

    .venv/bin/python scripts/modulated_width_proof.py

The width law is `w(u) = w0 (1 + 64 a u^3 (1-u)^3)`, the former Stage IV law.
The page draws the spine with its two rails and, dashed, a constant band of the
same base width. It reports the width ratio, the terminal seam, the maximum
deviation from the constant band, and the rail self-intersections.

The law is exact as a width; the rails are a normal construction, not an
equidistant offset. That distinction is the proof.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from modulated_width import cubic, rails, width_law  # noqa: E402
import plant_forms as PF  # noqa: E402

INK, BLUE, RED, GOLD = "#2e2413", "#1f5fa8", "#a23b2a", "#c9a441"
MUTED, PAPER = "#7b6c4e", "#fffdf7"

A = 0.6
W0 = 1.0
SPINE = cubic((0.0, 0.0), (3.2, 2.6), (6.8, -2.6), (10.0, 0.0), 320)


def _hits(pts):
    def cr(o, p, q):
        return (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])
    count = 0
    for i in range(len(pts) - 1):
        for j in range(i + 2, len(pts) - 1):
            a, b, c, d = pts[i], pts[i + 1], pts[j], pts[j + 1]
            d1, d2 = cr(a, b, c), cr(a, b, d)
            d3, d4 = cr(c, d, a), cr(c, d, b)
            if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
                count += 1
    return count


def proof_data() -> dict:
    left, right = rails(SPINE, A, W0)
    n = len(SPINE) - 1
    widths = [width_law(i / n, A, W0) for i in range(n + 1)]
    sep = [math.dist(left[i], right[i]) for i in range(n + 1)]
    deviation = max(abs((w - W0) / 2.0) for w in widths)
    return {
        "a": A,
        "w0": W0,
        "ratio": max(widths) / min(widths),
        "w_max": max(widths),
        "seam": (widths[0], widths[-1]),
        "deviation": deviation,
        "sep_error": max(abs(sep[i] - widths[i]) for i in range(n + 1)),
        "hits_left": _hits(left),
        "hits_right": _hits(right),
        "samples": n + 1,
        "widths": widths,
        "spine": SPINE,
        "left": left,
        "right": right,
    }


def width_plot(widths, w=420, h=240):
    pts = [(i / (len(widths) - 1), widths[i]) for i in range(len(widths))]
    ys = [p[1] for p in pts]
    x0, x1 = 0.0, 1.0
    y0, y1 = min(ys), max(ys)
    pad = 0.15 * (y1 - y0 or 1)
    y0, y1 = y0 - pad, y1 + pad
    kx, ky = (w - 70), (h - 50)
    def put(p):
        return 50 + p[0] * kx, h - 25 - (p[1] - y0) / (y1 - y0) * ky
    body = []
    # constant band reference
    yc = put((0.0, W0))[1]
    body.append(f'<line x1="50" y1="{yc:.1f}" x2="{w-20}" y2="{yc:.1f}" '
                f'stroke="{MUTED}" stroke-width="1" stroke-dasharray="4 3"/>')
    d = " ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in pts)
    body.append(f'<rect width="{w}" height="{h}" fill="{PAPER}" stroke="#e4dcc6"/>')
    body.append(f'<path d="M {d}" fill="none" stroke="{BLUE}" stroke-width="2"/>')
    body.append(f'<text x="12" y="18" font-family="Georgia,serif" font-size="12" fill="{INK}">width w(u) against the constant band</text>')
    body.append(f'<text x="12" y="{h-8}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{MUTED}">u 0 → 1 · dashed = w0 · solid = modulated</text>')
    body.append(f'<text x="50" y="{h-28}" font-family="ui-monospace,Menlo,monospace" font-size="9" fill="{MUTED}">0</text>')
    body.append(f'<text x="{w-30}" y="{h-28}" font-family="ui-monospace,Menlo,monospace" font-size="9" fill="{MUTED}">1</text>')
    return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">' + "".join(body) + "</svg>"


def main() -> int:
    d = proof_data()
    items = [
        (d["spine"], INK, 2.2, None),
        (d["left"], BLUE, 1.2, None),
        (d["right"], RED, 1.2, None),
        (PF.normal_offsets(d["spine"], W0 / 2.0)[0], MUTED, 1.0, "4 3"),
        (PF.normal_offsets(d["spine"], W0 / 2.0)[1], MUTED, 1.0, "4 3"),
    ]
    hero = PF.figure(items, 900, 420)
    plot = width_plot(d["widths"])

    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Modulated width proof — not a parallel offset</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1000px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 18px}}
h2{{font:600 12px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.10em;text-transform:uppercase;color:{MUTED};margin:30px 0 8px}}
.panel{{background:{PAPER};border:1px solid #d8ccae;padding:16px 18px;margin:0 0 18px}}
.art{{background:{PAPER};border:1px solid #d8ccae;padding:8px;margin:0 0 8px}}
svg{{display:block;width:100%;height:auto}}
.legend{{display:flex;gap:16px;flex-wrap:wrap;font:11px ui-monospace,Menlo,monospace;color:{MUTED};margin:6px 0 0}}
.sw{{display:inline-block;width:20px;height:0;border-top:3px solid {INK};margin-right:5px;vertical-align:middle}}
.sw.b{{border-top:2px solid {BLUE}}}.sw.r{{border-top:2px solid {RED}}}
.sw.m{{border-top:2px dashed {MUTED}}}
table{{border-collapse:collapse;width:100%;font:12px/1.5 ui-monospace,Menlo,monospace;margin:8px 0 0}}
td,th{{border-bottom:1px solid #d8ccae;padding:5px 8px;text-align:left}}
th{{color:{MUTED};font-weight:600}}
code{{font:12px ui-monospace,Menlo,monospace}}
</style></head><body><main>
<h1>Modulated width proof</h1>
<p class="lead">The width is a declared function, not a parallel offset. The
measurement below is the difference between the two ideas.</p>

<div class="panel">
<p><strong>The law.</strong> w(u) = w0 (1 + 64a u³(1−u)³), with a =
{d['a']:g} and w0 = {d['w0']:g}. The law, its slope and its curvature all meet
the plain stroke at both ends, so the band is continuous at the seams. The two
rails are built from it; they are not equidistant.</p>
<p><strong>The comparison.</strong> The dashed lines are a constant band at w0,
the 2 × parallel assumption. The solid rails leave it by up to
{d['deviation']:.3f} of a half-width. That difference is the proof: this curve
cannot be put in the 2 × parallel rule without making the rule false.</p>
</div>

<div class="art">{hero}</div>
<div class="legend">
<span><i class="sw"></i> spine</span>
<span><i class="sw b"></i> +rail</span>
<span><i class="sw r"></i> −rail</span>
<span><i class="sw m"></i> constant 2 × band (for comparison)</span>
</div>

<h2>The width itself</h2>
<div class="art">{plot}</div>

<h2>The numbers</h2>
<div class="panel">
<table>
<tr><th>width ratio</th><td>max {d['w_max']:.3f} / min {d['w0']:.3f} = {d['ratio']:.3f}</td></tr>
<tr><th>terminal seam</th><td>w(0) = {d['seam'][0]:.6f} · w(1) = {d['seam'][1]:.6f} · both w0</td></tr>
<tr><th>max deviation</th><td>{d['deviation']:.3f} of a half-width from the constant band</td></tr>
<tr><th>rail separation</th><td>matches w(u) to {d['sep_error']:.2e}</td></tr>
<tr><th>self-intersections</th><td>left {d['hits_left']} · right {d['hits_right']}</td></tr>
<tr><th>samples</th><td>{d['samples']} stations along the spine</td></tr>
</table>
</div>

<h2>What this proves</h2>
<div class="panel">
<p>A variable width is not a wide stroke and not a parallel band. It is a
width function whose rails happen to be smooth here, with no fold and no
self-crossing. The measured seam is exact because the law was chosen to meet
the plain stroke there — that is a design requirement, not a coincidence.</p>
<p class="note">Re-derive: <code>python scripts/modulated_width_proof.py</code> ·
<code>python -m unittest tests.test_modulated_width_proof</code></p>
</div>
</main></body></html>
'''
    out = ROOT / "workbench" / "modulated-width-proof.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
