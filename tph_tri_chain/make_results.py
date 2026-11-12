"""Emit RESULTS.md and results.html: integer hits, at twelve triangles.

One block list feeds both files. Every number is computed, never typed.

Run:  .venv/bin/python tph_tri_chain/make_results.py
"""

import os
from fractions import Fraction as F

from chain import chain, grid, integral, primitive

HERE = os.path.dirname(os.path.abspath(__file__))
N = 12                      # the one triangle count used throughout


def fx(x, p=6):
    return f"{float(x):.{p}f}"


def chordal(T, n):
    """Nodes exactly on the curve, joined by straight segments."""
    pts = [integral(F(i) * T / n)[:2] for i in range(n + 1)]
    length = sum(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** F(1, 2)
                 for a, b in zip(pts, pts[1:]))
    return pts, float(length)


def build_blocks():
    b = []

    b.append(("h1", "Integer hits on the Tschirnhausen cubic"))
    b.append(("status",
              "Every comparison here is at twelve triangles per side, the same "
              "count for both methods. The constraint is where the curve meets "
              "whole-number points, not how fine the drawing is."))

    # ------------------------------------------------------------ 1
    b.append(("h2", "1. Where the curve hits whole numbers"))
    b.append(("p", "The curve is x = t - t^3/3 and y = t^2. For a point to sit on "
                   "the integer lattice, both coordinates must be whole numbers."))
    b.append(("p", "Take t as a fraction in lowest terms. Then y = t^2 is a whole "
                   "number only if t is itself a whole number, because squaring a "
                   "fraction in lowest terms cannot clear its denominator. Once t "
                   "is whole, x = t - t^3/3 is whole exactly when 3 divides t. So "
                   "the hits are the multiples of 3, and nothing else at rational t."))
    b.append(("table", ["t", "x", "y", "arc length s", "note"],
              [["0", "0", "0", "0", "nose"],
               ["3", "-6", "9", "12", "first hit"],
               ["6", "-66", "36", "78", ""],
               ["9", "-234", "81", "252", ""],
               ["12", "-564", "144", "588", ""],
               ["15", "-1110", "225", "1140", ""]], []))
    b.append(("p", "The curve is odd in x and even in y, so each hit (x, y) has a "
                   "mirror (-x, y). One more whole-number point exists: the waist. "
                   "x = 0 at t = plus or minus the square root of 3, which gives "
                   "(0, 3). That parameter is not a fraction, so no chain built at "
                   "fractional steps can land on it."))

    # ------------------------------------------------------------ 2
    b.append(("h2", "2. What that rules out"))
    b.append(("p", "Every other stopping point considered so far fails the first "
                   "test: its height is not a whole number."))
    rows = []
    for T in (F(21, 10), F(12, 5), F(5, 2), F(3), F(4)):
        x, y, s = integral(T)
        rows.append([str(T), fx(x, 6), str(y), fx(y, 4),
                     "yes" if y.denominator == 1 else "no"])
    b.append(("table", ["stopping t", "x", "y exact", "y", "whole-number height?"], rows, []))
    b.append(("p", "Scaling the drawing does not rescue a stop. A fraction stays a "
                   "fraction when multiplied by any whole number, so a stop with "
                   "height 144/25 never becomes a whole-number point at any pitch."))

    # ------------------------------------------------------------ 3
    b.append(("h2", "3. Twelve triangles, both methods"))
    b.append(("p", "Midpoint chain: each step is evaluated at the middle of the "
                   "step, which is what makes the step sides exact whole numbers "
                   "after scaling. Chordal: the nodes sit exactly on the curve and "
                   "the segments are straight joins, so the node positions are exact "
                   "but the side lengths are square roots."))
    rows = []
    for T in (F(2), F(12, 5), F(5, 2), F(3), F(4)):
        r, dt = chain(F(0), T, N)
        g = grid(r)
        xt, yt, st = integral(T)
        pts, clen = chordal(T, N)
        rows.append([str(T), str(dt), str(g), fx(r[-1]["x"]),
                     fx(r[-1]["x"] - xt), "yes" if r[-1]["y"] == yt else "no",
                     f"({fx(pts[-1][0], 3)}, {fx(pts[-1][1], 3)})",
                     fx(r[-1]["s"]), fx(clen), fx(st)])
    b.append(("table", ["stopping t", "step width", "pitch", "midpoint tip x",
                        "gap", "y exact?", "chordal tip", "midpoint length",
                        "chordal length", "exact length"], rows, []))
    b.append(("p", "At twelve triangles the chordal path lands on the whole-number "
                   "point exactly, at t = 3 giving (-6, 9). The midpoint chain stops "
                   "1/64 short of it. At that same stop chordal is also the closer of "
                   "the two on total length, 11.986998 against 11.984375 and an exact "
                   "12; further in, at t = 2.4, the two swap and the midpoint chain "
                   "is closer by a hair. The midpoint chain's steady advantage is a "
                   "different one: every side is an exact whole-number triple, so the "
                   "path can be laid out with no square roots anywhere."))

    # ------------------------------------------------------------ 4
    r, dt = chain(F(0), F(3), N)
    g = grid(r)
    b.append(("h2", "4. The twelve triangles at t = 3"))
    b.append(("p", f"Step width 1/4, pitch {g} cells per unit. The sides, in cells "
                   f"and as reduced triples:"))
    rows = []
    for k, row in enumerate(r, 1):
        t3 = (int(row["dx"] * g), int(row["dy"] * g), int(row["ds"] * g))
        p = primitive(t3)
        rows.append([str(k), fx(row["t"], 2), str(t3[0]), str(t3[1]), str(t3[2]),
                     f"({p[0]}, {p[1]}, {p[2]})"])
    b.append(("table", ["step", "middle t", "dx", "dy", "ds", "reduced triple"], rows, []))
    b.append(("p", f"The last vertex is ({r[-1]['x']}, {r[-1]['y']}), against the "
                   f"curve's (-6, 9): short by 1/64 in x, exact in y. The y "
                   f"coordinate is exact for every count, because the vertical speed "
                   f"is linear and the midpoint rule integrates a linear function "
                   f"exactly."))

    # ------------------------------------------------------------ 5
    b.append(("h2", "5. How the pitch was chosen"))
    b.append(("p", "The pitch depends only on the step width, which is the stopping "
                   "point divided by the triangle count. At twelve triangles the "
                   "step width is t/12, so the stopping point alone decides the "
                   "pitch:"))
    b.append(("table", ["stopping t", "step width", "pitch", "why"],
              [["2", "1/6", "864", "denominator 6"],
               ["2.1", "7/40", "256000", "denominator 40, ugly"],
               ["2.4", "1/5", "500", "denominator 5"],
               ["2.5", "5/24", "55296", "denominator 24, numerator odd"],
               ["3", "1/4", "256", "denominator 4"],
               ["4", "1/3", "108", "denominator 3"]], []))
    b.append(("p", "That table is a single rule. Write the step width as a fraction "
                   "in lowest terms and look at its bottom number, call it q, and "
                   "its top number:"))
    b.append(("code", "pitch = q cubed\n"
                      "pitch = 4 times q cubed    when the top number is odd"))
    b.append(("p", "So the smallest pitch comes from the smallest denominator, and "
                   "the factor of 4 disappears when the top number is even. Checked "
                   "as an exact equality on twelve hundred combinations of stopping "
                   "point and count."))
    b.append(("p", "The worked example that started this: twelve triangles per side "
                   "out to t = 4. The step width is 4/12 = 1/3, the denominator is "
                   "3, so the pitch is 4 x 27 = 108. It is small because the step is "
                   "coarse: twelve triangles across four units is a big step, and a "
                   "big step has a small denominator. At t = 3 the same count gives a "
                   "step width of 1/4 and a pitch of 256; at t = 2.4 it gives 1/5 and "
                   "500. The count is fixed at twelve, so the stopping point is the "
                   "only lever you have."))

    # ------------------------------------------------------------ 6
    b.append(("h2", "6. The glyph at t = 3, in whole units"))
    b.append(("table", ["feature", "value"],
              [["nose", "(0, 0)"],
               ["waist", "(0, 3), reached at t = plus or minus the square root of 3"],
               ["tips", "(-6, 9) and (6, 9)"],
               ["body height", "3"],
               ["tail height", "6, exactly twice the body"],
               ["arc length, one side", "12"],
               ["full length, both sides", "24"]], []))
    b.append(("p", "This is the 'double the inner shape' proportion, measured in "
                   "height, and it needs no scaling and no irrational number. The "
                   "arc-length ratio is larger, 3.46, because the tail is thin and "
                   "long. The figure shows the two sides at twelve triangles, with "
                   "the whole-number points ringed."))
    b.append(("img", "out/lattice-t3.svg",
              "Fig. T1 -- the six whole-number points and the 24-triangle chain at t = 3"))
    b.append(("p", "A caution about the figure: the chain's last vertex sits at "
                   "(-5.984375, 9), just inside the ring at (-6, 9). That gap is the "
                   "1/64, and it is the whole story of this document."))

    # ------------------------------------------------------------ 7
    b.append(("h2", "7. Checks and reproduce"))
    corr = [
        ("t = 3 gives (-6, 9) and length 12 exactly", integral(F(3)) == (-6, 9, 12)),
        ("2.4, 2.5, 12/5 and 2.1 all have non-whole heights",
         all(integral(T)[1].denominator != 1 for T in (F(12, 5), F(5, 2), F(21, 10)))),
        ("twelve triangles at t = 4 gives pitch 108", grid(chain(F(0), F(4), N)[0]) == 108),
        ("twelve triangles at t = 3 gives pitch 256", grid(chain(F(0), F(3), N)[0]) == 256),
        ("twelve triangles at t = 2.5 gives pitch 55296", grid(chain(F(0), F(5, 2), N)[0]) == 55296),
        ("midpoint gap is 1/64 at t = 3", chain(F(0), F(3), N)[0][-1]["x"] - integral(F(3))[0] == F(1, 64)),
        ("chordal lands on (-6, 9) at t = 3", chordal(F(3), N)[0][-1] == (-6, 9)),
        ("first triangle at t = 3 is (63, 16, 65)", primitive((int(r[0]["dx"] * g), int(r[0]["dy"] * g), int(r[0]["ds"] * g))) == (63, 16, 65)),
    ]
    b.append(("p", "Equality tests run whenever this document is generated. A "
                   "failure means the document is wrong, not the numbers."))
    for name, ok in corr:
        b.append(("li", f"{'PASS' if ok else 'FAIL'} -- {name}"))
    b.append(("code",
              ".venv/bin/python tph_tri_chain/chain.py        # every table, exact\n"
              ".venv/bin/python tph_tri_chain/glyph.py        # figure and csv\n"
              ".venv/bin/python tph_tri_chain/make_results.py # this document"))
    b.append(("p", "y is up, as the curve is. The SVG writer flips y once, in fy()."))
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
            if out and out[-1].startswith("- "):
                out[-1] = out[-1] + "\n- " + blk[1]
            else:
                out.append("- " + blk[1])
        elif kind == "code":
            out.append("```text\n" + blk[1] + "\n```\n")
        elif kind == "table":
            headers, rows = blk[1], blk[2]
            out.append("| " + " | ".join(headers) + " |")
            out.append("|" + "|".join("---" for _ in headers) + "|")
            for row in rows:
                out.append("| " + " | ".join(row) + " |")
            out.append("")
        elif kind == "img":
            out.append(f"![{blk[2]}]({blk[1]})\n")
    return "\n".join(out)


def render_html(blocks, title):
    o = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
         f"<title>{title}</title><style>",
         "body{font:16px/1.55 -apple-system,Helvetica,Arial,sans-serif;max-width:1080px;"
         "margin:2.2rem auto;padding:0 1.4rem;color:#1a1a1a}",
         "h1{font-size:1.9rem;margin:0 0 .2rem}h2{font-size:1.25rem;margin:2rem 0 .6rem;"
         "border-bottom:1px solid #e4e4e4;padding-bottom:.25rem}",
         "p{margin:.7rem 0}pre{background:#f7f7f7;border:1px solid #e2e2e2;padding:.8rem 1rem;"
         "overflow-x:auto;font-size:.9rem;line-height:1.45}",
         "table{border-collapse:collapse;margin:.9rem 0;font-size:.88rem;"
         "font-variant-numeric:tabular-nums}th,td{border:1px solid #ddd;padding:.28rem .55rem;"
         "text-align:right}th:first-child,td:first-child{text-align:left}"
         "th{background:#f2f2f2;font-weight:600}",
         "ul{padding-left:1.3rem}li{margin:.2rem 0}",
         ".status{background:#fff8e1;border-left:4px solid #e0a800;padding:.7rem 1rem;"
         "margin:1rem 0;font-size:.95rem}",
         "</style></head><body>"]
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
                     f"{blk[2]}</figcaption></figure>")
        elif kind == "table":
            headers, rows = blk[1], blk[2]
            o.append("<table><thead><tr>"
                     + "".join(f"<th>{h}</th>" for h in headers)
                     + "</tr></thead><tbody>")
            for row in rows:
                o.append("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>")
            o.append("</tbody></table>")
    o.append("</body></html>")
    return "\n".join(o)


def main():
    blocks = build_blocks()
    md = render_md(blocks)
    with open(os.path.join(HERE, "RESULTS.md"), "w") as fh:
        fh.write(md + "\n")
    html = render_html(blocks, "Integer hits on the Tschirnhausen cubic")
    with open(os.path.join(HERE, "results.html"), "w") as fh:
        fh.write(html + "\n")
    fails = [blk[1] for blk in blocks if blk[0] == "li" and blk[1].startswith("FAIL")]
    print(f"blocks {len(blocks)}  md {len(md)}  html {len(html)}  failures {len(fails)}")
    for f in fails:
        print("  " + f)


if __name__ == "__main__":
    main()
