# State of the work

> **draft A** — a working draft, not a final text.

**As of 2026-11-18.** This page says what is proved, what is still a draft, and
what comes next. Every claim names the command that checks it.

## The three words

- **proved** — a command reproduces the number; the check is in the table below.
- **draft** — it exists and is shown, but no check fixes it yet. It carries the
  `draft A` label.
- **gap** — it does not work, or it is missing. It is written down here rather
  than hidden.

## Proved

| claim | number | the check |
|---|---|---|
| the achievements re-derive | 65 of 65 | `scripts/recheck.py` |
| stored curves agree with the exact core | 75 curves, every grid and bend | `scripts/exact_numbers.py` |
| stored crossing counts agree with the router | every record | `scripts/crossing_audit.py` |
| every dataset declares its format and reads through one loader | 24 files | `scripts/data_audit.py` |
| the book plates exist and match their manifest | 29 plates | `node scripts/plates_export.mjs --check` |
| the square and frame rule holds at a 45° leg | arch 0° kink, S 90° | `scripts/square_try.py` |
| a fixed fault stays fixed | the register, row by row | `scripts/test_regressions.py` |

The full gate is `.venv/bin/python scripts/test.py --full`. It runs the Python
suite, the JS tests, the data audits, and the page rebuild checks.

## Draft

Everything in the public tree is **draft A**. That is not modesty: the label is
on every outward page, and `scripts/stamp_draft.py --check` fails if one loses
it.

The parts most likely to change:

- the Astro app (`app/`): pages, the save endpoint, the book gallery;
- the book plates (`book/`): 29 plates, chosen by eye, no print proof yet;
- the prose (`docs/`): this page included;
- the sandbox pages (`workbench/`): experiments, labelled as such.

## Known gaps

These are open faults, written down rather than hidden:

- **Cut and rebuild falls back to the whole curve.** The exact span needed is
  longer than the largest exact square below 1, so only the whole span keeps the
  numbers exact. The page says so instead of cutting silently.
- **Rebuild without the legs often has nothing to remove.** The crossings span
  nearly all of `t` on the curves tried, so the leg removal is exact but rarely
  applies.
- **No login on the Astro app.** The Python server has a shared-token gate; the
  Astro lab does not. Do not put it on a public hostname.
- **The plates are drawn, not printed.** Stroke weights and page sizes are set
  from measurements; a printer has not confirmed them.

## Next

The current plan is in `state/PLAN-int.md`, and the one action is in
`next-fhandoff-int.md`. In order:

1. **The grid bill for every finder curve.** Rebuild each curve's exact
   polynomials from its definition and write `workbench/curve-records.json`, one
   row per curve, with kind, scale, grid, degree and formula. The calibration is
   `lace-1of8-3` at grid 1155.
2. **W02, terminals.** The cap families, measured and drawn.
3. **W03, the fleur grammar.** Parts, joints, symmetry.
4. **W04, twenty parameter sets.** The grammar with numbers.
5. **The primal studies** (fire, water, earth, air), then the archetypal
   ornaments.

## How to check a number here

```sh
.venv/bin/python scripts/recheck.py            # the achievements, 65 checks
.venv/bin/python scripts/exact_numbers.py      # grid and bend of every record
.venv/bin/python scripts/crossing_audit.py     # crossing pairs
.venv/bin/python -m unittest tests.test_regressions   # fixed faults, ~0.1 s
```

A number that does not come from one of these commands is not a number this
project will defend.
