# PROBLEMS — quintic-explained (docs page)

Faults this page has had, the operator's words where there were any, and the guard.

## 1. The C3 column read 0 on the first example (2026-11-27)

The first draft used `q6-trefoil-10` for the "two cubics hide a quintic" row. Its
third-derivative jump came out **0**, which would have shown the opposite of the
point: that a 2-span chain can satisfy the C3 test.

**Why.** That curve is symmetric: its start and end tangents are equal, and the
C2 spline's third difference on each end segment is
`2(b0 − b1) + h(d0 + d1)`. With `d0 = d2` and symmetric stations the two sides
coincide. A symmetric example hides the jump; the test is still a real test, the
example was degenerate.

**Fix.** The column is now computed on `q6-flattened-arch-10`, which has unequal end
tangents; its jump is a large number (see the block).

**Guard.** `scripts/quintic_explained.py` names the cases in `CASES` and regenerates
the column; `--check` fails if the page and the computed numbers disagree. Do not
choose a symmetric curve for this row.

## 2. The generator must not print floating-point noise as if it were error

The parabola is exactly representable by cubics, but the fit prints values around
`1e-5` px. The page says so in words ("floating-point zeros") instead of claiming
"exact". Rule: a measured zero in this page is described as a floating-point zero
when its source is arithmetic, not measurement.

## 3. Selecting the sheet's cage in the wrong mode looks broken (2026-11-27)

Driving the installed extension headless on `workbench/quintic-guides.svg` with the
default six-points mode gives `out of the six points by up to 872.6 px` and a
34.7 px stroke miss. Nothing is broken: the six points are taken at equal arc
length, so the quintic through them is not the sheet's quintic, and the sheet's
path is not a freehand stroke to fit.

**Fix for a user.** Use the six-points mode on a drawn stroke; use
*A cage: the guide's own 6 nodes* only when the selected path has exactly six
nodes — otherwise the extension says so and refuses. **Guard:** the cage mode's
node-count refusal is the message the user sees; this note explains the 872 px
number so it is not read as a fault.

