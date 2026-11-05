"""The log spiral's width: what is exact, and what only looks exact.

    .venv/bin/python scripts/log_spiral.py
    open workbench/log-spiral.html

The claim worth testing: "the equiangular spiral has easy offsets." It is half
true. A constant-width parallel is NOT a log spiral; the tangent-to-radius angle
drifts with d/r. What is exact is scaling: two log spirals with the same pitch
differ by a width proportional to the radius, which is a self-similar taper.
The evolute is exact too (a log spiral about the same origin).
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INK, GOLD, BLUE, RED = "#2e2413", "#c9a441", "#1f5fa8", "#a23b2a"
MUTED, RULE, PAPER = "#7b6c4e", "#d8ccae", "#fbf7ec"

B = 0.2


def r(th: float, a: float = 10.0) -> float:
    return a * math.exp(B * th)


def point(th: float, a: float = 10.0):
    rr = r(th, a)
    return rr * math.cos(th), rr * math.sin(th)


def unit_tangent(th: float, a: float = 10.0):
    rr = r(th, a)
    dr = B * rr
    v = (dr * math.cos(th) - rr * math.sin(th), dr * math.sin(th) + rr * math.cos(th))
    L = math.hypot(*v)
    return v[0] / L, v[1] / L


def unit_normal(th: float, a: float = 10.0):
    tx, ty = unit_tangent(th, a)
    return -ty, tx


def parallel(th0: float, th1: float, d: float, a: float = 10.0, n: int = 600):
    out = []
    for i in range(n):
        th = th0 + (th1 - th0) * i / (n - 1)
        px, py = point(th, a)
        nx, ny = unit_normal(th, a)
        out.append((px + d * nx, py + d * ny))
    return out


def tangent_angle_spread(pts) -> float:
    seq = []
    for i in range(1, len(pts) - 1):
        dx = pts[i + 1][0] - pts[i - 1][0]
        dy = pts[i + 1][1] - pts[i - 1][1]
        ang = math.atan2(dy, dx)
        rad = math.atan2(pts[i][1], pts[i][0])
        v = (ang - rad) % math.pi
        if seq:
            while v - seq[-1] > math.pi / 2:
                v -= math.pi
            while v - seq[-1] < -math.pi / 2:
                v += math.pi
        seq.append(v)
    return math.degrees(max(seq) - min(seq))


def evolute(th0: float, th1: float, a: float = 10.0, n: int = 600):
    out = []
    for i in range(n):
        th = th0 + (th1 - th0) * i / (n - 1)
        px, py = point(th, a)
        nx, ny = unit_normal(th, a)
        rho = r(th, a) * math.sqrt(1 + B * B)
        out.append((px + rho * nx, py + rho * ny))
    return out


class Frame:
    """Model (y up) to screen (y down), with the flip stated at output."""

    def __init__(self, pts, w=980, h=720, pad=56):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        self.x0, self.x1 = min(xs), max(xs)
        self.y0, self.y1 = min(ys), max(ys)
        self.w, self.h, self.pad = w, h, pad
        self.s = min((w - 2 * pad) / max(1e-9, self.x1 - self.x0),
                     (h - 2 * pad) / max(1e-9, self.y1 - self.y0))

    def __call__(self, p):
        return (self.pad + (p[0] - self.x0) * self.s,
                self.h - self.pad - (p[1] - self.y0) * self.s)


def path(pts, f: Frame) -> str:
    return " ".join(("M" if i == 0 else "L") + f"{f(p)[0]:.1f},{f(p)[1]:.1f}"
                    for i, p in enumerate(pts))


def run() -> None:
    th0, th1 = 0.0, 4 * math.pi
    spiral = [point(th0 + (th1 - th0) * i / 899) for i in range(900)]
    d_const = 8.0
    par = parallel(th0, th1, d_const)
    k = 1.35
    scaled = [(k * x, k * y) for x, y in spiral]

    # measurements
    ratios = (0.02, 0.05, 0.10, 0.20)
    drift = []
    for q in ratios:
        dd = q * r(0.0)
        drift.append((q, tangent_angle_spread(parallel(th0, th1, dd))))
    evo = evolute(th0, th1)
    evo_spread = tangent_angle_spread(evo)

    f = Frame(spiral + par + scaled, 980, 760)
    px_scaled = [f(p) for p in scaled]
    px_par = [f(p) for p in par]
    px_spiral = [f(p) for p in spiral]

    # width bars at two stations, measured along the normal
    def bar(th):
        p = point(th)
        n = unit_normal(th)
        q = (p[0] + d_const * n[0], p[1] + d_const * n[1])
        a_, b_ = f(p), f(q)
        mid = ((a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2)
        return a_, b_, mid

    bars = [bar(0.6), bar(3.0), bar(6.5)]

    # width of the scaled copy along the normal (exact, proportional to r)
    def tapered_width(th):
        # solve for the intersection of the normal ray with the scaled spiral
        p = point(th)
        n = unit_normal(th)
        lo, hi = 0.0, 30.0 * r(th)
        for _ in range(80):
            mid = (lo + hi) / 2
            q = (p[0] + mid * n[0], p[1] + mid * n[1])
            rr = math.hypot(*q)
            # the boundary spiral has radius k*r at the same polar angle
            ang = math.atan2(q[1], q[0])
            if rr > k * r(ang):
                hi = mid
            else:
                lo = mid
        return lo

    widths = [(th, tapered_width(th)) for th in (0.6, 1.8, 3.0, 4.5, 6.0)]

    # figure 2: drift against d/r
    gx0, gy0, gw, gh = 90, 100, 760, 300
    qmax = 0.22
    smax = max(v for _, v in drift) * 1.15

    def gpt(q, v):
        return (gx0 + q / qmax * gw, gy0 + gh - v / smax * gh)

    pts2 = [gpt(q, v) for q, v in drift]
    path2 = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}" for i, (x, y) in enumerate(pts2))

    rows = "".join(
        f"<tr><td>{q:.2f}</td><td>{v:.3f}°</td></tr>" for q, v in drift)
    wrows = "".join(
        f"<tr><td>{th:.1f}</td><td>{w:.3f}</td><td>{w / r(th):.4f}</td></tr>" for th, w in widths)

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Log spiral · what is exact about its width</title>
<style>
:root{{--paper:{PAPER};--ink:{INK};--muted:{MUTED};--rule:{RULE}}}
*{{box-sizing:border-box}} body{{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:34px 22px 70px}}
.eyebrow{{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
h1{{font-size:31px;line-height:1.12;margin:0 0 8px}} h2{{font-size:20px;margin:0 0 8px}}
.lede{{max-width:900px;color:var(--muted)}} .panel{{background:var(--paper);border:1px solid var(--rule);padding:16px 18px;margin:0 0 18px}}
table{{border-collapse:collapse;font:12px/1.5 ui-monospace,Menlo,monospace;margin:10px 0;width:100%}}
th,td{{border:1px solid var(--rule);padding:5px 8px;text-align:right}} th{{color:var(--muted);font-weight:400}}
.small{{font:12px/1.55 ui-monospace,Menlo,monospace;color:var(--muted)}}
code{{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}}
</style></head><body><main>
<p class="eyebrow">curve-lab · width without offsets</p>
<h1>The log spiral: an easy offset that is not an offset</h1>
<p class="lede">The equiangular spiral <code>r = a·e^(bθ)</code> is famous for being self-similar. It is often said that its offset curves are log spirals too. Half of that is true, and the half that is false is the half the stem needs.</p>

<section class="panel">
<h2>Fig. L1 · one spiral, a constant width that is not a spiral, and a scaling that is</h2>
<svg viewBox="0 0 980 760" width="100%" role="img" aria-label="log spiral with parallel and scaled copy">
  <rect width="980" height="760" fill="{PAPER}"/>
  <path d="{path(spiral, f)}" fill="none" stroke="{INK}" stroke-width="2.4"/>
  <path d="{path(par, f)}" fill="none" stroke="{BLUE}" stroke-width="1.8" stroke-dasharray="7 5"/>
  <path d="{path(scaled, f)}" fill="none" stroke="{GOLD}" stroke-width="2" />
  {"".join(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{RED}" stroke-width="1.4"/><circle cx="{b[0]:.1f}" cy="{b[1]:.1f}" r="3" fill="{RED}"/>' for a, b, m in bars)}
  <text x="16" y="24" font-family="Georgia,serif" font-size="13" fill="{INK}">Fig. L1 · r = 10·e^(0.2θ), θ = 0…4π · +y up, flipped to screen y down</text>
  <text x="16" y="44" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}">red bars: the constant offset d = 8 · x axis →, y axis ↑</text>
  <g font-family="Georgia,serif" font-size="15">
    <line x1="16" y1="730" x2="52" y2="730" stroke="{INK}" stroke-width="3"/><text x="60" y="735" fill="{INK}">spiral</text>
    <line x1="150" y1="730" x2="186" y2="730" stroke="{BLUE}" stroke-width="2" stroke-dasharray="7 5"/><text x="194" y="735" fill="{INK}">constant offset d = 8</text>
    <line x1="380" y1="730" x2="416" y2="730" stroke="{GOLD}" stroke-width="3"/><text x="424" y="735" fill="{INK}">scaled copy ×1.35 (exact log spiral)</text>
  </g>
</svg>
<p class="small">The blue curve is a true constant-width parallel; the gold is the same spiral scaled. Only the gold one is a log spiral, and its width grows with the radius — the red bars are equal by construction, the gold gap is not.</p>
</section>

<section class="panel">
<h2>Fig. L2 · the drift, measured</h2>
<p>A log spiral has one constant: the angle between its tangent and its radius. Fit that angle on the constant-width parallel and it is <em>not</em> constant. The spread grows with <code>d/r</code>:</p>
<svg viewBox="0 0 880 420" width="100%" role="img" aria-label="drift against d over r">
  <rect width="880" height="420" fill="{PAPER}"/>
  <line x1="{gx0}" y1="{gy0 + gh}" x2="{gx0 + gw}" y2="{gy0 + gh}" stroke="{INK}" stroke-width="1.2"/>
  <line x1="{gx0}" y1="{gy0}" x2="{gx0}" y2="{gy0 + gh}" stroke="{INK}" stroke-width="1.2"/>
  <path d="{path2}" fill="none" stroke="{RED}" stroke-width="2"/>
  {"".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{PAPER}" stroke="{RED}" stroke-width="2"/><text x="{x-6:.1f}" y="{y-10:.1f}" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="{INK}">{v:.2f}°</text>' for (x, y), (q, v) in zip(pts2, drift))}
  <text x="{gx0}" y="84" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}">spread of the tangent-to-radius angle (degrees)</text>
  <text x="{gx0 + gw - 90}" y="{gy0 + gh + 26}" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}">d / r (at the start)</text>
  <g font-family="Georgia,serif" font-size="15">
    <line x1="{gx0}" y1="396" x2="{gx0 + 26}" y2="396" stroke="{RED}" stroke-width="2.4"/>
    <text x="{gx0 + 34}" y="401" fill="{INK}">measured spread</text>
  </g>
</svg>
<table><tr><th>d / r</th><th>tangent-angle spread</th></tr>{rows}</table>
<p class="small">Exact zero would mean the parallel is a log spiral. It is not: at <code>d/r = 0.02</code> the spread is 0.22°, and it rises in proportion to <code>d/r</code>.</p>
</section>

<section class="panel">
<h2>What is exact</h2>
<p><strong>Scaling.</strong> Multiply the spiral by <code>k</code> and you get another log spiral with the same pitch. The width between them is measured along the normal and is proportional to the radius — a self-similar taper, exactly what a stem wants and exactly what a constant width is not.</p>
<table><tr><th>θ</th><th>width to the ×1.35 copy</th><th>width / r</th></tr>{wrows}</table>
<p><strong>The evolute.</strong> The centres of curvature trace another log spiral about the same origin; measured tangent-angle spread over four turns: <b>{evo_spread:.4f}°</b> — exact to sampling.</p>
<p class="small">So the honest formulation: the log spiral's easy relation is <em>similarity</em>, not offset. Width that grows with the radius is exact; width that stays constant is not.</p>
</section>

<section class="panel">
<h2>What this means for a stem</h2>
<p>A log-spiral stem can carry an exact tapered width — two spirals with the same <code>b</code> and different <code>a</code> — with the width law <code>w ∝ r</code>. It cannot carry an exact constant width, and it is not on the integer lattice at all. If you need both a constant width and exactness, this curve is the wrong source; if you need a taper, it is the cleanest one in the catalogue.</p>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "log-spiral.html"
    out.write_text(html, encoding="utf-8")
    print(out)
    print(f"drift at d/r=0.02..0.20: {[round(v,3) for _, v in drift]}")
    print(f"evolute spread: {evo_spread:.6f} deg")
    print(f"tapered width / r: {[round(w/r(th),4) for th, w in widths]}")


if __name__ == "__main__":
    run()
