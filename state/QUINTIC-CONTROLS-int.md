# QUINTIC-CONTROLS-int — the known six-point setups, and which ones `quintic-guides.ts` uses

Reference note, 2026-11-26. Answers one question the operator asked: "are there not already known
many control point setups to make the standard quintic curves?" Yes. This file records which ones
are exact, which are only approximations, and which the 100 guide curves actually use.

## 1. Polynomial curves are exact, by degree elevation

Any curve that is a polynomial of degree ≤ 5 in `t` **is** a quintic Bézier, exactly, with six
control points. The controls come from degree elevation, whose coefficients are binomial ratios:

```
        Σ_j  q_j · C(m, j) · C(5 − m, i − j)
p_i  =  ───────────────────────────────────────        m = the curve's degree, i = 0…5
                    C(5, i)
```

So a line (m = 1), a parabola (m = 2), a cubic S (m = 3), a quartic (m = 4) and a quintic (m = 5)
each have a unique six-point Bézier. Nothing has to be fitted or approximated.

**Checked, not assumed.** `q6-parabola-01` stores `y = (0, 36, 54, 54, 36, 0)` with
`x = (0, 24, 48, 72, 96, 120)`. The 2→5 elevation of `y = 4A·t(1 − t)` with `A = 45` gives exactly
`(0, 36, 54, 54, 36, 0)`, and the file's fit error is `0.000`. The script's least-squares fit
recovers the elevation rather than inventing a different curve, because the exact answer is unique.

Families in `workbench/quintic-guides.json` that are exact this way: **parabola, bowl, s-curve,
cusp, flattened-arch, rise** — six of the ten.

## 2. Conics are exact only with weights

A circle, ellipse and hyperbola are **not** polynomials. As a plain (polynomial) quintic they can
only be approximated. The exact form is a **rational Bézier** — six points plus six weights — or,
in SVG, an arc command (`A`), which is not a Bézier at all.

Known standard numbers, useful as a yardstick:

| classic | exact form | standard polynomial approximation |
|---|---|---|
| parabola | polynomial (degree 2) | exact — elevation, error 0 |
| circle / ellipse | rational, or `A` arc | the cubic quadrant with handle `k = 4/3·(√2 − 1) ≈ 0.5522847` has max radial error ≈ **0.027 %**; published quintic schemes get below 1e-5 |
| hyperbola | rational, weights `cosh` | no closed-form polynomial quintic; fit and measure |

`quintic-guides.ts` uses plain polynomial quintics for everything, because the Inkscape workflow
renders a path and an SVG `d` attribute cannot carry weights. So the **C** (half a circle), the
**hyperbola** and the **wave** are fitted, and each carries its measured error: 0.38, 0.50 and 0.63
grid units respectively. Those three are the honest approximations; the figure says so in its note.

**The gap this leaves.** If a conic must be exact, the object to store is (points **and** weights),
and every consumer has to know about them. That is a decision, not a bug: it changes the JSON
schema, the Inkscape extension's input, and the Blender/GeoGebra export (Blender's NURBS accepts
weights; GeoGebra can take a rational expression). Not done.

## 3. The repo already has one standard six-point construction

The **G3 quintic span** — `app/src/lib/glue.ts`, `state/SPEC-glue-int.md` — is exactly a six-point
Bézier with two free handle lengths, solved so both ends meet in position, tangent and curvature
(G0–G2 at each end plus curvature derivative, giving the six conditions). That is the standard
construction for a join, and it is the one the cubic-first rule falls back to. Any new six-point
family should reuse it rather than re-derive a join.

## 4. What "standard" would add, if wanted

1. A rational-conic family (circle, ellipse, hyperbola) with weights, stored alongside the points.
2. A published quintic circle approximation, quoted with its source and its error, as a reference
   curve beside the fitted one.
3. The degree-elevation table above as code (`elevateToQuintic(controls, degree)`), so a new family
   is a polynomial plus one call, not a fit.
