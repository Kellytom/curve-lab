"""The PH family gallery: one illustration per degree/construction.

    .venv/bin/python scripts/ph_families.py
    open workbench/ph-families.html

Every PH curve is z'(t) = h (u² − v², 2uv), with
n = deg h + 2 max(deg u, deg v) + 1. The page shows the built rungs of that
ladder, the non-PH integer cubic for contrast, and what is not built yet.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import generators as G  # noqa: E402
import g3_showcase as S  # noqa: E402
import missing_families as MF  # noqa: E402
import ph_quintic as PQ  # noqa: E402


def curve_svg(pts, w=340, h=250):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    pad = 0.09 * max(max(xs) - min(xs), max(ys) - min(ys), 1e-6)
    f = S.Frame(w, h, min(xs) - pad, max(xs) + pad,
                min(ys) - pad, max(ys) + pad, pad=34)
    step = S._nice_step(max(max(xs) - min(xs), max(ys) - min(ys)))
    grid = []
    gx = math.floor((min(xs) - pad) / step) * step
    while gx <= max(xs) + pad:
        a, b = f((gx, min(ys) - pad)), f((gx, max(ys) + pad))
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" '
                    f'x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{S.RULE}" '
                    f'stroke-width="0.6"/>')
        gx += step
    gy = math.floor((min(ys) - pad) / step) * step
    while gy <= max(ys) + pad:
        a, b = f((min(xs) - pad, gy)), f((max(xs) + pad, gy))
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" '
                    f'x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{S.RULE}" '
                    f'stroke-width="0.6"/>')
        gy += step
    zero = []
    if min(xs) - pad <= 0.0 <= max(xs) + pad:
        a, b = f((0.0, min(ys) - pad)), f((0.0, max(ys) + pad))
        zero.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                    f'y2="{b[1]:.1f}" stroke="{S.BLUE}" stroke-width="1" '
                    f'stroke-dasharray="4 3"/>')
        zero.append(f'<text x="{a[0] + 4:.1f}" y="{a[1] - 4:.1f}" '
                    f'font-family="ui-monospace,Menlo,monospace" font-size="8.5" '
                    f'fill="{S.BLUE}">x=0</text>')
    if min(ys) - pad <= 0.0 <= max(ys) + pad:
        a, b = f((min(xs) - pad, 0.0)), f((max(xs) + pad, 0.0))
        zero.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                    f'y2="{b[1]:.1f}" stroke="{S.BLUE}" stroke-width="1" '
                    f'stroke-dasharray="4 3"/>')
        zero.append(f'<text x="{a[0] + 4:.1f}" y="{a[1] - 4:.1f}" '
                    f'font-family="ui-monospace,Menlo,monospace" font-size="8.5" '
                    f'fill="{S.BLUE}">y=0</text>')
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="PH curve">
  <rect width="{w}" height="{h}" fill="{S.PAPER}"/>
  {''.join(grid)}
  {''.join(zero)}
  <path d="{S._path(pts, f)}" fill="none" stroke="{S.INK}" stroke-width="2.2"/>
  <text x="{w - 10}" y="{h - 10}" text-anchor="end" font-family="ui-monospace,Menlo,monospace" font-size="8.5" fill="{S.MUTED}">x {min(xs):.1f}…{max(xs):.1f} · y {min(ys):.1f}…{max(ys):.1f}</text>
</svg>"""


def card(title, pts, note, badge="PH", bad=False):
    cls = "ph-card bad" if bad else "ph-card"
    return f"""<div class="{cls}">
<h3>{title} <span class="badge {'badge-bad' if bad else ''}">{badge}</span></h3>
{curve_svg(pts)}
<p class="small">{note}</p>
</div>"""


def build():
    cards = []

    pc3 = G.PHCurve(3, u=(2, -2), v=(1, -2), h=(1,))
    cards.append(card(
        "n = 3 · Tschirnhausen PH cubic",
        [pc3.bezier(i / 300) for i in range(301)],
        "h=(1) · u=(2,−2) · v=(1,−2) · scale 24. Every proper cubic PH curve "
        "is the Tschirnhausen cubic up to scale/rotation: one shape, no "
        "inflection, a C-curve. The cubic interpolant in <code>hodograph.py</code> "
        "is a segment of this shape."))

    from curve_lab.pyth_cubic import representatives
    rep = representatives()["s"][0]
    P = [rep["p0"], rep["p1"], rep["p2"], rep["p3"]]
    cards.append(card(
        "n = 3 · integer cubic 3-4-5",
        [S.bezier(P, i / 200) for i in range(201)],
        "An exact integer-control cubic, <strong>not</strong> a PH curve. The "
        "control triple is Pythagorean, but the hodograph is not: the 3-4-5 "
        "base has no rational offset. This is the <code>pyth_cubic</code> "
        "family; see <a href='integer-cubic.html'>integer cubics</a>.",
        badge="not PH", bad=True))

    pc4 = G.PHCurve(4, u=(1, -1), v=(1, -2), h=(1, 2))
    cards.append(card(
        "n = 4 · PH quartic",
        [pc4.bezier(i / 300) for i in range(301)],
        "h=(1,2) · u=(1,−1) · v=(1,−2) · scale 1536. The even degree needs "
        "deg h = 1. It can inflect, which the cubic cannot."))

    for k, (title, h, u, v) in enumerate(PQ.CASES, 1):
        d = PQ.build_case(h, u, v)
        kind = ("u, v quadratic" if max(len(u), len(v)) - 1 == 2
                else "h quadratic, u, v linear")
        cards.append(card(
            f"n = 5 · PH quintic {k} · {kind}",
            d["pts"],
            f"h={h} · u={u} · v={v} · scale {d['scale']:,} · arc {d['arc']} "
            f"rational. One of three representative cases in "
            f"<code>ph_quintic.py</code>; the general quintic family is not "
            f"enumerated."))

    pc6 = G.PHCurve(6, u=(-1, 1, 0), v=(2, -1, 0), h=(1, 2))
    cards.append(card(
        "n = 6 · PH sextic",
        [pc6.bezier(i / 300) for i in range(301)],
        "h=(1,2) · u=(−1,1,0) · v=(2,−1,0) · scale 240. Even degree, with "
        "quadratic generators: the multiple-cusp shapes live here."))

    pts7, scale7, _pc7 = MF.degree_seven_ph()
    cards.append(card(
        "n = 7 · PH septic",
        pts7,
        f"u=(1,2,1,1) · v=(1,−1,1,0) · h=(1) · scale {scale7:,}. The "
        "degree-7 integer example; the general septic family is not built."))

    cards.append(card(
        "n = 2 rational · the circle",
        MF.rational_ph_circle(),
        "x=(1−t²)/(1+t²), y=2t/(1+t²); speed 2/(1+t²) is rational, so the "
        "arc length and offset are rational. There is no polynomial PH n=2; "
        "the rational circle is the n=2 rung."))

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PH families · degree by degree</title>
<style>{S.CSS}
.ph-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:14px}}
.ph-card{{background:var(--paper);border:1px solid var(--rule);padding:8px 10px}}
.ph-card.bad{{border-color:#a23b2a;background:#fff8f6}}
.ph-card h3{{font-size:15px;margin:0 0 6px}}
.badge-bad{{color:#a23b2a;border-color:#a23b2a}}
.lede{{max-width:960px;color:var(--muted)}}
</style></head><body><main>
<p class="eyebrow">curve-lab · PH families</p>
<h1>PH families · degree by degree</h1>
<p class="lede">Every planar PH curve is
<code>z'(t) = h(t)·(u²−v², 2uv)</code>, and Farouki–Sakkalis fixes the degree:
<code>n = deg h + 2·max(deg u, deg v) + 1</code>. With <code>h=1</code> only odd
degrees appear; the <code>h</code> factor is the only route to an even degree.
Below are the built rungs, the non-PH integer cubic for contrast, and what is
not built yet. Model coordinates, +y up; blue dashed lines are x=0/y=0.</p>

<div class="rule"><strong>Degree ladder.</strong>
<code>h=1, u,v linear → 3</code> · <code>h linear, u,v linear → 4</code> ·
<code>h=1, u,v quadratic → 5</code> · <code>h quadratic, u,v linear → 5</code> ·
<code>h linear, u,v quadratic → 6</code> · <code>h=1, u,v cubic → 7</code>.
The rational <code>h</code> gives the rational PH family (the circle).</div>

<div class="ph-grid">{''.join(cards)}</div>

<section class="panel">
<h2>What is made, and what is not</h2>
<p><strong>Made:</strong> the Tschirnhausen cubic; the quartic and sextic
examples with <code>h</code>; three representative PH quintics; the degree-7
integer PH; the rational circle; PH cubic interpolation (<code>hodograph.py</code>,
<code>catenary.html</code>); the integer scalings of each.</p>
<p><strong>Not made yet:</strong> the <strong>general</strong> PH quintic
family — <code>ph_quintic.py</code> has three examples, not the five-parameter
family; the PH quintic Hermite interpolant and C² PH spline; the PH quintic
transition curve (line to arc); the general degree-7 family (one example); the
n=8+ ladder; and rational PH beyond the circle.</p>
<p class="small">The <code>pyth_cubic</code> integer family is exact but
<strong>not PH</strong>: its name is the control triple, not the hodograph. The
cubic PH family is the Tschirnhausen, one shape. The
<a href="../docs/PH-INTEGER.html">PH-INTEGER notes</a> have the arithmetic;
<a href="missing-families.html">the missing families</a> have the rational
circle and the septic; <a href="catenary.html">the catenary</a> is four PH
cubics; <a href="quintic-showcase.html">the quintic G3 page</a> is a different
(interpolation) story.</p>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "ph-families.html"
    out.write_text(html, encoding="utf-8")
    print(out)
    return out


if __name__ == "__main__":
    build()
