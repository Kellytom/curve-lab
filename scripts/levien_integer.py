"""Levien integer sandbox.

    .venv/bin/python scripts/levien_integer.py
    open workbench/levien-integer.html

The simple conditions: a parabola y = x²/k on x∈[0,2], its half/quarter
variants, and a cubic control case.  Each card draws the source, the exact
normal rail, Levien's fitted cubic rail, the integer lattice, and the
near-integer hit counts.  Choose a family and offset distance with the two
selects.

The exact integer points on the source are known.  A parabola's exact parallel
is a higher-degree rational curve (not a cubic); a general cubic's exact
parallel is degree 10.  Levien's rail is fitted and real-valued, so integer rail
hits are a Diophantine question rather than a consequence of the fit; the page
is for finding the exceptions.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab.parallel_bezier import fit_chain  # noqa: E402

INK = "#2e2413"
BLUE = "#1f5fa8"
RED = "#b23a2b"
GOLD = "#c9a441"
MUTED = "#7b6c4e"
PAPER = "#fffdf7"
GRID = "#e4dcc6"
DOT = "#8c6a21"

N = 420
D_VALUES = (0.25, 0.5, 1.0, 1.5, 2.0)


def cubic_at(span, t):
    u = 1 - t
    (x0, y0), (x1, y1) = span["p0"], span["c1"]
    (x2, y2), (x3, y3) = span["c2"], span["p3"]
    return (u * u * u * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t * t * t * x3,
            u * u * u * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t * t * t * y3)


def cubic_tangent(span, t):
    u = 1 - t
    (x0, y0), (x1, y1) = span["p0"], span["c1"]
    (x2, y2), (x3, y3) = span["c2"], span["p3"]
    dx = 3 * u * u * (x1 - x0) + 6 * u * t * (x2 - x1) + 3 * t * t * (x3 - x2)
    dy = 3 * u * u * (y1 - y0) + 6 * u * t * (y2 - y1) + 3 * t * t * (y3 - y2)
    l = math.hypot(dx, dy) or 1e-12
    return dx / l, dy / l


def offset_point(span, t, d):
    x, y = cubic_at(span, t)
    tx, ty = cubic_tangent(span, t)
    return x - d * ty, y + d * tx


def rail_points(span, d, n=N):
    return [offset_point(span, i / n, d) for i in range(n + 1)]


def fit_points(fit, per=18):
    out = []
    for sp in fit["spans"]:
        for i in range(per):
            out.append(cubic_at(sp, i / per))
    out.append(fit["spans"][-1]["p3"])
    return out


def integer_hits(points, tol=0.01):
    out = {}
    for x, y in points:
        ix, iy = round(x), round(y)
        if abs(x - ix) <= tol and abs(y - iy) <= tol:
            out[(ix, iy)] = min(out.get((ix, iy), 9.0),
                               math.hypot(x - ix, y - iy))
    return out


def cubic_from_quadratic(p0, p1, p2):
    """Degree-elevate a quadratic Bézier exactly."""
    return {
        "p0": p0,
        "c1": ((p0[0] + 2 * p1[0]) / 3.0, (p0[1] + 2 * p1[1]) / 3.0),
        "c2": ((2 * p1[0] + p2[0]) / 3.0, (2 * p1[1] + p2[1]) / 3.0),
        "p3": p2,
    }


def families():
    out = {}
    for key, label, k in (("parabola", "parabola · y = x²", 1.0),
                          ("half", "half parabola · y = x²/2", 2.0),
                          ("quarter", "quarter parabola · y = x²/4", 4.0)):
        source = []
        for x in (0, 1, 2):
            y = x * x / k
            if abs(y - round(y)) < 1e-12:
                source.append((x, y))
        out[key] = {
            "label": label,
            "span": cubic_from_quadratic((0, 0), (1, 0), (2, 4 / k)),
            "source": source,
        }
    # y = x^2 / 64 on [0, 24].  Degree elevation gives integer handles:
    # (8, 0), (16, 3), and the integer points (0,0), (8,1), (16,4), (24,9).
    out["sixtyfourth"] = {
        "label": "sixty-fourth · y = x²/64 · x∈[0,24]",
        "span": {"p0": (0, 0), "c1": (8, 0), "c2": (16, 3), "p3": (24, 9)},
        "source": [(0, 0), (8, 1), (16, 4), (24, 9)],
    }
    # A non-parabolic cubic with integer controls, for comparison.
    out["cubic"] = {
        "label": "cubic control · integer points",
        "span": {"p0": (0, 0), "c1": (1, 0), "c2": (2, 4), "p3": (3, 9)},
        "source": [(0, 0), (3, 9)],
    }
    return out


def success_cases():
    """Curves where the degree-elevated cubic handles are all integers."""
    return [
        {
            "label": "y = x² · [0,3]",
            "span": {"p0": (0, 0), "c1": (1, 0), "c2": (2, 3), "p3": (3, 9)},
            "points": [(x, x * x) for x in range(4)],
            "caption": "handles (1,0), (2,3) · 4 integer points",
        },
        {
            "label": "y = x²/24 · [0,12]",
            "span": {"p0": (0, 0), "c1": (4, 0), "c2": (8, 2), "p3": (12, 6)},
            "points": [(12 * m, 6 * m * m) for m in range(2)],
            "caption": "handles (4,0), (8,2) · 2 integer points",
        },
        {
            "label": "y = x²/64 · [0,24]",
            "span": {"p0": (0, 0), "c1": (8, 0), "c2": (16, 3), "p3": (24, 9)},
            "points": [(8 * m, m * m) for m in range(4)],
            "caption": "handles (8,0), (16,3) · 4 integer points",
        },
        {
            "label": "y = x²/64 · [0,48]",
            "span": {"p0": (0, 0), "c1": (16, 0), "c2": (32, 12), "p3": (48, 36)},
            "points": [(8 * m, m * m) for m in range(7)],
            "caption": "handles (16,0), (32,12) · 7 integer points",
        },
    ]


def success_figure(case, w=330, h=220):
    span = case["span"]
    source = [cubic_at(span, i / 240) for i in range(241)]
    controls = [span["p0"], span["c1"], span["c2"], span["p3"]]
    pts = source + controls + case["points"]
    x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts)
    x1, y1 = max(p[0] for p in pts), max(p[1] for p in pts)
    dx, dy = (x1 - x0) or 1, (y1 - y0) or 1
    pad = 0.08
    x0, x1 = x0 - pad * dx, x1 + pad * dx
    y0, y1 = y0 - pad * dy, y1 + pad * dy
    k = min((w - 18) / (x1 - x0), (h - 18) / (y1 - y0))
    ox, oy = (w - (x1 - x0) * k) / 2, (h - (y1 - y0) * k) / 2

    def put(p):
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k)

    body = []
    for gx in range(math.floor(x0), math.ceil(x1) + 1):
        a, b = put((gx, y0)), put((gx, y1))
        body.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GRID}" stroke-width="0.6"/>')
    for gy in range(math.floor(y0), math.ceil(y1) + 1):
        a, b = put((x0, gy)), put((x1, gy))
        body.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GRID}" stroke-width="0.6"/>')
    # control polygon
    poly = " ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in controls)
    body.append(f'<polyline points="{poly}" fill="none" stroke="{MUTED}" stroke-width="1" stroke-dasharray="4 4"/>')
    # source
    d_attr = " ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in source)
    body.append(f'<path d="M {d_attr}" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>')
    # integer handles
    for i, p in enumerate(controls[1:3], start=1):
        q = put(p)
        body.append(f'<rect x="{q[0]-3.4:.1f}" y="{q[1]-3.4:.1f}" width="6.8" height="6.8" fill="{GOLD}" stroke="{INK}" stroke-width="0.8"/>')
        body.append(f'<text x="{q[0]+6:.1f}" y="{q[1]-5:.1f}" font-family="ui-monospace,Menlo,monospace" font-size="9" fill="{MUTED}">P{i}</text>')
    # integer source points
    for p in case["points"]:
        q = put(p)
        body.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="3.6" fill="{DOT}" stroke="{PAPER}" stroke-width="1"/>')
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{w}" height="{h}" fill="{PAPER}" stroke="{GRID}"/>'
            + "".join(body) + "</svg>")


def figure(fam, d, w=420, h=260):
    span = fam["span"]
    source = [cubic_at(span, i / N) for i in range(N + 1)]
    plus = rail_points(span, d)
    minus = rail_points(span, -d)
    fp = fit_chain([span], d, tol=0.006)
    fm = fit_chain([span], -d, tol=0.006)
    fp_points = fit_points(fp)
    fm_points = fit_points(fm)
    curves = [
        (source, INK, 2.0, None),
        (plus, BLUE, 1.0, None), (minus, RED, 1.0, None),
        (fp_points, GOLD, 1.1, "5 4"), (fm_points, GOLD, 1.1, "5 4"),
    ]
    pts = [p for c in curves for p in c[0]]
    x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts)
    x1, y1 = max(p[0] for p in pts), max(p[1] for p in pts)
    dx, dy = (x1 - x0) or 1, (y1 - y0) or 1
    pad = 0.1
    x0, x1 = x0 - pad * dx, x1 + pad * dx
    y0, y1 = y0 - pad * dy, y1 + pad * dy
    k = min((w - 18) / (x1 - x0), (h - 18) / (y1 - y0))
    ox, oy = (w - (x1 - x0) * k) / 2, (h - (y1 - y0) * k) / 2

    def put(p):
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k)

    body = []
    for gx in range(math.floor(x0), math.ceil(x1) + 1):
        a, b = put((gx, y0)), put((gx, y1))
        body.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GRID}" stroke-width="0.6"/>')
    for gy in range(math.floor(y0), math.ceil(y1) + 1):
        a, b = put((x0, gy)), put((x1, gy))
        body.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GRID}" stroke-width="0.6"/>')
    for pts2, colour, width, dash in curves:
        d_attr = " ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in pts2)
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        body.append(f'<path d="M {d_attr}" fill="none" stroke="{colour}" stroke-width="{width}" stroke-linejoin="round"{dash_attr}/>')
    for x, y in fam["source"]:
        q = put((x, y))
        body.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="3.2" fill="{DOT}"/>')
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{w}" height="{h}" fill="{PAPER}" stroke="{GRID}"/>'
            + "".join(body) + "</svg>"), fp, fm, source, plus, minus, fp_points, fm_points


def main():
    fams = families()
    cards = []
    for fam_key, fam in fams.items():
        for d in D_VALUES:
            svg, fp, fm, source, plus, minus, fpp, fmp = figure(fam, d)
            src_hits = integer_hits(source, 1e-9)
            exact_hits = integer_hits(plus + minus)
            fit_hits = integer_hits(fpp + fmp)
            cards.append(dict(fam=fam_key, d=d, svg=svg, span=fam["span"],
                              source_hits=len(src_hits), exact_hits=len(exact_hits),
                              fit_hits=len(fit_hits),
                              fit_err=max(fp["error_max"], fm["error_max"])))
    cards_html = "".join(f'''<section class="card" data-family="{c['fam']}" data-d="{c['d']}">
<div class="art">{c['svg']}</div>
<h3>{fams[c['fam']]['label']} · d = {c['d']}</h3>
<p class="note">source integer points {c['source_hits']} · exact rail near-integer {c['exact_hits']} · Levien fit near-integer {c['fit_hits']} · fit error {c['fit_err']:.4f}</p>
</section>''' for c in cards)
    gallery_cases = success_cases()
    gallery_html = "".join(
        f'<figure class="success"><div class="success-art">{success_figure(c)}</div>'
        f'<figcaption><strong>{c["label"]}</strong><br><span>{c["caption"]}</span></figcaption></figure>'
        for c in gallery_cases)
    opts_fam = "".join(f'<option value="{k}">{v["label"]}</option>' for k, v in fams.items())
    opts_d = "".join(f'<option value="{d}">{d}</option>' for d in D_VALUES)
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Levien integer sandbox</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1080px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 18px}}
.controls{{display:flex;gap:22px;flex-wrap:wrap;align-items:end;background:{PAPER};
border:1px solid #d8ccae;padding:14px 18px;margin:0 0 16px}}
label{{font:12px ui-monospace,Menlo,monospace;color:{MUTED};display:flex;gap:8px;align-items:center}}
select{{font:13px ui-monospace,Menlo,monospace}}
.art{{background:{PAPER};border:1px solid #d8ccae;padding:8px;margin:0 0 8px}}
svg{{display:block;width:100%;height:auto}}
.card{{background:{PAPER};border:1px solid #d8ccae;padding:10px}}
.card[hidden]{{display:none}}
h3{{font:600 13px/1.35 Georgia,serif;margin:0 0 3px}}
.note{{font:10px/1.4 ui-monospace,Menlo,monospace;color:{MUTED};margin:0}}
.panel{{background:{PAPER};border:1px solid #d8ccae;padding:16px 18px;margin:0 0 18px}}
.panel.quote p{{margin:0 0 10px}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px;margin:0 0 20px}}
.success{{margin:0;background:{PAPER};border:1px solid #d8ccae;padding:8px}}
.success-art{{margin:0 0 7px}}
.success figcaption{{font:10px/1.45 ui-monospace,Menlo,monospace;color:{MUTED}}}
.success figcaption strong{{font:600 12px/1.35 Georgia,serif;color:{INK}}}
.formula{{font:12px/1.75 ui-monospace,Menlo,monospace;background:#f8f3e6;
border-left:3px solid #c9a441;padding:10px 12px;margin:10px 0 12px;overflow-x:auto}}
table{{border-collapse:collapse;font:12px ui-monospace,Menlo,monospace;margin:8px 0 12px}}
th,td{{border:1px solid #d8ccae;padding:4px 9px;text-align:left}}
.cite{{font:10px/1.5 ui-monospace,Menlo,monospace;color:{MUTED};margin:12px 0 0}}
code{{font:12px ui-monospace,Menlo,monospace}}
</style></head><body><main>
<h1>Levien integer sandbox</h1>
<p class="lead">Simple conditions first: a parabola y = x², a half parabola y = x²/2, a quarter parabola, a sixty-fourth parabola y = x²/64, and one integer cubic.</p>
<div class="panel">
<p><strong>What you are seeing.</strong> Ink is the source, blue/red are the exact
normal rails, gold-dash is Levien's fitted cubic rail, and the grid is the
integer lattice. The dots are the known integer points on the source. The note
counts near-integer points on each rail (tolerance 0.01) and the Levien fit
error.</p>
<p><strong>The simple result.</strong> The source parabola has integer points
(0,0), (1,1), (2,4); the half has fewer; the quarter fewer still. A parabola's
exact offset is a higher-degree <em>rational</em> curve, but not a cubic; for a
general cubic the exact offset is degree 10. The vertex at t=0 gives an integer
point when d is an integer. Elsewhere the normal contains √(1+4t²), so an
exact integer point is a Diophantine question, not an automatic one; scaling can
clear denominators. Levien's rail is a real-valued fit, so it is not expected
to land on integers either. Use the selects to look for the exceptions; the
controls in the generator are the variables to reverse-engineer.</p>
</div>
<h2>Success gallery · integer handles</h2>
<p class="lead">Dashed line is the control polygon; gold squares are the two cubic handles; dots are integer source points. Each case has integer handles and a known number of integer points. These are source/handle successes, not claims that the fitted rail is integer.</p>
<div class="gallery">{gallery_html}</div>

<h2>Levien’s logic</h2>
<div class="panel quote">
<p><strong>Why fit at all.</strong> “The exact offset curve of a cubic Bézier can
be described (it is an analytic curve of degree 10) but it [is] not tractable to
work with.” So the practical method is an approximation.</p>
<p><strong>The method is curve fitting.</strong> “The fundamental concept is
curve fitting, or finding the parameters for a cubic Bézier that most closely
approximate the desired curve.” Levien then uses numerical support: cusp
finding, area/moment fitting, quartic root finding, and an error measure.</p>
<p><strong>One cubic may not be enough.</strong> “A single cubic Bézier might not
be a good enough approximation to the parallel curve of the source cubic Bézier,
so in those cases it is [subdivided] into multiple Bézier segments.”</p>
<p><strong>The error is the judge.</strong> Candidates are thrown into the mix
and “let the error measurement sort it out.” The error is measured by sampling
the exact curve and projecting each sample onto the approximation along the
normal — the Tiller–Hanson test — so subdivision is driven by measured distance,
not by a fixed count.</p>
<p><strong>Cusps are where the fold is.</strong> “These happen when the curvature
of the source curve is equal to one over the offset distance.” Levien finds and
subdivides at the cusps before fitting, because a cubic cannot carry the
reversal.</p>
<p><strong>Scaling.</strong> “If a curve is divided in half, the error of the
approximation will decrease by a factor of 64” — the claimed
<code>O(n⁶)</code> scaling. The earlier Euler-spiral approach was
<code>O(n⁴)</code> (a factor of 16), which is why the cubic fit is attractive.</p>
<p><strong>What it means for the integers.</strong> None of this constrains the
fitted control points to integers. Levien chooses the cubic that best matches
the exact parallel, so the rail is real-valued. That is why this sandbox
searches families and <code>d</code> with a tolerance, rather than assuming an
integer hit; exact integer routes remain lines/arcs, PH and the Pythagorean
spiral. The p-triple Euler polygon is the other integer-friendly route.</p>
<p class="cite">Quotes are short excerpts from Raph Levien, “Parallel curves of
cubic Béziers” (2022-09-09), local copy:
<a href="../reference/external/parallel-beziers.html">reference/external/parallel-beziers.html</a>.
See the article for the full derivation and code.</p>
</div>
<h2>The mechanism, in formulas</h2>
<div class="panel">
<p><strong>1. The exact target.</strong> Write the source cubic as B(t), its
derivative as B′(t), and the unit left normal as N(t). The exact parallel at
signed distance d is:</p>
<div class="formula">
B(t) = (1−t)³P₀ + 3(1−t)²tP₁ + 3(1−t)t²P₂ + t³P₃<br>
B′(t) = 3(1−t)²(P₁−P₀) + 6(1−t)t(P₂−P₁) + 3t²(P₃−P₂)<br>
N(t) = (−B′<sub>y</sub>(t), B′<sub>x</sub>(t)) / |B′(t)|<br>
O<sub>d</sub>(t) = B(t) + d N(t)
</div>
<p>For a general cubic this is an analytic curve of degree 10. It is not a
cubic Bézier, so the fit replaces it with one.</p>

<p><strong>2. Fix the free parameters.</strong> The endpoints and the tangent
<em>directions</em> are taken directly from the exact offset. That leaves only
the two handle lengths λ₀ and λ₁:</p>
<div class="formula">
Q₀ = B(0) + dN(0),   Q₃ = B(1) + dN(1)<br>
T₀ = B′(0)/|B′(0)|,  T₁ = B′(1)/|B′(1)|<br>
C₀ = Q₀,  C₁ = Q₀ + λ₀T₀,  C₂ = Q₃ − λ₁T₁,  C₃ = Q₃
</div>
<p>The handles lie on the two endpoint tangents. They are not constrained to a
parabola; the two scalars are what the area/moment equations determine.</p>

<p><strong>3. Measure area and moment.</strong> The target is reduced to two
numbers. Green’s theorem turns the double integrals into line integrals; the
code evaluates them with 32-point Gauss–Legendre quadrature:</p>
<div class="formula">
A* = ½∫₀¹ y(t) x′(t) dt,   M* = ½∫₀¹ x(t) y(t) x′(t) dt<br>
∫₀¹ f(t) dt ≈ ½ Σ w<sub>i</sub> f((1+ξ<sub>i</sub>)/2)
</div>
<p>After rotating the chord to the x-axis and translating its start to the
origin, normalize by the chord length L: A = A*/L² and M = M*/L³. The fit is
then scale-free.</p>

<p><strong>4. Solve for the handles.</strong> With the chord normalized to
(0,0)–(1,0), let θ₀ and θ₁ be the tangent angles. The signed area of the
candidate cubic is:</p>
<div class="formula">
A(λ₀,λ₁) = (3/20)[2λ₀ sinθ₀ − λ₀λ₁ sin(θ₀−θ₁) − 2λ₁ sinθ₁]
</div>
<p>Setting A(λ₀,λ₁) = A gives λ₁ linearly in λ₀:</p>
<div class="formula">
λ₁ = (2λ₀ sinθ₀ − 20A/3) / (λ₀ sin(θ₀−θ₁) + 2 sinθ₁)
</div>
<p>Substitute that into M(λ₀,λ₁) = M. Clearing the denominator gives a quartic
in λ₀:</p>
<div class="formula">
a₄λ₀⁴ + a₃λ₀³ + a₂λ₀² + a₁λ₀ + a₀ = 0
</div>
<p>The coefficients are polynomials in A, M, sinθ₀, sinθ₁, cosθ₀, cosθ₁; the
explicit expansion is in Levien’s <code>cubic_fit</code> (reference lines
1452–1480). Each non-negative root is a candidate. A near-zero or negative
length is clamped to the tangent intersection and still sent to the error test.</p>

<p><strong>5. Pick the best candidate.</strong> Each candidate is transformed
back to the original frame, then sampled against the exact offset. For each
sample, the code intersects the normal ray with the candidate cubic and takes
the maximum normal distance (Tiller–Hanson). If that error is above tolerance,
the interval is split at t = ½ and the process repeats.</p>

<p><strong>6. The parabola.</strong> For y = x² on x ∈ [0,2], the source
quadratic has P₁ = (1,0); degree elevation gives the cubic handles:</p>
<div class="formula">
Q(t) = (1−t)²(0,0) + 2(1−t)t(1,0) + t²(2,4)<br>
P₀ = (0,0), P₁ = (2/3,0), P₂ = (4/3,4/3), P₃ = (2,4)<br>
O<sub>d</sub>(t) = (t − 2dt/√(1+4t²),  t² + d/√(1+4t²))
</div>
<p>The quadratic handle (1,0) is the intersection of the end tangents. It is not
on the parabola; neither are the elevated cubic handles. The exact offset is a
higher-degree rational curve: set u = √(1+4t²) − 2t, then</p>
<div class="formula">
t = (1−u²)/(4u),  √(1+4t²) = (1+u²)/(2u)<br>
x(u) = t(1 − 2d/√(1+4t²)),  y(u) = t² + d/√(1+4t²)
</div>
<p>So a parabola’s parallel is rational, but it is not a cubic. A general
cubic’s exact parallel is degree 10. Levien’s two handles are still cubic
handles chosen by area and moment; there is no parabolic handle constraint.</p>

<p><strong>The handles on a parabola.</strong> The useful 64 example is
y = x²/64 on x ∈ [0,24]: the cubic handles are (8,0) and (16,3), and the
integer points are (0,0), (8,1), (16,4), (24,9). More generally, on [0,24n]
the handles are (8n,0) and (16n,3n²), all integer. Note that the lattice is
sparser in x — x must be a multiple of 8 — not denser; the gain is integer
handles, not more points per unit x.</p>
<p>For y = kx² over x ∈ [a,b], the
quadratic control is the tangent intersection, and degree elevation gives:</p>
<div class="formula">
P₀ = (a, ka²),  P₁ = ((a+b)/2, kab),  P₂ = (b, kb²)<br>
P₁′ = ((2a+b)/3, k a(a+2b)/3)<br>
P₂′ = ((a+2b)/3, k b(2a+b)/3)
</div>
<p>For a = 0 and b = 3n, these become (n,0) and (2n, 3kn²): integer handles
for integer k. That is a real integer-friendly source. A cubic is a parabola
exactly when C₃ − 3C₂ + 3C₁ − C₀ = 0; Levien does not impose that condition,
so his fitted cubic is general, not a parabola.</p>

<p><strong>Why 3ⁿ, 5ⁿ and 64 appear.</strong> Evaluate a cubic Bézier at a
rational parameter t = p/q:</p>
<div class="formula">
B(p/q) = [(q−p)³P₀ + 3(q−p)²pP₁ + 3(q−p)p²P₂ + p³P₃] / q³
</div>
<p>With integer controls the denominator divides q³. So t = 1/3 gives 27,
t = 1/4 gives 64, t = 1/5 gives 125; scaling by q³ clears the denominators.
This is a Bézier-basis fact, and it is a different “64” from Levien’s error law:
the error 64 is 2⁶, while the sample denominator 64 is 4³. Both can produce the
same-looking integer hits, but only denominator clearing is exact.</p>

<p><strong>7. Scaling: 64, 3⁶, 5⁶.</strong> The claimed error law is
E(m) ≈ E(1)/m⁶. Halving gives 2⁶ = 64; three pieces give 3⁶ = 729; five pieces
give 5⁶ = 15,625:</p>
<table>
<tr><th>subdivisions m</th><th>error factor</th><th>cubics</th></tr>
<tr><td>2</td><td>1/64</td><td>2</td></tr>
<tr><td>3</td><td>1/729</td><td>3</td></tr>
<tr><td>5</td><td>1/15,625</td><td>5</td></tr>
</table>
<p>This is approximation error, not a count of integer hits. More segments mean
more control handles, so there are more chances to <em>notice</em> a near-integer
coordinate; it does not make the curve exact. Scaling the whole geometry by S
multiplies every coordinate by S: a rational point whose denominator divides S
can become integral (the q³ rule above), but an irrational fitted coordinate
remains irrational. The error factor 3⁶ is 729; the sample denominator 3³ is
27; do not conflate the two.</p>

<p><strong>8. Hyperbolae and other sources.</strong> A hyperbola
H(t) = (a cosh t, b sinh t) has tangent (a sinh t, b cosh t) and normal</p>
<div class="formula">
N(t) = (−b cosh t, a sinh t) / √(b²cosh²t + a²sinh²t)
</div>
<p>For a rectangular hyperbola the square root is √(cosh 2t), which is not
generally rational in a rational parameter. The offset is therefore not an
automatic rational/integer curve. Levien’s fit still applies — area, moment and
normal distance can all be evaluated numerically — but exact integer hits are a
Diophantine property of the source, not a consequence of the fitting method.
The exact integer-friendly families remain lines, arcs, PH curves, the
Pythagorean spiral, and the p-triple polygon.</p>
</div>
<h2>Where the bounding-parabola idea lives</h2>
<div class="panel">
<p><strong>Blog, cusp finding (2022-09-09).</strong> The sentence is in
“Parallel curves of cubic Béziers,” section “Cusp finding”:
<a href="https://raphlinus.github.io/curves/2022/09/09/parallel-beziers.html#cusp-finding">raphlinus.github.io/curves/2022/09/09/parallel-beziers.html#cusp-finding</a>.
It is a prose aside; the post links no cusp-specific bounding-parabola code.</p>
<p><strong>Full design, cubic/cubic intersection (2022-08-16).</strong>
<a href="https://github.com/raphlinus/raphlinus.github.io/issues/79">raphlinus/raphlinus.github.io#79</a>
“Path operations” is the detailed write-up. It proposes x = ay² + by + c,
fits it by matching endpoints and signed area (or moments), bounds the cubic
with two hybrid quadratics, and claims Δy³ scaling — “convergence should be
cubic.” It also estimates the stop criterion as ε<sup>−1/3</sup>, roughly 100
segments at ε = 10<sup>−6</sup>.</p>
<p><strong>Prototype (2022-08 / 2023-05).</strong>
<a href="https://github.com/linebender/kurbo/pull/258">linebender/kurbo#258</a>
is the draft cubic/cubic intersection branch. The interesting file is
<a href="https://github.com/linebender/kurbo/blob/1f86c26bc9d35681d84581ae1bd3089eca8e5787/examples/cubic_fun.rs">examples/cubic_fun.rs</a>;
see <code>EstParab</code>, <code>from_cubic</code>, and
<code>intersect_cubics_rec</code>. It is not merged and not wired into kurbo.</p>
<p><strong>Follow-ups.</strong>
<a href="https://github.com/linebender/kurbo/issues/277">kurbo#277</a>
says “My approach is to compute bounding parabolas. A prototype exists in
#258”; <a href="https://github.com/linebender/kurbo/issues/274">kurbo#274</a>
separates the intersection-result trait from the bounding-parabola primitive.
<a href="https://github.com/jneem/linesweeper">jneem/linesweeper</a> is a later
Rust boolean-ops implementation based on #258; it is archived and has moved to
Radicle.</p>
</div>
<div class="controls">
<label>family <select id="family">{opts_fam}</select></label>
<label>offset d <select id="d">{opts_d}</select></label>
</div>
{cards_html}
<script>
const f = document.getElementById("family"), d = document.getElementById("d");
function show() {{
  const fam = f.value, dd = d.value;
  document.querySelectorAll(".card").forEach(c => {{
    c.hidden = !(c.dataset.family === fam && c.dataset.d === dd);
  }});
}}
f.addEventListener("change", show); d.addEventListener("change", show); show();
</script>
</main></body></html>
'''
    out = ROOT / "workbench" / "levien-integer.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    print(f"  {len(cards)} family/d cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
