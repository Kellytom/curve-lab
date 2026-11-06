"""The full data-driven catalogue for the showcase.

Every panel here comes from a table, never from a remembered shape:

- `generators.NAMED`           25 named curves
- `heart_forms.FORMS`          15 hearts
- `curve_lab.presets.PRESETS`   4 presets
- conics                        4 curves
- `euler_sections.SECTIONS`    10 C-curve sections
- `workbench/spirals/lac.json` 31 recovered LAC spines
- `pyth_cubic.catalogue`      316 integer cubics (arm pairs)

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
from curve_lab.pyth_cubic import catalogue as cubic_catalogue  # noqa: E402
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


def cubic_rows():
    """The catalogue ordered shallow to sharp by control-polygon turn."""
    return sorted(cubic_catalogue(1000), key=_cubic_turn)


def cubic_panels():
    out = []
    for row in cubic_rows():
        curve = _cubic_bezier(row)
        poly = [row["p0"], row["p1"], row["p2"], row["p3"]]
        out.append(_entry(
            len(out) + 1, f"{row['label']} · {row['order']}",
            [(poly, MUTED, 0.9, "4 3"), (curve, INK, 1.6, None)],
            f"chord {row['chord']} · arms ({row['a']}, {row['b']}) · "
            f"interior {180.0 - _cubic_turn(row):.1f}°",
            "curve_lab/pyth_cubic.py catalogue",
            dots=[(p, GOLD) for p in poly]))
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


FAMILIES = [
    ("named", "The named table · 25", "every curve in generators.NAMED", named_panels()),
    ("hearts", "The hearts · 15", "every form in heart_forms.FORMS", heart_panels()),
    ("presets", "The presets · 4", "the four named clothoid designs", preset_panels()),
    ("conics", "The conics · 4", "circle, ellipse, parabola, hyperbola", conic_panels()),
    ("euler", "The Euler sections · 10", "the C-curve table, one section each", euler_panels()),
    ("lac", "The LAC spines · 31", "every recovered spine in lac.json", lac_panels()),
    ("cubics", "The integer cubics · 316",
     "every ordered arm pair, shallow to sharp by control-polygon interior angle",
     cubic_panels()),
    ("stems", "The stem library · 177", "every card in the stem catalogue",
     stem_panels()),
    ("french", "French curves · 8",
     "drawing aids, each a chain of three Euler spans", french_panels()),
    ("leaves", "Leaves · 8", "one section mirrored across its own chord",
     leaf_panels()),
]

CATALOGUE = [panel for _, _, _, panels in FAMILIES for panel in panels]
for _i, _panel in enumerate(CATALOGUE, 1):
    _panel["key"] = f"c{_i:03d}"
    _panel["fig"] = f"Fig. C{_i}"
