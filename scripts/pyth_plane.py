"""The p-triple plane, and the parabola's parallels.

    .venv/bin/python scripts/pyth_plane.py
    open workbench/pyth-plane.html

Three things on one page:

1. In the (m, n) plane the level sets of `a = m^2 - n^2` and `b = 2mn` are
   hyperbolae; their integer points are the factorisations of `a` and of `b/2`.
   Near the origin they are sharp (radius of curvature sqrt(a) at the vertex);
   far out they flatten.
2. In the (a, b) plane the curves of fixed m are parabolas opening sideways.
3. The evolute of a parabola is a semicubical parabola; the involutes of that
   evolute are exactly the parallels of the original parabola - and those are
   not parabolas.
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INK, GOLD, BLUE, RED, GREEN = "#2e2413", "#c9a441", "#1f5fa8", "#a23b2a", "#3f7d4e"
MUTED, RULE, PAPER = "#7b6c4e", "#d8ccae", "#fbf7ec"


class Frame:
    def __init__(self, w, h, x0, x1, y0, y1, pad=54):
        self.w, self.h, self.pad = w, h, pad
        self.x0, self.x1, self.y0, self.y1 = x0, x1, y0, y1
        self.s = min((w - 2 * pad) / (x1 - x0), (h - 2 * pad) / (y1 - y0))

    def __call__(self, p):
        return (self.pad + (p[0] - self.x0) * self.s,
                self.h - self.pad - (p[1] - self.y0) * self.s)


def poly(pts, f):
    return " ".join(("M" if i == 0 else "L") + f"{f(p)[0]:.1f},{f(p)[1]:.1f}"
                    for i, p in enumerate(pts))


def axes(f, xlabel, ylabel, ticks=(), yticks=()):
    out = [f'<line x1="{f.pad}" y1="{f.h-f.pad}" x2="{f.w-f.pad}" y2="{f.h-f.pad}" stroke="{INK}" stroke-width="1.2"/>',
           f'<line x1="{f.pad}" y1="{f.h-f.pad}" x2="{f.pad}" y2="{f.pad}" stroke="{INK}" stroke-width="1.2"/>']
    for t in ticks:
        x = f((t, f.y0))[0]
        out.append(f'<line x1="{x:.1f}" y1="{f.h-f.pad}" x2="{x:.1f}" y2="{f.h-f.pad+5}" stroke="{INK}"/>')
        out.append(f'<text x="{x:.1f}" y="{f.h-f.pad+20}" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="{MUTED}" text-anchor="middle">{t}</text>')
    for t in yticks:
        y = f((f.x0, t))[1]
        out.append(f'<line x1="{f.pad}" y1="{y:.1f}" x2="{f.pad-5}" y2="{y:.1f}" stroke="{INK}"/>')
        out.append(f'<text x="{f.pad-9}" y="{y+4:.1f}" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="{MUTED}" text-anchor="end">{t}</text>')
    out.append(f'<text x="{f.w-f.pad}" y="{f.h-f.pad+40}" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}" text-anchor="end">{xlabel} →</text>')
    out.append(f'<text x="{f.pad-12}" y="{f.pad-18}" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}">{ylabel} ↑</text>')
    return "".join(out)


def triples_upto(C):
    out = set()
    for m in range(2, int(math.isqrt(C)) + 2):
        for n in range(1, m):
            a, b, c = m * m - n * n, 2 * m * n, m * m + n * n
            if a > 0 and c <= C:
                out.add((a, b, c))
    return out


def factor_rows(a):
    rows = []
    for d in range(1, int(math.isqrt(a)) + 1):
        if a % d:
            continue
        e = a // d
        if (e - d) % 2:
            continue
        n, m = (e - d) // 2, (e + d) // 2
        if n >= 1 and m > n:
            rows.append((d, e, m, n, m * m + n * n))
    return rows


def curvature_radius_vertex(a):
    # m = sqrt(a + n^2): radius of curvature at n = 0 is sqrt(a)
    return math.sqrt(a)


def parabola_pts(t0, t1, n=400):
    return [(t0 + (t1 - t0) * i / (n - 1), (t0 + (t1 - t0) * i / (n - 1)) ** 2 / 2)
            for i in range(n)]


def evolute_pts(t0, t1, n=400):
    out = []
    for i in range(n):
        t = t0 + (t1 - t0) * i / (n - 1)
        nrm = (-t / math.sqrt(1 + t * t), 1 / math.sqrt(1 + t * t))
        rho = (1 + t * t) ** 1.5
        out.append((t + rho * nrm[0], t * t / 2 + rho * nrm[1]))
    return out


def involute_pts(c, t0=0.02, t1=3.0, n=400):
    out = []
    for i in range(n):
        t = t0 + (t1 - t0) * i / (n - 1)
        nrm = (-t / math.sqrt(1 + t * t), 1 / math.sqrt(1 + t * t))
        s = (1 + t * t) ** 1.5 - 1
        E = (t + (1 + t * t) ** 1.5 * nrm[0], t * t / 2 + (1 + t * t) ** 1.5 * nrm[1])
        out.append((E[0] - (s - c) * nrm[0], E[1] - (s - c) * nrm[1]))
    return out


def parabola_fit_residual(d, tmax=3.0, n=4000):
    """Residual of the best even parabola y = A(x/tmax)^2 + C fitted to the offset."""
    pts = []
    for i in range(n):
        t = -tmax + 2 * tmax * i / (n - 1)
        nx, ny = -t / math.sqrt(1 + t * t), 1 / math.sqrt(1 + t * t)
        pts.append((t + d * nx, t * t / 2 + d * ny))
    S2 = S4 = Sy = Su2y = 0.0
    for x, y in pts:
        u = x / tmax
        u2 = u * u
        S2 += u2
        S4 += u2 * u2
        Sy += y
        Su2y += u2 * y
    det = len(pts) * S4 - S2 * S2
    A = (len(pts) * Su2y - S2 * Sy) / det
    C = (S4 * Sy - S2 * Su2y) / det
    return max(abs(A * (x / tmax) ** 2 + C - y) for x, y in pts)


def run() -> None:
    # ---- figure 1: (m, n) plane
    f1 = Frame(980, 700, 0, 14, 0, 14)
    curves = []
    for a in (5, 12, 21, 45):
        pts = []
        for i in range(2001):
            n = 14.0 * i / 2000
            m = math.sqrt(a + n * n)
            if m <= 14:
                pts.append((m, n))
        curves.append(("a", a, pts))
    for b in (12, 24, 48, 96):
        pts = [(m, b / (2 * m)) for m in [0.3 + 13.7 * i / 2000 for i in range(2001)] if b / (2 * m) <= 14]
        curves.append(("b", b, pts))

    tri = triples_upto(200)
    points = sorted({(m, n) for m in range(2, 15) for n in range(1, m)
                     if (m * m + n * n) <= 200 and math.gcd(m, n) == 1})

    f2 = Frame(980, 640, 0, 10, -4, 26)
    mcurves = []
    for m in (3, 4, 5, 6, 7, 8):
        pts = []
        for i in range(1201):
            b = 12.0 * i / 1200
            pts.append((b, m * m - b * b / (4 * m * m)))
        mcurves.append((m, pts))

    f3 = Frame(980, 560, -6, 6, -2, 9)
    par = parabola_pts(-3, 3)
    evo = evolute_pts(-2.6, 2.6)
    inv1 = involute_pts(0.0)
    inv2 = involute_pts(1.5)

    resid_small = parabola_fit_residual(0.1)
    resid_big = parabola_fit_residual(0.5)
    inv_err = max(math.dist(involute_pts(-1.0, 0.05, 3.0, 300)[i], parabola_pts(0.05, 3.0, 300)[i])
                  for i in range(0, 300, 7))

    counts = [(C, len(triples_upto(C))) for C in (100, 500, 1000, 5000)]
    rows = "".join(f"<tr><td>{C}</td><td>{n}</td><td>{C/(2*math.pi):.1f}</td></tr>" for C, n in counts)
    frows = "".join(
        f"<tr><td>{a}</td><td>{' · '.join(f'{d}×{e}→({m},{n}), c={c}' for d,e,m,n,c in factor_rows(a)) or '—'}</td></tr>"
        for a in (5, 12, 21, 40, 45))
    vrows = "".join(f"<tr><td>{a}</td><td>{math.sqrt(a):.3f}</td><td>{curvature_radius_vertex(a):.3f}</td></tr>"
                    for a in (5, 45, 405, 4005))

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>p-triple plane · hyperbolae, factorisation, parabola parallels</title>
<style>
:root{{--paper:{PAPER};--ink:{INK};--muted:{MUTED};--rule:{RULE}}}
*{{box-sizing:border-box}} body{{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:34px 22px 70px}}
.eyebrow{{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
h1{{font-size:31px;line-height:1.12;margin:0 0 8px}} h2{{font-size:20px;margin:0 0 8px}}
.lede{{max-width:920px;color:var(--muted)}} .panel{{background:var(--paper);border:1px solid var(--rule);padding:16px 18px;margin:0 0 18px}}
table{{border-collapse:collapse;font:12px/1.5 ui-monospace,Menlo,monospace;margin:10px 0;width:100%}}
th,td{{border:1px solid var(--rule);padding:5px 8px;text-align:right}} th{{color:var(--muted);font-weight:400}}
.small{{font:12px/1.55 ui-monospace,Menlo,monospace;color:var(--muted)}}
code{{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}}
</style></head><body><main>
<p class="eyebrow">curve-lab · the p-triple plane</p>
<h1>Hyperbolae, factorisation, and a parabola's parallels</h1>
<p class="lede">The level sets in the p-triple plane are not decoration: a fixed <code>a</code> or a fixed <code>b</code> is a hyperbola whose integer points are exactly the factorisations of that number. And the parabola in that plane has an exact parallel family — reached through its evolute, not through an offset formula.</p>

<section class="panel">
<h2>Fig. P1 · the (m, n) plane: a and b are hyperbolae</h2>
<svg viewBox="0 0 980 700" width="100%" role="img" aria-label="m n plane with hyperbolae and integer points">
<rect width="980" height="700" fill="{PAPER}"/>
{axes(f1, "m", "n", ticks=(0,2,4,6,8,10,12,14), yticks=(2,4,6,8,10,12,14))}
{"".join(f'<path d="{poly(c[2], f1)}" fill="none" stroke="{BLUE if c[0]=="a" else GOLD}" stroke-width="1.6"/>' for c in curves)}
{"".join(f'<text x="{f1((c[2][-1][0], c[2][-1][1]))[0]-6:.1f}" y="{f1((c[2][-1][0], c[2][-1][1]))[1]-6:.1f}" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="{BLUE if c[0]=="a" else GOLD}">{c[0]}={c[1]}</text>' for c in curves)}
{"".join(f'<circle cx="{f1(p)[0]:.1f}" cy="{f1(p)[1]:.1f}" r="3" fill="{RED}"/>' for p in points)}
<text x="16" y="24" font-family="Georgia,serif" font-size="13" fill="{INK}">Fig. P1 · m² − n² = a (blue) and 2mn = b (gold); red dots are primitive (m,n) with c ≤ 200 · +y up</text>
<g font-family="Georgia,serif" font-size="15">
<line x1="16" y1="672" x2="52" y2="672" stroke="{BLUE}" stroke-width="2"/><text x="60" y="677" fill="{INK}">a = const</text>
<line x1="190" y1="672" x2="226" y2="672" stroke="{GOLD}" stroke-width="2"/><text x="234" y="677" fill="{INK}">b = const</text>
<circle cx="380" cy="672" r="4" fill="{RED}"/><text x="392" y="677" fill="{INK}">integer (m,n)</text>
</g>
</svg>
<p class="small">Both families are hyperbolae. A fixed <code>a</code> has vertex at <code>(√a, 0)</code> and asymptote <code>n = m</code>; a fixed <code>b</code> is <code>n = b/2m</code>. Near the origin the curves are sharp; far out they flatten.</p>
<table><tr><th>a</th><th>factorisations of a, and the triples they give</th></tr>{frows}</table>
<table><tr><th>a</th><th>vertex √a</th><th>radius of curvature there</th></tr>{vrows}</table>
<p class="small">The radius of curvature at the vertex is exactly <code>√a</code>, so the "sharp near 0,0" impression is a fact: it grows as the square root of the level.</p>
</section>

<section class="panel">
<h2>Fig. P2 · the (a, b) plane: fixed m is a parabola, not a hyperbola</h2>
<svg viewBox="0 0 980 640" width="100%" role="img" aria-label="a b plane with side-opening parabolas">
<rect width="980" height="640" fill="{PAPER}"/>
{axes(f2, "b", "a", ticks=(2,4,6,8,10), yticks=(0,5,10,15,20,25))}
{"".join(f'<path d="{poly([p for p in pts if -4 <= p[1] <= 26], f2)}" fill="none" stroke="{GREEN}" stroke-width="1.6"/>' for m, pts in mcurves)}
{"".join(f'<text x="{f2((9.6, m*m-9.6*9.6/(4*m*m)))[0]-8:.1f}" y="{f2((9.6, m*m-9.6*9.6/(4*m*m)))[1]+4:.1f}" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="{GREEN}">m={m}</text>' for m, pts in mcurves)}
<text x="16" y="24" font-family="Georgia,serif" font-size="13" fill="{INK}">Fig. P2 · a = m² − b²/(4m²) for m = 3…8 · each opens sideways, vertex at (0, m²)</text>
<g font-family="Georgia,serif" font-size="15"><line x1="16" y1="612" x2="52" y2="612" stroke="{GREEN}" stroke-width="2"/><text x="60" y="617" fill="{INK}">fixed m (a parabola)</text></g>
</svg>
<p class="small">Eliminating <code>n</code> at fixed <code>m</code> gives <code>a = m² − b²/(4m²)</code>. The sideways curvature in the plot is this parabola, not a hyperbola; the hyperbolae live in the <code>(m,n)</code> plane above.</p>
</section>

<section class="panel">
<h2>Fig. P3 · the parabola's evolute and its exact parallels</h2>
<svg viewBox="0 0 980 560" width="100%" role="img" aria-label="parabola, its evolute and involute parallels">
<rect width="980" height="560" fill="{PAPER}"/>
{axes(f3, "x", "y", ticks=(-6,-4,-2,0,2,4,6), yticks=(0,2,4,6,8))}
<path d="{poly(par, f3)}" fill="none" stroke="{INK}" stroke-width="2.4"/>
<path d="{poly(evo, f3)}" fill="none" stroke="{RED}" stroke-width="2"/>
<path d="{poly(inv1, f3)}" fill="none" stroke="{BLUE}" stroke-width="1.8" stroke-dasharray="7 5"/>
<path d="{poly(inv2, f3)}" fill="none" stroke="{GOLD}" stroke-width="1.8" stroke-dasharray="4 4"/>
<text x="16" y="24" font-family="Georgia,serif" font-size="13" fill="{INK}">Fig. P3 · y = x²/2, its evolute, and two involutes of the evolute (the parallels) · +y up, flipped to screen y down</text>
<g font-family="Georgia,serif" font-size="15">
<line x1="16" y1="532" x2="52" y2="532" stroke="{INK}" stroke-width="3"/><text x="60" y="537" fill="{INK}">parabola</text>
<line x1="160" y1="532" x2="196" y2="532" stroke="{RED}" stroke-width="3"/><text x="204" y="537" fill="{INK}">evolute (semicubical)</text>
<line x1="420" y1="532" x2="456" y2="532" stroke="{BLUE}" stroke-width="2" stroke-dasharray="7 5"/><text x="464" y="537" fill="{INK}">involute: parallel d = 1</text>
<line x1="690" y1="532" x2="726" y2="532" stroke="{GOLD}" stroke-width="2" stroke-dasharray="4 4"/><text x="734" y="537" fill="{INK}">d = 2.5</text>
</g>
</svg>
<p>Take the evolute, then take its involute with a shift in arc length and you get the parabola back (shift <code>−1</code>, error <b>{inv_err:.1e}</b>) or, for any other shift, an exact parallel of it.</p>
<p>But a parallel of a parabola is <em>not</em> a parabola. Fitting a parabola to the offset leaves a residual of <b>{resid_small*100:.1f}% of d</b> at <code>d = 0.1</code> and <b>{resid_big*100:.1f}% of d</b> at <code>d = 0.5</code> (the offset folds beyond <code>d = 1</code>, the vertex radius):</p>
<p class="small">So the involute/evolute route gives the parallels <em>exactly</em> — and proves, rather than denies, that they are a different family. There is no parallel parabola.</p>
</section>

<section class="panel">
<h2>How many triples, and how they crowd</h2>
<table><tr><th>c ≤</th><th>triples (all, including multiples)</th><th>primitive only, N/2π</th></tr>{rows}</table>
<p class="small">The count grows linearly in <code>c</code>, which is why the hyperbolae look dense near the origin and thin farther out: the same linear density spread over a square grows sparser as <code>1/r</code>.</p>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "pyth-plane.html"
    out.write_text(html, encoding="utf-8")
    print(out)
    print("involute shift -1 error:", inv_err)
    print("parabola fit residual, d=0.5:", resid_small, " d=2:", resid_big)


if __name__ == "__main__":
    run()
