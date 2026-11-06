"""A fitted offset on an integer cubic: labelled fitted, never exact.

    .venv/bin/python scripts/integer_cubic_offset.py

The 3-4-5 integer cubic has exact integer controls and a rational tangent, but
it is not a Pythagorean-hodograph curve. Its offset is therefore algebraic and
not rational; the best available rail is Levien's fitted cubic chain. This page
draws the source, the dense exact offset and the fitted chain, and prints the
fit error. It does not claim an exact offset.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from curve_lab.parallel_bezier import fit_chain  # noqa: E402
from curve_lab.pyth_cubic import case  # noqa: E402
import plant_forms as PF  # noqa: E402

INK, BLUE, RED, GOLD, MUTED = "#2e2413", "#1f5fa8", "#a23b2a", "#c9a441", "#7b6c4e"
PAPER = "#fffdf7"

D = 0.5


def _sample(span, n=240):
    p0, c1, c2, p3 = span["p0"], span["c1"], span["c2"], span["p3"]
    out = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        out.append((mt ** 3 * p0[0] + 3 * mt * mt * t * c1[0]
                    + 3 * mt * t * t * c2[0] + t ** 3 * p3[0],
                    mt ** 3 * p0[1] + 3 * mt * mt * t * c1[1]
                    + 3 * mt * t * t * c2[1] + t ** 3 * p3[1]))
    return out


def _offset(pts, d):
    out = []
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy) or 1.0
        out.append((p[0] - dy / length * d, p[1] + dx / length * d))
    return out


def proof_data() -> dict:
    c = case(3, 4, 5)
    span = {"p0": c["p0"], "p1": c["p1"], "p2": c["p2"], "p3": c["p3"]}
    span = {"p0": span["p0"], "c1": span["p1"], "c2": span["p2"],
            "p3": span["p3"]}
    fitted = fit_chain([span], D, tol=0.005)
    return {
        "case": c,
        "span": span,
        "fitted": fitted,
        "error": fitted["error_max"],
        "cusps": len(fitted["cusps"]),
        "clamped": fitted["clamped"],
        "distance": D,
        "spans": len(fitted["spans"]),
    }


def main() -> int:
    d = proof_data()
    src = _sample(d["span"], 240)
    true = _offset(src, D)
    fit_pts = []
    for s in d["fitted"]["spans"]:
        fit_pts.extend(_sample(s, 20))
    items = [
        (src, INK, 2.2, None),
        (true, MUTED, 1.1, "4 3"),
        (fit_pts, BLUE, 1.6, None),
    ]
    figure = PF.figure(items, 900, 480)
    # a detail of the worst end, where the fit has to bend
    detail = PF.figure([
        (src, INK, 2.0, None),
        (true, MUTED, 1.0, "4 3"),
        (fit_pts, BLUE, 1.5, None),
    ], 520, 320)

    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Integer cubic offset — fitted, not exact</title>
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
.sw.b{{border-top:2px solid {BLUE}}}.sw.m{{border-top:2px dashed {MUTED}}}
table{{border-collapse:collapse;width:100%;font:12px/1.5 ui-monospace,Menlo,monospace;margin:8px 0 0}}
td,th{{border-bottom:1px solid #d8ccae;padding:5px 8px;text-align:left}}
th{{color:{MUTED};font-weight:600}}
code{{font:12px ui-monospace,Menlo,monospace}}
</style></head><body><main>
<h1>Integer cubic offset</h1>
<p class="lead">The controls are integers; the offset is not. The rail below is
a fitted cubic chain, and the page says so.</p>

<div class="panel">
<p><strong>The source.</strong> The {d['case']['label']} cubic has
P0 = {d['case']['p0']}, P1 = {d['case']['p1']}, P2 = {d['case']['p2']},
P3 = {d['case']['p3']}: integer controls, chord {d['case']['chord']}, both arms
{d['case']['arm']}, tangent {d['case']['angle']:.2f}°. It is exact as a cubic
and it is not a Pythagorean-hodograph curve.</p>
<p><strong>The rail.</strong> Levien's method samples the true normal offset and
fits a cubic chain at distance {d['distance']:g}. The maximum error is
<strong>{d['error']:.2e}</strong> over {d['spans']} fitted spans. The dashed
line is the dense exact offset, drawn for comparison only — the fitted chain is
the deliverable, and it is labelled fitted.</p>
<p class="note">Exact integer controls do not imply an exact offset. The corner
of that distinction is the whole reason the offset catalogue has a fitted tier.</p>
</div>

<div class="art">{figure}</div>
<div class="legend">
<span><i class="sw"></i> integer cubic (source)</span>
<span><i class="sw m"></i> dense exact offset (reference)</span>
<span><i class="sw b"></i> fitted cubic chain</span>
</div>

<h2>The numbers</h2>
<div class="panel">
<table>
<tr><th>triple</th><td>{d['case']['label']} · chord {d['case']['chord']} · arm {d['case']['arm']}</td></tr>
<tr><th>controls</th><td>{d['case']['p0']}, {d['case']['p1']}, {d['case']['p2']}, {d['case']['p3']}</td></tr>
<tr><th>offset</th><td>d = {d['distance']:g} · fitted cubic chain</td></tr>
<tr><th>fit error</th><td>{d['error']:.2e}</td></tr>
<tr><th>cusps / clamps</th><td>{d['cusps']} · {d['clamped']}</td></tr>
<tr><th>exact?</th><td>no — the integer cubic is not PH</td></tr>
</table>
</div>

<h2>The same rail at detail</h2>
<div class="art">{detail}</div>

<div class="panel">
<p><strong>What this rules out.</strong> Calling this an exact offset because
the source controls are integers. The exact routes are lines, arcs, PH curves,
the Pythagorean spiral and the Pythagorean integer cubic family's own exact
objects; a general integer cubic is not one of them.</p>
<p class="note">Re-derive: <code>python scripts/integer_cubic_offset.py</code> ·
<code>python -m unittest tests.test_integer_cubic_offset</code></p>
</div>
</main></body></html>
'''
    out = ROOT / "workbench" / "integer-cubic-offset.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    print(f"error {d['error']:.2e}, {d['spans']} spans, cusps {d['cusps']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
