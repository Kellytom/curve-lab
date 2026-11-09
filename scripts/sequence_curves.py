"""Sequence curves: factorials, triangular sums, and the symmetric closure.

    .venv/bin/python scripts/sequence_curves.py
    open workbench/sequence-curves.html

Every panel is a walk on the integer lattice with right-angle turns. The
lengths come from a number sequence: the factorials 4!, 3!, 2!, 1! and the
triangular sums T4, T3, T2, T1. The symmetric closure is the schedule

    1, 2, ..., n, -n, ..., -1

with equal chords: the return repeats each chord in reverse with the opposite
sign, so the displacement cancels pairwise and the walk returns to the origin
for every n. The two passes share the same chords, so the return is drawn
dashed on top of the outward pass.
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = "#fbf7ec"
INK, MUTED, GOLD, BLUE, RED = "#2e2413", "#7b6c4e", "#c9a441", "#1f5fa8", "#a23b2a"
RULE = "#d8ccae"
GREEN = "#2f6b3a"

DIRS = ((1, 0), (0, 1), (-1, 0), (0, -1))
FACT = [24, 6, 2, 1]
TRI = [10, 6, 3, 1]


def walk(lengths, start=(0, 0), d0=0):
    """A right-angle walk: the direction advances by 90 degrees at each step."""
    x, y = start
    pts = [(x, y)]
    for i, length in enumerate(lengths):
        dx, dy = DIRS[(d0 + i) % 4]
        x += length * dx
        y += length * dy
        pts.append((x, y))
    return pts


def symmetric(lengths):
    """The closure 1..n, -n..-1: return the chords in reverse, opposite sign."""
    n = len(lengths)
    out_dirs = [i % 4 for i in range(n)]
    pts = [(0, 0)]
    x = y = 0
    for i, length in enumerate(lengths):
        dx, dy = DIRS[out_dirs[i]]
        x += length * dx
        y += length * dy
        pts.append((x, y))
    out = list(pts)
    back = [(x, y)]
    for i in reversed(range(n)):
        dx, dy = DIRS[out_dirs[i]]
        x -= lengths[i] * dx
        y -= lengths[i] * dy
        back.append((x, y))
    return out, back


def signed(lengths):
    """The signed schedule 1..n, -n..-1, as a single list of signed steps."""
    return list(lengths) + [-length for length in reversed(lengths)]


def closure(lengths):
    out, back = symmetric(lengths)
    return back[-1], math.dist(back[-1], (0, 0))


class Frame:
    def __init__(self, w, h, x0, x1, y0, y1, pad=44):
        self.w, self.h = w, h
        self.s = min((w - 2 * pad) / (x1 - x0), (h - 2 * pad) / (y1 - y0))
        self.ox = (w - (x1 - x0) * self.s) / 2.0 - x0 * self.s
        self.oy = (h - (y1 - y0) * self.s) / 2.0 + y1 * self.s

    def __call__(self, p):
        # +y up in the model; flipped here on the way to screen coordinates
        return (self.ox + p[0] * self.s, self.oy - p[1] * self.s)


def path(pts, f):
    return " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}"
                    for i, (x, y) in enumerate(f(p) for p in pts))


def nice_step(span):
    for step in (1, 2, 5, 10, 20, 50):
        if span / step <= 10:
            return step
    return 100


def figure(pts, w=600, h=420, back=None, labels=None, title="", note=""):
    allp = list(pts) + (list(back) if back else [])
    xs = [p[0] for p in allp]
    ys = [p[1] for p in allp]
    pad = 0.12 * max(max(xs) - min(xs), max(ys) - min(ys), 1)
    f = Frame(w, h, min(xs) - pad, max(xs) + pad,
              min(ys) - pad, max(ys) + pad)

    step = nice_step(max(xs) - min(xs) + max(ys) - min(ys))
    grid = []
    gx = math.floor((min(xs) - pad) / step) * step
    while gx <= max(xs) + pad:
        a, b = f((gx, min(ys) - pad)), f((gx, max(ys) + pad))
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                    f'y2="{b[1]:.1f}" stroke="{RULE}" stroke-width="0.6"/>')
        gx += step
    gy = math.floor((min(ys) - pad) / step) * step
    while gy <= max(ys) + pad:
        a, b = f((min(xs) - pad, gy)), f((max(xs) + pad, gy))
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                    f'y2="{b[1]:.1f}" stroke="{RULE}" stroke-width="0.6"/>')
        gy += step

    dots = []
    for p in pts:
        x, y = f(p)
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{PAPER}" '
                    f'stroke="{INK}" stroke-width="1.1"/>')
    labels_svg = []
    if labels:
        for (x, y), text in labels:
            X, Y = f((x, y))
            labels_svg.append(f'<text x="{X + 5:.1f}" y="{Y - 5:.1f}" '
                              f'font-family="ui-monospace,Menlo,monospace" '
                              f'font-size="11" fill="{MUTED}">{text}</text>')

    back_svg = ""
    if back:
        back_svg = (f'<path d="{path(back, f)}" fill="none" stroke="{GOLD}" '
                    f'stroke-width="1.8" stroke-dasharray="6 4"/>')

    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{title}">
  <rect width="{w}" height="{h}" fill="{PAPER}"/>
  {''.join(grid)}
  <path d="{path(pts, f)}" fill="none" stroke="{INK}" stroke-width="2.4"/>
  {back_svg}
  {''.join(dots)}
  {''.join(labels_svg)}
  <text x="12" y="22" font-family="Georgia,serif" font-size="14" fill="{INK}">{title}</text>
  <text x="12" y="40" font-family="ui-monospace,Menlo,monospace" font-size="10.5" fill="{MUTED}">{note}</text>
  <text x="{w / 2:.0f}" y="{h - 10}" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{MUTED}">x (lattice units)</text>
  <text x="12" y="{h / 2:.0f}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{MUTED}" transform="rotate(-90 12 {h / 2:.0f})">y (lattice units)</text>
  <g font-family="Georgia,serif" font-size="11">
    <line x1="12" y1="{h - 26}" x2="38" y2="{h - 26}" stroke="{INK}" stroke-width="2.4"/><text x="44" y="{h - 22}" fill="{INK}">outward</text>
    {'' if not back else f'<line x1="112" y1="{h - 26}" x2="138" y2="{h - 26}" stroke="{GOLD}" stroke-width="1.8" stroke-dasharray="6 4"/><text x="144" y="{h - 22}" fill="{INK}">return</text>'}
  </g>
</svg>"""


def factorial_panel():
    pts = walk(FACT)
    labels = [(((p[0] + q[0]) / 2, (p[1] + q[1]) / 2), t)
              for p, q, t in zip(pts, pts[1:], ["4!", "3!", "2!", "1!"])]
    return {
        "key": "S1", "title": "Fig. S1 · factorial lengths · 4! down to 1!",
        "pts": pts, "back": None, "labels": labels,
        "note": "24, 6, 2, 1 · right-angle turns · integer vertices",
    }


def triangular_panel():
    pts = walk(TRI)
    labels = [(((p[0] + q[0]) / 2, (p[1] + q[1]) / 2), t)
              for p, q, t in zip(pts, pts[1:], ["T₄", "T₃", "T₂", "T₁"])]
    return {
        "key": "S2", "title": "Fig. S2 · triangular sums · T₄ down to T₁",
        "pts": pts, "back": None, "labels": labels,
        "note": "10, 6, 3, 1 · right-angle turns · integer vertices",
    }


def closure_panel(n, key):
    out, back = symmetric(list(range(1, n + 1)))
    return {
        "key": key, "title": f"Fig. {key} · symmetric closure · 1…{n}, −{n}…−1",
        "pts": out, "back": back, "labels": [],
        "note": ("the return repeats each chord in reverse with the opposite sign; "
                 "the endpoint is (0, 0)"),
    }


def factor_closure_panel():
    out, back = symmetric(FACT)
    return {
        "key": "S5", "title": "Fig. S5 · factorial closure · 24, 6, 2, 1, −1, −2, −6, −24",
        "pts": out, "back": back, "labels": [],
        "note": "the same symmetric rule applied to the factorial lengths · endpoint (0, 0)",
    }


PANELS = [factorial_panel(), triangular_panel(),
          closure_panel(4, "S3"), closure_panel(6, "S4"), factor_closure_panel()]


CSS = """
:root{--paper:#fbf7ec;--ink:#2e2413;--muted:#7b6c4e;--rule:#d8ccae}
*{box-sizing:border-box} body{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}
main{max-width:1120px;margin:0 auto;padding:34px 22px 70px}
.eyebrow{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}
h1{font-size:31px;line-height:1.12;margin:0 0 8px} h2{font-size:20px;margin:0 0 8px}
.lede{max-width:920px;color:var(--muted)}
.panel{background:var(--paper);border:1px solid var(--rule);padding:16px 18px;margin:0 0 18px}
table{border-collapse:collapse;font:12px/1.5 ui-monospace,Menlo,monospace;margin:10px 0;width:100%}
th,td{border:1px solid var(--rule);padding:5px 8px;text-align:right} th{color:var(--muted);font-weight:400}
.small{font:12px/1.6 ui-monospace,Menlo,monospace;color:var(--muted)}
.rule{background:#fffdf7;border-left:4px solid #c9a441;padding:12px 16px;margin:0 0 18px}
code{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}
"""


def build():
    cards = "".join(
        f"""<section class="panel"><h2>{p['title']}</h2>
{figure(p['pts'], back=p['back'], labels=p['labels'],
        title=p['title'], note=p['note'])}</section>""" for p in PANELS)

    rows = "".join(
        f"<tr><td>{p['key']}</td><td>{len(p['pts']) - 1}</td>"
        f"<td>{p['pts'][-1]}</td>"
        f"<td>{'closed' if p['back'] and p['back'][-1] == (0, 0) else 'open'}</td></tr>"
        for p in PANELS)

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sequence curves · factorials, triangulars, symmetric closure</title>
<style>{CSS}</style></head><body><main>
<p class="eyebrow">curve-lab · sequence curves</p>
<h1>Sequence curves on the integer lattice</h1>
<p class="lede">Five right-angle walks whose segment lengths come from a number sequence.
The factorials give 24, 6, 2, 1; the triangular sums give T₄ = 10, T₃ = 6, T₂ = 3, T₁ = 1.
Every vertex is integer because every step is an integer length along an axis.</p>

<div class="rule"><strong>The symmetric closure.</strong> The schedule
<code>1, 2, …, n, −n, …, −1</code> closes exactly and returns to the origin. The return
repeats each chord in reverse with the opposite sign, so the displacement cancels pairwise:
<code>Σ L k = −Σ L k = 0</code>. The two passes share the same chords, so the return
is drawn dashed on top of the outward pass. This is a closed walk, not a
non-overlapping polygon; the point is the exact integer closure.</div>

{cards}

<section class="panel">
<h2>The closure ledger</h2>
<table><tr><th>figure</th><th>steps</th><th>endpoint</th><th>state</th></tr>{rows}</table>
<p class="small">Re-derive: <code>python scripts/sequence_curves.py</code> ·
test: <code>python -m unittest tests.test_sequence_curves</code></p>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "sequence-curves.html"
    out.write_text(html, encoding="utf-8")
    print(out)
    return out


if __name__ == "__main__":
    build()
