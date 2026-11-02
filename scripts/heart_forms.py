"""Five heart forms, each drawn to its true extent.

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

    body = "".join(
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
         note="sextic · genus 4 · three real cusps · sampled",
         branches=beutel),
    dict(key="Cardioid",
         eq="r = 1 + sin θ",
         note="rational · one cusp, at the bottom · exact",
         branches=cardioid),
    dict(key="|x| heart",
         eq="x² + (y − |x|²ᐟ³)² = 1",
         note="two sampled branches · cusps at the cleft and the point",
         branches=abs_heart),
    dict(key="Fourier Valentine",
         eq="x = 16 sin³ t, y = 13 cos t − 5 cos 2t − 2 cos 3t − cos 4t",
         note="Fourier series · closed · sampled",
         branches=valentine),
    dict(key="Polar heart",
         eq="r = 2 − 2 sin θ + sin θ √|cos θ| / (sin θ + 1.4)",
         note="polar · after MathWorld's heart curve · sampled",
         branches=wolfram),
]


def main():
    cards = "".join(
        f"""<section><h2>{f['key']}</h2>
  <p class="input">{f['eq']}</p>
  <div class="art">{figure(f['branches']())}</div>
  <p class="cap">{f['note']}</p></section>""" for f in FORMS)
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Heart forms — five, to their true extent</title>
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
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
section{{background:#fffdf7;border:1px solid {LINE};padding:12px}}
.art{{background:#fffdf7;margin:4px 0 8px}}
svg{{display:block;width:100%;height:auto}}
.panel{{background:#fffdf7;border:1px solid {LINE};padding:16px 18px;margin:0 0 20px}}
</style></head><body><main>
<h1>Heart forms</h1>
<p class="lead">Five heart forms, each drawn to its true extent.  The Beutel
sextic is the one the engine samples; the other four are here to read against
it before the French-curve and clothoid work begins.</p>
<div class="panel">
<p><strong>What is on the page.</strong> The cardioid is the one rational
member here.  The <code>|x|</code> heart and the two closed parametric forms
are sampled, because they are not polynomial rational curves in the engine's
sense.  No form is fitted, measured against a reference, or spliced at this
stage; the page is a catalogue, not a claim.</p>
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
