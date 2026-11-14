"""Rosettes from a short arc: repeat it N-fold about its own centroid.

    .venv/bin/python scripts/lac_rosettes.py
    open workbench/lac-rosettes.html

The finding this page records: an arc of 45 or 90 degrees, repeated N times at
360/N about its centroid, crosses its neighbour exactly once for N of 3 and
more, and twice for N = 2. The crossings are the ornament: a rosette of N petals
with N meetings, or a lens with two.

Two families are drawn, the circle (p = 0) and the log spiral (p = 1), because
they are the two ends of the log-aesthetic family that behave: the circle is
congruent under rotation, the spiral grows. The Euler (p = -1) looks the same at
this turn and is left out to keep the page readable.

Page space is y down, as every consumer of spirals/*.json expects, so each
figure is flipped once at output.
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys  # noqa: E402
sys.path.insert(0, str(ROOT / "scripts"))

import lac_generate as L  # noqa: E402
from ph_crossings import pair_crossings  # noqa: E402

OUT = ROOT / "workbench" / "lac-rosettes.html"
SIZE = 210
FAMILIES = ((0.0, "circle"), (1.0, "log spiral"))
TURNS = (45, 90)
COPIES = (2, 3, 4, 6)


def rotate(points, degrees, about):
    angle = math.radians(degrees)
    cos, sin = math.cos(angle), math.sin(angle)
    cx, cy = about
    return [(cx + (x - cx) * cos - (y - cy) * sin,
             cy + (x - cx) * sin + (y - cy) * cos) for x, y, _ in points]


def centroid(points):
    return (sum(p[0] for p in points) / len(points),
            sum(p[1] for p in points) / len(points))


def rosette(alpha, turn, copies):
    base = L.points_for(alpha, turn)
    centre = centroid(base)
    petals = [rotate(base, 360.0 * k / copies, centre) for k in range(copies)]
    meetings = 0
    for k in range(copies):
        meetings += len(pair_crossings(petals[k], petals[(k + 1) % copies]))
    return petals, meetings


def panel(alpha, label, turn, copies, number):
    petals, meetings = rosette(alpha, turn, copies)
    points = [point for petal in petals for point in petal]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    pad = 16
    scale = (SIZE - 2 * pad) / span
    ox = pad - min(xs) * scale
    oy = pad - min(ys) * scale

    def draw(petal):
        # y is flipped once here: the data is design space, the page is y down
        return "M" + " L".join(
            f"{(ox + x * scale):.1f},{(oy + y * scale):.1f}" for x, y in petal)

    paths = "".join(f'<path d="{draw(petal)}" fill="none" stroke="#2e2413" '
                    f'stroke-width="1.5"/>' for petal in petals)
    title = f"{label} &middot; {turn}&deg; &middot; {copies} copies"
    return f'''<figure class="plate">
  <figcaption><span class="tag">Fig. R{number}</span> {title}</figcaption>
  <svg viewBox="0 0 {SIZE} {SIZE}" role="img" aria-label="{title}, {meetings} crossings">
    <rect width="{SIZE}" height="{SIZE}" fill="#fbf7ec"/>
    {paths}
    <text x="{SIZE // 2}" y="{SIZE - 6}" font-size="11" fill="#7b6c4e"
          text-anchor="middle">{meetings} crossings</text>
  </svg>
</figure>'''


def build():
    plates = []
    number = 1
    for alpha, label in FAMILIES:
        for turn in TURNS:
            for copies in COPIES:
                plates.append(panel(alpha, label, turn, copies, number))
                number += 1
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rosettes from a short arc</title>
<style>
:root{{--paper:#fbf7ec;--ink:#2e2413;--muted:#7b6c4e;--rule:#d8ccae}}
*{{box-sizing:border-box}}
body{{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:18px 20px 40px}}
h1{{font-size:24px;margin:0 0 4px}}
.eyebrow{{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;
  text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
.panel{{background:var(--paper);border:1px solid var(--rule);padding:12px 14px;margin:0 0 12px}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}
@media(max-width:820px){{.grid{{grid-template-columns:repeat(2,1fr)}}}}
.plate{{margin:0;background:var(--paper);border:1px solid var(--rule);padding:6px}}
.plate figcaption{{font:11px/1.4 ui-monospace,Menlo,monospace;color:var(--muted);margin:0 0 4px}}
.plate .tag{{color:#8a3b2a}}
.plate svg{{width:100%;height:auto;display:block}}
</style></head><body><main>
<p class="eyebrow">curve-lab &middot; short arcs</p>
<h1>Rosettes from a 45 or 90 degree arc</h1>
<section class="panel">
<p>One arc of 45 or 90 degrees, repeated N times at 360/N about its own centroid.
The count under each plate is where neighbouring petals cross. Three or more
copies cross once per join, so a rosette of N petals has N meetings; two copies
cross twice, which is the lens.</p>
<p class="small">The circle (p = 0) and the log spiral (p = 1) are the two ends of
the log-aesthetic family that behave at this turn. Generated by
<code>scripts/lac_rosettes.py</code> from <code>scripts/lac_generate.py</code>.</p>
</section>
<section class="panel">
<div class="grid">
{"".join(plates)}
</div>
</section>
</main></body></html>
'''
    OUT.write_text(page)
    print(f"{OUT.relative_to(ROOT)}  {len(plates)} plates")


if __name__ == "__main__":
    build()
