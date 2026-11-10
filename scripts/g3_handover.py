"""Every G3-complete curve as a panel: the curve left, d(kappa)/ds right.

    .venv/bin/python scripts/g3_handover.py
    open workbench/g3-handover.html

The panels are built from `g3_catalogue.catalogue()`, so the curves, the
acceleration graphs and the badges are the catalogue's own data, not a copy.
Curves are grouped by source; within a group the smooth handover rows come
first, then the rows that are complete with a declared cusp or node.

Coordinates are model coordinates with +y up. The SVG writer flips y at
output, which is the only place the flip happens.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import g3_catalogue as C  # noqa: E402
import g3_showcase as S  # noqa: E402

PAPER, INK, MUTED, GOLD = S.PAPER, S.INK, S.MUTED, S.GOLD
BLUE, RED, RULE, GREEN = S.BLUE, S.RED, S.RULE, S.GREEN
RED_MARK = "#e01b1b"   # brighter than the text red, for the diagnostic marks

EXTRA_CSS = """
.grid{display:grid;grid-template-columns:1fr;gap:0}
.group{margin:30px 0 10px;padding-top:10px;border-top:1px solid var(--rule)}
.zoom-btn{float:right;font:10px/1.6 ui-monospace,Menlo,monospace;letter-spacing:.08em;
  text-transform:uppercase;color:var(--muted);background:transparent;
  border:1px solid var(--rule);padding:1px 8px;border-radius:2px;cursor:pointer}
.zoom-btn:hover{color:var(--ink);border-color:var(--ink)}
.panel.zoom .panel-grid{grid-template-columns:1fr}
.panel.zoom .main,.panel.zoom .side{overflow:auto}
.panel.zoom .main svg{width:240%;max-width:none}
.panel.zoom .side svg{width:200%;max-width:none}
.fix{margin:8px 0 0;padding:7px 10px;border-left:3px solid var(--rule);
  font:12px/1.55 ui-monospace,Menlo,monospace}
.fix strong{font-weight:400;text-transform:uppercase;letter-spacing:.06em}
.fix.verified,.fix.fixed{border-left-color:#2f6b3a;color:#2f6b3a}
.fix.needs-fix,.fix.needs-eye{border-left-color:#8a5a00;color:#8a5a00}
"""

TIGHT_SPEED = 0.25   # advisory only; never a red defect mark

# Visible status on the affected figures. Status is one of:
#   verified  — no rendering defect; the measurements pass
#   fixed     — a concrete correction has been made
#   needs-fix — a concrete correction is still to be made (I can do it)
#   needs-eye — needs the operator's description/decision
FIX_NOTES = {
    "S44 · Fig. 6 · LAC: p = 0, turn 270":
        ("fixed", "Source cubic chain, 5.63e-8; S44 label; no quintic."),
    "Stage II · Fig. 11 · Arc, Euler, line, Euler, arc · spine 3":
        ("verified", "G3 joins below 1e-12; deviation 0.30%. The old red was a "
                     "speed heuristic. If it still looks wrong, describe the point."),
    "Stage II · Fig. 13 · Log spiral, one turn each way · spine 3":
        ("verified", "G3 joins below 1e-12; deviation 0.74%; no defect."),
    "Stage II · Fig. 14 · Involute, one turn each way · spine 3":
        ("verified", "G3 joins below 1e-12; deviation 0.67%; no defect."),
    "Stage II · Fig. 16 · Log spiral, two turns each way · spine 2":
        ("verified", "G3 joins below 1e-12; deviation 0.80%; no defect."),
    "Stage II · Fig. 19 · Log spiral, both ends · spine 3":
        ("verified", "G3 joins below 1e-12; deviation 0.68%; no defect."),
    "Stage II · Fig. 20 · Involute, both ends · spine 3":
        ("verified", "G3 joins below 1e-12; deviation 0.69%; no defect."),
    "Stage II · Fig. 5 · The S branch · spine 3":
        ("verified", "G3 joins below 1e-12; deviation 0.60%; no defect."),
    "Stage II · Fig. 5 · The S branch · spine 5":
        ("verified", "G3 joins below 1e-12; deviation 0.60%; no defect."),
    "Stage II · Fig. 6 · The S root · spine 4":
        ("verified", "G3 joins below 1e-12; deviation 0.60%; no defect."),
    "Stage II · Fig. 6 · The S root · spine 6":
        ("verified", "G3 joins below 1e-12; deviation 0.62%; no defect."),
    "misc · Maclaurin trisectrix · exact loop":
        ("verified", "G3 joins below 1e-10; deviation 0.80%; no defect."),
    "misc · Pell · x² − 2y² = 1 · +":
        ("verified", "G3 joins below 1e-11; deviation 0.32%; no defect."),
    "misc · Pell · x² − 2y² = 1 · −":
        ("verified", "G3 joins below 1e-11; deviation 0.32%; no defect."),
    "misc · Reuleaux triangle":
        ("verified", "G3 joins below 1e-9; deviation 0.86%; no defect."),
    "misc · catenary":
        ("verified", "G3 joins below 1e-14; deviation 0.17%; no defect."),
    "bicorn":
        ("fixed", "cusp ×2 (was recorded as a node); admitted cusp, green."),
    "deltoid":
        ("fixed", "cusp ×3; admitted cusp, green."),
    "epicycloid k=3":
        ("fixed", "cusp ×4; admitted cusp, green."),
    "epicycloid k=5":
        ("fixed", "cusp ×6; admitted cusp, green."),
    "hypocycloid k=5":
        ("fixed", "cusp ×5; admitted cusp, green."),
    "heart · Eisemann lower":
        ("needs-eye", "Cusp-aware fit restored; cusp declared. The cusp is the "
                      "junction with the upper half; say if the sibling should be drawn."),
    "heart · Hechinger lower":
        ("needs-eye", "Cusp-aware fit restored; cusp declared. Same half-heart "
                      "junction question."),
    "heart · Kuriscak lower":
        ("needs-eye", "Cusp-aware fit restored; the cusp is at the end. Confirm the "
                      "expected tangent or draw the sibling."),
    "heart · Mangaldan":
        ("needs-eye", "cusp ×2; the better 0.0226 fit is restored. The cusp "
                      "locations need your eye."),
    "heart · Valentine":
        ("needs-eye", "cusp ×2; the better 0.331 fit is restored. The cusp "
                      "locations need your eye."),
    "heart · |x|^(2/3) upper":
        ("needs-fix", "Interior cusp at x=0 is smoothed; split into two arcs."),
    "heart · |x|^(2/3) lower":
        ("needs-fix", "Interior cusp at x=0 is smoothed; split into two arcs."),
}

GROUPS = [
    ("named", "Named curves"),
    ("heart", "Heart forms"),
    ("integer-cubic", "Integer cubics"),
    ("preset", "Presets"),
    ("primal", "Primals"),
    ("lac", "LAC spines"),
    ("stage-two", "Stage II spines"),
    ("misc", "Other families"),
    ("cusp", "Cusp-arc curves"),
]


def _grid(f, x0, x1, y0, y1, step):
    out = []
    gx = math.floor(x0 / step) * step
    while gx <= x1:
        a, b = f((gx, y0)), f((gx, y1))
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                   f'y2="{b[1]:.1f}" stroke="{RULE}" stroke-width="0.6"/>')
        gx += step
    gy = math.floor(y0 / step) * step
    while gy <= y1:
        a, b = f((x0, gy)), f((x1, gy))
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                   f'y2="{b[1]:.1f}" stroke="{RULE}" stroke-width="0.6"/>')
        gy += step
    return "".join(out)


def is_tight(row):
    """A red ring is only for a tight smooth span, never a declared feature."""
    ms = row.get("min_speed")
    return (isinstance(ms, (int, float)) and ms < TIGHT_SPEED
            and not row.get("feature"))


def worst_problem(row):
    probs = [(i, b["problem"]) for i, b in enumerate(row.get("branches", []))
             if b.get("problem")]
    if not probs:
        return None
    return min(probs, key=lambda item: item[1]["ratio"])


def curve_svg(row, w=560, h=360, mark=False, fig=None):
    """The curve: ideal dashed, G3 spans solid, joins circled, axis labels."""
    branches = row["branches"]
    pts = [p for br in branches for p in br["ideal"]]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = 0.08 * max(x1 - x0, y1 - y0, 1e-6)
    f = S.Frame(w, h, x0 - pad, x1 + pad, y0 - pad, y1 + pad, pad=46)
    step = S._nice_step(max(x1 - x0, y1 - y0))

    ground_y = y0 - 0.45 * pad
    ga, gb = f((x0 - pad, ground_y)), f((x1 + pad, ground_y))

    body = []
    for br in branches:
        body.append(f'<path d="{S._path(br["ideal"], f)}" fill="none" '
                    f'stroke="{MUTED}" stroke-width="1.1" stroke-dasharray="4 4"/>')
        samples = []
        for P in br["spans"]:
            samples.extend(S.bezier(P, i / 40.0) for i in range(41))
        body.append(f'<path d="{S._path(samples, f)}" fill="none" '
                    f'stroke="{INK}" stroke-width="2.2"/>')
        for P in br["spans"]:
            X, Y = f(S.bezier(P, 0.0))
            body.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="3.0" '
                        f'fill="none" stroke="{GREEN}" stroke-width="1.3"/>')

    if mark:
        wp = worst_problem(row)
        if wp:
            _, p = wp
            X, Y = f(p["point"])
            body.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="15" '
                        f'fill="none" stroke="{GOLD}" stroke-width="4.2"/>')
            body.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="5.5" fill="{GOLD}"/>')
            lx = min(max(X + 17, 8), w - 205)
            ly = min(max(Y - 15, 58), h - 46)
            body.append(f'<text x="{lx:.1f}" y="{ly:.1f}" '
                        f'font-family="ui-monospace,Menlo,monospace" font-size="12" '
                        f'fill="{GOLD}">tightest · {p["ratio"]:.1%} of chord speed</text>')

    if mark:
        badge, col = f"tightest {row.get('min_speed', 0):.1%}", GOLD
    elif row.get("smooth"):
        badge, col = "smooth handover", GREEN
    else:
        badge, col = f"declared: {row.get('feature') or 'feature'}", GOLD
    nspans = row.get("spans") or sum(len(b["spans"]) for b in branches)
    rel = row.get("relative")
    rel_s = f"{rel:.1%}" if isinstance(rel, (int, float)) else "—"
    g3v = row.get("g3")
    g3_s = f"{g3v:.1e}" if isinstance(g3v, (int, float)) else "—"
    sub = (f"{nspans} spans · {len(branches)} path"
           f"{'s' if len(branches) != 1 else ''} · deviation "
           f"{rel_s} · worst Δ(dκ/ds) {g3_s}")
    zero = []
    if x0 - pad <= 0.0 <= x1 + pad:
        a, b = f((0.0, y0 - pad)), f((0.0, y1 + pad))
        zero.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                    f'y2="{b[1]:.1f}" stroke="{BLUE}" stroke-width="1" '
                    f'stroke-dasharray="4 3"/>')
        zero.append(f'<text x="{a[0] + 4:.1f}" y="{a[1] - 4:.1f}" '
                    f'font-family="ui-monospace,Menlo,monospace" font-size="9" '
                    f'fill="{BLUE}">x=0</text>')
    if y0 - pad <= 0.0 <= y1 + pad:
        a, b = f((x0 - pad, 0.0)), f((x1 + pad, 0.0))
        zero.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                    f'y2="{b[1]:.1f}" stroke="{BLUE}" stroke-width="1" '
                    f'stroke-dasharray="4 3"/>')
        zero.append(f'<text x="{a[0] + 4:.1f}" y="{a[1] - 4:.1f}" '
                    f'font-family="ui-monospace,Menlo,monospace" font-size="9" '
                    f'fill="{BLUE}">y=0</text>')
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{row['key']} · G3 interpolation">
  <rect width="{w}" height="{h}" fill="{PAPER}"/>
  {_grid(f, x0 - pad, x1 + pad, y0 - pad, y1 + pad, step)}
  {''.join(zero)}
  {''.join(body)}
  <line x1="{ga[0]:.1f}" y1="{ga[1]:.1f}" x2="{gb[0]:.1f}" y2="{gb[1]:.1f}" stroke="{INK}" stroke-width="1"/>
  <text x="{ga[0] + 4:.1f}" y="{ga[1] + 12:.1f}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{MUTED}">ground</text>
  <text x="14" y="24" font-family="Georgia,serif" font-size="15" fill="{INK}">Fig. {fig if fig is not None else 'H'} · {row['key']}</text>
  <text x="14" y="43" font-family="ui-monospace,Menlo,monospace" font-size="10.5" fill="{MUTED}">{sub}</text>
  <text x="{w - 14}" y="24" text-anchor="end" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{col}">{badge}</text>
  <text x="{w / 2:.0f}" y="{h - 10}" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="{MUTED}">x (model units)</text>
  <text x="15" y="{h / 2:.0f}" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="{MUTED}" transform="rotate(-90 15 {h / 2:.0f})">y (model units)</text>
  <g font-family="Georgia,serif" font-size="11">
    <line x1="14" y1="{h - 28}" x2="42" y2="{h - 28}" stroke="{MUTED}" stroke-width="1.1" stroke-dasharray="4 4"/><text x="48" y="{h - 24}" fill="{INK}">ideal</text>
    <line x1="96" y1="{h - 28}" x2="124" y2="{h - 28}" stroke="{INK}" stroke-width="2.2"/><text x="130" y="{h - 24}" fill="{INK}">G3</text>
    <circle cx="168" cy="{h - 28}" r="3" fill="none" stroke="{GREEN}" stroke-width="1.3"/><text x="177" y="{h - 24}" fill="{INK}">join</text>
  </g>
</svg>"""


def accel_svg(row, w=380, h=240, mark=False):
    """d(kappa)/ds along each path; branch breaks are declared, not joins."""
    branches = row["branches"]
    segs = []            # (offset, length, xs, vals)
    lengths = []
    for br in branches:
        xs, vals = [], []
        s = 0.0
        prev = None
        for P in br["spans"]:
            for i in range(41):
                q = S.bezier(P, i / 40.0)
                if prev is not None:
                    s += math.dist(prev, q)
                xs.append(s)
                vals.append(S.curvature_rate(P, i / 40.0))
                prev = q
        lengths.append(s)
    gap = 0.03 * (sum(lengths) or 1.0)
    problem_marks = []
    offset = 0.0
    for br, length in zip(branches, lengths):
        xs, vals = [], []
        s = 0.0
        prev = None
        for P in br["spans"]:
            for i in range(41):
                q = S.bezier(P, i / 40.0)
                if prev is not None:
                    s += math.dist(prev, q)
                xs.append(offset + s)
                vals.append(S.curvature_rate(P, i / 40.0))
                prev = q
        segs.append((offset, length, xs, vals))
        if mark and br.get("problem"):
            p = br["problem"]
            idx = min(range(len(xs)),
                      key=lambda i: abs((xs[i] - offset) - p["s"]))
            problem_marks.append((xs[idx], vals[idx], p))
        offset += length + gap

    if problem_marks:
        problem_marks = [min(problem_marks, key=lambda item: item[2]["ratio"])]
    total = offset - gap if segs else 1.0
    finite = sorted(v for _o, _l, _xs, vs in segs for v in vs
                    if math.isfinite(v))

    def pct(q):
        return finite[min(len(finite) - 1, max(0, int(q * (len(finite) - 1))))]

    # A declared cusp or a trimmed singular endpoint can spike dκ/ds by many
    # orders of magnitude. The body is read on the 2–98% band; spikes are
    # clipped and the title says so.
    lo, hi = pct(0.02), pct(0.98)
    if hi - lo < 1e-12:
        lo, hi = lo - 1.0, hi + 1.0
    pad = 0.12 * (hi - lo)
    y0, y1 = lo - pad, hi + pad
    clipped = any(v < y0 or v > y1 for v in finite)
    left, right, top, bottom = 44, 14, 30, 30

    def gx(x):
        return left + (x / total) * (w - left - right)

    def gy(y):
        return (h - bottom) - (y - y0) / (y1 - y0) * (h - top - bottom)

    grid = []
    for k in range(6):
        y = y0 + (y1 - y0) * k / 5
        grid.append(f'<line x1="{left}" y1="{gy(y):.1f}" x2="{w - right}" '
                    f'y2="{gy(y):.1f}" stroke="{RULE}" stroke-width="0.6"/>')
        grid.append(f'<text x="{left - 4}" y="{gy(y) + 3:.1f}" text-anchor="end" '
                    f'font-family="ui-monospace,Menlo,monospace" font-size="9" '
                    f'fill="{MUTED}">{y:.1f}</text>')
    if y0 < 0 < y1:
        grid.append(f'<line x1="{left}" y1="{gy(0):.1f}" x2="{w - right}" '
                    f'y2="{gy(0):.1f}" stroke="{BLUE}" stroke-width="1" stroke-dasharray="3 3"/>')

    marks = []
    for offset_, length, xs, vals in segs:
        # internal span boundaries only; the branch end is a declared break,
        # not a body join.
        for s in xs[40:-1:40]:
            marks.append(f'<line x1="{gx(s):.1f}" y1="{top}" x2="{gx(s):.1f}" '
                         f'y2="{h - bottom}" stroke="{GREEN}" stroke-width="0.7" stroke-dasharray="2 3"/>')
    break_marks = []
    for offset_, length, xs, vals in segs[:-1]:
        x = gx(offset_ + length + gap / 2)
        break_marks.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" '
                           f'y2="{h - bottom}" stroke="{GOLD}" stroke-width="1.1" stroke-dasharray="4 3"/>')
        break_marks.append(f'<text x="{x + 2:.1f}" y="{top + 9}" font-family="ui-monospace,Menlo,monospace" font-size="8" fill="{GOLD}">break</text>')

    paths = []
    for offset_, length, xs, vals in segs:
        pts = [(gx(x), min(max(gy(v), top), h - bottom))
               for x, v in zip(xs, vals) if math.isfinite(v)]
        if len(pts) < 2:
            continue
        d = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}"
                     for i, (x, y) in enumerate(pts))
        paths.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="2"/>')

    red = []
    for px, pv, p in problem_marks:
        X = gx(px)
        Y = min(max(gy(pv), top + 13), h - bottom - 13)
        red.append(f'<line x1="{X:.1f}" y1="{top}" x2="{X:.1f}" '
                   f'y2="{h - bottom}" stroke="{GOLD}" stroke-width="3.0" '
                   f'stroke-dasharray="4 3"/>')
        red.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="12" '
                   f'fill="none" stroke="{GOLD}" stroke-width="3.8"/>')

    broke = " · declared breaks marked" if len(segs) > 1 else ""
    if clipped:
        broke += " · 2–98% band, spikes clipped"
    if problem_marks:
        broke += f" · tightest {problem_marks[0][2]['ratio']:.1%} circled"
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="dκ/ds along {row['key']}">
  <rect width="{w}" height="{h}" fill="{PAPER}"/>
  {''.join(grid)}
  <line x1="{left}" y1="{top}" x2="{left}" y2="{h - bottom}" stroke="{INK}" stroke-width="1"/>
  <line x1="{left}" y1="{h - bottom}" x2="{w - right}" y2="{h - bottom}" stroke="{INK}" stroke-width="1"/>
  {''.join(marks)}
  {''.join(break_marks)}
  {''.join(red)}
  {''.join(paths)}
  <text x="10" y="18" font-family="Georgia,serif" font-size="12" fill="{INK}">dκ/ds · G3 joins{broke}</text>
  <text x="{left + (w - left - right) / 2:.0f}" y="{h - 8}" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{MUTED}">arc length s (model units, paths abut)</text>
  <text x="12" y="{top + (h - top - bottom) / 2:.0f}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{MUTED}" transform="rotate(-90 12 {top + (h - top - bottom) / 2:.0f})">dκ/ds</text>
</svg>"""


def record(row, diagnostic=False):
    if diagnostic:
        return f"""<p class="small">branches {len(row['branches'])} · tightest span
{row.get('min_speed', 0):.1%} of the chord<br>
below the 25% display threshold; the 10% floor is the admission line.<br>
Gold ring: the speed minimum on the curve. Gold line and ring: the same point on
<code>dκ/ds</code>. Use <strong>zoom</strong> to enlarge.</p>"""
    state = "smooth handover" if row.get("smooth") else f"declared: {row.get('feature') or 'feature'}"
    seam = ("seam passes" if row.get("seam_pass")
            else "seam declared")
    speed = row.get("min_speed")
    speed_s = f"{speed:.1%}" if isinstance(speed, (int, float)) else "—"
    xs = [p[0] for br in row["branches"] for p in br["ideal"]]
    ys = [p[1] for br in row["branches"] for p in br["ideal"]]
    bbox = (f"x [{min(xs):.2f}, {max(xs):.2f}] · y [{min(ys):.2f}, {max(ys):.2f}]"
            if xs else "—")
    return f"""<p class="small">branches {len(row['branches'])} · spans {row['spans']} ·
max deviation {row['relative']:.1%} · worst Δ(dκ/ds) {row['g3']:.1e}<br>
native: {row.get('native')} · {state} · {seam} · speed floor {speed_s}<br>
{bbox}<br>
G3 at every body join; the closure seam is checked, and a declared node or
cusp is named rather than counted as a failed join.</p>"""


def panel(row, ring=False, diagnostic=False, fig=None):
    zoom = ("<button class=\"zoom-btn\" "
            "onclick=\"this.closest('.panel').classList.toggle('zoom')\">"
            "zoom</button>")
    if diagnostic:
        badge = f"tightest {row.get('min_speed', 0):.1%}"
    elif row.get("smooth"):
        badge = "smooth"
    else:
        badge = row.get("feature") or "declared"
    label = f"Fig. {fig} · " if fig is not None else ""
    fix = FIX_NOTES.get(row["key"])
    fix_html = ""
    if fix:
        status, note = fix
        text = {"verified": "verified", "fixed": "fixed",
                "needs-fix": "needs fix", "needs-eye": "needs your eye"}[status]
        fix_html = (f'<p class="fix {status}"><strong>{text}</strong> · '
                    f'{note}</p>')
    return f"""<section class="panel">
<h2>{label}{row['key']} <span class="badge">{badge}</span> {zoom}</h2>
<div class="panel-grid">
<div class="main">{curve_svg(row, mark=ring, fig=fig)}</div>
<div class="side">
<div class="side-head">1 · G3 acceleration</div>
{accel_svg(row, mark=ring)}
<div class="side-head">2 · the record</div>
{record(row, diagnostic=diagnostic)}
</div>
</div>
{fix_html}
</section>"""


def row_problem(row):
    wp = worst_problem(row)
    if not wp:
        return None
    bi, p = wp
    return {"branch": bi, "span": p["span"], "t": p["t"],
            "point": [p["point"][0], p["point"][1]],
            "s": p["s"], "ratio": p["ratio"]}


def gallery_payload(fig_start=None):
    """The grouped gallery sections and counts, shared by both pages.

    fig_start numbers the panels consecutively on the combined showcase; the
    standalone handover page leaves them as Fig. H.
    """
    rows = C.catalogue_cached()
    complete = [r for r in rows if r.get("g3_complete")]
    smooth = [r for r in complete if r.get("smooth")]
    declared = [r for r in complete if not r.get("smooth")]
    problems = [r for r in rows if is_tight(r)]

    nav, sections = [], []
    counter = fig_start
    for src, label in GROUPS:
        items = [r for r in complete if (r.get("source") or "named") == src]
        if not items:
            continue
        items.sort(key=lambda r: (not r.get("smooth"), r["key"]))
        nav.append(f'<a href="#g-{src}">{label} · {len(items)}</a>')
        cards = []
        for r in items:
            cards.append(panel(r, fig=counter))
            if counter is not None:
                counter += 1
        sections.append(f'<h2 id="g-{src}" class="group">{label} · {len(items)}</h2>'
                        f'<div class="grid">{"".join(cards)}</div>')
    return {"rows": rows, "complete": complete, "smooth": smooth,
            "declared": declared, "problems": problems,
            "nav": nav, "sections": sections}


def build():
    payload = gallery_payload()
    rows = payload["rows"]
    complete = payload["complete"]
    smooth = payload["smooth"]
    declared = payload["declared"]
    problems = payload["problems"]
    nav = payload["nav"]
    sections = payload["sections"]

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>G3 handover · every complete curve, with its acceleration</title>
<style>{S.CSS}{EXTRA_CSS}</style></head><body><main>
<p class="eyebrow">curve-lab · G3 handover</p>
<h1>Every working curve, with its G3 acceleration</h1>
<p class="lede">The curves below are the <strong>{len(complete)} G3-complete</strong>
candidates: every body join matches position, tangent, curvature and
curvature-rate, and the closure seam is checked rather than exempt. The
<strong>{len(smooth)} smooth handover</strong> rows are one path with no declared
feature and a deviation under 5% of the curve size; the {len(declared)} others are
complete with a declared cusp, node or singular endpoint. Each panel is the curve on
the left and <code>dκ/ds</code> on the right, in the same format as the
<a href="g3-showcase.html">cubic G3 showcase</a>. Model coordinates are
<strong>+y up</strong>; the SVG writer flips y at output.</p>
<p class="small">{' · '.join(nav)}</p>

<div class="rule"><strong>How to read a panel.</strong> The dashed line is the ideal
curve, the solid line the delivered G3 chain, the green circles the joins. On the
right, <code>dκ/ds</code> is plotted against arc length; green lines are G3 joins, gold
dashed lines are declared breaks between paths (a cusp or node), and the blue dashed
line is zero. A smooth curve has one path and no gold line. A tight span is collected
on the <a href="g3-diagnostics.html">tightest-span diagnostics page</a>, where it is
ringed in <span style="color:{GOLD}">gold</span>. The gallery itself carries no ring:
red is reserved for a rejected cusp or a failing join. The record gives the deviation
as a share of the curve
size, the worst curvature-rate gap, the native degree (<em>cubic-native</em> means the
fifth divided difference vanished), the speed floor, and the declared feature if
any.</p>

<p class="small">Counts: {len(complete)} G3-complete · {len(smooth)} smooth handover ·
{len(declared)} with a declared feature · <a href="g3-diagnostics.html">tightest
spans · {len(problems)}</a> · built from
<code>g3_catalogue.catalogue()</code>; re-derive:
<code>python scripts/g3_handover.py</code>. Back to the
<a href="g3-catalogue.html">catalogue</a> ·
<a href="g3-showcase.html">showcase</a> ·
<a href="g3-notes.html">notes</a>.</p>

{''.join(sections)}
</main></body></html>
"""
    out = ROOT / "workbench" / "g3-handover.html"
    out.write_text(html, encoding="utf-8")

    data = {
        "counts": {
            "candidates": len(rows),
            "complete": len(complete),
            "smooth": len(smooth),
            "declared": len(declared),
        },
        "curves": [
            {"key": r["key"], "source": r.get("source") or "named",
             "smooth": bool(r.get("smooth")),
             "feature": r.get("feature"), "native": r.get("native"),
             "relative": r.get("relative"), "g3": r.get("g3"),
             "spans": r.get("spans")}
            for r in complete
        ],
    }
    (ROOT / "workbench" / "g3-handover.json").write_text(
        json.dumps(data, indent=1), encoding="utf-8")

    problems.sort(key=lambda r: (r.get("min_speed") or 1.0, r["key"]))
    diag_cards = "".join(panel(r, ring=True, diagnostic=True) for r in problems)
    diag = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>G3 diagnostics · the tightest spans</title>
<style>{S.CSS}{EXTRA_CSS}</style></head><body><main>
<p class="eyebrow">curve-lab · tightest-span diagnostics</p>
<h1>Tightest spans · the closest approaches, in gold</h1>
<p class="lede">A join-only test can pass two spans that each graze a near-cusp
inside: the ends match, but the span nearly stops and <code>dκ/ds</code> spikes by
orders of magnitude. The fit now rejects any span below <strong>10% of its chord
speed</strong>. These <strong>{len(problems)}</strong> working curves keep a span
below 25%: none is rejected, but they are the closest approaches that remain. The
gold ring is the speed minimum on the curve; the gold line and ring on the right are
the same point on <code>dκ/ds</code>. <strong>Zoom</strong> enlarges the panel and
lets you scroll to the mark.</p>
<p class="small">Worst first · back to the
<a href="g3-handover.html">handover gallery</a> ·
<a href="g3-catalogue.html">catalogue</a> ·
<a href="g3-showcase.html">showcase</a> · re-derive:
<code>python scripts/g3_handover.py</code>.</p>
{diag_cards or '<p class="small">No near-cusp rows in this build.</p>'}
</main></body></html>
"""
    dout = ROOT / "workbench" / "g3-diagnostics.html"
    dout.write_text(diag, encoding="utf-8")
    ddata = {"count": len(problems), "curves": [
        {"key": r["key"], "source": r.get("source") or "named",
         "min_speed": r.get("min_speed"), "reason": r.get("reason"),
         "problem": row_problem(r)} for r in problems]}
    (ROOT / "workbench" / "g3-diagnostics.json").write_text(
        json.dumps(ddata, indent=1), encoding="utf-8")
    print(dout)
    return out


if __name__ == "__main__":
    build()
