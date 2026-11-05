"""Fleur proof 01: the fleur grammar read through the plant-form rules.

    .venv/bin/python scripts/fleur_proof.py

The fleur study (`curve_lab.grammar.study_01`) is a right half, mirrored, plus
a band. This page applies the plant-form grammar to it rather than inventing a
second fleur:

- the central lance is the **stalk**;
- its 25-unit width is the two **rails** at ±12.5;
- the lance tip gets a **cone terminal** (R = 2 × offset), so the point is no
  longer bare;
- the side petal is the **branch**, and it inherits the ending rule: a
  seagrass at its tip;
- the **integer nodes** are marked, and two of them carry pyramid growth marks.

The numbers are recomputed from the grammar here and written into the page, so
the page cannot drift from the study it claims to draw.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from curve_lab import engine, grammar  # noqa: E402
from curve_lab import plant as P  # noqa: E402
from curve_lab.model import Design  # noqa: E402
import plant_forms as PF  # noqa: E402

INK, BLUE, RED, GOLD, GREEN = "#2e2413", "#1f5fa8", "#a23b2a", "#c9a441", "#2f6f4f"
MUTED, PAPER, GRID, FILL = "#7b6c4e", "#fffdf7", "#e4dcc6", "#f8efd7"

WIDTH = 25.0
OFFSET = WIDTH / 2.0
NODE_TOL = 1e-6


def _design(right):
    return Design(name="fleur right", segments=right["spans"],
                  anchor={"x": right["start"][0], "y": right["start"][1],
                          "angle": right["angle"]}, g1=True)


def _sample(chain, n=640):
    length = chain.length
    return [chain.point(length * i / (n - 1)) for i in range(n)]


def _mirror(pts):
    return [(-x, y) for x, y in pts]


def _node_marks(right):
    """Unique integer nodes: right half, its mirror, and the band corners."""
    band = grammar.band(grammar.STUDY_01)
    pts = list(right["nodes"]) + _mirror(right["nodes"]) + list(band["nodes"])
    out = []
    for x, y in pts:
        if abs(x - round(x)) < NODE_TOL and abs(y - round(y)) < NODE_TOL:
            q = (int(round(x)), int(round(y)))
            if q not in out:
                out.append(q)
    return out


def _pyramid(point, angle, offset, outward_sign, size=(34.0, 78.0)):
    tx, ty = math.cos(angle), math.sin(angle)
    nx, ny = -ty * outward_sign, tx * outward_sign
    base = (point[0] + offset * nx, point[1] + offset * ny)
    tri = P.pyramid(base, (tx, ty), (nx, ny), size)
    return tri + [tri[0]]


def proof_data() -> dict:
    """The numbers the page states, recomputed from the grammar."""
    o = grammar.STUDY_01
    right = grammar.fleur_right(o)
    band = grammar.band(o)
    chain = engine.build(_design(right))

    starts = [0.0]
    for seg in right["spans"]:
        starts.append(starts[-1] + seg.length)
    petal = starts[8] - starts[5]          # band node -> petal tip
    marks = _node_marks(right)

    return {
        "half_spans": len(right["spans"]),
        "band_spans": len(band["spans"]),
        "spans": 2 * len(right["spans"]) + len(band["spans"]),
        "width": WIDTH,
        "offset": OFFSET,
        "radius": 2.0 * OFFSET,
        "nodes": len(marks),
        "integer_nodes": len(marks),
        "petal_length": petal,
        "length": chain.length,
        "marks": marks,
    }


def build_items() -> tuple[list, dict]:
    o = grammar.STUDY_01
    right = grammar.fleur_right(o)
    band = grammar.band(o)
    data = proof_data()

    chain = engine.build(_design(right))
    pts = _sample(chain)
    plus, minus = PF.normal_offsets(pts, OFFSET)
    items = [
        (plus, BLUE, 1.0, None),
        (minus, RED, 1.0, None),
        (_mirror(plus), BLUE, 1.0, None),
        (_mirror(minus), RED, 1.0, None),
        (pts, INK, 2.0, None),
        (_mirror(pts), INK, 2.0, None),
    ]

    band_chain = engine.build(Design(
        name="band", segments=band["spans"],
        anchor={"x": band["start"][0], "y": band["start"][1],
                "angle": band["angle"]}, g1=True))
    items.append((_sample(band_chain, 360), INK, 1.6, None))

    # the integer nodes, then two pyramid pairs at chosen hits
    for x, y in data["marks"]:
        diamond = [(x - 9, y), (x, y + 9), (x + 9, y), (x, y - 9), (x - 9, y)]
        items.append((diamond, GOLD, 0.8, None, GOLD))
    for node_i, sign in ((5, 1), (5, -1)):
        s = [0.0]
        for seg in right["spans"]:
            s.append(s[-1] + seg.length)
        angle = chain.tangent(s[node_i])
        point = chain.point(s[node_i])
        items.append((_pyramid(point, angle, OFFSET, sign), GOLD, 0.9, None, GOLD))

    # the stalk's ending: a cone at the lance tip, R = 2 x offset
    tip = chain.point(chain.length)
    tangent = (tip[0] - chain.point(chain.length - 20.0)[0],
               tip[1] - chain.point(chain.length - 20.0)[1])
    cone = P.cone_terminal(tip, tangent, OFFSET)
    items.append((cone["left"], INK, 1.8, None))
    items.append((cone["right"], INK, 1.8, None))

    # the branch's ending: seagrass at the petal tip, mirrored
    petal_tip = right["nodes"][8]
    petal_tan = (right["nodes"][8][0] - right["nodes"][7][0],
                 right["nodes"][8][1] - right["nodes"][7][1])
    for mirror in (1, -1):
        p = (petal_tip[0] * mirror, petal_tip[1])
        t = (petal_tan[0] * mirror, petal_tan[1])
        for blade in P.seagrass(p, t, OFFSET):
            items.append((blade, GREEN, 1.2, None))
    return items, data


def main() -> int:
    items, data = build_items()
    hero = PF.figure(items, 980, 760)
    right = grammar.fleur_right(grammar.STUDY_01)
    chain = engine.build(_design(right))
    cone_tip = chain.point(chain.length)
    prev = chain.point(chain.length - 20.0)
    tangent = (cone_tip[0] - prev[0], cone_tip[1] - prev[1])
    cone = P.cone_terminal(cone_tip, tangent, OFFSET)
    cone_items = [
        (cone["left"], INK, 1.8, None),
        (cone["right"], INK, 1.8, None),
        ([(cone_tip[0] - 60, cone_tip[1]), (cone_tip[0], cone_tip[1])],
         MUTED, 1.2, None),
    ]
    detail = PF.figure(cone_items, 360, 300)

    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fleur proof 01 — the fleur on the plant grammar</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1000px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 18px}}
h2{{font:600 12px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.10em;text-transform:uppercase;color:{MUTED};margin:30px 0 8px}}
.panel{{background:{PAPER};border:1px solid #d8ccae;padding:16px 18px;margin:0 0 18px}}
.art{{background:{PAPER};border:1px solid #d8ccae;padding:8px;margin:0 0 8px}}
svg{{display:block;width:100%;height:auto}}
.legend{{display:flex;gap:16px;flex-wrap:wrap;font:11px ui-monospace,Menlo,monospace;color:{MUTED};margin:6px 0 0}}
.sw{{display:inline-block;width:20px;height:0;border-top:3px solid {INK};margin-right:5px;vertical-align:middle}}
.sw.b{{border-top:2px solid {BLUE}}}.sw.r{{border-top:2px solid {RED}}}
.sw.g{{border-top:2px solid {GOLD}}}.sw.e{{border-top:2px solid {GREEN}}}
table{{border-collapse:collapse;width:100%;font:12px/1.5 ui-monospace,Menlo,monospace;margin:8px 0 0}}
td,th{{border-bottom:1px solid #d8ccae;padding:5px 8px;text-align:left}}
th{{color:{MUTED};font-weight:600}}
.card{{display:grid;grid-template-columns:340px 1fr;gap:18px;align-items:start}}
@media(max-width:760px){{.card{{grid-template-columns:1fr}}}}
.note{{font:11px/1.6 ui-monospace,Menlo,monospace;color:{MUTED}}}
</style></head><body><main>
<h1>Fleur proof 01</h1>
<p class="lead">The fleur study read through the plant-form grammar: stalk, two
rails, an ending, integer marks, and the petal as a branch.</p>

<div class="panel">
<p><strong>The reading.</strong> The central lance is the stalk. The study's
{data['width']:g}-unit width is the pair of rails at ±{data['offset']:g}. The
lance tip is no longer a bare point: it ends in a <strong>cone terminal</strong>
of radius <strong>2 × offset = {data['radius']:g}</strong>. The side petal is
the branch, and it ends in seagrass, because a branch inherits the ending rule.
The gold dots are the integer nodes; two of them carry pyramid growth marks on
the rails.</p>
<p>Nothing is redrawn by eye: the half, the mirror and the band come from
<code>curve_lab.grammar.study_01</code>, and the counts below are recomputed
from that module by <code>scripts/fleur_proof.py</code>.</p>
</div>

<div class="art">{hero}</div>
<div class="legend">
<span><i class="sw"></i> fleur centreline</span>
<span><i class="sw b"></i> +offset rail</span>
<span><i class="sw r"></i> −offset rail</span>
<span><i class="sw g"></i> integer node / growth mark</span>
<span><i class="sw e"></i> seagrass branch ending</span>
</div>

<h2>The numbers</h2>
<div class="panel">
<table>
<tr><th>spans</th><td>{data['half_spans']} half + {data['half_spans']} mirrored + {data['band_spans']} band = {data['spans']}</td></tr>
<tr><th>width</th><td>{data['width']:g} · rails at ±{data['offset']:g}</td></tr>
<tr><th>cone terminal</th><td>R = 2 × offset = {data['radius']:g}</td></tr>
<tr><th>integer nodes</th><td>{data['integer_nodes']} (both halves plus the band corners, deduplicated)</td></tr>
<tr><th>petal branch</th><td>{data['petal_length']:.1f} units of centreline, seagrass ending</td></tr>
<tr><th>centreline</th><td>{data['length']:.1f} units from foot to lance tip (one half)</td></tr>
</table>
</div>

<h2>The ending, enlarged</h2>
<div class="panel card">
<div class="art">{detail}</div>
<div>
<p>The cone is two arcs of radius {data['radius']:g}, one from each rail, each
tangent at its base and meeting at the centreline. It is the rule for a stalk
with no flower head, and it is what makes the lance tip legal. No bare tip.</p>
<p class="note">R = 2 × offset · tangent at the rail base · one meeting point</p>
</div>
</div>

<h2>What this proves</h2>
<div class="panel">
<p>That the fleur study is not a special drawing: it is a plant-form with the
same vocabulary as the LAC stalks and the integer spines. The central lance is
a stalk, its rails are offsets, its tip is a terminal, its side petal is a
branch with an ending, and its exact nodes are lattice points. The grammar
holds on the ornament that was the acceptance test for the port.</p>
<p class="note">Re-derive: <code>python scripts/fleur_proof.py</code> ·
<code>python -m unittest tests.test_fleur_proof</code></p>
</div>
</main></body></html>
'''
    out = ROOT / "workbench" / "fleur-proof.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
