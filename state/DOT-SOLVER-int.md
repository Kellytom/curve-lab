# DOT-SOLVER-int — the sub-focus for marks that miss the curve

## What it is

A measured system, not a drawing tweak. One figure per **class** of dot
failure, rendered large, with each mark checked against the curve it belongs
to. The page is `workbench/dot-solver.html`; the gate is
`scripts/check-dots.py`.

## The rule

1. A mark is a **p-triangle join** — a vertex of the chain the curve was
   converted to — not a crossing of a display grid.
2. Every solid curve gets its **own** chain. A figure of four copies gets four
   chains; one chain across all four marks only the copy it was fitted to.
3. The chain resolution is **solved, not fixed**: 24, 48, 96, 192, 384 chords,
   stopping when the joins sit inside the tolerance. The chosen resolution is
   reported per case.
4. The mark itself is the join **projected onto the curve**, so a mark is never
   off the ink. The distance it had to move is the chain's **fit error** and is
   printed next to the verdict: that is the honesty, not the fix.

## How to check

```sh
.venv/bin/python scripts/dot_solver.py     # rebuild the page
.venv/bin/python scripts/check-dots.py     # 6/6 cases pass, exit 0
```

The page carries the same numbers: marks per case, chain fit in pixels, and
PASS/FAIL. A regression is a non-zero exit, not an opinion.

## Images — the one place they are allowed

This subproject may send generated PNGs back for diagnosis. The operator
authorises it per session and runs `/fhandoff` then `/fhandon` first, so a
freeze costs one step. Scope: only images this solver produced, only in this
sub-focus. If the engine rejects one, stop and start a fresh session.

## Known quality gaps, reported not hidden

- Closed curves fit the p-triple chain poorly: the circle case sits ~13 px off
  at 192 chords even after solving. The marks are on the curve (projected);
  the *chain* is the approximation. A closed loop needs a declared seam before
  the fit can be exact.
- The clothoid spans (2b/2c) are not in the solver yet: it takes sampled
  polylines, and those two need their span endpoints as inputs.
