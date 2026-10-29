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
PHOTO = ROOT.parent / "reference" / "IMG_5972.JPG"
TONED = FIG / "cloud-photo.png"
RAW = FIG / "cloud-photo-raw.png"
INK, GOLD, RED, BLUE, FAINT = ex.INK, ex.GOLD, ex.RED, ex.BLUE, ex.FAINT

# one palette: light tans and grays, narrow enough to tone any photograph into
WALL = "#e6dbc9"
PALETTE = {
    "wall": WALL,
    "haze": "#ded8cf",
    "bank": "#cfc9bf",
    "billow": "#ddd0bb",
    "crown": "#f2ead9",
    "shadow": "#b7ad9d",
    "cool": "#9aa0a4",
    "cool_dark": "#71777c",
    "warm": "#c3b49b",
    "warm_dark": "#9b8a70",
}


def tone_photo(width=460):
    """Map a photograph onto the palette: luminance in, tan/gray out.

    The value structure is kept and the colour argument is dropped. This is the
    half of the unification that happens before the cloud is drawn.
    """
    from PIL import Image, ImageOps

    stops = [(0, (143, 127, 102)), (128, (195, 180, 155)), (255, (242, 234, 217))]

    def lut(channel):
        table = []
        for v in range(256):
            for (a, ca), (b, cb) in zip(stops, stops[1:]):
                if a <= v <= b:
                    t = (v - a) / (b - a)
                    table.append(round(ca[channel] + t * (cb[channel] - ca[channel])))
                    break
            else:
                table.append(stops[-1][1][channel])
        return table

    im = Image.open(PHOTO).convert("L")
    im = ImageOps.autocontrast(im, cutoff=1)
    im.thumbnail((width, width * 2))
    raw = im.convert("RGB")
    raw.save(RAW)
    rgb = Image.merge("RGB", tuple(im.point(lut(c)) for c in range(3)))
    rgb.save(TONED)
    return rgb.size


def image_at(c, x, y, w, h, href):
    """Place a raster in the canvas's data rectangle, in page coordinates."""
    x0, y0 = c.xy(x, y + h)
    x1, y1 = c.xy(x + w, y)
    c.out.append(f'<image x="{x0:.2f}" y="{y0:.2f}" width="{x1 - x0:.2f}" '
                 f'height="{y1 - y0:.2f}" href="{href}" '
                 f'preserveAspectRatio="xMidYMid slice"/>')
    c.out.append(f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{x1 - x0:.2f}" '
                 f'height="{y1 - y0:.2f}" fill="none" stroke="{INK}" '
                 f'stroke-width="0.8"/>')


def circle_points(per_degree: float = 2.0):
    tri = for_angle(per_degree)
    n = round(360 / tri.degrees)
    path = Spiral(tri, 1, heading=Dir.east())
    path.extend([0] + [1] * (n - 1))
    return path.nodes, tri


CIRCLE, TRI = circle_points()


def billow(c, cx, cy, rx, ry, tilt=0, fill=None, alpha=0.4, edge=0.0):
    """An exact ellipse, tilted by whole triangle angles, with a soft edge."""
    d = place.rotation(TRI, int(tilt))
    pts = []
    for x, y in CIRCLE:
        q = place.rotate((Fraction(rx) * x, Fraction(ry) * y), d)
        pts.append((float(q[0]) + cx, float(q[1]) + cy))
    if edge:
        c.poly(pts + [pts[0]], fill=fill, stroke=fill, width=edge,
               opacity=alpha * 0.55)
    c.poly(pts + [pts[0]], fill=fill, stroke=fill, width=0.6, opacity=alpha)
    return pts


# (cx, cy, rx, ry, tilt in triangle steps, layer)
CLOUD = [
    # haze: the outer breath, almost no edge
    (10, 33, 12, 6, 3, "haze"),
    (66, 30, 16, 5, -4, "haze"),
    (113, 36, 10, 7, 2, "haze"),
    (24, 55, 9, 6, 5, "haze"),
    # bank: the heavy base, coolest
    (22, 37, 16, 8, 2, "bank"),
    (42, 35, 18, 9, -2, "bank"),
    (64, 36, 20, 9, 1, "bank"),
    (87, 37, 17, 8, -3, "bank"),
    (104, 35, 12, 7, 4, "bank"),
    # billows: the volume, warmer
    (25, 45, 12, 10, -6, "billow"),
    (45, 47, 14, 11, 4, "billow"),
    (66, 49, 15, 13, -3, "billow"),
    (88, 46, 12, 10, 6, "billow"),
    (103, 44, 8, 8, -5, "billow"),
    # crowns: the lit tops
    (34, 56, 8, 7, 7, "crown"),
    (54, 59, 9, 8, -5, "crown"),
    (73, 61, 9, 8, 3, "crown"),
    (91, 56, 7, 6, -6, "crown"),
]

LAYER = {"haze": 0.16, "bank": 0.40, "billow": 0.44, "crown": 0.56}


def draw_cloud(c, only=None, veil=1.0):
    for cx, cy, rx, ry, tilt, layer in CLOUD:
        if only is not None and layer != only:
            continue
        billow(c, cx, cy, rx, ry, tilt, PALETTE[layer],
               LAYER[layer] * veil, edge=3.2)


def draw_work(c, cx, base_y, kind, toned):
    """A framed painting or a statue, in a cool or a warm tone."""
    light = PALETTE["warm"] if toned else PALETTE["cool"]
    dark = PALETTE["warm_dark"] if toned else PALETTE["cool_dark"]
    if kind == "painting":
        c.poly([(cx - 13, base_y), (cx - 13, base_y + 26),
                (cx + 13, base_y + 26), (cx + 13, base_y)], fill=light,
               stroke=dark, width=1.0)
        c.poly([(cx - 10, base_y + 3), (cx - 10, base_y + 22),
                (cx + 10, base_y + 22), (cx + 10, base_y + 3)], fill=dark,
               stroke="none", opacity=0.55)
        c.dot((cx, base_y + 18), 2.6, light)
        c.poly([(cx - 3.4, base_y + 14), (cx - 2.4, base_y + 5),
                (cx + 2.4, base_y + 5), (cx + 3.4, base_y + 14)],
               fill=light, stroke="none", opacity=0.85)
    else:
        c.poly([(cx - 8, base_y), (cx - 8, base_y + 4), (cx + 8, base_y + 4),
                (cx + 8, base_y)], fill=dark, stroke="none")
        c.poly([(cx - 4.4, base_y + 4), (cx - 3.0, base_y + 15),
                (cx - 2.2, base_y + 22), (cx + 2.2, base_y + 22),
                (cx + 3.0, base_y + 15), (cx + 4.4, base_y + 4)],
               fill=light, stroke=dark, width=0.5)
        c.dot((cx, base_y + 23.6), 2.2, light)


def fig_tone(size):
    pw, ph = size
    aspect = pw / ph
    rows = []
    for href, label in ((RAW, "as photographed: value kept, colour dropped"),
                        (TONED, "toned: the one palette")):
        c = ex.Canvas((0, 120), (0, 52), 760, 300)
        c.poly([(0, 52), (120, 52), (120, 0), (0, 0)], fill=WALL, stroke="none")
        h = 40
        image_at(c, 20, 5, h * aspect, h, f"fig/{Path(href).name}")
        c.text(3, 49, label, 10, GOLD)
        c.text(56, 26, "one work, two treatments", 10, GOLD)
        rows.append((c, 300))
    return ex.stack(rows, width=760, gap=8)


def fig_veil(size):
    pw, ph = size
    aspect = pw / ph
    c = ex.Canvas((0, 120), (0, 78), 800, 560)
    c.poly([(0, 78), (120, 78), (120, 0), (0, 0)], fill=WALL, stroke="none")
    h = 30
    image_at(c, 22, 3, h * aspect, h, f"fig/{Path(TONED).name}")
    draw_work(c, 84, 4, "statue", True)
    c.poly([(6, 0), (6, 12), (114, 12), (114, 0)], fill=PALETTE["shadow"],
           stroke="none", opacity=0.35)
    draw_cloud(c)
    c.text(3, 74, "one veil over a photograph and a statue: the constant is the cloud",
           10, GOLD)
    return c.svg("cloud over two works")


def fig_layers():
    panels = []
    for key in ("haze", "bank", "billow", "crown"):
        c = ex.Canvas((0, 120), (0, 70), 760, 210)
        c.poly([(0, 70), (120, 70), (120, 0), (0, 0)], fill=WALL, stroke="none")
        draw_cloud(c, only=key)
        c.text(3, 66, f"{key}  alpha {LAYER[key]}", 10, GOLD)
        panels.append((c, 210))
    return ex.stack(panels, width=760, gap=8)


def fig_conics():
    c = ex.Canvas((0, 100), (0, 60), 760, 380)
    for cx, rx, ry, label in ((25, 18, 18, "circle"), (72, 26, 14, "ellipse")):
        pts = []
        for x, y in CIRCLE:
            pts.append((float(Fraction(rx) * x) + cx,
                        float(Fraction(ry) * y) + 30))
        c.poly(pts + [pts[0]], stroke=INK, width=1.4)
        for t in (-3, -2, -1, 0, 1, 2, 3):
            px = cx + rx * t / 4
            qx = px + rx * (1 - abs(t) / 4) * (1 if t >= 0 else -1)
            c.line((px, 30), (qx, 30 + ry * 0.55), FAINT, 0.9)
        c.text(cx, 8, label, 10, GOLD, "middle")
    c.text(3, 56, "the same points, scaled: exact; rays stay rational", 10, GOLD)
    return c.svg("circle and ellipse")


# ----------------------------------------------------------------- text ---
def build_blocks(photo_size):
    blocks = [
        ("h1", "A cloud, for veiling"),
        ("p", "The cathedral has no single artwork problem; it has one per "
              "piece. The proposal is a veil rather than a repair: tone the "
              "photographs into one palette of light tans and grays, and put a "
              "layered, semi-transparent cloud in front. The cloud is the "
              "constant; the works stay different behind it."),
        ("quote", "The cloud is also a theological choice. At the Transfiguration, "
                  "at the baptism, at the temple when Gabriel spoke, at Fatima, "
                  "the cloud does not explain the action -- it shelters it. What "
                  "is hidden stays God's to reveal."),
        ("table", [["role", "tone", "use"],
                   ["wall", PALETTE["wall"], "the constant ground"],
                   ["haze", PALETTE["haze"], "outer breath, alpha 0.16"],
                   ["bank", PALETTE["bank"], "the heavy base, alpha 0.40"],
                   ["billow", PALETTE["billow"], "volume, alpha 0.44"],
                   ["crown", PALETTE["crown"], "lit tops, alpha 0.56"],
                   ["shadow", PALETTE["shadow"], "under the cloud, never black"]]),
        ("h2", "1. Tone first, then veil"),
        ("fig", lambda: fig_tone(photo_size),
         "One photograph: value kept, colour dropped, then mapped onto the palette."),
        ("p", "Tone is the first half of the unification and the cloud is the "
              "second. The photograph here is `reference/IMG_5972.JPG`, reduced "
              "to luminance and mapped onto the ramp above; the value structure "
              "stays, the colour argument goes. "
              "Two works of different periods then sit in the same room before "
              "the cloud is even drawn. The cloud hides the remaining seams -- "
              "the edges, the varnish, the reproduction -- rather than the "
              "subjects."),
        ("p", "This is deliberately unheroic: no restoration, no repainting, no "
              "claim that the works match. They do not, and the veil says so "
              "honestly by being visible."),

        ("h2", "2. The veil"),
        ("fig", lambda: fig_veil(photo_size),
         "Four layers of billows over a toned photograph and a toned statue: the works stay legible, the edges soften."),
        ("p", "The cloud is built from **exact ellipses**. A circle is a chain "
              "with one triangle angle per chord; scaling it by two rational "
              "radii and turning it by whole triangle angles gives an ellipse "
              "whose every point is still rational. So each billow can be "
              "placed on the integer lattice, repeated, mirrored and stored "
              "without a float deciding its edge. What is not exact is the "
              "compositing: tone and transparency are design numbers, not "
              "geometry."),
        ("code", "layers   4   haze 0.16, bank 0.40, billow 0.44, crown 0.56\n"
                 "puffs    18  ellipses, tilted by whole triangle angles\n"
                 "edge     a wider translucent stroke, same colour\n"
                 "overlap  the sum does the softening\n"
                 "geometry exact; opacity and tone are choices"),
        ("h2", "3. The layers"),
        ("fig", fig_layers,
         "Haze, bank, billow and crown drawn alone. No single shape is a cloud; their sum is."),
        ("p", "Drawing the layers separately is the whole method: the base is "
              "cool and heavy, the volume warmer, the crowns light. Move one "
              "puff, resize it by a rational, change one opacity -- the cloud "
              "changes without any retouching. The same palette then sits over "
              "every work in the building."),
        ("p", "Two variants are worth keeping. A **cumulus** (above) has a flat "
              "base and a domed top; an **incense** cloud is taller, thinner and "
              "more transparent, with vertical drift, and is better for a side "
              "chapel or a shrine where the veil should rise rather than rest. "
              "Both use the same palette and the same ellipses; only the layout "
              "and the opacities differ."),

        ("h2", "4. Circles, ellipses, parabolas, hyperbolas"),
        ("fig", fig_conics,
         "A circle and the same circle scaled: both exact, and the rays remain rational under the scale."),
        ("p", "Not all four are the same curve, and it matters which is which. "
              "The chain is built from whole triangle angles, so its exact "
              "members are the circle (constant turn), the straight line (zero "
              "turn), the quarter-turn corner, and the clothoid-like family "
              "where curvature grows linearly. A circle is exact. An ellipse is "
              "exact **as an affine image of a circle** -- scale x by one "
              "rational and y by another, and every point stays rational -- but "
              "it is not a Euclidean circle and its curvature is not a clothoid. "
              "A parabola and a hyperbola have no such rational affine origin "
              "here, and no linear-curvature parameterisation; they can only be "
              "approximated, to the lattice's resolution, and the error should "
              "be measured rather than assumed."),
        ("p", "The constructive part is real: because the ellipse is a scaled "
              "circle, a circle with rays from its diameter scales into an "
              "ellipse with rays, exactly. That is how the second drawing was "
              "made -- same points, same rational slopes, one rational scale. "
              "For a sunburst, a rose-window basis, or a billow with ribs, that "
              "is enough. For a true parabola or hyperbola, use the float path "
              "and report the gap."),

        ("h2", "5. What this is not"),
        ("p", "This framework does not replace the clothoid engine, and it is "
              "not a subset of its curves. Bertolazzi gives real clothoids -- "
              "exact Fresnel geometry, many parameterisations, tolerances. The "
              "chain here is an Euler polygon whose *headings* match a clothoid "
              "at the nodes; its position is up to a chord away, and its "
              "curvature is a staircase. What it adds is the other column: "
              "rational points, rational slopes, exact joins and mirrors, and a "
              "known lattice. The caps in `out/caps` came from the engine and "
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
    size = tone_photo()
    blocks = build_blocks(size)
    names = ["cloud-tone", "cloud-veil", "cloud-layers", "cloud-conics"]
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
