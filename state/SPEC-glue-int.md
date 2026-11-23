# SPEC — the glue sandbox (`/glue/`)

**Status, 2026-11-23:** the G1 cubic connector works and is checked; G3 and the loop are next.

**The page:** `app/src/pages/glue.astro`
**The maths:** `app/src/lib/glue.js`; the drawing: `app/src/scripts/glue-sandbox.js`
**The test:** `tests/js/glue.test.mjs`
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

## What it does not do yet

- **G2 and G3.** A cubic has eight numbers; G3 needs ten conditions (position, direction,
  curvature and its rate at each end). G3 therefore needs a quintic (twelve numbers), and it
  needs the neighbours' curvature and curvature rate at the join, which a record does not carry
  at its leg today.
- **A loop at the join** (the Tschirnhausen flourish). A cubic joining two directions that
  point roughly forward is an S; a loop needs the extra control of the quintic.

## The next action

A quintic connector with G3 at both ends: twelve control numbers, solved from the two end
points, the two directions, the two curvatures and the two curvature rates; loop and no-loop
modes. `Proves:` a test that prints all six end conditions at 1e-9 for a stated case, and the
sandbox prints the same six numbers.
