"""Arches and pillars: one section, mirrored.

    .venv/bin/python scripts/arches_pillars.py
    open workbench/arches-pillars.html

The rule is in the join, not the curve. Take a section from the showcase,
place it, mirror it across the centreline:

- if the two ends meet inward at the crown, it is an **arch**;
- if the two halves leave the stem and branch outward, it is a **capital**.

Every panel names the section it came from and measures the join, so the
difference is a number rather than a label. These are rigid placements of
existing sections, not fitted joins; the page says so.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import curve_morphs as M  # noqa: E402

INK, MUTED, RULE, PAPER = "#2e2413", "#7b6c4e", "#d8ccae", "#fbf7ec"
BLUE, GOLD, RED = "#1f5fa8", "#c9a441", "#a23b2a"


def place(pts, p0, p1):
    """Rigid motion: map pts[0] → p0 and pts[-1] → p1, uniformly scaled."""
    vx, vy = pts[-1][0] - pts[0][0], pts[-1][1] - pts[0][1]
    tx, ty = p1[0] - p0[0], p1[1] - p0[1]
    lv = math.hypot(vx, vy) or 1e-12
    lt = math.hypot(tx, ty) or 1e-12
    s = lt / lv
    a = math.atan2(ty, tx) - math.atan2(vy, vx)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for x, y in pts:
        x -= pts[0][0]
        y -= pts[0][1]
        out.append((p0[0] + (ca * x - sa * y) * s,
                    p0[1] + (sa * x + ca * y) * s))
    return out


def mirror(pts):
    return [(-x, y) for x, y in pts]


def end_tangent(pts):
    dx = pts[-1][0] - pts[-2][0]
    dy = pts[-1][1] - pts[-2][1]
    return math.degrees(math.atan2(dy, dx))


def crown_off_vertical(pts):
    """How far the right half's end tangent is from straight up, in degrees."""
    t = end_tangent(pts)
    return abs(((t - 90.0 + 180.0) % 360.0) - 180.0)


def capital_divergence(right):
    """Angle between the two halves' outgoing tangents, in degrees."""
    a = end_tangent(right)
    b = end_tangent(mirror(right))
    d = (a - b + 180.0) % 360.0 - 180.0
    return abs(d)


# the sections, chosen from the showcase's leaf set
SECTIONS = dict(M.leaf_sections())

ARCH_P0, ARCH_P1 = (1.55, 0.0), (0.0, 2.15)
CAP_P0, CAP_P1 = (0.0, 0.0), (1.45, 1.75)

ARCH_IF_CROWN = 20.0                 # degrees off vertical still reads as an arch
CAPITAL_IF_DIVERGE = (10.0, 90.0)    # outward, but not folded back


def classify():
    """Every section, both placements, and the verdict the join gives it."""
    rows = []
    for title, section in SECTIONS.items():
        right_a = place(section, ARCH_P0, ARCH_P1)
        right_c = place(section, CAP_P0, CAP_P1)
        crown = crown_off_vertical(right_a)
        div = capital_divergence(right_c)
        if crown <= ARCH_IF_CROWN:
            use = "arch"
        elif CAPITAL_IF_DIVERGE[0] <= div <= CAPITAL_IF_DIVERGE[1]:
            use = "capital"
        else:
            use = "—"
        rows.append({"title": title, "crown": crown, "div": div,
                     "use": use, "right_a": right_a, "right_c": right_c})
    return rows


def cases():
    out = []
    for row in classify():
        if row["use"] == "arch":
            out.append(("arch", row["title"], row["right_a"],
                        f"crown off vertical {row['crown']:.1f}°",
                        "curve_morphs.leaf_sections"))
        elif row["use"] == "capital":
            out.append(("capital", row["title"], row["right_c"],
                        f"branches diverge {row['div']:.1f}°",
                        "curve_morphs.leaf_sections"))
    return out


# -- drawing ----------------------------------------------------------------

def panel(kind, title, right, note, source):
    left = mirror(right)
    pts = right + left
    w, h = 420, 360
    pad = 40
    xs = [p[0] for p in pts] + [0.0]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    s = min((w - 2 * pad) / max(1e-9, x1 - x0),
            (h - 2 * pad) / max(1e-9, y1 - y0))
    ox = (w - (x1 - x0) * s) / 2 - x0 * s
    oy = (h - (y1 - y0) * s) / 2 + y1 * s

    def f(p):
        return (ox + p[0] * s, oy - p[1] * s)

    def path(seq):
        return " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}"
                        for i, (x, y) in enumerate(f(p) for p in seq))

    cx = f((0, 0))[0]
    base = f((0, 0))[1]
    springs = f((ARCH_P0[0], 0))[0] if kind == "arch" else cx
    foot = (f"<line x1='{f((-ARCH_P0[0], 0))[0]:.1f}' y1='{base:.1f}' "
            f"x2='{f((ARCH_P0[0], 0))[0]:.1f}' y2='{base:.1f}' "
            f"stroke='{RULE}' stroke-width='3'/>")
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{kind}: {title}">
  <rect width="{w}" height="{h}" fill="{PAPER}"/>
  <line x1="{cx}" y1="{pad // 2}" x2="{cx}" y2="{h - pad // 2}" stroke="{RULE}" stroke-width="1" stroke-dasharray="5 5"/>
  {foot}
  <path d="{path(right)}" fill="none" stroke="{INK}" stroke-width="2.2"/>
  <path d="{path(left)}" fill="none" stroke="{INK}" stroke-width="2.2"/>
  <text x="10" y="20" font-family="Georgia,serif" font-size="12" fill="{INK}">{kind} · {title}</text>
  <text x="10" y="{h - 10}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{MUTED}">{note}</text>
  <text x="{w - 26}" y="{h - 10}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{MUTED}">x →</text>
  <text x="10" y="36" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{MUTED}">y ↑</text>
</svg>"""


def build():
    rows = cases()
    table_rows = classify()
    ranking = "".join(
        f"<tr><td>{r['title']}</td><td>{r['crown']:.1f}°</td>"
        f"<td>{r['div']:.1f}°</td><td>{r['use']}</td></tr>"
        for r in table_rows)
    arch_note = ", ".join(f"{r['title']} {r['crown']:.1f}°"
                          for r in table_rows if r["use"] == "arch")
    cap_note = ", ".join(f"{r['title']} {r['div']:.1f}°"
                         for r in table_rows if r["use"] == "capital")

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Arches and pillars · mirrored sections</title>
<style>
:root{{--paper:{PAPER};--ink:{INK};--muted:{MUTED};--rule:{RULE}}}
*{{box-sizing:border-box}} body{{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:34px 22px 70px}}
.eyebrow{{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
h1{{font-size:31px;line-height:1.12;margin:0 0 8px}} h2{{font-size:20px;margin:0 0 8px}}
.lede{{max-width:920px;color:var(--muted)}}
.panel{{background:var(--paper);border:1px solid var(--rule);padding:16px 18px;margin:0 0 18px}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}
@media(max-width:900px){{.grid{{grid-template-columns:1fr}}}}
.small{{font:12px/1.6 ui-monospace,Menlo,monospace;color:var(--muted)}}
code{{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}}
</style></head><body><main>
<p class="eyebrow">curve-lab · arches and pillars</p>
<h1>One section, mirrored: the join decides</h1>
<p class="lede">Take a section from the showcase, place it, mirror it about the centreline. If the two
ends meet inward at the crown it is an <b>arch</b>; if they leave the stem and branch outward it is a
<b>capital</b>. The curve does not change between the two rows — only where it is placed and which
way it faces. Each panel names its section and measures the join.</p>

<section class="panel">
<h2>Arches · the halves meet inward</h2>
<div class="grid">
{''.join(f"<div>{panel(*r)}</div>" for r in rows if r[0] == 'arch')}
</div>
<p class="small">The crown is the test: a well-set arch arrives near vertical, so the two mirrored
tangents meet with little kink. Measured off-vertical: {arch_note}. These are rigid placements of
existing sections, not fitted joins — the number says how far from a smooth crown each one is.</p>
</section>

<section class="panel">
<h2>Capitals · the halves branch outward</h2>
<div class="grid">
{''.join(f"<div>{panel(*r)}</div>" for r in rows if r[0] == 'capital')}
</div>
<p class="small">The same sections, set at the top of a stem with the far end outward. The halves now
diverge instead of meeting: {cap_note}. A capital is the arch rule read backwards — the join is at the
bottom, and the curve is free at the top.</p>
</section>

<section class="panel">
<h2>Why these six</h2>
<p>The sections were not chosen by eye. Each one was placed both ways and measured, and the join
decided the use. An arch has to arrive near vertical (≤ 20° off); a capital has to leave the stem
outward, between 10° and 90°, so it is a branch and not a fold.</p>
<table>
<tr><th>section</th><th>crown off vertical</th><th>outward divergence</th><th>use</th></tr>
{ranking}
</table>
<p class="small">The rejects are the useful part: the log spiral is 49° outward (a capital) but 100°
at the crown, so it is not an arch; the cycloid is a good arch (3.9°) but folds back 143° as a
capital. A section is a shape, not a role — the placement and the join give it one.</p>
</section>

<section class="panel">
<h2>Next</h2>
<p>The page establishes the vocabulary and the test; it does not yet build a whole bay. The next step
is a bay: two piers, a capital on each, an arch between them, with the springing and impost heights
declared and the sections chosen for the span. The grammar is the same one the plant-forms use —
a full line, an ending, a join — applied vertically.</p>
<p class="small">Re-derive: <code>python scripts/arches_pillars.py</code> ·
test: <code>python -m unittest tests.test_arches_pillars</code></p>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "arches-pillars.html"
    out.write_text(html, encoding="utf-8")
    print(out)
    return out


if __name__ == "__main__":
    for kind, title, right, note, source in cases():
        print(f"{kind:8s} {title:22s} {note}")
    build()
