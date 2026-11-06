"""Stem offset catalogue — two rails per stalk, with the option set shown.

    .venv/bin/python scripts/stem_offset_library.py
    open workbench/stem-library-offset.html

Each card is a stalk and its two rails at ±d. The rails are 2d apart; the card
gutter is the breathing room. Formulaic curves come first, then the conics,
then the LAC chain rails, then a two-stalk card.

Three offset options are shown where the source allows:

- the exact normal rail (PH is exact; the other normal rails are the sampled
  exact parallel, not a fitted claim);
- Levien's fitted cubic-Bézier parallel (`curve_lab/parallel_bezier.py`);
- the LAC/chain rail (`design_from_spans` -> `build_rail`).

The Levien rail is a fitted option, never exact. The page reports the fit error
and the cusp/fold count.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from grid_view import crossings, grid_lines, nice_step  # noqa: E402
import generators as G  # noqa: E402
from curve_lab import engine  # noqa: E402
from curve_lab.interpolate import design_from_spans  # noqa: E402
from curve_lab.offsets import build_rail  # noqa: E402
from curve_lab.parallel_bezier import fit_chain  # noqa: E402

INK = "#2e2413"
BLUE = "#1f5fa8"
RED = "#b23a2b"
GOLD = "#c9a441"
MUTED = "#7b6c4e"
PAPER = "#fffdf7"
GRID = "#e4dcc6"

CARDS: list[dict] = []


def sample(fn, t0, t1, n=360):
    return [fn(t0 + (t1 - t0) * i / n) for i in range(n + 1)]


def bbox(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def size(points):
    x0, y0, x1, y1 = bbox(points)
    return math.hypot(x1 - x0, y1 - y0) or 1.0


def normal_offsets(points, d):
    """Two rails at signed normal distance d; left normal is +."""
    out_plus, out_minus = [], []
    n = len(points) - 1
    for i, p in enumerate(points):
        a = points[max(0, i - 1)]
        b = points[min(n, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy) or 1e-12
        nx, ny = -dy / length, dx / length
        out_plus.append((p[0] + d * nx, p[1] + d * ny))
        out_minus.append((p[0] - d * nx, p[1] - d * ny))
    return out_plus, out_minus


def flip_spans(spans):
    def f(p):
        return (p[0], -p[1])
    return [{"p0": f(s["p0"]), "c1": f(s["c1"]),
             "c2": f(s["c2"]), "p3": f(s["p3"])} for s in spans]


def spans_points(spans, per=18):
    points = []
    for s in spans:
        for i in range(per):
            t = i / per
            mt = 1 - t
            x = (mt ** 3 * s["p0"][0] + 3 * mt * mt * t * s["c1"][0]
                 + 3 * mt * t * t * s["c2"][0] + t ** 3 * s["p3"][0])
            y = (mt ** 3 * s["p0"][1] + 3 * mt * mt * t * s["c1"][1]
                 + 3 * mt * t * t * s["c2"][1] + t ** 3 * s["p3"][1])
            points.append((x, y))
    points.append(spans[-1]["p3"])
    return points


def add_card(section, label, title, source, note, base, d,
             plus=None, minus=None, fit=None, extra=None, meta=None):
    card = dict(section=section, label=label, title=title, source=source,
                note=note, base=base, d=d,
                plus=plus, minus=minus, fit=fit, extra=extra or [],
                **(meta or {}))
    CARDS.append(card)
    return card


def formulaic(section, label, title, source, note, points, factor=0.07):
    d = factor * size(points)
    plus, minus = normal_offsets(points, d)
    add_card(section, label, title, source, note.format(d=d, sep=2 * d),
             points, d, plus, minus)


def cubic_spans_from_preset(spec):
    item = G.build_preset(spec)
    scale = item["scale"]
    cps = item["cps"]
    pts = [(x / scale, y / scale) for x, y in cps]
    return [{"p0": pts[0], "c1": pts[1], "c2": pts[2], "p3": pts[3]}]


def cubic_card(section, label, title, source, spans, note):
    base = spans_points(spans)
    d = 0.08 * size(base)
    plus, minus = normal_offsets(base, d)
    fit = fit_chain(spans, d, tol=0.006)
    fit_points = spans_points(fit["spans"])
    add_card(section, label, title, source,
             note.format(d=d, sep=2 * d, err=fit["error_max"],
                         cusps=len(fit["cusps"])),
             base, d, plus, minus, fit_points, extra=fit["spans"],
             meta={"fit_error": fit["error_max"],
                   "cusps": len(fit["cusps"]),
                   "clamped": fit["clamped"]})


def lac_spans(index):
    data = json.loads((ROOT / "workbench" / "spirals" / "lac.json")
                      .read_text(encoding="utf-8"))
    fig = data["figures"][index]
    return fig["title"], flip_spans(fig["spines"][0]["spans"])


def lac_card(section, label, title, index):
    title, spans = lac_spans(index)
    design = design_from_spans(spans, name=title)
    chain = engine.build(design)
    rmin, _ = chain.min_radius()
    base = spans_points(spans)
    d = min(0.035 * size(base), 0.55 * rmin)
    plus_rail = build_rail(chain, d, tol=0.01)
    minus_rail = build_rail(chain, -d, tol=0.01)
    plus = spans_points(plus_rail["spans"])
    minus = spans_points(minus_rail["spans"])
    fit = fit_chain(spans, d, tol=0.008)
    fit_points = spans_points(fit["spans"])
    folds = len(plus_rail["folds"]) + len(minus_rail["folds"])
    add_card(section, label, title, "LAC spine · design_from_spans → build_rail",
             f"±{d:.2f} · 2× = {2*d:.2f} · chain error {plus_rail['error_max']:.3f} · "
             f"Levien error {fit['error_max']:.3f} · folds {folds}",
             base, d, plus, minus, fit_points,
             extra=plus_rail["spans"] + minus_rail["spans"],
             meta={"chain_error": plus_rail["error_max"],
                   "fit_error": fit["error_max"], "folds": folds,
                   "cusps": len(fit["cusps"])})


def build():
    if CARDS:
        return
    # Formulaic / classical families.
    cubic = cubic_spans_from_preset(G.PRESETS[0])
    cubic_card("Formulaic", "OffS1", "PH cubic · exact rail + Levien fit",
               "generators preset cubic · PH",
               cubic,
               "±{d:.3f} · 2× = {sep:.3f} · Levien error {err:.4f} · cusps {cusps}")

    log = sample(lambda t: (math.exp(0.18 * t) * math.cos(t),
                            math.exp(0.18 * t) * math.sin(t)), 0.0, 4 * math.pi)
    formulaic("Formulaic", "OffS2", "log spiral · exact family rail",
              "r = a e^{bθ} · the offset is another log spiral",
              "±{d:.3f} · 2× = {sep:.3f} · normal offset, sampled for drawing", log)

    inv = sample(lambda t: (math.cos(t) + t * math.sin(t),
                            math.sin(t) - t * math.cos(t)), 0.15, 2.5 * math.pi)
    formulaic("Formulaic", "OffS3", "circle involute · exact family rail",
              "x = cos t + t sin t, y = sin t − t cos t",
              "±{d:.3f} · 2× = {sep:.3f} · offset is another involute of the same circle", inv)

    cyc = sample(lambda t: (t - math.sin(t), 1 - math.cos(t)), 0.15, 2 * math.pi - 0.15)
    formulaic("Formulaic", "OffS4", "cycloid · fitted normal rail",
              "one arch · stem S69",
              "±{d:.3f} · 2× = {sep:.3f} · normal offset; the evolute is a cycloid, the parallel is not", cyc)

    cat = sample(lambda t: (t, math.cosh(t)), 0.0, 2.0)
    formulaic("Formulaic", "OffS5", "½ catenary · fitted normal rail",
              "x∈[0,2] · stem S166",
              "±{d:.3f} · 2× = {sep:.3f} · normal offset; the tractrix is the evolute, not the parallel", cat)

    hcyc = sample(lambda t: (t - math.sin(t), 1 - math.cos(t)), 0.0, math.pi)
    formulaic("Formulaic", "OffS6", "½ cycloid · fitted normal rail",
              "t∈[0,π] · stem S167",
              "±{d:.3f} · 2× = {sep:.3f} · normal offset; the evolute is a cycloid", hcyc)

    # Parallel conics.
    par = sample(lambda t: (t, t * t), -1.4, 1.4)
    formulaic("Conics", "OffS7", "parallel parabola",
              "y = t² · the evolute is the semicubical parabola",
              "±{d:.3f} · 2× = {sep:.3f} · algebraic, not rational; fitted normal rail", par)

    ell = sample(lambda t: (math.cos(t), 0.62 * math.sin(t)), 0.0, 2 * math.pi)
    formulaic("Conics", "OffS8", "parallel ellipse",
              "x = cos t, y = 0.62 sin t · evolute is the astroid",
              "±{d:.3f} · 2× = {sep:.3f} · fitted normal rail", ell)

    hyp = sample(lambda t: (math.cosh(t), math.sinh(t)), -1.2, 1.2)
    formulaic("Conics", "OffS9", "parallel hyperbola",
              "x = cosh t, y = sinh t",
              "±{d:.3f} · 2× = {sep:.3f} · fitted normal rail", hyp)

    # LAC chain rails. Pick the p=1 plates: a clean log-spiral-like member.
    lac_card("LAC", "OffS10", "LAC p=1 · turn 270 · chain rail", 7)
    lac_card("LAC", "OffS11", "LAC p=1 · turn 360 · chain rail", 17)

    # Two stalks: envelopes separated by 2d + a breathing gap.
    base = cubic_spans_from_preset(G.PRESETS[2])
    base_points = spans_points(base)
    d = 0.08 * size(base_points)
    gap = 0.45 * d
    sep = 2 * d + gap
    a = base_points
    b = [(x + sep, y) for x, y in base_points]
    pa, ma = normal_offsets(a, d)
    pb, mb = normal_offsets(b, d)
    # one card, four rails + two bases; re-use the curve slots via extra
    add_card("Multiple", "OffS12", "two stalks · envelopes separated",
             "two PH cubics · 2d + breathing room",
             f"±{d:.3f} · 2× = {2*d:.3f} · envelope gap {gap:.3f} · centre separation {sep:.3f}",
             a + [None] + b, d, pa, ma,
             extra=[(b, INK, None, 2.2), (pb, BLUE, None, 1.2),
                    (mb, RED, None, 1.2)])


def figure(card, w=300, h=200):
    curves = []
    if card["base"] and None not in card["base"]:
        curves.append((card["base"], INK, None, 2.2))
    elif card["base"]:
        # two stems separated by a None marker
        i = card["base"].index(None)
        curves.append((card["base"][:i], INK, None, 2.2))
        curves.append((card["base"][i + 1:], INK, None, 2.2))
    curves += [(card["plus"], BLUE, None, 1.2),
               (card["minus"], RED, None, 1.2)]
    if card["fit"]:
        curves.append((card["fit"], GOLD, "5 4", 1.3))
    for item in card["extra"]:
        if isinstance(item, tuple) and len(item) >= 3 and isinstance(item[0], list):
            curves.append((item[0], item[1], item[2] if len(item) > 2 else None,
                           item[3] if len(item) > 3 else 1.2))
    allpoints = [p for c in curves for p in c[0]]
    x0, y0, x1, y1 = bbox(allpoints)
    pad = 0.09
    dx, dy = (x1 - x0) or 1, (y1 - y0) or 1
    x0, x1 = x0 - pad * dx, x1 + pad * dx
    y0, y1 = y0 - pad * dy, y1 + pad * dy
    k = min((w - 14) / (x1 - x0), (h - 14) / (y1 - y0))
    ox = (w - (x1 - x0) * k) / 2
    oy = (h - (y1 - y0) * k) / 2

    def put(p):
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k)

    step = nice_step(max(x1 - x0, y1 - y0))
    body = grid_lines(put, x0, x1, y0, y1, step, "#efe7d2")
    body += [f'<circle class="lattice" cx="{put(q)[0]:.1f}" '
             f'cy="{put(q)[1]:.1f}" r="2.0" fill="{GOLD}"/>'
             for q in crossings([c[0] for c in curves if not c[2]], step)]
    for pts, colour, dash, width in curves:
        d = " ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in pts)
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        body.append(f'<path d="M {d}" fill="none" stroke="{colour}" '
                    f'stroke-width="{width}" stroke-linejoin="round"{dash_attr}/>')
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{w}" height="{h}" fill="{PAPER}" stroke="{GRID}"/>'
            + "".join(body) + "</svg>")


def main():
    build()
    groups = []
    for card in CARDS:
        if not groups or groups[-1][0] != card["section"]:
            groups.append((card["section"], []))
        groups[-1][1].append(card)
    sections = []
    for section, cards in groups:
        rows = []
        for card in cards:
            rows.append(f'''<section class="card">
  <div class="art">{figure(card)}</div>
  <h3><span class="idx">{card['label']}</span> {card['title']}</h3>
  <p class="src">{card['source']}</p>
  <p class="note">{card['note']}</p>
</section>''')
        sections.append(f'<h2 class="group">{section} <span>{len(cards)}</span></h2>'
                        f'<div class="grid">{"".join(rows)}</div>')
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Stem offsets — two rails, 2× apart</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1160px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 20px}}
.group{{font:600 12px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.10em;
text-transform:uppercase;color:{MUTED};margin:32px 0 10px}}
.group span{{color:#b09a6a;font-weight:400}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}
.card{{background:{PAPER};border:1px solid #d8ccae;padding:10px}}
.art{{margin:0 0 8px}}
svg{{display:block;width:100%;height:auto}}
h3{{font:600 12px/1.35 Georgia,serif;margin:0 0 3px}}
.idx{{font:11px ui-monospace,Menlo,monospace;color:{RED};margin-right:4px}}
.src,.note{{font:10px/1.35 ui-monospace,Menlo,monospace;color:{MUTED};margin:0}}
.note{{color:#a08a64}}
.panel{{background:{PAPER};border:1px solid #d8ccae;padding:16px 18px;margin:0 0 18px}}
.legend{{display:flex;gap:18px;flex-wrap:wrap;font:11px ui-monospace,Menlo,monospace;
color:{MUTED};margin:0 0 14px}}
.sw{{display:inline-block;width:22px;height:0;border-top:3px solid {INK};margin-right:6px;vertical-align:middle}}
.sw.b{{border-top:2px solid {BLUE}}}.sw.r{{border-top:2px solid {RED}}}
.sw.g{{border-top:2px dashed {GOLD}}}
a{{color:#8c6a21}}
</style></head><body><main>
<h1>Stem offsets</h1>
<p class="lead">One stalk, two rails. The rails stand at ±d, so they are
<strong>2d apart</strong>; the card gutter is the breathing room. The catalogue
shows the exact normal rail where it is exact, Levien's fitted cubic-Bézier
parallel (gold dash), and the LAC chain rail.</p>
<div class="panel">
<p><strong>The rule.</strong> Every card is one stalk with two offsets at
±d. A rail folds when d reaches the local centre of curvature; the LAC cards
choose d below the minimum radius and report the margin. The Levien fit is an
option, never an exact claim: its error is the maximum distance between the
fitted cubic chain and the dense exact normal offset. The exact PH offset is
the PH rail; the LAC rail is the clothoid-chain fit; the formulaic/conic rails
are the sampled normal offset unless the family closes under offsetting.</p>
<p><strong>Offset tiers.</strong> exact PH/arcs · exact-in-family log spiral and
circle involute · Levien fitted cubic Bézier · LAC/chain rail · sampled.
Reference: <a href="../reference/external/parallel-beziers.html">Levien,
“Parallel curves of cubic Béziers”</a>.</p>
</div>
<div class="legend">
<span><i class="sw"></i> stalk</span>
<span><i class="sw b"></i> +d rail</span>
<span><i class="sw r"></i> −d rail</span>
<span><i class="sw g"></i> Levien fitted cubic</span>
</div>
{"".join(sections)}
</main></body></html>
'''
    out = ROOT / "workbench" / "stem-library-offset.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    print(f"  {len(CARDS)} cards")
    for card in CARDS:
        print(f"  {card['label']} {card['title']}  d={card['d']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
