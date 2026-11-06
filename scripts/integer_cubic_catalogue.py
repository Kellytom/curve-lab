"""The integer-cubic catalogue: every triple's ordered arm pairs, signs and rotation.

    .venv/bin/python scripts/integer_cubic_catalogue.py
    open workbench/integer-cubic-catalogue.html

The table is the whole catalogue for primitive triples with c <= 1000: one row
per ordered arm pair, with both sign variants and the exact integer rotation by
the triple's own angle at scale c. The cards at the top draw the first six
triples in both arm orders, from the same rows the table lists.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab.pyth_cubic import catalogue, catalogue_c  # noqa: E402
from curve_lab.pyth_triples import base_triples  # noqa: E402
from grid_view import MARK, crossings, grid_lines, nice_step  # noqa: E402

INK, BLUE, RED, GOLD = "#2e2413", "#1f5fa8", "#a23b2a", "#c9a441"
MUTED, PAPER, GRID = "#7b6c4e", "#fffdf7", "#e4dcc6"

C_MAX = 1000


def bezier(p0, p1, p2, p3, n=120):
    out = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        out.append((mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0]
                    + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
                    mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1]
                    + 3 * mt * t * t * p2[1] + t ** 3 * p3[1]))
    return out


def card(row, title) -> str:
    pts = bezier(row["p0"], row["p1"], row["p2"], row["p3"])
    ctrl = [row["p0"], row["p1"], row["p2"], row["p3"]]
    allp = pts + ctrl
    x0 = min(p[0] for p in allp); x1 = max(p[0] for p in allp)
    y0 = min(p[1] for p in allp); y1 = max(p[1] for p in allp)
    w, h, pad = 340, 230, 26
    dx, dy = (x1 - x0) or 1, (y1 - y0) or 1
    k = min((w - 2 * pad) / dx, (h - 4 * pad) / dy)

    def put(p):
        return pad + (p[0] - x0) * k, h - 2 * pad - (p[1] - y0) * k

    body = [f'<rect width="{w}" height="{h}" fill="{PAPER}" stroke="{GRID}"/>']
    step = nice_step(max(x1 - x0, y1 - y0))
    body += grid_lines(put, x0, x1, y0, y1, step, "#efe7d2")
    poly = " ".join(f"{put(p)[0]:.1f},{put(p)[1]:.1f}" for p in ctrl)
    body.append(f'<polyline points="{poly}" fill="none" stroke="{MUTED}" '
                f'stroke-width="1" stroke-dasharray="4 3"/>')
    curve = " ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in pts)
    body.append(f'<path d="M {curve}" fill="none" stroke="{INK}" stroke-width="2"/>')
    for p in ctrl:
        q = put(p)
        body.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="2.8" fill="{GOLD}"/>')
    for p in crossings([pts], step, limit=16):
        q = put(p)
        body.append(f'<circle class="lattice" cx="{q[0]:.1f}" cy="{q[1]:.1f}" '
                    f'r="2.0" fill="{MARK}"/>')
    body.append(f'<text x="10" y="18" font-family="Georgia,serif" font-size="12" '
                f'fill="{INK}">{title}</text>')
    body.append(f'<text x="10" y="{h-8}" font-family="ui-monospace,Menlo,monospace" '
                f'font-size="10" fill="{MUTED}">chord {row["chord"]} · arm {row["arm"]} '
                f'· P1 {row["p1"]}</text>')
    return f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{title}">' + "".join(body) + "</svg>"


def main() -> int:
    rows = catalogue(C_MAX)
    prims = [t for t in base_triples(C_MAX) if t["k"] == 1]
    sign_variants = 2 * len(rows)
    sample = rows[:12]
    c_rows = catalogue_c(C_MAX)
    c_sample = c_rows[:12]
    c_cards = "".join(
        f'<figure class="card">{card(r, r["label"] + " · " + r["order"])}'
        f'<figcaption>{r["label"]} · arms ({r["a"]}, {r["b"]}) · height {r["height"]}</figcaption></figure>'
        for r in c_sample)
    c_body = []
    for i, r in enumerate(c_rows, 1):
        c_body.append(
            f'<tr><td>{i}</td><td>{r["label"]}</td><td>{r["m"]},{r["n"]}</td>'
            f'<td>{r["order"]}</td><td>({r["a"]}, {r["b"]})</td>'
            f'<td>{r["chord"]}</td><td>{r["height"]}</td>'
            f'<td>{r["p1"]}</td><td>{r["p2"]}</td></tr>')

    cards = "".join(
        f'<figure class="card">{card(r, r["label"] + " · " + r["order"])}'
        f'<figcaption>{r["label"]} · arms ({r["a"]}, {r["b"]}) · chord {r["chord"]}</figcaption></figure>'
        for r in sample)

    body_rows = []
    for i, r in enumerate(rows, 1):
        body_rows.append(
            f'<tr><td>{i}</td><td>{r["label"]}</td><td>{r["m"]},{r["n"]}</td>'
            f'<td>{r["order"]}</td><td>({r["a"]}, {r["b"]})</td>'
            f'<td>{r["chord"]}</td><td>{r["arm"]}</td>'
            f'<td>{r["angle"]:.2f}</td>'
            f'<td>{r["p1"]}</td><td>{r["p2"]}</td>'
            f'<td>{r["mirror_p1"]}</td><td>{r["mirror_p2"]}</td>'
            f'<td>{r["rotation_points"][1]}</td></tr>')

    from curve_lab.pyth_cubic import hit_table
    hit_rows = "".join(
        f'<tr><td>{r["scale"]}</td><td>{round(r["scale"] ** (1 / 3))}</td>'
        f'<td>{r["s_min"]}–{r["s_max"]}</td><td>{r["c_min"]}–{r["c_max"]}</td></tr>'
        for r in hit_table())

    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Integer cubic catalogue — arm pairs, signs, rotations</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 18px}}
h2{{font:600 12px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.10em;text-transform:uppercase;color:{MUTED};margin:30px 0 8px}}
.panel{{background:{PAPER};border:1px solid #d8ccae;padding:16px 18px;margin:0 0 18px}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
.card{{margin:0;background:{PAPER};border:1px solid #d8ccae;padding:8px}}
.card figcaption{{font:10px/1.45 ui-monospace,Menlo,monospace;color:{MUTED};margin-top:4px}}
svg{{display:block;width:100%;height:auto}}
table{{border-collapse:collapse;width:100%;font:10px/1.4 ui-monospace,Menlo,monospace}}
th,td{{border-bottom:1px solid #d8ccae;padding:3px 5px;text-align:left;white-space:nowrap}}
th{{color:{MUTED};font-weight:600;position:sticky;top:0;background:{PAPER}}}
.scroll{{max-height:520px;overflow:auto;border:1px solid #d8ccae;background:{PAPER}}}
code{{font:12px ui-monospace,Menlo,monospace}}
@media(max-width:900px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body><main>
<h1>Integer cubic catalogue</h1>
<p class="lead">Every primitive triple up to c = {C_MAX}, in both arm orders,
with both signs and the exact integer rotation the triple supplies.</p>

<div class="panel">
<p><strong>What is counted.</strong> {len(prims)} primitive triples with
c ≤ {C_MAX}. Each gives two ordered arm pairs — (a, b) and (b, a) — so
<strong>{len(rows)}</strong> canonical curves. Each curve has two sign variants:
P1 = (a, −b), the construction, and its mirror P1 = (a, b), so
<strong>{sign_variants}</strong> integer cubics in the table.</p>
<p><strong>What is canonical.</strong> The construction is fixed: P0 = (0,0),
P1 = (a, −b), P2 = (2c − a, b), P3 = (2c, 0). The arm pair is the only ordering
choice; the sign is the only reflection choice. The rotation is recorded, not
counted: the triple's own angle is an exact rational rotation, and at scale c
it keeps every control point an integer. Its powers are exact too, so the
rotation column is one generator of a group, not a finite list.</p>
</div>

<h2>The first six triples, both arm orders</h2>
<div class="grid">{cards}</div>

<h2>Lattice hits at the key distances</h2>
<div class="panel">
<p><strong>The arithmetic.</strong> At t = k/q the cubic's coordinates have
denominator q³, so the drawing is integer at that fraction only when it is
scaled by q³. At scale 1 an S cubic is integral at exactly three points:
t = 0, ½ and 1 — the two ends and (c, 0). The table below is the hit count for
every S and C curve at each key distance, unique points, t = k/q up to q = 25.
This is why an unscaled cubic "has no lattice": it has three.</p>
<table>
<thead><tr><th>scale (q³)</th><th>q</th><th>S hits</th><th>C hits</th></tr></thead>
<tbody>{hit_rows}</tbody>
</table>
</div>

<h2>The catalogue · {len(rows)} rows</h2>
<div class="scroll">
<table>
<thead><tr><th>#</th><th>triple</th><th>m,n</th><th>order</th><th>arms</th>
<th>chord</th><th>arm</th><th>tangent°</th><th>P1</th><th>P2</th>
<th>mirror P1</th><th>mirror P2</th><th>rotated P1</th></tr></thead>
<tbody>{''.join(body_rows)}</tbody>
</table>
</div>

<h2>The three aspects</h2>
<div class="panel">
<p><strong>Linearity:</strong> both end tangents are straight, and the control
polygon is two triangles against the chord. <strong>Curve:</strong> the S bend
changes the tangent continuously between them. <strong>Infinity:</strong>
absent — a cubic is a bounded arc. A design that uses one of these curves must
supply the third aspect elsewhere, with a spiral tail or a ray to a point at
infinity. The catalogue is a parts list, not a finished design.</p>
</div>

<h2>The C cubics · {len(c_rows)}</h2>
<div class="panel">
<p><strong>The other shape.</strong> Put both handles on the same side of the
chord — P1 = (a, b), P2 = (2c − a, b) — and the same integer triple gives a
C-shaped arch instead of an S. The controls stay integer; the height is b. The
count is the same {len(c_rows)} ordered arm pairs.</p>
</div>
<div class="grid">{c_cards}</div>
<div class="scroll">
<table>
<thead><tr><th>#</th><th>triple</th><th>m,n</th><th>order</th><th>arms</th>
<th>chord</th><th>height</th><th>P1</th><th>P2</th></tr></thead>
<tbody>{''.join(c_body)}</tbody>
</table>
</div>

<div class="panel">
<p><strong>Reading a row.</strong> The chord is 2c and both handle arms are c,
so the control polygon is two congruent triples against the chord. P1 and P2
are the canonical controls; mirror P1/P2 are the sign variant; rotated P1 is
where the triple's own rotation sends P1 at scale c — an integer by
construction, which is the exactness the catalogue is for.</p>
<p class="note">Re-derive: <code>python scripts/integer_cubic_catalogue.py</code> ·
<code>python -m unittest tests.test_pyth_cubic_catalogue</code></p>
</div>
</main></body></html>
'''
    out = ROOT / "workbench" / "integer-cubic-catalogue.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    print(f"{len(prims)} triples, {len(rows)} curves, {sign_variants} sign variants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
