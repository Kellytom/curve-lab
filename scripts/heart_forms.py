"""Fifteen heart forms, each drawn to its true extent.

    .venv/bin/python scripts/heart_forms.py
    open workbench/heart-forms.html

The Beutel sextic is the one the engine samples elsewhere.  The other four are
here for comparison: the cardioid (rational), the |x|^(2/3) heart (two sampled
branches), the Fourier Valentine, and the polar heart after MathWorld.  Nothing
is fitted yet; the page is a catalogue, so the shapes can be read side by side
before any clothoid work starts.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from grid_view import MARK, crossings, grid_lines, nice_step  # noqa: E402
import generators as G  # noqa: E402

INK, GOLD, DOT = "#2e2413", "#c9a441", "#b23a2b"
GRID, LINE, MUTED = "#ece4cf", "#d8ccae", "#7b6c4e"


def beutel(n=400):
    upper, lower = G.heart_branches(n)
    return [[(float(x), float(y)) for x, y in upper],
            [(float(x), float(y)) for x, y in lower]]


def cardioid(n=720):
    pts = []
    for i in range(n + 1):
        th = 2 * math.pi * i / n
        r = 1 + math.sin(th)
        pts.append((r * math.cos(th), r * math.sin(th)))
    return [pts]


def abs_heart(n=720):
    upper, lower = [], []
    for i in range(n + 1):
        x = -1 + 2 * i / n
        base = abs(x) ** (2 / 3)
        s = math.sqrt(max(0.0, 1 - x * x))
        upper.append((x, base + s))
        lower.append((x, base - s))
    return [upper, lower]


def valentine(n=1440):
    pts = []
    for i in range(n + 1):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = (13 * math.cos(t) - 5 * math.cos(2 * t) -
             2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((x, y))
    return [pts]


def wolfram(n=1440):
    pts = []
    for i in range(n + 1):
        th = 2 * math.pi * i / n
        r = (2 - 2 * math.sin(th) +
             math.sin(th) * math.sqrt(abs(math.cos(th))) /
             (math.sin(th) + 1.4))
        pts.append((r * math.cos(th), r * math.sin(th)))
    return [pts]


def kuriscak(n=720):
    """x^2 + [y - 2(x^2+|x|-6)/(3(x^2+|x|+2))]^2 = 36, two branches."""
    upper, lower = [], []
    for i in range(n + 1):
        x = -6 + 12 * i / n
        f = 2 * (x * x + abs(x) - 6) / (3 * (x * x + abs(x) + 2))
        s = math.sqrt(max(0.0, 36 - x * x))
        upper.append((x, f + s))
        lower.append((x, f - s))
    return [upper, lower]


def wu_nick(n=720):
    """x^2 + y^2 - |x| y = 1: the ellipse half plus its reflection."""
    xmax = 2 / math.sqrt(3)
    upper, lower = [], []
    for i in range(n + 1):
        x = -xmax + 2 * xmax * i / n
        s = math.sqrt(max(0.0, 4 - 3 * x * x))
        upper.append((x, (abs(x) + s) / 2))
        lower.append((x, (abs(x) - s) / 2))
    return [upper, lower]


def mangaldan(n=1440):
    """A nephroid modified into a heart (MathWorld 7-8)."""
    pts = []
    for i in range(n + 1):
        t = 2 * math.pi * i / n
        x = -math.sqrt(2) * math.sin(t) ** 3
        y = 2 * math.cos(t) - math.cos(t) ** 2 - math.cos(t) ** 3
        pts.append((x, y))
    return [pts]


def dascanio(n=1440):
    """x = sin t cos t ln|t|, y = |t|^0.3 sqrt(cos t), t in [-1, 1]."""
    pts = []
    for i in range(n + 1):
        t = -1 + 2 * i / n
        if t == 0:
            continue
        x = math.sin(t) * math.cos(t) * math.log(abs(t))
        y = abs(t) ** 0.3 * math.sqrt(max(0.0, math.cos(t)))
        pts.append((x, y))
    return [pts]


def half_ellipses(n=720):
    """y = |x| +/- sqrt(1-x^2): two half-ellipses, the tongue-in-cheek heart."""
    upper, lower = [], []
    for i in range(n + 1):
        x = -1 + 2 * i / n
        s = math.sqrt(max(0.0, 1 - x * x))
        upper.append((x, abs(x) + s))
        lower.append((x, abs(x) - s))
    return [upper, lower]


def sqrt_heart(n=720):
    """y = sqrt(|x|) +/- sqrt(1-x^2)."""
    upper, lower = [], []
    for i in range(n + 1):
        x = -1 + 2 * i / n
        s = math.sqrt(max(0.0, 1 - x * x))
        r = math.sqrt(abs(x))
        upper.append((x, r + s))
        lower.append((x, r - s))
    return [upper, lower]


def eisemann(n=720):
    """x^2 + (y - (3/4)|x|^(2/3))^2 = 1."""
    upper, lower = [], []
    for i in range(n + 1):
        x = -1 + 2 * i / n
        s = math.sqrt(max(0.0, 1 - x * x))
        b = 0.75 * abs(x) ** (2 / 3)
        upper.append((x, b + s))
        lower.append((x, b - s))
    return [upper, lower]


def sio(n=720):
    """x^2 + 2(y - (3/5)|x|^(2/3))^2 = 1."""
    upper, lower = [], []
    for i in range(n + 1):
        x = -1 + 2 * i / n
        s = math.sqrt(max(0.0, (1 - x * x) / 2))
        b = 0.6 * abs(x) ** (2 / 3)
        upper.append((x, b + s))
        lower.append((x, b - s))
    return [upper, lower]


def holzapfel(n=720):
    """Two semicircles on top; y = acos(1-|x|) - pi below."""
    upper, lower = [], []
    for i in range(n + 1):
        x = -2 + 4 * i / n
        ax = abs(x)
        u = 1 - (ax - 1) ** 2
        if u >= 0:
            upper.append((x, math.sqrt(u)))
        v = 1 - ax
        if -1 <= v <= 1:
            lower.append((x, math.acos(v) - math.pi))
    return [upper, lower]


def hechinger(n=720):
    """Two semicircles on top; y = -3 sqrt(1 - sqrt(|x|/2)) below."""
    upper, lower = [], []
    for i in range(n + 1):
        x = -2 + 4 * i / n
        ax = abs(x)
        u = 1 - (ax - 1) ** 2
        if u >= 0:
            upper.append((x, math.sqrt(u)))
        v = 1 - math.sqrt(ax / 2)
        if v >= 0:
            lower.append((x, -3 * math.sqrt(v)))
    return [upper, lower]


def figure(branches, w=300.0, h=300.0):
    pts = [p for br in branches for p in br]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = 0.08
    x0, x1 = x0 - pad * (x1 - x0), x1 + pad * (x1 - x0)
    y0, y1 = y0 - pad * (y1 - y0), y1 + pad * (y1 - y0)
    k = min((w - 16) / (x1 - x0), (h - 16) / (y1 - y0))
    ox, oy = (w - (x1 - x0) * k) / 2, (h - (y1 - y0) * k) / 2

    def put(p):
        # +y up in the model, y-down in SVG: the one flip
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k)

    step = nice_step(max(x1 - x0, y1 - y0))
    body = "".join(grid_lines(put, x0, x1, y0, y1, step, "#ece4cf"))
    body += "".join(
        f'<circle class="lattice" cx="{put(p)[0]:.1f}" cy="{put(p)[1]:.1f}" '
        f'r="2.0" fill="{MARK}"/>' for p in crossings(branches, step))
    body += "".join(
        '<path d="M ' + " L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}"
                                   for p in br) +
        f'" fill="none" stroke="{INK}" stroke-width="2.2" '
        f'stroke-linejoin="round"/>' for br in branches)
    return (f'<svg viewBox="0 0 {w:.0f} {h:.0f}" '
            f'xmlns="http://www.w3.org/2000/svg">'
            f'<rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" '
            f'fill="#fffdf7" stroke="{LINE}"/>{body}</svg>')


FORMS = [
    dict(key="Beutel sextic",
         eq="(x² + y² − 1)³ = x² y³",
         kind="implicit",
         note="sextic · genus 4 · three real cusps · sampled",
         source="E. Beutel 1909 · MathWorld (1)",
         branches=beutel),
    dict(key="Cardioid",
         eq="r = 1 + sin θ",
         kind="polar",
         note="rational · one cusp, at the bottom · exact",
         source="MathWorld (11)",
         branches=cardioid),
    dict(key="|x| heart",
         eq="x² + (y − |x|²ᐟ³)² = 1",
         kind="implicit",
         note="two sampled branches · cusps at the cleft and the point",
         source="J. Schroeder · MathWorld (2)",
         branches=abs_heart),
    dict(key="Fourier Valentine",
         eq="x = 16 sin³ t, y = 13 cos t − 5 cos 2t − 2 cos 3t − cos 4t",
         kind="parametric",
         note="Fourier series · closed · sampled",
         source="MathWorld (5–6)",
         branches=valentine),
    dict(key="Polar heart",
         eq="r = 2 − 2 sin θ + sin θ √|cos θ| / (sin θ + 1.4)",
         kind="polar",
         note="after MathWorld's anonymous polar heart · sampled",
         source="MathWorld (12)",
         branches=wolfram),
    dict(key="Kuriscak heart",
         eq="x² + [y − 2(x²+|x|−6)/(3(x²+|x|+2))]² = 36",
         kind="implicit",
         note="two sampled branches · the Kuriscak heart",
         source="P. Kuriscak · MathWorld (4)",
         branches=kuriscak),
    dict(key="Wu/Nick heart",
         eq="x² + y² − |x| y = 1",
         kind="implicit",
         note="the right half of an ellipse plus its reflection",
         source="F. Wu 2025 · Nick 2014 · MathWorld (13–14)",
         branches=wu_nick),
    dict(key="Mangaldan heart",
         eq="x = −√2 sin³ t, y = 2 cos t − cos² t − cos³ t",
         kind="parametric",
         note="a nephroid modified into a heart · closed",
         source="J. Mangaldan 2023 · MathWorld (7–8)",
         branches=mangaldan),
    dict(key="Dascanio heart",
         eq="x = sin t cos t ln|t|, y = |t|⁰·³ √cos t",
         kind="parametric",
         note="t ∈ [−1, 1] · the two halves meet at the origin",
         source="H. Dascanio 2003 · MathWorld (9–10)",
         branches=dascanio),
    dict(key="Half-ellipses",
         eq="y = |x| ± √(1 − x²)",
         kind="explicit",
         note="two half-ellipses · the oldest joke heart",
         source="N. Herrmann · Sillke collection",
         branches=half_ellipses),
    dict(key="Square-root heart",
         eq="y = √|x| ± √(1 − x²)",
         kind="explicit",
         note="two sampled branches",
         source="F. Krause / K.-H. Kriegl · Sillke collection",
         branches=sqrt_heart),
    dict(key="Eisemann heart",
         eq="x² + (y − (3/4)|x|²ᐟ³)² = 1",
         kind="implicit",
         note="the |x| heart with a smaller lift",
         source="K. Eisemann · Sillke collection",
         branches=eisemann),
    dict(key="sio heart",
         eq="x² + 2(y − (3/5)|x|²ᐟ³)² = 1",
         kind="implicit",
         note="a wider |x| heart",
         source="sio · Sillke collection",
         branches=sio),
    dict(key="Holzapfel heart",
         eq="y = √(1−(|x|−1)²), y = arccos(1−|x|) − π",
         kind="explicit",
         note="two semicircles on top, an arccos curve below",
         source="M. Holzapfel · Sillke collection",
         branches=holzapfel),
    dict(key="Hechinger heart",
         eq="y = √(1−(|x|−1)²), y = −3√(1−√(|x|/2))",
         kind="explicit",
         note="two semicircles on top, a root curve below",
         source="T. Hechinger · Sillke collection",
         branches=hechinger),
]


def main():
    cards = "".join(
        f"""<section><h2>{f['key']}</h2>
  <p class="input">{f['eq']}</p>
  <div class="art">{figure(f['branches']())}</div>
  <p class="cap">{f['kind']} · {f['note']}<br>
  <span class="src">{f['source']}</span></p></section>""" for f in FORMS)
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Heart forms — fifteen, to their true extent</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1040px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 22px}}
h2{{font:600 11px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.12em;
text-transform:uppercase;color:{MUTED};margin:0 0 4px}}
.input{{font:12px/1.45 ui-monospace,Menlo,monospace;color:{MUTED};
margin:0 0 6px;word-break:break-word}}
.cap{{font-size:12px;color:{MUTED};margin:0}}
.src{{display:block;font-size:11px;color:#a89a7e;margin-top:2px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
section{{background:#fffdf7;border:1px solid {LINE};padding:12px}}
.art{{background:#fffdf7;margin:4px 0 8px}}
svg{{display:block;width:100%;height:auto}}
.panel{{background:#fffdf7;border:1px solid {LINE};padding:16px 18px;margin:0 0 20px}}
</style></head><body><main>
<h1>Heart forms</h1>
<p class="lead">Fifteen formulaic hearts, each drawn to its true extent.  The
Beutel sextic is the one the engine samples; the rest are here to read against
it before the French-curve and clothoid work begins.</p>
<div class="panel">
<p><strong>What is on the page.</strong> The cardioid is the one rational
member here.  The rest are sampled: the implicit forms because they are not
rational in the engine's sense, the parametric and polar forms because they are
transcendental or piecewise.  No form is fitted, measured against a reference,
or spliced at this stage; the page is a catalogue, not a claim.</p>
<p><strong>Sources.</strong> The implicit, parametric and polar forms are from
<a href="https://mathworld.wolfram.com/HeartCurve.html">MathWorld's Heart
Curve</a>; the explicit and composite forms are from
<a href="https://www.math.uni-bielefeld.de/~sillke/PUZZLES/heart-curves">Torsten
Sillke's collection</a>.  The original names are on each card.</p>
</div>
<div class="grid2">{cards}</div>
</main></body></html>
"""
    out = ROOT / "workbench" / "heart-forms.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
