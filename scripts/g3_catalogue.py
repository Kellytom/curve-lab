"""The G3 catalogue: every named curve, interpolated by quintic Beziers.

    .venv/bin/python scripts/g3_catalogue.py
    open workbench/g3-catalogue.html

The catalogue is an interpolation showcase, not a gallery of ideal curves.
Each admitted curve is a chain of quintic Bezier spans whose joins are G3;
the ideal curve is drawn only as a faint reference. A branch that cannot be
interpolated G3 — a cusp, a point at infinity, a singular handle solve — is
listed as rejected with the reason, not quietly dropped.

The JSON beside the page is the machine-readable form of the same result.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generators as G  # noqa: E402
import g3_showcase as G3  # noqa: E402

PAPER = "#fbf7ec"
INK, MUTED, GOLD, BLUE, RED = "#2e2413", "#7b6c4e", "#c9a441", "#1f5fa8", "#a23b2a"
RULE = "#d8ccae"
GREEN = "#2f6b3a"

SPANS = 6
HGRID = (0.15, 0.2, 0.25, 0.3, 0.35, 0.4)
ERR_LIMIT = 0.06


# -- exact evaluation of a homogeneous branch ------------------------------

def homog_eval(ctrl, t):
    n = len(ctrl) - 1
    X = Y = W = 0.0
    for i, (x, y, w) in enumerate(ctrl):
        b = math.comb(n, i) * t ** i * (1.0 - t) ** (n - i)
        X += float(x) * b
        Y += float(y) * b
        W += float(w) * b
    if abs(W) < 1e-12:
        return None
    return (X / W, Y / W)


def branch_points(ctrl, n=1000):
    pts, ts = [], []
    for i in range(n + 1):
        t = i / n
        p = homog_eval(ctrl, t)
        if p is not None:
            pts.append(p)
            ts.append(t)
    return pts, ts


def der5(f, t, h=1e-4):
    fm2, fm1, f0, fp1, fp2 = f(t - 2 * h), f(t - h), f(t), f(t + h), f(t + 2 * h)
    if None in (fm2, fm1, f0, fp1, fp2):
        return None
    return (
        (fm2 - 8 * fm1 + 8 * fp1 - fp2) / (12 * h),
        (-fm2 + 16 * fm1 - 30 * f0 + 16 * fp1 - fp2) / (12 * h * h),
        (-fm2 + 2 * fm1 - 2 * fp1 + fp2) / (2 * h ** 3),
    )


def fit_branch(ctrl, nspans=SPANS):
    """Fit one branch with quintic G3 spans; return None when it cannot fit."""
    pts, ts = branch_points(ctrl)
    if len(pts) < 30:
        return None
    s = [0.0]
    for a, b in zip(pts, pts[1:]):
        s.append(s[-1] + math.dist(a, b))
    total = s[-1]
    if total <= 0.0:
        return None
    closed = math.dist(pts[0], pts[-1]) < 1e-6
    lo = 0.0 if closed else 0.015 * total
    hi = total if closed else 0.985 * total

    knot_t, knot_p = [], []
    for i in range(nspans + 1):
        target = lo + (hi - lo) * i / nspans
        j = 0
        while j < len(s) - 2 and s[j + 1] < target:
            j += 1
        frac = (target - s[j]) / (s[j + 1] - s[j]) if s[j + 1] > s[j] else 0.0
        t = ts[j] + (ts[j + 1] - ts[j]) * frac
        p = homog_eval(ctrl, t)
        if p is None:
            return None
        knot_t.append(t)
        knot_p.append(p)

    D = []
    for t in knot_t:
        fx = lambda u: (lambda q: None if q is None else q[0])(homog_eval(ctrl, u))
        fy = lambda u: (lambda q: None if q is None else q[1])(homog_eval(ctrl, u))
        dx, dy = der5(fx, t), der5(fy, t)
        if dx is None or dy is None:
            return None
        d1, d2, d3 = (dx[0], dy[0]), (dx[1], dy[1]), (dx[2], dy[2])
        sp = math.hypot(*d1)
        if sp < 1e-12:
            return None
        T = (d1[0] / sp, d1[1] / sp)
        N = d1[0] * d2[1] - d1[1] * d2[0]
        Np = d1[0] * d3[1] - d1[1] * d3[0]
        k = N / sp ** 3
        kp = Np / sp ** 3 - 3 * N * (d1[0] * d2[0] + d1[1] * d2[1]) / sp ** 5
        D.append((T, k, kp / sp))

    dense = pts[::max(1, len(pts) // 320)]

    def near(p):
        return min(math.dist(p, q) for q in dense)

    spans, errs = [], []
    for i in range(nspans):
        p0, p5 = knot_p[i], knot_p[i + 1]
        T0, k0, r0 = D[i]
        T1, k1, r1 = D[i + 1]
        chord = math.dist(p0, p5)
        if chord < 1e-12:
            return None
        best = None
        for fa in HGRID:
            for fb in HGRID:
                P = G3.quintic_g3(p0, p5, T0, T1, k0, k1, r0, r1,
                                  fa * chord, fb * chord)
                if P is None:
                    continue
                e = max(near(G3.bezier(P, j / 20)) for j in range(21))
                if best is None or e < best[0]:
                    best = (e, P)
        if best is None:
            return None
        spans.append(best[1])
        errs.append(best[0])

    joins = G3.gate(spans)
    closed = math.dist(knot_p[0], knot_p[-1]) < 1e-6
    if closed:
        A, B = spans[-1], spans[0]
        row = {
            "join": "seam",
            "dp": math.dist(G3.bezier(A, 1.0), G3.bezier(B, 0.0)),
            "angle": abs(math.degrees(math.atan2(
                G3.derivative(A, 1.0, 1)[0] * G3.derivative(B, 0.0, 1)[1]
                - G3.derivative(A, 1.0, 1)[1] * G3.derivative(B, 0.0, 1)[0],
                G3.derivative(A, 1.0, 1)[0] * G3.derivative(B, 0.0, 1)[0]
                + G3.derivative(A, 1.0, 1)[1] * G3.derivative(B, 0.0, 1)[1]))),
            "dk": abs(G3.curvature(A, 1.0) - G3.curvature(B, 0.0)),
            "dks": abs(G3.curvature_rate(A, 1.0) - G3.curvature_rate(B, 0.0)),
        }
        row["pass"] = (row["dp"] < 1e-9 and row["angle"] < 1e-6
                       and row["dk"] < 1e-9 and row["dks"] < 1e-9)
        joins.append(row)

    return {
        "spans": spans,
        "ideal": pts[::max(1, len(pts) // 240)],
        "error": max(errs),
        "g3": max(row["dks"] for row in joins),
        "pass": all(row["pass"] for row in joins),
        "closed": closed,
    }


# -- the catalogue ----------------------------------------------------------

def attempted(spec):
    if spec["branches"] is None:
        return None, "sampled curve; no exact control polygon to interpolate yet"
    data = G.named_data(spec)
    if not data["ctrl"]:
        return None, "no exact control polygon"
    fitted = []
    for ctrl in data["ctrl"]:
        r = fit_branch(ctrl)
        if r is None:
            return None, "cusp, point at infinity, or singular handle solve"
        fitted.append(r)
    bad = [r for r in fitted if not r["pass"]]
    if bad:
        return None, "G3 gate failed"
    return fitted, None


def catalogue():
    rows = []
    for spec in G.NAMED:
        fitted, why = attempted(spec)
        if fitted is None:
            rows.append({"key": spec["key"], "admitted": False, "reason": why})
        else:
            rows.append({
                "key": spec["key"], "admitted": True,
                "spans": SPANS,
                "branches": fitted,
                "error": max(r["error"] for r in fitted),
                "g3": max(r["g3"] for r in fitted),
            })
    return rows


# -- drawing ----------------------------------------------------------------

class Frame:
    def __init__(self, w, h, x0, x1, y0, y1, pad=34):
        self.w, self.h = w, h
        self.s = min((w - 2 * pad) / (x1 - x0), (h - 2 * pad) / (y1 - y0))
        self.ox = (w - (x1 - x0) * self.s) / 2.0 - x0 * self.s
        self.oy = (h - (y1 - y0) * self.s) / 2.0 + y1 * self.s

    def __call__(self, p):
        return (self.ox + p[0] * self.s, self.oy - p[1] * self.s)


def _path(pts, f):
    return " ".join(("M" if i == 0 else "L") + f"{x:.2f},{y:.2f}"
                    for i, (x, y) in enumerate(f(p) for p in pts))


def panel(row, w=520, h=330):
    pts = [p for br in row["branches"] for p in br["ideal"]]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = 0.08 * max(x1 - x0, y1 - y0, 1e-6)
    f = Frame(w, h, x0 - pad, x1 + pad, y0 - pad, y1 + pad)

    ideal = []
    g3 = []
    knots = []
    for br in row["branches"]:
        ideal.append(f'<path d="{_path(br["ideal"], f)}" fill="none" '
                     f'stroke="{MUTED}" stroke-width="1.1" stroke-dasharray="4 4"/>')
        samples = []
        for P in br["spans"]:
            samples.extend(G3.bezier(P, i / 40) for i in range(41))
        g3.append(f'<path d="{_path(samples, f)}" fill="none" '
                  f'stroke="{INK}" stroke-width="2.1"/>')
        for P in br["spans"]:
            p = G3.bezier(P, 0.0)
            X, Y = f(p)
            knots.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="3.0" '
                         f'fill="none" stroke="{GREEN}" stroke-width="1.3"/>')

    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{row['key']} G3 interpolation">
  <rect width="{w}" height="{h}" fill="{PAPER}"/>
  {''.join(ideal)}
  {''.join(g3)}
  {''.join(knots)}
  <text x="12" y="22" font-family="Georgia,serif" font-size="14" fill="{INK}">Fig. G3.C · {row['key']}</text>
  <text x="12" y="40" font-family="ui-monospace,Menlo,monospace" font-size="10.5" fill="{MUTED}">{row['spans']} quintic spans · max deviation {row['error']:.1e} · worst Δ(dκ/ds) {row['g3']:.1e}</text>
  <text x="{w / 2:.0f}" y="{h - 8}" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="10.5" fill="{MUTED}">x (model units)</text>
  <g font-family="Georgia,serif" font-size="11">
    <line x1="12" y1="{h - 24}" x2="38" y2="{h - 24}" stroke="{MUTED}" stroke-width="1.1" stroke-dasharray="4 4"/><text x="44" y="{h - 20}" fill="{INK}">ideal</text>
    <line x1="92" y1="{h - 24}" x2="118" y2="{h - 24}" stroke="{INK}" stroke-width="2.1"/><text x="124" y="{h - 20}" fill="{INK}">G3 interpolation</text>
  </g>
</svg>"""


def table(rows):
    body = []
    for row in rows:
        if row["admitted"]:
            note = " · see notes" if row["key"] == "circle" else ""
            body.append(
                f"<tr><td>{row['key']}</td><td>{len(row['branches'])}</td>"
                f"<td>{row['spans']}</td><td>{row['error']:.1e}</td>"
                f"<td>{row['g3']:.1e}</td><td class=\"ok\">admitted{note}</td></tr>")
        else:
            body.append(
                f"<tr><td>{row['key']}</td><td>—</td><td>—</td><td>—</td>"
                f"<td>—</td><td class=\"bad\">rejected: {row['reason']}</td></tr>")
    return ("<table><tr><th>curve</th><th>branches</th><th>spans</th>"
            "<th>max deviation</th><th>worst Δ(dκ/ds)</th><th>status</th></tr>"
            + "".join(body) + "</table>")


CSS = """
:root{--paper:%(paper)s;--ink:%(ink)s;--muted:%(muted)s;--rule:%(rule)s}
*{box-sizing:border-box} body{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}
main{max-width:1120px;margin:0 auto;padding:34px 22px 70px}
.eyebrow{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}
h1{font-size:31px;line-height:1.12;margin:0 0 8px} h2{font-size:20px;margin:0 0 8px}
.lede{max-width:920px;color:var(--muted)}
.panel{background:var(--paper);border:1px solid var(--rule);padding:14px 16px;margin:0 0 16px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(500px,1fr));gap:16px}
table{border-collapse:collapse;font:12px/1.5 ui-monospace,Menlo,monospace;margin:10px 0;width:100%%}
th,td{border:1px solid var(--rule);padding:5px 8px;text-align:right} th{color:var(--muted);font-weight:400}
.ok{color:%(green)s} .bad{color:%(red)s;font-weight:700}
.small{font:12px/1.6 ui-monospace,Menlo,monospace;color:var(--muted)}
.rule{background:#fffdf7;border-left:4px solid %(gold)s;padding:12px 16px;margin:0 0 18px}
code{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}
""" % {"paper": PAPER, "ink": INK, "muted": MUTED, "rule": RULE,
       "green": GREEN, "red": RED, "gold": GOLD}


def build():
    rows = catalogue()
    admitted = [r for r in rows if r["admitted"]]
    rejected = [r for r in rows if not r["admitted"]]
    # The circle is G3 everywhere and is explained on the notes page; it is
    # deliberately not drawn as a catalogue panel.
    drawn = [r for r in admitted if r["key"] != "circle"]
    panels = "".join(f'<section class="panel">{panel(r)}</section>' for r in drawn)

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>G3 catalogue · the named curves as quintic interpolations</title>
<style>{CSS}</style></head><body><main>
<p class="eyebrow">curve-lab · G3 catalogue</p>
<h1>The named curves, as G3 quintic interpolations</h1>
<p class="lede">This page shows the <strong>interpolation</strong>, not the ideal curve. Each
admitted curve is a chain of quintic Bézier spans, {SPANS} spans per branch, with every
join measured G3: position, direction, bend, and the smooth acceleration of the bend. The
ideal curve is the faint dashed line underneath. A branch that cannot be interpolated G3 —
a cusp, a point at infinity, a singular handle solve — is rejected and named in the table,
not quietly dropped.</p>

<div class="rule"><strong>How admission works.</strong> The knots are placed at equal arc
length on the exact curve. At each knot the tangent, curvature and curvature-rate are read
from the exact homogeneous control polygon; the quintic span matches them at both ends, and
the two handle lengths are chosen to minimise the deviation from the ideal. The table's
<code>max deviation</code> is a geometric distance, not a parameter error. The G3 gate is
computed from the Bézier derivatives, not from the drawn polyline.</p>

<section class="panel">
<h2>The gate</h2>
{table(rows)}
<p class="small">{len(admitted)} admitted of {len(rows)} named curves ·
{len(rejected)} rejected · {SPANS} quintic spans per branch ·
re-derive: <code>python scripts/g3_catalogue.py</code></p>
</section>

<h2 style="margin:26px 0 10px">Admitted curves</h2>
<div class="grid">{panels}</div>

<section class="panel">
<h2>Rejected, with the reason</h2>
<p class="small">A cusp has no tangent direction, so G3 is undefined there; a point at
infinity has no finite position. These are not failures of the interpolation — they are
curves outside the G3 domain. The sampled curves (heart, squircle) are not yet fitted; they
need a smooth polyline spline first. The next pass adds those, and more span counts.</p>
<p class="small">Back to the <a href="g3-showcase.html">G3 showcase</a> ·
theory on the <a href="g3-notes.html">G3 notes page</a>.</p>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "g3-catalogue.html"
    out.write_text(html, encoding="utf-8")

    cache = {
        "spans": SPANS,
        "curves": [
            {"key": r["key"], "admitted": r["admitted"],
             "reason": r.get("reason"),
             "error": r.get("error"), "g3": r.get("g3"),
             "branches": [
                 {"error": b["error"], "g3": b["g3"],
                  "pass": b["pass"], "closed": b["closed"]}
                 for b in r.get("branches", [])
             ]}
            for r in rows
        ],
    }
    (ROOT / "workbench" / "g3-catalogue.json").write_text(
        json.dumps(cache, indent=1), encoding="utf-8")
    print(out)
    return out


if __name__ == "__main__":
    build()
