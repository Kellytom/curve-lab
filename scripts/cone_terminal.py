"""Draw the two-arc cone terminal, default and symmetric, with its numbers.

    .venv/bin/python scripts/cone_terminal.py

Writes `workbench/cone-terminal.html`. The cap is `curve_lab.terminals.cone_terminal`;
this script only draws what that function returns, so the page cannot disagree
with the engine.

Two figures, same pair of rails:

  * **default** — the cap built from the rail ends as they come. The pair is
    leaned (one rail ends 0.3 lower than the other, the usual small difference on
    a curved spine), so the cap's midpoint sits off the stroke.
  * **symmetric** — `symmetric=True`, `centre` at the stroke's end and `tangent`
    along it. Each rail end is snapped to its mirror position, the tip lands on
    the centreline, and the page prints the shift each end took and the axis
    twist in degrees.

The page states R = 2 x half, the tip at sqrt(3) x half, and both arc centres.
One curve, one picture: the geometry comes from the engine function, not from a
second implementation here.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab.terminals import cone_terminal  # noqa: E402

OUT = ROOT / "workbench" / "cone-terminal.html"

WIDTH, HEIGHT = 900, 430
PAD = 70
HALF = 40.0
LEAN = 12.0  # the - rail ends this much further along the stroke, in model units


def rails(half=HALF, lean=LEAN):
    """Two straight rails ending near y = 0, the second leaned along the stroke."""
    def ribbon(x, end_y):
        return {"spans": [{
            "p0": (x, -260.0), "c1": (x, -170.0), "c2": (x, -80.0),
            "p3": (x, end_y), "t": (0.0, 1.0),
        }]}

    return ribbon(+half, 0.0), ribbon(-half, lean)


class Sheet:
    """Model coordinates to the page: scale, then flip y so +y is up (AGENTS.md)."""

    def __init__(self, scale: float, top: float):
        self.scale = scale
        self.top = top

    def __call__(self, point):
        return (WIDTH / 2 + point[0] * self.scale, self.top - point[1] * self.scale)


def figure(cone, rails_pair, title, notes, axis=None):
    """One cap as an SVG, with labels inside the figure."""
    at = Sheet(2.4, HEIGHT - 90)
    pos, neg = rails_pair
    parts = []
    parts.append(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#fbf7ec"/>')
    # the rails, as the pieces that end at the cap
    for rail, colour in ((pos, "#1f5fa8"), (neg, "#1f5fa8")):
        a, b = at(rail["spans"][0]["p0"]), at(rail["spans"][0]["p3"])
        parts.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" '
                     f'stroke="{colour}" stroke-width="2" fill="none"/>')
    # the cap
    points = []
    for span in cone["spans"]:
        for key in ("p0", "c1", "c2", "p3"):
            points.append(at(span[key]))
    d = (f'M {points[0][0]:.2f},{points[0][1]:.2f} '
         f'C {points[1][0]:.2f},{points[1][1]:.2f} {points[2][0]:.2f},{points[2][1]:.2f} {points[3][0]:.2f},{points[3][1]:.2f} '
         f'C {points[4][0]:.2f},{points[4][1]:.2f} {points[5][0]:.2f},{points[5][1]:.2f} {points[6][0]:.2f},{points[6][1]:.2f}')
    parts.append(f'<path d="{d}" fill="none" stroke="#2e2413" stroke-width="2.2"/>')
    # the tip and the two centres
    tip = at(cone["tip"])
    parts.append(f'<circle cx="{tip[0]:.2f}" cy="{tip[1]:.2f}" r="4" fill="#b23a2b"/>')
    for name, centre in (("centre 1", cone["centres"]["pos"]), ("centre 2", cone["centres"]["neg"])):
        x, y = at(centre)
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.5" fill="none" stroke="#5b7f3a" stroke-width="1.6"/>')
        parts.append(f'<text x="{x + 8:.1f}" y="{y + 4:.1f}" font-size="12" fill="#5b7f3a">{name}</text>')
    # the two radii the construction states
    for centre in (cone["centres"]["pos"], cone["centres"]["neg"]):
        a, b = at(centre), at(cone["tip"])
        parts.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" '
                     f'stroke="#5b7f3a" stroke-width="1" stroke-dasharray="4 4" opacity="0.8"/>')
    if axis is not None:
        a, b = at(axis[0]), at(axis[1])
        parts.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" '
                     f'stroke="#7b6c4e" stroke-width="1" stroke-dasharray="2 5"/>')
        parts.append(f'<text x="{b[0] + 6:.1f}" y="{b[1]:.1f}" font-size="12" fill="#7b6c4e">centreline</text>')
    # titles and numbers, inside the figure
    parts.append(f'<text x="18" y="26" font-size="15" font-weight="600" fill="#2e2413">{title}</text>')
    rows = [notes] if isinstance(notes, str) else notes
    for index, row in enumerate(rows):
        parts.append(f'<text x="18" y="{48 + 16 * index}" font-size="12" fill="#4a3d28">{row}</text>')
    parts.append(f'<circle cx="{WIDTH - 150}" cy="22" r="4" fill="#b23a2b"/>'
                 f'<text x="{WIDTH - 140}" y="26" font-size="12" fill="#4a3d28">tip</text>'
                 f'<circle cx="{WIDTH - 150}" cy="40" r="3.5" fill="none" stroke="#5b7f3a"/>'
                 f'<text x="{WIDTH - 140}" y="44" font-size="12" fill="#4a3d28">arc centre</text>')
    return ('<svg viewBox="0 0 %d %d" role="img" aria-label="%s">%s</svg>'
            % (WIDTH, HEIGHT, title, "".join(parts)))


def table():
    rows = []
    for half in (20.0, 40.0, 60.0):
        rows.append(
            f"<tr><td>{half:g}</td><td>{2 * half:g}</td>"
            f"<td>{math.sqrt(3.0) * half:.3f}</td></tr>")
    return ("<table><thead><tr><th>half width d</th><th>R = 2d</th><th>tip = √3·d</th></tr></thead>"
            "<tbody>" + "".join(rows) + "</tbody></table>")


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fig. C1: the two-arc cone terminal</title>
<style>
:root{{--paper:#fbf7ec;--ink:#2e2413;--muted:#7b6c4e;--rule:#d8ccae}}
body{{margin:0;background:var(--paper);color:var(--ink);
  font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
main{{max-width:960px;margin:0 auto;padding:26px 20px 48px}}
h1{{font-size:24px;margin:0 0 6px}} h2{{font-size:18px;margin:26px 0 8px}}
p{{max-width:74ch}} svg{{width:100%;height:auto;border:1px solid var(--rule);margin:10px 0}}
table{{border-collapse:collapse;margin:8px 0;font:13px/1.5 ui-monospace,Menlo,monospace}}
th,td{{border:1px solid var(--rule);padding:4px 10px;text-align:right}}
th{{background:#f2ead8}} code{{font:13px ui-monospace,Menlo,monospace}}
.note{{color:var(--muted);font-size:13px}}
</style></head><body><main>
<h1>Fig. C1: the two-arc cone terminal</h1>
<p>The end of a ribbon, closed by <strong>two arcs</strong> instead of a cap. Each arc
leaves a rail end, both have radius <code>R = 2 × half width</code>, and they meet at a
point on the centreline <code>√3 × half</code> beyond it. Each arc is a 60° turn, so the
pair is 120° — exactly the cap limit in <code>docs/PHILOSOPHY.md</code>. The tip is a
point, and that is the point of a cone.</p>

<h2>Fig. C1a — the default cap, on a leaned pair of rails</h2>
{default}
<p class="note">The two rail ends disagree by 0.3 model units along the stroke, which is
what a curved spine does. The cap is symmetric about its own axis, but that axis sits off
the stroke: the tip is at x = {default_tip_x:.3f}, not 0. This is the "slightly offset"
the operator saw.</p>

<h2>Fig. C1b — the symmetric cap</h2>
{symmetric}
<p class="note">With <code>symmetric=True</code>, the stroke's end is the cap's midpoint
and the stroke's tangent is its axis. Each rail end is snapped to its mirror position at
the ribbon's true half width ({half:.3f}), the tip lands on the centreline, and the page
reports what moved: {shifts}.</p>

<h2>The numbers</h2>
{table}
<p>Arc centres, as the construction states them: the arc leaving the <code>+</code> rail is
centred on the <code>−</code> rail's end, and the other way round. So the two centres are
the two rail ends, swapped, and each is exactly <code>R</code> from the tip.</p>
<p class="note">Generated by <code>scripts/cone_terminal.py</code> from
<code>curve_lab.terminals.cone_terminal</code>; the page cannot disagree with the engine.
y is up in the model and flipped here at output.</p>
</main></body></html>
"""


def build():
    pos, neg = rails()
    default = cone_terminal(pos, neg)
    symmetric = cone_terminal(pos, neg, symmetric=True, centre=(0.0, 0.0), tangent=(0.0, 1.0))

    # the centreline, drawn as a segment from the cap's midpoint through the tip
    axis = ((0.0, -30.0), (0.0, symmetric["tip"][1] + 20.0))

    default_svg = figure(
        default, (pos, neg), "Fig. C1a: default cap — the tip sits off the stroke",
        [f"R = 2 × half = {default['radius']:.3f}",
         f"tip at ({default['tip'][0]:.3f}, {default['tip'][1]:.3f})",
         f"shift +end {default['shift']['pos']:.3f} · −end {default['shift']['neg']:.3f}",
         f"axis twist {default['axis_twist']:.2f}°"])
    symmetric_svg = figure(
        symmetric, (pos, neg), "Fig. C1b: symmetric cap — the tip on the centreline",
        [f"R = 2 × half = {symmetric['radius']:.3f}",
         f"tip at ({symmetric['tip'][0]:.3f}, {symmetric['tip'][1]:.3f}) = √3 × {symmetric['half']:.3f}",
         f"shift +end {symmetric['shift']['pos']:.3f} · −end {symmetric['shift']['neg']:.3f}",
         f"axis twist {symmetric['axis_twist']:.2f}°"],
        axis=axis)

    shifts = (f"the + rail moved {symmetric['shift']['pos']:.3f} and the − rail "
              f"{symmetric['shift']['neg']:.3f}, axis twist {symmetric['axis_twist']:.2f}°")
    page = PAGE.format(default=default_svg, symmetric=symmetric_svg,
                       default_tip_x=default["tip"][0], half=symmetric["half"],
                       shifts=shifts, table=table())
    OUT.write_text(page)
    print(OUT.relative_to(ROOT))


if __name__ == "__main__":
    build()
