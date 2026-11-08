"""Extend-and-cut terminals: fit past the station, then cut the G3 chain.

    .venv/bin/python scripts/g3_cut.py
    open workbench/g3-cut.html

A stem or an ending often wants to stop at a station on a longer smooth
curve, not at a natural endpoint. The rule is:

    cut at a station only when the curve continues smoothly through it.

So the conveyor fits a longer parameter range, then splits the span that
contains the requested station. The cut is interior to a G3 chain, so the
kept chain's new end inherits the G3 data; the discarded tail is not drawn as
part of the terminal. This page measures the cut: its distance from the ideal
curve, the tangent/curvature/curvature-rate errors, and the G3 defect across
the split before the tail is discarded.
"""

from __future__ import annotations

import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import g3_showcase as G3  # noqa: E402

PAPER = "#fbf7ec"
INK, MUTED, GOLD, BLUE, RED = "#2e2413", "#7b6c4e", "#c9a441", "#1f5fa8", "#a23b2a"
RULE = "#d8ccae"
GREEN = "#2f6b3a"


def split(P, t):
    levels = [list(P)]
    while len(levels[-1]) > 1:
        q = levels[-1]
        levels.append([(q[j][0] + (q[j + 1][0] - q[j][0]) * t,
                        q[j][1] + (q[j + 1][1] - q[j][1]) * t)
                       for j in range(len(q) - 1)])
    left = [levels[j][0] for j in range(len(P))]
    right = [levels[j][-1] for j in reversed(range(len(P)))]
    return left, right


def span_samples(P, n=40):
    return [G3.bezier(P, i / n) for i in range(n + 1)]


def chain_samples(spans, n=40):
    pts = []
    for P in spans:
        pts.extend(span_samples(P, n))
    return pts


def cut_panel(name, point, tangent, kappa, rho, t0, t1, cut_fraction, nspans=8):
    ts = [t0 + (t1 - t0) * i / nspans for i in range(nspans + 1)]
    spans, err = G3.quintic_param_spans(ts, point, tangent, kappa, rho, point)
    cut_t = t0 + (t1 - t0) * cut_fraction
    idx = 0
    while idx < nspans - 1 and ts[idx + 1] < cut_t:
        idx += 1
    local = (cut_t - ts[idx]) / (ts[idx + 1] - ts[idx])
    left, right = split(spans[idx], local)
    kept = spans[:idx] + [left]
    tail = [right] + spans[idx + 1:]

    cut_p = G3.bezier(left, 1.0)
    ideal_p = point(cut_t)
    d1a = G3.derivative(left, 1.0, 1)
    d1b = G3.derivative(right, 0.0, 1)
    ang = math.degrees(abs(math.atan2(d1a[0] * d1b[1] - d1a[1] * d1b[0],
                                      d1a[0] * d1b[0] + d1a[1] * d1b[1])))
    dp = math.dist(cut_p, G3.bezier(right, 0.0))
    dk = abs(G3.curvature(left, 1.0) - G3.curvature(right, 0.0))
    dks = abs(G3.curvature_rate(left, 1.0) - G3.curvature_rate(right, 0.0))

    # the cut's own data against the ideal at the same parameter
    sp = math.hypot(*d1a)
    T = (d1a[0] / sp, d1a[1] / sp)
    Ti = tangent(cut_t)
    tangent_err = math.degrees(abs(math.atan2(T[0] * Ti[1] - T[1] * Ti[0],
                                              T[0] * Ti[0] + T[1] * Ti[1])))
    kappa_err = abs(G3.curvature(left, 1.0) - kappa(cut_t))
    rate_err = abs(G3.curvature_rate(left, 1.0) - rho(cut_t))
    allpts = chain_samples(spans)
    xs = [q[0] for q in allpts]
    ys = [q[1] for q in allpts]
    size = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
    ok = (math.dist(cut_p, ideal_p) < 0.01 * size
          and tangent_err < 1.0 and kappa_err < 0.05
          and rate_err < 0.1 and max(dp, dk, dks) < 1e-9)
    return {
        "name": name, "spans": spans, "kept": kept, "tail": tail,
        "t0": t0, "t1": t1, "size": size, "ok": ok,
        "cut_t": cut_t, "cut_p": cut_p, "ideal_p": ideal_p,
        "distance": math.dist(cut_p, ideal_p),
        "tangent_err": tangent_err, "kappa_err": kappa_err,
        "rate_err": rate_err,
        "dp": dp, "angle": ang, "dk": dk, "dks": dks,
        "g3": max(dp, dk, dks),
        "fit_error": err,
        "point": point,
    }


class Frame:
    def __init__(self, w, h, x0, x1, y0, y1, pad=40):
        self.w, self.h = w, h
        self.s = min((w - 2 * pad) / (x1 - x0), (h - 2 * pad) / (y1 - y0))
        self.ox = (w - (x1 - x0) * self.s) / 2.0 - x0 * self.s
        self.oy = (h - (y1 - y0) * self.s) / 2.0 + y1 * self.s

    def __call__(self, p):
        return (self.ox + p[0] * self.s, self.oy - p[1] * self.s)


def path(pts, f):
    return " ".join(("M" if i == 0 else "L") + f"{x:.2f},{y:.2f}"
                    for i, (x, y) in enumerate(f(p) for p in pts))


def figure(panel, w=560, h=380):
    allpts = chain_samples(panel["spans"])
    xs = [p[0] for p in allpts]
    ys = [p[1] for p in allpts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = 0.10 * max(x1 - x0, y1 - y0, 1e-6)
    f = Frame(w, h, x0 - pad, x1 + pad, y0 - pad, y1 + pad)
    ideal = [panel["point"](panel["t0"] + (panel["t1"] - panel["t0"]) * i / 200)
             for i in range(201)]
    kept = chain_samples(panel["kept"])
    tail = chain_samples(panel["tail"])
    cx, cy = f(panel["cut_p"])
    d1 = G3.derivative(panel["kept"][-1], 1.0, 1)
    sp = math.hypot(*d1)
    tx = (d1[0] / sp, d1[1] / sp)
    L = 0.10 * max(x1 - x0, y1 - y0)
    a = f((panel["cut_p"][0] - L * tx[0], panel["cut_p"][1] - L * tx[1]))
    b = f((panel["cut_p"][0] + L * tx[0], panel["cut_p"][1] + L * tx[1]))
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{panel['name']} extend and cut">
  <rect width="{w}" height="{h}" fill="{PAPER}"/>
  <path d="{path(ideal, f)}" fill="none" stroke="{MUTED}" stroke-width="1" stroke-dasharray="4 4"/>
  <path d="{path(tail, f)}" fill="none" stroke="{GOLD}" stroke-width="1.6" stroke-dasharray="5 4"/>
  <path d="{path(kept, f)}" fill="none" stroke="{INK}" stroke-width="2.4"/>
  <line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{BLUE}" stroke-width="1.4"/>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="6.5" fill="none" stroke="{GREEN}" stroke-width="1.8"/>
  <text x="{cx + 10:.1f}" y="{cy - 8:.1f}" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="{GREEN}">cut</text>
  <text x="12" y="22" font-family="Georgia,serif" font-size="14" fill="{INK}">Fig. G3.X · {panel['name']} · cut at t = {panel['cut_t']:.3f}</text>
  <text x="12" y="40" font-family="ui-monospace,Menlo,monospace" font-size="10.5" fill="{MUTED}">kept {len(panel['kept'])} spans · tail discarded {len(panel['tail'])} · cut deviation {panel['distance']:.1e} · G3 across cut {panel['g3']:.1e}</text>
  <text x="{w / 2:.0f}" y="{h - 10}" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="10.5" fill="{MUTED}">x (model units)</text>
  <g font-family="Georgia,serif" font-size="11">
    <line x1="12" y1="{h - 26}" x2="38" y2="{h - 26}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="4 4"/><text x="44" y="{h - 22}" fill="{INK}">ideal</text>
    <line x1="92" y1="{h - 26}" x2="118" y2="{h - 26}" stroke="{INK}" stroke-width="2.4"/><text x="124" y="{h - 22}" fill="{INK}">kept</text>
    <line x1="172" y1="{h - 26}" x2="198" y2="{h - 26}" stroke="{GOLD}" stroke-width="1.6" stroke-dasharray="5 4"/><text x="204" y="{h - 22}" fill="{INK}">discarded tail</text>
  </g>
</svg>"""


def table(panels):
    rows = "".join(
        f"<tr><td>{p['name']}</td><td>{p['cut_t']:.3f}</td>"
        f"<td>{p['distance']:.1e}</td><td>{p['tangent_err']:.1e}°</td>"
        f"<td>{p['kappa_err']:.1e}</td><td>{p['rate_err']:.1e}</td>"
        f"<td>{p['g3']:.1e}</td><td class=\"{'ok' if p['ok'] else 'bad'}\">"
        f"{'pass' if p['ok'] else 'FAIL'}</td></tr>" for p in panels)
    return ("<table><tr><th>curve</th><th>cut t</th><th>cut deviation</th>"
            "<th>tangent error</th><th>κ error</th><th>dκ/ds error</th>"
            "<th>G3 across cut</th><th>cut gate</th></tr>" + rows + "</table>")


CSS = """
:root{--paper:%(paper)s;--ink:%(ink)s;--muted:%(muted)s;--rule:%(rule)s}
*{box-sizing:border-box} body{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}
main{max-width:1120px;margin:0 auto;padding:34px 22px 70px}
.eyebrow{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}
h1{font-size:31px;line-height:1.12;margin:0 0 8px} h2{font-size:20px;margin:0 0 8px}
.lede{max-width:920px;color:var(--muted)}
.panel{background:var(--paper);border:1px solid var(--rule);padding:16px 18px;margin:0 0 18px}
table{border-collapse:collapse;font:12px/1.5 ui-monospace,Menlo,monospace;margin:10px 0;width:100%%}
th,td{border:1px solid var(--rule);padding:5px 8px;text-align:right} th{color:var(--muted);font-weight:400}
.ok{color:%(green)s} .bad{color:%(red)s;font-weight:700}
.small{font:12px/1.6 ui-monospace,Menlo,monospace;color:var(--muted)}
.rule{background:#fffdf7;border-left:4px solid %(gold)s;padding:12px 16px;margin:0 0 18px}
code{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}
""" % {"paper": PAPER, "ink": INK, "muted": MUTED, "rule": RULE,
       "green": GREEN, "red": RED, "gold": GOLD}


def log_panel():
    b = 0.2
    point = lambda t: (math.exp(b * t) * math.cos(t), math.exp(b * t) * math.sin(t))

    def rd(t, order):
        z = complex(b, 1.0) ** order * complex(math.cos(t), math.sin(t)) * math.exp(b * t)
        return (z.real, z.imag)

    def tangent(t):
        d = rd(t, 1)
        s = math.hypot(*d)
        return (d[0] / s, d[1] / s)

    def kappa(t):
        d, dd = rd(t, 1), rd(t, 2)
        return G3.cross(d, dd) / math.hypot(*d) ** 3

    def rho(t):
        d, dd, ddd = rd(t, 1), rd(t, 2), rd(t, 3)
        sp = math.hypot(*d)
        N = G3.cross(d, dd)
        Np = G3.cross(d, ddd)
        return (Np / sp ** 3 - 3 * N * (d[0] * dd[0] + d[1] * dd[1]) / sp ** 5) / sp

    return cut_panel("log spiral stem", point, tangent, kappa, rho,
                     0.0, 2.0 * math.pi, 0.76, nspans=8)


def sine_panel():
    point = lambda t: (t, math.sin(2.0 * t))
    tangent = lambda t: (1.0 / math.hypot(1.0, 2.0 * math.cos(2.0 * t)),
                         2.0 * math.cos(2.0 * t) / math.hypot(1.0, 2.0 * math.cos(2.0 * t)))
    kappa = lambda t: -4.0 * math.sin(2.0 * t) / (1.0 + 4.0 * math.cos(2.0 * t) ** 2) ** 1.5
    # d(kappa)/ds for y = sin 2x, via the graph formula
    def rho(t):
        fp = 2.0 * math.cos(2.0 * t)
        fpp = -4.0 * math.sin(2.0 * t)
        fppp = -8.0 * math.cos(2.0 * t)
        return ((fppp * (1 + fp * fp) - 3 * fp * fpp * fpp)
                / (1 + fp * fp) ** 3)
    return cut_panel("sine ending", point, tangent, kappa, rho,
                     0.0, math.pi, 0.78, nspans=8)


PANELS = [log_panel(), sine_panel()]


def build():
    cards = "".join(
        f"<section class=\"panel\"><h2>{p['name']}</h2>{figure(p)}</section>"
        for p in PANELS)
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>G3 extend-and-cut terminals</title>
<style>{CSS}</style></head><body><main>
<p class="eyebrow">curve-lab · G3 terminals</p>
<h1>Extend, then cut at the station</h1>
<p class="lede">A stem or an ending often stops at a station on a longer smooth curve.
The conveyor fits the longer run, finds the span containing the station, and splits it with
de Casteljau. The kept chain's new end is interior to a G3 chain, so it inherits the G3
data; the discarded tail is drawn only to prove the curve continued. This is the third
case in the G3 rule — the first two are a smooth natural end (land on it) and a singular
end (trim or reject).</p>

<div class="rule"><strong>The cut is a station, not a singularity.</strong> The page measures
the cut point's distance from the ideal, the tangent, curvature and curvature-rate errors,
and the G3 defect across the split before the tail is thrown away. The cut gate is
1% of the curve size, 1° of tangent, 0.05 of curvature, 0.1 of curvature-rate, and 1e-9
across the split; otherwise the curve should be trimmed or rejected, not cut to hide an
overshoot.</div>

<section class="panel">
<h2>The measurements</h2>
{table(PANELS)}
<p class="small">The cut tangent is blue in each figure; the green ring is the cut. The
dashed gold line is the discarded continuation. The solid line is the terminal.</p>
</section>

{cards}

<section class="panel">
<p class="small">Back to the <a href="g3-showcase.html">G3 showcase</a> ·
the <a href="g3-catalogue.html">G3 catalogue</a> ·
the <a href="g3-notes.html">G3 notes</a>.</p>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "g3-cut.html"
    out.write_text(html, encoding="utf-8")
    print(out)
    return out


if __name__ == "__main__":
    build()
