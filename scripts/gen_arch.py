"""Gen-Arch: the generalized Archimedean spiral, and the radial of a LA curve.

    .venv/bin/python scripts/gen_arch.py
    open workbench/gen-arch.html

Gen-Arch is r = a + b·φ^(1/c). The dial c names the classical spirals:
c = −2 lituus, c = −1 hyperbolic, c = 1 Archimedean, c = 2 Fermat.

The claim worth having here is the one in Salvi (2026): the radial of a
log-aesthetic curve — the curve traced by its centre of curvature — is a
Gen-Arch spiral with c = α − 1, where α is the LCH slope of the LA curve.
The repo's LAC dial is the curvature exponent p, and κ ∝ s^p, while the LA
definition is κ ∝ s^(−1/α), so p = −1/α and c = −1/p − 1. The clothoid
(p = 1) gives c = −2, the lituus; the circle involute (α = 2, p = −1/2)
gives c = 1, the Archimedean.
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER, INK, MUTED, RULE = "#fbf7ec", "#2e2413", "#7b6c4e", "#d8ccae"
BLUE, RED, GOLD, GREEN = "#1f5fa8", "#a23b2a", "#c9a441", "#3f7d4e"


def spiral(c, a=0.0, b=1.0, phi0=0.0, phi1=18.0, n=1200):
    """r = a + b φ^(1/c), sampled; c < 0 needs φ > 0."""
    out = []
    for i in range(n + 1):
        phi = phi0 + (phi1 - phi0) * i / n
        if phi <= 0 and c < 0:
            continue
        r = a + b * (phi ** (1.0 / c) if phi > 0 else 0.0)
        out.append((r * math.cos(phi), r * math.sin(phi)))
    return out


# -- the LA radial identity -------------------------------------------------

def la_radius_ratio(s, alpha, c0=1.0, c1=1.0):
    """r / φ^(1/(α−1)) for the radial of a LA curve; it is constant.

    κ(s) = (c0 s + c1)^(−1/α), θ(s) = α/((α−1)c0)·(c0 s + c1)^((α−1)/α) − π/2,
    φ = θ + π/2, r = 1/κ. With c0 = c1 = 1 the constant is
    ((α−1)/α)^(1/(α−1)).
    """
    u = c0 * s + c1
    phi = alpha / ((alpha - 1) * c0) * u ** ((alpha - 1) / alpha)
    r = u ** (1 / alpha)
    return r / phi ** (1 / (alpha - 1))


def radial_row(alpha, s0=0.2, s1=2.0, n=240):
    s_vals = [s0 + (s1 - s0) * i / n for i in range(n + 1)]
    ratios = [la_radius_ratio(s, alpha) for s in s_vals]
    const = ((alpha - 1) / alpha) ** (1 / (alpha - 1))
    dev = max(abs(x / const - 1) for x in ratios)

    xs = [math.log(alpha / (alpha - 1) * (s + 1) ** ((alpha - 1) / alpha))
          for s in s_vals]
    ys = [math.log((s + 1) ** (1 / alpha)) for s in s_vals]
    n_ = len(xs)
    mx, my = sum(xs) / n_, sum(ys) / n_
    slope = (sum((x - mx) * (y - my) for x, y in zip(xs, ys))
             / sum((x - mx) ** 2 for x in xs))
    return {"alpha": alpha, "c": alpha - 1, "p": -1.0 / alpha,
            "slope": slope, "expect": 1.0 / (alpha - 1), "dev": dev,
            "s": s_vals, "phi": [math.exp(x) for x in xs],
            "r": [math.exp(y) for y in ys]}


def analysis():
    return [radial_row(a) for a in (-1.0, -2.0, 2.0, 3.0)]


def cases():
    """The four classical Gen-Arch spirals, one curve each."""
    return [
        ("c = −2 · lituus", spiral(-2, phi0=0.55, phi1=18.0),
         "r = φ^(−1/2) · the radial of a clothoid (α = −1, p = 1)",
         "Salvi 2026 · Gen-Arch"),
        ("c = −1 · hyperbolic", spiral(-1, phi0=0.55, phi1=18.0),
         "r = 1/φ · the radial of Nielsen's spiral (α = 0)",
         "Salvi 2026 · Gen-Arch"),
        ("c = 1 · Archimedean", spiral(1, phi0=0.0, phi1=18.0),
         "r = φ · the radial of the circle involute (α = 2, p = −1/2)",
         "Salvi 2026 · Gen-Arch"),
        ("c = 2 · Fermat", spiral(2, phi0=0.0, phi1=18.0),
         "r = √φ · the radial of the LA curve α = 3 (p = −1/3)",
         "Salvi 2026 · Gen-Arch"),
    ]


# -- drawing ----------------------------------------------------------------

def clothoid(s0=0.35, s1=2.3, n=500):
    """The unit clothoid κ = s, integrated numerically."""
    pts = []
    x = y = 0.0
    ds = (s1 - s0) / n
    for i in range(n + 1):
        s = s0 + i * ds
        pts.append((x, y))
        th = s * s / 2
        x += math.cos(th) * ds
        y += math.sin(th) * ds
    return pts


def radial_figure(cloth, w=980, h=470):
    """Left: the clothoid with osculating circles. Right: its radial, a lituus."""
    def fit(pts, x0, y0, ww, hh, pad=40):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        xa, xb, ya, yb = min(xs), max(xs), min(ys), max(ys)
        s = min((ww - 2 * pad) / max(1e-9, xb - xa),
                (hh - 2 * pad) / max(1e-9, yb - ya))
        ox = x0 + (ww - (xb - xa) * s) / 2 - xa * s
        oy = y0 + (hh - (yb - ya) * s) / 2 + yb * s
        return lambda p: (ox + p[0] * s, oy - p[1] * s)

    rad = []
    for i in range(240):
        s = 0.45 + (2.2 - 0.45) * i / 239
        th = s * s / 2
        rho = 1.0 / s
        rad.append((rho * math.cos(th + math.pi / 2),
                    rho * math.sin(th + math.pi / 2)))

    cl = list(cloth)
    f1 = fit(cl + [(0, 0)], 0, 0, w // 2, h)
    f2 = fit(rad, w // 2, 0, w // 2, h)

    circ = []
    for i in range(len(cl)):
        s = 0.35 + i * (2.3 - 0.35) / (len(cl) - 1)
        if not any(abs(s - t) < 0.004 for t in (0.8, 1.4, 2.0)):
            continue
        th = s * s / 2
        rho = 1.0 / s
        p = cl[i]
        cx, cy = p[0] - rho * math.sin(th), p[1] + rho * math.cos(th)
        c = f1((cx, cy))
        r = rho * abs(f1((cx + 1, cy))[0] - c[0])
        circ.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{r:.1f}" '
                    f'fill="none" stroke="{GOLD}" stroke-width="1.2" stroke-dasharray="4 4"/>')
        circ.append(f'<line x1="{f1(p)[0]:.1f}" y1="{f1(p)[1]:.1f}" x2="{c[0]:.1f}" '
                    f'y2="{c[1]:.1f}" stroke="{GOLD}" stroke-width="0.9"/>')
        circ.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="3" fill="{RED}"/>')

    dp = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}"
                  for i, (x, y) in enumerate(f1(p) for p in cl))
    dr = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}"
                  for i, (x, y) in enumerate(f2(p) for p in rad))
    o2 = f2((0, 0))
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="clothoid, osculating circles, and its lituus radial">
  <rect width="{w}" height="{h}" fill="{PAPER}"/>
  <line x1="{w // 2}" y1="20" x2="{w // 2}" y2="{h - 20}" stroke="{RULE}" stroke-width="1"/>
  <path d="{dp}" fill="none" stroke="{INK}" stroke-width="2.2"/>
  {''.join(circ)}
  <circle cx="{o2[0]:.1f}" cy="{o2[1]:.1f}" r="3" fill="{MUTED}"/>
  <path d="{dr}" fill="none" stroke="{BLUE}" stroke-width="2"/>
  <text x="16" y="24" font-family="Georgia,serif" font-size="13" fill="{INK}">Fig. GA0 · left: the clothoid κ = s, with osculating circles · right: the same radii as a radial, at the origin</text>
  <text x="16" y="44" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="{MUTED}">each gold radius becomes a polar radius r of the blue curve; the radial of the clothoid is the lituus (c = −2)</text>
  <g font-family="Georgia,serif" font-size="15">
    <line x1="16" y1="{h - 16}" x2="52" y2="{h - 16}" stroke="{INK}" stroke-width="3"/><text x="60" y="{h - 11}" fill="{INK}">clothoid</text>
    <circle cx="176" cy="{h - 16}" r="3" fill="{RED}"/><text x="188" y="{h - 11}" fill="{INK}">centre of curvature</text>
    <circle cx="380" cy="{h - 16}" r="5" fill="{PAPER}" stroke="{GOLD}" stroke-width="2"/><text x="394" y="{h - 11}" fill="{INK}">osculating circle</text>
    <line x1="560" y1="{h - 16}" x2="596" y2="{h - 16}" stroke="{BLUE}" stroke-width="3"/><text x="604" y="{h - 11}" fill="{INK}">the radial (a lituus)</text>
  </g>
</svg>"""


def mini_svg(pts, title, note, w=460, h=340):
    pad = 34
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    span = max(x1 - x0, y1 - y0, 1e-9)
    s = (min(w, h) - 2 * pad) / span
    ox = (w - (x1 - x0) * s) / 2 - x0 * s
    oy = (h - (y1 - y0) * s) / 2 + y1 * s

    def f(p):
        return (ox + p[0] * s, oy - p[1] * s)

    d = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}"
                 for i, (x, y) in enumerate(f(p) for p in pts))
    ax, ay = f((0, 0))
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{title}">
  <rect width="{w}" height="{h}" fill="{PAPER}"/>
  <line x1="{pad}" y1="{ay:.1f}" x2="{w - pad}" y2="{ay:.1f}" stroke="{RULE}" stroke-width="1"/>
  <line x1="{ax:.1f}" y1="{pad}" x2="{ax:.1f}" y2="{h - pad}" stroke="{RULE}" stroke-width="1"/>
  <path d="{d}" fill="none" stroke="{INK}" stroke-width="2"/>
  <text x="10" y="20" font-family="Georgia,serif" font-size="12" fill="{INK}">{title}</text>
  <text x="10" y="{h - 10}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{MUTED}">{note}</text>
  <text x="{w - 26}" y="{h - 10}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{MUTED}">x →</text>
  <text x="10" y="36" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{MUTED}">y ↑</text>
</svg>"""


def law_svg(rows):
    w, h, pad = 900, 420, 74
    xs = [math.log(r["phi"][i]) for r in rows for i in range(0, len(r["phi"]), 12)]
    ys = [math.log(r["r"][i]) for r in rows for i in range(0, len(r["r"]), 12)]
    x0, x1 = min(xs) - 0.2, max(xs) + 0.2
    y0, y1 = min(ys) - 0.2, max(ys) + 0.2

    def f(p):
        return (pad + (p[0] - x0) / (x1 - x0) * (w - 2 * pad),
                h - pad - (p[1] - y0) / (y1 - y0) * (h - 2 * pad))

    colours = [RED, BLUE, GOLD, GREEN]
    paths = []
    for row, colour in zip(rows, colours):
        sel = range(0, len(row["phi"]), 12)
        d = " ".join(("M" if i == 0 else "L")
                     + f"{x:.1f},{y:.1f}"
                     for i, (x, y) in enumerate(f((math.log(row["phi"][j]),
                                                   math.log(row["r"][j]))) for j in sel))
        paths.append(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="2"/>')

    legend = "".join(
        f'<line x1="{20 + i * 180}" y1="{h - 14}" x2="{56 + i * 180}" y2="{h - 14}" '
        f'stroke="{c}" stroke-width="3"/><text x="{64 + i * 180}" y="{h - 9}" '
        f'font-family="Georgia,serif" font-size="15" fill="{INK}">α = {row["alpha"]:g}</text>'
        for i, (row, c) in enumerate(zip(rows, colours)))
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="LA radials are Gen-Arch spirals">
  <rect width="{w}" height="{h}" fill="{PAPER}"/>
  <line x1="{pad}" y1="{h - pad}" x2="{w - pad}" y2="{h - pad}" stroke="{INK}" stroke-width="1.2"/>
  <line x1="{pad}" y1="{pad}" x2="{pad}" y2="{h - pad}" stroke="{INK}" stroke-width="1.2"/>
  {''.join(paths)}
  <text x="{pad}" y="34" font-family="Georgia,serif" font-size="13" fill="{INK}">Fig. GA2 · the radial r against φ, log–log · a straight line of slope 1/(α−1)</text>
  <text x="{pad}" y="54" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}">fitted slopes: {" · ".join(f"{r['alpha']:g}: {r['slope']:.3f}" for r in rows)}</text>
  <text x="{w / 2:.0f}" y="{h - 34}" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}">log10 φ</text>
  <text x="18" y="{h / 2:.0f}" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}" transform="rotate(-90 18 {h / 2:.0f})">log10 r</text>
  {legend}
</svg>"""


def build():
    rows = analysis()
    table = "".join(
        f"<tr><td>{r['alpha']:g}</td><td>{r['p']:.4g}</td><td>{r['c']:g}</td>"
        f"<td>{r['expect']:.4f}</td><td>{r['slope']:.6f}</td><td>{r['dev']:.1e}</td></tr>"
        for r in rows)
    cards = "".join(
        f'<div>{mini_svg(pts, title, note)}</div>' for title, pts, note, _ in cases())

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gen-Arch · the generalized Archimedean spiral</title>
<style>
:root{{--paper:{PAPER};--ink:{INK};--muted:{MUTED};--rule:{RULE}}}
*{{box-sizing:border-box}} body{{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:34px 22px 70px}}
.eyebrow{{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
h1{{font-size:31px;line-height:1.12;margin:0 0 8px}} h2{{font-size:20px;margin:0 0 8px}}
.lede{{max-width:920px;color:var(--muted)}}
.panel{{background:var(--paper);border:1px solid var(--rule);padding:16px 18px;margin:0 0 18px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
@media(max-width:760px){{.grid{{grid-template-columns:1fr}}}}
table{{border-collapse:collapse;font:12px/1.5 ui-monospace,Menlo,monospace;margin:10px 0;width:100%}}
th,td{{border:1px solid var(--rule);padding:5px 8px;text-align:right}} th{{color:var(--muted);font-weight:400}}
.small{{font:12px/1.6 ui-monospace,Menlo,monospace;color:var(--muted)}}
code{{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}}
</style></head><body><main>
<p class="eyebrow">curve-lab · Gen-Arch</p>
<h1>The generalized Archimedean spiral, and the radial of a LA curve</h1>
<p class="lede">Gen-Arch is <code>r = a + b·φ^(1/c)</code>. The dial <code>c</code> names the classical
spirals: −2 lituus, −1 hyperbolic, 1 Archimedean, 2 Fermat. Its exact use is as the radial of a
log-aesthetic curve: the centre of curvature of an LA curve traces a Gen-Arch spiral with
<code>c = α − 1</code> (Salvi 2026). Here that identity is measured, and the repo's own LAC dial is
translated into it.</p>

<section class="panel">
<h2>Fig. GA0 · what “radial” means</h2>
{radial_figure(clothoid())}
<p class="small">At each point of the clothoid, the osculating circle has radius ρ = 1/κ and a centre.
The <em>radial</em> is those centres written as polar points about the origin: angle = the normal
angle, radius = ρ. The left panel shows three; the right panel is all of them — the curve the centres
trace is the lituus. That is the whole object: not an offset, not an evolute drawn in place, but the
radius of curvature used as a polar distance.</p>
</section>

<section class="panel">
<h2>Fig. GA1 · the four classical cases, a = 0, b = 1</h2>
<div class="grid">{cards}</div>
<p class="small">φ runs 0.55–18 for the two negative-c spirals (they need φ &gt; 0) and 0–18 for the
positive ones. The lituus winds in from r = 1.35, the hyperbolic from 1.8; the Archimedean and Fermat
wind out. Curvature is monotone where (t²+1)c² ≥ |c|√(c²+3).</p>
</section>

<section class="panel">
<h2>Fig. GA2 · the radial identity</h2>
{law_svg(rows)}
<p class="small">For each LA slope α, the radial is r = const·φ^(1/(α−1)); the log–log line is
straight and the fitted exponent matches 1/(α−1) to six places. The constant is
((α−1)/α)^(1/(α−1)); the largest relative deviation over 241 samples is in the table.</p>
<table>
<tr><th>α (LCH slope)</th><th>repo p = −1/α</th><th>c = α − 1</th><th>1/(α−1)</th><th>fitted</th><th>max dev</th></tr>
{table}
</table>
</section>

<section class="panel">
<h2>What the dials mean, and what this corrects</h2>
<p>Three different numbers are in play, and they are easy to confuse. <b>α</b> is the slope of the
logarithmic curvature histogram — the paper's LA parameter, with κ ∝ s<sup>−1/α</sup>. <b>p</b> is
this repo's LAC dial, the curvature exponent, with κ ∝ s<sup>p</sup>; therefore <b>p = −1/α</b>.
<b>c</b> is the Gen-Arch dial, and for a radial <b>c = α − 1 = −1/p − 1</b>. So the showcase card
labelled <code>p = 3</code> is α = −1/3, not α = 3; and α = 3 would be p = −1/3, whose radial is the
Fermat spiral. The label on the stem cuts now says <code>p = 3</code>, which is the repo's own dial
and cannot be mistaken for α or for the p-triple's <code>a</code>.</p>
<p>Special cases: clothoid (α = −1, p = 1) → c = −2, the lituus; Nielsen's spiral (α = 0) → c = −1,
the hyperbolic spiral; circle involute (α = 2, p = −1/2) → c = 1, the Archimedean. The logarithmic
spiral (α = 1) is the exception: its radial is a logarithmic spiral, and c = 0 is the limit of
Gen-Arch, not a member.</p>
<p>The practical consequence is the paper's Section 5: a Gen-Arch segment with c = α − 1 is a cheap
approximant of the LA curve, matching curvature at the start and approaching the same LCH slope as t
grows. The limitation is at small t, where the fit is short; at large t the two are hard to tell
apart.</p>
<p class="small">Gen-Arch is transcendental, so it is declared outside <code>NAMED</code>
(<code>tests/test_curve_census.py</code>) and carries no lattice-exactness claim.
Re-derive: <code>python scripts/gen_arch.py</code> ·
test: <code>python -m unittest tests.test_gen_arch</code></p>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "gen-arch.html"
    out.write_text(html, encoding="utf-8")
    print(out)
    return out


if __name__ == "__main__":
    build()
