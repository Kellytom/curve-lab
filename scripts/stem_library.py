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
from grid_view import MARK, best_step, crossings, grid_lines, nice_step  # noqa: E402

INK, MUTED, GUIDE = "#2e2413", "#7b6c4e", "#ece4cf"
DOT = "#b23a2b"
SIZE = 170.0
N = 120

CARDS = []

ENDING = {"spiral": "spiral ending", "straight": "straight stalk"}


def add(group, name, source, note, branches, mark=None, colors=None,
        legend=None):
    CARDS.append(dict(group=group, name=name, source=source, note=note,
                      branches=branches, mark=mark, colors=colors,
                      legend=legend))


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
    step = best_step(branches, max(x1 - x0, y1 - y0))
    grid = "".join(grid_lines(put, x0, x1, y0, y1, step, GUIDE))
    lattice = "".join(
        f'<circle class="lattice" cx="{put(p)[0]:.1f}" '
        f'cy="{put(p)[1]:.1f}" r="2.0" fill="{MARK}"/>'
        for p in crossings(branches, step))
    dots = "".join(
        f'<circle cx="{put(p)[0]:.1f}" cy="{put(p)[1]:.1f}" r="2.8" '
        f'fill="#c9a441"/>' for p in (mark or []))
    return (f'<svg viewBox="0 0 {size:.0f} {size:.0f}" '
            f'xmlns="http://www.w3.org/2000/svg">'
            f'<rect x="0" y="0" width="{size:.0f}" height="{size:.0f}" '
            f'fill="#fffdf7" stroke="{GUIDE}"/>{grid}{body}{lattice}{dots}</svg>')


def bbox_size(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return math.hypot(max(xs) - min(xs), max(ys) - min(ys)) or 1.0


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


def lac_p_branches(p, turn_deg=360.0, n=480):
    """One LAC from the law κ = C(a+s)^p, in the recovered LAC page frame.

    The recovered p>0 plates all start at (420,780), head -90° and run from
    curvature 1/640 to 1/80 over the requested turn.  The library flips the
    y-down page frame, as it does for the recovered spans.
    """
    turn = math.radians(turn_deg)
    k0, k1 = 1.0 / 640.0, 1.0 / 80.0
    if p < 0:
        k0, k1 = k1, k0
    if abs(p) < 1e-12:
        k0 = k1 = 1.0 / 80.0
    if abs(p) < 1e-12:
        a, L, C = 0.0, abs(turn / k1), k1
    elif abs(k0) < 1e-12:
        L = turn * (p + 1) / k1
        a, C = 0.0, k1 / L ** p
    else:
        ratio = (k1 / k0) ** (1.0 / p)
        if abs(p + 1) < 1e-9:
            a = turn / (k0 * math.log(ratio))
            L = a * (ratio - 1)
            C = k0 * a
        else:
            a = turn * (p + 1) / (k0 * (ratio ** (p + 1) - 1))
            L = a * (ratio - 1)
            C = k0 / a ** p

    def theta(s):
        if abs(p) < 1e-12:
            return C * s
        if abs(p + 1) < 1e-9:
            return C * math.log((a + s) / a)
        return C / (p + 1) * ((a + s) ** (p + 1) - a ** (p + 1))

    th0 = math.radians(-90.0)
    ds = L / n
    x, y = 420.0, 780.0
    pts = [(x, -y)]
    for i in range(1, n + 1):
        th = th0 + theta((i - 0.5) * ds)
        x += math.cos(th) * ds
        y += math.sin(th) * ds
        pts.append((x, -y))
    return pts


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
            add("Plants", f"S{s0}–S{s0 + 4} · {ENDING[root_kind]}", "plant",
                f"{ENDING[root_kind]} at one join · fan 60–120°", branches,
                mark=[(0.0, 0.0)])

    # 9. same-angle overlays.  The boundary p=±0.5 member is the visible jump,
    #    so S39 is removed from the S35–S39 pair and S41 from S41–S45.
    palette = [INK, "#b23a2b", "#1f5fa8", "#2f6f4f", "#6f4a8c"]

    def sliced(group, s0, drop=()):
        keep = [i for i in range(len(group)) if i not in drop]
        return ([group[i] for i in keep],
                [palette[i] for i in keep],
                [(palette[i], f"S{s0 + i}") for i in keep],
                f"S{s0 + keep[0]}–S{s0 + keep[-1]}")

    for gname, start, s0, drop in (("S35–S39", 0, 35, (4,)),
                                   ("S41–S45", 6, 41, (0,))):
        group = lac_cards[start:start + 5]
        sub, colors, legend, label = sliced(group, s0, drop)
        for root_kind in ("spiral", "straight"):
            branches = plant(sub, root_kind, same_angle=90.0)
            add("Plants", f"{label} · {ENDING[root_kind]} · same angle",
                "plant overlay",
                "all stems leave at 90° · colours show the overlap", branches,
                mark=[(0.0, 0.0)], colors=colors, legend=legend)

    # 10. the same treatment for S46–S50 and S51–S55: scrolls and sprays.
    #     In the S51–S55 group the spiral slot of each pair is a double of
    #     S46…S55 (S138=S46+S46, S140=S47+S47, … S156=S55+S55); the straight
    #     slot keeps the pair.
    new_groups = (("S46–S50", 11, 46), ("S51–S55", 16, 51))
    for gname, start, s0 in new_groups:
        group = lac_cards[start:start + 5]
        if gname == "S51–S55":
            doubles = lac_cards[11:21]      # S46–S55
            for k, (i, j) in enumerate(itertools.combinations(range(5), 2)):
                d = doubles[k]
                add(f"Combinations · {gname}", f"S{46 + k}+S{46 + k}",
                    "double",
                    "spiral ends joined · G1 at the join",
                    [join_pair(d, d, "spiral")])
                add(f"Combinations · {gname}", f"S{51 + i}+S{51 + j}",
                    "combination",
                    "straight ends joined · G1 at the join",
                    [join_pair(group[i], group[j], "straight")])
        else:
            for i, j in itertools.combinations(range(5), 2):
                for variant in ("spiral", "straight"):
                    pts = join_pair(group[i], group[j], variant)
                    add(f"Combinations · {gname}", f"S{s0 + i}+S{s0 + j}",
                        "combination",
                        f"{variant} ends joined · G1 at the join", [pts])
    for gname, start, s0 in new_groups:
        group = lac_cards[start:start + 5]
        for root_kind in ("spiral", "straight"):
            drop = ((4,) if (gname == "S46–S50" and root_kind == "spiral")
                    else (0,) if (gname == "S51–S55" and root_kind == "spiral")
                    else ())
            sub, colors, legend, label = sliced(group, s0, drop)
            branches = plant(sub, root_kind)
            add("Plants", f"{label} · {ENDING[root_kind]}", "plant",
                f"{ENDING[root_kind]} at one join · fan 60–120°", branches,
                mark=[(0.0, 0.0)], colors=colors, legend=legend)
    for gname, start, s0 in new_groups:
        group = lac_cards[start:start + 5]
        for root_kind in ("spiral", "straight"):
            drop = (4,) if gname == "S46–S50" else (0,)
            sub, colors, legend, label = sliced(group, s0, drop)
            branches = plant(sub, root_kind, same_angle=90.0)
            add("Plants", f"{label} · {ENDING[root_kind]} · same angle",
                "plant overlay",
                "all stems leave at 90° · colours show the overlap", branches,
                mark=[(0.0, 0.0)], colors=colors, legend=legend)

    # 11. the open halves of the two symmetric gestures (S166/S167)
    half_cat = [(x, math.cosh(x)) for x in (2.0 * i / 240 for i in range(241))]
    add("Gestures · halves", "½ catenary", "cosh",
        "x∈[0,2] · half a hanging chain · rotated 150° CW",
        [rotate(half_cat, -150.0)])

    half_cyc = [(t - math.sin(t), 1 - math.cos(t))
                for t in (math.pi * i / 240 for i in range(241))]
    add("Gestures · halves", "½ cycloid", "cycloid",
        "t∈[0,π] · half an arch · rotated 90° CW",
        [rotate(half_cyc, -90.0)])

    # 12. the fractional LAC series, after the halves: SM17/SM18
    frac = [(0.25, "1/4"), (1/3, "1/3"), (0.5, "1/2"), (2/3, "2/3"),
            (3/4, "3/4"), (1.0, "1")]
    frac_group = [dict(branches=[lac_p_branches(p)]) for p, _ in frac]

    # The recovered plates live in the extraction page frame, about 7.6× the
    # frame of the generator.  p=1 is S52, so scale the whole generated family
    # by that ratio before SM18 puts it in one figure with S53–S55.
    ref = lac_cards[17]["branches"][0]        # S52, p = 1, turn 360
    gen = frac_group[-1]["branches"][0]       # p = 1
    scale = bbox_size(ref) / bbox_size(gen)
    frac_group = [
        dict(branches=[[(x * scale, y * scale) for x, y in card["branches"][0]]])
        for card in frac_group]

    frac_colors = ["#1f5fa8", "#2f6f9f", "#2f6f4f",
                   "#6f6a2f", "#8a5a2b", "#b23a2b"]
    frac_legend = [(c, f"p = {lab}") for c, (_, lab) in zip(frac_colors, frac)]
    add("Plants · LAC fractions", "LAC p = 1/4 → 1 · fractional series",
        "LAC law κ = C(a+s)^p",
        "same law/start/k0/k1 · turn 360° · normalised to S52",
        plant(frac_group, "straight", same_angle=90.0),
        mark=[(0.0, 0.0)], colors=frac_colors, legend=frac_legend)

    tail = lac_cards[18:21]              # S53–S55 = p = 1.5, 2, 3
    tail_colors = ["#6f4a8c", "#8a3f6b", "#5f6f2f"]
    combined = frac_group + tail
    combined_colors = frac_colors + tail_colors
    combined_legend = frac_legend + [
        (tail_colors[k], f"p = {lab}")
        for k, lab in enumerate(("3/2", "2", "3"))]
    add("Plants · LAC fractions", "SM16 + SM17 · p = 1/4 → 3 · shared p = 1",
        "frac + S53–S55",
        "same law/start/k0/k1; fractions normalised to S52; p = 1 shared",
        plant(combined, "straight", same_angle=90.0),
        mark=[(0.0, 0.0)], colors=combined_colors, legend=combined_legend)

    # 13. end-spacing studies: the same p range, different sequences.
    #     The gaps are measured on the straight-root fan in the S52 frame.
    def spaced_card(p):
        return dict(branches=[[(x * scale, y * scale)
                               for x, y in lac_p_branches(p)]])

    spacing_palette = ["#1f5fa8", "#2f6f9f", "#2f6f4f",
                       "#6f6a2f", "#8a5a2b", "#b23a2b",
                       "#6f4a8c", "#8a3f6b", INK]
    log_p = [0.25 * 12 ** (i / 8) for i in range(9)]
    spacing = [
        ("equal tip arc",
         [0.25, 0.3657, 0.4887, 0.6306, 0.8063, 1.04, 1.378, 1.926, 3.0],
         ["1/4", "0.366", "0.489", "0.631", "0.806", "1.04", "1.378", "1.926", "3"],
         "equal tip arc · gaps 236.3–236.5 · CV 0.0%"),
        ("simple fractions",
         [0.25, 3/8, 0.5, 5/8, 0.8, 1.0, 11/8, 2.0, 3.0],
         ["1/4", "3/8", "1/2", "5/8", "4/5", "1", "11/8", "2", "3"],
         "simple fractions · gaps 207.5–270.0 · CV 9.8%"),
        ("logarithmic p",
         log_p,
         [f"{p:.3g}" for p in log_p],
         "log p_i = 1/4·12^(i/8) · gaps 156.8–297.9 · CV 20.3%"),
        ("Fibonacci-like p",
         [0.25, 1/3, 0.5, 2/3, 1.0, 1.5, 2.0, 3.0],
         ["1/4", "1/3", "1/2", "2/3", "1", "3/2", "2", "3"],
         "Fibonacci-like p · gaps 170.7–384.0 · CV 27.6%"),
    ]
    for name, seq, labels, note in spacing:
        colors = spacing_palette[:len(seq)]
        legend = [(colors[i], f"p = {labels[i]}") for i in range(len(seq))]
        add("Plants · LAC spacing", name, "LAC spacing study", note,
            plant([spaced_card(p) for p in seq], "straight", same_angle=90.0),
            mark=[(0.0, 0.0)], colors=colors, legend=legend)

    # 14. integer studies.  p = n / 3125, so n = 3125 is exactly p = 1.
    integer_palette = ["#1f5fa8", "#2f6f9f", "#2f6f4f", "#6f6a2f",
                       "#8a5a2b", "#b23a2b", "#6f4a8c", "#8a3f6b",
                       INK, "#7b6c4e", "#2f6f6f"]
    integers = [
        ("integer log · n/3125",
         [781, 1066, 1454, 1984, 2706, 3692, 5037, 6872, 9375],
         "log integers · no 3125 · CV 20.3%"),
        ("integer equal-tip · n/3125",
         [781, 1143, 1527, 1971, 2520, 3250, 4306, 6019, 9375],
         "equal-tip integers · no 3125 · CV 0.0%"),
        ("3125 · 25-grid",
         [775, 1150, 1525, 1975, 2525, 3125, 4300, 6025, 9375],
         "all n ≡ 0 mod 25 · 3125 exact · CV 7.7%"),
        ("3125 · 5-grid",
         [780, 1070, 1370, 1695, 2070, 2520, 3125,
          3830, 4880, 6500, 9375],
         "all n ≡ 0 mod 5 · 3125 exact · CV 2.8%"),
    ]
    for name, ns, note in integers:
        colors = integer_palette[:len(ns)]
        legend = [(colors[i], str(ns[i])) for i in range(len(ns))]
        add("Plants · LAC integers", name, "LAC integer study",
            note + " · p = n/3125",
            plant([spaced_card(n / 3125) for n in ns],
                  "straight", same_angle=90.0),
            mark=[(0.0, 0.0)], colors=colors, legend=legend)


def legend(card):
    if not card.get("legend"):
        return ""
    rows = "".join(
        f'<tr><td><span class="sw" style="background:{c}"></span></td>'
        f'<td>{label}</td></tr>' for c, label in card["legend"])
    return f'<table class="legend">{rows}</table>'


def main():
    build()
    groups = []
    for card in CARDS:
        if not groups or groups[-1][0] != card["group"]:
            groups.append((card["group"], []))
        groups[-1][1].append(card)

    idx = 0
    sm = 0
    sections = []
    for group, cards in groups:
        rows = []
        for card in cards:
            idx += 1
            card["index"] = f"S{idx:02d}"
            if card["group"].startswith("Plants"):
                sm += 1
                card["display"] = f"SM{sm}"
            else:
                card["display"] = card["index"]
            rows.append(f"""<section class="card">
  <div class="art">{figure(card['branches'], mark=card.get('mark'), colors=card.get('colors'))}</div>
  <h3><span class="idx">{card['display']}</span> {card['name']}</h3>
  <p class="src">{card['source']}</p>
  <p class="note">{card['note']}</p>
  {legend(card)}
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
.legend{{border-collapse:collapse;margin:6px 0 0;font:10px/1.4 ui-monospace,Menlo,monospace}}
.legend td{{border:0;padding:1px 4px 1px 0}}
.sw{{display:inline-block;width:9px;height:9px;border:1px solid #d8ccae;vertical-align:middle}}
.panel{{background:#fffdf7;border:1px solid #d8ccae;padding:16px 18px;margin:0 0 20px}}
a{{color:{DOT}}}
</style></head><body><main>
<h1>Stem library</h1>
<p class="lead">{len(CARDS)} candidates, one curve per tight square.  Nothing here
is in a vase; this is the catalogue.</p>
<div class="panel">
<p><strong>How to use it.</strong> Every single stem has an <strong>S-number</strong>;
every multiple-stem plant has an <strong>SM-number</strong>.  Both carry their
source.  Tell the sheet which S- or SM-numbers to promote and they can be
moved into <a href="flowers.html">flowers.html</a> with their own vases.  The
curves are drawn at their own scale and orientation; the sheet applies the
rotation, the 7 in (or 60 mm) height and the vase placement.</p>
<p>The four groups with numbers are the two existing sources of exact data
(generators, Euler), the spiral-turns clothoids, the recovered LAC spines, and
four gestures.  The named-curve group is there because a loop or a drop can be
a stem; the LAC group is there because the soft S is the missing middle.</p>
</div>
<div class="panel">
<p><strong>The fractional LAC series (SM17–SM18).</strong> The LAC is one law,
κ = C(a+s)<sup>p</sup>; the recovered plates are points on it. SM17 is the same
law at p = 1/4, 1/3, 1/2, 2/3, 3/4 and 1, with the same start, initial heading,
curvature range 1/640 → 1/80 and 360° turn. The p = 1 member is the recovered
S52 spine: generating it from the law matches that spine to less than 0.001 of
the chord, so the join is the same curve, not a blend. p = 1/2 is the old
p = 0.5; 2/3 and 3/4 are the new points in the gap. SM18 carries the series on
into p = 1.5, 2, 3 (S53–S55), with p = 1 shared once. The boundary p = ±0.5
stems are removed from the same-angle multiples (SM5/SM6 lose S39; SM7/SM8
lose S41; SM13/SM14 lose S50; SM15/SM16 lose S51) and from the two spiral fans
SM9/SM11 (S50/S51), so the jump that prompted the series is gone from the
multiples; the individual reference plates remain in the LAC group.</p>
</div>
<div class="panel">
<p><strong>Equal end spacing (SM19–SM22).</strong> The gaps between the free
ends are not linear in p. With the SM18 mix they run 114–336 in the S52 frame
(CV 30%); a constant Δp is much worse (57–652, CV 83%). A log step
p<sub>i</sub> = 1/4·12<sup>i/8</sup> brings the CV to 20%; the simple fractions
1/4, 3/8, 1/2, 5/8, 4/5, 1, 11/8, 2, 3 reach 9.8%. The exact equal-tip-arc
series is p = 1/4, 0.366, 0.489, 0.631, 0.806, 1.04, 1.378, 1.926, 3; all eight
gaps are 236.3–236.5 (CV 0). Fibonacci-like p values are no better than the
current mix (27.6%). Distances are in the S52 frame; the card auto-fit leaves
the ratios unchanged.</p>
</div>
<div class="panel">
<p><strong>Integer numerators and 3125 (SM23–SM26).</strong> These four cards
use p = n / 3125, so n = 3125 is exactly p = 1. The log numerators
781, 1066, …, 9375 give CV 20.3%; the equal-tip numerators 781, 1143, …, 9375
give CV 0 but do not contain 3125 (the nearest is 3250). On a 25 grid, forcing
3125 gives 775, 1150, 1525, 1975, 2525, 3125, 4300, 6025, 9375 (CV 7.7%).
On a 5 grid it gives 780, 1070, 1370, 1695, 2070, 2520, 3125, 3830, 4880,
6500, 9375 (CV 2.8%). 3125 can therefore be hit exactly on either grid; the
25 grid is the neater one, the 5 grid the closer one.</p>
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
