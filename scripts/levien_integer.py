"""Levien integer sandbox.

    .venv/bin/python scripts/levien_integer.py
    open workbench/levien-integer.html

The simple conditions: a parabola y = x²/k on x∈[0,2], its half/quarter
variants, and a cubic control case.  Each card draws the source, the exact
normal rail, Levien's fitted cubic rail, the integer lattice, and the
near-integer hit counts.  Choose a family and offset distance with the two
selects.

The exact integer points on the source are known.  The exact parallel of a
parabola is not rational, and Levien's rail is fitted, so integer rail hits are
expected to be rare; the page is for finding the exceptions.
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
    # A non-parabolic cubic with integer controls, for comparison.
    out["cubic"] = {
        "label": "cubic control · integer points",
        "span": {"p0": (0, 0), "c1": (1, 0), "c2": (2, 4), "p3": (3, 9)},
        "source": [(0, 0), (3, 9)],
    }
    return out


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
.cite{{font:10px/1.5 ui-monospace,Menlo,monospace;color:{MUTED};margin:12px 0 0}}
code{{font:12px ui-monospace,Menlo,monospace}}
</style></head><body><main>
<h1>Levien integer sandbox</h1>
<p class="lead">Simple conditions first: a parabola y = x², a half parabola y = x²/2, a quarter parabola, and one integer cubic.</p>
<div class="panel">
<p><strong>What you are seeing.</strong> Ink is the source, blue/red are the exact
normal rails, gold-dash is Levien's fitted cubic rail, and the grid is the
integer lattice. The dots are the known integer points on the source. The note
counts near-integer points on each rail (tolerance 0.01) and the Levien fit
error.</p>
<p><strong>The simple result.</strong> The source parabola has integer points
(0,0), (1,1), (2,4); the half has fewer; the quarter fewer still. The exact
parallel of a parabola is not rational, so an integer rail point is rare. The
vertex at t=0 gives one when d is an integer; elsewhere the normal contains
√(1+4t²), so it is not integer. Levien's rail is a real-valued fit, so it is
not expected to land on integers either. Use the selects to look for the
exceptions; the controls in the generator are the variables to reverse-engineer.</p>
</div>
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
