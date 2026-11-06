"""W05 · Storey 02: the pillar.

    .venv/bin/python scripts/storey_pillar.py
    open workbench/storey-pillar.html

A pillar is a column: a plinth, a torus, an entasised shaft, and a capital.
It reuses the part vocabulary already built — a ground line, cubic profiles,
integer control points and a declared axis — rather than inventing a new
grammar.

The three aspects and the grounding are stated on the page: stripes of
linearity (the ground, the plinth and abacus edges, the flutes), the curve of
the entasis and the echinus, and the axis drawn as a ray, which is the infinite
direction. Ground: the baseline at y = 0. Vertical: the axis at x = 0.

The shaft is an elevation, so its width comes from the *profile*, not from an
offset: the left and right edges are two mirrored cubics with integer controls,
and no parallel-offset claim is made. The swell is the entasis, not an error.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import plant_forms as PF  # noqa: E402

INK, BLUE, RED, GOLD, MUTED = "#2e2413", "#1f5fa8", "#a23b2a", "#c9a441", "#7b6c4e"
PAPER = "#fffdf7"

GROUND = 0.0
AXIS_X = 0.0
PLINTH_TOP = 6.0
BASE_TOP = 12.0
SHAFT_TOP = 84.0
CAP_BAND = 88.0
ABACUS_BOTTOM = 94.0
HEIGHT = 100.0
AXIS_TOP = 110.0

PLINTH_HALF = 24.0
ABACUS_HALF = 19.0
SHAFT_BOTTOM_HALF = 15.0
SHAFT_TOP_HALF = 9.0

# Integer controls, mirrored. right shaft profile; left is the x-negated mirror.
SHAFT_RIGHT = ((15.0, 12.0), (20.0, 38.0), (10.0, 62.0), (9.0, 84.0))
TORUS_RIGHT = ((18.0, 6.0), (22.0, 7.0), (20.0, 11.0), (15.0, 12.0))
ECHINUS_RIGHT = ((10.0, 88.0), (10.0, 91.0), (17.0, 92.0), (17.0, 94.0))

FLUTE_XS = (-5.5, -2.5, 2.5, 5.5)


def mirror(points):
    return [(-p[0], p[1]) for p in points]


def shaft_profiles(n=160):
    right = PF.cubic(*SHAFT_RIGHT, n)
    left = PF.cubic(*mirror(SHAFT_RIGHT), n)
    return left, right


def waist():
    """Widest half-width of the shaft and where it occurs (the entasis)."""
    _left, right = shaft_profiles()
    i = max(range(len(right)), key=lambda k: right[k][0])
    return right[i][0], right[i][1]


def storey_data() -> dict:
    half, y = waist()
    return {
        "height": HEIGHT,
        "ground": GROUND,
        "axis_x": AXIS_X,
        "plinth_half": PLINTH_HALF,
        "abacus_half": ABACUS_HALF,
        "shaft_bottom_half": SHAFT_BOTTOM_HALF,
        "shaft_top_half": SHAFT_TOP_HALF,
        "waist_half": half,
        "waist_y": y,
        "flutes": len(FLUTE_XS),
        "controls": SHAFT_RIGHT,
    }


def build_items() -> list:
    left, right = shaft_profiles()
    items = [
        ([(-34.0, GROUND), (34.0, GROUND)], INK, 2.0, None),
        ([(-PLINTH_HALF, GROUND), (PLINTH_HALF, GROUND), (PLINTH_HALF, PLINTH_TOP),
          (-PLINTH_HALF, PLINTH_TOP), (-PLINTH_HALF, GROUND)], INK, 1.8, None),
        (PF.cubic(*TORUS_RIGHT), INK, 1.6, None),
        (PF.cubic(*mirror(TORUS_RIGHT)), INK, 1.6, None),
        (left, INK, 2.0, None),
        (right, INK, 2.0, None),
        ([(-SHAFT_BOTTOM_HALF, BASE_TOP), (SHAFT_BOTTOM_HALF, BASE_TOP)],
         INK, 1.4, None),
        ([(-SHAFT_TOP_HALF, SHAFT_TOP), (SHAFT_TOP_HALF, SHAFT_TOP)],
         INK, 1.4, None),
    ]
    for x in FLUTE_XS:
        items.append(([(x, BASE_TOP), (x, SHAFT_TOP)], MUTED, 0.6, None))
    items += [
        ([(-10.0, SHAFT_TOP), (10.0, SHAFT_TOP), (10.0, CAP_BAND),
          (-10.0, CAP_BAND), (-10.0, SHAFT_TOP)], INK, 1.6, None),
        (PF.cubic(*ECHINUS_RIGHT), INK, 1.6, None),
        (PF.cubic(*mirror(ECHINUS_RIGHT)), INK, 1.6, None),
        ([(-ABACUS_HALF, ABACUS_BOTTOM), (ABACUS_HALF, ABACUS_BOTTOM),
          (ABACUS_HALF, HEIGHT), (-ABACUS_HALF, HEIGHT),
          (-ABACUS_HALF, ABACUS_BOTTOM)], INK, 2.0, None),
        ([(AXIS_X, GROUND), (AXIS_X, AXIS_TOP)], GOLD, 0.9, "7 5"),
    ]
    return items


def main() -> int:
    data = storey_data()
    figure = PF.figure(build_items(), 900, 760)
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Storey 02 · Pillar</title>
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
.sw.m{{border-top:2px solid {MUTED}}}
.sw.g{{border-top:2px dashed {GOLD}}}
table{{border-collapse:collapse;width:100%;font:12px/1.5 ui-monospace,Menlo,monospace;margin:8px 0 0}}
td,th{{border-bottom:1px solid #d8ccae;padding:5px 8px;text-align:left}}
th{{color:{MUTED};font-weight:600}}
code{{font:12px ui-monospace,Menlo,monospace}}
</style></head><body><main>
<h1>Storey 02 · Pillar</h1>
<p class="lead">A grounded column from the existing parts: a plinth, a torus,
an entasised shaft and a capital, on one declared axis.</p>

<div class="panel">
<p><strong>The parts.</strong> The baseline is the ground; the plinth is a
{data['plinth_half']*2:g}-wide block; the torus is a pair of mirrored cubics;
the shaft is two mirrored cubic profiles with integer controls, swelling to
{data['waist_half']:.2f} at y = {data['waist_y']:.0f} before tapering to
{data['shaft_top_half']:g}; {data['flutes']} flutes mark the shaft; the capital
is a band, an echinus pair and a {data['abacus_half']*2:g}-wide abacus.</p>
<p><strong>The three aspects.</strong> Linearity: the baseline, the plinth and
abacus edges, and the flutes. Curve: the entasis profiles and the echinus.
Infinity: the axis, drawn past the abacus as a ray — the vertical has no top.
<strong>Grounded:</strong> the baseline at y = 0 is the datum; the vertical is
the axis at x = 0. The column stands on the one and rises through the other.</p>
</div>

<div class="art">{figure}</div>
<div class="legend">
<span><i class="sw"></i> ground, plinth, torus, shaft, capital</span>
<span><i class="sw m"></i> flutes</span>
<span><i class="sw g"></i> axis (the vertical, a ray)</span>
</div>

<h2>The numbers</h2>
<div class="panel">
<table>
<tr><th>height</th><td>{data['height']:g} · ground at y = {data['ground']:g}</td></tr>
<tr><th>plinth / abacus</th><td>±{data['plinth_half']:g} / ±{data['abacus_half']:g}</td></tr>
<tr><th>shaft</th><td>±{data['shaft_bottom_half']:g} at the base → ±{data['shaft_top_half']:g} at the neck</td></tr>
<tr><th>entasis</th><td>widest ±{data['waist_half']:.2f} at y = {data['waist_y']:.0f} — the swell, not an error</td></tr>
<tr><th>controls</th><td>{', '.join(f"({p[0]:g},{p[1]:g})" for p in data['controls'])} — integers</td></tr>
<tr><th>ground / vertical</th><td>baseline at y = 0 / axis at x = 0</td></tr>
</table>
</div>

<h2>Why it is a storey</h2>
<div class="panel">
<p>The pillar is not a new curve family. It is the part vocabulary at
architecture scale: ground, block, torus, profile, flute, echinus, abacus,
axis. The profiles are cubics with integer controls and are exact mirrors of
one another; the width comes from the profile, so nothing here claims a
parallel offset. The piece is grounded and names its three aspects.</p>
<p class="note">Re-derive: <code>python scripts/storey_pillar.py</code> ·
<code>python -m unittest tests.test_storey_pillar</code></p>
</div>
</main></body></html>
'''
    out = ROOT / "workbench" / "storey-pillar.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
