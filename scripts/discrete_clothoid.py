"""A discrete clothoid: how a p-triple turn schedule tracks κ ∝ s.

    .venv/bin/python scripts/discrete_clothoid.py
    open workbench/discrete-clothoid.html

A clothoid has curvature proportional to arc length. Built from equal chords
it is a turn schedule: at step k the heading turns by Δθ_k ∝ k. Quantise each
Δθ_k to the nearest p-triple angle and the polygon is exact — every node is
rational, every turn is a right-triangle angle — and the schedule still rises
linearly. The quantisation error is bounded by half the gap of the ladder, and
the exponent stays 1 rather than drifting.

This is the rising case. The Euclid family chain is the falling case: its
turns decrease, and its curvature exponent drifts to −4/3 (recorded on the
showcase, Fig. 6c). The same construction gives both; the schedule decides.
"""

from __future__ import annotations

import math
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
from curve_lab import pyth_triples as T  # noqa: E402

PAPER, INK, MUTED, RULE = "#fbf7ec", "#2e2413", "#7b6c4e", "#d8ccae"
RED, BLUE, GOLD = "#a23b2a", "#1f5fa8", "#c9a441"

DELTA = 2.5          # degrees of turn in the first chord
N = 18               # chords
C_MAX = 3125


def ladder(c_max=C_MAX):
    rows = []
    for t in T.base_triples(c_max):
        if t["k"] != 1:
            continue
        a, b, c = t["a"], t["b"], t["c"]
        rows.append({"a": a, "b": b, "c": c,
                     "deg": math.degrees(math.atan2(b, a))})
    rows.append({"a": 1, "b": 0, "c": 1, "deg": 0.0})
    rows.sort(key=lambda r: r["deg"])
    return rows


LADDER = ladder()


def nearest(theta_deg):
    return min(LADDER, key=lambda r: abs(r["deg"] - theta_deg))


def build():
    """The quantised schedule, the ideal one, and both polylines."""
    a2 = 0.5 / math.radians(DELTA)          # κ(0.5) = DELTA in radians
    chosen = []
    for k in range(1, N + 1):
        ideal = (k - 0.5) / a2            # radians
        row = nearest(math.degrees(ideal))
        chosen.append({"k": k, "ideal": math.degrees(ideal), "row": row})

    # exact polygon: unit chords, rational turns, so rational nodes
    x = y = Fraction(0)
    hx, hy = Fraction(1), Fraction(0)
    exact = [(x, y)]
    for step in chosen:
        a, b, c = step["row"]["a"], step["row"]["b"], step["row"]["c"]
        x, y = x + hx, y + hy
        hx, hy = (hx * a - hy * b) / c, (hx * b + hy * a) / c
        exact.append((x, y))
    scale = 1
    for p in exact:
        for v in p:
            scale = scale * v.denominator // math.gcd(scale, v.denominator)

    qu = [(float(p[0]), float(p[1])) for p in exact]

    # the ideal clothoid, integrated
    ideal_pts = []
    s = 0.0
    px = py = 0.0
    for i in range(N * 40 + 1):
        s = N * i / (N * 40)
        th = s * s / (2 * a2)
        px += math.cos(th) * N / (N * 40)
        py += math.sin(th) * N / (N * 40)
        ideal_pts.append((px, py))

    steps = [c["ideal"] for c in chosen]
    measured = [c["row"]["deg"] for c in chosen]
    err = [abs(m - i) for m, i in zip(measured, steps)]
    xs = [math.log10(c["k"] - 0.5) for c in chosen]
    ys = [math.log10(math.radians(c["row"]["deg"])) for c in chosen]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    slope = (sum((x - mx) * (y - my) for x, y in zip(xs, ys))
             / sum((x - mx) ** 2 for x in xs))
    pos = [r["deg"] for r in LADDER if r["deg"] > 0]
    gap = max(b - a for a, b in zip(pos, pos[1:])) if len(pos) > 1 else 0.0
    return dict(chosen=chosen, exact=exact, scale=scale, qu=qu,
                ideal_pts=ideal_pts, err=err, slope=slope,
                max_err=max(err), median_err=sorted(err)[len(err) // 2],
                ladder_size=len(LADDER), gap=gap,
                digits=len(str(scale)))


class Frame:
    def __init__(self, w, h, pts, pad=46):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        self.s = min((w - 2 * pad) / max(1e-9, x1 - x0),
                     (h - 2 * pad) / max(1e-9, y1 - y0))
        self.ox = (w - (x1 - x0) * self.s) / 2 - x0 * self.s
        self.oy = (h - (y1 - y0) * self.s) / 2 + y1 * self.s

    def __call__(self, p):
        return (self.ox + p[0] * self.s, self.oy - p[1] * self.s)


def path(pts, f):
    return " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}"
                    for i, (x, y) in enumerate(f(p) for p in pts))


def fig_schedule(d):
    f = Frame(980, 600, d["ideal_pts"] + d["qu"])
    nodes = "".join(f'<circle cx="{f(p)[0]:.1f}" cy="{f(p)[1]:.1f}" r="3.4" fill="{GOLD}"/>'
                    for p in d["qu"])
    return f"""<svg viewBox="0 0 980 600" width="100%" role="img" aria-label="quantised clothoid and ideal clothoid">
  <rect width="980" height="600" fill="{PAPER}"/>
  <path d="{path(d['ideal_pts'], f)}" fill="none" stroke="{BLUE}" stroke-width="2" stroke-dasharray="7 5"/>
  <path d="{path(d['qu'], f)}" fill="none" stroke="{RED}" stroke-width="2.2"/>
  {nodes}
  <text x="16" y="26" font-family="Georgia,serif" font-size="13" fill="{INK}">Fig. D1 · equal chords, turns Δθ_k ∝ k · quantised to p-triple angles · +y up, flipped to screen</text>
  <text x="16" y="46" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}">{N} chords · δ = {DELTA}° · ideal A² = {0.5 / math.radians(DELTA):.2f} · nodes are rational (scale {d['scale']}, {d['digits']} digits)</text>
  <g font-family="Georgia,serif" font-size="15">
    <line x1="16" y1="572" x2="52" y2="572" stroke="{RED}" stroke-width="2.6"/><text x="60" y="577" fill="{INK}">quantised polygon</text>
    <line x1="250" y1="572" x2="286" y2="572" stroke="{BLUE}" stroke-width="2" stroke-dasharray="7 5"/><text x="294" y="577" fill="{INK}">ideal clothoid</text>
    <circle cx="470" cy="572" r="4" fill="{GOLD}"/><text x="484" y="577" fill="{INK}">node</text>
  </g>
</svg>"""


def fig_law(d):
    w, h, pad = 880, 420, 74
    if w <= 2 * pad or h <= 2 * pad:
        raise ValueError("frame too small")
    xs = [math.log10(c["k"] - 0.5) for c in d["chosen"]]
    ys = [math.log10(math.radians(c["row"]["deg"])) for c in d["chosen"]]
    ideal = [math.log10(math.radians(c["ideal"])) for c in d["chosen"]]
    x0, x1 = min(xs) - 0.2, max(xs) + 0.2
    y0, y1 = min(ys + ideal) - 0.2, max(ys + ideal) + 0.2
    f = Frame(w, h, [(x0, y0), (x1, y1)], pad=pad)

    def line(vals):
        return " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}"
                        for i, (x, y) in enumerate(f((a, b)) for a, b in zip(xs, vals)))

    marks = "".join(
        f'<circle cx="{f((x, y))[0]:.1f}" cy="{f((x, y))[1]:.1f}" r="4.5" fill="{PAPER}" '
        f'stroke="{RED}" stroke-width="2"/>'
        for x, y in zip(xs, ys))
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="turn size against arc length">
  <rect width="{w}" height="{h}" fill="{PAPER}"/>
  <line x1="{pad}" y1="{h - pad}" x2="{w - pad}" y2="{h - pad}" stroke="{INK}" stroke-width="1.2"/>
  <line x1="{pad}" y1="{pad}" x2="{pad}" y2="{h - pad}" stroke="{INK}" stroke-width="1.2"/>
  <path d="{line(ideal)}" fill="none" stroke="{BLUE}" stroke-width="2" stroke-dasharray="7 5"/>
  <path d="{line(ys)}" fill="none" stroke="{RED}" stroke-width="2"/>
  {marks}
  <text x="{pad}" y="34" font-family="Georgia,serif" font-size="13" fill="{INK}">Fig. D2 · Δθ against s, log–log · measured slope {d['slope']:.3f} (a clothoid is 1)</text>
  <text x="{pad}" y="54" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}">max quantisation error {d['max_err']:.2f}° · ladder gap {d['gap']:.2f}° · {d['ladder_size']} angles to c ≤ {C_MAX}</text>
  <text x="{w / 2:.0f}" y="{h - 20}" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}">log10 s (chords)</text>
  <text x="18" y="{h / 2:.0f}" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}" transform="rotate(-90 18 {h / 2:.0f})">log10 Δθ (radians)</text>
  <g font-family="Georgia,serif" font-size="15">
    <circle cx="300" cy="{h - 12}" r="4.5" fill="{PAPER}" stroke="{RED}" stroke-width="2"/><text x="314" y="{h - 7}" fill="{INK}">quantised</text>
    <line x1="440" y1="{h - 12}" x2="476" y2="{h - 12}" stroke="{BLUE}" stroke-width="2" stroke-dasharray="7 5"/><text x="484" y="{h - 7}" fill="{INK}">Δθ ∝ s</text>
  </g>
</svg>"""


def analysis():
    return build()


def main():
    d = build()
    rows = "".join(
        f"<tr><td>{c['k']}</td><td>{c['ideal']:.2f}°</td>"
        f"<td>{c['row']['a']}-{c['row']['b']}-{c['row']['c']}</td>"
        f"<td>{c['row']['deg']:.2f}°</td>"
        f"<td>{abs(c['row']['deg'] - c['ideal']):.2f}°</td></tr>"
        for c in d["chosen"])

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Discrete clothoid · a turn schedule, quantised</title>
<style>
:root{{--paper:{PAPER};--ink:{INK};--muted:{MUTED};--rule:{RULE}}}
*{{box-sizing:border-box}} body{{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:34px 22px 70px}}
.eyebrow{{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
h1{{font-size:31px;line-height:1.12;margin:0 0 8px}} h2{{font-size:20px;margin:0 0 8px}}
.lede{{max-width:920px;color:var(--muted)}}
.panel{{background:var(--paper);border:1px solid var(--rule);padding:16px 18px;margin:0 0 18px}}
table{{border-collapse:collapse;font:12px/1.5 ui-monospace,Menlo,monospace;margin:10px 0;width:100%}}
th,td{{border:1px solid var(--rule);padding:4px 7px;text-align:right}} th{{color:var(--muted);font-weight:400}}
.small{{font:12px/1.6 ui-monospace,Menlo,monospace;color:var(--muted)}}
code{{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}}
</style></head><body><main>
<p class="eyebrow">curve-lab · the discrete clothoid</p>
<h1>A clothoid built from equal chords and p-triple turns</h1>
<p class="lede">A clothoid has curvature proportional to arc length. With equal chords that is a rule
for the turn schedule: Δθ_k ∝ k. Quantise each turn to the nearest p-triple angle and the polygon is
exact — rational nodes, right-triangle turns — while the schedule still rises linearly. This is what
the spine does when it rounds a turn schedule; here the schedule is a clothoid.</p>

<section class="panel">
<h2>Fig. D1 · the quantised polygon over the ideal clothoid</h2>
{fig_schedule(d)}
<p class="small">The polygon is drawn from exact rational nodes; the scale that clears the denominators
is {d['scale']} ({d['digits']} digits), so the drawing is the rational polygon, not a rounded copy. The
dashed curve is the ideal clothoid with the same curvature law.</p>
</section>

<section class="panel">
<h2>Fig. D2 · the law survives the quantisation</h2>
{fig_law(d)}
<p class="small">Each point is a measured turn; the dashed line is Δθ ∝ s. The fitted exponent is
<b>{d['slope']:.3f}</b> against the ideal 1, and the largest quantisation error is
<b>{d['max_err']:.2f}°</b> — under half the {d['gap']:.2f}° gap of the {d['ladder_size']}-angle ladder
(c ≤ {C_MAX}). Rising schedule: the law holds. The Euclid chain is the falling case — its turns
decrease and its curvature exponent drifts to −4/3 (showcase, Fig. 6c) — which is why it is a curl,
not a clothoid.</p>
</section>

<section class="panel">
<h2>The schedule, step by step</h2>
<table>
<tr><th>k</th><th>ideal Δθ</th><th>triple</th><th>quantised Δθ</th><th>error</th></tr>
{rows}
</table>
<p class="small">Re-derive: <code>python scripts/discrete_clothoid.py</code> ·
test: <code>python -m unittest tests.test_discrete_clothoid</code></p>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "discrete-clothoid.html"
    out.write_text(html, encoding="utf-8")
    print(out)
    return out


if __name__ == "__main__":
    main()
