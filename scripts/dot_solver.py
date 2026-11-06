"""The dot solver: one figure per failure class, measured, with a verdict.

    .venv/bin/python scripts/dot_solver.py
    open workbench/dot-solver.html

The problem this exists to solve: lattice marks that are missing, or that sit
off the curve. Each case below is one *class* of failure, drawn large, with its
marks and its numbers. The page carries the verdict; `scripts/check-dots.py`
re-derives the same verdict from the geometry and exits non-zero if any case
regresses.

The rule the solver enforces:

1. A mark is a p-triangle join — a vertex of the chain the curve was converted
   to — not a crossing of a display grid.
2. A join is projected onto the curve it belongs to, so a mark is never off the
   ink, even when the chain is a poor fit. The distance it had to move is the
   *fit error*, reported beside it: that number is the honesty, not the fix.
3. Every solid curve gets its own joins. A figure made of four copies gets
   four chains, not one chain from the longest copy.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import showcase as S  # noqa: E402

TOL_PX = 2.0          # a mark this close to the ink reads as on the curve
SCALE_PX = 336.0      # the panel's long side, for converting model units


def _dist_point_segment(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.dist(p, a)
    t = ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.dist(p, (ax + t * dx, ay + t * dy))


def nearest_on(points, p):
    """The closest point of a polyline, and how far away it was."""
    best, at = float("inf"), points[0]
    for a, b in zip(points, points[1:]):
        d = _dist_point_segment(p, a, b)
        if d < best:
            best = d
            ax, ay = a
            bx, by = b
            dx, dy = bx - ax, by - ay
            t = 0.0 if dx == 0 and dy == 0 else (
                ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy))
            t = max(0.0, min(1.0, t))
            at = (ax + t * dx, ay + t * dy)
    return at, best


def chain_of(points, n=24):
    """The p-triple chain for one curve, in that curve's own frame."""
    from curve_lab.euler_polygon import convert
    d = convert(points, n=n)
    x0, y0 = points[0]
    dx, dy = points[1][0] - points[0][0], points[1][1] - points[0][1]
    a = math.atan2(dy, dx)
    c, s = math.cos(a), math.sin(a)
    joins = [(x0 + X * c - Y * s, y0 + X * s + Y * c) for X, Y in d["polygon"]]
    return joins, d["chord"]


def solved_marks(curves, tol_px=TOL_PX):
    """One mark per p-triangle join per curve, projected onto that curve.

    Returns the marks, the worst fitted distance (model units), and the same
    expressed in panel pixels so a verdict can be stated in the units the eye
    uses.
    """
    marks, worst, worst_px = [], 0.0, 0.0
    if not curves or not any(curves):
        return marks, worst, worst_px, 0, 0.0
    xs = [p[0] for pts in curves for p in pts]
    if not xs:
        return marks, worst, worst_px, 0, 0.0
    ys = [p[1] for pts in curves for p in pts]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    px_per_unit = SCALE_PX / span
    chords = 24
    proj_worst = 0.0
    for pts in curves:
        if len(pts) < 8:
            # an explicit construction polyline: its vertices are the joins
            marks.extend(pts)
            continue
        # solve: raise the chain resolution until the joins sit on the ink
        best = None
        for n in (24, 48, 96, 192, 384):
            try:
                joins, _chord = chain_of(pts, n=n)
            except Exception:
                joins = []
            if not joins:
                continue
            err = max(nearest_on(pts, j)[1] for j in joins)
            if best is None or err < best[0]:
                best = (err, joins, n)
            if err * px_per_unit <= tol_px:
                break
        if best is None:
            continue
        err, joins, chords = best
        if len(joins) > 25:                     # readable: 25 joins per curve
            stride = len(joins) / 25
            joins = [joins[int(i * stride)] for i in range(25)]
        for j in joins:
            at, moved = nearest_on(pts, j)
            marks.append(at)
            proj_worst = max(proj_worst, moved)
        worst = max(worst, err)
        worst_px = max(worst_px, err * px_per_unit)
    return marks, worst, worst_px, chords, proj_worst


def case_curves():
    """One entry per failure class, named for what is wrong with it."""
    import generators as G

    def named(key):
        return S.named_curve(key) or []

    circle = [(math.cos(t), math.sin(t))
              for t in [i * 2 * math.pi / 240 for i in range(241)]]
    def polar(fn, t0, t1, n=240):
        return [[(fn(t0 + (t1 - t0) * i / n)[0], fn(t0 + (t1 - t0) * i / n)[1])
                 for i in range(n + 1)]]

    piriform = named("piriform") or polar(
        lambda t: ((1 + math.sin(t)) * math.cos(t), (1 + math.sin(t)) * math.sin(t)),
        0.0, 2 * math.pi)
    gerono = named("gerono") or polar(
        lambda t: (math.cos(t), math.sin(t) * math.cos(t)), 0.0, 2 * math.pi)
    bicorn = named("bicorn") or polar(
        lambda t: (math.sin(t), math.cos(t) ** 2 * (1 + math.sin(t)) / (1 - math.sin(t) + 1e-9)),
        0.0, math.pi)

    def rotate(pts, deg):
        a = math.radians(deg)
        c, s = math.cos(a), math.sin(a)
        return [(x * c - y * s, x * s + y * c) for x, y in pts]

    flower = []
    for k in range(4):
        for br in bicorn[:1]:
            moved = [(x, y - 1.0) for x, y in br]
            flower.append(rotate(moved, 90 * k))

    cases = [
        ("closed-smooth", "9b-class · closed smooth curve, poor p-triple fit",
         "the circle member: a closed loop has no clean p-triple stop, so the "
         "chain drifts and the joins land beside the ink",
         [circle]),
        ("cusped", "9b-class · cusped quartic",
         "a cusp breaks the converter; the joins must still sit on the two "
         "branches", piriform),
        ("two-branch", "11f-class · two branches, one node",
         "the bicorn: joins from the right half must not be drawn on the left",
         bicorn),
        ("composed", "11g-class · four transformed copies",
         "each copy needs its own chain; one chain across all four marks only "
         "the copy it was fitted to", flower),
        ("sampled-named", "9a-class · sampled quartic",
         "Gerono: a sampled curve with a node at the origin", gerono),
        ("chain", "2b-class · joined spans, curvature matched",
         "a p-triple chain of whole-number turns: every join is a construction "
         "vertex", [S.turn_polygon([1, 2, 2, 1, 1], 4, 3, chord=1.0)]),
    ]
    out = []
    for key, title, why, curves in cases:
        out.append({"key": key, "title": title, "why": why,
                    "curves": [c for c in curves if len(c) > 3]})
    return out


def measure(cases):
    rows = []
    for c in cases:
        marks, worst, worst_px, chords, proj = solved_marks(c["curves"])
        # every solid curve must carry at least two marks; the chain's own
        # fit is reported beside the verdict, not hidden behind it
        ok = len(marks) >= 2 * max(1, len([c for c in c["curves"] if len(c) > 3]))
        rows.append({**c, "marks": marks, "worst": worst,
                     "worst_px": worst_px, "chords": chords, "proj": proj,
                     "ok": ok})
    return rows


def main() -> int:
    rows = measure(case_curves())
    cards, table = [], []
    for r in rows:
        usable = [pts for pts in r["curves"] if len(pts) > 7]
        if not usable:
            table.append(f'<tr><td>{r["key"]}</td><td>0</td><td>—</td>'
                         f'<td>—</td><td>FAIL</td></tr>')
            continue
        curves = [(pts, S.INK, 1.8, None) for pts in usable]
        svg = S.panel(r["title"], r["why"], curves, dots=[(p, S.MARK) for p in r["marks"]],
                      joins=False)
        cards.append(f'<section class="case"><div class="art">{svg}</div>'
                     f'<p class="verdict {("ok" if r["ok"] else "bad")}">'
                     f'{"PASS" if r["ok"] else "FAIL"} · {len(r["marks"])} marks · '
                     f'worst {r["worst_px"]:.2f} px off the ink</p></section>')
        table.append(
            f'<tr><td>{r["key"]}</td><td>{len(r["marks"])}</td>'
            f'<td>{r["worst"]:.4f}</td><td>{r["worst_px"]:.2f}</td>'
            f'<td>{"PASS" if r["ok"] else "FAIL"}</td></tr>')

    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dot solver · one figure per failure class</title>
<style>
body{{margin:0;background:#f6f1e4;color:{S.INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1100px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:30px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 18px}}
h2{{font:600 12px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.10em;
   text-transform:uppercase;color:{S.MUTED};margin:30px 0 8px}}
.case{{background:#fffdf7;border:1px solid #d8ccae;padding:10px;margin:0 0 16px}}
.art svg{{display:block;width:100%;height:auto}}
.verdict{{font:12px/1.6 ui-monospace,Menlo,monospace;margin:6px 0 0}}
.verdict.ok{{color:#2f6f4f}} .verdict.bad{{color:#a23b2a}}
table{{border-collapse:collapse;width:100%;font:12px/1.5 ui-monospace,Menlo,monospace}}
th,td{{border-bottom:1px solid #d8ccae;padding:5px 8px;text-align:left}}
th{{color:{S.MUTED};font-weight:600}}
.note{{font:12px/1.6 ui-monospace,Menlo,monospace;color:{S.MUTED}}}
</style></head><body><main>
<h1>Dot solver</h1>
<p class="lead">One figure per class of failure: marks missing, or marks off the
curve. Each case is measured, not eyeballed.</p>
<p class="note">Rule: a mark is a p-triangle join, projected onto the curve it
belongs to. The distance it had to move is the chain's fit error, shown beside
it. Tolerance {TOL_PX:g} px on a {SCALE_PX:g} px panel.</p>

<h2>The cases</h2>
{''.join(cards)}

<h2>The measurement</h2>
<table>
<thead><tr><th>case</th><th>marks</th><th>worst move (units)</th>
<th>worst move (px)</th><th>verdict</th></tr></thead>
<tbody>{''.join(table)}</tbody>
</table>
<p class="note">Re-derive: <code>python scripts/dot_solver.py</code> ·
<code>python scripts/check-dots.py</code></p>
</main></body></html>
'''
    out = ROOT / "workbench" / "dot-solver.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    bad = [r["key"] for r in rows if not r["ok"]]
    print("fail:", ", ".join(bad) if bad else "none")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
