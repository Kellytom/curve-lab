"""W05 · Storey 01: the monstrance.

    .venv/bin/python scripts/storey_monstrance.py
    open workbench/storey-monstrance.html

A monstrance is a vessel: a foot, a stem, a head with a host, and a ray
sunburst. This first storey reuses the part vocabulary already built — a
ground line, a stem with two rails, a circular head, the p-triple ray fan and a
small cross — rather than inventing a new grammar.

The three aspects and the grounding are stated on the page: stripes of
linearity (ground, rays), the curve of the stem and head, the rays as the
infinite direction, and the vertical stem grounded on the horizontal baseline.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import plant_forms as PF  # noqa: E402

INK, BLUE, RED, GOLD, MUTED = "#2e2413", "#1f5fa8", "#a23b2a", "#c9a441", "#7b6c4e"
PAPER = "#fffdf7"

GROUND = 0.0
FOOT = 7.0
STEM_TOP = 82.0
HEAD = (0.0, 108.0)
HEAD_R = 24.0
HOST_R = 12.0
RAYS = [(m, 2.0 * math.atan2(1.0, m)) for m in range(2, 14)]
CROSS_TOP = 154.0


def stem_points(n=220):
    return PF.cubic((0.0, FOOT), (0.0, 30.0), (0.0, 58.0),
                    (0.0, STEM_TOP), n)


def ray_lines():
    out = []
    for m, ang in RAYS:
        length = 44.0 - 1.7 * m
        for sign in (1, -1):
            a = 0.5 * math.pi + sign * ang
            out.append([(HEAD[0] + HEAD_R * math.cos(a),
                         HEAD[1] + HEAD_R * math.sin(a)),
                        (HEAD[0] + (HEAD_R + length) * math.cos(a),
                         HEAD[1] + (HEAD_R + length) * math.sin(a))])
    return out


def circle(radius, n=240):
    return [(HEAD[0] + radius * math.cos(2 * math.pi * i / n),
             HEAD[1] + radius * math.sin(2 * math.pi * i / n))
            for i in range(n + 1)]


def storey_data() -> dict:
    return {
        "rays": 2 * len(RAYS),
        "head_radius": HEAD_R,
        "host_radius": HOST_R,
        "stem": STEM_TOP - FOOT,
        "height": CROSS_TOP,
        "ground": GROUND,
    }


def build_items() -> list:
    stem = stem_points()
    plus, minus = PF.normal_offsets(stem, 2.2)
    items = [
        ([(-62.0, GROUND), (62.0, GROUND)], INK, 2.0, None),
        ([(-34.0, GROUND), (-22.0, FOOT), (22.0, FOOT), (34.0, GROUND)],
         INK, 1.8, None),
        (plus, BLUE, 1.0, None),
        (minus, RED, 1.0, None),
        (stem, INK, 2.2, None),
    ]
    for line in ray_lines():
        items.append((line, GOLD, 1.2, None))
    items.append((circle(HEAD_R), INK, 2.0, None))
    items.append((circle(HOST_R), INK, 1.6, None))
    items.append(([(0.0, HEAD[1] + HEAD_R), (0.0, CROSS_TOP)], INK, 1.8, None))
    items.append(([(-8.0, CROSS_TOP - 8.0), (8.0, CROSS_TOP - 8.0)],
                  INK, 1.8, None))
    return items


def main() -> int:
    data = storey_data()
    figure = PF.figure(build_items(), 900, 760)
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Storey 01 · Monstrance</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1000px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 18px}}
h2{{font:600 12px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.10em;text-transform:uppercase;color:{MUTED};margin:30px 0 8px}}
.panel{{background:{PAPER};border:1px solid #d8ccae;padding:16px 18px;margin:0 0 18px}}
.art{{background:{PAPER};border:1px solid #d8ccae;padding:8px;margin:0 0 8px}}
svg{{display:block;width:100%;height:auto}}
.legend{{display:flex;gap:16px;flex-wrap:wrap;font:11px ui-monospace,Menlo,monospace;color:{MUTED};margin:6px 0 0}}
.sw{{display:inline-block;width:20px;height:0;border-top:3px solid {INK};margin-right:5px;vertical-align:middle}}
.sw.b{{border-top:2px solid {BLUE}}}.sw.r{{border-top:2px solid {RED}}}
.sw.g{{border-top:2px solid {GOLD}}}
table{{border-collapse:collapse;width:100%;font:12px/1.5 ui-monospace,Menlo,monospace;margin:8px 0 0}}
td,th{{border-bottom:1px solid #d8ccae;padding:5px 8px;text-align:left}}
th{{color:{MUTED};font-weight:600}}
code{{font:12px ui-monospace,Menlo,monospace}}
</style></head><body><main>
<h1>Storey 01 · Monstrance</h1>
<p class="lead">A vessel from the existing parts: a ground, a stem, a head,
a host and a p-triple ray fan.</p>

<div class="panel">
<p><strong>The parts.</strong> The baseline is the ground; the foot is a
trapezoid; the stem is a cubic with two rails at ±2.2; the head is a circle of
radius {data['head_radius']:g} with a host of {data['host_radius']:g}; the
{data['rays']} rays are the p-triple angles 2·atan(1/m), mirrored. A small cross
tops it.</p>
<p><strong>The three aspects.</strong> Linearity: the baseline and the rays.
Curve: the stem and the head. Infinity: the rays continue to a point at
infinity. <strong>Grounded:</strong> the horizontal baseline is the datum; the
stem is the vertical. The vessel stands on the one and rises through the
other.</p>
</div>

<div class="art">{figure}</div>
<div class="legend">
<span><i class="sw"></i> ground, foot, stem, head, cross</span>
<span><i class="sw b"></i> +rail</span>
<span><i class="sw r"></i> −rail</span>
<span><i class="sw g"></i> p-triple rays</span>
</div>

<h2>The numbers</h2>
<div class="panel">
<table>
<tr><th>rays</th><td>{data['rays']} · 2·atan(1/m), m = 2…13, mirrored</td></tr>
<tr><th>head / host</th><td>R = {data['head_radius']:g} · host R = {data['host_radius']:g}</td></tr>
<tr><th>stem</th><td>{data['stem']:g} tall · rails at ±2.2</td></tr>
<tr><th>overall</th><td>{data['height']:g} high · ground at y = {data['ground']:g}</td></tr>
<tr><th>ground / vertical</th><td>baseline at y = 0 / stem on x = 0</td></tr>
</table>
</div>

<h2>Why it is a storey</h2>
<div class="panel">
<p>The monstrance is not a new curve family. It is the part vocabulary used at
architecture scale: ground, foot, stem, rails, head, host, rays, cross. The
parts are declared, the rays are the same exact p-triple angles as the showcase
fan, and the piece is grounded and names its three aspects.</p>
<p class="note">Re-derive: <code>python scripts/storey_monstrance.py</code> ·
<code>python -m unittest tests.test_storey_monstrance</code></p>
</div>
</main></body></html>
'''
    out = ROOT / "workbench" / "storey-monstrance.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
