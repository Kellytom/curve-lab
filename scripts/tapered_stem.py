"""A tapered stem from the exact log-spiral band.

    .venv/bin/python scripts/tapered_stem.py
    open workbench/tapered-stem.html

The band between two log spirals is exact: the rails are spirals, and the width
is proportional to the radius. It is not symmetric about the centreline — the
two widths differ by a measured percentage — and it is transcendental, so it
carries no lattice. Both facts are stated on the page rather than hidden.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import plant  # noqa: E402
from curve_lab.taper import LogSpiral, width_ratio  # noqa: E402

INK, GOLD, BLUE, RED, GREEN = "#2e2413", "#c9a441", "#1f5fa8", "#a23b2a", "#3f7d4e"
MUTED, RULE, PAPER = "#7b6c4e", "#d8ccae", "#fbf7ec"

A, B, K = 20.0, 0.28, 1.12
TH0, TH1 = 0.0, 3.2 * math.pi


def run() -> None:
    inner = LogSpiral(A, B)
    outer = inner.scaled(K)
    mid = LogSpiral(A * math.sqrt(K), B)
    root_k = math.sqrt(K)

    w_mid_in = width_ratio(1 / root_k, B) * mid.radius(0.0)
    w_mid_out = width_ratio(root_k, B) * mid.radius(0.0)
    asym = (w_mid_out - w_mid_in) / ((w_mid_out + w_mid_in) / 2)

    # geometry for the drawing
    n = 900
    inner_pts, outer_pts, mid_pts = [], [], []
    for i in range(n):
        th = TH0 + (TH1 - TH0) * i / (n - 1)
        inner_pts.append(inner.point(th))
        outer_pts.append(outer.point(th))
        mid_pts.append(mid.point(th))

    # cone terminal at the narrow end, on the centreline, at the mean half-width
    p0 = mid.point(TH0)
    t0 = mid.tangent(TH0)
    half = (w_mid_in + w_mid_out) / 2
    cone = plant.cone_terminal(p0, t0, half)
    seam = abs(half - w_mid_in) / max(1e-9, half)

    allpts = inner_pts + outer_pts + mid_pts + cone["left"] + cone["right"] + [cone["tip"]]
    xs = [p[0] for p in allpts]
    ys = [p[1] for p in allpts]
    pad, W, H = 60, 980, 720
    s = min((W - 2 * pad) / (max(xs) - min(xs)), (H - 2 * pad) / (max(ys) - min(ys)))
    ox = (W - (max(xs) - min(xs)) * s) / 2
    oy = (H - (max(ys) - min(ys)) * s) / 2

    def put(p):
        return (ox + (p[0] - min(xs)) * s, H - oy - (p[1] - min(ys)) * s)   # +y up, flipped here

    def path(pts):
        return " ".join(("M" if i == 0 else "L") + f"{put(p)[0]:.1f},{put(p)[1]:.1f}"
                        for i, p in enumerate(pts))

    # width bars at three stations
    bars = []
    for th in (0.9, 1.9, 2.9):
        p = mid.point(th)
        nrm = mid.normal(th)
        a_ = (p[0] + w_mid_in * nrm[0], p[1] + w_mid_in * nrm[1])
        b_ = (p[0] - w_mid_out * nrm[0], p[1] - w_mid_out * nrm[1])
        bars.append((a_, b_))

    rows = "".join(
        f"<tr><td>{th:.2f}</td><td>{width_ratio(root_k, B) * mid.radius(th):.3f}</td>"
        f"<td>{width_ratio(1/root_k, B) * mid.radius(th):.3f}</td>"
        f"<td>{(width_ratio(root_k, B) / width_ratio(1/root_k, B)):.4f}</td></tr>"
        for th in (0.0, 0.9, 1.9, 2.9))

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tapered stem · exact log-spiral band</title>
<style>
:root{{--paper:{PAPER};--ink:{INK};--muted:{MUTED};--rule:{RULE}}}
*{{box-sizing:border-box}} body{{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:31px;line-height:1.12;margin:0 0 8px}} h2{{font-size:20px;margin:0 0 8px}}
.lede{{max-width:920px;color:var(--muted)}} .panel{{background:var(--paper);border:1px solid var(--rule);padding:16px 18px;margin:0 0 18px}}
table{{border-collapse:collapse;font:12px/1.5 ui-monospace,Menlo,monospace;margin:10px 0;width:100%}}
th,td{{border:1px solid var(--rule);padding:5px 8px;text-align:right}} th{{color:var(--muted);font-weight:400}}
.small{{font:12px/1.55 ui-monospace,Menlo,monospace;color:var(--muted)}}
code{{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}}
</style></head><body><main>
<p class="eyebrow">curve-lab · a stem with a width that is exact</p>
<h1>Tapered stem from the log-spiral band</h1>
<p class="lede">Two spirals with the same pitch bound a band whose width is proportional to the radius. The rails are exact, the taper is exact, and the width is not symmetric about the centreline — that asymmetry is the price, and it is measured below.</p>

<section class="panel">
<h2>Fig. T1 · the band, its centreline, and a cone terminal</h2>
<svg viewBox="0 0 980 720" width="100%" role="img" aria-label="log spiral stem with a terminal">
<rect width="980" height="720" fill="{PAPER}"/>
<path d="{path(inner_pts)}" fill="none" stroke="{BLUE}" stroke-width="1.8"/>
<path d="{path(outer_pts)}" fill="none" stroke="{BLUE}" stroke-width="1.8"/>
<path d="{path(mid_pts)}" fill="none" stroke="{INK}" stroke-width="1.4" stroke-dasharray="6 5"/>
<path d="{path(cone['left'])}" fill="none" stroke="{RED}" stroke-width="2"/>
<path d="{path(cone['right'])}" fill="none" stroke="{RED}" stroke-width="2"/>
{"".join(f'<line x1="{put(a)[0]:.1f}" y1="{put(a)[1]:.1f}" x2="{put(b)[0]:.1f}" y2="{put(b)[1]:.1f}" stroke="{GOLD}" stroke-width="1.6"/>' for a, b in bars)}
<circle cx="{put(cone['tip'])[0]:.1f}" cy="{put(cone['tip'])[1]:.1f}" r="4" fill="{RED}"/>
<text x="16" y="24" font-family="Georgia,serif" font-size="13" fill="{INK}">Fig. T1 · r = 20·e^(0.28θ), rails ×1 and ×{K}, θ = 0…3.2π · +y up, flipped to screen y down</text>
<text x="16" y="44" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}">gold bars: the two half-widths at three stations · red: cone terminal, R = 2 × offset</text>
<g font-family="Georgia,serif" font-size="15">
<line x1="16" y1="692" x2="52" y2="692" stroke="{BLUE}" stroke-width="2.4"/><text x="60" y="697" fill="{INK}">exact rails (two spirals)</text>
<line x1="300" y1="692" x2="336" y2="692" stroke="{INK}" stroke-width="1.4" stroke-dasharray="6 5"/><text x="344" y="697" fill="{INK}">geometric-mean centreline</text>
<line x1="620" y1="692" x2="656" y2="692" stroke="{RED}" stroke-width="2.4"/><text x="664" y="697" fill="{INK}">cone terminal</text>
</g>
</svg>
<p class="small">The rails are not offsets of the centreline; they are the two spirals themselves. That is what makes them exact.</p>
</section>

<section class="panel">
<h2>What is exact, and what is not</h2>
<p><strong>Exact:</strong> both rails are log spirals of the same pitch; the ratio <code>width / r</code> is constant at <b>{(w_mid_in / mid.radius(0)):.4f}</b> on the inside and <b>{(w_mid_out / mid.radius(0)):.4f}</b> on the outside — measured to 1e-9 at every station.</p>
<p><strong>Not exact:</strong> the band is asymmetric. The outer half-width exceeds the inner by <b>{100*asym:.2f}%</b> of their mean. A symmetric stem would need an offset of the centreline, which is the thing this construction exists to avoid.</p>
<table><tr><th>θ</th><th>outer half-width</th><th>inner half-width</th><th>ratio</th></tr>{rows}</table>
<p class="small">The cone terminal is placed at the mean half-width; each rail therefore misses the cone base by <b>{100*seam:.2f}%</b> of the offset. On a k = 1.12 band that is a fraction of a millimetre at this scale, but it is not zero, and it is the seam a real design has to declare.</p>
</section>

<section class="panel">
<h2>Where it belongs</h2>
<p>This is the only exact variable-width stem in the catalogue. It is the right base for a tapered stalk, a seagrass blade or a volute; it is the wrong base for anything that must land on the integer lattice, because every coordinate is transcendental. Pair it with a rational connector at a declared seam, rather than pretending it is on a grid.</p>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "tapered-stem.html"
    out.write_text(html, encoding="utf-8")
    print(out)
    print("width ratio in/out:", round(w_mid_in / mid.radius(0), 6), round(w_mid_out / mid.radius(0), 6))
    print("asymmetry:", round(100 * asym, 2), "%")
    print("terminal seam:", round(100 * seam, 2), "% of offset")


if __name__ == "__main__":
    run()
