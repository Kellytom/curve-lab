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
import cloud_form as cf  # noqa: E402

FIG = ex.FIG
REF = ROOT.parent / "reference"
RAW = FIG / "cloud-photo-raw.png"
STATUE = FIG / "cloud-photo-statue.png"
FRESCO = FIG / "cloud-photo-fresco.png"
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

STOPS = [(0, (143, 127, 102)), (128, (195, 180, 155)), (255, (242, 234, 217))]


def circle_points(per_degree: float = 2.0):
    tri = for_angle(per_degree)
    n = round(360 / tri.degrees)
    path = Spiral(tri, 1, heading=Dir.east())
    path.extend([0] + [1] * (n - 1))
    return path.nodes, tri


CIRCLE, TRI = circle_points()
STATUE_SIZE = (940, 1185)
VEIL_TARGET = 0.9


def tone_photo(src: Path, out: Path, width=460):
    """Map a photograph onto the palette: luminance in, tan/gray out."""
    from PIL import Image, ImageOps

    def lut(channel):
        table = []
        for v in range(256):
            for (a, ca), (b, cb) in zip(STOPS, STOPS[1:]):
                if a <= v <= b:
                    t = (v - a) / (b - a)
                    table.append(round(ca[channel] + t * (cb[channel] - ca[channel])))
                    break
            else:
                table.append(STOPS[-1][1][channel])
        return table

    im = Image.open(src).convert("L")
    im = ImageOps.autocontrast(im, cutoff=1)
    im.thumbnail((width, width * 2))
    rgb = Image.merge("RGB", tuple(im.point(lut(c)) for c in range(3)))
    rgb.save(out)
    return rgb.size


def raw_photo(src: Path, out: Path, width=460):
    from PIL import Image, ImageOps
    im = Image.open(src).convert("L")
    im = ImageOps.autocontrast(im, cutoff=1)
    im.thumbnail((width, width * 2))
    im.convert("RGB").save(out)
    return im.size


def image_at(c, x, y, w, h, href):
    x0, y0 = c.xy(x, y + h)
    x1, y1 = c.xy(x + w, y)
    c.out.append(f'<image x="{x0:.2f}" y="{y0:.2f}" width="{x1 - x0:.2f}" '
                 f'height="{y1 - y0:.2f}" href="{href}" '
                 f'preserveAspectRatio="xMidYMid slice"/>')
    c.out.append(f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{x1 - x0:.2f}" '
                 f'height="{y1 - y0:.2f}" fill="none" stroke="{INK}" '
                 f'stroke-width="0.7"/>')


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


# a cumulus: a tower with shaded lobes, not a band
CLOUD = [
    # haze: the outer breath
    (24, 39, 6, 4, -4, "haze"), (90, 40, 5, 4, 3, "haze"),
    (30, 36, 5, 3.5, 5, "haze"),
    (40, 71, 4, 3.5, 5, "haze"), (70, 68, 4, 3.5, -5, "haze"),
    # base: the flat underside
    (38, 34, 9, 4.5, 2, "bank"), (52, 38, 11, 4.5, -1, "bank"),
    (66, 36, 9, 4.5, 3, "bank"), (79, 41, 7, 4, -3, "bank"),
    # the veil down over the works, so the whole image is covered
    (24, 20, 9, 6, -3, "bank"), (42, 18, 11, 6, 3, "bank"),
    (60, 19, 11, 6, -2, "bank"), (78, 21, 9, 6, 4, "bank"),
    (32, 27, 10, 8, -5, "billow"), (50, 29, 11, 9, 4, "billow"),
    (68, 28, 10, 9, -3, "billow"), (84, 30, 8, 7, 5, "billow"),
    # only the bottom layer reaches the work; the upper layers stay above it
    (36, 8, 10, 4.5, -2, "bank"), (56, 7, 11, 4.5, 3, "bank"),
    (76, 8, 10, 4.5, -3, "bank"),
    # lower lobes
    (36, 42, 10, 8, -5, "billow"), (50, 44, 12, 9, 3, "billow"),
    (65, 43, 10, 8, -4, "billow"), (79, 41, 7, 6, 5, "billow"),
    # middle
    (42, 52, 8, 7, 4, "billow"), (56, 55, 9, 8, -3, "billow"),
    (70, 52, 7, 7, 5, "billow"),
    # upper and crown
    (48, 62, 6, 6, -4, "crown"), (60, 63, 6, 6, 3, "crown"),
    (54, 69, 5, 4.5, -3, "crown"),
]

VEIL = 0.14  # solved at run time: see solve_veil()
LAYER = {"haze": 0.14, "bank": 0.34, "billow": 0.46, "crown": 0.60}
_FILTER = [0]


def _inside(cx, cy, rx, ry, tilt, x, y):
    """Is (x,y) inside the tilted ellipse? Whole triangle angles for tilt."""
    a = math.radians(tilt * TRI.degrees)
    dx, dy = x - cx, y - cy
    u = dx * math.cos(a) + dy * math.sin(a)
    v = -dx * math.sin(a) + dy * math.cos(a)
    return (u / rx) ** 2 + (v / ry) ** 2 <= 1.0


def veil_opacity(x, y, veil=None):
    """Composited alpha of every billow covering a point, at a veil setting."""
    v = VEIL if veil is None else veil
    a = 0.0
    for cx, cy, rx, ry, tilt, layer in CLOUD:
        if _inside(cx, cy, rx, ry, tilt, x, y):
            a = a + (1 - a) * LAYER[layer] * v
    return a


def artwork_worst_opacity(veil=None, size=None):
    """The most opaque point over the works: the veil is judged there."""
    pw, ph = size or (STATUE_SIZE[0], STATUE_SIZE[1])
    aspect = pw / ph
    hs = 32.0
    aw = hs * aspect
    xs = [16 + aw * i / 12 for i in range(13)] + [100 - aw + aw * i / 12
                                                  for i in range(13)]
    ys = [10 + hs * j / 12 for j in range(13)]
    return max(veil_opacity(x, y, veil) for x in xs for y in ys)


def solve_veil(target_contrast=0.95):
    """The veil setting whose worst artwork point keeps the total under limit.

    The bottom layer is the veil; the upper layers are kept off the work, so
    the sampled opacity there is the bottom layer's alone. Bisection, because
    the opacity is monotone in the veil.
    """
    limit = 1.0 - target_contrast
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if artwork_worst_opacity(mid) > limit:
            hi = mid
        else:
            lo = mid
    return lo


def _cloud_filter(c, scale=8, blur=6):
    """A displacement filter: the geometry stays ellipses, the edge is air."""
    _FILTER[0] += 1
    fid = f"cloud{_FILTER[0]}"
    c.out.append(
        f'<defs><filter id="{fid}" x="-50%" y="-50%" width="200%" '
        f'height="200%"><feTurbulence type="fractalNoise" '
        f'baseFrequency="0.012 0.02" numOctaves="3" seed="7" result="noise"/>'
        f'<feDisplacementMap in="SourceGraphic" in2="noise" scale="{scale}" '
        f'xChannelSelector="R" yChannelSelector="G" result="air"/>'
        f'<feGaussianBlur in="air" stdDeviation="{blur}"/></filter></defs>')
    return fid


def draw_cloud(c, only=None, veil=1.0, drop=0.0):
    # a soft shadow where the mass meets the air, biased under the crown
    if only is None:
        c.poly([(22, 34), (48, 31), (74, 32), (96, 35), (88, 30), (42, 29)],
               fill=PALETTE["shadow"], stroke="none", opacity=0.13 * veil)
    cy = 0
    fid = _cloud_filter(c)
    c.out.append(f'<g filter="url(#{fid})">')
    for cx, cy, rx, ry, tilt, layer in CLOUD:
        if only is not None and layer != only:
            continue
        if layer in ("billow", "crown") and only is None:
            # undersides give the lobes their edges even where the silhouette
            # is smooth: a cloud reads by shading, not by outline
            billow(c, cx + 1.8, cy - drop - 3.4, rx * 1.02, ry * 0.92, tilt,
                   PALETTE["warm_dark"], 0.12 * veil)
            billow(c, cx - 1.4, cy - drop + 2.6, rx * 0.84, ry * 0.78, tilt,
                   "#fbf6ea", 0.16 * veil)
        # only the bottom layer is the veil and carries the veil factor; the
        # upper layers keep their body because they never reach the work
        alpha = LAYER[layer] * (VEIL if layer == "bank" else 1.0)
        billow(c, cx, cy - drop, rx, ry, tilt, PALETTE[layer],
               alpha * veil, edge=2.6)
    c.out.append('</g>')


def draw_statue(c, cx, base_y):
    """A robed figure on a plinth, in the warm tone."""
    light, dark = PALETTE["warm"], PALETTE["warm_dark"]
    c.poly([(cx - 7, base_y), (cx + 7, base_y), (cx + 7, base_y + 3),
            (cx - 7, base_y + 3)], fill=dark, stroke="none")
    c.poly([(cx - 3.6, base_y + 3), (cx - 4.2, base_y + 16),
            (cx - 2.6, base_y + 24), (cx + 2.6, base_y + 24),
            (cx + 4.2, base_y + 16), (cx + 3.6, base_y + 3)],
           fill=light, stroke=dark, width=0.6)
    c.line((cx - 1.0, base_y + 6), (cx - 1.6, base_y + 20), dark, 0.6)
    c.dot((cx, base_y + 26), 2.3, light, dark, 0.5)


def fig_tone(sizes):
    rows = []
    for src, label in ((RAW, "as photographed: value kept, colour dropped"),
                       (STATUE, "toned: the one palette")):
        w, h = sizes[src]
        aspect = w / h
        c = ex.Canvas((0, 120), (0, 54), 760, 320)
        c.poly([(0, 54), (120, 54), (120, 0), (0, 0)], fill=WALL, stroke="none")
        hh = 42
        image_at(c, 22, 5, hh * aspect, hh, f"fig/{src.name}")
        c.text(3, 51, label, 10, GOLD)
        c.text(58, 22, "one work, two treatments", 10, GOLD)
        c.text(58, 17, "the cloud in the next figure sits over both",
               9, PALETTE["warm_dark"])
        rows.append((c, 320))
    return ex.stack(rows, width=760, gap=8)


def fig_veil(sizes):
    c = ex.Canvas((0, 120), (0, 80), 800, 560)
    c.poly([(0, 80), (120, 80), (120, 0), (0, 0)], fill=WALL, stroke="none")
    hs = 32
    aw = hs * sizes[STATUE][0] / sizes[STATUE][1]
    bw = hs * sizes[FRESCO][0] / sizes[FRESCO][1]
    image_at(c, 16, 10, aw, hs, f"fig/{STATUE.name}")
    image_at(c, 100 - bw, 10, bw, hs, f"fig/{FRESCO.name}")
    draw_cloud(c)
    return c.svg("cloud over two works")


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
def build_blocks(sizes):
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
                   ["haze", PALETTE["haze"], f"outer breath, alpha {LAYER['haze'] * VEIL:.2f}"],
                   ["bank", PALETTE["bank"], f"the flat base, alpha {LAYER['bank'] * VEIL:.2f}"],
                   ["billow", PALETTE["billow"], f"volume, alpha {LAYER['billow'] * VEIL:.2f}"],
                   ["crown", PALETTE["crown"], f"lit tops, alpha {LAYER['crown'] * VEIL:.2f}"],
                   ["shadow", PALETTE["shadow"], "under the mass, never black"]]),
        ("h2", "1. Tone first, then veil"),
        ("fig", lambda: fig_tone(sizes),
         "One photograph: value kept, colour dropped, then mapped onto the palette."),
        ("p", "Tone is the first half of the unification and the cloud is the "
              "second. The photograph here is `reference/IMG_5972.JPG`, reduced "
              "to luminance and mapped onto the ramp above; the value structure "
              "stays, the colour argument goes. Two works of different periods "
              "then sit in the same room before the cloud is even drawn. The "
              "cloud hides the remaining seams -- the edges, the varnish, the "
              "reproduction -- rather than the subjects."),
        ("p", "This is deliberately unheroic: no restoration, no repainting, no "
              "claim that the works match. They do not, and the veil says so "
              "honestly by being visible."),

        ("h2", "2. The veil"),
        ("fig", lambda: fig_veil(sizes),
         "Four layers of billows over a toned statue and a toned fresco: the works stay legible, the edges soften."),
        ("p", "The cloud is built from **exact ellipses**. A circle is a chain "
              "with one triangle angle per chord; scaling it by two rational "
              "radii and turning it by whole triangle angles gives an ellipse "
              "whose every point is still rational. So each billow can be "
              "placed on the integer lattice, repeated, mirrored and stored "
              "without a float deciding its edge. What is not exact is the "
              "compositing: tone and transparency are design numbers, not "
              "geometry."),
        ("code", f"layers   4   haze {LAYER['haze']}, bank {LAYER['bank']}, "
                 f"billow {LAYER['billow']}, crown {LAYER['crown']}\n"
                 f"puffs    {len(CLOUD)}  ellipses, tilted by whole triangle angles\n"
                 "edge     fractal displacement + gaussian blur, optical only\n"
                 f"veil     {VEIL:.2f}, solved to keep "
                 f"{VEIL_TARGET:.0%} of the works' contrast\n"
                 "overlap  the sum does the softening\n"
                 "geometry exact; opacity and tone are choices"),
        ("p", "Two variants are worth keeping. A **cumulus** (above) has a flat "
              "base and a domed top. An **incense** cloud is taller, thinner and "
              "more transparent, with vertical drift; it is the better veil for "
              "a side chapel or a shrine, where the cloud should rise in front "
              "of the work rather than rest above it. Both are the same palette "
              "and the same ellipses -- only the layout and the opacities "
              "differ."),

        ("h2", "3. Circles, ellipses, parabolas, hyperbolas"),
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

        ("h2", "4. The clothoid-like cloud, in four arcs"),
        ("p", "The simplest form is not a mass of puffs but four arcs: two big "
              "ones under the cloud, turning upward and meeting at (0,0); two "
              "half-size ones on top, turning downward and meeting near "
              "(0,200). Plotted with the stated centres, the form does not "
              "close -- the bottom circles are centred at (120,120) and "
              "(-120,120) with radius 169.7, the top at (60,180) and (-60,180) "
              "with radius 63.2, and the right-hand pair is nested by 21.6, so "
              "there is no side joint."),
        ("fig", cf.fig_literal,
         "The four arcs as stated, with centres and the two meeting points."),
        ("p", "Moving the bottom centres in to (100,100) fixes it more neatly "
              "than a side crossing would: the bottom radius becomes 141.4, "
              "which is also the distance to (0,200), so the bottom pair passes "
              "through both (0,0) and (0,200) -- and the top pair already passes "
              "through (0,200). That is the common point, and the cloud closes "
              "there. Two numbers remain: the big lobes reach x = 241 (about "
              "twice the intended width), and the tangent at (0,200) is G0, not "
              "G1, so the next tune is one centre and one tangent."),
        ("fig", cf.fig_adjusted,
         "Bottom centres at (100,100): all four arcs meet at (0,200)."),
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


def prepare():
    sizes = {}
    sizes[RAW] = raw_photo(REF / "IMG_5972.JPG", RAW)
    sizes[STATUE] = tone_photo(REF / "IMG_5972.JPG", STATUE)
    sizes[FRESCO] = tone_photo(REF / "IMG_5975.JPG", FRESCO)
    return sizes


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    sizes = prepare()
    global VEIL
    import sys as _sys
    global VEIL_TARGET
    VEIL_TARGET = float(_sys.argv[1]) if len(_sys.argv) > 1 else 0.9
    VEIL = solve_veil(VEIL_TARGET)
    print(f"veil {VEIL:.3f}  worst artwork opacity "
          f"{artwork_worst_opacity(VEIL):.3f}  contrast kept {1 - artwork_worst_opacity(VEIL):.2f}")
    blocks = build_blocks(sizes)
    names = ["cloud-tone", "cloud-veil", "cloud-conics",
             "cloud-form-stated", "cloud-form-adjusted"]
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
    import json
    settings = {
        "veil_transparency": VEIL,
        "canvas": [120, 80],
        "palette": PALETTE,
        "layers": {k: round(v * VEIL, 4) for k, v in LAYER.items()},
        "blobs": [{"x": x, "y": y, "rx": rx, "ry": ry, "tilt": t, "layer": l}
                  for x, y, rx, ry, t, l in CLOUD],
        "filter": {"displacement": 8, "blur": 6},
        "works": {"statue": "reference/IMG_5972.JPG",
                  "fresco": "reference/IMG_5975.JPG"},
    }
    (ROOT / "docs" / "veil-settings.json").write_text(
        json.dumps(settings, indent=1) + "\n")
    print(f"docs/CLOUD.md, docs/cloud.html, docs/veil-settings.json, {len(figs)} figures")


if __name__ == "__main__":
    main()
