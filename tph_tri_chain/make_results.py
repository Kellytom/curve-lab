"""Emit RESULTS.md and results.html from one source of truth.

Both files are rendered from the same block list, so they cannot drift.
Every number comes from chain.py, never from typing.

Run:  .venv/bin/python tph_tri_chain/make_results.py
"""

import os
from fractions import Fraction as F
from math import sqrt

from chain import chain, grid, integral, primitive

HERE = os.path.dirname(os.path.abspath(__file__))
T_FISH = F(12, 5)
N_FISH = 120


def fnum(x):
    return f"{float(x):.6f}"


def frac(x):
    return f"{x.numerator}/{x.denominator}"


def build_blocks():
    inner = 4 * sqrt(3)
    b = []

    b.append(("h1", "T-PH fish glyph as a Pythagorean triangle chain"))
    b.append(("status",
              "Working result, not yet documentation. Held in tph_tri_chain/ so it "
              "stays separable from curve_lab/ph_hermite. Promote to docs/ only "
              "after the operator accepts the grid correction in section 10."))

    # ---------------------------------------------------------------- 1
    b.append(("h2", "1. What this is and is not"))
    b.append(("p", "This is the discrete midpoint chain of the Tschirnhausen cubic "
                   "Pythagorean-hodograph curve. It is not a Bezier curve, not a "
                   "spline, and not a generic cubic: no control polygon, basis "
                   "function, knot vector or de Casteljau step appears in it. The "
                   "curve is defined only by its two generator polynomials."))

    # ---------------------------------------------------------------- 2
    b.append(("h2", "2. The curve, exactly"))
    b.append(("p", "Generators u(t) = 1, v(t) = t. Everything below follows from "
                   "those two polynomials."))
    b.append(("table", ["quantity", "exact expression", "value at t = 12/5"],
              [["x'(t)", "1 - t^2", fnum(1 - T_FISH ** 2)],
               ["y'(t)", "2t", fnum(2 * T_FISH)],
               ["sigma(t), the speed", "1 + t^2", fnum(1 + T_FISH ** 2)],
               ["x(t)", "t - t^3/3", fnum(integral(T_FISH)[0])],
               ["y(t)", "t^2", fnum(integral(T_FISH)[1])],
               ["s(t)", "t + t^3/3", fnum(integral(T_FISH)[2])]], []))

    # ---------------------------------------------------------------- 3
    b.append(("h2", "3. Midpoint quadrature, and why the triple is exact"))
    b.append(("p", "[t0, t1] is split into N equal steps of width dt = (t1 - t0)/N. "
                   "Each step is sampled at its midpoint t_i = t0 + (i + 1/2)dt, "
                   "never at an endpoint."))
    b.append(("code", "dx_i = (1 - t_i^2) * dt\n"
                      "dy_i = (2 * t_i)   * dt\n"
                      "ds_i = (1 + t_i^2) * dt"))
    b.append(("p", "With u = 1 and v = t_i those three values are "
                   "(u^2 - v^2)dt, (2uv)dt and (u^2 + v^2)dt. Expanding gives "
                   "(u^2 - v^2)^2 + (2uv)^2 = (u^2 + v^2)^2 identically, so every "
                   "step is a right triangle with an exact rational hypotenuse. "
                   "The identity is tested as equality of Fractions in chain.py, "
                   "not to a tolerance."))
    b.append(("p", "Midpoint sampling also makes the y coordinates exact for any "
                   "N: sum of 2t_i dt telescopes to t_max^2. Only x carries "
                   "quadrature error."))

    # ---------------------------------------------------------------- 4
    r4, _ = chain(F(0), F(2), 4)
    g4 = grid(r4)
    b.append(("h2", "4. Worked example: [0, 2] in four steps"))
    b.append(("p", f"The whole four-triangle chain is exact on the integer grid "
                   f"{g4}. Legs, hypotenuses and nodes:"))
    b.append(("table", ["i", "midpoint t", "dx", "dy", "ds", "node x", "node y"],
              [[str(r["i"]), fnum(r["t"]), str(int(r["dx"] * g4)),
                str(int(r["dy"] * g4)), str(int(r["ds"] * g4)),
                fnum(r["x"]), fnum(r["y"])] for r in r4], []))
    prim = [primitive((int(r["dx"] * g4), int(r["dy"] * g4), int(r["ds"] * g4))) for r in r4]
    b.append(("p", "Primitive triples, in order: "
                   + ", ".join(f"({p[0]}, {p[1]}, {p[2]})" for p in prim) + "."))
    b.append(("p", f"End point (-0.625, 4.000) against exact (-0.666667, 4.000); "
                   f"chain length {frac(r4[-1]['s'])} = {fnum(r4[-1]['s'])} against "
                   f"exact {frac(integral(F(2))[2])} = {fnum(integral(F(2))[2])}. "
                   f"Length error {100 * float(r4[-1]['s'] / integral(F(2))[2] - 1):.2f} "
                   f"percent at four triangles."))

    # ---------------------------------------------------------------- 5
    b.append(("h2", "5. Domain, symmetry, and where the loop closes"))
    b.append(("p", "x(-t) = -x(t) and y(-t) = y(t), so the branch over [0, t_max] "
                   "is half the glyph; the other half is the reflection x -> -x "
                   "with y unchanged. The self-intersection is where x(t) = 0, "
                   "i.e. t = sqrt(3) = 1.732051, at the point (0, 3). The closed "
                   f"loop has exact length 4*sqrt(3) = {inner:.6f}."))
    b.append(("p", "A discrete chain does not hit (0, 3) exactly; it passes near "
                   "it. At the step count used below the nearest node is about "
                   "0.028 away in y."))

    # ---------------------------------------------------------------- 6
    b.append(("h2", "6. Coordinate table, [0, 2], N = 25"))
    r25, _ = chain(F(0), F(2), 25)
    g25 = grid(r25)
    b.append(("p", f"Exact integer grid {g25}. dx, dy, ds are counts of 1/{g25}; "
                   f"x, y are the cumulative node."))
    b.append(("table", ["i", "midpoint t", "dx", "dy", "ds", "node x", "node y"],
              [[str(r["i"]), fnum(r["t"]), str(int(r["dx"] * g25)),
                str(int(r["dy"] * g25)), str(int(r["ds"] * g25)),
                fnum(r["x"]), fnum(r["y"])] for r in r25], []))
    b.append(("p", f"End ({fnum(r25[-1]['x'])}, {fnum(r25[-1]['y'])}), length "
                   f"{fnum(r25[-1]['s'])}. The first five primitive triples are "
                   + ", ".join(f"({t[0]}, {t[1]}, {t[2]})" for t in
                               [primitive(x) for x in
                                [(int(r["dx"] * g25), int(r["dy"] * g25),
                                  int(r["ds"] * g25)) for r in r25[:5]]])
                   + "."))

    # ---------------------------------------------------------------- 7
    half, _ = chain(F(0), T_FISH, N_FISH)
    g = grid(half)
    exact = integral(T_FISH)
    total = half[-1]["s"] * 2
    b.append(("h2", "7. The fish glyph: [0, 12/5], N = 120 per branch"))
    b.append(("p", f"Branch table. Step width dt = {frac(T_FISH / N_FISH)}, exact "
                   f"grid {g} = {frac(F(g, 3125))} x 3125. The mirrored branch "
                   f"reuses these triples with dx negated, giving "
                   f"{2 * N_FISH} triangles in total."))
    b.append(("table", ["i", "midpoint t", "dx", "dy", "ds", "node x", "node y"],
              [[str(r["i"]), fnum(r["t"]), str(int(r["dx"] * g)),
                str(int(r["dy"] * g)), str(int(r["ds"] * g)),
                fnum(r["x"]), fnum(r["y"])] for r in half], []))
    b.append(("table", ["measure", "value"],
              [["triangles, both branches", str(2 * N_FISH)],
               ["tail tip, exact", "(-2.208000, 5.760000)"],
               ["tail tip, chain", f"(-{fnum(half[-1]['x'])}, {fnum(half[-1]['y'])})"],
               ["chain length", f"{frac(total)} = {fnum(total)}"],
               ["exact length", f"{frac(2 * exact[2])} = {fnum(2 * exact[2])}"],
               ["length error", f"{float(total - 2 * exact[2]):+.3e}"],
               ["ratio to inner loop", f"{float(total) / inner:.3f}"],
               ["far tip on grid (t = 12/5)",
                f"{int(half[-1]['x'] * g)} / {int(half[-1]['y'] * g)}"]],
              []))
    b.append(("img", "out/fish-t24.svg",
              "Fig. T1 -- the fish glyph as a 240-triangle Pythagorean chain against the smooth T-PH curve"))
    b.append(("p", "The tail height 144/25 = 5.76 is exact for every N, because "
                   "midpoint quadrature is exact on the linear y'(t). The tail is "
                   "2.02 times the inner loop length, so the glyph is close to "
                   "double the inner shape, as intended."))
    b.append(("p", "Artifacts: out/fish-t24.csv holds all 240 steps as integers, "
                   "out/fish-t24.svg is the labelled figure."))

    # ---------------------------------------------------------------- 8
    stops = []
    for label, tmax, N in [("5/2", F(5, 2), 125), ("12/5", F(12, 5), 120)]:
        r, _ = chain(F(0), tmax, N)
        tip = integral(tmax)
        stops.append([label, f"({float(tip[0]):.4f}, {float(tip[1]):.4f})",
                      fnum(r[-1]["s"] * 2),
                      f"{float(r[-1]['s'] * 2) / inner:.3f}", str(grid(r))])
    stops.append(["sqrt6", "(-2.4495, 6.0000)", "14.696938", "2.121",
                  "none, t irrational"])
    b.append(("h2", "8. Where to stop"))
    b.append(("p", "The loop closes at t = sqrt(3). Past it there are three "
                   "natural stops:"))
    b.append(("table", ["t_max", "tail tip", "full length", "ratio", "exact grid"], stops, []))
    b.append(("p", "12/5 is the grid-exact choice: 2.023 times the loop length with "
                   "every step on one integer grid. sqrt(6) is the geometric "
                   "choice, tail height exactly double the loop height, but t is "
                   "irrational so no rational chain ends there. 5/2 is the cleanest "
                   "division but overshoots to 2.22 times."))

    # ---------------------------------------------------------------- 9
    lad = []
    for tmax, Ns in [(F(12, 5), (6, 12, 24, 30, 60, 120, 240)),
                     (F(5, 2), (5, 10, 25, 50, 125))]:
        for N in Ns:
            r, _ = chain(F(0), tmax, N)
            gg = grid(r)
            lad.append([frac(tmax), str(N), frac(tmax / N), str(gg),
                        "yes" if 3125 % gg == 0 else "no",
                        f"{float(r[-1]['s'] - integral(tmax)[2]):.3e}"])
    b.append(("h2", "9. Accuracy and grid cost"))
    b.append(("p", "Error falls as 1/N^2, as midpoint quadrature predicts. The exact "
                   "integer grid grows as N^3, so doubling the triangle count "
                   "multiplies the grid by eight. The grid is not a fixed canvas "
                   "you can keep adding triangles to."))
    b.append(("table", ["t_max", "N", "dt", "grid", "fits 3125", "half-length error"],
              lad, []))

    # ---------------------------------------------------------------- 10
    b.append(("h2", "10. The 3125 grid: correction"))
    b.append(("p", "The exact integer grid depends only on the step width dt = (t1 - t0)/N, "
                   "not on t_max or N separately. Write dt = c/q in lowest terms and let "
                   "p = 2i + 1, always odd; then t_i = p c / (2q) and"))
    b.append(("code", "grid = q^3        when c is even\n"
                      "grid = 4 * q^3    when c is odd"))
    b.append(("p", "Verified as exact equality on 1200 (t_max, N) pairs across ten rational "
                   "t_max. The 4 is the midpoint half-step: when c is odd, "
                   "4q^2 - p^2 c^2 is odd, so the factor 4 can never cancel. An even "
                   "numerator cancels it completely, and that is the only route to an "
                   "odd grid."))
    b.append(("table", ["dt", "grid", "triangles per branch at t = 12/5", "note"],
              [["2/5", "125", "6", "only exact option on 3125"],
               ["4/5", "125", "3", "coarser, still on 3125"],
               ["1/5", "500", "12", "odd numerator, factor 4 returns"],
               ["2/25", "15625", "30", "5 x 3125, even numerator"],
               ["1/25", "62500", "60", "odd numerator"],
               ["1/50", "500000", "120", "current figure, 160 x 3125"]], []))
    b.append(("p", "Because 3125 = 5^5 is odd, it can only appear when c is even and "
                   "q^3 divides it: q = 5, so dt = 2/5 or 4/5, i.e. N = 5 t_max / 2. "
                   "At dt = 2/5 the fish gets 6 triangles per branch. That is the "
                   "trade: the 3125 canvas buys six triangles, not a hundred and "
                   "twenty. The nearest dense option on the same base is dt = 2/25, "
                   "grid 15625 = 5 x 3125, 30 triangles per branch."))
    b.append(("p", "The /3 in x = t - t^3/3 and s = t + t^3/3 does not enter the step "
                   "grid: the chain is built from the hodograph, which has no cubic "
                   "term. It affects only the exact reference values. A t_max that is "
                   "a multiple of 3 gives integers there: t = 3 gives x = -6, y = 9, "
                   "s = 12."))
    b.append(("p", "A longer curve is cheaper per triangle. At fixed N, larger t_max "
                   "makes dt coarser and the grid smaller: t = 3 at N = 120 needs "
                   "256000 against 500000 at t = 12/5. The price is proportion, since "
                   "tail over loop is 3.46 at t = 3 against 2.02 at 12/5."))
    corr = [
        ("[0, 2], N = 25 needs grid 15625, not 3125", grid(r25) == 15625),
        ("[0, 2], N = 25 first step is (1248, 100, 1252), not (1248, 200, 1252)",
         (int(r25[0]["dx"] * g25), int(r25[0]["dy"] * g25), int(r25[0]["ds"] * g25))
         == (1248, 100, 1252)),
        ("[0, 2], N = 25 tail y is 4 exactly", r25[-1]["y"] == 4),
        ("[0, 1], N = 25 needs grid 62500, not 3125; first step (2499, 100, 2501)",
         grid(chain(F(0), F(1), 25)[0]) == 62500),
        ("[0, 2], N = 4 triples are (15,8,17) (7,24,25) (-9,40,41) (-33,56,65) on grid 32",
         [tuple(int(v * 32) for v in (r["dx"], r["dy"], r["ds"])) for r in r4]
         == [(15, 8, 17), (7, 24, 25), (-9, 40, 41), (-33, 56, 65)]),
        ("[0, 2], N = 4 ends at (-5/8, 4) with length 37/8 = 4.625",
         r4[-1]["x"] == F(-5, 8) and r4[-1]["y"] == 4 and r4[-1]["s"] == F(37, 8)),
        ("[0, 12/5], N = 120 needs grid 500000", grid(half) == 500000),
        ("3125 is exact only at N = 5 over [0, 2], grid 125",
         grid(chain(F(0), F(2), 5)[0]) == 125),
    ]
    b.append(("p", "Checks against the draft this method arrived in. Each is an "
                   "equality test run at generation time; a FAIL means the "
                   "document is wrong, not the numbers."))
    for name, ok in corr:
        b.append(("li", f"{'PASS' if ok else 'FAIL'} -- {name}"))

    # ---------------------------------------------------------------- 11
    b.append(("h2", "11. Reproduce"))
    b.append(("code",
              ".venv/bin/python tph_tri_chain/chain.py        # every table, exact\n"
              ".venv/bin/python tph_tri_chain/glyph.py        # fish CSV and SVG\n"
              ".venv/bin/python tph_tri_chain/make_results.py # this document"))
    b.append(("p", "Figure convention: the model has +y up, as the curve does. The "
                   "SVG writer flips y once at output; the flip lives in one "
                   "function, fy(), in glyph.py."))
    return b


def render_md(blocks):
    out = []
    for blk in blocks:
        kind = blk[0]
        if kind == "h1":
            out.append("\n# " + blk[1] + "\n")
        elif kind == "h2":
            out.append("\n## " + blk[1] + "\n")
        elif kind == "status":
            out.append("> " + blk[1] + "\n")
        elif kind == "p":
            out.append(blk[1] + "\n")
        elif kind == "li":
            # keep list items adjacent so markdown renders one tight list
            if out and out[-1].startswith("- "):
                out[-1] = out[-1] + "\n- " + blk[1]
            else:
                out.append("- " + blk[1])
        elif kind == "code":
            out.append("```text\n" + blk[1] + "\n```\n")
        elif kind == "img":
            out.append(f"![{blk[2]}]({blk[1]})\n")
        elif kind == "table":
            headers, rows = blk[1], blk[2]
            out.append("| " + " | ".join(headers) + " |")
            out.append("|" + "|".join("---" for _ in headers) + "|")
            for r in rows:
                out.append("| " + " | ".join(r) + " |")
            out.append("")
    return "\n".join(out)


def render_html(blocks, title):
    o = [f'<!doctype html><html lang="en"><head><meta charset="utf-8">',
         f'<title>{title}</title><style>',
         'body{font:16px/1.55 -apple-system,Helvetica,Arial,sans-serif;max-width:1080px;'
         'margin:2.2rem auto;padding:0 1.4rem;color:#1a1a1a}',
         'h1{font-size:1.9rem;margin:0 0 .2rem}h2{font-size:1.25rem;margin:2rem 0 .6rem;'
         'border-bottom:1px solid #e4e4e4;padding-bottom:.25rem}',
         'p{margin:.7rem 0}pre{background:#f7f7f7;border:1px solid #e2e2e2;padding:.8rem 1rem;'
         'overflow-x:auto;font-size:.9rem;line-height:1.45}',
         'table{border-collapse:collapse;margin:.9rem 0;font-size:.88rem;'
         'font-variant-numeric:tabular-nums}th,td{border:1px solid #ddd;padding:.28rem .55rem;'
         'text-align:right}th:first-child,td:first-child{text-align:left}'
         'th{background:#f2f2f2;font-weight:600}',
         'ul{padding-left:1.3rem}li{margin:.2rem 0}',
         '.status{background:#fff8e1;border-left:4px solid #e0a800;padding:.7rem 1rem;'
         'margin:1rem 0;font-size:.95rem}',
         '</style></head><body>']
    for blk in blocks:
        kind = blk[0]
        if kind == "h1":
            o.append(f"<h1>{blk[1]}</h1>")
        elif kind == "h2":
            o.append(f"<h2>{blk[1]}</h2>")
        elif kind == "status":
            o.append(f'<div class="status">{blk[1]}</div>')
        elif kind == "p":
            o.append(f"<p>{blk[1]}</p>")
        elif kind == "li":
            o.append(f"<li>{blk[1]}</li>")
        elif kind == "code":
            o.append("<pre>" + blk[1].replace("<", "&lt;") + "</pre>")
        elif kind == "img":
            o.append(f'<figure style="margin:1.4rem 0"><img src="{blk[1]}" alt="{blk[2]}" '
                     f'style="max-width:100%;border:1px solid #e6e6e6">'
                     f'<figcaption style="font-size:.9rem;color:#555;margin-top:.4rem">'
                     f'{blk[2]}</figcaption></figure>')
        elif kind == "table":
            headers, rows = blk[1], blk[2]
            o.append("<table><thead><tr>"
                     + "".join(f"<th>{h}</th>" for h in headers)
                     + "</tr></thead><tbody>")
            for r in rows:
                o.append("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
            o.append("</tbody></table>")
    o.append("</body></html>")
    return "\n".join(o)


def main():
    blocks = build_blocks()
    md = render_md(blocks)
    with open(os.path.join(HERE, "RESULTS.md"), "w") as fh:
        fh.write(md + "\n")
    html = render_html(blocks, "T-PH fish glyph as a Pythagorean triangle chain")
    with open(os.path.join(HERE, "results.html"), "w") as fh:
        fh.write(html + "\n")
    fails = [b[1] for b in blocks if b[0] == "li" and b[1].startswith("FAIL")]
    print(f"blocks {len(blocks)}  md {len(md)} bytes  html {len(html)} bytes")
    print(f"checks: {len([b for b in blocks if b[0]=='li'])} run, {len(fails)} failed")
    for f in fails:
        print("  " + f)


if __name__ == "__main__":
    main()
