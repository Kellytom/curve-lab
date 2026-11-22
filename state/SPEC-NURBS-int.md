# SPEC-NURBS-int — the switchover to NURBS, as a separate subsystem

> **PARKED 2026-11-21** — the operator's decision, after the analysis: the
> deliverable is cubic Beziers for Inkscape and glyphs, so the direct route
> wins unless a consumer needs NURBS input. The spec stays as the reference
> for that day; the exact-rail formula (section 1.2) carries over to the
> direct route as the rail-fit source.

What this is: a **parallel, additive subsystem** that carries the catalogue —
the curves **and their rails** — into NURBS form, while the current Bézier
pipeline keeps iterating untouched. Nothing on `main` changes until the
operator flips. The work lives on the `nurbs` branch, in its own git worktree
at `../curve-lab-nurbs/`, in modules under `app/src/lib/nurbs/`.

## 1 · The object, in plain words

The curves are stored as **speed rows** (`u(t)`, `v(t)`), which make the
position polynomial `x(t)`, `y(t)` exact, and make the stroke's speed a
polynomial — the Pythagorean-hodograph property. Three NURBS facts follow, and
they are what this subsystem builds on:

1. **Every curve is already a NURBS.** A polynomial is a rational Bézier with
   every weight 1. The conversion is a basis change (power → Bernstein),
   exact, no weights to solve, no error.
2. **Every rail (offset) is exactly rational too.** Because the speed is the
   polynomial square `w2 = u² + v²`, the offset at distance `d` is the
   rational curve `X = (x·w2 − d·y′)/w2`, `Y = (y·w2 + d·x′)/w2` — degree
   **2n−1** where n is the curve's degree, denominator degree 2·max(du, dv).
   The perpendicularity to the tangent and the exact distance `d` hold
   identically in the algebra; there is nothing to verify numerically.
3. **The exact coefficients are enormous.** At degree 23 (c-0260, the 19-crossing
   knot) the denominator's coefficients reach ~10^16. Float evaluation of a
   degree-45 rational at those magnitudes is meaningless. **Every number in
   this subsystem is a BigInt fraction** — the same rule `curve_lab/measure.py`
   was written to enforce, and the reason the repository exists.

## 2 · The vocabulary (the words this spec uses)

| word | meaning |
|---|---|
| power form | the polynomial as stored: `Σ c_i t^i` |
| Bernstein form | the same polynomial as a Bézier: `Σ b_i B_i^n(t)`; the basis the drawing tools use |
| rational Bézier | a Bernstein form with a weight per control point and a common denominator (all weights 1 = an ordinary polynomial curve) |
| NURBS | Non-Uniform Rational B-Spline — the family name; for us, one Bézier piece at a time (no knots in scope, §5) |
| exact rails | the offset curves built from the formula in §1.2, degree 2n−1 |
| w2 | `u² + v²` — the speed polynomial; the rational form's denominator |
| weights | the per-control-point multipliers of a rational Bézier; all 1 for the curves, computed for the exact rails |

## 3 · Scope

**In:**
- the exact basis change (power → Bernstein) per curve, in `Fraction`;
- the exact rational rails from the formula above;
- weights computed for the rails from the rational control points;
- evaluation of NURBS objects in exact arithmetic, with a scaled-doubles
  evaluator for the pages;
- a stress case at the top degree (c-0260, degree 23 / rails 45);
- a comparison page row: current cubic spans vs the exact NURBS, same curve.

**Out:**
- replacing the live pipeline (the flip is the operator's, later);
- B-spline knot vectors, spline merging, degree reduction (recorded as ideas,
  not built);
- performance work (nothing here is timed);
- touching any file outside `app/src/lib/nurbs/` and `state/` on this branch.

## 4 · The modules, in build order

| row | module | what it holds | done when |
|---|---|---|---|
| N1 | `nurbs/fraction.ts` | the BigInt fraction helpers (add/sub/mul/div, from-decimal, limit-free) — a copy of the `measure.ts` discipline, so the folder imports nothing outside `nurbs/` | its own unit checks pass |
| N2 | `nurbs/basis.ts` | power → Bernstein, exact; Bernstein → evaluation (the de Casteljau-style Horner in Bernstein form) | both forms evaluate identically at 41 samples per curve, diff ≤ 1e-12, for all 371 |
| N3 | `nurbs/curve.ts` | the per-curve NURBS object: control points (exact fractions), weights (all 1), degree n | one object per stored curve; a spot-check against the Python core on 12 curves |
| N4 | `nurbs/rails.ts` | the exact rational rails: numerator/denominator formulas, degree 2n−1, the two algebra identities asserted | the identities hold exactly on every studied curve (they are algebra; the check is symbolic) |
| N5 | `nurbs/weights.ts` | the rails' weights from the rational control points; a check that no weight is zero | the weights reproduce the rational form exactly |
| N6 | `nurbs/evaluate.ts` | exact evaluation; plus a scaled-doubles evaluator whose error is measured against the exact one | the scaled evaluator's worst error over the studied set is reported, not hidden |
| N7 | `nurbs/stress.ts` | c-0260 end to end: curve degree 23, rails 45, exact evaluation | the stress output is byte-stable across runs |

## 5 · The rules, each with its check

- **R1 · Exact or nothing.** Every stored coefficient is a BigInt fraction.
  *Check:* a test scans `nurbs/*.ts` for float-typed coefficient storage —
  none permitted (floats appear only inside the scaled evaluator's output).
- **R2 · Parity with the power form.** For every studied curve, the NURBS
  object evaluates to the same points as the stored polynomial at 41 samples,
  diff ≤ 1e-12. *Check:* the parity script, per curve, named.
- **R3 · The rails are algebra, not samples.** The two identities —
  perpendicularity to the tangent, and distance exactly `d` — hold as
  polynomial identities. *Check:* exact symbolic cancellation asserted in
  `Fraction` arithmetic, per curve.
- **R4 · Degree discipline.** Curves: degree n. Rails: degree 2n−1,
  denominator 2·max(du, dv). *Check:* asserted per object against the
  inventory (`workbench/nurbs-inventory.json`).
- **R5 · Weights never zero.** *Check:* asserted when built.
- **R6 · The folder imports only itself.** `nurbs/*.ts` may not import from
  `src/lib` outside `nurbs/`. *Check:* an import scan in the parity script.
- **R7 · The flip is one function.** When the operator flips, a page switches
  by calling `nurbs/evaluate.ts` where it called the piece builder — no page
  rewrite. *Check:* a demo page on the branch draws one curve both ways and
  the two paths are within the scaled evaluator's reported error.

## 6 · The known limits, stated in place

- **No knots.** This spec builds one Bézier piece per curve (or per span
  later). Knot vectors and spline merging are future ideas, not here.
- **No degree reduction.** The rails arrive at degree 2n−1. If a tool
  complains, degree reduction is its own exact task, recorded as an idea.
- **The huge-coefficient evaluation is the risk.** N6's scaled evaluator is
  the piece most likely to need a second design; its error report is the
  deliverable, not a promise.
- **The registry is the source.** The 371 rows come from
  `workbench/curve-registry.json` via the same dump the measure port used;
  re-dumped per run, never remembered.

## 7 · What carries over from the current codebase

Nothing imports it. What carries over is knowledge: the exact-fraction
discipline (`measure.ts`), the fraction-arithmetic faults and their fixes
(`state/SC-NOTES-measure-port.md` — the three port faults there are the same
faults a fraction module rewrite can re-introduce), and the inventory
(`workbench/nurbs-inventory.json`) which is the per-curve degree and offset
table this whole build checks itself against.

## 8 · Definition of done, for the whole spec

N1–N7 landed with their checks green; the stress case (c-0260) stable; the
demo page draws one curve both ways; the comparison row on the branch's copy
of the comparison page shows the exact rails beside the approximated ones;
`main` untouched since the branch point except by DeepSeek1.

## 9 · Open for the operator's ideas

- What the flip should look like (a page? a build flag? a runtime toggle?).
- Whether the rails' degree 45 is acceptable as-is or degree reduction should
  move up the order.
- Whether the scaled-doubles evaluator should target the pages' precision or
  something stricter.
- Anything else — this section is the invitation.
