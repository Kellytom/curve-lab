# SPEC-reduction — the degree-11 reduction pipeline

> **draft A** — DeepSeek1's corrections baked in. Kept separate from DeepSeek1's
> work until complete: this folder (`reduction/`) on the `reduction` branch, its
> own worktree (`../curve-lab-reduction/`). Same repo.

## 1 · The task

The 110 stored curves whose position degree exceeds 11 (and their rails, which
sit at 2n−1 and break the ceiling harder) stay in **internal exact storage** —
BigInt fractions, never degraded. This pipeline builds **delivered variants**:
reduced curves at degree ≤ 11 and rails fitted at ≤ 11, each a **new variant
record** beside its exact parent, with both misses measured and printed.

## 2 · The dial, defined (DeepSeek1's correction 1)

The dial is a **stated maximum miss as a share of the curve's size**, measured
per curve and printed. Not "error ≤ tol" — a share of size, so a long curve and
a short curve are held to the same visible standard:

    maxMiss = max over samples of |delivered(t) − exact(t)| / size

where `size` is the curve's bounding-box diagonal and `delivered` is the
reduced form evaluated at t. The dial is stated once (proposed: 0.05 % of size,
adjustable), and every record prints its own measured miss next to that dial.
A record over the dial is marked, not quietly shipped.

Two different operations live under this dial, and they are not the same:

- **reduction** — an exact polynomial row (wave, lace, the (0,7) family)
  approximated at degree ≤ 11. There is no "refit dial" yet; the dial above is
  the new one.
- **refit** — the 4–5 fit-family curves (catenary, involute, euler, logspiral)
  whose degree 15 came from a fit. Those can be re-fitted at ≤ 11 with the fit
  error as the dial. Counted separately from the reductions.

## 3 · The rail is its own job (correction 2)

Reducing the curve does not reduce its rail: the exact PH rail is degree 2n−1,
so a degree-11 curve's exact rail is **degree 21 — still over the ceiling**.
Every rail-bearing curve therefore needs:

- the curve reduced to ≤ 11 (or the fit re-run), and
- **each rail fitted at ≤ 11 against the original's exact offset** — built from
  the exact formula (`X = x·w2 − d·y′` over `w2`), not from the reduced curve.

**Both misses are reported, plus the total:** the curve miss (exact → reduced
curve), the rail miss (exact offset → fitted rail), and the combined delivered
miss. Fitting the rail to the reduced curve and reporting only that error would
hide the original-to-reduced miss; that is forbidden by this spec.

## 4 · The naming rule (correction 3)

A reduced curve is a **variant record, not a rename**. The exact original is
never touched. The variant record carries:

    params.variantOf   = <exact uid>
    reducedFrom        = <exact uid>
    reducedDegree      = 11
    maxMiss            = <measured share of size>
    maxMissRail        = <measured rail miss, same share>

The plates page already groups a variant beside its parent and prints the
provenance; that is where "reduced to degree 11, miss 0.04 % of size" shows.

## 5 · The audit (DeepSeek1's addition)

A **degree audit on the delivered set, not the storage**: per record, the
position degree, the delivered rail degree, and the total miss. The exact >11
rows stay in the inventory and are **exempt** — they live in internal storage.
The audit runs on what would be handed to NURBS or Inkscape. It fails the task
if any delivered record is over the ceiling or over the dial.

## 6 · Scope and counts (computed, from `workbench/nurbs-inventory.json`)

| block | count | operation |
|---|---|---|
| curves with position degree > 11 | 110 | reduction (or refit for the 4–5 fit-family rows) |
| exact rails of those curves, degree > 11 | 207 rail instances | rail fit at ≤ 11 against the exact offset |
| both within the ceiling already | 6 | exempt; audited, not rebuilt |
| over-limit rails with ≥ 5 crossings (the good knots) | 29 | first batch — the operator's favourites go first |

## 7 · The folder

    reduction/
      SPEC-reduction.md     this file
      README.md             how to run it
      reduce.ts             the reducer: power → Bernstein, degree-elevate,
                            split at knots, reduce each piece to 11, exact at
                            the knots, interior miss in Fraction
      railfit.ts            the rail fitter against the exact offset formula
      audit.ts              the delivered-set audit
      parity/               the Python-vs-TS harness, same discipline as the
                            measure/clearance/bezier rows

It imports nothing from DeepSeek1's working set. The parity discipline is the
same as the measure/clearance/bezier rows: zero mismatches or it does not land.

## 8 · The order of work

| row | what | proves |
|---|---|---|
| R1 | the reducer for one curve (amper, degree 7 → 11 is a no-op since 7 < 11; first real row: a degree-11 curve, then a degree-15) | the miss prints, is under the dial |
| R2 | the rail fitter against the exact offset | the rail miss prints, both misses stated |
| R3 | the variant-record writer (registry rows via the standard path, coordinated at delivery) | a variant beside its parent on the plates page |
| R4 | the audit over the delivered set | the audit fails anything over ceiling or dial |
| R5 | the batch: the 29 good knots first, then the rest | the audit green over the batch |

## 9 · Open for the operator

- The dial value: 0.05 % of size is the proposal.
- Whether the 4–5 fit-family rows are re-fits (cheaper) or reductions like the
  rest, and in which order.
- Whether "delivered" means the plates page now, or only when NURBS/Inkscape
  consumption starts.
