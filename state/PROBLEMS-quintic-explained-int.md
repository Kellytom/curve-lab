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
