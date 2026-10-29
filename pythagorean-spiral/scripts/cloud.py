"""Generate docs/CLOUD.md and its HTML twin: a layered cloud as a veil.

    python scripts/cloud.py
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from pythagorean_spiral import place  # noqa: E402
from pythagorean_spiral.exact import Dir  # noqa: E402
from pythagorean_spiral.spiral import Spiral  # noqa: E402
from pythagorean_spiral.triples import for_angle  # noqa: E402

import explainer as ex  # noqa: E402

FIG = ex.FIG
INK, GOLD, RED, BLUE, FAINT = ex.INK, ex.GOLD, ex.RED, ex.BLUE, ex.FAINT

# light tans and grays: one palette for every artwork behind the veil
WALL = "#e9dfd0"
TANS = ["#f1e9dc", "#e9dfd0", "#ded2c0", "#d3c6b2"]
GRAYS = ["#d9d5ce", "#cbc6be", "#bcb7ae"]


def circle_points(per_degree: int = 1):
    """A near-closed circle chain: one triangle angle per chord, exact points."""
    tri = for_angle(2.0)
    n = round(360 / tri.degrees)
    path = Spiral(tri, 1, heading=Dir.east())
    path.extend([0] + [1] * (n - 1))
    return path.nodes, tri, n


CIRCLE, TRI, N = circle_points()


def ellipse(cx, cy, rx, ry):
    """A circle scaled by rational radii: still exact, now an ellipse."""
    cx, cy = Fraction(cx), Fraction(cy)
    rx, ry = Fraction(rx), Fraction(ry)
    return [(cx + rx * x, cy + ry * y) for x, y in CIRCLE]


def puff(c, cx, cy, rx, ry, fill, alpha=0.42):
    pts = [(float(x), float(y)) for x, y in ellipse(cx, cy, rx, ry)]
    c.poly(pts + [pts[0]], fill=fill, stroke=fill, width=0.6, opacity=alpha)
    return pts


# (cx, cy, rx, ry, layer)
PUFFS = [
    # back layer: the broad bank, coolest and lightest
    (28, 30, 12.0, 6.0, 0), (42, 32, 14.0, 7.0, 0),
    (58, 31, 13.0, 6.5, 0), (72, 33, 11.0, 5.5, 0),
    (50, 24, 18.0, 6.0, 0), (24, 22, 9.0, 4.5, 0),
    (78, 24, 10.0, 5.0, 0),
    # middle layer: the billows
    (34, 36, 9.0, 7.0, 1), (48, 39, 10.0, 8.0, 1),
    (63, 37, 9.5, 7.5, 1), (76, 36, 7.0, 5.0, 1),
    (40, 27, 10.0, 5.5, 1), (60, 27, 9.0, 5.0, 1),
    (51, 33, 11.0, 6.5, 1),
    # front layer: the brightest crowns
    (44, 43, 6.0, 5.0, 2), (57, 44, 5.5, 4.5, 2),
    (50, 45, 7.0, 5.5, 2), (35, 40, 4.5, 3.5, 2),
    (68, 41, 4.5, 3.5, 2),
]


def draw_cloud(c, alpha=1.0, only_layer=None):
    for cx, cy, rx, ry, layer in PUFFS:
        if only_layer is not None and layer != only_layer:
            continue
        if layer == 0:
            fill, a = GRAYS[0], 0.34
        elif layer == 1:
            fill, a = TANS[3], 0.40
        else:
            fill, a = TANS[0], 0.52
        puff(c, cx, cy, rx, ry, fill, a * alpha)


def draw_artwork(c):
    """A placeholder: an arched panel and a figure, in the gray palette."""
    c.poly([(38, 12), (38, 34), (44, 42), (50, 45), (56, 42), (62, 34),
            (62, 12)], fill=GRAYS[1], stroke=GRAYS[2], width=0.8)
    c.poly([(47, 16), (46, 26), (48, 32), (52, 32), (54, 26), (53, 16)],
           fill=GRAYS[2], stroke="none")
    c.dot((50, 35), 3.4, GRAYS[2])
    c.text(50, 9, "artwork (placeholder)", 9, GOLD, "middle")


def fig_veil():
    c = ex.Canvas((0, 100), (0, 70), 760, 540)
    c.poly([(0, 70), (100, 70), (100, 0), (0, 0)], fill=WALL, stroke="none")
    draw_artwork(c)
    draw_cloud(c)
    c.text(3, 66, "cloud over the work: one palette, one veil", 10, GOLD)
    return c.svg("cloud over artwork")


def fig_layers():
    panels = []
    for layer, label in ((0, "back"), (1, "middle"), (2, "front")):
        c = ex.Canvas((0, 100), (0, 60), 760, 190)
        c.poly([(0, 60), (100, 60), (100, 0), (0, 0)], fill=WALL, stroke="none")
        draw_cloud(c, only_layer=layer)
        c.text(3, 56, label, 10, GOLD)
        panels.append((c, 190))
    return ex.stack(panels, width=760, gap=10)


def fig_conics():
    """A circle and the same circle scaled: rays survive the scaling."""
    c = ex.Canvas((0, 100), (0, 60), 760, 380)
    for cx, rx, ry, label in ((25, 18, 18, "circle"), (72, 26, 14, "ellipse")):
        pts = [(float(x), float(y)) for x, y in ellipse(cx, 30, rx, ry)]
        c.poly(pts + [pts[0]], stroke=INK, width=1.4)
        # rays from evenly spaced points on the horizontal diameter
        for t in (-3, -2, -1, 0, 1, 2, 3):
            px = cx + rx * t / 4
            qx = px + rx * (1 - abs(t) / 4) * (1 if t >= 0 else -1)
            c.line((px, 30), (qx, 30 + ry * 0.55), FAINT, 0.9)
        c.text(cx, 8, label, 10, GOLD, "middle")
    c.text(3, 56, "the same points, scaled: exact; rays stay rational",
           10, GOLD)
    return c.svg("circle and ellipse")


# ----------------------------------------------------------------- text ---
def build_blocks():
    blocks = [
        ("h1", "A cloud, for veiling"),
        ("p", "The cathedral has no single artwork problem; it has one per "
              "piece. The proposal here is a veil rather than a repair: take the "
              "photographs, pull them into one palette of light tans and grays, "
              "and put a layered, semi-transparent cloud in front. The cloud is "
              "the constant; the works stay different behind it."),
        ("quote", "The cloud is also a theological choice. At the Transfiguration, "
                  "at the baptism, at the temple when Gabriel spoke, at Fatima, "
                  "the cloud does not explain the action -- it shelters it. What "
                  "is hidden stays God's to reveal."),
        ("p", "This is a study, not a final asset: the geometry is exact, the "
              "opacity is optical, and both are computed below. The palette is "
              "deliberately narrow so that a photograph of any period can be "
              "toned into it."),
        ("table", [["role", "tone", "use"],
                   ["wall", WALL, "the constant ground"],
                   ["back billows", GRAYS[0], "the bank, coolest"],
                   ["middle billows", TANS[3], "volume, warmer"],
                   ["front crowns", TANS[0], "light, catching the top"],
                   ["shadow", GRAYS[2], "the work behind, never black"]]),
        ("fig", fig_veil,
         "Three layers of billows over a placeholder panel: the work stays legible, the edges soften."),
        ("p", "The cloud is built from **exact ellipses**. A circle is a chain "
              "with one triangle angle per chord; scaling it by two rational "
              "radii gives an ellipse whose every point is still rational. So "
              "each billow can be placed on the integer lattice, repeated, "
              "mirrored and stored without a float deciding its edge. What is "
              "not exact is the compositing: the tone and the transparency are "
              "design numbers, not geometry."),
        ("h2", "1. The layers"),
        ("fig", fig_layers,
         "Back, middle and front drawn alone. The veil is their sum, not one shape."),
        ("code", "back     7 puffs, alpha 0.34, gray\n"
                 "middle   7 puffs, alpha 0.40, warm tan\n"
                 "front    5 puffs, alpha 0.52, light tan\n"
                 "overlap  the sum does the softening\n"
                 "edge     a billow is an ellipse, not a blur"),
        ("p", "Drawing the layers separately is the whole method: no single "
              "shape has to look like cloud. The overlap does, and the overlap "
              "is cheap to vary -- move a puff, resize it by a rational, change "
              "one opacity. The same palette then sits over every work in the "
              "building."),

        ("h2", "2. Circles, ellipses, parabolas, hyperbolas"),
        ("fig", fig_conics,
         "A circle and the same circle scaled: both exact, and the rays remain rational under the scale."),
        ("p", "Not all four are the same curve, and it matters which is which. "
              "The chain is built from whole triangle angles, so its exact "
              "members are the circle (constant turn), the straight line (zero "
              "turn), the quarter-turn corner, and the clothoid-like family "
              "where curvature grows linearly. A circle is exact. An ellipse is "
              "exact **as an affine image of a circle** -- scale x by one "
              "rational and y by another and every point stays rational -- but "
              "it is not a Euclidean circle and its curvature is not a clothoid. "
              "A parabola and a hyperbola have no such rational affine origin "
              "here, and no linear-curvature parameterisation; they can only be "
              "approximated, to the lattice's resolution, and the error should "
              "be measured, not assumed."),
        ("p", "The constructive part is real: because the ellipse is a scaled "
              "circle, a circle with rays from its diameter scales into an "
              "ellipse with rays, exactly. That is how the second drawing was "
              "made -- same points, same rational slopes, one rational scale. "
              "For a sunburst, a rose window basis, or a billow with ribs, that "
              "is enough. For a true parabola or hyperbola, use the float path "
              "and report the gap."),

        ("h2", "3. What this is not"),
        ("p", "This framework does not replace the clothoid engine, and it is "
              "not a subset of its curves. Bertolazzi gives real clothoids -- "
              "exact Fresnel geometry, many parameterisations, tolerances. The "
              "chain here is an Euler polygon whose *headings* match a clothoid "
              "at the nodes; its position is up to a chord away, and its "
              "curvature is a staircase. What it adds is the other column: "
              "rational points, rational slopes, exact joins and mirrors, and "
              "a known lattice. The caps in `out/caps` came from the engine and "
              "transfer here by quantising each chord's turn, with a measured "
              "gap. The honest architecture is: engine for the transcendental "
              "curve, chain for the exact plan, and a converter between them."),
        ("h2", "Reproduce"),
        ("code", "cd pythagorean-spiral\n"
                 "../.venv/bin/python scripts/cloud.py\n"
                 "../.venv/bin/python -m unittest discover -s tests -t ."),
    ]
    return blocks


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    blocks = build_blocks()
    names = ["cloud-veil", "cloud-layers", "cloud-conics"]
    figs, fig_names = [], []
    i = 0
    for kind, *rest in blocks:
        if kind != "fig":
            continue
        svg = rest[0]()
        (FIG / f"{names[i]}.svg").write_text(svg + "\n")
        figs.append((svg, names[i]))
        fig_names.append(f"{names[i]}.svg")
        i += 1
    md = ex.to_md(blocks, fig_names)
    (ROOT / "docs" / "CLOUD.md").write_text(md.rstrip() + "\n")
    html = ex.to_html(blocks, figs, "A cloud, for veiling")
    (ROOT / "docs" / "cloud.html").write_text(html + "\n")
    print(f"docs/CLOUD.md, docs/cloud.html, {len(figs)} figures")


if __name__ == "__main__":
    main()
