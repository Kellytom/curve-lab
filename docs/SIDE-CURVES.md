# How to make side curves correctly

*For DeepSeek1, from DeepSeek2's session of 2026-11-21. Every rule here is
taken from the settled record — `state/DESIGN-int.md`, `state/HANDOFF-int.md`,
register rows 51–52 — with the file that proves it named beside it.*

---

## 1. What a side curve is

A side curve is a **per-construction partner**: the same construction run
again with a shifted parameter. A smaller partner on the right (parameter
`− d_R`) and a larger one on the left (`+ d_L`), drawn either side of the
spine.

It is **never** a parallel offset of the drawn curve. The operator's rule,
2026-11-17: no parallel curves as a general side curve — too mechanical.
Exceptions: scrollwork and a few select cases the operator names. If you
cannot say which construction parameter you shifted, you have not made a
side curve.

## 2. The character rail is one law

    distance = base × (1 + strength × profile(t))

- `base` — the record's width percent.
- `strength` — the record's `plus` (left) and `minus` (right).
- `profile(t)` — the record's character: `bow`, `s`, or `taper`.

One law, not a choice. Settled decisions that keep it one law:

- **The cap is solved directly, not by halving.** The rule is
  `distance × peak ≤ 0.9`; the used width is the largest safe width, so the
  band never narrows as the slider rises. Halving made the width jump
  (`c-0002`: 2.2 % → 1.15 % at the next step).
- **No second construction on top.** A local pinch cap was tried on
  2026-11-21 and reverted: at the same saved number it drew a band about
  four times too wide. The operator: "you cant cheat and use another way to
  make the character rails."
- **The fold guard sees the bow.** The station-wise offset × curvature
  *including* the strength profile is what is capped — not base width ×
  peak curvature. Register 51: at `c-0001`'s preset the widest rail reached
  1.28 × the fold limit when the guard ignored the plus, and the rail
  crossed at the loop.

## 3. The fold guard, exactly

`curvatureWorst` in `workbench/plate_math.js`: at 400 stations, the rail's
offset at a station is `distance × (1 + strength × profile(t))`, and the
fold is that offset × the curvature there. The guard caps the width so the
worst fold stays ≤ 0.9. At the `WIDTH_FLOOR` of 0.2 % the plate is
spine-only and says so in its note.

The character bow is *inside* the guard (`c-0001`: 1 % cuts to 0.7 %, the
next 0.01 % folds). A saved width above the safe one is cut, not obeyed
(`c-0006` carries a saved 8 %; the guard cuts it to 2.84 %).

## 4. The preset, and who it applies to

The operator, 2026-11-21: "i didnt ask for spines only. i asked for clean
curves like the first two."

The preset is **width 2 %, plus 2.5, minus 0.1** for the review (doubled on 2026-11-22 so the gap is visible; the first two curves keep their saved 1 %), and it applies to:

- every curve with **no saved width**,
- every curve with a **saved zero or missing width** — the note migration
  wrote 0 into width for untouched curves and those plates drew a 0 % band
  (register 52; plus = minus = 0 is a parallel offset, which is refused),
- **stored paths included** — a stored path with no width takes the preset.

A **saved width wins** over the preset. The plate reads its saved values
from `data/curves.json`, never from a stale notes export.

## 5. The parameter is per family — state it before you use it

Shifting the parameter is a different operation per family. The four stated
so far (in `scripts/side_curves.mjs`, `PARAMS`):

| family | parameter shifted | effect |
|---|---|---|
| row | the speed rows `(u, v)` | speed ×(1 ∓ d) → position ×(1 ∓ d)² about the origin |
| mobile | arm radius `r` | `r → r ∓ d`, so the partner is `(1 ∓ d)·P(t)` |
| double | the wonk half radius `r` | `r → r ∓ d`, then mirrored across y = x |
| hybrid | the middle weight `k` | `k → k ∓ d`, so `station_d = (1 ∓ d)·station` |

A new family states its parameter on the page **before** a partner is
drawn with it. A partner whose parameter is not named on the page is the
fault class of register 52 — a drawing nobody can reconstruct.

## 6. Exactness

- The partner's speed rows are the spine's rows scaled by `(1 ∓ d)` — the
  grid of the partner is the spine's grid ×(1 ∓ d) (for d = 0.04: ×0.96).
  Keep d a clean fraction so the grid stays readable (the operator likes
  grids like 5/25/3125 — powers and small factors, not long decimals).
- The exactness desk's law from 2026-11-21 applies to anything a page
  prints: exact integers and plain decimals, never an exponent
  (`app/src/lib/plain-number.js`).
- A partner built as a *drawing* (offsetting stations) is not a curve and
  carries no speed rows — do not put it in the registry. The registry only
  takes records with speed rows.

## 7. Where the code and the guards live

| file | role |
|---|---|
| `workbench/plate_math.js` | `sideRail`, `curvatureWorst`, `characterDesign` — the one law |
| `scripts/side_curves.mjs` | the sandbox → `/workbench/side-curves.html` (spine + two partners, cap lines) |
| `scripts/partner_preview.mjs` | one row per family at collection scale, mean gap per side |
| `scripts/print_plates.mjs --svg-only` | all 371 plate SVGs in ~11 s — **the SVG is the plate** |
| `tests/js/plate-guard.test.mjs` | the guard keeps a band and does not fold at the preset |
| `tests/js/plate-row.test.mjs` | zero/missing width takes the preset; a saved width wins |

Run the guards: `node --test tests/js/*.test.js`. Register rows 51 and 52
in `state/REGRESSIONS-int.md` are the two faults that wrote these tests —
read them before changing the guard or the preset.

## 8. The size and canvas law

The canvas size is decided by the bounding box of **spine plus both rails**
(`state/DESIGN-int.md`). The curve fills 97.6 % of the long side; a 1.2 %
margin keeps the stroke from being cut. Long side 3000 px, stroke 0.35 % of
that; the 300 dpi PNG is a separate, slow export — the SVG is the working
plate.

## 9. Known open cases

- `c-0260` renders 3000 × 88 with no rails (guard floor) — its partner is
  the fix, same as the ribbon overwrap at tight loops: that is what the
  per-construction partner is *for*.
- The plate preset per family migration is next: start with the row family
  (the sandbox is the worked rule); the operator names the
  scrollwork/select exceptions.
- The ribbon still overwraps visually at a tight loop even when the guard
  passes — judge it by eye, then lower the width for that record; the
  guard's 0.9 is a fold limit, not a beauty verdict.

## 10. The operator's words, verbatim — the tie-breakers

- "i didnt ask for spines only. i asked for clean curves like the first two."
- "no parallel curves as a general side curve" (except scrollwork and named
  cases).
- "you cant cheat and use another way to make the character rails."
- Numbers on a page: "i like numbers like 5, 25, 3125" — no `e16`.
