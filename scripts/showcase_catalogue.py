"""The full data-driven catalogue for the showcase.

Every panel here comes from a table, never from a remembered shape:

- `generators.NAMED`           25 named curves
- `heart_forms.FORMS`          15 hearts
- `curve_lab.presets.PRESETS`   4 presets
- conics                        4 curves
- `euler_sections.SECTIONS`    10 C-curve sections
- `workbench/spirals/lac.json` 31 recovered LAC spines
- `pyth_cubic.representatives`  11 S + 10 C integer cubics, one per bin

The showcase renders these in rows of three; the notes page reads the same
list, so the figures and their notes cannot disagree.
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import euler_sections as ES  # noqa: E402
import generators as G  # noqa: E402
import heart_forms as H  # noqa: E402
from curve_lab import engine  # noqa: E402
from curve_lab import presets  # noqa: E402
from curve_lab.pyth_cubic import lattice_hits, representatives  # noqa: E402

_REPS = None
from curve_morphs import french_panels, leaf_panels  # noqa: E402

INK, MUTED, GOLD, BLUE = "#2e2413", "#7b6c4e", "#c9a441", "#1f5fa8"


def _named(key, n=240):
    spec = next(s for s in G.NAMED if s["key"] == key)
    data = G.named_data(spec)
    if data["paths"]:
        return spec, [[(float(a), float(b)) for a, b in br]
                      for br in data["paths"]]
    out = []
    for ctrl in data["ctrl"]:
        pts = []
        for i in range(n + 1):
            p = G.homog_point(ctrl, Fraction(i, n))
            if p is not None:
                pts.append((float(p[0]), float(p[1])))
        if len(pts) > 1:
            out.append(pts)
    return spec, out


def _chain_points(design, n=240):
    chain = engine.build(design)
    return [chain.point(chain.length * i / (n - 1)) for i in range(n)]


def _cubic_bezier(row, n=90):
    p0, p1, p2, p3 = row["p0"], row["p1"], row["p2"], row["p3"]
    out = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        out.append((mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0]
                    + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
                    mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1]
                    + 3 * mt * t * t * p2[1] + t ** 3 * p3[1]))
    return out


def _span_points(span, n=18):
    p0, c1, c2, p3 = span["p0"], span["c1"], span["c2"], span["p3"]
    out = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        out.append((mt ** 3 * p0[0] + 3 * mt * mt * t * c1[0]
                    + 3 * mt * t * t * c2[0] + t ** 3 * p3[0],
                    mt ** 3 * p0[1] + 3 * mt * mt * t * c1[1]
                    + 3 * mt * t * t * c2[1] + t ** 3 * p3[1]))
    return out


def _entry(index, title, curves, note, source, dots=(), curve=""):
    return {
        "fig": f"Fig. C{index}", "key": f"c{index:03d}", "title": title,
        "curves": curves, "dots": list(dots), "note": note,
        "source": source, "curve": curve,
    }


def named_panels():
    out = []
    for spec in G.NAMED:
        _, curves = _named(spec["key"])
        out.append(_entry(
            len(out) + 1, spec["key"], [(p, INK, 1.8, None) for p in curves],
            spec["eq"][:54], "scripts/generators.py NAMED",
            curve=spec["key"]))
    return out


def heart_panels():
    out = []
    for form in H.FORMS:
        curves = form["branches"]()
        out.append(_entry(
            len(out) + 1, form["key"], [(p, INK, 1.7, None) for p in curves],
            form["note"][:54], "scripts/heart_forms.py FORMS"))
    return out


def preset_panels():
    out = []
    for name in presets.PRESETS:
        pts = _chain_points(presets.get(name), 220)
        out.append(_entry(
            len(out) + 1, name, [(pts, INK, 2.0, None)],
            "the four named clothoid designs", "curve_lab/presets.py PRESETS"))
    return out


def conic_panels():
    out = []
    circle = [(math.cos(t), math.sin(t))
              for t in [i * 2 * math.pi / 240 for i in range(241)]]
    ellipse = [(1.6 * math.cos(t), math.sin(t))
               for t in [i * 2 * math.pi / 240 for i in range(241)]]
    parabola = [(x, x * x / 2) for x in [(-2.6 + 5.2 * i / 160) for i in range(161)]]
    hyp_r = [(math.cosh(t), math.sinh(t))
             for t in [(-1.9 + 3.8 * i / 160) for i in range(161)]]
    hyp_l = [(-x, y) for x, y in hyp_r]
    for title, curves, note in (
            ("circle", [circle], "x² + y² = 1 · constant curvature"),
            ("ellipse", [ellipse], "x²/1.6² + y² = 1 · rational points"),
            ("parabola", [parabola], "y = x²/2 · integer points"),
            ("hyperbola", [hyp_r, hyp_l], "x² − y² = 1 · two branches")):
        out.append(_entry(len(out) + 1, title,
                          [(p, INK, 1.8, None) for p in curves], note,
                          "curve_lab · conics"))
    return out


def euler_panels():
    out = []
    for name, note, fn, _opts in ES.SECTIONS:
        out.append(_entry(len(out) + 1, name, [(fn(), INK, 1.8, None)],
                          note, "scripts/euler_sections.py SECTIONS"))
    return out


def lac_panels():
    data = json.loads((ROOT / "workbench" / "spirals" / "lac.json").read_text())
    out = []
    for fig in data["figures"]:
        curves = []
        for spine in fig["spines"]:
            pts = []
            for span in spine["spans"]:
                pts.extend(_span_points(span))
            curves.append(pts)
        out.append(_entry(len(out) + 1, f"{fig['plate']} · {fig['title']}",
                          [(p, INK, 1.6, None) for p in curves],
                          f"LAC spine · {fig['family']}",
                          "workbench/spirals/lac.json"))
    return out


def _cubic_turn(row):
    """Turn of the control polygon at P1 (= at P2), in degrees."""
    a, b, c = row["a"], row["b"], row["c"]
    v0 = (a, -b)
    v1 = (c - a, b)
    dot = v0[0] * v1[0] + v0[1] * v1[1]
    return math.degrees(math.acos(max(-1.0, min(1.0,
        dot / (math.hypot(*v0) * math.hypot(*v1))))))


def _cubic_reps():
    """One sampling of each integer-cubic shape family, cached."""
    global _REPS
    if _REPS is None:
        _REPS = representatives()
    return _REPS


def cubic_rows():
    """The 11 S representatives: one per interior-angle bin, shallow to sharp."""
    return sorted(_cubic_reps()["s"], key=_cubic_turn)


def cubic_panels():
    out = []
    for row in cubic_rows():
        curve = _cubic_bezier(row)
        poly = [row["p0"], row["p1"], row["p2"], row["p3"]]
        out.append(_entry(
            len(out) + 1, f"{row['label']} · {row['order']}",
            [(poly, MUTED, 0.9, "4 3"), (curve, INK, 1.6, None)],
            f"chord {row['chord']} · arms ({row['a']}, {row['b']}) · "
            f"interior {180.0 - _cubic_turn(row):.1f}° · "
            f"{len({h['point'] for h in lattice_hits(row, 1)})} integer points",
            "curve_lab/pyth_cubic.py catalogue",
            dots=[(p, GOLD) for p in poly] +
                 [(h["point"], "#b23a2b") for h in lattice_hits(row, 1)]))
    return out


def cubic_c_panels():
    rows = sorted(_cubic_reps()["c"], key=lambda r: r["height"])
    out = []
    for row in rows:
        curve = _cubic_bezier(row)
        poly = [row["p0"], row["p1"], row["p2"], row["p3"]]
        out.append(_entry(
            len(out) + 1, f"{row['label']} · {row['order']}",
            [(poly, MUTED, 0.9, "4 3"), (curve, INK, 1.6, None)],
            f"chord {row['chord']} · arms ({row['a']}, {row['b']}) · "
            f"height {row['height']} · "
            f"{len({h['point'] for h in lattice_hits(row, 1)})} integer points",
            "curve_lab/pyth_cubic.py catalogue_c",
            dots=[(p, GOLD) for p in poly] +
                 [(h["point"], "#b23a2b") for h in lattice_hits(row, 1)]))
    return out


def stem_panels():
    import stem_library as SL
    SL.build()
    out = []
    idx = sm = 0
    for card in SL.CARDS:
        idx += 1
        if card["group"].startswith("Plants"):
            sm += 1
            label = f"SM{sm}"
        else:
            label = f"S{idx:02d}"
        out.append(_entry(
            len(out) + 1, f"{label} · {card['name']}",
            [(p, INK, 1.4, None) for p in card["branches"]],
            card["note"][:54], "scripts/stem_library.py CARDS"))
    return out


def stem_variant_panels():
    """The cuts a stem is actually taken from — one curve each."""
    import stem_variants as SV
    out = []
    for title, pts, note, source in SV.cases():
        out.append(_entry(len(out) + 1, title, [(pts, INK, 1.8, None)], note, source))
    return out


def reuleaux_panels():
    """Constant width: the exact arcs, the Bézier handles, and the Pell limit."""
    import reuleaux as R
    out = []
    for title, pts, note, source in R.cases():
        out.append(_entry(len(out) + 1, title, [(pts, INK, 1.6, None)], note, source))
    return out


def maclaurin_panels():
    """The Maclaurin trisectrix: exact loop at √3, and the Pell copy."""
    import maclaurin as M
    out = []
    for title, pts, note, source in M.cases():
        out.append(_entry(len(out) + 1, title, [(pts, INK, 1.8, None)], note, source))
    return out


def arch_panels():
    """Parts of genus-1+ curves, used as arches."""
    import arches as A
    out = []
    for title, pts, note, source in A.cases():
        out.append(_entry(len(out) + 1, title, [(pts, INK, 1.8, None)], note, source))
    return out


def la_special_panels():
    """The two LA special cases the Gen-Arch dials name."""
    import gen_arch as GA
    out = []
    for title, pts, note, source in GA.special_cases():
        out.append(_entry(len(out) + 1, title, [(pts, INK, 1.8, None)], note, source))
    return out


def drawn_pair_panels():
    """Lissajous, and the yin-yang boundary."""
    import drawn_pairs as D
    out = []
    for title, pts, note, source in D.cases():
        out.append(_entry(len(out) + 1, title, [(pts, INK, 1.6, None)], note, source))
    return out


def ph_quintic_panels():
    """Degree-five PH curves: integer controls after one scale."""
    import ph_quintic as PQ
    out = []
    for title, pts, note, source in PQ.cases():
        out.append(_entry(len(out) + 1, title, [(pts, INK, 1.8, None)], note, source))
    return out


def gen_arch_panels():
    """Gen-Arch: the four classical generalized Archimedean spirals."""
    import gen_arch as GA
    out = []
    for title, pts, note, source in GA.cases():
        out.append(_entry(len(out) + 1, title, [(pts, INK, 1.8, None)], note, source))
    return out


def _billow(c, n=36):
    cx, cy, rx, ry, tilt, layer, power, shape = c
    a = math.radians(tilt)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for i in range(n + 1):
        t = 2.0 * math.pi * i / n
        x = rx * math.cos(t)
        y = ry * math.sin(t)
        pts.append((cx + ca * x - sa * y, cy + sa * x + ca * y))
    return pts


def cloud_panels():
    from curve_lab import spine
    pkg = spine.load()
    from pythagorean_spiral import veil
    layers = ["bank", "billow", "crown", "haze", "light", "shade"]
    out = [_entry(1, "cloud · all billows",
                  [(_billow(c), INK, 0.7, None) for c in veil.BILLOWS],
                  f"{len(veil.BILLOWS)} billows · the whole veil",
                  "pythagorean_spiral/veil.py BILLOWS")]
    for layer in layers:
        curves = [_billow(c) for c in veil.BILLOWS if c[5] == layer]
        out.append(_entry(
            len(out) + 1, f"cloud · {layer}",
            [(p, INK, 0.8, None) for p in curves],
            f"{len(curves)} billows · the {layer} layer",
            "pythagorean_spiral/veil.py BILLOWS"))
    return out


def combined_panels():
    import sys
    sys.path.insert(0, str(ROOT / "pythagorean-spiral" / "scripts"))
    import gallery

    def nodes(spiral):
        return [(float(x), float(y)) for x, y in spiral.nodes]

    out = []
    path, _ = gallery.catenary()
    out.append(_entry(1, "catenary chain", [(nodes(path), INK, 1.6, None)],
                      "the catenary as an exact chord walk",
                      "pythagorean-spiral/scripts/gallery.py catenary()"))
    out.append(_entry(2, "drapery, five ribbons",
                      [(ch, INK, 1.0, None) for ch in gallery.drape()],
                      "five catenary ribbons from one rail",
                      "pythagorean-spiral/scripts/gallery.py drape()"))
    pts, _ = gallery.volute()
    out.append(_entry(3, "Corinthian volute", [(pts, INK, 1.4, None)],
                      "arcs of shrinking chord, joined G1",
                      "pythagorean-spiral/scripts/gallery.py volute()"))
    pts, _ = gallery.violin_scroll()
    out.append(_entry(4, "violin scroll", [(pts, INK, 1.4, None)],
                      "neck, exact quarter cusp, then the scroll",
                      "pythagorean-spiral/scripts/gallery.py violin_scroll()"))
    spine, lobes, _ = gallery.acanthus()
    out.append(_entry(5, "acanthus",
                      [(nodes(spine), INK, 1.6, None)]
                      + [(nodes(l), INK, 1.0, None) for l in lobes],
                      "a spine with paired lobes on exact forks",
                      "pythagorean-spiral/scripts/gallery.py acanthus()"))
    half, base, _ = gallery.fleur()
    out.append(_entry(6, "fleur-de-lis",
                      [(nodes(p), INK, 1.2, None) for p in half + [base]],
                      "three lobed petals and a band",
                      "pythagorean-spiral/scripts/gallery.py fleur()"))
    return out


def primal_panels():
    from curve_lab import primal
    from curve_lab.piece import build_piece

    out = []
    for key, fn in primal.PRIMAL.items():
        groups, _info = build_piece(fn())
        curves = []
        for group in groups:
            pts = []
            for span in group.spans:
                pts.extend(_span_points(span))
            if len(pts) > 1:
                curves.append(pts)
        out.append(_entry(
            len(out) + 1, f"primal · {key}",
            [(p, INK, 1.4, None) for p in curves],
            "one grammar, built from arcs, lines and Euler spans",
            "curve_lab/primal.py PRIMAL"))
    return out


def drapery_panels():
    import sys
    sys.path.insert(0, str(ROOT / "pythagorean-spiral" / "scripts"))
    import gallery
    chains = gallery.drape()
    out = [_entry(1, "drapery · one rail, five ribbons",
                  [(ch, INK, 1.2, None) for ch in chains],
                  "five catenary ribbons hung from one rail",
                  "pythagorean-spiral/scripts/gallery.py drape()")]
    for i, ch in enumerate(chains):
        out.append(_entry(i + 2, f"drapery · ribbon {i + 1}",
                          [(ch, INK, 1.4, None)],
                          "exact offsets, no weft",
                          "pythagorean-spiral/scripts/gallery.py drape()"))
    return out


FAMILIES = [
    ("named", "The named table · 29", "every curve in generators.NAMED", named_panels()),
    ("hearts", "The hearts · 15", "every form in heart_forms.FORMS", heart_panels()),
    ("presets", "The presets · 4", "the four named clothoid designs", preset_panels()),
    ("conics", "The conics · 4", "circle, ellipse, parabola, hyperbola", conic_panels()),
    ("euler", "The Euler sections · 10", "the C-curve table, one section each", euler_panels()),
    ("lac", "The LAC spines · 31", "every recovered spine in lac.json", lac_panels()),
    ("cubics", "The integer cubics · 11",
     "one per interior-angle bin, smallest c in each; the 632-row table of "
     "record is integer-cubic-catalogue.html",
     cubic_panels()),
    ("cubics-c", "The integer C cubics · 10",
     "C-shaped counterparts, one per height/chord bin, smallest c in each",
     cubic_c_panels()),
    ("stems", "The stem library · 181", "every card in the stem catalogue",
     stem_panels()),
    ("french", "French curves · 8",
     "drawing aids, each a chain of three Euler spans", french_panels()),
    ("leaves", "Leaves · 8", "one section mirrored across its own chord",
     leaf_panels()),
    ("clouds", "Clouds · 7", "the whole veil and its six billow layers",
     cloud_panels()),
    ("drapery", "Drapery · 6", "one drape and its five catenary ribbons",
     drapery_panels()),
    ("combined", "Combined curves · 6",
     "the gallery objects: catenary, drapery, volute, violin, acanthus, fleur",
     combined_panels()),
    ("primal", "Primal · 4", "earth, water, air and fire as whole grammars",
     primal_panels()),
    ("stem-variants", "Stem cuts · 66",
     "every LAC spine at 90° and 130° of turn, plus the conic halves and Euler S spans",
     stem_variant_panels()),
    ("gen-arch", "Gen-Arch · 4",
     "the generalized Archimedean spiral: lituus, hyperbolic, Archimedean, Fermat",
     gen_arch_panels()),
    ("constant-width", "Constant width · 3",
     "Reuleaux at 60°: exact arcs, Bézier handles, and the Pell limit",
     reuleaux_panels()),
    ("maclaurin", "Maclaurin · 2",
     "a rational curve whose node sits at t = ±√3: exact loop, and the Pell copy",
     maclaurin_panels()),
    ("arches", "Higher-genus sections · 4",
     "elliptic and Fermat parts: exact at their integer endpoints, declared non-rational",
     arch_panels()),
    ("la-specials", "LA specials · 2",
     "the two LA cases the dials name: α = 3, and Nielsen’s α = 0",
     la_special_panels()),
    ("drawn-pairs", "Drawn pairs · 2",
     "Lissajous 3:2, and the yin-yang boundary as two exact semicircles",
     drawn_pair_panels()),
    ("ph-quintics", "PH quintics · 3",
     "degree five, integer controls after one scale, rational arc length",
     ph_quintic_panels()),
]

CATALOGUE = [panel for _, _, _, panels in FAMILIES for panel in panels]
for _i, _panel in enumerate(CATALOGUE, 1):
    _panel["key"] = f"c{_i:03d}"
    _panel["fig"] = f"Fig. C{_i}"
