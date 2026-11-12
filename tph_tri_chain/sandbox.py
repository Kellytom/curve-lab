"""Build tph-tri-sandbox.html: the working page, exact fractions only.

CSS is lifted from workbench/showcase.html at build time so the page matches
the rest of the workbench. No value is written as a decimal.

Run:  .venv/bin/python tph_tri_chain/sandbox.py
"""

import re
from fractions import Fraction as F
from math import gcd
from pathlib import Path

from chain import chain, grid, integral, primitive

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
N = 12


def fmt(x):
    """Exact fraction, never a decimal."""
    x = F(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def pt(x, y):
    return f"({fmt(x)}, {fmt(y)})"


def css():
    src = (ROOT / "workbench" / "showcase.html").read_text()
    blocks = re.findall(r"<style[^>]*>(.*?)</style>", src, re.S)
    return max(blocks, key=len)


def chordal(T, n):
    return [integral(F(i) * T / n)[:2] for i in range(n + 1)]


def chordal_exact(T, n):
    """Chordal length as (1/M) * sum of square roots of integers, all exact."""
    pts = chordal(T, n)
    m = 1
    for a, b in zip(pts, pts[1:]):
        for v in (b[0] - a[0], b[1] - a[1]):
            m = m * v.denominator // gcd(m, v.denominator)
    rads = []
    for a, b in zip(pts, pts[1:]):
        dx, dy = (b[0] - a[0]) * m, (b[1] - a[1]) * m
        rads.append(int(dx * dx + dy * dy))
    return m, rads


STOPS = [F(2), F(21, 10), F(12, 5), F(5, 2), F(3), F(24, 5), F(4)]


def table(headers, rows, cls="tbl"):
    out = [f'<table class="{cls}"><thead><tr>'
           + "".join(f"<th>{h}</th>" for h in headers) + "</tr></thead><tbody>"]
    for r in rows:
        out.append("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
    out.append("</tbody></table>")
    return "\n".join(out)


def build():
    h = []
    h.append('<p class="eyebrow">curve-lab · tph_tri_chain · sandbox</p>')
    h.append("<h1>Integer hits on the Tschirnhausen cubic</h1>")
    h.append('<p class="lede">Everything here is exact. No value is written as a '
             'decimal, because a decimal cannot tell you whether a point is on the '
             'lattice. Every comparison is at twelve triangles per side.</p>')

    # 1 -------------------------------------------------------------
    h.append('<div class="key"><strong>The rule, in whole units.</strong> y = t&sup2; is a whole '
             'number only if t is a whole number. Once t is whole, '
             'x = t &minus; t&sup3;/3 is whole exactly when 3 divides t. So the curve '
             'meets whole-number points only at t = 0, 3, 6, 9 &hellip;, plus the '
             'waist (0,&nbsp;3), which is reached at t = &plusmn;&radic;3 and so by '
             'no fractional chain.</div>')

    rows = []
    for u in range(0, 6):
        x, y, s = integral(F(3 * u))
        rows.append([str(3 * u), fmt(x), fmt(y), fmt(s),
                     {0: "nose", 3: "first hit"}.get(3 * u, "")])
    h.append("<h2>The hits, exactly</h2>")
    h.append(table(["t", "x", "y", "arc length", "note"], rows))

    # 2 -------------------------------------------------------------
    h.append("<h2>The grid exists to clear fractions</h2>")
    h.append("<p>A fractional coordinate is not a problem to be ruled out. Choose a "
             "pitch that is a multiple of the denominators and the point lands on a "
             "whole cell. That is the entire purpose of the pitch: 144/25 of a unit "
             "is 2880 cells at pitch 500.</p>")
    h.append("<p>So the useful question is not whether the height is a whole number, "
             "but how coarse a pitch makes the point whole, and whether the chain's "
             "own sides are whole at that same pitch.</p>")
    rows = []
    for T in STOPS:
        x, y, s = integral(T)
        gc = 1
        for v in (x, y, s):
            gc = gc * v.denominator // gcd(gc, v.denominator)
        gch = grid(chain(F(0), T, N)[0])
        rows.append([fmt(T), fmt(x), fmt(y), f"({fmt(x * gc)}, {fmt(y * gc)})",
                     str(gc), str(gch)])
    h.append(table(["stop t", "x", "y", "the point, in cells", "smallest pitch "
                    "for the curve", "smallest pitch for every chain side"], rows))
    h.append('<p class="note">t = 3 needs no scaling at all. Every other stop is '
             'exact too, at a pitch equal to its denominators: 3 at t = 2 and t = 4, '
             '24 at 5/2, 125 at 12/5, 1000 at 21/10. What singles out t = 3 is that '
             'it is the only stop exact in whole units. The chain needs a larger '
             'pitch than the curve at every stop, because each side has to be whole '
             'as well as each vertex.</p>')

    # 3 -------------------------------------------------------------
    h.append("<h2>Twelve triangles per side, both methods</h2>")
    rows = []
    for T in STOPS:
        r, w = chain(F(0), T, N)
        g = grid(r)
        xt, yt, st = integral(T)
        ct = chordal(T, N)[-1]
        m, rads = chordal_exact(T, N)
        rows.append([fmt(T), fmt(w), str(g), fmt(r[-1]["x"]),
                     fmt(r[-1]["x"] - xt), "yes" if r[-1]["y"] == yt else "no",
                     pt(ct[0], ct[1]), fmt(r[-1]["s"]),
                     f"(&#931;&#8730;)/{m}", fmt(st)])
    h.append(table(["stop t", "step width", "pitch", "midpoint chain tip x",
                    "gap", "y exact?", "straight joins tip", "midpoint length",
                    "chordal length", "exact length"], rows))
    m3, rads3 = chordal_exact(F(3), N)
    h.append('<p class="note">The chordal length is irrational, so it is written as '
             'an expression. At t = 3 it is '
             f'(&radic;{rads3[0]} + &radic;{rads3[1]} + &hellip; + &radic;{rads3[-1]})'
             f'/{m3}, twelve terms, denominator {m3}. The midpoint total at the same '
             f'count is the fraction {fmt(chain(F(0), F(3), N)[0][-1]["s"])}, because '
             'every side there is a whole-number triple.</p>')
    h.append('<p>At t = 3 the path of straight joins lands on the whole-number point '
             'exactly. The midpoint chain stops 1/64 short of it. The exchange is set '
             'out at the end of the page: exact positions, or exact lengths.</p>')

    # 4 -------------------------------------------------------------
    r, w = chain(F(0), F(3), N)
    g = grid(r)
    h.append("<h2>The twelve triangles at t = 3</h2>")
    h.append(f'<p class="note">Step width {fmt(w)}, pitch {g} cells per unit. Sides '
             f'given both in cells and as reduced triples.</p>')
    rows = []
    for k, row in enumerate(r, 1):
        cells = (int(row["dx"] * g), int(row["dy"] * g), int(row["ds"] * g))
        p = primitive(cells)
        rows.append([str(k), fmt(row["t"]), str(cells[0]), str(cells[1]),
                     str(cells[2]), f"({p[0]}, {p[1]}, {p[2]})"])
    h.append(table(["step", "middle t", "dx", "dy", "ds", "reduced triple"], rows))
    h.append(f'<p>The last vertex is {pt(r[-1]["x"], r[-1]["y"])} against the curve&rsquo;s '
             f'(&minus;6,&nbsp;9): short by 1/64 in x, exact in y.</p>')

    # 5 -------------------------------------------------------------
    h.append("<h2>The pitch, and where it comes from</h2>")
    h.append('<p>The pitch is the number of cells per unit, and the grid is the whole integer '
             'lattice at that pitch \u2014 not a box fitted round the curve. It depends on the '
             'step width and nothing else. Write the step width as a fraction in lowest '
             'terms, call the bottom number q:</p>')
    h.append('<pre class="note">pitch = q&sup3;\n'
             'pitch = 4 &times; q&sup3;    when the top number is odd</pre>')
    h.append('<p>With the count fixed at twelve, the step width is t/12, so the '
             'stopping point alone decides the pitch. That is the whole of it.</p>')
    rows = []
    for T in STOPS:
        w2 = T / N
        q, c = w2.denominator, w2.numerator
        g2 = q ** 3 * (4 if c % 2 else 1)
        r2, _ = chain(F(0), T, N)
        xt, yt, _ = integral(T)
        first = (int(r2[0]["dx"] * g2), int(r2[0]["dy"] * g2), int(r2[0]["ds"] * g2))
        rows.append([fmt(T), fmt(w2), str(g2),
                     pt(xt * g2, yt * g2), f"({first[0]}, {first[1]}, {first[2]})"])
    h.append(table(["stop t", "step width", "pitch",
                    "curve tip, in cells", "first step, in cells"], rows))
    h.append('<p><strong>Worked example, twelve triangles out to t = 4.</strong> The '
             'step width is 4/12 = 1/3. The bottom number is 3, the top number is odd, '
             'so the pitch is 4 &times; 27 = 108. It is small because the step is '
             'coarse: twelve triangles across four units is a big step, and a big step '
             'has a small bottom number.</p>')
    h.append('<p><strong>If the grid must be 3125.</strong> A power of five only '
             'arrives when the step width is 2/5 or 4/5, since 3125 is odd. At twelve '
             'triangles that means t = 24/5: the grid is 125, and 3125 is twenty-five '
             'of those, with 625 being five. The curve then runs to height 576/25 and '
             'fills only part of the grid.</p>')
    h.append('<p><strong>Same count, t = 3.</strong> Step width 1/4, bottom number 4, '
             'pitch 4 &times; 64 = 256. The very first '
             'step is evaluated at t = 1/8, so its sides are '
             '(1 &minus; 1/64)/4 &times; 256 = 63, then 2(1/8)/4 &times; 256 = 16, and '
             '(1 + 1/64)/4 &times; 256 = 65: the triple (63,&nbsp;16,&nbsp;65).</p>')

    # 6 -------------------------------------------------------------
    h.append("<h2>The glyph at t = 3, in whole units</h2>")
    h.append(table(["feature", "value"], [
        ["nose", "(0, 0)"],
        ["waist", "(0, 3), at t = &plusmn;&radic;3"],
        ["tips", "(&minus;6, 9) and (6, 9)"],
        ["body height", "3"],
        ["tail height", "6, exactly twice the body"],
        ["arc length, one side", "12"],
        ["full length, both sides", "24"],
    ]))
    h.append('<figure><img src="out/lattice-t3.svg" alt="the curve, the twelve '
             'triangles, and the whole-number points"><figcaption class="note">'
             'Fig. T1 &mdash; the 24 triangles at t = 3 on a grid of 256 cells per '
             'unit, the pitch the 1/4 step width forces. Unit lines are solid, '
             'quarter-unit lines pale. The rings are the curve&rsquo;s whole-number '
             'points; the chain&rsquo;s last vertex falls just inside the left one, '
             'by 1/64.</figcaption>'
             '</figure>')

    # 7 -------------------------------------------------------------
    h.append("<h2>Why the method works, and what the ends do</h2>")
    h.append('<figure><img src="out/midpoint.svg" alt="four panels: one step, the exact '
             'height, the drifting sideways part, and the two ends"><figcaption '
             'class="note">Fig. T2 &mdash; three steps over t = 0 to 3, step width 1. '
             'Panel A is one step; B shows why the height is exact; C shows the 1/12 '
             'that every step adds sideways; D shows where it ends up.</figcaption>'
             '</figure>')
    h.append("<p><strong>One step.</strong> Cut the run into equal slices. In each "
             "slice, read the speed at the middle of the slice and multiply by the "
             "width of the slice. That gives one straight move, and its across and up "
             "parts come out as whole numbers of cells.</p>")
    h.append("<p><strong>The height is exact.</strong> The upward speed is 2t, a "
             "straight line. Reading a straight line at the middle of a slice gives "
             "exactly its average over that slice, so every node lands on the curve's "
             "height exactly &mdash; panel B, where the rectangle and the triangle "
             "have the same area.</p>")
    h.append("<p><strong>The sideways part drifts.</strong> The sideways speed is "
             "1 &minus; t&sup2;, which bends. At the middle of the first slice it reads "
             "3/4, while the true average over that slice is 2/3. So the move is 1/12 "
             "too long sideways, in every slice, always the same way &mdash; panel C. "
             "Three slices make 1/4.</p>")
    h.append("<p><strong>The two ends.</strong> The first slice is read at its middle, "
             "t = 1/2, so the chain leaves the nose along the line there rather than "
             "along the line at the nose itself: it starts a hair off the curve. At the "
             "far end the 1/12s have added up, and the chain stops 1/4 short of "
             "&minus;6, while the height is still exactly 9 &mdash; panel D. Nothing "
             "corrects it, because every step is wrong in the same direction.</p>")
    h.append("<p><strong>What that buys.</strong> Every side is a whole number of "
             "cells: 63 across, 16 up, 65 along, and 63&times;63 + 16&times;16 = "
             "65&times;65. A pen or a cutter can walk the path cell by cell and finish "
             "each move on a corner, and the lengths can be added up exactly on paper: "
             "767/64 for one side, against 12 for the curve. Joining points on the "
             "curve instead puts the nodes exactly on it, but every join has a length "
             "like the square root of a number that is not a square, so the total is a "
             "sum of square roots and cannot be added up exactly. That is the steady "
             "advantage: no square roots anywhere in the chain.</p>")

    h.append('<h2>Open questions</h2>')
    h.append('<ul class="note"><li>Is the 1/64 visible in the figure at working size, '
             'and is that acceptable for an ornament line?</li>'
             '<li>Should the chain be snapped so its last vertex sits exactly on '
             '(&minus;6,&nbsp;9)? That breaks the pure midpoint rule.</li></ul>')
    return "\n".join(h)


def main():
    extra = """
main{max-width:1120px}
h2{font-size:21px;margin:30px 0 8px;padding-top:12px;border-top:2px solid var(--ink)}
.tbl{border-collapse:collapse;margin:10px 0 14px;font:13px/1.5 ui-monospace,Menlo,monospace;font-variant-numeric:tabular-nums}
.tbl th,.tbl td{border:1px solid var(--rule);padding:4px 9px;text-align:right;background:var(--paper)}
.tbl th{background:#efe7d2;text-align:right;font-weight:600}
.tbl th:first-child,.tbl td:first-child{text-align:left}
pre.note{background:var(--paper);border:1px solid var(--rule);padding:10px 14px;margin:10px 0 16px}
figure{margin:16px 0} figure img{max-width:100%;border:1px solid var(--rule);background:var(--paper)}
figure figcaption{margin-top:6px}
ul.note{padding-left:20px}
"""
    html = ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<title>T-PH integer hits — sandbox</title><style>"
            + css() + extra +
            "</style></head><body><main>" + build() + "</main></body></html>\n")
    out = HERE / "tph-tri-sandbox.html"
    out.write_text(html)
    print(f"wrote {out}  ({len(html)} bytes)")


if __name__ == "__main__":
    main()
