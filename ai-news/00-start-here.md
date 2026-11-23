# Start here

## The project in one paragraph

Exact integer and rational curves on one grid. The goal is not a gallery: it is a grammar of
plant-forms that becomes an ornament grammar, printed as book plates and taken to Inkscape and
a glyph editor. Every curve is drawn from an equation; a curve that cannot be exact is stored as
a sampled outline and says so. The operator is a craftsman, not a programmer — plain English,
units on every number, and no claim without a measurement.

## The truth, as of 2026-11-23

- **393 curves** in the collection. 213-ish are speed-row curves (`x' = u²−v²`, `y' = 2uv`), the
  rest are sampled paths; the counts in `03-data.md` are generated and authoritative.
- **Plates** are one law: the inside of a turn is thin (capped at `0.9 / κ`), the outside keeps
  the asked width; unedited curves sit at a **1 %** gap. Red dots mark places where the outside
  line crosses itself (future cut points); blue marks the start, orange the end.
- **The registers are the memory**: `state/REGRESSIONS-int.md` (faults and their tests) and
  `state/DESIGN-int.md` (settled decisions and why). `LTMemory-int.md` is the map.
- **The app is Astro on :4321** (Node 24). The main pages: `/plates/`, `/review/` (the review
  desk), `/tune/<uid>` (the tuning desk), `/extra-curves/` (what is missing, with drawings),
  `/glue/` (connectors between two slopes), `/class-v/` (the gothic arch), `/hearts/` (the two
  hearts), `/said/` (the operator's own messages), `/jobs/` (the slow-job queue).

## Where the truth lives

| question | file |
|---|---|
| what is fixed, and the test that keeps it fixed | `state/REGRESSIONS-int.md` |
| what is settled, and why | `state/DESIGN-int.md` |
| the map and the invariants | `LTMemory-int.md` |
| the current session's truth | `state/HANDOFF-int.md` (tail) |
| the one next action | `next-fhandoff-int.md` |
| what is missing from the collection | `state/GAPS-int.md`, `/extra-curves/` |
| how to work here | `AGENTS.md`, `senior-dev.md` |
| the data model | `state/DATA-int.md`, `03-data.md` |

## The working standard, in six lines

1. Plain English; a number carries its unit and how it was measured.
2. A rule that cannot fail a command is a wish — put the check in `tests/`.
3. One exact core (`curve_lab/measure.py`); no second implementation of a number.
4. A failed read is never a write; a view may hide data, never destroy it.
5. Curves, not jagged lines: exact stations, cubic chain between them, labelled approximate.
6. Commit per action, with the register row in the same commit.

## The three words that prevent most mistakes

- **crossing** — a crossing *pair* (two parameters through one place), never a place.
- **grid** — the single integer denominator; `1/105`, not "105".
- **bend** — arc over chord; a plain number, no percent.
