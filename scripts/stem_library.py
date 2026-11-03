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

import itertools
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


def add(group, name, source, note, branches, mark=None, colors=None):
    CARDS.append(dict(group=group, name=name, source=source, note=note,
                      branches=branches, mark=mark, colors=colors))


def figure(branches, size=SIZE, mark=None, colors=None):
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
        f'" fill="none" stroke="{colors[i] if colors and i < len(colors) else INK}" '
        f'stroke-width="1.5" stroke-linejoin="round"/>'
        for i, br in enumerate(branches))
    dots = "".join(
        f'<circle cx="{put(p)[0]:.1f}" cy="{put(p)[1]:.1f}" r="2.8" '
        f'fill="#c9a441"/>' for p in (mark or []))
    return (f'<svg viewBox="0 0 {size:.0f} {size:.0f}" '
            f'xmlns="http://www.w3.org/2000/svg">'
            f'<rect x="0" y="0" width="{size:.0f}" height="{size:.0f}" '
            f'fill="#fffdf7" stroke="{GUIDE}"/>{body}{dots}</svg>')


def rotate(points, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [(x * c - y * s, x * s + y * c) for x, y in points]


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


def _rate(p, q, r):
    v1 = (q[0] - p[0], q[1] - p[1])
    v2 = (r[0] - q[0], r[1] - q[1])
    cross = v1[0] * v2[1] - v1[1] * v2[0]
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    ang = abs(math.atan2(cross, dot))
    return ang / max(math.hypot(*v2), 1e-12)


def spiral_end(pts):
    """Which end curls harder: 'start' or 'end'."""
    rs = _rate(pts[0], pts[1], pts[2])
    re = _rate(pts[-3], pts[-2], pts[-1])
    return "start" if rs >= re else "end"


def _arm_to(pts, join_end):
    """Orient so the join is the last point; return (pts, join, tangent)."""
    q = list(pts) if join_end == "end" else list(reversed(pts))
    join = q[-1]
    tan = (q[-1][0] - q[-2][0], q[-1][1] - q[-2][1])
    return q, join, tan


def _arm_from(pts, join_end):
    """Orient so the join is the first point; return (pts, join, tangent)."""
    q = list(pts) if join_end == "start" else list(reversed(pts))
    join = q[0]
    tan = (q[1][0] - q[0][0], q[1][1] - q[0][1])
    return q, join, tan


def join_pair(a, b, variant):
    """Join two LAC cards at their spiral or straight ends, G1 at the join."""
    a_se, b_se = spiral_end(a["branches"][0]), spiral_end(b["branches"][0])
    a_join = a_se if variant == "spiral" else ("end" if a_se == "start" else "start")
    b_join = b_se if variant == "spiral" else ("end" if b_se == "start" else "start")
    a_pts, a_j, a_t = _arm_to(a["branches"][0], a_join)
    b_pts, b_j, b_t = _arm_from(b["branches"][0], b_join)
    ang = math.atan2(a_t[0] * b_t[1] - a_t[1] * b_t[0],
                     a_t[0] * b_t[0] + a_t[1] * b_t[1])
    ca, sa = math.cos(ang), math.sin(ang)
    b_rot = [(b_j[0] + (x - b_j[0]) * ca - (y - b_j[1]) * sa,
              b_j[1] + (x - b_j[0]) * sa + (y - b_j[1]) * ca)
             for x, y in b_pts]
    b_rot = [(x + a_j[0] - b_j[0], y + a_j[1] - b_j[1])
             for x, y in b_rot]
    return a_pts + b_rot[1:]


def plant(group, root_kind, spread=(60.0, 120.0), same_angle=None):
    """One root, several stems: the chosen ends meet at (0,0) and fan out."""
    branches = []
    n = len(group)
    for k, card in enumerate(group):
        pts = card["branches"][0]
        se = spiral_end(pts)
        root_end = se if root_kind == "spiral" else ("end" if se == "start" else "start")
        q, j, t = _arm_from(pts, root_end)
        target = (math.radians(same_angle) if same_angle is not None else
                  math.radians(spread[0] + (spread[1] - spread[0]) * k / max(n - 1, 1)))
        cur = math.atan2(t[1], t[0])
        ang = target - cur
        ca, sa = math.cos(ang), math.sin(ang)
        q_rot = [((x - j[0]) * ca - (y - j[1]) * sa,
                  (x - j[0]) * sa + (y - j[1]) * ca) for x, y in q]
        branches.append(q_rot)
    return branches


def build():
    if CARDS:
        return
    # 1. generator presets
    preset_rot = {"cubic": 45.0, "quintic": 45.0, "sextic": -135.0}
    for spec in G.PRESETS:
        branches = preset_branches(spec)
        note = (f"n={spec['n']} · h={spec['h']} · u={spec['u']} · v={spec['v']}"
                f" · 1/{spec['m']}")
        deg = preset_rot.get(spec["key"], 0.0)
        if deg:
            branches = [rotate(br, deg) for br in branches]
            note += (f" · rotated {abs(deg):g}° " +
                     ("CCW" if deg > 0 else "CW"))
        add("Generators presets", spec["key"], "generators preset",
            note, branches)

    # 2. named curves
    for spec in G.NAMED:
        data = G.named_data(spec)
        kind = "exact" if data["exact"] else "sampled"
        add("Named curves", spec["key"], "generators named",
            f"{kind} · {spec.get('eq', '')}"[:120], named_branches(spec))

    # 3. Euler corners
    corner = E.corner()
    add("Euler", "Euler 45°", "euler-square corner",
        "first half of the curvature tent · rotated 90° CCW",
        [rotate(corner[:len(corner) // 2 + 1], 90.0)])
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
    for i, fig in enumerate(lac["figures"]):
        spine = fig["spines"][0]
        branches = lac_branches(spine["spans"])
        note = f"{fig['plate']} · {fig['family']}"
        if i < 5:                      # S35–S39: rotate 90° CCW
            branches = [rotate(br, 90.0) for br in branches]
            note += " · rotated 90° CCW"
        elif 11 <= i <= 15:            # S46–S50: rotate 180° CCW
            branches = [rotate(br, 180.0) for br in branches]
            note += " · rotated 180° CCW"
        elif 21 <= i <= 25:            # S56–S60: rotate 180° CCW
            branches = [rotate(br, 180.0) for br in branches]
            note += " · rotated 180° CCW"
        add("Log-aesthetic", f"{fig['figure']} · {fig['title']}",
            "LAC spine", note, branches)

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
    add("Gestures", "involute", "circle involute",
        "x=cos t+t sin t, y=sin t−t cos t · rotated 180° CCW",
        [rotate(inv, 180.0)])

    cyc = [(t - math.sin(t), 1 - math.cos(t))
           for t in (2 * math.pi * i / 240 for i in range(241))]
    add("Gestures", "cycloid", "cycloid", "one arch", [cyc])

    # 7. combinations of the first ten LAC cards: S35–S39 and S41–S45
    lac_cards = [c for c in CARDS if c["group"] == "Log-aesthetic"]
    for gname, start, s0 in (("S35–S39", 0, 35), ("S41–S45", 6, 41)):
        group = lac_cards[start:start + 5]
        for i, j in itertools.combinations(range(5), 2):
            for variant in ("spiral", "straight"):
                pts = join_pair(group[i], group[j], variant)
                add(f"Combinations · {gname}", f"S{s0 + i}+S{s0 + j}",
                    "combination",
                    f"{variant} ends joined · G1 at the join", [pts])

    # 8. plants: one root, five stems from a group, fanned 60–120°
    for gname, start, s0 in (("S35–S39", 0, 35), ("S41–S45", 6, 41)):
        group = lac_cards[start:start + 5]
        for root_kind in ("spiral", "straight"):
            branches = plant(group, root_kind)
            add("Plants", f"S{s0}–S{s0 + 4} · {root_kind} root", "plant",
                f"{root_kind} ends at one root · fan 60–120°", branches,
                mark=[(0.0, 0.0)])

    # 9. same-angle overlays: all five leave at 90°, one colour each
    palette = [INK, "#b23a2b", "#1f5fa8", "#2f6f4f", "#6f4a8c"]
    for gname, start, s0 in (("S35–S39", 0, 35), ("S41–S45", 6, 41)):
        group = lac_cards[start:start + 5]
        for root_kind in ("spiral", "straight"):
            branches = plant(group, root_kind, same_angle=90.0)
            add("Plants", f"S{s0}–S{s0 + 4} · {root_kind} root · same angle",
                "plant overlay",
                "all five leave at 90° · colours show the overlap", branches,
                mark=[(0.0, 0.0)], colors=palette)


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
  <div class="art">{figure(card['branches'], mark=card.get('mark'), colors=card.get('colors'))}</div>
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
