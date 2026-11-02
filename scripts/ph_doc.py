"""Write docs/PH-INTEGER.md and its HTML twin from one source.

    .venv/bin/python scripts/ph_doc.py

Every number in the text is computed here from `scripts/generators.py`, so the prose
and the arithmetic cannot drift apart.  The HTML twin exists because the same
page is read outside mkdocs; both are generated, neither is hand-edited.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import markdown  # noqa: E402  (mkdocs dependency)

import generators  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT_MD = ROOT / "docs" / "PH-INTEGER.md"
OUT_HTML = ROOT / "docs" / "PH-INTEGER.html"


def preset_rows():
    rows = []
    for spec in generators.PRESETS:
        it = generators.build_preset(spec)
        x0, y0, x1, y1 = it["box"]
        rows.append(
            f"| {spec['key']} | {spec['n']} | "
            f"`h=({','.join(map(str, spec['h']))})` "
            f"`u=({','.join(map(str, spec['u']))})` "
            f"`v=({','.join(map(str, spec['v']))})` | 1/{spec['m']} | "
            f"{it['scale']} | {x1 - x0} × {y1 - y0} |")
    return "\n".join(rows)


def named_rows():
    rows = []
    for spec in generators.NAMED:
        d = generators.named_data(spec)
        if d["exact"]:
            tier = "rational · exact Bézier"
            scale = f"control {d['cscale']}, milestones {d['mscale']}"
        elif spec.get("sampler"):
            tier = spec.get("tier", "not rational · sampled")
            scale = "—"
        else:
            tier = "no real points"
            scale = "—"
        rows.append(f"| {spec['key']} | `{spec['eq']}` | "
                    f"{spec.get('deg_label', spec['deg'])} | "
                    f"{tier} | {scale} |")
    return "\n".join(rows)


def body() -> str:
    return f"""# Integer PH curves: the generator, the grid, and what is actually true

A corrected version of a survey that has been circulating in this project.
Where it agrees with the arithmetic it is kept; where it does not, the number
below was computed, not remembered. Every figure on this page comes from
`scripts/generators.py`, which works in `fractions.Fraction` and asserts that each
coordinate is integral before it writes anything.

## The generator

A planar curve has a *Pythagorean hodograph* when the speed is a polynomial:

```
x'(t)^2 + y'(t)^2 = sigma(t)^2
```

Every such curve is written, with complex polynomials `w = u + iv` and a factor
`h`,

```
z'(t) = h(t) · ( u(t)^2 - v(t)^2 ,  2 u(t) v(t) )
sigma = h(t) · ( u(t)^2 + v(t)^2 )
```

and Farouki and Sakkalis's lemma fixes the degree:

```
n = deg h + 2 · max(deg u, deg v) + 1
```

That identity is the load-bearing one, and the survey omitted it — which is why
its quartics and sextics had no construction. With `h = 1` only odd degrees
appear; the `h` factor is the only way to reach an even degree:

| `deg h` | `max(deg u, deg v)` | degree |
|---|---|---|
| 0 | 1 | 3 |
| 1 | 1 | 4 |
| 0 | 2 | 5 |
| 2 | 1 | 5 |
| 1 | 2 | 6 |

## What comes free

With integer generators, and no approximation anywhere:

- **speed** is the polynomial `h (u² + v²)`;
- **arc length** integrates it exactly, as a polynomial;
- **tangent** is `2·atan(v/u)`, or in integers, Euclid's doubling
  `(u²−v², 2uv) / (u²+v²)`;
- **offset** by a distance `d` is *rational*, not refitted;
- **curvature** is a rational function;
- **splitting** at any `t` keeps the curve PH and keeps the generators integral.

## The integer arithmetic

Control points come from integrating the hodograph, so the cubic divides by 3,
the quartic by 4, the quintic by 5, the sextic by 6 — then a conversion to the
Bernstein basis multiplies by binomials. Milestones at `t = k/m` bring the
Bernstein weights, which carry `m` to the degree. The least integer that clears
both is the scale.

What that means in practice, for four curves built from small numbers:

| curve | n | generators | step | scale | integer grid |
|---|---|---|---|---|---|
{preset_rows()}

Three consequences, and they contradict the folklore.

**The milestone scale is `mⁿ`, and PH never improves it.** A plain Bézier whose
control points are integers already has integer control points at scale 1, and
pays exactly the same `mⁿ` for its milestones. PH *costs* a factor of 3
(cubic) or 15 (quintic) on the control points, because the integration
denominator has to be cleared. What PH buys is exact arc length, rational
offsets and a rational frame — not a smaller lattice.

**Integer milestones always exist.** Any finite set of rational parameters
clears at the lowest common multiple of its denominators. The bean, for
example, has quarter-points with denominators 1, 91, 3, 91 and 1, so a scale of
273 puts every one on the grid. The scale is a fact about the arithmetic, not a
wall.

**What is impossible is the strong claim.** No bounded curve holds infinitely
many lattice points, so "infinitely many points on the curve can be integers"
cannot be true of any curve, PH or not. You get finitely many, at parameters
you choose.

## The numbers that circulate

| claim | what it is | verdict |
|---|---|---|
| cubic, fifths, scale 750 | 375 for `u=(2,1)`, `v=(1,2)` | 2× too high |
| quintic, fifths, 3,125 | `5⁵`, the step term | a floor, not the scale |
| quintic, fifths, 187,500 | `2²·3·5⁶`, one generator set | true of some numbers only |
| quintic, tenths, 3,000,000 | `10⁵ = 100,000` is the step floor | 30× too high |
| "2, 4, 8, 16 at eighths → 128" | a cubic at eighths is at least `3·512` | not reproduced |
| arc length 26 for the worked example | 26 is the unscaled sum; ×3 gives 78 | off by the scale |

None of these are fatal — they are all the same error, which is treating a
number that belongs to *one set of generators* as if it belonged to the degree.

## Degree by degree

- **n = 2** does not exist. There are no quadratic PH curves.
- **n = 3** is the Tschirnhausen cubic, up to scale and rotation: one shape
  only, no inflection, so a C-curve. Loops and cusps are reachable by letting
  the generators cross.
- **n = 4** needs `deg h = 1`. It can inflect, which the cubic cannot.
- **n = 5** is the workhorse: C and S shapes, first-order Hermite interpolation
  with a single segment, and the only low degree that supports C² PH splines.
  The quintic transition curve — straight line to circular arc with monotone
  curvature — is the lowest-degree polynomial that does the clothoid's job.
- **n = 6** takes `deg h = 1` with quadratic generators. This is where the
  multiple-cusp shapes live.

## Named curves

Two of these are nodal cubics, and only one is the PH one. Every cubic PH curve
is a scaled, rotated *Tschirnhausen cubic*, `27ay² = (a−x)(8a+x)²`, whose node
crosses at 60 degrees. The other, `y² = x²(x+1)`, crosses at 90 — same genus,
same degree, reachable from the first only by an affine map, never by a
similarity, because an angle is not affine. A cubic PH curve's control polygon
is what the top of this page has been building; the node angle is how you tell
whether a nodal cubic is that family or merely nearby.

The test that separates these is rationality, and it is decidable: count the
singular points, and check that the gradient vanishes at each. A rational curve
has an exact Bézier — substitute `t = s/(1−s)` and clear denominators. A curve
with a cusp does not, and sampling is the honest fallback.

| curve | equation | degree | tier | integer data |
|---|---|---|---|---|
{named_rows()}

The bean is worth spelling out. In polar form it is `r = cosθ / (1 − ¼sin²2θ)`,
a ratio of polynomials; with `t = tan(θ/2)` and `t = s/(1−s)` it becomes an
exact rational Bézier whose homogeneous control values are whole numbers, and
it reproduces the curve to `10⁻¹⁶`. Its two `W = 0` control values are points at
infinity, which is why there is no control *polygon* to lay on the lattice.

The piriform is the fourth exact one. Its equation is `a⁴y² = b²x³(2a − x)`,
which at `a = b = 1` is `y² = x³(2 − x)`: a rational quartic with a cusp at the
origin, a vertex at `(2, 0)`, and the bounds `0 ≤ x ≤ 2`, `|y| ≤ 3√3/4`.
Through `x = 1 + sin t`, `y = cos t (1 + sin t)`, then `u = tan(t/2)`, the
homogeneous generator is `X = (u+1)²(1+u²)`, `Y = (u+1)²(1−u²)`, `W = (1+u²)²`
— whole numbers, no clearing needed.

Two wrong forms are worth recording, because both look plausible. The quartic
`x⁴ − x²y + y² = 0` is a quadratic in `y` with discriminant `−3x⁴`, so its only
real point is the origin; and `x⁴ + x²y − y² = 0` factorises as
`(y − k₁x²)(y − k₂x²)` with `k = (1 ± √5)/2` — two parabolas, not a pear. Only
the `x³` form is the curve.

## The catenary

A true catenary is `a·cosh(x/a)`: transcendental, so no scale factor can put it
on an integer grid, and the AHPH family keeps the PH property in a hyperbolic
basis — exact arc length, rational offsets — but not integers.

**This is solved, on its own page.** `workbench/catenary.html` builds the
catenary two ways and neither pretends to be a single integer curve:

- **four PH cubics** over the curve, exact at both endpoints and both tangents,
  worst error **0.41 per cent of `a`**;
- an **integer chord walk** where the heading snaps to a rung of the 3-4-5
  ladder and each chord is the hypotenuse of a real triangle, so every node is a
  whole number on the lattice.

That is the answer, and it is recorded in `state/ACHIEVEMENTS.md`. Do not solve
it again.

## What this session measured

Two results, both negative, both worth keeping.

**The discriminant route does not produce a lattice.** It is true that a
segment's closure quadratic has a rational square discriminant exactly when the
fit is exact. But on the full 92-rung pythagorean ladder, for the four catenary
chords, **0 of 17,168** non-negative discriminants are squares; and where one
is, `k` carries a denominator in the thousands, so the control points are
rational, not integral. Choosing the pair buys exactness, not integers.

**The generator route does.** You do not fit through prescribed points and hope;
you choose integers and the endpoint is whatever it is. That is the difference
between `scripts/generators.py` and a least-squares fit.

Along the way `from_pairs` in `scripts/hodograph.py` turned out to rotate by
half the tangent angle, so it only closed when a segment started at zero. It is
fixed and now agrees with `from_hermite` to `10⁻¹⁴`.

## Open

- Whether the named curves should be fitted to a measured reference with a
  stated tolerance, in the manner of `FIDELITY.md`.
- Whether the named curves should be fitted to a measured reference with a
  stated tolerance, in the manner of `FIDELITY.md`.
- Whether `generators` should write straight into the web app's input pages.
"""


CSS = """
:root{--paper:#f4f0e6;--ink:#1d1d18;--muted:#6d685b;--line:#d8d1c1;
--accent:#8c6a21;--code:#fbf9f3;--mono:ui-monospace,"SF Mono",Menlo,monospace}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
font:16px/1.6 Georgia,"Iowan Old Style",serif}
main{max-width:760px;margin:0 auto;padding:48px 26px 90px}
h1{font-size:31px;line-height:1.2;margin:0 0 10px;font-weight:600}
h2{font-size:20px;margin:38px 0 10px;font-weight:600;
border-bottom:1px solid var(--line);padding-bottom:6px}
p{margin:0 0 14px}
code{font:13px/1.45 var(--mono);background:var(--code);
padding:1px 5px;border-radius:3px}
pre{background:var(--code);border:1px solid var(--line);padding:12px 14px;
overflow-x:auto;margin:0 0 16px}
pre code{background:none;padding:0;font-size:12.5px;line-height:1.5}
table{border-collapse:collapse;width:100%;margin:0 0 18px;font-size:13.5px}
th,td{border-bottom:1px solid var(--line);padding:6px 9px;text-align:left;
vertical-align:top}
th{font:600 11px/1.3 var(--mono);letter-spacing:.06em;text-transform:uppercase;
color:var(--muted)}
ul,ol{margin:0 0 16px;padding-left:22px}
li{margin:0 0 7px}
strong{font-weight:600}
hr{border:0;border-top:1px solid var(--line);margin:30px 0}
"""


def main() -> int:
    md = body()
    OUT_MD.write_text(md, encoding="utf-8")
    html_body = markdown.markdown(
        md, extensions=["tables", "fenced_code", "attr_list", "toc"])
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Integer PH curves · curve-lab</title>
<style>{CSS}</style>
</head>
<body><main>
<p style="font:600 11px/1.3 var(--mono);letter-spacing:.08em;
text-transform:uppercase;color:var(--muted);margin:0 0 14px">
curve-lab · generated by scripts/ph_doc.py · do not edit</p>
{html_body}
</main></body></html>
"""
    OUT_HTML.write_text(page, encoding="utf-8")
    print(OUT_MD)
    print(OUT_HTML)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
