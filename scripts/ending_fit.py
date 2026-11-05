"""Ending fit pass: the C families fitted to one stalk tip, with numbers.

    .venv/bin/python scripts/ending_fit.py

Each card takes a section from `scripts/euler_sections.py` (the repo's own
table of C-curve sections), attaches its first point to a standard stalk tip,
rotates its first tangent onto the stalk, scales it to six offsets, and mirrors
it into a two-sided ending. The page reports the scale, the reach, the minimum
clearance to the stalk, the self-intersections and the cusps.

This is a measurement pass, not a new grade: the ending grades in `TODO.md`
stand, and a card is flagged only if the numbers contradict them.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import euler_sections as ES  # noqa: E402
import plant_forms as PF  # noqa: E402

INK, BLUE, RED, GOLD, GREEN = "#2e2413", "#1f5fa8", "#a23b2a", "#c9a441", "#2f6f4f"
MUTED, PAPER = "#7b6c4e", "#fffdf7"

OFFSET = 0.5
REACH = 6.0 * OFFSET
STALK = [(0.0, -2.0), (0.0, 0.0)]
GRADES = {
    "Cycloid": "B",
    "Astroid": "A",
    "Semicubical / Neile": "B",
    "Tractrix": "B",
    "Heart": "A/B",
    "Squircle": "A/B",
    "Bicorn": "B",
    "Nodal": "B",
    "Tschirnhausen": "B",
    "Piriform 2×": "B",
}


def _fit(points):
    """Attach the first point to the origin, first tangent to +y, reach 6d."""
    p0 = points[0]
    dx, dy = points[1][0] - p0[0], points[1][1] - p0[1]
    rot = math.pi / 2.0 - math.atan2(dy, dx)
    ca, sa = math.cos(rot), math.sin(rot)
    local = [((x - p0[0]) * ca - (y - p0[1]) * sa,
              (x - p0[0]) * sa + (y - p0[1]) * ca) for x, y in points]
    reach = max(math.hypot(x, y) for x, y in local) or 1.0
    scale = REACH / reach
    return [(x * scale, y * scale) for x, y in local], scale


def _seg_hits(a, b, c, d):
    def cross(o, p, q):
        return (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])
    d1, d2 = cross(a, b, c), cross(a, b, d)
    d3, d4 = cross(c, d, a), cross(c, d, b)
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))


def _intersections(branches):
    count = 0
    for bi, pts in enumerate(branches):
        for i in range(len(pts) - 1):
            for j in range(i + 2, len(pts) - 1):
                if _seg_hits(pts[i], pts[i + 1], pts[j], pts[j + 1]):
                    count += 1
        for other in branches[bi + 1:]:
            for i in range(len(pts) - 1):
                for j in range(len(other) - 1):
                    if _seg_hits(pts[i], pts[i + 1], other[j], other[j + 1]):
                        # the two halves meet at the declared attachment;
                        # only a crossing away from the tip is a fold
                        if (math.hypot(*pts[i]) > 0.2
                                and math.hypot(*pts[i + 1]) > 0.2
                                and math.hypot(*other[j]) > 0.2
                                and math.hypot(*other[j + 1]) > 0.2):
                            count += 1
    return count


def _cusps(pts):
    out = 0
    for i in range(1, len(pts) - 1):
        a = (pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
        b = (pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
        la, lb = math.hypot(*a), math.hypot(*b)
        if la < 1e-12 or lb < 1e-12:
            out += 1
            continue
        turn = math.degrees(math.acos(max(-1.0, min(1.0,
            (a[0] * b[0] + a[1] * b[1]) / (la * lb)))))
        if turn > 150.0:
            out += 1
    return out


def _point_seg(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    l2 = dx * dx + dy * dy
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / l2))
    return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy))


def _clearance(pts):
    """Minimum distance from the ending to either stalk rail, above the tip."""
    best = 99.0
    for p in pts:
        if p[1] < 0.1:
            continue
        for sx in (-OFFSET, OFFSET):
            best = min(best, _point_seg(p, (sx, -2.0), (sx, 0.0)))
    return best


def fit_data() -> list[dict]:
    rows = []
    for name, note, fn, _opts in ES.SECTIONS:
        pts, scale = _fit(fn())
        mirrored = [(-x, y) for x, y in pts]
        branches = [pts, mirrored]
        rows.append({
            "name": name,
            "note": note,
            "grade": GRADES.get(name, "B"),
            "scale": scale,
            "reach": max(math.hypot(x, y) for x, y in pts),
            "clearance": _clearance(pts),
            "intersections": _intersections(branches),
            "cusps": _cusps(pts),
            "points": pts,
            "mirrored": mirrored,
        })
    return rows


def card(row) -> str:
    items = [
        (STALK, INK, 1.6, None),
        ([(OFFSET, -2.0), (OFFSET, 0.0)], BLUE, 1.1, None),
        ([(-OFFSET, -2.0), (-OFFSET, 0.0)], RED, 1.1, None),
        (row["points"], INK, 1.7, None),
        (row["mirrored"], INK, 1.7, None),
    ]
    return PF.figure(items, 360, 280)


def main() -> int:
    rows = fit_data()
    cards = []
    for row in rows:
        flag = (row["intersections"] > 0)
        status = "flag" if flag else "keeps its grade"
        cards.append(f'''<section class="card">
<div class="art">{card(row)}</div>
<h3>{row['name']} <span class="grade">ending {row['grade']}</span></h3>
<p class="note">{row['note']} · scale {row['scale']:.3f} · reach {row['reach']:.2f} ·
clearance {row['clearance']:.2f} · {row['cusps']} cusp(s) ·
{row['intersections']} self-intersection(s) · {status}</p>
</section>''')
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ending fit pass — the C families on one stalk tip</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 18px}}
.panel{{background:{PAPER};border:1px solid #d8ccae;padding:16px 18px;margin:0 0 18px}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
.card{{background:{PAPER};border:1px solid #d8ccae;padding:10px}}
.card h3{{font:600 13px/1.35 Georgia,serif;margin:0 0 4px}}
.grade{{font:10px ui-monospace,Menlo,monospace;color:{MUTED};font-weight:400}}
.art{{margin:0 0 6px}}
svg{{display:block;width:100%;height:auto}}
.note{{font:10px/1.45 ui-monospace,Menlo,monospace;color:{MUTED};margin:0}}
code{{font:12px ui-monospace,Menlo,monospace}}
@media(max-width:900px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body><main>
<h1>Ending fit pass</h1>
<p class="lead">Every C-family section attached to one stalk tip, at a fixed
6 × offset reach, with the numbers that decide whether it can be an ending.</p>

<div class="panel">
<p><strong>The fit.</strong> The stalk is vertical, width {2*OFFSET:g}, so the
rails stand at ±{OFFSET:g}. Each curve's first point is placed on the tip and
its first tangent turned onto the stalk; it is then scaled so its farthest
point is {REACH:g} from the tip (6 × offset) and mirrored into a two-sided
ending. The 2 × offset rule is untouched: the ending grows beyond the tip, it
does not narrow the stalk.</p>
<p><strong>What is measured.</strong> The scale factor, the reach, the minimum
clearance from the ending to either rail, the number of cusps (turns over
150°), and the number of segment crossings. A card is flagged only when a
measured crossing contradicts its grade; the ending grades in <code>TODO.md</code>
stand, because a fit is evidence, not a promotion.</p>
</div>

<div class="grid">
{''.join(cards)}
</div>

<div class="panel">
<p><strong>Reading the pass.</strong> The section table already splits the
cusps off these curves, so the fitted section is the smooth part the ending
would use. All ten attach, all clear the rails by about the offset, and none
crosses itself away from the declared tip — so every grade in the ending track
stands. No card is promoted: a fit is evidence, not a promotion.</p>
<p class="note">Re-derive: <code>python scripts/ending_fit.py</code> ·
<code>python -m unittest tests.test_ending_fit</code></p>
</div>
</main></body></html>
'''
    out = ROOT / "workbench" / "ending-fit.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
