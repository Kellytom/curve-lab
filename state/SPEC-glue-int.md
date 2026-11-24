# SPEC — the glue sandbox (`/glue/`)

**Status, 2026-11-24:** the G1 cubic, the rational loop and the **G3 quintic** work; the quintic's
own loop mode is next.

**The page:** `app/src/pages/glue.astro`
**The maths:** `app/src/lib/glue.ts`; the drawing: `app/src/scripts/glue-sandbox.ts`
**The test:** `tests/js/glue.test.ts`
**The check:** `app/scripts/check-pages.mjs /glue`

## What it is

The operator: the curves go in a line — a page border or frame — and must be joined. "the
slope of curve 1 will be different than curve 2, but a curve has to connect them: eg slope 1 =
3/4 but slope 2 = -7/24". The sandbox makes that connector.

- **Two slopes, typed as fractions.** `3/4` and `-7/24`; anything else is refused with a
  message. A decimal is refused on purpose: the direction is a pair of whole numbers.
- **The ends are exact by construction.** The inner control points lie on the typed
  directions, so the cubic's end slopes *are* the typed slopes — the readout proves it to six
  decimals and the test pins your own example.
- **Directions are p-triples.** `4:3` has hypotenuse 5 and `24:-7` has 25, so both unit
  directions are rational; the control points are fractions, not approximations. A pair whose
  hypotenuse is not whole falls back to a float and says so.
- **Handles are shares of the gap**, 1–60 %, each side independent.
- **The quintic is G3.** Six control points: `P0` and `P5` fixed, `P1`/`P4` on the typed
  directions at the handle distances, and `P2`/`P3` solved so the signed curvature and its rate
  match the typed targets at both ends. Four linear equations in `P2`/`P3` once the handles are
  chosen; the page prints all six numbers (slope, κ, dκ/ds at each end). A straight glue
  (zero targets, collinear ends) is underdetermined and uses the declared collinear fallback.

## What it does not do yet

- **The quintic's own loop mode.** The rational cubic loops with a negative weight; the quintic
  loop (a declared shape, not a wider handle) is the next action.
- **The neighbours' curvature and rate are typed, not read.** The sandbox takes them as four
  numbers; a record does not yet carry them at its leg.

## The next action

The quintic's own loop mode: a declared loop at the join (a shape parameter, not a wider
handle), with the crossing printed and the six G3 conditions still met. `Proves:` a test that
prints the six end conditions at 1e-9 for a loop case and the sandbox draws it.
