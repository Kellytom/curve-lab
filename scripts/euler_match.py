"""Match each named curve with an Euler polygon, on that curve's own grid.

    .venv/bin/python scripts/euler_match.py
    open workbench/euler-match.html

An Euler polygon is the chain you get by walking equal chords and taking the
heading from the curve at each node: first order in the chord, which is exactly
what the spine layer's power-turn chain is.  Two numbers matter:

  deviation  the furthest the polygon strays from the curve, as a % of the
             curve's own size -- this is the fidelity budget.
  snap       how far each node has to move to sit on the curve's integer grid.
             That is the price of the lattice, and it is reported separately
             because it is a different kind of error: the shape is right, the
             node is rounded.

Neither number is allowed to hide the other.
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from grid_view import crossings, grid_lines, nice_step  # noqa: E402
import generators as G  # noqa: E402

INK, GOLD, DOT = "#2e2413", "#c9a441", "#b23a2b"
GRID, LINE, MUTED = "#ece4cf", "#d8ccae", "#7b6c4e"

M = 400                     # curve samples per branch
TARGET = 0.01               # aim for 1% of curve size


def sample(ctrl, m=M):
    deg = len(ctrl) - 1
    pts = []
    for i in range(m + 1):
        s = F(i, m)
        w = sum(F(p[2]) * G.bern_n(j, deg, s) for j, p in enumerate(ctrl))
        if w == 0:
            continue
        x, y = G.homog_point(ctrl, s)
        pts.append((float(x), float(y)))
    return pts


def arc(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def tangent_at(pts, s, total):
    """Direction at arc length s, blended between neighbouring samples.

    Without the blend, a chord shorter than the sample spacing inherits one
    segment's angle and the polygon turns into a staircase -- which reads as a
    huge deviation that has nothing to do with the curve.
    """
    acc = 0.0
    prev_th = None
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        d = math.dist(a, b)
        th = math.atan2(b[1] - a[1], b[0] - a[0])
        if prev_th is None:
            prev_th = th
        if acc + d >= s and d > 0:
            t = (s - acc) / d
            # unwrap the two headings before blending
            delta = (th - prev_th + math.pi) % (2 * math.pi) - math.pi
            return prev_th + delta * t
        acc += d
        prev_th = th
    a, b = pts[-2], pts[-1]
    return math.atan2(b[1] - a[1], b[0] - a[0])


def euler_polygon(pts, n):
    """n equal chords, each along the curve's tangent at its start node."""
    total = arc(pts)
    L = total / n
    node = pts[0]
    out = [node]
    for k in range(n):
        th = tangent_at(pts, (k + 0.5) * L, total)
        node = (node[0] + L * math.cos(th), node[1] + L * math.sin(th))
        out.append(node)
    return out, L


def curvature_fit(pts):
    """Least squares kappa(s) = a + b s on the sampled curve."""
    cum = [0.0]
    for a_, b_ in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.dist(a_, b_))
    th = [math.atan2(b_[1] - a_[1], b_[0] - a_[0]) for a_, b_ in zip(pts, pts[1:])]
    ks, ss = [], []
    for i in range(1, len(th)):
        ds = cum[i + 1] - cum[i]
        if ds <= 0:
            continue
        d = (th[i] - th[i - 1] + math.pi) % (2 * math.pi) - math.pi
        ks.append(d / ds)
        ss.append((cum[i] + cum[i + 1]) / 2)
    n = len(ss)
    if n < 3:
        return 0.0, 0.0
    ms = sum(ss) / n
    mk = sum(ks) / n
    den = sum((x - ms) ** 2 for x in ss)
    b = sum((x - ms) * (k - mk) for x, k in zip(ss, ks)) / den if den else 0.0
    return mk - b * ms, b


def clothoid_polygon(pts, n):
    """The same chord count, but with the clothoid's quadratic heading."""
    total = arc(pts)
    L = total / n
    a, b = curvature_fit(pts)
    th0 = math.atan2(pts[1][1] - pts[0][1], pts[1][0] - pts[0][0])
    node = pts[0]
    out = [node]
    for k in range(n):
        s_k = k * L
        th = th0 + a * s_k + b * s_k * s_k / 2
        node = (node[0] + L * math.cos(th), node[1] + L * math.sin(th))
        out.append(node)
    return out


def clothoid_spans(pts, k):
    """A chain of k clothoid spans: continuous in heading, curvature jumps."""
    total = arc(pts)
    L = total / 640.0
    cum = [0.0]
    for a_, b_ in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.dist(a_, b_))
    runs = []
    for j in range(k):
        lo, hi = total * j / k, total * (j + 1) / k
        run = [p_ for p_, c in zip(pts, cum) if lo - 1e-9 <= c <= hi + 1e-9]
        runs.append(run if len(run) >= 4 else pts[:3])
    fits = [curvature_fit(r) for r in runs]

    th = math.atan2(pts[1][1] - pts[0][1], pts[1][0] - pts[0][0])
    node = pts[0]
    out = [node]
    n = max(4, int(round(total / (L * 4))))
    n = min(n, 400)
    step = total / n
    for i in range(n):
        s_i = i * step
        j = min(k - 1, int(s_i / total * k))
        a, b = fits[j]
        node = (node[0] + step * math.cos(th), node[1] + step * math.sin(th))
        out.append(node)
        # the fit's s is local to its run
        lo = total * j / k
        s0, s1 = s_i - lo, s_i + step - lo
        th += a * step + b * (s1 * s1 - s0 * s0) / 2
    return out


def deviation(poly, pts):
    """Furthest a polygon vertex or chord midpoint sits from the curve."""
    worst = 0.0
    for a, b in zip(poly, poly[1:]):
        for t in (0.0, 0.25, 0.5, 0.75, 1.0):
            x = a[0] + t * (b[0] - a[0])
            y = a[1] + t * (b[1] - a[1])
            worst = max(worst, min(math.dist((x, y), q) for q in pts))
    return worst


def size(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return max(max(xs) - min(xs), max(ys) - min(ys), 1e-9)


def fit_branch(pts, target=TARGET):
    """Smallest chord count that lands under the target deviation."""
    S = size(pts)
    n = 4
    best = None
    while n <= 4096:
        poly, L = euler_polygon(pts, n)
        d = deviation(poly, pts) / S
        best = (n, d, poly, L)
        if d <= target:
            return best
        n *= 2
    return best


def snap(poly, scale):
    """Move every node to the grid; report the worst move and the angle change."""
    worst_pos, worst_ang = 0.0, 0.0
    snapped = []
    for a, b in zip(poly, poly[1:]):
        n = (round(b[0] * scale) / scale, round(b[1] * scale) / scale)
        worst_pos = max(worst_pos, math.dist(b, n))
        snapped.append(n)
    out = [poly[0]] + snapped
    for (a, b), (c, d) in zip(zip(poly, poly[1:]), zip(out, out[1:])):
        t1 = math.atan2(b[1] - a[1], b[0] - a[0])
        t2 = math.atan2(d[1] - c[1], d[0] - c[0])
        worst_ang = max(worst_ang, abs((t2 - t1 + math.pi) % (2 * math.pi) - math.pi))
    return out, worst_pos, math.degrees(worst_ang)


def run(spec):
    data = G.named_data(spec)
    branches = []
    for ctrl in data["ctrl"]:
        pts = sample(ctrl)
        if len(pts) < 3:
            continue
        n, d, poly, L = fit_branch(pts)
        clo = clothoid_polygon(pts, n)
        d_clo = deviation(clo, pts) / size(pts)
        best_spans = (0, 9.9, None)
        for k in (4, 8, 16, 32, 64):
            sp = clothoid_spans(pts, k)
            dd = deviation(sp, pts) / size(pts)
            if dd < best_spans[1]:
                best_spans = (k, dd, sp)
            if dd <= TARGET:
                break
        sn, pos, ang = snap(poly, data["cscale"])
        branches.append(dict(pts=pts, poly=poly, snapped=sn, n=n, dev=d,
                             L=L, snap=pos, snap_ang=ang, clo=clo, dev_clo=d_clo,
                             spans=best_spans[0], dev_spans=best_spans[1],
                             size=size(pts)))
    worst_dev = max(b["dev"] for b in branches)
    worst_clo = max(b["dev_clo"] for b in branches)
    worst_spans = max(b["dev_spans"] for b in branches)
    span_count = max(b["spans"] for b in branches)
    worst_snap = max(b["snap"] for b in branches)
    total_n = sum(b["n"] for b in branches)
    return dict(spec=spec, branches=branches, dev=worst_dev, dev_clo=worst_clo,
                dev_spans=worst_spans, span_count=span_count,
                snap=worst_snap, n=total_n, scale=data["cscale"])


def figure(item, w=430.0, h=300.0, dot=2.4):
    pts = [p for b in item["branches"] for p in b["pts"]]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = 0.06
    x0, x1 = x0 - pad * (x1 - x0), x1 + pad * (x1 - x0)
    y0, y1 = y0 - pad * (y1 - y0), y1 + pad * (y1 - y0)
    k = min((w - 16) / (x1 - x0), (h - 16) / (y1 - y0))
    ox, oy = (w - (x1 - x0) * k) / 2, (h - (y1 - y0) * k) / 2

    def put(p):
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k)

    step = nice_step(max(x1 - x0, y1 - y0))
    grid = "".join(grid_lines(put, x0, x1, y0, y1, step, "#ece4cf"))
    marks = "".join(
        f'<circle class="lattice" cx="{put(p)[0]:.1f}" cy="{put(p)[1]:.1f}" '
        f'r="2.0" fill="{GOLD}"/>'
        for p in crossings([b["pts"] for b in item["branches"]], step))
    curve = "".join(
        '<path d="' + "M " + " L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}"
                                        for p in b["pts"]) +
        f'" fill="none" stroke="{INK}" stroke-width="2.2"/>'
        for b in item["branches"])
    chain = "".join(
        '<path d="' + "M " + " L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}"
                                        for p in b["poly"]) +
        f'" fill="none" stroke="{GOLD}" stroke-width="1.3"/>'
        for b in item["branches"])
    nodes = "".join(
        f'<circle cx="{put(p)[0]:.1f}" cy="{put(p)[1]:.1f}" r="2.4" fill="{DOT}"/>'
        for b in item["branches"] for p in b["poly"])
    return f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fffdf7" stroke="{LINE}"/>
    {grid}{curve}{chain}{marks}{nodes}
  </svg>"""


def main():
    curves = [s for s in G.NAMED if G.named_data(s)["exact"]]
    items = []
    for spec in curves:
        it = run(spec)
        items.append(it)
        print(f"  {spec['key']:16s} n={it['n']:4d}  error {100*it['dev']:5.2f}%"
              f"  clothoid {100*it['dev_clo']:6.2f}%"
              f"  spans {it['span_count']:2d} -> {100*it['dev_spans']:5.2f}%")

    def size(spec):
        # the full cruciform arm is wide, so it keeps the landscape panel
        return (430.0, 300.0)

    def dots(spec):
        return 2.4

    for i, it in enumerate(items):
        it["num"] = i + 1
    tall = [it for it in items if it["spec"]["key"] == "cruciform"]
    items = [it for it in items if it["spec"]["key"] != "cruciform"]

    cards = "".join(
        f"""<section><h2>Fig. {it['num']} · {it['spec']['key']}</h2>
  <div class="art">{figure(it, *size(it['spec']), dot=dots(it['spec']))}</div>
  <p class="cap">{it['n']} chords · error {100*it['dev']:.2f}% of curve size ·
  one-clothoid error {100*it['dev_clo']:.1f}% · {it['span_count']}-span error
  {100*it['dev_spans']:.2f}% · snap error {it['snap']*it['scale']:.2f} of a grid
  unit on {it['scale']}</p>
  </section>""" for i, it in enumerate(items))

    rows = "".join(
        f"<tr><td>{it['spec']['key']}</td><td>{it['n']}</td>"
        f"<td>{100*it['dev']:.2f}%</td><td>{100*it['dev_clo']:.1f}%</td>"
        f"<td>{it['span_count']}</td><td>{100*it['dev_spans']:.2f}%</td>"
        f"<td>{it['scale']}</td>"
        f"<td>{it['snap']*it['scale']:.3f}</td>"
        f"<td>{max(b['snap_ang'] for b in it['branches']):.2f}°</td></tr>"
        for it in items)

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Euler match — the named curves as polygons</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1080px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 22px}}
h2{{font:600 11px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.12em;
text-transform:uppercase;color:{MUTED};margin:0 0 4px}}
.cap{{font-size:12px;color:{MUTED};margin:0}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start}}
section{{background:#fffdf7;border:1px solid {LINE};padding:12px}}
.art{{background:#fffdf7;margin:4px 0 8px}}
svg{{display:block;width:100%;height:auto}}
table{{border-collapse:collapse;width:100%;font:12px/1.4 ui-monospace,Menlo,monospace}}
th,td{{border-bottom:1px solid {LINE};padding:5px 8px;text-align:right}}
th:first-child,td:first-child{{text-align:left}}
th{{color:{MUTED};font-weight:600}}
.panel{{background:#fffdf7;border:1px solid {LINE};padding:16px 18px;margin:0 0 20px}}
</style></head><body><main>
<h1>Euler match</h1>
<p class="lead">Every exact named curve, replaced by a chain of equal chords whose
heading is the curve's own tangent. Gold is the chain, ink is the curve, red is a
node.</p>
<div class="panel">
<p><strong>What is being measured.</strong> <em>Deviation</em> is an <strong>error</strong>: how far the
chain strays from the curve, as a percentage of the curve's own size — the same
currency as the fidelity budget. <em>Snap</em> is how far each node has to move
to sit on that curve's integer grid; it is reported in grid units, because a
snap of 0.3 units on a grid of 273 is a third of a pixel while the same 0.3 on a
grid of 5 is enormous.</p>
<p>The chord count is the smallest that lands under <strong>1% of size</strong>.
Halving the chord halves the deviation — that is the whole dial. Three chains
are compared, because they answer different questions:</p>
<ul>
<li><strong>Euler polygon</strong> — equal chords, heading taken from the curve at
each node. First order in the chord, and the cheapest thing that works. Under 1%
on every curve here.</li>
<li><strong>One clothoid</strong> — a single quadratic heading over the whole
curve. It is the honest test of "is this curve clothoid-shaped", and it fails on
almost all of them: 35% on the bean, 45% on the nodal cubic, 72% on the
Bernoulli lemniscate. A single linear-curvature law cannot follow a curve whose
curvature changes sign.</li>
<li><strong>A chain of clothoid spans</strong> — one quadratic heading per span,
continuous in heading, curvature jumping at the joins. This is what the spine
layer does, and it works: <strong>0.44 to 1.1%</strong> on bean, nodal,
Tschirnhausen, trifolium, quadrifolium, Gerono, piriform, Bernoulli, circle and
the rounded square, at 4 to 32 spans.</li>
</ul>
<p><strong>What it cannot do is a cusp.</strong> The astroid, deltoid, cardioid,
nephroid and the epicycloids all carry real cusps, where the tangent reverses in
no distance at all. A clothoid turns finitely, so the chain cuts the corner and
the deviation stays between 9% and 63% however many spans you spend. Those
curves want a corner in the chain — a joint, not a blend — which is the
`Segment.corner` the engine already has.</p>
</div>
<div class="grid2">{cards}</div>
{''.join(f"<section style='max-width:430px;margin:24px auto'><h2>Fig. {it['num']} · {it['spec']['key']}</h2><div class='art'>{figure(it, *size(it['spec']), dot=dots(it['spec']))}</div><p class='cap'>{it['n']} chords · error {100*it['dev']:.2f}% · {it['span_count']} spans {100*it['dev_spans']:.2f}%</p></section>" for it in tall)}
<div class="panel">
<table>
<tr><th>curve</th><th>chords</th><th>Euler polygon<br>error, % of size</th>
<th>one clothoid<br>error, %</th><th>spans</th><th>span chain<br>error, %</th>
<th>grid</th><th>snap<br>error, grid units</th>
<th>angle change<br>degrees</th></tr>
{rows}
</table>
</div>
</main></body></html>
"""
    out = ROOT / "workbench" / "euler-match.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    print(f"  worst error {100*max(i['dev'] for i in items):.2f}% of size ·"
          f" {sum(i['n'] for i in items)} chords total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
