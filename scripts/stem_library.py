"""A labelled library of stem candidates for the flowers sheet.

    .venv/bin/python scripts/stem_library.py
    open workbench/stem-library.html

Every card is one curve in a tight square, with an S-number and its source.
Nothing here is in a vase and nothing is placed on the print sheet; this is the
catalogue to pick from.  To promote one, add its curve to the STEMS list in
scripts/stems_print.py (or copy the sampled points from the JSON).

Groups:
  generators presets      4
  named curves           25
  Euler                  2   (45 and 90 degrees)
  spiral-turns           3   (r = 5, 17, 28.3)
  log-aesthetic        31   (the recovered LAC spines)
  gestures               4   (catenary, volute, involute, cycloid)
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import euler_square as E  # noqa: E402
import generators as G  # noqa: E402
import spiral_turns as S  # noqa: E402

INK, MUTED, GUIDE = "#2e2413", "#7b6c4e", "#ece4cf"
DOT = "#b23a2b"
SIZE = 170.0
N = 120

CARDS = []


def add(group, name, source, note, branches):
    CARDS.append(dict(group=group, name=name, source=source, note=note,
                      branches=branches))


def figure(branches, size=SIZE):
    pts = [p for br in branches for p in br]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = 0.08
    x0, x1 = x0 - pad * (x1 - x0), x1 + pad * (x1 - x0)
    y0, y1 = y0 - pad * (y1 - y0), y1 + pad * (y1 - y0)
    k = min((size - 16) / (x1 - x0), (size - 16) / (y1 - y0))
    ox, oy = (size - (x1 - x0) * k) / 2, (size - (y1 - y0) * k) / 2

    def put(p):
        return ox + (p[0] - x0) * k, size - (oy + (p[1] - y0) * k)

    body = "".join(
        '<path d="M ' + " L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}"
                                   for p in br) +
        f'" fill="none" stroke="{INK}" stroke-width="1.5" '
        f'stroke-linejoin="round"/>' for br in branches)
    return (f'<svg viewBox="0 0 {size:.0f} {size:.0f}" '
            f'xmlns="http://www.w3.org/2000/svg">'
            f'<rect x="0" y="0" width="{size:.0f}" height="{size:.0f}" '
            f'fill="#fffdf7" stroke="{GUIDE}"/>{body}</svg>')


def preset_branches(spec):
    item = G.build_preset(spec)
    scale = item["scale"]
    pts = [item["curve"].bezier(F(i, N)) for i in range(N + 1)]
    return [[(float(x) * scale, float(y) * scale) for x, y in pts]]


def named_branches(spec):
    data = G.named_data(spec)
    if data["exact"]:
        return [[(float(a), float(b)) for a, b in
                 (G.homog_point(c, F(i, N)) for i in range(N + 1))]
                for c in data["ctrl"]]
    return [[(float(a), float(b)) for a, b in br]
            for br in (data["paths"] or [])]


def lac_branches(spans, per_span=24):
    pts = []
    for span in spans:
        p0, c1 = span["p0"], span["c1"]
        c2, p3 = span["c2"], span["p3"]
        for i in range(per_span):
            t = i / per_span
            mt = 1 - t
            x = (mt ** 3 * p0[0] + 3 * mt * mt * t * c1[0] +
                 3 * mt * t * t * c2[0] + t ** 3 * p3[0])
            y = (mt ** 3 * p0[1] + 3 * mt * mt * t * c1[1] +
                 3 * mt * t * t * c2[1] + t ** 3 * p3[1])
            # the LAC page is y-down; the library figure is y-up
            pts.append((x, -y))
    p3 = spans[-1]["p3"]
    pts.append((p3[0], -p3[1]))
    return [pts]


def build():
    if CARDS:
        return
    # 1. generator presets
    for spec in G.PRESETS:
        add("Generators presets", spec["key"], "generators preset",
            f"n={spec['n']} · h={spec['h']} · u={spec['u']} · v={spec['v']}"
            f" · 1/{spec['m']}", preset_branches(spec))

    # 2. named curves
    for spec in G.NAMED:
        data = G.named_data(spec)
        kind = "exact" if data["exact"] else "sampled"
        add("Named curves", spec["key"], "generators named",
            f"{kind} · {spec.get('eq', '')}"[:120], named_branches(spec))

    # 3. Euler corners
    corner = E.corner()
    add("Euler", "Euler 45°", "euler-square corner",
        "first half of the curvature tent", [corner[:len(corner) // 2 + 1]])
    add("Euler", "Euler 90°", "euler-square corner",
        "full corner, 0→90°", [corner])

    # 4. spiral-turns outward paths
    for radius in (5.0, 17.0, 49.0 / math.sqrt(3.0)):
        pts, heads, turns, gap, infl = S.outward_path(radius, 1.0, 49.0)
        add("Spiral turns", f"spiral r={radius:.1f}", "spiral-turns outward_path",
            f"{turns:.1f} turns · {gap:.0f} pt edge gap"
            + (" · inflection" if infl else ""), [pts])

    # 5. log-aesthetic spines
    lac = json.loads((ROOT / "workbench" / "spirals" / "lac.json")
                     .read_text(encoding="utf-8"))
    for fig in lac["figures"]:
        spine = fig["spines"][0]
        add("Log-aesthetic", f"{fig['figure']} · {fig['title']}",
            "LAC spine", f"{fig['plate']} · {fig['family']}",
            lac_branches(spine["spans"]))

    # 6. gestures
    cat = [(x, math.cosh(x)) for x in
           (-2.0 + 4.0 * i / 240 for i in range(241))]
    add("Gestures", "catenary", "cosh", "a hanging chain, y = cosh x", [cat])

    vol = [(0.12 * math.exp(0.20 * t) * math.cos(t),
            0.12 * math.exp(0.20 * t) * math.sin(t))
           for t in (2.5 * 2 * math.pi * i / 480 for i in range(481))]
    add("Gestures", "volute", "log spiral", "r = a e^{bθ}, 2.5 turns", [vol])

    inv = [(math.cos(t) + t * math.sin(t), math.sin(t) - t * math.cos(t))
           for t in (2.5 * math.pi * i / 480 for i in range(481))]
    add("Gestures", "involute", "circle involute", "x=cos t+t sin t, y=sin t−t cos t",
        [inv])

    cyc = [(t - math.sin(t), 1 - math.cos(t))
           for t in (2 * math.pi * i / 240 for i in range(241))]
    add("Gestures", "cycloid", "cycloid", "one arch", [cyc])


def main():
    build()
    groups = []
    for card in CARDS:
        if not groups or groups[-1][0] != card["group"]:
            groups.append((card["group"], []))
        groups[-1][1].append(card)

    idx = 0
    sections = []
    for group, cards in groups:
        rows = []
        for card in cards:
            idx += 1
            card["index"] = f"S{idx:02d}"
            rows.append(f"""<section class="card">
  <div class="art">{figure(card['branches'])}</div>
  <h3><span class="idx">{card['index']}</span> {card['name']}</h3>
  <p class="src">{card['source']}</p>
  <p class="note">{card['note']}</p>
</section>""")
        sections.append(
            f'<h2 class="group">{group} <span>{len(cards)}</span></h2>'
            f'<div class="grid">{"".join(rows)}</div>')
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Stem library — {len(CARDS)} candidates</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1180px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 20px}}
.group{{font:600 12px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.10em;
text-transform:uppercase;color:{MUTED};margin:32px 0 10px}}
.group span{{color:#b09a6a;font-weight:400}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
.card{{background:#fffdf7;border:1px solid #d8ccae;padding:10px}}
.art{{margin:0 0 8px}}
svg{{display:block;width:100%;height:auto}}
h3{{font:600 12px/1.35 Georgia,serif;margin:0 0 3px}}
.idx{{font:11px ui-monospace,Menlo,monospace;color:{DOT};margin-right:4px}}
.src,.note{{font:10px/1.35 ui-monospace,Menlo,monospace;color:{MUTED};margin:0}}
.note{{color:#a08a64}}
.panel{{background:#fffdf7;border:1px solid #d8ccae;padding:16px 18px;margin:0 0 20px}}
a{{color:{DOT}}}
</style></head><body><main>
<h1>Stem library</h1>
<p class="lead">{len(CARDS)} candidates, one curve per tight square.  Nothing here
is in a vase; this is the catalogue.</p>
<div class="panel">
<p><strong>How to use it.</strong> Every card has an <strong>S-number</strong>
and its source.  Tell the sheet which S-numbers to promote and they can be
moved into <a href="flowers.html">flowers.html</a> with their own vases.  The
curves are drawn at their own scale and orientation; the sheet applies the
rotation, the 7 in (or 60 mm) height and the vase placement.</p>
<p>The four groups with numbers are the two existing sources of exact data
(generators, Euler), the spiral-turns clothoids, the recovered LAC spines, and
four gestures.  The named-curve group is there because a loop or a drop can be
a stem; the LAC group is there because the soft S is the missing middle.</p>
</div>
{''.join(sections)}
</main></body></html>
"""
    out = ROOT / "workbench" / "stem-library.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    print(f"  {len(CARDS)} cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
